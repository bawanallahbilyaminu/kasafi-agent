"""User-facing texts in Hausa and English, and the first-contact consent notice.

Style rules (tests/test_messages.py enforces them):
- A blank line between paragraphs.
- Hausa always uses the hooked letters ɓ ɗ ƙ ƴ (saƙo, karɓi, kuɗi, ƙasa, ...).
The notice must keep matching the privacy policy (docs/site/privacy.md, published at
halalnumeriq.com.ng/kasafi/privacy).
"""

PRIVACY_URL = "https://halalnumeriq.com.ng/kasafi/privacy"

BTN_CONSENT = ("consent_ok", "OK / Na yarda")
BTN_HAUSA = ("lang_ha", "Hausa")
BTN_ENGLISH = ("lang_en", "English")
NOTICE_BUTTONS = [BTN_CONSENT, BTN_HAUSA, BTN_ENGLISH]
LANG_BUTTONS = [BTN_HAUSA, BTN_ENGLISH]

_NOTICE_HA = """*Barka da zuwa Kasafi* (gwaji).

Ina amsa tambayoyi game da takardun kasafi da manufofin gwamnati.

• Sabis ɗin AI na Meta ne ke sarrafa saƙonninka da saƙon murya. Yayin da muke amfani da kuɗin gwaji kyauta, Meta na iya amfani da su don inganta ayyukansa.

• Kada ka tura bayanan sirri.

• Ana goge saƙon murya bayan an mayar da shi rubutu.

{lang_line}

Sirri: {url}

Danna *OK / Na yarda* a saƙon da ke ƙasa idan ka yarda."""

_NOTICE_EN = """*Welcome to Kasafi* (pilot).

I answer questions about public budget and policy documents.

• Your messages and voice notes are processed by Meta AI services. While we use free credits, Meta may use them to improve its services.

• Don't share personal details.

• Voice notes are deleted after transcription.

{lang_line}

Privacy: {url}

Tap *OK / Na yarda* to agree."""

_LANG_LINE = {
    ("detected", "ha"): ("Bisa ga saƙonka na farko, zan riƙa amsa da Hausa. Don sauyawa, aika /english.",
                         "Based on your first message, I'll reply in Hausa. Switch any time with /english."),
    ("detected", "en"): ("Bisa ga saƙonka na farko, zan riƙa amsa da Turanci. Don sauyawa, aika /hausa.",
                         "Based on your first message, I'll reply in English. Switch any time with /hausa."),
    ("chosen", "ha"): ("Zan riƙa amsa da Hausa. Don sauyawa, aika /english.",
                       "I'll reply in Hausa. Switch any time with /english."),
    ("chosen", "en"): ("Zan riƙa amsa da Turanci. Don sauyawa, aika /hausa.",
                       "I'll reply in English. Switch any time with /hausa."),
}
_ASK_LANG = ("Da wane harshe zan riƙa amsa? Danna *Hausa* ko *English* a ƙasa.",
             "Which language should I reply in? Tap *Hausa* or *English* below.")


def first_contact_notice(lang: str | None, source: str | None) -> tuple[str, str]:
    """The consent notice as two messages: Hausa first, then English (which carries the buttons)."""
    ha_line, en_line = (_LANG_LINE.get((source or "detected", lang)) if lang else None) or _ASK_LANG
    return (_NOTICE_HA.format(lang_line=ha_line, url=PRIVACY_URL),
            _NOTICE_EN.format(lang_line=en_line, url=PRIVACY_URL))


