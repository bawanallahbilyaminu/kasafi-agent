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

import logging
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import Settings
from app.data_rights import DELETED_REPLY, delete_user_data, is_delete_command
from app.guardrails import scope
from app.guardrails.emergency import EMERGENCY_REPLY, is_medical_emergency
from app.language import detect_language
from app.providers.chat import ProviderError
from app.providers.stt import heard_texts
from app.users import UserStore, user_key
from app.whatsapp.client import mask_phone
from app.whatsapp.messages import LANG_BUTTONS, NOT_IN_PILOT, NOTICE_BUTTONS, first_contact_notice, t
from app.whatsapp.corrections import Resolution, quick_resolve, resolve
from app.agent.answer import answer_from_documents
from app.whatsapp.voice import VoiceOutcome, is_pilot, reply_for_voice

log = logging.getLogger(__name__)

LANG_COMMANDS = {"/hausa": "ha", "hausa": "ha", "/english": "en", "english": "en", "turanci": "en", "/turanci": "en"}
LANG_BUTTON_IDS = {"lang_ha": "ha", "lang_en": "en"}
CONSENT_TEXTS = {"ok", "okay", "na yarda", "na amince", "i agree", "agree", "ok na yarda"}


@dataclass
class Out:
    text: str
    buttons: list[tuple[str, str]] | None = None


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


async def _no_notify(out: Out) -> None:
    return None


async def handle(msg: dict[str, Any], wa: Any, *, store: UserStore, settings: Settings,
                 voice_fn: VoiceFn = reply_for_voice, notify: NotifyFn = _no_notify,
                 resolve_fn: ResolveFn = resolve, guard_fn: GuardFn = scope.check,
                 answer_fn: AnswerFn | None | object = _DEFAULT) -> list[Out]:
    """Returns the replies to send. `notify` sends a message right away (the "listening" ack)."""
    sender, kind = msg.get("from", ""), msg.get("type")
    text = (msg.get("text") or {}).get("body", "") if kind == "text" else ""
    button = _button_id(msg)

    # 1. Safety and data rights first
    if text and is_delete_command(text):
        delete_user_data(sender, store=store, settings=settings)
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
        await notify(Out(t("searching", lang)))   # planning + search + answer takes ~8 s
        try:
            body = await answer(question, lang, settings=settings)
        except Exception as e:  # DB or model down: tell the user rather than go silent
            log.exception("answer failed: %s", type(e).__name__)
            body = t("answer_failed", lang)
        return [Out(f"{prefix}\n\n{body}" if prefix else body)]

    async def resolution_reply(res: Resolution, pending_q: str) -> list[Out]:
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

    # 5a. Eh / A'a to a pending read-back: no model needed to decide
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
                store.clear_pending(key)
                return await resolution_reply(res, pending[0])
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
            store.clear_pending(key)
            if res.kind != "new":
                return await resolution_reply(res, pending[0])
        if refusal := await _guarded([text], lang, guard_fn, settings):
            return [refusal]
        return await respond(text[:1000], "", Out(t("echo", lang, text=text[:500])))
    if button == "consent_ok":
        return [Out(t("consent_thanks", lang))]
    return [Out(t("other", lang))]


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


