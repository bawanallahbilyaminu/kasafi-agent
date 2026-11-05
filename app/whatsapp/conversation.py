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
import json
from dataclasses import dataclass, replace
from typing import Any

import httpx

from app.config import Settings
from app.data_rights import DELETED_REPLY, delete_user_data, is_delete_command
from app.geo.facilities import WORDS as FAC_WORDS
from app.geo.facilities import (Filters, FacilitySearch, add_routes, emergency_lookup, filters_from, follow_up,
                                is_facility_query, location_payload, profile_from, search_replies)
from app.geo.facilities import FACILITY as FACILITY_WORD
from app.geo.facility_info import NAMED, ROUTE_TO, as_facility, card, counted, is_count, lookup
from app.geo.location import SHARE, Spot, locate_point, pin_of, place_from_text
from app.place.answer import place_route
from app.place.planner import area_route
from app.agent.routing import document_question, facility_intent, other_subject
from app.privacy import names as name_memory
from app.privacy import given_name, speaking, stated_name, strip_location, strip_name
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
from app.whatsapp import menu
from app.whatsapp.messages import FIX_BUTTONS, LANG_BUTTONS, NOT_IN_PILOT, NOTICE_BUTTONS, first_contact_notice, t
from app.whatsapp.corrections import Resolution, choose_option, quick_resolve, resolve
from app.agent.calculate import CalcError, Calculation
from app.evidence.crops import plan_crops
from app.agent.calculate import result_text as calc_result_text
from app.agent.answer import answer_from_documents
from app.agent.understand import understand_message
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
PROGRESS_AFTER_S = 8.0      # "Checking the documents…" only when the answer takes longer (the typing indicator before)
SLOW_ANSWER_S = 25.0        # after this, a "still checking" note (unless a fetch note was already sent)
# the rows and arithmetic behind the last answer, kept with the turn: sent from the store, no model call
SHOW_QUOTES = {"quotes", "quote", "show quotes", "show the quotes", "/quotes", "nuna rubutun", "nuna min rubutun",
               "rubutun", "nuna rubutu", "/rubutu"}
QUOTES_NONE = {"en": "That answer quoted no document text.", "ha": "Wannan amsar ba ta ambaci rubutun takarda ba."}
FULL_BRIEF = {"full brief", "the full brief", "brief", "full report", "pdf", "cikakken rahoto", "cikakken bayani a pdf",
              "rahoto pdf"}
BRIEF_TTL_S = 3600
BRIEF_WORDS = {"en": {"caption": "📄 The full brief: every section with its sources and pages.",
                      "none": "There is no recent analysis to send as a brief. Ask a broad question first, e.g. "
                              "'What's the state of PHCs in Sokoto?'"},
               "ha": {"caption": "📄 Cikakken rahoton: dukkan sassan da madogararsu da shafuka.",
                      "none": "Babu wani bincike na kwanan nan da zan aika a matsayin rahoto. Ku fara da tambaya mai "
                              "fadi, misali 'Yaya yanayin cibiyoyin kiwon lafiya na Sokoto?'"}}
_briefs: dict[str, tuple[float, str, object]] = {}     # user key -> (when, question, deep result): memory only, 1 h
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
    document: tuple[bytes, str] | None = None   # a PDF (bytes, file name), sent with `text` as its caption
    menu: dict | None = None           # an interactive list: button, sections (app/whatsapp/menu.py)

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
SIZE_WAIT = "__size__:"                           # a place-history question waiting for the farm's size or corners


ROAD_WAIT_S = 8.0                                 # how long the emergency follow-up waits for ORS road distances


