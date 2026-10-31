"""Turns one incoming WhatsApp message into the replies to send.

Order matters:
1. Delete command and medical emergency: for everyone, consented or not. Both are local checks; no model.
2. Access gate: KASAFI_OPEN_ACCESS, or only KASAFI_PILOT_NUMBERS when it's false.
3. Language commands (/hausa, /english, Hausa, English, Turanci, or the buttons).
4. Consent: on first contact nothing goes to any model. The user gets the bilingual notice
   with [OK / Na yarda] [Hausa] [English] buttons, and stays there until they agree.
5. After consent: per-number daily limits and the global spend cap, then the actual work.
   After a voice read-back, the next reply is about that pending question: Eh/Yes confirms,
   A'a/No cancels, and anything else is merged by the model as a correction, or treated as a new
   question when it clearly is one (app/whatsapp/corrections.py).
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import Settings
from app.data_rights import DELETED_REPLY, delete_user_data, is_delete_command
from app.geo.facilities import WORDS as FAC_WORDS
from app.geo.facilities import (FacilitySearch, add_routes, emergency_lookup, filters_from, follow_up,
                                is_facility_query, location_payload, profile_from, search_replies)
from app.geo.facilities import FACILITY as FACILITY_WORD
from app.geo.facility_info import NAMED, ROUTE_TO, as_facility, card, counted, is_count, lookup
from app.geo.location import SHARE, Spot, locate_point, pin_of, place_from_text
from app.maps.render import render_specs
from app.geo.location import memory as location_memory
from app.guardrails import scope
from app.alerts.recipients import encrypt as encrypt_number
from app.sources.lga_names import name_of
from app.alerts.signup import reply as alerts_reply
from app.guardrails import emergency as em
from app.guardrails.emergency import EMERGENCY_REPLY, is_medical_emergency
from app.language import detect_language, normalize_letters
from app.providers.chat import ProviderError
from app.providers.stt import heard_texts
from app.users import UserStore, user_key
from app.whatsapp.client import mask_phone
from app.whatsapp.messages import FIX_BUTTONS, LANG_BUTTONS, NOT_IN_PILOT, NOTICE_BUTTONS, first_contact_notice, t
from app.whatsapp.corrections import Resolution, choose_option, quick_resolve, resolve
from app.agent.calculate import CalcError, Calculation
from app.evidence.crops import plan_crops
from app.agent.calculate import result_text as calc_result_text
from app.agent.answer import answer_from_documents
from app.whatsapp.voice import VoiceOutcome, is_pilot, reply_for_voice

log = logging.getLogger(__name__)

LANG_COMMANDS = {"/hausa": "ha", "hausa": "ha", "/english": "en", "english": "en", "turanci": "en", "/turanci": "en"}
LANG_BUTTON_IDS = {"lang_ha": "ha", "lang_en": "en"}
CALC_BUTTONS = {"ha": [("calc_yes", "Eh, lissafa"), ("calc_no", "A'a")],
                "en": [("calc_yes", "Yes, calculate"), ("calc_no", "No")]}
IMAGE_COMMANDS = {"images off": False, "/images off": False, "no images": False, "kashe hotuna": False,
                  "hotuna a kashe": False, "/hotuna kashe": False,
                  "images on": True, "/images on": True, "kunna hotuna": True, "hotuna a kunna": True,
                  "/hotuna kunna": True}
CONSENT_TEXTS = {"ok", "okay", "na yarda", "na amince", "i agree", "agree", "ok na yarda"}
SLOW_ANSWER_S = 12.0        # after this, a "still checking" note (unless a fetch note was already sent)
# the rows and arithmetic behind the last answer, kept with the turn: sent from the store, no model call
SHOW_QUOTES = {"quotes", "quote", "show quotes", "show the quotes", "/quotes", "nuna rubutun", "nuna min rubutun",
               "rubutun", "nuna rubutu", "/rubutu"}
QUOTES_NONE = {"en": "That answer quoted no document text.", "ha": "Wannan amsar ba ta ambaci rubutun takarda ba."}
SHOW_WORKING = {"nuna lissafi", "nuna min lissafi", "nuna lissafin", "yadda aka lissafa", "lissafi",
                "show working", "show the working", "show me the working", "show calculation", "working", "/lissafi",
                "/working"}


@dataclass
class Out:
    text: str
    buttons: list[tuple[str, str]] | None = None
    crops: list | None = None          # evidence images to send after this message (app/evidence/crops.py)
    lang: str = "ha"
    location_request: bool = False     # sent as WhatsApp's location request message ("Share location" button)
    location: dict | None = None       # sent as a location message (a facility's pin): latitude, longitude, name...
    image: bytes | None = None         # a map (JPEG), sent with `text` as its caption

    def __post_init__(self) -> None:   # every message: no look-alike letters from other scripts ('ҳ' for 'ƴ')
        self.text = normalize_letters(self.text, self.lang)


def _norm(text: str) -> str:
    return " ".join(re.sub(r"[^\w\s/]", " ", text).lower().split())


def _button_id(msg: dict[str, Any]) -> str | None:
    inter = msg.get("interactive") or {}
    return (inter.get("button_reply") or {}).get("id") if inter.get("type") == "button_reply" else None


def _notice(lang: str | None, source: str | None) -> list[Out]:
    """Two messages: Hausa, then English carrying the [OK / Na yarda] [Hausa] [English] buttons."""
    ha, en = first_contact_notice(lang, source)
    return [Out(ha), Out(en, NOTICE_BUTTONS)]


VoiceFn = Callable[..., Awaitable[VoiceOutcome]]
ResolveFn = Callable[..., Awaitable[Resolution]]
GuardFn = Callable[..., Awaitable[scope.Verdict]]
AnswerFn = Callable[..., Awaitable[str]]
_DEFAULT = object()   # answer_fn default: answer from the documents when a database is configured
NotifyFn = Callable[[Out], Awaitable[None]]
LocateFn = Callable[..., Awaitable[Any]]          # (settings, lat, lon) -> app.geo.Area | None
PlaceFn = Callable[..., Awaitable[Any]]           # (settings, text) -> app.geo.location.Spot | None
FacilityFn = Callable[..., Awaitable[list]]       # app.geo.facilities.search_replies
EmergencyFn = Callable[..., Awaitable[list]]      # app.geo.facilities.emergency_lookup
ClassifyFn = Callable[..., Awaitable[Any]]        # app.guardrails.emergency.classify
EMERGENCY_WAIT = "__emergency__:"                 # a location request sent by the fast path


ROAD_WAIT_S = 8.0                                 # how long the emergency follow-up waits for ORS road distances


def searching_key(question: str) -> str:
    """The 'working on it' line: forecasts for a hazard question (heat, dust, rain, rivers, fires; not one about
    money for them), documents otherwise. Words only: the planner hasn't run yet."""
    from app.agent.answer import MONEY_WORDS
    from app.hazards.answer import layers_asked
    return "searching_forecasts" if layers_asked(question) and not MONEY_WORDS.search(question or "") else "searching"


