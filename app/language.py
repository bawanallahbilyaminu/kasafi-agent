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


# --- Hausa letters: models sometimes write a look-alike from another script ('Ɗaҳan' for 'Ƴaƴan') ----------------

# Cyrillic and Greek letters that look like Latin ones (any language): the Latin letter. Cyrillic ҳ (h with a
# descender) and ӄ / ҡ (k with a hook) stand in for Hausa ƴ and ƙ.
_LOOKALIKE = str.maketrans({
    "ҳ": "ƴ", "Ҳ": "Ƴ", "ӄ": "ƙ", "Ӄ": "Ƙ", "ҡ": "ƙ", "Ҡ": "Ƙ", "ԁ": "d",
    "а": "a", "А": "A", "в": "b", "В": "B", "е": "e", "Е": "E", "к": "k", "К": "K", "м": "m", "М": "M", "н": "h",
    "Н": "H", "о": "o", "О": "O", "р": "p", "Р": "P", "с": "c", "С": "C", "т": "t", "Т": "T", "у": "y", "У": "Y",
    "х": "x", "Х": "X", "і": "i", "І": "I", "ј": "j", "Ј": "J", "ѕ": "s", "Ѕ": "S", "ԛ": "q", "ԝ": "w",
    "α": "a", "Α": "A", "Β": "B", "ε": "e", "Ε": "E", "Ζ": "Z", "Η": "H", "ι": "i", "Ι": "I", "κ": "k", "Κ": "K",
    "Μ": "M", "Ν": "N", "ο": "o", "Ο": "O", "ρ": "p", "Ρ": "P", "Τ": "T", "υ": "u", "Υ": "Y", "χ": "x", "Χ": "X",
})
# Latin letters that models write for Hausa's hooked ones (Hausa only: đ and ķ are real letters elsewhere)
_HAUSA_HOOKS = str.maketrans({"ķ": "ƙ", "Ķ": "Ƙ", "ƃ": "ɓ", "Ƃ": "Ɓ", "đ": "ɗ", "Đ": "Ɗ", "ď": "ɗ", "Ď": "Ɗ",
                              "ÿ": "ƴ", "Ÿ": "Ƴ"})


def normalize_letters(text: str, lang: str | None = None) -> str:
    """Look-alike letters from other scripts back to Latin, and (for Hausa) the hooked letters ɓ ɗ ƙ ƴ written
    with the wrong mark. Latin letters, including the user's own spelling of names, are left as they are."""
    if not text:
        return text
    out = text.translate(_LOOKALIKE)
    return out.translate(_HAUSA_HOOKS) if lang == "ha" else out


def foreign_letters(text: str) -> list[str]:
    """Letters that are not Latin script (the test: Hausa replies contain none)."""
    import unicodedata
    return [ch for ch in text if ch.isalpha() and not unicodedata.name(ch, "").startswith("LATIN")]