def searching_key(question: str, understanding=None) -> str:
    """The 'working on it' line, for the capability the answer will use: the reading's when there is one (the
    routes obey it: 3 Nov, 'Was Wamakko affected by floods in 2025, according to NEMA?' said 'Checking the latest
    forecasts…' and was answered from the documents); else the words: forecasts for a hazard question (heat, dust,
    rain, rivers, fires; not one about money for them), satellite for a place's record, documents otherwise."""
    from app.agent.answer import MONEY_WORDS
    from app.hazards.answer import layers_asked
    from app.place.answer import place_route
    if understanding is not None and understanding.capability not in ("other", "conversation", ""):
        return {"hazard": "searching_forecasts", "place_history": "searching_satellite"}.get(understanding.capability,
                                                                                           "searching")
    if place_route(question):
        return "searching_satellite"
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
                 emergency_fn: EmergencyFn = emergency_lookup, classify_fn: ClassifyFn = em.classify,
                 understand_fn=understand_message, heard: bool = False, spoken_lang: str | None = None) -> list[Out]:
    """Returns the replies to send. `notify` sends a message right away (the "listening" ack). `understand_fn`:
    the conversation-understanding step (app/agent/understand.py), on with KASAFI_UNDERSTANDING. `heard`: this
    text is a voice note's transcript re-entering the text path (already counted and checked as voice)."""
    sender, kind = msg.get("from", ""), msg.get("type")
    speaking("")                                 # no name carried over from another message handled on this task
    text = ((msg.get("text") or {}).get("body", "") if kind == "text" else
            (msg.get("button") or {}).get("text", "") if kind == "button" else "")   # a template's MORE / STOP
    button = _button_id(msg)

    # 1. Safety and data rights first
    if text and is_delete_command(text):
        delete_user_data(sender, store=store, settings=settings)
        location_memory.forget(user_key(sender, settings))       # and any point still in memory
        name_memory.forget(user_key(sender, settings))           # and a name the user stated (memory only)
        _first_messages.pop(user_key(sender, settings), None)    # and a first message kept before consent
        return [Out(DELETED_REPLY)]
    key = user_key(sender, settings)
    store.touch_alert_contact(key)             # a subscriber's sign-up lasts 90 days from their last message
    user = store.get(key)
    allowed = settings.kasafi_open_access or is_pilot(sender, settings)
    consented = bool(user and user.consented and allowed)          # the classifier (a model) only after consent
    early_lang = (user.lang if user and user.lang else None) or (detect_language(text) if text else None) or "ha"
    # the emergency fast path, for everyone: a phrase fires at once; the classifier only after consent
    safety: dict = {"phrase": False, "classifier": "not asked"}     # what the fast path's layers said (the trace)
    if text and (d := em.detect(text)) and (d.hit or (d.health and consented)):
        if (verdict := await em.decide(text, settings, consented, classify_fn, why=safety)) is not None:
            await _trace_emergency(settings, early_lang, verdict.by or "phrase", safety, consented)
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

    async def replay(first: dict) -> list[Out]:
        """The message kept from before consent, handled as if it had just arrived (same functions)."""
        return await handle(first, wa, store=store, settings=settings, voice_fn=voice_fn, notify=notify,
                            resolve_fn=resolve_fn, guard_fn=guard_fn, answer_fn=answer_fn, locate_fn=locate_fn,
                            place_fn=place_fn, facility_fn=facility_fn, emergency_fn=emergency_fn,
                            classify_fn=classify_fn, understand_fn=understand_fn)

    # 3. Language switch
    chosen = LANG_BUTTON_IDS.get(button or "") or LANG_COMMANDS.get(_norm(text))
    if chosen:
        if user is None:
            store.create(key, None)
        store.set_lang(key, chosen)
        user = store.get(key)
        if user.consented and (first := _kept_first(key)) is not None:   # consent came first, then the language
            return [Out(t("consent_thanks_first", chosen))] + await replay(first)
        return [Out(t("lang_set", chosen))] if user.consented else _notice(chosen, "chosen")

    # 4. Consent
    if user is None:
        user = store.create(key, detect_language(text) if text else None)
        _first_messages.pop(key, None)            # a new user never inherits a kept message
        if not (button == "consent_ok" or _norm(text) in CONSENT_TEXTS):
            log.info("first contact from %s: consent notice sent (lang=%s)", mask_phone(sender), user.lang)
            _keep_first(key, msg)
            return _notice(user.lang, user.lang_source)
    if not user.consented:
        if button == "consent_ok" or _norm(text) in CONSENT_TEXTS:
            store.give_consent(key)
            log.info("consent given by %s", mask_phone(sender))
            if user.lang is None:                 # the kept first message waits for the language
                return [Out(t("consent_thanks_ask_lang", None), LANG_BUTTONS)]
            if (first := _kept_first(key)) is not None:
                # the first message, through the whole pipeline now that models may be called: the fast path
                # (phrases, then the classifier) and the understanding step's 'urgent' come before anything else
                outs = await replay(first)
                emergency = bool(outs) and outs[0].text.startswith(em.WORDS.get(user.lang, em.WORDS["ha"])["now"][:1])
                return outs if emergency else [Out(t("consent_thanks_first", user.lang))] + outs
            return [Out(t("consent_thanks", user.lang))]
        _keep_first(key, msg)
        return _notice(user.lang, user.lang_source)

    # 5. Consented: limits (skipped for our own test numbers), then work
    # a voice note is answered in the language it was spoken in (4 Nov: a Hausa note had got English, the saved
    # preference); typed messages keep the saved language
    lang = spoken_lang if spoken_lang in ("ha", "en") else (user.lang or "ha")
    # a name the user states for themselves is held in memory for an hour after their last message (never the
    # WhatsApp profile name; never written to disk: app/privacy.py); every message restarts that hour
    # The conversation-understanding step finds the name (any wording or letter case: 'call me musa', 'Musa ne
    # sunana'); the wording rules of app/privacy.py decide only when that step doesn't run or fails.
    name_memory.touch(key)
    said = stated_name(text) if text else ""
    speaking(name_memory.recall(key) or said)    # what this message's work stores carries '[name removed]' instead
    resume = ""                                  # a place-history question that waited for this pin or shape
    resume_reading = None                        # … or a place-budget reading that waited for a location
    before: list[Out] = []                       # the replies that go out before the resumed question's answer
    # the menu's rows and the buttons under answers (app/whatsapp/menu.py): shortcuts into the same pipeline. A row
    # or a button gives a reading (no understanding call) and its restatement as the message, or a reply of its own
    preset = None
    if (crow := menu.change_row(msg)) is not None:          # the change map's lists: a measure, then an area
        outs = await _change_row(crow, key, lang, store, settings)
        await _trace_route(settings, f"[{crow}]", lang, f"menu:{crow}", None, outs, 0.0)
        return outs
    if (row := menu.row_of(msg)) is not None or button in ANSWER_BUTTONS:
        outs, preset, typed_as, lang = (await _menu_row(row, key, lang, settings) if row is not None else
                                        await _answer_button(button, key, lang, store))
        if outs is not None:
            await _trace_route(settings, f"[{row or button}]", lang, f"menu:{row or button}", None, outs, 0.0)
            return outs
        kind, text = "text", typed_as
    # the farm's size or its corner pins, asked for when no outline could be drawn (app/place/shape.py); or
    # "these are the corners" with recent pins. Shapes and pins stay in memory only.
    waiting = location_memory.peek_question(key) or ""
    sizing = waiting.startswith(SIZE_WAIT)
    if sizing or (text and shape_words(text) and location_memory.recent_pins(key)):
        shaped = await _plot_shape(msg, text, key, lang, waiting[len(SIZE_WAIT):] if sizing else "",
                                   settings=settings, locate_fn=locate_fn, store=store)
        if shaped is not None:
            before, resume = shaped
            if not resume:
                return before
    # a location pin, or "share my location": handled here (PostGIS, no model); the point stays in memory only
    if not resume and (kind == "location" or (text and SHARE.search(text))):
        # something waiting for this place (a menu row, a location request, 'Send location', a question that needed
        # a place in the last 30 minutes): the acknowledgement says what is coming, never 'what would you like?'
        coming = _coming(location_memory.peek_question(key)) if pin_of(msg) is not None else ""
        before = await _location(msg, key, lang, store, settings, locate_fn, coming=coming)
        if (pin := pin_of(msg)) is not None:
            location_memory.add_pin(key, *pin)                                            # a corner candidate
        if pin and (spot := location_memory.recall(key)) and (q := location_memory.waiting_question(key)):
            after = await _after_location(q, key, lang, settings, facility_fn, spot)     # the question that asked
            before += after
            if q.startswith(PLACE_BUDGET_WAIT):                    # 'what does the budget give my area?'
                resume, resume_reading = q[len(PLACE_BUDGET_WAIT):], place_budget_reading(q)
            elif q.startswith(CHANGE_WAIT):                        # a change map that waited for the place
                measure, _, area = q[len(CHANGE_WAIT):].partition(":")
                before += await _change_draw(measure, area, {"lat": spot.lat, "lon": spot.lon, "lga_pcode": spot.lga_pcode,
                                                             "wardcode": spot.wardcode}, lang, settings)
            elif q.startswith(READING_WAIT):                       # a menu row or 'Send location' that waited
                r = reading_from_wait(q)
                if r.capability == "facility":
                    before += await _facility_reading(r.restatement, r, key, lang, settings, facility_fn, spot) or []
                else:
                    resume, resume_reading = r.restatement, r
            elif not q.startswith((FACILITY_WAIT, CLAIM_WAIT, SIZE_WAIT, CHANGE_WAIT)) and not after and \
                    not is_facility_query(q):
                resume = q                                         # any other question that waited for a place
        if not resume:
            return before
    # the reply to "share your location, or tell me your LGA or town": a typed place, from our own gazetteer
    if text and (waiting := location_memory.waiting_question(key)) is not None:
        if (typed := await place_fn(settings, text)) is not None:
            # a typed town answers the waits below; a plain farm question still needs a pin, so nothing is promised
            answers = waiting.startswith((READING_WAIT, PLACE_BUDGET_WAIT, FACILITY_WAIT, CLAIM_WAIT)) or \
                is_facility_query(waiting)
            located = _located(key, lang, store, typed, coming=_coming(waiting) if answers else "") + \
                await _after_location(waiting, key, lang, settings, facility_fn, typed)
            if waiting.startswith(READING_WAIT) and (r := reading_from_wait(waiting)).capability != "facility":
                before, resume, resume_reading = located, r.restatement, r
            elif waiting.startswith(READING_WAIT):
                return located + (await _facility_reading(r.restatement, r, key, lang, settings, facility_fn,
                                                          typed) or [])
            elif not waiting.startswith(PLACE_BUDGET_WAIT):
                return located
            else:
                before, resume, resume_reading = located, waiting[len(PLACE_BUDGET_WAIT):], \
                    place_budget_reading(waiting)
    # what the message means in the conversation (app/agent/understand.py): one small model call before any route,
    # after the emergency fast path; keyword shortcuts below are hints it overrides. Not for commands, read-backs
    # and pending choices, which have their own fixed replies.
    u = preset                                   # a menu row's or a button's reading: no model call needed
    if u is None and kind == "text" and text and not resume and settings.kasafi_understanding and \
            _needs_understanding(text, key, store, settings):
        fallbacks: list[str] = []
        started_u = time.perf_counter()
        u = await understand_fn(strip_location(text), store.recent_turns(key), _place_for(key, store), settings,
                                fallbacks=fallbacks)
        if u is None and settings.has_database:     # both models failed: the keyword routing decides; counted
            from app.agent.trace import save_event
            await asyncio.to_thread(save_event, settings, strip_location(text), lang, "understanding_fallback",
                                    "understanding", {"fallback": fallbacks, "safety": safety},
                                    time.perf_counter() - started_u)
    if u is not None:
        u.safety = safety
    # the user's own name, when this message gives it: from the reading when the step read the message (a name it
    # returns must be in the message itself), else from the wording rules
    read = u is not None and u is not preset
    if given := (given_name(u.user_name, text) if read else said):
        name_memory.remember(key, given)
        speaking(given)
    # the safety net behind the fast path (2 Nov): an emergency happening now that its phrases and classifier missed
    # ('matata na naƙuda'), read from the meaning; 2-4 s later than a phrase, but never missed
    if u is not None and u.urgent:
        maternal = u.care == "maternal" or bool(em.MATERNAL.search(text))
        await _trace_emergency(settings, lang, "understanding", {**safety, "urgent": True}, True)
        log.info("emergency from the understanding step (fast path layers: %s)", safety)
        # a conditional reading ('if my child has trouble breathing') still fires (the safe side), and says so
        conditional = u.urgent_reason.lower().startswith("conditional") or bool(IF_WORDS.search(text))
        return await _emergency(key, lang, em.Detection(True, maternal=maternal, by="understanding",
                                                        conditional=conditional), store,
                                settings, emergency_fn, notify=_sender(notify))
    # 'menu' / 'zaɓi', read as kind 'menu' (with no reading, the word alone): the interactive list
    if kind == "text" and text and (u.kind == "menu" if u is not None else _norm(text) in MENU_WORDS):
        outs = [menu_out(lang)]
        await _trace_route(settings, text, lang, "menu", u, outs, 0.0)
        return outs
    # a message about Kasafi or the conversation ('Who are you?', 'Na gode', 'help'): one Muse Spark call under the
    # core prompt, never the document search; with no reading, the plain self-questions the same way
    if kind == "text" and text and (u.capability == "conversation" if u is not None else ABOUT_KASAFI.match(text)):
        if refusal := await _guarded([text], lang, guard_fn, settings):
            return [refusal]
        return await _conversational(text, key, lang, store, settings, u)
    # a claim about a named facility ('But UDUTH is closer to me'), after a list or cold: checked by road from the
    # pin, or from the LGA on file (said so), or the location asked for; never the document search
    parts = multi_parts(u, settings) if kind == "text" and text else []   # two or three things asked at once
    if kind == "text" and text and settings.has_database and not parts and (
            (u is not None and u.capability == "facility" and
             (u.kind == "correction" or CLOSER.search(f"{text} {u.restatement}"))) or
            (u is None and CLOSER.search(text))):
        t_route = time.perf_counter()
        if (outs := await _facility_correction(u or claim_reading(text), key, lang, settings, facility_fn,
                                               store=store)) is not None:
            _remember_turn(store, key, lang, text, outs)
            await _trace_route(settings, text, lang, "facility_check", u, outs, time.perf_counter() - t_route)
            return outs
    # no route fits and it isn't a request for information ('ok', 'hmm'): what Kasafi can help with, and a question
    if kind == "text" and text and u is not None and u.capability == "other" and not parts and \
            not looks_like_request(text):
        from app.agent.conversational import help_text
        outs = [Out(help_text(lang, _place_for(key, store)), lang=lang)]
        await _trace_route(settings, text, lang, "help", u, outs, 0.0)
        return outs
    # "nearest hospital?" and its follow-ups ("next", "route?", "only government hospitals"): PostGIS and ORS, no model
    if text and settings.has_database and settings.kasafi_shortcut_facilities and not parts and \
            (u is None or (u.capability == "facility" and u.kind != "correction")) and \
            ((outs := await _facilities(text, key, lang, store, settings, place_fn, facility_fn, u)) is not None or
             (u is not None and u.restatement and
              (outs := await _facilities(u.restatement, key, lang, store, settings, place_fn, facility_fn,
                                         u)) is not None)):
        _remember_turn(store, key, lang, text, outs)
        return outs
    # a facility reading the keyword shortcut didn't take ('Is there anywhere I can deliver a baby?', 'what about
    # UDTH?'): the registry and the nearest search, the location asked for when there is none; never the documents.
    # Staff, equipment, services and money at facilities, and a report named, stay with the documents (the registry
    # holds none of them)
    if text and settings.has_database and settings.kasafi_shortcut_facilities and u is not None and not parts and \
            u.capability == "facility" and u.kind != "correction" and not document_question(text) and \
            not (other_subject(f"{text} {u.restatement}") and not is_facility_query(f"{text} {u.restatement}")):
        t_route = time.perf_counter()
        if (outs := await _facility_reading(text, u, key, lang, settings, facility_fn)) is not None:
            _remember_turn(store, key, lang, text, outs)
            await _trace_route(settings, text, lang, "facility_reading", u, outs, time.perf_counter() - t_route)
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
    if text and _norm(text) in FULL_BRIEF:                          # the last deep analysis as a PDF, no model
        brief = _briefs.get(key)
        if not brief or time.time() - brief[0] > BRIEF_TTL_S:
            return [Out(BRIEF_WORDS.get(lang, BRIEF_WORDS["en"])["none"], lang=lang)]
        from app.agent.deep import brief_pdf
        pdf = await asyncio.to_thread(brief_pdf, brief[1], brief[2])
        return [Out(BRIEF_WORDS.get(lang, BRIEF_WORDS["en"])["caption"], lang=lang,
                    document=(pdf, "kasafi-brief.pdf"))]
    exempt = "".join(ch for ch in sender if ch.isdigit()) in settings.exempt_numbers
    voice_used, questions_used = store.usage(key)
    pending = store.get_pending(key, settings.kasafi_pending_ttl_minutes)

    def over_cap(cost: float) -> bool:
        return not exempt and store.spent_today() + cost > settings.kasafi_daily_spend_cap_usd

    answer = (answer_from_documents if settings.has_database else None) if answer_fn is _DEFAULT else answer_fn
    outer_notify = notify

    async def respond(question: str, prefix: str, fallback: Out, understanding=None, announced: bool = False,
                      sink: NotifyFn | None = None, closing: bool = True, short: bool = False) -> list[Out]:
        """Answer an in-scope, confirmed question from the documents, after `prefix` (what we heard).

        With no document store (dev, tests), the old acknowledgement `fallback` is sent instead. `announced`: the
        location acknowledgement already said what is being checked, so the first progress line is not sent again.
        `sink`: where this answer's progress lines and early text go instead of the user (a part of a multi-part
        question: the runner speaks for all the parts).
        """
        notify = sink or outer_notify
        if answer is None:
            return [fallback]
        if over_cap(settings.kasafi_cost_per_question_usd):
            log.warning("daily spend cap reached")
            return [Out(t("busy", lang))]
        store.add_spend(settings.kasafi_cost_per_question_usd)
        # one progress line per request: a place-history question sends its own ("checking about N years of
        # satellite images…", app/place/answer.py) on a first request and answers from the cache in seconds otherwise
        satellite = understanding.capability == "place_history" if understanding is not None and \
            understanding.capability not in ("other", "conversation", "") else bool(place_route(question))
        sent: list[str] = []
        closed = False                            # set when the answer timed out: nothing of it is sent after that

        async def still_working() -> None:
            # the typing indicator covers a quick answer: "Checking the documents…" only when it takes longer than
            # PROGRESS_AFTER_S, and a slow one (a second search, a fallback) gets one more word later
            await asyncio.sleep(PROGRESS_AFTER_S)
            if not sent and not satellite and not announced:
                await notify(Out(t(searching_key(question, understanding), lang)))
            await asyncio.sleep(SLOW_ANSWER_S - PROGRESS_AFTER_S)
            if not sent and not satellite:
                await notify(Out(t("still_working", lang)))
        slow = asyncio.create_task(still_working())
        started = time.perf_counter()
        try:
            async def send_now(text: str) -> None:   # e.g. "Ina neman takardar…" while a document is fetched
                if closed:                            # a job past its limit (a worker thread, a task it started)
                    log.warning("a message from a timed-out answer was dropped")   # can never send after the apology
                    return
                sent.append(text)
                await notify(Out(text))
            # the user's point (memory, 30 min) or LGA on file, for 'here' and hazards; only when there is one
            place = _place_for(key, store)
            try:
                # every long job ends in an answer or an apology within the limit, never silence
                from app.agent.deep import DEEP_TURN_S, deep_question
                # a deep analysis (by the reading, or by its words) gets the longer limit: the reading, the check and
                # a rewrite round must fit (5 Nov: a deep turn worded plainly had the shorter one, and its check
                # was skipped for lack of time); past it, it is sent when ready
                deep_turn = deep_question(question) or (understanding is not None and
                                                        understanding.capability == "deep")
                limit = max(settings.kasafi_answer_timeout_s, DEEP_TURN_S) if deep_turn \
                    else settings.kasafi_answer_timeout_s
                # an exact location typed or spoken into the question never reaches a model (app/privacy.py);
                # the history is read back from the store, where it was removed before writing
                job = asyncio.ensure_future(
                    answer(strip_location(question), lang, settings=settings, notify=send_now,
                           history=store.recent_turns(key),
                           **({"place": place} if place else {}),
                           **({"understanding": understanding} if understanding is not None else {})))
                result = await _await_answer(job, limit, sent, lang, notify, carry_on=deep_turn)
            finally:
                slow.cancel()
            body = result if isinstance(result, str) else result.text
            # "I couldn't find the answer…" never answers a message that isn't a document question: what Kasafi
            # can help with, and what they are looking for
            if getattr(result, "found", True) is False and not getattr(result, "clarify", None) and \
                    not getattr(result, "needs_pin", False) and not getattr(result, "needs_size", False) and \
                    (understanding.capability in ("conversation", "other") if understanding is not None
                     else not looks_like_request(question)):
                from app.agent.conversational import help_text
                body = help_text(lang, place)
            working = getattr(result, "working", "")
            if short and getattr(result, "found", True) is not False:   # a part of a multi-part reply: the lead
                body, rest = short_form(body)                            # and sources; the rest to 'show working'
                working = f"{rest}\n\n{working}".strip() if rest else working
            # Keep the turn for follow-ups ("check again", "what about 2024?"): 5 turns, 90 days, no number.
            store.add_turn(key, lang, question, body, getattr(result, "sources", []), working,
                           getattr(result, "quotes", ""))
        except FetchStillRunning as fsr:
            # the fetch outran even the long limit: the job goes on and its answer is sent when ready (never
            # 'took too long' while a fetch is running)
            seconds = time.perf_counter() - started
            log.warning("fetch still running after %.0fs: the answer will follow on its own", seconds)
            asyncio.get_running_loop().create_task(
                _deliver_later(fsr.job, sender, key, lang, strip_location(question), store, settings))
            words = FETCH_WORDS.get(lang, FETCH_WORDS["en"])
            body, result = words["later" if fetch_started(sent) else "deep_later"], None
        except asyncio.TimeoutError:
            closed = True
            seconds = time.perf_counter() - started
            log.error("answer timed out after %.0fs (limit %.0fs): %s", seconds, settings.kasafi_answer_timeout_s,
                      "satellite" if satellite else "documents")
            body, result = t("satellite_failed" if satellite else "answer_timeout", lang), None
            await _note_failure(settings, question, lang, f"{'satellite' if satellite else 'documents'}: timeout after {seconds:.0f}s", seconds, body)
        except Exception as e:  # DB or model down: tell the user rather than go silent
            seconds = time.perf_counter() - started
            log.exception("answer failed: %s", type(e).__name__)
            body, result = t("satellite_failed" if satellite else "answer_failed", lang), None
            await _note_failure(settings, question, lang, f"{'satellite' if satellite else 'documents'}: {type(e).__name__}: {e}"[:300], seconds, body)
        offer = getattr(result, "offer", None)
        store.set_pending_calc(key, offer.to_dict() if offer else None)
        text_out = f"{prefix}\n\n{body}" if prefix else body
        if options := getattr(result, "clarify", None):     # two readings: ask which one, with buttons
            store.set_pending_clarify(key, options)
            return [Out(text_out, [(f"clar_{i}", o["title"][:20]) for i, o in enumerate(options[:3])])]   # split when sent
        if getattr(result, "needs_pin", False):             # a place-history question: the pin first, then the answer
            # a place-budget reading waits with its restatement, and resumes with the same reading
            location_memory.wait_for_location(key, PLACE_BUDGET_WAIT + understanding.restatement
                                              if understanding is not None and
                                              understanding.capability == "place_budget" else question)
            return [Out(text_out, lang=lang, location_request=True)]
        if getattr(result, "needs_size", False):            # no outline: the farm's size or corner pins, then the answer
            location_memory.wait_for_location(key, SIZE_WAIT + question)
            location_memory.clear_pins(key)                 # only pins sent from now on are corners
            return [Out(text_out, lang=lang)]
        crops = (plan_crops(result, settings.kasafi_max_images)
                 if result is not None and settings.kasafi_evidence_images and store.images_on(key) else None)
        answered = result is not None and getattr(result, "found", True) is not False
        if answered and closing and understanding is not None and \
                understanding.capability not in ("conversation", "other") \
                and not offer and (closing_line := menu.closing_offer(lang, understanding, text_out)):
            text_out = f"{text_out}\n\n{closing_line}"     # one short next step tied to this answer
        if understanding is not None:
            _remember_reading(key, understanding)          # for 'Hausa / English' and 'Send location' buttons
        outs = [Out(text_out, CALC_BUTTONS.get(lang, CALC_BUTTONS["en"]) if offer else None, crops or None, lang)]
        if (deep := getattr(result, "deep", None)) is not None:     # one short message per dimension; the brief kept
            outs += [Out(p, lang=lang) for p in getattr(result, "parts", []) or []]
            _briefs[key] = (time.time(), question, deep)
            for k in [k for k, v in _briefs.items() if time.time() - v[0] > BRIEF_TTL_S]:
                _briefs.pop(k, None)
        if (specs := getattr(result, "maps", None)) and store.images_on(key) and settings.has_database:
            from app.agent.answer import lagos_today           # 'tomorrow' on tomorrow's map, not 'today'
            # the checked text goes now; the maps follow under their own deadline (follow-up review, finding 5).
            # The webhook skips the identical text when the list returns and sends its crops after it.
            if _sender(notify) is not None:
                await notify(outs[0])
            try:
                drawn = await asyncio.wait_for(asyncio.to_thread(render_specs, settings, specs, lang, lagos_today()),
                                               MAP_DEADLINE_S)
            except asyncio.TimeoutError:
                log.warning("maps not drawn within %.0f s: the answer went without them", MAP_DEADLINE_S)
                drawn = []
            outs += [Out(m.caption, lang=lang, image=m.jpeg) for m in drawn]
            if len(drawn) < len(specs):            # the answer always has its map; when it can't be drawn, say so
                outs.append(Out(t("map_failed", lang), lang=lang))
        if result is not None and not offer:
            _add_buttons(outs, lang, result, understanding, question, _place_for(key, store))
        return outs

    async def multi_part(readings: list) -> list[Out]:
        """Two or three things asked at once (KASAFI_MULTI_PART): each part answered by its own capability with the
        shared pin, LGA and language, in parallel, then joined in the order asked under a short heading each; a
        part's crops and maps follow its text; a part that fails gets its honest line and the others still go."""
        t_route = time.perf_counter()
        if _sender(notify) is not None:
            await notify(Out(parts_progress(lang, readings), lang=lang))
        # the point the parts share, read once: a part that starts a wait (the farm's size, a pin) must not change
        # what another part sees (4 Nov: the clinic part lost the pin to the flood part's size request)
        spot = location_memory.recall(key)

        async def one(r) -> list[Out]:
            try:
                if r.capability == "facility" and settings.has_database and settings.kasafi_shortcut_facilities and \
                        (outs := await _facility_reading(r.restatement, r, key, lang, settings, facility_fn,
                                                         spot)) is not None:
                    _remember_turn(store, key, lang, r.restatement, outs)
                    return outs
                return await respond(r.restatement[:1000], "", Out(t("echo", lang, text=r.restatement[:500])),
                                     understanding=r, announced=True, sink=_no_notify, closing=False, short=True)
            except Exception as e:              # noqa: BLE001 - one part's failure never drops the others
                log.exception("a part of a multi-part question failed: %s", type(e).__name__)
                return [Out(t("answer_failed", lang), lang=lang)]
        results = await asyncio.gather(*(one(r) for r in readings))
        store.set_pending_calc(key, None)       # a part's calculation offer has no button in the joined reply
        outs = join_parts(readings, list(results), lang, settings.kasafi_max_images)
        if u is not None:
            _remember_reading(key, u)
        await _trace_route(settings, text, lang, "multi_part", u, outs, time.perf_counter() - t_route)
        return outs

    if resume:                                   # the pin or the shape arrived: the place-history question goes on
        announced = any(o.text.startswith("📍") for o in before)        # 'Got it: … Checking …' already said
        if _sender(notify) is not None:          # "Got it…" goes out now, before the answer's own progress line
            for o in before:
                await notify(o)
            before = []
        return before + await respond(resume, "", Out(t("echo", lang, text=resume[:500])), understanding=resume_reading,
                                      announced=announced)

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
    # (the reading's 'alerts' with the words matching no sign-up: its restatement is tried too)
    if settings.kasafi_alerts and settings.kasafi_shortcut_alerts and kind in ("text", "button", "interactive") and \
            ((step := alerts_reply(
                text, button, key, lang, store, store.get_last_lga(key),
                seal=lambda: encrypt_number(sender, settings))) is not None or
             (u is not None and u.capability == "alerts" and u.restatement and
              (step := alerts_reply(u.restatement, None, key, lang, store, store.get_last_lga(key),
                                    seal=lambda: encrypt_number(sender, settings))) is not None)):
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
        # a clearly heard note that is itself a whole question is a new question, never a correction of the
        # pending read-back (4 Nov: a full Hausa question got "Corrected: …" instead of "I heard: …")
        if pending and outcome.result and not (not outcome.result.needs_confirmation and
                                               len(outcome.result.transcript.split()) >= 6):
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
            # the read-back waits on disk without a name the speaker gave (the store removes it); the name itself
            # is held in memory as for any message
            if heard_name := stated_name(r.transcript) or stated_name(r.english):
                name_memory.remember(key, heard_name)
                speaking(heard_name)
            store.set_pending(key, r.transcript, r.english)
            return [Out(outcome.text)]            # read-back: answer after Eh or a correction
        if r and outcome.text != EMERGENCY_REPLY:  # heard clearly: the transcript takes exactly the text path
            # (understanding, multi-part, every shortcut and capability, the shared pin), after "I heard: …".
            # 4 Nov: a three-part voice note had gone straight to the document search as one question
            heard_msg = {**msg, "id": f"{msg.get('id', '')}-heard", "type": "text", "text": {"body": r.transcript[:1000]}}
            spoken = r.language if r.language in ("ha", "en") else None        # answered in the note's language
            outs = await handle(heard_msg, wa, store=store, settings=settings, voice_fn=voice_fn, notify=notify,
                                resolve_fn=resolve_fn, guard_fn=guard_fn, answer_fn=answer_fn, locate_fn=locate_fn,
                                place_fn=place_fn, facility_fn=facility_fn, emergency_fn=emergency_fn,
                                classify_fn=classify_fn, understand_fn=understand_fn, heard=True, spoken_lang=spoken)
            return [Out(t("heard_prefix", spoken or lang, transcript=r.transcript[:1000]))] + outs
        return [Out(outcome.text)]                # emergency referral, not heard, too long

    if kind == "text":
        if not heard:                             # a voice note's transcript was counted and capped as voice
            if not exempt and questions_used >= settings.kasafi_questions_per_day:
                return [Out(t("question_limit", lang, n=settings.kasafi_questions_per_day))]
            store.count(key, "questions")
            from app.agent.deep import deep_question
            if deep_question(text):               # a deep analysis counts double against the daily limit
                store.count(key, "questions")
        # a typed message that is itself a whole question is a new question, never a correction of the pending
        # read-back (4 Nov live: 'How much did Sokoto spend on social protection in Q3 2026?' got 'Corrected: …')
        if pending and not (len(text.split()) >= 6 and text.rstrip().endswith("?")):   # a typed correction, or new
            if over_cap(settings.kasafi_cost_per_question_usd):
                return [Out(t("busy", lang))]
            store.add_spend(settings.kasafi_cost_per_question_usd)
            res = await _resolve_safely(pending[0], text, resolve_fn, settings)
            if res.kind != "new":
                if res.kind != "ambiguous":
                    store.clear_pending(key)
                return await resolution_reply(res, pending[0], text)
            store.clear_pending(key)
        elif pending:
            store.clear_pending(key)
        if not heard and (refusal := await _guarded([text], lang, guard_fn, settings)):   # voice: guarded already
            return [refusal]
        if parts:
            return await multi_part(parts)
        return await respond(text[:1000], "", Out(t("echo", lang, text=text[:500])), understanding=u)
    if button == "consent_ok":
        return [Out(t("consent_thanks", lang))]
    return [Out(t("other", lang))]


