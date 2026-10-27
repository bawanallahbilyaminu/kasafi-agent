"""Turns one incoming WhatsApp message into the replies to send.

Order matters:
1. Delete command and medical emergency: for everyone, consented or not. Both are local checks; no model.
2. Access gate: KASAFI_OPEN_ACCESS, or only KASAFI_PILOT_NUMBERS when it's false.
3. Language commands (/hausa, /english, Hausa, English, Turanci, or the buttons).
4. Consent: on first contact nothing goes to any model. The user gets the bilingual notice
   with [OK / Na yarda] [Hausa] [English] buttons, and stays there until they agree.
5. After consent: per-number daily limits and the global spend cap, then the actual work.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from app.config import Settings
from app.data_rights import DELETED_REPLY, delete_user_data, is_delete_command
from app.guardrails.emergency import EMERGENCY_REPLY, is_medical_emergency
from app.language import detect_language
from app.users import UserStore, user_key
from app.whatsapp.client import mask_phone
from app.whatsapp.messages import LANG_BUTTONS, NOT_IN_PILOT, NOTICE_BUTTONS, first_contact_notice, t
from app.whatsapp.voice import is_pilot, reply_for_voice

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


def _notice(lang: str | None, source: str | None) -> Out:
    return Out(first_contact_notice(lang, source), NOTICE_BUTTONS)


VoiceFn = Callable[..., Awaitable[str]]


async def handle(msg: dict[str, Any], wa: Any, *, store: UserStore, settings: Settings,
                 voice_fn: VoiceFn = reply_for_voice) -> list[Out]:
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
        return [Out(t("lang_set", chosen))] if user.consented else [_notice(chosen, "chosen")]

    # 4. Consent
    if user is None:
        user = store.create(key, detect_language(text) if text else None)
        if not (button == "consent_ok" or _norm(text) in CONSENT_TEXTS):
            log.info("first contact from %s: consent notice sent (lang=%s)", mask_phone(sender), user.lang)
            return [_notice(user.lang, user.lang_source)]
    if not user.consented:
        if button == "consent_ok" or _norm(text) in CONSENT_TEXTS:
            store.give_consent(key)
            log.info("consent given by %s", mask_phone(sender))
            if user.lang is None:
                return [Out(t("consent_thanks_ask_lang", None), LANG_BUTTONS)]
            return [Out(t("consent_thanks", user.lang))]
        return [_notice(user.lang, user.lang_source)]

    # 5. Consented: limits, then work
    lang = user.lang or "ha"
    voice_used, questions_used = store.usage(key)
    if kind == "audio":
        if voice_used >= settings.kasafi_voice_per_day:
            return [Out(t("voice_limit", lang, n=settings.kasafi_voice_per_day))]
        if store.spent_today() + settings.kasafi_cost_per_voice_usd > settings.kasafi_daily_spend_cap_usd:
            log.warning("daily spend cap reached")
            return [Out(t("busy", lang))]
        store.count(key, "voice")
        store.add_spend(settings.kasafi_cost_per_voice_usd)
        return [Out(await voice_fn(msg, wa, lang=lang, settings=settings))]
    if kind == "text":
        if questions_used >= settings.kasafi_questions_per_day:
            return [Out(t("question_limit", lang, n=settings.kasafi_questions_per_day))]
        store.count(key, "questions")
        # Text answers don't call a model yet. When the agent lands, check the spend cap and
        # add_spend(kasafi_cost_per_question_usd) here, as for voice.
        return [Out(t("echo", lang, text=text[:500]))]
    if button == "consent_ok":
        return [Out(t("consent_thanks", lang))]
    return [Out(t("other", lang))]