async def _no_notify(out: Out) -> None:
    return None


def _sender(notify: NotifyFn) -> NotifyFn | None:
    """`notify` when it really sends (the webhook's), else None: the fast reply is then returned, not dropped."""
    return None if notify is _no_notify else notify


async def handle(msg: dict[str, Any], wa: Any, *, store: UserStore, settings: Settings,
                 voice_fn: VoiceFn = reply_for_voice, notify: NotifyFn = _no_notify,
                 resolve_fn: ResolveFn = resolve, guard_fn: GuardFn = scope.check,
                 answer_fn: AnswerFn | None | object = _DEFAULT, locate_fn: LocateFn = locate_point,
                 place_fn: PlaceFn = place_from_text, facility_fn: FacilityFn = search_replies,
                 emergency_fn: EmergencyFn = emergency_lookup, classify_fn: ClassifyFn = em.classify) -> list[Out]:
    """Returns the replies to send. `notify` sends a message right away (the "listening" ack)."""
    sender, kind = msg.get("from", ""), msg.get("type")
    text = ((msg.get("text") or {}).get("body", "") if kind == "text" else
            (msg.get("button") or {}).get("text", "") if kind == "button" else "")   # a template's MORE / STOP
    button = _button_id(msg)

    # 1. Safety and data rights first
    if text and is_delete_command(text):
        delete_user_data(sender, store=store, settings=settings)
        location_memory.forget(user_key(sender, settings))       # and any point still in memory
        return [Out(DELETED_REPLY)]
    key = user_key(sender, settings)
    store.touch_alert_contact(key)             # a subscriber's sign-up lasts 90 days from their last message
    user = store.get(key)
    allowed = settings.kasafi_open_access or is_pilot(sender, settings)
    consented = bool(user and user.consented and allowed)          # the classifier (a model) only after consent
    early_lang = (user.lang if user and user.lang else None) or (detect_language(text) if text else None) or "ha"
    # the emergency fast path, for everyone: a phrase fires at once; the classifier only after consent
    if text and (d := em.detect(text)) and (d.hit or (d.health and consented)):
        if (verdict := await em.decide(text, settings, consented, classify_fn)) is not None:
            return await _emergency(key, early_lang, verdict, store, settings, emergency_fn,
                                    notify=_sender(notify))
    # the answer to the fast path's location request: a pin or a typed place, even before consent (no model)
    if (waiting := location_memory.peek_question(key)) and waiting.startswith(EMERGENCY_WAIT):
        maternal = waiting.endswith("maternal")
        if kind == "location" and (pin := pin_of(msg)):
            location_memory.waiting_question(key)
            return await _emergency(key, early_lang, em.Detection(True, maternal=maternal), store, settings,
                                    emergency_fn, Spot(pin[0], pin[1], how="pin"), first=False,
                                    notify=_sender(notify))
        if text and (typed := await place_fn(settings, text)) is not None:
            location_memory.waiting_question(key)
            return await _emergency(key, early_lang, em.Detection(True, maternal=maternal), store, settings,
                                    emergency_fn, typed, first=False, notify=_sender(notify))

    # 2. Access
    if not allowed:
        return [Out(NOT_IN_PILOT)]

    # 3. Language switch
    chosen = LANG_BUTTON_IDS.get(button or "") or LANG_COMMANDS.get(_norm(text))
    if chosen:
        if user is None:
            store.create(key, None)
        store.set_lang(key, chosen)
        user = store.get(key)
        return [Out(t("lang_set", chosen))] if user.consented else _notice(chosen, "chosen")

    # 4. Consent
    if user is None:
        user = store.create(key, detect_language(text) if text else None)
        if not (button == "consent_ok" or _norm(text) in CONSENT_TEXTS):
            log.info("first contact from %s: consent notice sent (lang=%s)", mask_phone(sender), user.lang)
            return _notice(user.lang, user.lang_source)
    if not user.consented:
        if button == "consent_ok" or _norm(text) in CONSENT_TEXTS:
            store.give_consent(key)
            log.info("consent given by %s", mask_phone(sender))
            if user.lang is None:
                return [Out(t("consent_thanks_ask_lang", None), LANG_BUTTONS)]
            return [Out(t("consent_thanks", user.lang))]
        return _notice(user.lang, user.lang_source)

    # 5. Consented: limits (skipped for our own test numbers), then work
    lang = user.lang or "ha"
    # a location pin, or "share my location": handled here (PostGIS, no model); the point stays in memory only
    if kind == "location" or (text and SHARE.search(text)):
        outs = await _location(msg, key, lang, store, settings, locate_fn)
        if pin_of(msg) and (spot := location_memory.recall(key)) and (q := location_memory.waiting_question(key)):
            outs += await _after_location(q, key, lang, settings, facility_fn, spot)    # the question that asked
        return outs
    # the reply to "share your location, or tell me your LGA or town": a typed place, from our own gazetteer
    if text and (waiting := location_memory.waiting_question(key)) is not None:
        if (typed := await place_fn(settings, text)) is not None:
            return _located(key, lang, store, typed) + await _after_location(waiting, key, lang, settings,
                                                                             facility_fn, typed)
    # "nearest hospital?" and its follow-ups ("next", "route?", "only government hospitals"): PostGIS and ORS, no model
    if text and settings.has_database and (outs := await _facilities(text, key, lang, store, settings, place_fn,
                                                                         facility_fn)) is not None:
        return outs
    # "show me a map" / "nuna min taswira" on its own: the map for what was just asked, no model
    if text and settings.has_database and MAP_ONLY.match(text):
        return await _map_only(key, lang, store, settings)
    if (images := IMAGE_COMMANDS.get(_norm(text))) is not None:     # "images off" / "kashe hotuna": no model needed
        store.set_images(key, images)
        return [Out(t("images_on" if images else "images_off", lang))]
    if text and _norm(text) in SHOW_QUOTES:                         # "nuna rubutun": the stored quotes, no model
        turns = store.recent_turns(key)
        quotes = turns[-1].get("quotes", "") if turns else ""
        return [Out(quotes or QUOTES_NONE.get(lang, QUOTES_NONE["en"]))]
    if text and _norm(text) in SHOW_WORKING:                        # "nuna lissafi": the stored working, no model
        turns = store.recent_turns(key)
        working = turns[-1].get("working", "") if turns else ""
        return [Out(working or t("no_working", lang))]
    exempt = "".join(ch for ch in sender if ch.isdigit()) in settings.exempt_numbers
    voice_used, questions_used = store.usage(key)
    pending = store.get_pending(key, settings.kasafi_pending_ttl_minutes)

    def over_cap(cost: float) -> bool:
        return not exempt and store.spent_today() + cost > settings.kasafi_daily_spend_cap_usd

    answer = (answer_from_documents if settings.has_database else None) if answer_fn is _DEFAULT else answer_fn

    async def respond(question: str, prefix: str, fallback: Out) -> list[Out]:
        """Answer an in-scope, confirmed question from the documents, after `prefix` (what we heard).

        With no document store (dev, tests), the old acknowledgement `fallback` is sent instead.
        """
        if answer is None:
            return [fallback]
        if over_cap(settings.kasafi_cost_per_question_usd):
            log.warning("daily spend cap reached")
            return [Out(t("busy", lang))]
        store.add_spend(settings.kasafi_cost_per_question_usd)
        await notify(Out(t(searching_key(question), lang)))   # planning + search + answer: median ~10 s
        sent: list[str] = []

        async def still_working() -> None:        # a slow answer (a second search, a fallback) gets one more word
            await asyncio.sleep(SLOW_ANSWER_S)
            if not sent:
                await notify(Out(t("still_working", lang)))
        slow = asyncio.create_task(still_working())
        try:
            async def send_now(text: str) -> None:   # e.g. "Ina neman takardar…" while a document is fetched
                sent.append(text)
                await notify(Out(text))
            # the user's point (memory, 30 min) or LGA on file, for 'here' and hazards; only when there is one
            spot, last = location_memory.recall(key), store.get_last_lga(key)
            place = ({"lat": spot.lat, "lon": spot.lon, "lga_pcode": spot.lga_pcode, "lga": spot.lga} if spot else
                     {"lga_pcode": last} if last else None)
            try:
                result = await answer(question, lang, settings=settings, notify=send_now,
                                      history=store.recent_turns(key), **({"place": place} if place else {}))
            finally:
                slow.cancel()
            body = result if isinstance(result, str) else result.text
            # Keep the turn for follow-ups ("check again", "what about 2024?"): 5 turns, 90 days, no number.
            store.add_turn(key, lang, question, body, getattr(result, "sources", []), getattr(result, "working", ""),
                           getattr(result, "quotes", ""))
        except Exception as e:  # DB or model down: tell the user rather than go silent
            log.exception("answer failed: %s", type(e).__name__)
            body, result = t("answer_failed", lang), None
        offer = getattr(result, "offer", None)
        store.set_pending_calc(key, offer.to_dict() if offer else None)
        text_out = f"{prefix}\n\n{body}" if prefix else body
        if options := getattr(result, "clarify", None):     # two readings: ask which one, with buttons
            store.set_pending_clarify(key, options)
            return [Out(text_out, [(f"clar_{i}", o["title"][:20]) for i, o in enumerate(options[:3])])]   # split when sent
        crops = (plan_crops(result, settings.kasafi_max_images)
                 if result is not None and settings.kasafi_evidence_images and store.images_on(key) else None)
        outs = [Out(text_out, CALC_BUTTONS.get(lang, CALC_BUTTONS["en"]) if offer else None, crops or None, lang)]
        if (specs := getattr(result, "maps", None)) and store.images_on(key) and settings.has_database:
            from app.agent.answer import lagos_today           # 'tomorrow' on tomorrow's map, not 'today'
            drawn = await asyncio.to_thread(render_specs, settings, specs, lang, lagos_today())
            outs += [Out(m.caption, lang=lang, image=m.jpeg) for m in drawn]
            if len(drawn) < len(specs):            # the answer always has its map; when it can't be drawn, say so
                outs.append(Out(t("map_failed", lang), lang=lang))
        return outs

    async def resolution_reply(res: Resolution, pending_q: str, reply: str = "") -> list[Out]:
        if res.kind == "ambiguous":            # replace or add? Ask once; the pending question stays
            store.set_pending_options(key, {"replace": res.replace, "add": res.add, "value": reply[:200]})
            return [Out(t("ask_replace_or_add", lang, value=reply[:200]), FIX_BUTTONS.get(lang, FIX_BUTTONS["ha"]))]
        if res.kind == "confirm":
            return await respond(pending_q, t("confirmed_prefix", lang, question=pending_q),
                                 Out(t("confirmed", lang, question=pending_q)))
        if res.kind == "cancel":
            return [Out(t("cancelled", lang))]
        if res.kind == "failed":
            return [Out(t("correction_failed", lang))]
        if (d := em.detect(res.question, res.english)).hit:
            return await _emergency(key, lang, d, store, settings, emergency_fn,
                                    notify=_sender(notify))
        if refusal := await _guard_correction(res, lang, guard_fn, settings):
            return [refusal]
        q = res.question[:1000]
        return await respond(q, t("corrected_prefix", lang, question=q), Out(t("corrected", lang, question=q)))

    # 5. Hazard alerts (app/alerts): sign-up and its explicit OK, the menu, STOP / DAINA, MORE; no model. Only with
    # KASAFI_ALERTS on (off on the server until step 6 is released)
    if settings.kasafi_alerts and kind in ("text", "button", "interactive") and (step := alerts_reply(
            text, button, key, lang, store, store.get_last_lga(key),
            seal=lambda: encrypt_number(sender, settings))) is not None:
        if not step.ask:
            return [Out(body, buttons, lang=lang) for body, buttons in step.messages]
        if answer is not None:
            if not exempt and questions_used >= settings.kasafi_questions_per_day:
                return [Out(t("question_limit", lang, n=settings.kasafi_questions_per_day))]
            store.count(key, "questions")
        if refusal := await _guarded([step.ask], lang, guard_fn, settings):
            return [refusal]
        return await respond(step.ask[:1000], "", Out(t("echo", lang, text=step.ask[:500])))

    # 5a. Answering "replace or add?": a button or a typed choice picks one of the two versions
    options = store.get_pending_options(key) if pending else None
    if options:
        if choice := choose_option(button or text):
            q = options[choice][:1000]
            log.info("read-back choice from %s: %s", mask_phone(sender), choice)
            store.clear_pending(key)
            if answer is not None:
                if not exempt and questions_used >= settings.kasafi_questions_per_day:
                    return [Out(t("question_limit", lang, n=settings.kasafi_questions_per_day))]
                store.count(key, "questions")
            if refusal := await _guarded([q], lang, guard_fn, settings):
                return [refusal]
            return await respond(q, t("corrected_prefix", lang, question=q), Out(t("corrected", lang, question=q)))
        if text and (quick := quick_resolve(text)) and quick.kind == "confirm":
            # "Eh" doesn't say which: answering it would mean answering the misheard version. Ask again.
            return [Out(t("ask_replace_or_add", lang, value=options.get("value", "")), FIX_BUTTONS.get(lang, FIX_BUTTONS["ha"]))]
        store.clear_pending_options(key)       # anything else: drop the question and carry on as usual

    # 5a1. The answer to "which did you mean?": a button, the option's number or its title
    if (clarify := store.get_pending_clarify(key)) and not pending:
        store.set_pending_clarify(key, None)
        choice = _clarify_choice(button, text, clarify)
        if choice is not None:
            q = clarify[choice]["question"][:1000]
            log.info("clarification chosen by %s: option %d", mask_phone(sender), choice + 1)
            if answer is not None:
                if not exempt and questions_used >= settings.kasafi_questions_per_day:
                    return [Out(t("question_limit", lang, n=settings.kasafi_questions_per_day))]
                store.count(key, "questions")
            return await respond(q, "", Out(t("echo", lang, text=q[:500])))
        # anything else: the question lapses and the message is handled as usual

    # 5a2. Eh to a calculation offer: computed here from the stored, checked inputs (no model call)
    calc = store.get_pending_calc(key)
    if calc and not pending:
        quick = quick_resolve(text) if text else None
        if button in ("calc_yes", "calc_no") or quick:
            store.set_pending_calc(key, None)
            if button == "calc_yes" or (quick and quick.kind == "confirm"):
                log.info("calculation run for %s", mask_phone(sender))
                try:
                    return [Out(calc_result_text(Calculation.from_dict(calc), lang))]
                except CalcError:
                    return [Out(t("answer_failed", lang))]
            return [Out(t("calc_cancelled", lang))]
        store.set_pending_calc(key, None)      # anything else: the offer lapses, carry on as usual

    # 5b. Eh / A'a to a pending read-back: no model needed to decide
    if pending and text and (quick := quick_resolve(text)):
        log.info("read-back reply from %s: %s (typed, no model)", mask_phone(sender), quick.kind)
        if quick.kind == "confirm" and answer is not None:
            if not exempt and questions_used >= settings.kasafi_questions_per_day:
                return [Out(t("question_limit", lang, n=settings.kasafi_questions_per_day))]
            store.count(key, "questions")      # confirming now produces an answer
        store.clear_pending(key)
        return await resolution_reply(quick, pending[0])

    if kind == "audio":
        if not exempt and voice_used >= settings.kasafi_voice_per_day:
            return [Out(t("voice_limit", lang, n=settings.kasafi_voice_per_day))]
        if over_cap(settings.kasafi_cost_per_voice_usd):
            log.warning("daily spend cap reached")
            return [Out(t("busy", lang))]
        store.count(key, "voice")
        store.add_spend(settings.kasafi_cost_per_voice_usd)
        await notify(Out(t("listening", lang)))   # transcription takes ~10 s; say we're on it
        outcome = await voice_fn(msg, wa, lang=lang, settings=settings)
        if pending and outcome.result:            # a spoken Eh / A'a / correction
            res = await _resolve_safely(pending[0], outcome.result.transcript, resolve_fn, settings)
            if res.kind != "new":
                if res.kind != "ambiguous":
                    store.clear_pending(key)
                return await resolution_reply(res, pending[0], outcome.result.transcript)
        store.clear_pending(key)                  # a new question replaces any pending one
        r = outcome.result
        if r and outcome.text == EMERGENCY_REPLY:  # the phrase list on the transcript: the fast path
            return await _emergency(key, lang, em.detect(*heard_texts(r)), store, settings, emergency_fn,
                                    notify=_sender(notify))
        if r and (verdict := await em.decide(" ".join(heard_texts(r)), settings, True, classify_fn)) is not None:
            return await _emergency(key, lang, verdict, store, settings, emergency_fn,
                                    notify=_sender(notify))
        if r and outcome.text != EMERGENCY_REPLY and (refusal := await _guarded(heard_texts(r), lang, guard_fn, settings)):
            return [refusal]
        if r and r.needs_confirmation and not is_medical_emergency(*heard_texts(r)):
            store.set_pending(key, r.transcript, r.english)
            return [Out(outcome.text)]            # read-back: answer after Eh or a correction
        if r and outcome.text != EMERGENCY_REPLY:  # heard clearly: answer now
            # a facility question by voice ('ina asibiti mafi kusa', 'how far is Arkilla PHC') as by text
            if settings.has_database and (outs := await _facilities(r.english or r.transcript, key, lang, store,
                                                                    settings, place_fn, facility_fn)) is not None:
                return [Out(t("heard_prefix", lang, transcript=r.transcript[:1000]))] + outs
            return await respond(r.transcript, t("heard_prefix", lang, transcript=r.transcript[:1000]),
                                 Out(outcome.text))
        return [Out(outcome.text)]                # emergency referral, not heard, too long

    if kind == "text":
        if not exempt and questions_used >= settings.kasafi_questions_per_day:
            return [Out(t("question_limit", lang, n=settings.kasafi_questions_per_day))]
        store.count(key, "questions")
        if pending:                               # a typed correction, or a new question
            if over_cap(settings.kasafi_cost_per_question_usd):
                return [Out(t("busy", lang))]
            store.add_spend(settings.kasafi_cost_per_question_usd)
            res = await _resolve_safely(pending[0], text, resolve_fn, settings)
            if res.kind != "new":
                if res.kind != "ambiguous":
                    store.clear_pending(key)
                return await resolution_reply(res, pending[0], text)
            store.clear_pending(key)
        if refusal := await _guarded([text], lang, guard_fn, settings):
            return [refusal]
        return await respond(text[:1000], "", Out(t("echo", lang, text=text[:500])))
    if button == "consent_ok":
        return [Out(t("consent_thanks", lang))]
    return [Out(t("other", lang))]