MULTI_WORDS = {
    "en": {"progress": "Checking {n} things: {labels}…", "none": "I couldn't answer this part."},
    "ha": {"progress": "Ina duba abubuwa {n}: {labels}…", "none": "Ban iya amsa wannan ɓangaren ba."},
}


def multi_parts(u, settings: Settings) -> list:
    """The readings of a message that asks for two or three different things (app/agent/understand.py `parts`),
    with KASAFI_MULTI_PART on; [] otherwise, and the whole message's reading answers as before."""
    return u.part_readings() if u is not None and settings.kasafi_multi_part else []


def parts_progress(lang: str, readings: list) -> str:
    w = MULTI_WORDS.get(lang, MULTI_WORDS["en"])
    labels = ", ".join((r.label or r.restatement[:40]) for r in readings)
    return w["progress"].format(n=len(readings), labels=labels)


def short_form(body: str) -> tuple[str, str]:
    """A part of a multi-part reply, kept short: its lead paragraph (the first paragraph that isn't an assumption
    note), then its sources line and the 'show working' hint; everything between (execution detail, statewide
    figures, the agency breakdown) goes to 'show working'. Returns (short text, the rest)."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", body or "") if p.strip()]
    if len(paras) <= 2:
        return (body or "").strip(), ""
    keep, rest, lead_done, take_next = [], [], False, False
    for p in paras:
        tail = p.startswith(("📄", "_Reply", "_Ku rubuta", "Sources:", "📎"))
        title = "\n" not in p and p.startswith("*") and (p.endswith("*") or "experimental" in p)
        note = "\n" not in p and len(p) <= 200 and not any(ch.isdigit() for ch in p) and \
            not p.startswith(("_Assumption", "_Zato"))
        if tail:
            keep.append(p)
        elif take_next:                         # the lead ended with ':' — its list belongs with it
            keep.append(p)
            take_next = False
        elif not lead_done and (title or note):
            keep.append(p)                      # a title line or a short scope note: kept with the first findings
        elif not lead_done and not p.startswith(("_Assumption", "_Zato")):
            keep.append(p)                      # the first paragraph with figures: the lead
            lead_done, take_next = True, p.rstrip().endswith(":")
        else:
            rest.append(p)
    return "\n\n".join(keep), "\n\n".join(rest)


def join_parts(readings: list, results: list[list[Out]], lang: str, max_images: int = 3) -> list[Out]:
    """One reply from the parts' replies: each part's text under a numbered heading, in the order asked, then
    every part's attachments (page crops with the first message, then maps, pins and documents) in the same
    order. A part with no reply at all gets one honest line; no part is ever dropped."""
    w = MULTI_WORDS.get(lang, MULTI_WORDS["en"])
    heads, crops, rest, location_request = [], [], [], False
    for i, (r, outs) in enumerate(zip(readings, results), 1):
        first = outs[0] if outs else Out(w["none"], lang=lang)
        label = (r.label or r.restatement[:60]).strip().rstrip(".?:")
        label = label[:1].upper() + label[1:]                   # "1. Government spending"
        heads.append(f"*{i}. {label}*\n{first.text.strip()}")
        crops += first.crops or []
        location_request = location_request or first.location_request
        rest += [o for o in outs[1:] if o.text or o.image or o.document or o.location]
    return [Out("\n\n".join(heads), None, crops[:max_images] or None, lang, location_request=location_request)] + rest


FETCH_LIMIT_S = 300.0        # a turn that started a document fetch gets this long (download, index, then answer)
FETCH_PROGRESS_S = 45.0      # a progress line this often while the fetch runs
FETCH_WORDS = {
    "en": {"progress": ["⬇️ Downloading the report…", "📖 Reading the tables…", "📖 Still indexing the report…"],
           "later": "The report is still being indexed. I'll send the answer here as soon as it's ready.",
           "deep_later": "I'm still checking this analysis. I'll send it here as soon as it's ready."},
    "ha": {"progress": ["⬇️ Ina sauke rahoton…", "📖 Ina karanta teburinsa…", "📖 Har yanzu ina shigar da rahoton…"],
           "later": "Har yanzu ana shigar da rahoton. Zan aiko da amsar a nan da zarar ta shirya.",
           "deep_later": "Har yanzu ina duba wannan bincike. Zan aiko shi a nan da zarar ya shirya."},
}


class FetchStillRunning(Exception):
    """The turn's fetch ran past FETCH_LIMIT_S: the job goes on and the answer is sent when it finishes."""

    def __init__(self, job: asyncio.Task) -> None:
        super().__init__("fetch still running")
        self.job = job


