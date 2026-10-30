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
from app.geo.facilities import (FacilitySearch, filters_from, follow_up, is_facility_query, profile_from,
                                search_replies)
from app.geo.location import SHARE, Spot, locate_point, pin_of, place_from_text
from app.geo.location import memory as location_memory
from app.guardrails import scope
from app.guardrails.emergency import EMERGENCY_REPLY, is_medical_emergency
from app.language import detect_language
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


async def _no_notify(out: Out) -> None:
    return None


async def handle(msg: dict[str, Any], wa: Any, *, store: UserStore, settings: Settings,
                 voice_fn: VoiceFn = reply_for_voice, notify: NotifyFn = _no_notify,
                 resolve_fn: ResolveFn = resolve, guard_fn: GuardFn = scope.check,
                 answer_fn: AnswerFn | None | object = _DEFAULT, locate_fn: LocateFn = locate_point,
                 place_fn: PlaceFn = place_from_text, facility_fn: FacilityFn = search_replies) -> list[Out]:
    """Returns the replies to send. `notify` sends a message right away (the "listening" ack)."""
    sender, kind = msg.get("from", ""), msg.get("type")
    text = (msg.get("text") or {}).get("body", "") if kind == "text" else ""
    button = _button_id(msg)

    # 1. Safety and data rights first
    if text and is_delete_command(text):
        delete_user_data(sender, store=store, settings=settings)
        location_memory.forget(user_key(sender, settings))       # and any point still in memory
        return [Out(DELETED_REPLY)]
    if text and is_medical_emergency(text):
        return [Out(EMERGENCY_REPLY)]

    # 2. Access
    if not settings.kasafi_open_access and not is_pilot(sender, settings):
        return [Out(NOT_IN_PILOT)]

    key = user_key(sender, settings)
    user = store.get(key)

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
            outs += await _facility_search(q, key, lang, settings, facility_fn, spot)   # the question that asked
        return outs
    # the reply to "share your location, or tell me your LGA or town": a typed place, from our own gazetteer
    if text and (waiting := location_memory.waiting_question(key)) is not None:
        if (typed := await place_fn(settings, text)) is not None:
            return _located(key, lang, store, typed) + await _facility_search(waiting, key, lang, settings,
                                                                              facility_fn, typed)
    # "nearest hospital?" and its follow-ups ("next", "route?", "only government hospitals"): PostGIS and ORS, no model
    if text and settings.has_database and (outs := await _facilities(text, key, lang, store, settings, place_fn,
                                                                         facility_fn)) is not None:
        return outs
    if (images := IMAGE_COMMANDS.get(_norm(text))) is not None:     # "images off" / "kashe hotuna": no model needed
        store.set_images(key, images)
        return [Out(t("images_on" if images else "images_off", lang))]
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
        await notify(Out(t("searching", lang)))   # planning + search + answer: median ~10 s
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
            store.add_turn(key, lang, question, body, getattr(result, "sources", []), getattr(result, "working", ""))
        except Exception as e:  # DB or model down: tell the user rather than go silent
            log.exception("answer failed: %s", type(e).__name__)
            body, result = t("answer_failed", lang), None
        offer = getattr(result, "offer", None)
        store.set_pending_calc(key, offer.to_dict() if offer else None)
        text_out = f"{prefix}\n\n{body}" if prefix else body
        if options := getattr(result, "clarify", None):     # two readings: ask which one, with buttons
            store.set_pending_clarify(key, options)
            return [Out(text_out[:1024], [(f"clar_{i}", o["title"][:20]) for i, o in enumerate(options[:3])])]
        crops = (plan_crops(result, settings.kasafi_max_images)
                 if result is not None and settings.kasafi_evidence_images and store.images_on(key) else None)
        return [Out(text_out, CALC_BUTTONS.get(lang, CALC_BUTTONS["en"]) if offer else None, crops or None, lang)]

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
        if is_medical_emergency(res.question, res.english):
            return [Out(EMERGENCY_REPLY)]
        if refusal := await _guard_correction(res, lang, guard_fn, settings):
            return [refusal]
        q = res.question[:1000]
        return await respond(q, t("corrected_prefix", lang, question=q), Out(t("corrected", lang, question=q)))

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
        if r and outcome.text != EMERGENCY_REPLY and (refusal := await _guarded(heard_texts(r), lang, guard_fn, settings)):
            return [refusal]
        if r and r.needs_confirmation and not is_medical_emergency(*heard_texts(r)):
            store.set_pending(key, r.transcript, r.english)
            return [Out(outcome.text)]            # read-back: answer after Eh or a correction
        if r and outcome.text != EMERGENCY_REPLY:  # heard clearly: answer now
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
    return outs + _located(key, lang, store, Spot(pin[0], pin[1], area.lga_pcode, area.lga, area.ward))


def _located(key: str, lang: str, store: UserStore, spot: Spot) -> list[Out]:
    """A place found (a pin or a typed place): the point in memory, the LGA on the user record and in the log."""
    location_memory.remember(key, spot)
    store.set_last_lga(key, spot.lga_pcode)
    log.info("location: %s LGA (%s)", spot.lga, spot.how)
    ward = t("location_ward", lang, ward=spot.ward) if spot.ward else ""
    return [Out(t("location_got", lang, lga=spot.lga, ward=ward))]


async def _facilities(text: str, key: str, lang: str, store: UserStore, settings: Settings, place_fn: PlaceFn,
                      facility_fn: FacilityFn) -> list[Out] | None:
    """A facility question or a follow-up to one; None when the message is neither. Without a point: a place the
    question names ("nearest clinic in Gwadabawa"), else the location request, the question kept for the pin."""
    spot, search = location_memory.recall(key), location_memory.last_search(key)
    if spot is not None and search is not None and (step := follow_up(text)):
        if step == "next":
            search.skip += len(search.shown) or 3
        elif step == "filter":
            search.filters, search.skip = filters_from(text, search.filters), 0
        search.profile = profile_from(text, search.profile)
        log.info("facility follow-up: %s", step)
        return await _facility_replies(spot, search, lang, settings, facility_fn, "route" if step == "route" else "list")
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


async def _facility_search(question: str, key: str, lang: str, settings: Settings, facility_fn: FacilityFn,
                           spot: Spot) -> list[Out]:
    """A new search for the question (its filters and travel mode) from the point; [] when it isn't one."""
    if not is_facility_query(question):
        return []
    search = FacilitySearch(filters_from(question), profile=profile_from(question))
    location_memory.remember_search(key, search)
    return await _facility_replies(spot, search, lang, settings, facility_fn, "list")


async def _facility_replies(spot: Spot, search: FacilitySearch, lang: str, settings: Settings,
                            facility_fn: FacilityFn, mode: str) -> list[Out]:
    try:
        pairs = await facility_fn(settings, spot.lat, spot.lon, search, lang, mode=mode)
    except Exception as e:      # noqa: BLE001 - PostGIS down: ask for the LGA rather than go silent
        log.warning("facility search failed: %s", type(e).__name__)
        return [Out(t("location_unavailable", lang))]
    log.info("facility search: %s LGA, %d shown, %s", spot.lga, len(search.shown), mode)
    return [Out(text, lang=lang, location=loc) for text, loc in pairs]


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