async def _location(msg: dict[str, Any], key: str, lang: str, store: UserStore, settings: Settings,
                    locate_fn: LocateFn) -> list[Out]:
    """A pin: its LGA (and ward) from the boundaries; the point kept in memory for 30 minutes, only the LGA on the
    user record and in the log. No pin ("share my location"): the request button. The notice line comes once."""
    outs = [Out(t("location_notice", lang))] if store.location_notice_due(key) else []
    pin = pin_of(msg)
    if pin is None:
        if not location_memory.is_waiting(key):        # keep a question already waiting ("nearest hospital?")
            location_memory.wait_for_location(key, "")  # the next message may be a typed place
        return outs + [Out(t("location_request", lang), lang=lang, location_request=True)]
    try:
        area = await locate_fn(settings, *pin)
    except Exception as e:      # no database or PostGIS down: ask for the LGA instead
        log.warning("location lookup failed: %s", type(e).__name__)
        return outs + [Out(t("location_unavailable", lang))]
    if area is None:
        log.info("location: outside Sokoto (pin)")
        return outs + [Out(t("location_outside", lang))]
    return outs + _located(key, lang, store, Spot(pin[0], pin[1], area.lga_pcode, area.lga, area.ward,
                                                  ward_likely=getattr(area, "ward_likely", False)))