def fetch_started(sent: list[str]) -> bool:
    return any(x.startswith("📥") for x in sent)


async def _await_answer(job: asyncio.Task, limit: float, sent: list[str], lang: str, notify: NotifyFn,
                        carry_on: bool = False):
    """The answer within `limit`; when the job has started a document fetch (its progress line went out), the
    turn runs on to FETCH_LIMIT_S with a progress line every FETCH_PROGRESS_S (4 Nov: a live fetch finished after
    the 2-minute limit and the user got 'took too long', then the answer only on asking again). Past that, the
    job keeps running and FetchStillRunning carries it to the caller, which sends the answer when it's done. With
    `carry_on` (a deep analysis), the same past `limit`."""
    t0 = asyncio.get_running_loop().time()
    words = FETCH_WORDS.get(lang, FETCH_WORDS["en"])["progress"]
    n = 0
    while True:
        elapsed = asyncio.get_running_loop().time() - t0
        budget = FETCH_LIMIT_S if fetch_started(sent) else limit
        if elapsed >= budget:
            if fetch_started(sent) or carry_on:
                raise FetchStillRunning(job)
            job.cancel()
            raise asyncio.TimeoutError()
        step = min(budget - elapsed, FETCH_PROGRESS_S if fetch_started(sent) else max(0.05, limit - elapsed))
        try:
            return await asyncio.wait_for(asyncio.shield(job), step)
        except asyncio.TimeoutError:
            if job.done():
                return job.result()
            if fetch_started(sent) and asyncio.get_running_loop().time() - t0 < FETCH_LIMIT_S:
                await notify(Out(words[min(n, len(words) - 1)], lang=lang))
                n += 1


async def _deliver_later(job: asyncio.Task, sender: str, key: str, lang: str, question: str, store: UserStore,
                         settings: Settings) -> None:
    """The answer of a fetch that outran the turn, sent on its own when the job finishes (inside the 24-hour
    window); kept as a turn for follow-ups. Never raises."""
    from app.whatsapp.client import WhatsAppClient
    try:
        result = await job
        body = result if isinstance(result, str) else result.text
        store.add_turn(key, lang, question, body, getattr(result, "sources", []), getattr(result, "working", ""),
                       getattr(result, "quotes", ""))
        client = WhatsAppClient()
        try:
            await client.send_text(sender, body)
            for part in getattr(result, "parts", None) or []:      # a deep analysis's section messages
                await client.send_text(sender, part)
        finally:
            await client.aclose()
        log.info("late answer sent after a fetch for %s", mask_phone(sender))
    except Exception as e:              # noqa: BLE001
        log.exception("late answer after a fetch failed: %s", type(e).__name__)
        await _note_failure(settings, question, lang, f"late answer after a fetch: {type(e).__name__}", 0.0, "")


