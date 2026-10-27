"""Reply-language detection (Hausa or English) for a user's first text message.

It runs locally on purpose: nothing reaches a model before the user consents. Mixed messages go
to the dominant language; when it's unclear (e.g. "OK", or a voice note) the caller asks.
"""

import re

# Words that are distinctly one language. Ambiguous ones are left out ("a", "in", "to": Hausa
# "To, ..." means "Okay, ...", and "in" is Hausa for "if/that I").
HAUSA = {
    "da", "na", "ne", "ce", "ta", "ya", "ka", "ki", "ina", "nawa", "me", "mene", "menene", "shin", "kuma",
    "ba", "wa", "cikin", "gwamnati", "gwamnatin", "jihar", "jahar", "kasafi", "kasafin", "kudi", "kuɗi",
    "don", "allah", "wane", "wace", "wadanne", "waɗanne", "yaya", "akwai", "zuwa", "daga", "ga", "aka",
    "yi", "shekara", "shekarar", "so", "san", "sanin", "son", "ni", "mu", "su", "kai", "ita", "shi",
    "lafiya", "ilimi", "ruwa", "ƙananan", "kananan", "hukumar", "hukumomi", "nan", "kenan", "haka",
    "game", "rahoton", "rahoto", "tambaya", "gode", "yau", "gobe", "har", "amma", "saboda",
}
ENGLISH = {
    "the", "is", "are", "what", "how", "much", "many", "of", "for", "and", "budget", "please", "does",
    "did", "was", "were", "which", "with", "allocated", "allocation", "spent", "state", "government",
    "health", "education", "report", "year", "percentage", "compare", "compared", "this", "that",
    "there", "my", "your", "i", "you", "we", "can", "could", "would", "about", "who", "where", "when",
    "why", "thanks", "thank",
}
GREETINGS = {"sannu": "ha", "barka": "ha", "assalamu": "ha", "salamu": "ha", "hello": "en", "hi": "en", "hey": "en"}
_HAUSA_LETTERS = re.compile(r"[ɓɗƙƴƁƊƘƳ]")


def detect_language(text: str) -> str | None:
    """'ha', 'en', or None when unclear."""
    words = re.findall(r"[^\W\d_]+", text.lower())
    ha = sum(w in HAUSA for w in words) + 2 * sum(GREETINGS.get(w) == "ha" for w in words)
    en = sum(w in ENGLISH for w in words) + 2 * sum(GREETINGS.get(w) == "en" for w in words)
    ha += 2 * len(_HAUSA_LETTERS.findall(text))
    if ha + en < 2 or ha == en:
        return None
    return "ha" if ha > en else "en"