def _located(key: str, lang: str, store: UserStore, spot: Spot) -> list[Out]:
    """A place found (a pin or a typed place): the point in memory, the LGA on the user record and in the log."""
    location_memory.remember(key, spot)
    store.set_last_lga(key, spot.lga_pcode)
    log.info("location: %s LGA (%s)", spot.lga, spot.how)
    ward = t("location_ward_likely" if spot.ward_likely else "location_ward", lang, ward=spot.ward) if spot.ward else ""
    return [Out(t("location_got", lang, lga=spot.lga, ward=ward))]


async def _emergency(key: str, lang: str, d: em.Detection, store: UserStore, settings: Settings,
                     emergency_fn: EmergencyFn, spot: Spot | None = None, first: bool = True,
                     notify: NotifyFn | None = None) -> list[Out]:
    """The fast path (section 7): get help now, the verified numbers only, the nearest suitable facility and its pin
    when a point or LGA is known, else the location request. No medical instructions; no model; only that it
    fired is logged. From a point, the fast reply goes through `notify` at once (returned first when there is
    none) and the road-distance follow-up is returned."""
    t0 = time.perf_counter()
    lang = lang if lang in em.WORDS else "ha"
    w = em.WORDS[lang]
    spot = spot or location_memory.recall(key)
    last = None if spot else store.get_last_lga(key)
    lines = ([w["now"]] if first else []) + em.contact_lines(lang, lga=spot.lga if spot else name_of(last or ""))
    outs: list[Out] = []
    picks = []
    if (spot or last) and settings.has_database:
        try:
            picks = await asyncio.wait_for(
                emergency_fn(settings, spot.lat if spot else None, spot.lon if spot else None, d.maternal,
                             lga_pcode=last or ""), 2.5)
        except Exception as e:      # noqa: BLE001 - PostGIS slow or down: the help line and the request still go
            log.warning("emergency facility lookup failed: %s", type(e).__name__)
    if picks and spot is not None:
        # the fast reply now, with the straight line; the road distance, time and driving link follow once ORS
        # answers (up to ROAD_WAIT_S), so a slow ORS never holds up "get help now"
        lines += em.facility_lines(lang, picks, "spot", follows=True)
        fast = [Out("\n".join(lines), lang=lang), Out("", lang=lang, location=location_payload(picks[0][1], lang))]
        if notify is None:
            outs += fast
        else:
            for out in fast:
                await notify(out)
        log.info("emergency fast path fired (%s; location point) in %.2fs", "maternal" if d.maternal else "general",
                 time.perf_counter() - t0)
        t1, routed = time.perf_counter(), False
        try:
            routed = await asyncio.wait_for(add_routes(settings, spot.lat, spot.lon, [f for _, f in picks],
                                                       timeout=ROAD_WAIT_S), ROAD_WAIT_S + 0.5)
        except Exception as e:      # noqa: BLE001 - slow or down: the link alone, the straight line said as such
            log.info("emergency road distance unavailable: %s", type(e).__name__)
        log.info("emergency road distance %s in %.2fs", "given" if routed else "unavailable", time.perf_counter() - t1)
        return outs + [Out(em.road_follow_up(lang, picks, routed), lang=lang)]
    if picks:
        lines += em.facility_lines(lang, picks, "lga", picks[0][1].lga)
    outs.append(Out("\n".join(lines), lang=lang))
    if picks:
        outs.append(Out("", lang=lang, location=location_payload(picks[0][1], lang)))
    if spot is None:                # a pin gives the nearest facility to where they are
        location_memory.wait_for_location(key, EMERGENCY_WAIT + ("maternal" if d.maternal else "general"))
        outs.append(Out(w["ask"], lang=lang, location_request=True))
    log.info("emergency fast path fired (%s; location %s) in %.2fs", "maternal" if d.maternal else "general",
             "point" if spot else "LGA" if last else "unknown", time.perf_counter() - t0)
    return outs