async def _note_failure(settings: Settings, question: str, lang: str, reason: str, seconds: float, apology: str) -> None:
    """The failure reason for the admin page (a trace row with outcome 'failed'); never raises."""
    if not settings.has_database:
        return
    from app.agent.trace import save_failure
    await asyncio.to_thread(save_failure, settings, question, lang, reason, seconds, apology)


def shape_words(text: str) -> bool:
    from app.place.shape import CORNER_WORDS, DONE_WORDS
    return bool(CORNER_WORDS.search(text) or DONE_WORDS.match(text))


async def _plot_shape(msg: dict[str, Any], text: str, key: str, lang: str, question: str, *,
                      settings: Settings | None = None, locate_fn: LocateFn | None = None, store: UserStore | None = None
                      ) -> tuple[list[Out], str] | None:
    """The plot shape a farmer gives (app/place/shape.py): a corner pin (counted), 'done' (the pins joined into
    the plot, the point moved to its centre), a size ('3 acres'), or 'skip' (the 1 ha circle). Returns the
    replies and the waiting question to answer now (''
    when nothing is to be answered yet); None when the message is something else (the wait is dropped and the
    size counts as declined, so the next place question answers with the 1 ha circle instead of asking again)."""
    from app.place import shape as S
    from app.place.answer import W as PW
    w = PW["ha" if lang == "ha" else "en"]
    if (pin := pin_of(msg)) is not None:
        n = location_memory.add_pin(key, *pin)
        return [Out(w["corner_got"].format(n=n), lang=lang)], ""
    if not text:
        return None
    if S.DONE_WORDS.match(text) or S.CORNER_WORDS.search(text):
        pins = location_memory.recent_pins(key)
        if len(pins) < S.MIN_CORNERS:
            return [Out(w["corner_few"].format(n=len(pins)), lang=lang)], ""
        shape = S.shape_from_corners(pins[-S.MAX_CORNERS:])
        if shape is None:
            _, _, why = S.corners_polygon(pins[-S.MAX_CORNERS:])
            location_memory.clear_pins(key)
            return [Out(w["corner_bad"].format(n=len(pins), why=w["corner_why"].get(why, why)), lang=lang)], ""
        location_memory.clear_pins(key)
        if question:
            location_memory.waiting_question(key)
        clat, clon = S.centroid(shape["geometry"])                      # the plot's centre is now the point
        spot = location_memory.recall(key)
        centre = Spot(clat, clon, spot.lga_pcode if spot else "", spot.lga if spot else "", spot.ward if spot else "",
                      how="pin", ward_likely=bool(spot and spot.ward_likely), wardcode=spot.wardcode if spot else "")
        if locate_fn is not None and settings is not None:              # the centre may sit in another ward or LGA
            try:
                if (area := await locate_fn(settings, clat, clon)) is not None:
                    centre = Spot(clat, clon, area.lga_pcode, area.lga, area.ward, how="pin",
                                  ward_likely=getattr(area, "ward_likely", False), wardcode=getattr(area, "wardcode", ""))
                    if store is not None:
                        store.set_last_lga(key, area.lga_pcode)
            except Exception as e:      # noqa: BLE001 - PostGIS down: the corner pins' area stands
                log.warning("plot centre lookup failed: %s", type(e).__name__)
        location_memory.remember(key, centre)                           # the point first, then its plot's shape
        location_memory.remember_shape(key, shape, at=(clat, clon))
        return [Out(w["shape_set"].format(ha=f"{shape['area_ha']:.1f}", n=shape["corners"],
                                          next="" if question else w["shape_next"]).strip(), lang=lang)], question
    if not question:
        return None
    if S.SKIP_WORDS.match(text):
        location_memory.remember_shape(key, {"declined": True})
        location_memory.waiting_question(key)
        return [], question
    ha = S.parse_area_ha(text, asked=True)
    if ha is not None:
        spot = location_memory.recall(key)
        if spot is None:                                                 # the point expired: ask for it again
            location_memory.waiting_question(key)
            location_memory.wait_for_location(key, question)
            return [Out(t("location_request", lang), lang=lang, location_request=True)], ""
        location_memory.remember_shape(key, S.shape_from_size(spot.lat, spot.lon, ha))
        location_memory.waiting_question(key)
        return [Out(w["size_set"].format(ha=f"{ha:g}", next="").strip(), lang=lang)], question
    if re.search(r"\d", text) and len(text) < 40:                        # a size we couldn't read: say how
        return [Out(w["size_bad"], lang=lang)], ""
    location_memory.waiting_question(key)                                # something else: the size is declined
    location_memory.remember_shape(key, {"declined": True})
    return None


async def _location(msg: dict[str, Any], key: str, lang: str, store: UserStore, settings: Settings,
                    locate_fn: LocateFn, coming: str = "") -> list[Out]:
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
                                                  ward_likely=getattr(area, "ward_likely", False),
                                                  wardcode=getattr(area, "wardcode", "")), coming=coming)


def _located(key: str, lang: str, store: UserStore, spot: Spot, coming: str = "") -> list[Out]:
    """A place found (a pin or a typed place): the point in memory, the LGA on the user record and in the log. With
    something waiting for it (`coming`, from _coming), the acknowledgement says the place and what is coming, and
    the request is answered next; only with nothing waiting does it ask what the user would like to know."""
    location_memory.remember(key, spot)
    store.set_last_lga(key, spot.lga_pcode)
    log.info("location: %s LGA (%s)%s", spot.lga, spot.how, f"; answering the waiting {coming} request" if coming else "")
    ward = t("location_ward_likely" if spot.ward_likely else "location_ward", lang, ward=spot.ward) if spot.ward else ""
    if coming:
        from app.whatsapp.messages import COMING
        return [Out(t("location_got_for", lang, lga=spot.lga, ward=ward,
                      coming=COMING["en" if lang == "en" else "ha"][coming]), lang=lang)]
    return [Out(t("location_got", lang, lga=spot.lga, ward=ward))]


def _coming(waiting: str | None) -> str:
    """What a request waiting for a place will get now ('' when nothing is waiting): outlook, forecast, budget,
    facility, claim, satellite or question (a key of the 'location_coming' message)."""
    if not waiting:
        return ""
    if waiting.startswith(READING_WAIT):
        r = reading_from_wait(waiting)
        if r.capability == "hazard":
            return "outlook" if r.time == "forecast" and re.search(r"(?i)outlook|flood", r.restatement or "") else "forecast"
        return {"place_budget": "budget", "facility": "facility", "place_history": "satellite"}.get(r.capability, "question")
    if waiting.startswith(PLACE_BUDGET_WAIT):
        return "budget"
    if waiting.startswith(CHANGE_WAIT):
        return "map"
    if waiting.startswith(CLAIM_WAIT):
        return "claim"
    if waiting.startswith(FACILITY_WAIT) or is_facility_query(waiting):
        return "facility"
    if waiting.startswith((EMERGENCY_WAIT, SIZE_WAIT)):
        return ""
    return "satellite" if place_route(waiting) or area_route(waiting) else "question"


async def _emergency(key: str, lang: str, d: em.Detection, store: UserStore, settings: Settings,
                     emergency_fn: EmergencyFn, spot: Spot | None = None, first: bool = True,
                     notify: NotifyFn | None = None) -> list[Out]:
    """The fast path (section 7): get help now, the verified numbers only, the nearest suitable facility and its pin
    when a point or LGA is known, else the location request. No medical instructions; no model; only that it
    fired is logged. From a point, the fast reply goes through `notify` at once (returned first when there is
    none) and the road-distance follow-up is returned."""
    t0 = time.perf_counter()
    if first:
        store.count_event("emergency_fast_path")      # a count per day for the admin status page; no key, no text
    lang = lang if lang in em.WORDS else "ha"
    w = em.WORDS[lang]
    spot = spot or location_memory.recall(key)
    last = None if spot else store.get_last_lga(key)
    lines = ([w["now_if" if d.conditional else "now"]] if first else []) + em.contact_lines(lang, lga=spot.lga if spot else name_of(last or ""))
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
                      facility_fn: FacilityFn, reading=None) -> list[Out] | None:
    """A facility question or a follow-up to one; None when the message is neither. Without a point: a place the
    question names ("nearest clinic in Gwadabawa"), else the location request, the question kept for the pin.
    `reading`: the understanding step's reading, whose care, level and ownership choose the facilities."""
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
            search.filters, search.skip = reading_filters(reading, text, search.filters), 0
        search.profile = profile_from(text, search.profile)
        log.info("facility follow-up: %s", step)
        return await _facility_replies(spot, search, lang, settings, facility_fn, "route" if step == "route" else "list",
                                       key)
    if document_question(text):          # a publisher, survey or report named: the document path answers
        return None                      # (the planner may add registry data as a supplement; app/agent/routing.py)
    from app.agent.deep import deep_question
    if deep_question(text):              # 'the state of PHCs': a deep analysis, never the registry's one-line count
        return None
    if other_subject(text) and not is_facility_query(text):   # staff, equipment, services, money AT facilities
        return None                      # are the planner's (the nearest-facility search still takes 'nearest')
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
    if spot is None:                     # the search waits for the pin with the filters chosen now
        _wait_for_search(key, text, reading_filters(reading, text))
        return [Out(FAC_WORDS.get(lang, FAC_WORDS["en"])["need_location"], lang=lang, location_request=True)]
    return await _facility_search(text, key, lang, settings, facility_fn, spot, reading)


async def _named_facility(text: str, key: str, lang: str, settings: Settings, facility_fn: FacilityFn,
                          spot: Spot | None) -> list[Out] | None:
    """A facility the message names ('What about Arkilla PHC'): its registry card, kept as the facility a follow-up
    means; with 'go to' / 'how far': the route to it from the point, or the location request when there is none."""
    if not (text or "").strip() or not settings.has_database or not (FACILITY_WORD.search(text) or ROUTE_TO.search(text)):
        return None
    # unambiguous intent only ('where is', 'how far', 'what about X', 'is X open'): "What did UNFPA find out about
    # health facilities in Wamakko" matched the LGA and a facility word and got a facility card (1 Nov 2026)
    if document_question(text) or not (facility_intent(text) or ROUTE_TO.search(text)):
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


def _needs_understanding(text: str, key: str, store: UserStore, settings: Settings) -> bool:
    """Every message is understood except fixed commands and replies to a pending read-back, choice or offer."""
    n = _norm(text)
    if MAP_ONLY.match(text) or n in IMAGE_COMMANDS or n in SHOW_QUOTES or n in SHOW_WORKING or n in FULL_BRIEF:
        return False
    if store.get_pending(key, settings.kasafi_pending_ttl_minutes) or store.get_pending_clarify(key) or \
            store.get_pending_calc(key) or store.get_pending_options(key):
        return False
    return quick_resolve(text) is None