TEXTS = {
    "consent_thanks": {
        "ha": "Na gode.\n\nYanzu ka aiko da tambayarka, a rubuce ko da saƙon murya.",
        "en": "Thank you.\n\nNow send your question, as text or a voice note.",
    },
    "consent_thanks_ask_lang": {
        "both": "Na gode. Da wane harshe zan riƙa amsa?\n\nThank you. Which language should I reply in?",
    },
    "lang_set": {
        "ha": "To, zan riƙa amsa da Hausa.\n\nDon sauyawa, aika /english.",
        "en": "OK, I'll reply in English.\n\nSwitch any time with /hausa.",
    },
    "voice_limit": {
        "ha": "Ka kai iyakar saƙon murya {n} na yau.\n\nDon Allah ka rubuta tambayarka, ko ka sake gwadawa gobe.",
        "en": "You've reached today's limit of {n} voice notes.\n\nPlease type your question, or try again tomorrow.",
    },
    "question_limit": {
        "ha": "Ka kai iyakar tambayoyi {n} na yau.\n\nDon Allah ka sake gwadawa gobe. Mun gode!",
        "en": "You've reached today's limit of {n} questions.\n\nPlease try again tomorrow. Thank you!",
    },
    "busy": {
        "ha": "Yi haƙuri, Kasafi ya kai iyakar aikinsa na yau.\n\nDon Allah ka sake gwadawa gobe.",
        "en": "Sorry, Kasafi has reached its capacity for today.\n\nPlease try again tomorrow.",
    },
    "echo": {
        "ha": "Kasafi (gwaji): na karɓi saƙonka:\n\n«{text}»",
        "en": "Kasafi (test): I received your message:\n\n«{text}»",
    },
    "other": {
        "ha": "Kasafi (gwaji): don Allah ka aiko da rubutu ko saƙon murya.",
        "en": "Kasafi (test): please send text or a voice note.",
    },
    # Voice notes
    "listening": {
        "ha": "🎧 Ina sauraro…",
        "en": "🎧 Listening…",
    },
    "read_back": {
        "ha": "Na ji kamar ka ce:\n\n«{transcript}»\n\nKana nufin haka? Ka amsa *Eh*, ko ka gyara, misali da shekarar da ta dace.",
        "en": "I heard:\n\n«{transcript}»\n\nDid you mean that? Reply *Yes*, or send a correction, for example the right year.",
    },
    "heard": {
        "ha": "Na ji tambayarka:\n\n«{transcript}»\n\n(Kasafi yana gwaji: amsoshi za su zo nan ba da jimawa ba.)",
        "en": "I heard your question:\n\n«{transcript}»\n\n(Kasafi is in testing: answers are coming soon.)",
    },
    "not_heard": {
        "ha": "Yi haƙuri, ban ji saƙon muryar sosai ba.\n\nDon Allah ka sake turawa, ko ka rubuta tambayarka.",
        "en": "Sorry, I couldn't hear that voice note clearly.\n\nPlease send it again, or type your question.",
    },
    "too_long": {
        "ha": "Saƙon murya ya yi tsawo.\n\nDon Allah ka tura gajere (ƙasa da minti {minutes}), ko ka rubuta tambayarka.",
        "en": "That voice note is too long.\n\nPlease send a shorter one (under {minutes} minutes), or type your question.",
    },
    # Read-back confirmation and corrections
    "confirmed": {
        "ha": "Na gode. Tambayarka:\n\n«{question}»\n\n(Kasafi yana gwaji: amsoshi za su zo nan ba da jimawa ba.)",
        "en": "Thank you. Your question:\n\n«{question}»\n\n(Kasafi is in testing: answers are coming soon.)",
    },
    "corrected": {
        "ha": "Na gyara:\n\n«{question}»\n\n(Kasafi yana gwaji: amsoshi za su zo nan ba da jimawa ba.)",
        "en": "Corrected:\n\n«{question}»\n\n(Kasafi is in testing: answers are coming soon.)",
    },
    "correction_failed": {
        "ha": "Yi haƙuri, ban iya yin wannan gyaran ba.\n\nDon Allah ka sake aiko da cikakkiyar tambayar.",
        "en": "Sorry, I couldn't apply that correction.\n\nPlease send the full question again.",
    },
    # Scope guardrails (app/guardrails/scope.py)
    "guard_electoral": {
        "ha": "Kasafi ba ya ba da ra'ayi kan 'yan takara, jam'iyyu ko zaɓe.\n\nIna amsa tambayoyi ne kawai game da takardun kasafi da manufofin gwamnati, tare da madogara.",
        "en": "Kasafi doesn't give opinions on candidates, parties or elections.\n\nI only answer questions about public budget and policy documents, with sources.",
    },
    "guard_verdict": {
        "ha": "Kasafi ba ya yanke hukunci kan ayyukan gwamnati ko na 'yan siyasa.\n\nAmma zan iya nuna maka bayanai daga takardu gefe da gefe, misali: «Nawa aka ware wa ilimi a 2025, kuma nawa aka kashe?»",
        "en": "Kasafi doesn't judge the performance of the government or politicians.\n\nBut I can show you the facts from the documents side by side, for example: «How much was allocated to education in 2025, and how much was spent?»",
    },
    "guard_security": {
        "ha": "Yi haƙuri, tambayoyi game da tsaro, rikici ko hare-hare ba sa cikin abin da Kasafi ke amsawa.\n\nIna amsa tambayoyi game da kasafi da manufofin gwamnati.",
        "en": "Sorry, questions about security, conflict or attacks are outside what Kasafi covers.\n\nI answer questions about public budgets and policies.",
    },
    "guard_medical_advice": {
        "ha": "Kasafi ba ya ba da shawarar magani ko ta abinci mai gina jiki.\n\nDon Allah ka tuntuɓi ma'aikacin lafiya. Zan iya taimaka maka da alƙaluman kasafin lafiya, misali: «Nawa aka ware wa lafiya a 2026?»",
        "en": "Kasafi doesn't give medical or nutrition advice.\n\nPlease speak to a health worker. I can help with health budget figures, for example: «How much was allocated to health in 2026?»",
    },
    "cancelled": {
        "ha": "To, an soke wannan tambayar.\n\nKa aiko da sabuwar tambaya a duk lokacin da kake so.",
        "en": "OK, that question is cancelled.\n\nSend a new question whenever you like.",
    },
}

NOT_IN_PILOT = (
    "Kasafi yana cikin gwaji, kuma ba a buɗe shi ga kowa ba tukuna.\n\n"
    "Kasafi is in a closed pilot and isn't open to everyone yet."
)


def t(key: str, lang: str | None, **kw) -> str:
    variants = TEXTS[key]
    text = variants.get("both") or variants.get(lang or "ha") or variants["ha"]
    return text.format(**kw)