MAP_ONLY = re.compile(r"(?i)^\s*(?:(?:please\s+)?(?:show|send|give)\s+(?:me\s+)?(?:a|the)\s+maps?|(?:a\s+)?maps?|"
                      r"(?:don allah\s+)?(?:nuna|turo|aiko)(?:\s+min|\s+mini)?\s+(?:da\s+)?taswira\w*|taswira\w*)"
                      r"\s*[?.!]*\s*$")
MAP_NONE = {"en": "There's no map for that yet: ask about heat, dust, rain, rivers or the nearest health facility.",
            "ha": "Babu taswira ga haka tukuna: tambayi game da zafin rana, ƙura, ruwan sama, koguna ko cibiyar lafiya "
                  "mafi kusa."}


async def _map_only(key: str, lang: str, store: UserStore, settings: Settings) -> list[Out]:
    """'Show me a map' on its own: after a facility search, the near-you map; else the map of the hazard the last
    question asked about (what is in season when it named none), the user's LGA outlined."""
    from app.geo.facilities import _near_map, route_line
    from app.hazards.answer import SEASON, layers_asked
    from app.agent.answer import lagos_today
    spot, search = location_memory.recall(key), location_memory.last_search(key)
    if spot is not None and search is not None and search.shown:
        line = await route_line(settings, spot.lat, spot.lon, search.shown[0], search.profile)
        image = await asyncio.to_thread(_near_map, settings, spot.lat, spot.lon, search.shown[0].lga, search.shown,
                                        line, lang, "")
        return [Out("", lang=lang, image=image)] if image else [Out(MAP_NONE.get(lang, MAP_NONE["en"]))]
    turns = store.recent_turns(key)
    asked = [x for x in layers_asked(turns[-1].get("question", "") if turns else "") if x in ("heat", "air", "rain",
                                                                                             "flood")]
    today = lagos_today()
    layer = (asked or [x for x in SEASON[today.month] if x in ("heat", "air", "rain", "flood")])[0]
    highlight = spot.lga_pcode if spot else (store.get_last_lga(key) or "")
    spec = {"kind": "river", "day": today.isoformat()} if layer == "flood" else \
        {"kind": "hazard", "layer": layer, "day": today.isoformat(), "highlight": highlight}
    maps = await asyncio.to_thread(render_specs, settings, [spec], lang, today)
    return [Out(m.caption, lang=lang, image=m.jpeg) for m in maps] or [Out(MAP_NONE.get(lang, MAP_NONE["en"]))]