def _place_for(key: str, store: UserStore) -> dict | None:
    """The user's point (memory, 30 min) or LGA on file, as the answer paths take it; None when there is none."""
    spot, last = location_memory.recall(key), store.get_last_lga(key)
    place = ({"lat": spot.lat, "lon": spot.lon, "lga_pcode": spot.lga_pcode, "lga": spot.lga, "ward": spot.ward,
              "wardcode": spot.wardcode, "ward_likely": spot.ward_likely} if spot else
             {"lga_pcode": last} if last else None)
    if spot and spot.how == "pin":              # a farm pin: the shape the user gave, or ask when none can be drawn
        place["shape"] = location_memory.shape(key)
        place["ask_size"] = True
    return place


# with no reading (the understanding step failed): the plain self-questions, the whole message only
ABOUT_KASAFI = re.compile(r"(?i)^\s*(?:who are you|what are you|what can you do|how does (?:this|it) work|"
                          r"who (?:made|built|created) you|are you a (?:bot|robot|person|human)|is this a bot|help|"
                          r"hello|hi|thanks?(?: you)?|kai wa[ny]e ?ne|ke wa[cy]e ?ce|me za ka iya yi|wa ya yi ka|"
                          r"good (?:morning|afternoon|evening)|bye|goodbye|assalamu alaikum|ina kwana|ina wuni|"
                          r"sai anjima|sannu(?: da \w+)?|na gode)\s*[?.!]*\s*$")
# a claim that a facility is nearer than another: checked by road, never searched in documents
CLOSER = re.compile(r"(?i)\b(?:closer|nearer|ya fi kusa|ta fi kusa|fi kusa da)\b")
REQUEST_WORDS = re.compile(r"(?i)\b(?:what|how|which|when|where|who|why|show|list|give|tell|find|send|is|are|does|"
                           r"nawa|mene|menene|wane|wace|wanne|ina|yaya|yaushe|nuna|ba ni|fa[ɗd]a|budget|kasafi\w*)\b")
# the user's own 'if' (a fallback when the reading's reason doesn't say 'conditional')
IF_WORDS = re.compile(r"(?i)\b(?:if|in case|idan|in har|ko da)\b")
CLAIM_WAIT = "facility-claim:"     # a facility claim waiting for the user's location: the facility's name follows
PLACE_BUDGET_WAIT = "place-budget:"  # a place-budget reading waiting for a location: its restatement follows
FACILITY_WAIT = "facility-search:"  # a facility reading waiting for a location: the message follows


def reading_filters(u, text: str, base: Filters = Filters()) -> Filters:
    """The facilities a search is for, from the understanding step's reading (care, level, ownership), on top of
    `base` (a follow-up keeps its list's filters unless the reading changes them): 'where can my wife deliver a
    baby' is maternal care whatever the words. The keyword filters (filters_from) only when there is no reading."""
    if u is None or u.capability != "facility" or not u.care:
        return filters_from(text, base)
    f = base
    if u.ownership in ("public", "private"):
        f = replace(f, ownership=u.ownership.title())
    if u.facility_level == "hospital":
        f = replace(f, levels=("Secondary", "Tertiary"))
    elif u.facility_level == "primary":
        f = replace(f, levels=("Primary",))
    if u.care == "maternal":
        f = replace(f, emonc=f.emonc or "bemonc")
    return f


def _wait_for_search(key: str, words: str, filters: Filters) -> None:
    """A facility search waiting for the location, with the filters the reading chose (the pin resumes it)."""
    location_memory.wait_for_location(key, FACILITY_WAIT + json.dumps(
        {"q": words[:600], "levels": list(filters.levels), "own": filters.ownership, "emonc": filters.emonc}))


def _waiting_search(question: str) -> FacilitySearch:
    d = json.loads(question[len(FACILITY_WAIT):])
    return FacilitySearch(Filters(levels=tuple(d.get("levels") or ()), ownership=d.get("own") or "",
                                  emonc=d.get("emonc") or ""), profile=profile_from(d.get("q") or ""))


READING_WAIT = "reading:"          # a menu row or 'Send location' waiting for the location: the reading (JSON) follows
MENU_WORDS = {"menu", "/menu", "zaɓi", "zabi", "zaɓuɓɓuka", "zabubbuka"}   # with no reading (the step failed)
ANSWER_BUTTONS = {menu.BTN_WORKING, menu.BTN_BRIEF, menu.BTN_LANG, menu.BTN_LOCATION, menu.BTN_MENU}
LAST_READING_S = 1800
_last_reading: dict[str, tuple[float, Any]] = {}   # key -> (time, the last answered reading): in memory only


def menu_out(lang: str) -> Out:
    p = menu.menu_payload(lang)
    return Out(p["body"], lang=lang, menu={"button": p["button"], "sections": p["sections"]})


CHANGE_WAIT = "change-map:"        # a change map waiting for the location: '<measure>:<area>' follows


def _change_checks(settings: Settings) -> list[str]:
    """The change-map measures whose data check passes (app/place/change.py: checks)."""
    import psycopg
    from app.place import change
    with psycopg.connect(settings.db_url(), connect_timeout=5) as conn:
        ok = change.checks(conn)
    return [m for m in change.MEASURES if ok.get(m)]


async def _change_measures(lang: str, settings: Settings) -> Out:
    w = menu.change_words(lang)
    try:
        available = await asyncio.to_thread(_change_checks, settings) if settings.has_database else []
    except Exception as e:                       # noqa: BLE001 - no database: say so, never a broken list
        log.warning("change map checks failed: %s", type(e).__name__)
        available = []
    if not available:
        return Out(w["none"], lang=lang)
    p = menu.change_measures(lang, available)
    return Out(p["body"], lang=lang, menu={"button": p["button"], "sections": p["sections"]})


async def _change_row(rid: str, key: str, lang: str, store: UserStore, settings: Settings) -> list[Out]:
    """A measure picked: the areas it has data for. An area picked: the map, from the place on file; an area that
    needs a place with none on file asks for the location and draws the map when it comes."""
    from app.place import change
    w = menu.change_words(lang)
    if rid.startswith(menu.CHANGE_MEASURE):
        measure = rid[len(menu.CHANGE_MEASURE):]
        if measure not in change.MEASURES:
            return [await _change_measures(lang, settings)]
        p = menu.change_areas(lang, measure, change.areas_for(measure, _change_place(key, store)))
        return [Out(p["body"], lang=lang, menu={"button": p["button"], "sections": p["sections"]})]
    measure, _, area = rid[len(menu.CHANGE_AREA):].partition("_")
    if measure not in change.MEASURES or area not in change.OFFER[measure]:
        return [await _change_measures(lang, settings)]
    place = _change_place(key, store)
    needs_pin = area in ("spot", "5km", "ward") or (area == "lga" and not place.get("lga_pcode"))
    if needs_pin and place.get("lat") is None:
        location_memory.wait_for_location(key, f"{CHANGE_WAIT}{measure}:{area}")
        return [Out(w["need_place"], lang=lang, location_request=True)]
    return await _change_draw(measure, area, place, lang, settings)


def _change_place(key: str, store: UserStore) -> dict:
    spot = location_memory.recall(key)
    if spot is not None:
        return {"lat": spot.lat, "lon": spot.lon, "lga_pcode": spot.lga_pcode, "wardcode": spot.wardcode}
    last = store.get_last_lga(key)
    return {"lga_pcode": last} if last else {}


async def _change_draw(measure: str, area: str, place: dict, lang: str, settings: Settings) -> list[Out]:
    from app.agent.answer import lagos_today
    from app.place import change

    def draw() -> list:
        import psycopg
        with psycopg.connect(settings.db_url(), connect_timeout=5) as conn:
            spec = change.spec_for(conn, measure, area, place)
        return render_specs(settings, [spec], lang, lagos_today()) if spec else []
    try:
        maps = await asyncio.wait_for(asyncio.to_thread(draw), 60)
    except Exception as e:                       # noqa: BLE001 - a map that can't be drawn is said, never silence
        log.warning("change map failed: %s", type(e).__name__)
        maps = []
    log.info("change map: %s, %s: %s", measure, area, "drawn" if maps else "not drawn")
    if not maps:
        return [Out(menu.change_words(lang)["no_map"], lang=lang)]
    return [Out(m.caption, lang=lang, image=m.jpeg) for m in maps]


def _wait_with_reading(key: str, u) -> None:
    location_memory.wait_for_location(key, READING_WAIT + json.dumps(
        {k: v for k, v in u.to_dict().items() if k not in ("safety", "seconds")}))


def reading_from_wait(waiting: str):
    from app.agent.understand import Understanding
    return Understanding(**json.loads(waiting[len(READING_WAIT):]))


def _remember_reading(key: str, u) -> None:
    now = time.time()
    _last_reading[key] = (now, u)
    for k in [k for k, (at, _) in _last_reading.items() if now - at > LAST_READING_S]:
        _last_reading.pop(k, None)


def _last(key: str):
    at, u = _last_reading.get(key, (0.0, None))
    return u if time.time() - at <= LAST_READING_S else None


PLACE_CAPABILITIES = {"place_budget", "place_history", "hazard", "facility"}


def _add_buttons(outs: list[Out], lang: str, result, u, question: str, place: dict | None) -> None:
    """Reply buttons under an answer (at most 3; 'Menu' when nothing else applies). On the answer itself when it is
    one message of 1,024 characters or fewer with no images; otherwise on a short last message ('Anything else?'),
    so the answer is never cut and the buttons come after its images."""
    asked_in = detect_language(question)
    needs_location = u is not None and (u.capability in PLACE_CAPABILITIES or u.level in ("pin", "ward", "lga")) \
        and not (place and place.get("lat") is not None)
    buttons = menu.answer_buttons(lang, working=bool(getattr(result, "working", "")),
                                  brief=getattr(result, "deep", None) is not None,
                                  other_lang=bool(asked_in) and asked_in != lang, needs_location=needs_location)
    first = outs[0]
    if len(outs) == 1 and not first.crops and not first.buttons and len(first.text) <= menu.BODY_WITH_BUTTONS:
        first.buttons = buttons
    else:
        outs.append(Out(menu.words(lang)["anything_else"], buttons, lang=lang))


