"""User-facing texts in Hausa and English, and the bilingual first-contact consent notice.

The notice must keep matching the privacy policy (docs/site/privacy.md, published at
halalnumeriq.com.ng/kasafi/privacy).
"""

PRIVACY_URL = "https://halalnumeriq.com.ng/kasafi/privacy"

BTN_CONSENT = ("consent_ok", "OK / Na yarda")
BTN_HAUSA = ("lang_ha", "Hausa")
BTN_ENGLISH = ("lang_en", "English")
NOTICE_BUTTONS = [BTN_CONSENT, BTN_HAUSA, BTN_ENGLISH]
LANG_BUTTONS = [BTN_HAUSA, BTN_ENGLISH]

_NOTICE = {
    "ha": (
        "Barka da zuwa Kasafi (gwaji). Ina amsa tambayoyi game da takardun kasafi da manufofin gwamnati.\n"
        "• Sabis ɗin AI na Meta ne ke sarrafa saƙonninka da saƙon murya. Yayin da muke amfani da kuɗin "
        "gwaji kyauta, Meta na iya amfani da su don inganta ayyukansa.\n"
        "• Kada ka tura bayanan sirri.\n"
        "• Ana goge saƙon murya bayan an mayar da shi rubutu."
    ),
    "en": (
        "Welcome to Kasafi (pilot). I answer questions about public budget and policy documents.\n"
        "• Your messages and voice notes are processed by Meta AI services. While we use free credits, "
        "Meta may use them to improve its services.\n"
        "• Don't share personal details.\n"
        "• Voice notes are deleted after transcription."
    ),
}
_LANG_LINE = {
    ("detected", "ha"): ("Bisa ga saƙonka na farko, zan riƙa amsa da Hausa. Don sauyawa, aika /english.",
                         "Based on your first message, I'll reply in Hausa. Switch any time with /english."),
    ("detected", "en"): ("Bisa ga saƙonka na farko, zan riƙa amsa da Turanci. Don sauyawa, aika /hausa.",
                         "Based on your first message, I'll reply in English. Switch any time with /hausa."),
    ("chosen", "ha"): ("Zan riƙa amsa da Hausa. Don sauyawa, aika /english.",
                       "I'll reply in Hausa. Switch any time with /english."),
    ("chosen", "en"): ("Zan riƙa amsa da Turanci. Don sauyawa, aika /hausa.",
                       "I'll reply in English. Switch any time with /hausa."),
    (None, None): ("Da wane harshe zan riƙa amsa? Danna Hausa ko English.",
                   "Which language should I reply in? Tap Hausa or English."),
}
_AGREE = ("Danna *OK / Na yarda* idan ka yarda.", "Tap *OK / Na yarda* to agree.")


def first_contact_notice(lang: str | None, source: str | None) -> str:
    """Bilingual consent and language notice. The user's language comes first; Hausa first when unknown."""
    line = _LANG_LINE.get((source or "detected", lang)) if lang else None
    ha_line, en_line = line or _LANG_LINE[(None, None)]
    ha = f"{_NOTICE['ha']}\n{ha_line}\n{_AGREE[0]}"
    en = f"{_NOTICE['en']}\n{en_line}\n{_AGREE[1]}"
    first, second = (en, ha) if lang == "en" else (ha, en)
    return f"{first}\n\n{second}\n\n{PRIVACY_URL}"


TEXTS = {
    "consent_thanks": {
        "ha": "Na gode. Yanzu ka aiko da tambayarka, a rubuce ko da saƙon murya.",
        "en": "Thank you. Now send your question, as text or a voice note.",
    },
    "consent_thanks_ask_lang": {
        "both": "Na gode. Da wane harshe zan riƙa amsa?\nThank you. Which language should I reply in?",
    },
    "lang_set": {
        "ha": "To, zan riƙa amsa da Hausa. Don sauyawa, aika /english.",
        "en": "OK, I'll reply in English. Switch any time with /hausa.",
    },
    "voice_limit": {
        "ha": "Ka kai iyakar saƙon murya {n} na yau. Don Allah ka rubuta tambayarka, ko ka sake gwadawa gobe.",
        "en": "You've reached today's limit of {n} voice notes. Please type your question, or try again tomorrow.",
    },
    "question_limit": {
        "ha": "Ka kai iyakar tambayoyi {n} na yau. Don Allah ka sake gwadawa gobe. Mun gode!",
        "en": "You've reached today's limit of {n} questions. Please try again tomorrow. Thank you!",
    },
    "busy": {
        "ha": "Yi haƙuri, Kasafi ya kai iyakar aikinsa na yau. Don Allah ka sake gwadawa gobe.",
        "en": "Sorry, Kasafi has reached its capacity for today. Please try again tomorrow.",
    },
    "echo": {
        "ha": "Kasafi (gwaji): na karɓi saƙonka: «{text}»",
        "en": "Kasafi (test): I received your message: «{text}»",
    },
    "other": {
        "ha": "Kasafi (gwaji): don Allah ka aiko da rubutu ko saƙon murya.",
        "en": "Kasafi (test): please send text or a voice note.",
    },
    # Voice notes
    "read_back": {
        "ha": "Na ji kamar ka ce:\n«{transcript}»{extra}\n\nKana nufin haka? Ka amsa *Eh*, ko ka sake faɗa ko rubuta tambayarka.",
        "en": "I heard:\n«{transcript}»{extra}\n\nDid you mean that? Reply *Yes*, or say or type your question again.",
    },
    "heard": {
        "ha": "Na ji tambayarka:\n«{transcript}»{extra}\n\n(Kasafi yana gwaji: amsoshi za su zo nan ba da jimawa ba.)",
        "en": "I heard your question:\n«{transcript}»{extra}\n\n(Kasafi is in testing: answers are coming soon.)",
    },
    "not_heard": {
        "ha": "Yi haƙuri, ban ji saƙon muryar sosai ba. Don Allah ka sake turawa, ko ka rubuta tambayarka.",
        "en": "Sorry, I couldn't hear that voice note clearly. Please send it again, or type your question.",
    },
    "too_long": {
        "ha": "Saƙon murya ya yi tsawo. Don Allah ka tura gajere (ƙasa da minti {minutes}), ko ka rubuta tambayarka.",
        "en": "That voice note is too long. Please send a shorter one (under {minutes} minutes), or type your question.",
    },
}

NOT_IN_PILOT = (
    "Kasafi yana cikin gwaji, kuma ba a buɗe shi ga kowa ba tukuna.\n"
    "Kasafi is in a closed pilot and isn't open to everyone yet."
)


def t(key: str, lang: str | None, **kw) -> str:
    variants = TEXTS[key]
    text = variants.get("both") or variants.get(lang or "ha") or variants["ha"]
    return text.format(**kw)