async def _facilities(text: str, key: str, lang: str, store: UserStore, settings: Settings, place_fn: PlaceFn,
                      facility_fn: FacilityFn) -> list[Out] | None:
    """A facility question or a follow-up to one; None when the message is neither. Without a point: a place the
    question names ("nearest clinic in Gwadabawa"), else the location request, the question kept for the pin."""
    spot, search = location_memory.recall(key), location_memory.last_search(key)
    if search is not None and (step := follow_up(text)):
        # a facility the message names wins over the shortcut: "how far is Arkilla PHC" is the route to Arkilla,
        # not to the last list's first one; "route?" / "next" / "how far is it" name none
        if (named := await _named_facility(text, key, lang, settings, facility_fn, spot)) is not None:
            return named
        if spot is None:                # 'how far is it from me?' with no point: ask, the question kept for the pin
            location_memory.wait_for_location(key, text)
            return [Out(FAC_WORDS.get(lang, FAC_WORDS["en"])["need_location"], lang=lang, location_request=True)]
        if step == "next":
            search.skip += len(search.shown) or 3
        elif step == "filter":
            search.filters, search.skip = filters_from(text, search.filters), 0
        search.profile = profile_from(text, search.profile)
        log.info("facility follow-up: %s", step)
        return await _facility_replies(spot, search, lang, settings, facility_fn, "route" if step == "route" else "list",
                                       key)
    if is_count(text):                   # 'how many PHCs in Sokoto?': the registry's count
        return [Out(await asyncio.to_thread(counted, settings, text, lang), lang=lang)]
    if not is_facility_query(text) and (named := await _named_facility(text, key, lang, settings, facility_fn, spot)):
        return named
    if not is_facility_query(text):
        return None
    if (typed := await place_fn(settings, text)) is not None:      # a place named wins over the point in memory
        location_memory.remember(key, typed)
        store.set_last_lga(key, typed.lga_pcode)
        spot = typed
    if spot is None:
        location_memory.wait_for_location(key, text)
        return [Out(FAC_WORDS.get(lang, FAC_WORDS["en"])["need_location"], lang=lang, location_request=True)]
    return await _facility_search(text, key, lang, settings, facility_fn, spot)