async def _menu_row(row: str, key: str, lang: str, settings: Settings) -> tuple:
    """(replies, None, '', lang) for a row with a reply of its own; (None, reading, restatement, lang) for a row that
    enters the pipeline. A row that needs a place uses the point of the last 30 minutes, else asks for it."""
    from app.agent.understand import Understanding
    from app.whatsapp.messages import PRIVACY_URL
    w = menu.words(lang)
    if row == "menu_docs":
        return [Out(w["docs"], lang=lang)], None, "", lang
    if row == "menu_lang":
        return [Out(w["lang"], LANG_BUTTONS, lang=lang)], None, "", lang
    if row == "menu_privacy":
        return [Out(w["privacy"].format(url=PRIVACY_URL), lang=lang)], None, "", lang
    if row == "menu_about":
        u = Understanding(kind="chitchat", capability="conversation", restatement=w["about"])
        return None, u, w["about"], lang
    if row == "menu_change":
        return [await _change_measures(lang, settings)], None, "", lang
    u = menu.reading_for(row)
    if location_memory.recall(key) is None:
        if u.capability == "facility":
            _wait_for_search(key, u.restatement, Filters())
        else:
            _wait_with_reading(key, u)
        return [Out(w["need_place"][row], lang=lang, location_request=True)], None, "", lang
    return None, u, u.restatement, lang


async def _answer_button(button: str, key: str, lang: str, store: UserStore) -> tuple:
    """A reply button under an answer, as the command it stands for (typed words still work)."""
    w = menu.words(lang)
    if button == menu.BTN_WORKING:
        return None, None, "show working", lang
    if button == menu.BTN_BRIEF:
        return None, None, "full brief", lang
    if button == menu.BTN_MENU:
        return [menu_out(lang)], None, "", lang
    last = _last(key)
    if button == menu.BTN_LOCATION:
        if last is not None:            # the answer that wanted a pin is answered again when it comes
            _wait_with_reading(key, last)
        return [Out(w["send_location"], lang=lang, location_request=True)], None, "", lang
    other = "en" if lang == "ha" else "ha"   # BTN_LANG: switch, and the same question answered in the other language
    store.set_lang(key, other)
    if last is None:
        return [Out(t("lang_set", other), lang=other)], None, "", other
    return None, last, last.restatement, other


FIRST_TTL_S = 1800
# before consent no model may read the message, so a bare greeting is told apart by its words alone
GREETING = re.compile(r"(?i)^\s*(?:hello|hi|hey|good (?:morning|afternoon|evening)|sannu(?: da \w+)?|"
                      r"assalamu alaikum|salam|ina kwana|ina wuni|barka da \w+)\s*[.!]*\s*$")
# a message sent before consent: kept in memory only (never sent to a model before consent, never written to disk),
# for 30 minutes, and handled right after the user accepts; DELETE MY DATA drops it
_first_messages: dict[str, tuple[float, dict]] = {}


def _keep_first(key: str, msg: dict) -> None:
    """Keep the first question sent before consent (not the consent words, buttons or later messages)."""
    if key in _first_messages or msg.get("type") not in ("text", "audio") or _button_id(msg):
        return
    body = ((msg.get("text") or {}).get("body") or "") if msg.get("type") == "text" else ""
    if msg.get("type") == "text" and (not body.strip() or _norm(body) in CONSENT_TEXTS or
                                      LANG_COMMANDS.get(_norm(body)) or GREETING.match(body)):
        return                     # a bare greeting opened the conversation: nothing to answer after consent
    now = time.time()
    _first_messages[key] = (now, {**msg, "id": f"{msg.get('id', '')}-after-consent"})
    for k in [k for k, (at, _) in _first_messages.items() if now - at > FIRST_TTL_S]:
        _first_messages.pop(k, None)


def _kept_first(key: str) -> dict | None:
    at, msg = _first_messages.pop(key, (0.0, None))
    return msg if msg is not None and time.time() - at <= FIRST_TTL_S else None


def sweep_first_messages() -> int:
    """Deletes every kept first message past its 30 minutes (app/maintenance.py). Returns how many went."""
    now = time.time()
    old = [k for k, (at, _) in list(_first_messages.items()) if now - at > FIRST_TTL_S]
    for k in old:
        _first_messages.pop(k, None)
    return len(old)


def place_budget_reading(waiting: str):
    """The reading a place-budget question resumes with once the location has come."""
    from app.agent.understand import Understanding
    return Understanding(kind="new", capability="place_budget", level="lga",
                         restatement=waiting.removeprefix(PLACE_BUDGET_WAIT))


def looks_like_request(text: str) -> bool:
    """A request for information ('how much…', 'nearest hospital in Tambuwal'), not 'ok' or 'hmm'."""
    text = text or ""
    return "?" in text or bool(re.search(r"\d", text)) or len(text.split()) >= 4 or bool(REQUEST_WORDS.search(text))


def claim_reading(text: str, name: str = ""):
    """A facility claim's reading when the understanding step gave none (the facility found by its name in it)."""
    from app.agent.understand import Understanding
    return Understanding(kind="correction", capability="facility", level="facility", name=name, restatement=text)


async def _conversational(text: str, key: str, lang: str, store: UserStore, settings: Settings, u) -> list[Out]:
    from app.agent.conversational import reply
    t0 = time.perf_counter()
    # a name the user stated within the last hour (memory only, app/privacy.py): the reply may use it once, in a
    # greeting or thanks; what is kept (the follow-up history, the trace) carries '[name removed]' instead
    name = name_memory.recall(key)
    body, how = await reply(strip_location(text), lang, store.recent_turns(key), _place_for(key, store), settings,
                            **({"name": name} if name else {}))
    outs = [Out(body, lang=lang)]
    kept = [Out(strip_name(body, name), lang=lang)] if name else outs
    _remember_turn(store, key, lang, text, kept)
    log.info("conversational reply (%s) in %.2fs", how, time.perf_counter() - t0)
    await _trace_route(settings, text, lang, f"conversation:{how}", u, kept, time.perf_counter() - t0)
    return outs


async def _trace_emergency(settings: Settings, lang: str, layer: str, safety: dict, consented: bool) -> None:
    """A trace row that the fast path fired and which layer fired it (phrase, classifier, understanding), with what
    each layer said. As the fast path's own logging: never the message, the reason or the place."""
    if not settings.has_database:
        return
    from app.agent.trace import save_event
    # on a daemon thread: the reply never waits for the trace, nor does anything that ends the event loop
    import threading
    threading.Thread(target=save_event, daemon=True,
                     args=(settings, "(emergency: message not kept)", lang, "emergency", f"emergency:{layer}",
                           {"route": f"emergency:{layer}", "safety": safety, "consented": consented}, 0.0)).start()


async def _trace_route(settings: Settings, text: str, lang: str, route: str, u, outs: list[Out],
                       seconds: float) -> None:
    """A trace row for a reply from a route of its own, with the reading that sent it there (admin traces page)."""
    if not settings.has_database:
        return
    from app.agent.trace import save_event
    detail = {**({"understanding": u.to_dict()} if u is not None else {}), "route": route,
              "timings": {"route": round(seconds, 2), **({"understanding": round(u.seconds, 2)} if u else {})}}
    await asyncio.to_thread(save_event, settings, strip_location(text), lang, "answered", route, detail,
                            seconds + (u.seconds if u is not None else 0.0),
                            "\n".join(o.text for o in outs if getattr(o, "text", "")))


def _remember_turn(store: UserStore, key: str, lang: str, question: str, outs: list[Out]) -> None:
    """A shortcut's reply (a facility list, a correction) kept as a turn, so the next message is read with it."""
    body = "\n".join(o.text for o in outs if getattr(o, "text", ""))
    if body:
        store.add_turn(key, lang, question, body[:2000], [], "", "")


# well-known abbreviations people use for facilities ('UDUTH is closer'): the registry spells the names out
FACILITY_ALIASES = {"uduth": "Usman Danfodio University Teaching Hospital",
                    "sosuth": "Sokoto State University Teaching Hospital",
                    "sokoto specialist": "Specialist Hospital Sokoto"}
CORRECTION_WORDS = {
    "en": {"closer": "You're right: {name} is closer to you than the ones I listed.",
           "not_closer": "{first} is still the closest of these to you by road.",
           "where": "{name}: {road} by road from your pin ({km} km in a straight line).",
           "first": "The nearest I listed, {first}: {road} by road.",
           "why_filter": "It wasn't in the list because the search was for {what}.",
           "why_line": "It wasn't in the list because I take the {k} nearest in a straight line before checking "
                       "road time, and it is {km} km away in a straight line.",
           "no_road": "{name} is {km} km from your pin in a straight line (road time unavailable now).",
           "why_missed": "It should have been in the list: it is nearer than the ones I gave.",
           # a claim with no list before it ('But UDUTH is closer to me' as a first message)
           "need_location": "To check whether {name} is the closest to you, I need your location: share it, or "
                            "tell me your LGA or town.",
           "from_lga": "I don't have your exact location, so I measured from the centre of {lga} LGA (your LGA on "
                       "file). Share your location for an exact answer.",
           "where_lga": "{name}: {road} by road from the centre of {lga} LGA ({km} km in a straight line).",
           "no_road_lga": "{name} is {km} km from the centre of {lga} LGA in a straight line (road time "
                          "unavailable now).",
           "other": "The nearest other {what}, {first}: {road} by road.",
           "other_km": "The nearest other {what}, {first}: {km} km in a straight line.",
           "cold_closer": "You're right: {name} is the closest {what} to {you}.",
           "cold_not_closer": "{first} is closer to {you} than {name}.",
           "you": "you", "you_lga": "the centre of {lga} LGA", "hospital": "hospital", "facility": "health facility"},
    "ha": {"closer": "Gaskiya ne: {name} ya fi kusa da kai fiye da waɗanda na lissafa.",
           "not_closer": "{first} ne har yanzu mafi kusa da ku ta hanya.",
           "where": "{name}: {road} ta hanya daga wurinku ({km} km a mike).",
           "first": "Mafi kusa da na lissafa, {first}: {road} ta hanya.",
           "why_filter": "Ba ya cikin jerin saboda binciken na {what} ne.",
           "why_line": "Ba ya cikin jerin saboda ina ɗaukar {k} mafi kusa a mike kafin in duba lokacin tafiya ta "
                       "hanya, kuma yana da {km} km a mike.",
           "no_road": "{name} yana da {km} km daga wurinku a mike (ba a samu lokacin tafiya ta hanya yanzu ba).",
           "why_missed": "Ya kamata ya kasance cikin jerin: ya fi waɗanda na bayar kusa.",
           "need_location": "Don in duba ko {name} ne mafi kusa da ku, ina buƙatar wurinku: ku raba shi, ko ku faɗa mini "
                            "ƙaramar hukumarku ko garinku.",
           "from_lga": "Ba ni da ainihin wurinku, don haka na auna daga tsakiyar ƙaramar hukumar {lga} (wadda ke "
                       "rubuce a wurina). Ku raba wurinku don amsa daidai.",
           "where_lga": "{name}: {road} ta hanya daga tsakiyar ƙaramar hukumar {lga} ({km} km a mike).",
           "no_road_lga": "{name} yana da {km} km daga tsakiyar ƙaramar hukumar {lga} a mike (ba a samu lokacin "
                          "tafiya ta hanya yanzu ba).",
           "other": "Wani {what} mafi kusa, {first}: {road} ta hanya.",
           "other_km": "Wani {what} mafi kusa, {first}: {km} km a mike.",
           "cold_closer": "Gaskiya ne: {name} ne {what} mafi kusa da {you}.",
           "cold_not_closer": "{first} ya fi {name} kusa da {you}.",
           "you": "ku", "you_lga": "tsakiyar ƙaramar hukumar {lga}", "hospital": "asibiti",
           "facility": "cibiyar lafiya"},
}