async def _named_facility(text: str, key: str, lang: str, settings: Settings, facility_fn: FacilityFn,
                          spot: Spot | None) -> list[Out] | None:
    """A facility the message names ('What about Arkilla PHC'): its registry card, kept as the facility a follow-up
    means; with 'go to' / 'how far': the route to it from the point, or the location request when there is none."""
    if not (text or "").strip() or not settings.has_database or not (FACILITY_WORD.search(text) or ROUTE_TO.search(text)):
        return None
    try:
        hits = await asyncio.to_thread(lookup, settings, text)
    except Exception as e:          # noqa: BLE001 - PostGIS down: the message goes on as usual
        log.warning("facility lookup failed: %s", type(e).__name__)
        return None
    if not hits or hits[0].score < NAMED:
        return None
    f, others = hits[0], [h for h in hits[1:] if h.score >= NAMED - 0.05][:3]
    search = FacilitySearch(shown=[as_facility(f, spot.lat if spot else None, spot.lon if spot else None)])
    location_memory.remember_search(key, search)
    log.info("facility named: %s LGA", f.lga)
    if not ROUTE_TO.search(text):
        return [Out(card(f, lang, others), lang=lang)]
    if spot is None:
        location_memory.wait_for_location(key, text)
        return [Out(FAC_WORDS.get(lang, FAC_WORDS["en"])["need_location"], lang=lang, location_request=True)]
    return await _facility_replies(spot, search, lang, settings, facility_fn, "route", key)