def _lga_centre(settings: Settings, pcode: str) -> tuple[float, float] | None:
    import psycopg

    from app.geo.facilities import lga_point
    with psycopg.connect(settings.db_url(), connect_timeout=5) as conn:
        return lga_point(conn, pcode)


async def _facility_correction(u, key: str, lang: str, settings: Settings, facility_fn: FacilityFn,
                               store: UserStore | None = None, spot: Spot | None = None) -> list[Out] | None:
    """'But UDUTH is closer to me': the named facility's road distance from the pin, checked against the list just
    given, and why it wasn't in it (the search's filter, or the straight-line shortlist before road time). With no
    list (a cold claim, 2 Nov trace #123): against the nearest others of its kind, from the pin, or from the centre of
    the LGA on file (said so); with neither, the location is asked for and the check runs when it comes. None when
    no facility is named (the message then goes on as usual)."""
    from app.geo.facilities import distance_text
    from app.geo.facilities import _query as nearest_query
    spot = spot or location_memory.recall(key)
    search = location_memory.last_search(key)
    asked = (u.name or "").strip()
    name = FACILITY_ALIASES.get(asked.lower(), asked)
    try:
        hits = await asyncio.to_thread(lookup, settings, name or u.restatement)
    except Exception as e:          # noqa: BLE001
        log.warning("facility lookup failed: %s", type(e).__name__)
        return None
    if not name:                    # no name read: only a facility the message names for certain
        hits = [h for h in hits if h.score >= NAMED]
    if not hits:
        return None
    w = CORRECTION_WORDS.get(lang, CORRECTION_WORDS["en"])
    listed = spot is not None and search is not None and bool(search.shown)
    levels = set(search.filters.levels) if listed else set()
    pick = next((h for h in hits if not levels or h.level in levels), hits[0])
    lga = ""
    if spot is None:
        last = store.get_last_lga(key) if store is not None else None
        point = await asyncio.to_thread(_lga_centre, settings, last) if last else None
        if point is None:
            location_memory.wait_for_location(key, CLAIM_WAIT + pick.name)
            return [Out(w["need_location"].format(name=pick.name), lang=lang, location_request=True)]
        lga = name_of(last) or last
        spot = Spot(point[0], point[1], last, lga, how="lga")
    f = as_facility(pick, spot.lat, spot.lon)
    if not listed:
        return await _facility_claim(f, pick, spot, lga, key, lang, settings, w, nearest_query)
    first = search.shown[0]
    await add_routes(settings, spot.lat, spot.lon, [f, first], search.profile)
    w = CORRECTION_WORDS.get(lang, CORRECTION_WORDS["en"])
    lines = []
    if f.minutes is not None and first.minutes is not None:
        lines.append(w["where"].format(name=f.name, road=distance_text(lang, f, search.profile), km=f.km))
        lines.append(w["first"].format(first=first.name, road=distance_text(lang, first, search.profile)))
        closer = f.minutes < first.minutes
    else:
        lines.append(w["no_road"].format(name=f.name, km=f.km))
        closer = f.km < first.km
    lines.append(w["closer"].format(name=f.name) if closer else w["not_closer"].format(first=first.name))
    if f.fid not in {x.fid for x in search.shown}:
        if levels and pick.level not in levels or search.filters.ownership and pick.ownership != search.filters.ownership:
            lines.append(w["why_filter"].format(what=search.filters.describe(lang) or "another kind of facility"))
        elif f.km > max(x.km for x in search.shown):
            lines.append(w["why_line"].format(k=len(search.shown), km=f.km))
        else:                       # nearer than every one listed and not filtered out: the list was wrong
            lines.append(w["why_missed"])
    search.shown = [f] + [x for x in search.shown if x.fid != f.fid]     # 'route?' now means this one
    location_memory.remember_search(key, search)
    log.info("facility correction checked: %s, closer=%s", f.lga, closer)
    return [Out("\n".join(lines), lang=lang)]


async def _facility_claim(f, pick, spot: Spot, lga: str, key: str, lang: str, settings: Settings, w: dict,
                          nearest_query) -> list[Out]:
    """A claim with no list before it: the named facility against the nearest others of its kind (hospitals for a
    hospital), by road from the point (the pin, or the LGA's centre when `lga` is set)."""
    from app.geo.facilities import Filters, distance_text
    hospital = pick.level in ("Secondary", "Tertiary") or "hospital" in f"{pick.kind} {pick.name}".lower()
    search = FacilitySearch(Filters(levels=("Secondary", "Tertiary")) if hospital else Filters())
    try:
        near = await asyncio.to_thread(nearest_query, settings, spot.lat, spot.lon, search.filters, 0)
    except Exception as e:          # noqa: BLE001 - PostGIS down: the named facility's distance alone
        log.warning("nearest facilities failed: %s", type(e).__name__)
        near = []
    others = [x for x in near if x.fid != f.fid][:3]
    await add_routes(settings, spot.lat, spot.lon, [f, *others], search.profile)
    routed = f.minutes is not None and all(x.minutes is not None for x in others)
    what = w["hospital" if hospital else "facility"]
    you = w["you_lga"].format(lga=lga) if lga else w["you"]
    lines = [w["from_lga"].format(lga=lga)] if lga else []
    road = distance_text(lang, f, search.profile)
    lines.append(w["where_lga"].format(name=f.name, road=road, km=f.km, lga=lga) if lga and routed else
                 w["no_road_lga"].format(name=f.name, km=f.km, lga=lga) if lga else
                 w["where"].format(name=f.name, road=road, km=f.km) if routed else
                 w["no_road"].format(name=f.name, km=f.km))
    if not others:
        search.shown = [f]
    else:
        measure = (lambda x: x.minutes) if routed else (lambda x: x.km)
        best = min(others, key=measure)
        lines.append(w["other"].format(what=what, first=best.name, road=distance_text(lang, best, search.profile))
                     if routed else w["other_km"].format(what=what, first=best.name, km=best.km))
        closer = measure(f) <= measure(best)
        lines.append(w["cold_closer"].format(name=f.name, what=what, you=you) if closer else
                     w["cold_not_closer"].format(first=best.name, name=f.name, you=you))
        search.shown = [f, best] if closer else [best, f]          # 'route?' now means the nearer one
        log.info("facility claim checked: %s, closer=%s, from %s", f.lga, closer, "the LGA" if lga else "the pin")
    location_memory.remember_search(key, search)
    return [Out("\n".join(lines), lang=lang)]


async def _facility_reading(text: str, u, key: str, lang: str, settings: Settings, facility_fn: FacilityFn,
                            spot: Spot | None = None) -> list[Out] | None:
    """A facility reading with no name, count or 'nearest' words the shortcut knows: the facility the reading names
    (its registry card), else a nearest search of the kind the words ask for (maternity, hospitals, government…)
    from the point; with no point, the location is asked for and the search runs when it comes."""
    words = f"{text} {u.restatement}"
    # a name the reading gives is a facility only when its subject is one: at pin, ward, LGA or state level the
    # name is the user's place (4 Nov: 'nearest clinic to my ward' with name 'Gumbi' matched Gumbi Health Clinic)
    if u.name and u.level not in ("pin", "ward", "lga", "state"):
        name = FACILITY_ALIASES.get(u.name.strip().lower(), u.name)
        try:
            hits = await asyncio.to_thread(lookup, settings, name)
        except Exception as e:      # noqa: BLE001 - PostGIS down: the message goes on as usual
            log.warning("facility lookup failed: %s", type(e).__name__)
            return None
        if hits and hits[0].score >= NAMED:
            f, others = hits[0], [h for h in hits[1:] if h.score >= NAMED - 0.05][:3]
            spot = spot or location_memory.recall(key)
            location_memory.remember_search(key, FacilitySearch(
                shown=[as_facility(f, spot.lat if spot else None, spot.lon if spot else None)]))
            log.info("facility from the reading: %s LGA", f.lga)
            return [Out(card(f, lang, others), lang=lang)]
    spot = spot or location_memory.recall(key)
    filters = reading_filters(u, words)                # care, level and ownership from the reading
    if spot is None:
        _wait_for_search(key, words, filters)
        return [Out(FAC_WORDS.get(lang, FAC_WORDS["en"])["need_location"], lang=lang, location_request=True)]
    search = FacilitySearch(filters, profile=profile_from(words))
    location_memory.remember_search(key, search)
    log.info("facility search from the reading: %s LGA, care %s", spot.lga, u.care or "-")
    return await _facility_replies(spot, search, lang, settings, facility_fn, "list", key)


async def _after_location(question: str, key: str, lang: str, settings: Settings, facility_fn: FacilityFn,
                          spot: Spot) -> list[Out]:
    """The question that asked for a location, answered now that there is one: a nearest-facility search, a route
    to a named facility, 'how far is it' for the facility last shown, or a facility claim ('UDUTH is closer')."""
    if question.startswith((READING_WAIT, CHANGE_WAIT)):   # a menu row's reading or a change map: the caller's
        return []
    if question.startswith(CLAIM_WAIT):
        name = question[len(CLAIM_WAIT):]
        return await _facility_correction(claim_reading(name, name), key, lang, settings, facility_fn,
                                          spot=spot) or []
    if question.startswith(FACILITY_WAIT):     # a facility search that waited for the location, its filters kept
        search = _waiting_search(question)
        location_memory.remember_search(key, search)
        return await _facility_replies(spot, search, lang, settings, facility_fn, "list", key)
    if is_facility_query(question):
        return await _facility_search(question, key, lang, settings, facility_fn, spot)
    if (named := await _named_facility(question, key, lang, settings, facility_fn, spot)):
        return named
    search = location_memory.last_search(key)
    if search is not None and search.shown and follow_up(question) == "route":
        return await _facility_replies(spot, search, lang, settings, facility_fn, "route", key)
    return []


async def _facility_search(question: str, key: str, lang: str, settings: Settings, facility_fn: FacilityFn,
                           spot: Spot, reading=None) -> list[Out]:
    """A new search for the question (the reading's filters, else the words'; its travel mode) from the point; []
    when it isn't one."""
    if not is_facility_query(question):
        return []
    search = FacilitySearch(reading_filters(reading, question), profile=profile_from(question))
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
MAP_DEADLINE_S = 30.0       # an answer's maps: drawn within this, after the text has gone, or a note says so
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