async def _after_location(question: str, key: str, lang: str, settings: Settings, facility_fn: FacilityFn,
                          spot: Spot) -> list[Out]:
    """The question that asked for a location, answered now that there is one: a nearest-facility search, a route
    to a named facility, or 'how far is it' for the facility last shown."""
    if is_facility_query(question):
        return await _facility_search(question, key, lang, settings, facility_fn, spot)
    if (named := await _named_facility(question, key, lang, settings, facility_fn, spot)):
        return named
    search = location_memory.last_search(key)
    if search is not None and search.shown and follow_up(question) == "route":
        return await _facility_replies(spot, search, lang, settings, facility_fn, "route", key)
    return []


async def _facility_search(question: str, key: str, lang: str, settings: Settings, facility_fn: FacilityFn,
                           spot: Spot) -> list[Out]:
    """A new search for the question (its filters and travel mode) from the point; [] when it isn't one."""
    if not is_facility_query(question):
        return []
    search = FacilitySearch(filters_from(question), profile=profile_from(question))
    location_memory.remember_search(key, search)
    return await _facility_replies(spot, search, lang, settings, facility_fn, "list", key)


async def _facility_replies(spot: Spot, search: FacilitySearch, lang: str, settings: Settings,
                            facility_fn: FacilityFn, mode: str, key: str = "") -> list[Out]:
    try:
        pairs = await facility_fn(settings, spot.lat, spot.lon, search, lang, mode=mode)
    except Exception as e:      # noqa: BLE001 - PostGIS down: ask for the LGA rather than go silent
        log.warning("facility search failed: %s", type(e).__name__)
        return [Out(t("location_unavailable", lang))]
    log.info("facility search: %s LGA, %d shown, %s", spot.lga, len(search.shown), mode)
    outs = []
    for text, loc, *rest in pairs:
        image = rest[0] if rest else None
        if text or loc or image:
            outs.append(Out(text, lang=lang, location=loc, image=image))
    return one_map(key, outs) if key else outs


MAP_REPEAT_S = 600
_maps_sent: dict[str, tuple[str, float]] = {}       # in memory: the last near-you map's hash per search, 10 minutes


def one_map(key: str, outs: list[Out]) -> list[Out]:
    """At most one map per answer, and not the same map again within 10 minutes (a repeated search or a follow-up
    that draws the same facilities sends the text and pin only)."""
    import hashlib
    now, kept, seen = time.monotonic(), [], False
    for out in outs:
        if out.image:
            digest = hashlib.sha1(out.image).hexdigest()
            last = _maps_sent.get(key)
            if seen or (last and last[0] == digest and now - last[1] < MAP_REPEAT_S):
                if out.text:
                    kept.append(Out(out.text, lang=out.lang))
                continue
            seen = True
            _maps_sent[key] = (digest, now)
        kept.append(out)
    for k in [k for k, (_, at) in _maps_sent.items() if now - at > MAP_REPEAT_S]:
        _maps_sent.pop(k, None)
    return kept


async def _guarded(texts: list[str], lang: str, guard_fn: GuardFn, settings: Settings) -> Out | None:
    """A polite refusal if the message is out of scope (political, security, medical advice), else None."""
    verdict = await guard_fn(texts, settings=settings)
    if not verdict.blocked:
        return None
    log.info("out of scope: %s (by %s)", verdict.category, verdict.tier)
    return Out(t(f"guard_{verdict.category}", lang))


async def _guard_correction(res: Resolution, lang: str, guard_fn: GuardFn, settings: Settings) -> Out | None:
    if res.kind != "correction" or is_medical_emergency(res.question, res.english):
        return None   # confirm/cancel/failed need no check; emergencies get the referral
    return await _guarded([res.question, res.english], lang, guard_fn, settings)


async def _resolve_safely(pending: str, reply: str, resolve_fn: ResolveFn, settings: Settings) -> Resolution:
    t0 = time.perf_counter()
    try:
        res = await resolve_fn(pending, reply, settings=settings)
    except (ProviderError, httpx.HTTPError, ValueError) as e:  # model down or bad JSON
        log.warning("correction merge failed: %s after %.1fs", type(e).__name__, time.perf_counter() - t0)
        return Resolution("failed")
    log.info("read-back reply resolved: %s in %.1fs", res.kind, time.perf_counter() - t0)
    return res




def _clarify_choice(button: str | None, text: str, options: list[dict]) -> int | None:
    """Which option a reply picks: the button "clar_<i>", its number ("1", "2"), or its title."""
    if button and button.startswith("clar_") and button[5:].isdigit() and int(button[5:]) < len(options):
        return int(button[5:])
    n = _norm(text)
    if n.isdigit() and 1 <= int(n) <= len(options):
        return int(n) - 1
    return next((i for i, o in enumerate(options) if n and n == _norm(o.get("title", ""))), None)
