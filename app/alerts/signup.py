"""Signing up for hazard alerts, stopping them, and MORE: pattern and button replies, no model.

- "Sanar da ni game da ambaliya a Goronyo" / "alert me about heat in Wamakko": the hazards and LGAs named; a missing
  LGA is taken from the LGA on file (shown in the confirmation), else asked for; missing hazards are asked for.
- ALERTS / FAƊAKARWA on its own: the menu (hazards by number or name, then the LGAs, in one reply).
- Nothing is stored until the user taps "Yes, sign me up" (or types Eh / Yes) on a confirmation that says what is
  kept and how to stop; the alerts' language is the user's language then (HAUSA / ENGLISH changes it).
  "Just answer now" answers the message as a question instead (Hausa "sanar da ni game da ..." can be either).
- STOP / DAINA deletes the subscription. MORE (the template's button) asks about the last alert's hazard and LGA.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.hazards.advisories import lgas_in
from app.sources.lga_names import name_of

HAZARDS = ("heat", "dust", "flood", "outbreak")
HAZARD_WORDS = {
    "heat": r"heat|hot\b|temperature|zafi|zafin rana",
    "dust": r"dust|harmattan|haze|air quality|ƙura|kura\b|hazo|hunturu",
    "flood": r"flood|rivers?\b|ambaliya|kogi",
    "outbreak": r"outbreak|disease|cholera|meningitis|measles|lassa|diphtheria|annoba|cututtuka|cuta\b|kwalara|"
                r"sankarau|kyanda|ɓarkewa|barkewa",
}
ALL = re.compile(r"(?i)\ball (?:hazards|four|of them)\b|\bduka\b|\bdukkan\b|\bduk huɗun\b")
INTENT = re.compile(r"(?i)\b(?:sanar(?: da)? ni|faɗakar(?: da)? ni|fadakar(?: da)? ni|alert me|notify me|warn me|"
                    r"send me (?:an? )?alerts?|sign me up|subscribe|(?:ina son|ina so a) (?:faɗakarwa|fadakarwa)|"
                    r"tell me (?:when|if)|let me know (?:when|if))\b")
MENU = {"alerts", "alert", "kasafi alerts", "my alerts", "faɗakarwa", "fadakarwa", "faɗakarwar kasafi",
        "fadakarwar kasafi", "/alerts", "/faɗakarwa"}
STOP = {"stop", "daina", "stop alerts", "daina faɗakarwa", "daina fadakarwa", "a daina", "unsubscribe"}
MORE = {"more", "ƙari", "kari", "more details"}
YES = {"eh", "ee", "e", "yes", "ok", "okay", "to", "toh", "na yarda", "i agree"}
NO = {"a a", "aa", "a'a", "no", "kar", "a'a kar a yi"}
BUTTONS = {"en": [("alert_yes", "Yes, sign me up"), ("alert_no", "No"), ("alert_ask", "Just answer now")],
           "ha": [("alert_yes", "Ee, yi min rajista"), ("alert_no", "A'a"), ("alert_ask", "Amsa tambayar kawai")]}

NAMES = {"en": {"heat": "heat", "dust": "harmattan dust", "flood": "floods", "outbreak": "disease outbreaks"},
         "ha": {"heat": "zafin rana", "dust": "ƙurar hunturu", "flood": "ambaliya", "outbreak": "ɓarkewar cututtuka"}}
WORDS = {
    "en": {
        "menu": "🔔 *Kasafi alerts*\n{have}Choose what and where in one reply, e.g. *1 3 Goronyo* or *floods Goronyo, "
                "Wurno*:\n1 Heat\n2 Harmattan dust\n3 Floods\n4 Disease outbreaks\n5 All four\nThen the LGA or LGAs: "
                "any of Sokoto's 23.",
        "have": "You're signed up for {hazards} in {lgas}. To add more:\n",
        "ask_lga": "Which LGA or LGAs should the {hazards} alerts cover? E.g. *Goronyo* or *Goronyo, Wurno*.",
        "confirm": "🔔 *Kasafi alerts*: {hazards} in {lgas}.\n"
                   "• At most one alert per hazard per LGA a day, and none from 22:00 to 06:00 except official "
                   "warnings.\n"
                   "• Each alert names its source. Alerts are information, not emergency response.\n"
                   "• Kasafi keeps only a code made from your number (never the number), the LGAs, the hazards, your "
                   "language and the date you signed up. Reply STOP at any time to stop and delete them.\n"
                   "• Alerts will be in English (reply HAUSA for Hausa).\n\nSign up?",
        "done": "You're signed up for Kasafi alerts about {hazards} in {lgas}. You'll get at most one alert per hazard "
                "per day, and none at night except official warnings. Each alert names its source. Reply STOP at any "
                "time to stop.",
        "declined": "OK: no alerts. You can ask Kasafi anything at any time.",
        "stopped": "Done: you won't receive Kasafi alerts any more. You can still ask Kasafi questions at any time.",
        "none": "You have no Kasafi alerts to stop. You can still ask Kasafi questions at any time.",
        "lga_one": "{lga} LGA", "lga_many": "{lgas} LGAs", "and": " and ",
        "more_q": "What is the {hazard} situation in {lga} LGA today?",
        "more_outbreak": "Is there a disease outbreak in Sokoto now?",
    },
    "ha": {
        "menu": "🔔 *Faɗakarwar Kasafi*\n{have}Zaɓi abin da kuma inda a saƙo ɗaya, misali *1 3 Goronyo* ko *ambaliya "
                "Goronyo, Wurno*:\n1 Zafin rana\n2 Ƙurar hunturu\n3 Ambaliya\n4 Ɓarkewar cututtuka\n5 Duka huɗun\n"
                "Sannan ƙaramar hukuma ɗaya ko fiye: kowace daga cikin 23 na Jihar Sokoto.",
        "have": "Kana da rajistar {hazards} a {lgas}. Don ƙara wasu:\n",
        "ask_lga": "Wace ƙaramar hukuma (ɗaya ko fiye) faɗakarwar {hazards} za ta shafa? Misali *Goronyo* ko "
                   "*Goronyo, Wurno*.",
        "confirm": "🔔 *Faɗakarwar Kasafi*: {hazards} a {lgas}.\n"
                   "• Faɗakarwa ɗaya kawai ga kowane haɗari a kowace ƙaramar hukuma a rana, kuma babu daga 22:00 zuwa "
                   "06:00 sai gargaɗin hukuma.\n"
                   "• Kowace faɗakarwa tana faɗin majiyarta. Bayani ne, ba agajin gaggawa ba.\n"
                   "• Kasafi zai ajiye lambar sirri da aka yi daga lambar wayarka kawai (ba lambar kanta ba), "
                   "ƙananan hukumomin, haɗurran, harshenka da ranar rajista. Rubuta DAINA a kowane lokaci don dainawa "
                   "da goge su.\n"
                   "• Faɗakarwar za ta zo da Hausa (rubuta ENGLISH don Turanci).\n\nA yi rajista?",
        "done": "An yi maka rajistar faɗakarwar Kasafi game da {hazards} a {lgas}. Ba za ka samu fiye da faɗakarwa "
                "ɗaya ga kowane haɗari a rana ba, kuma babu da daddare sai sanarwar hukuma. Kowace faɗakarwa tana "
                "faɗin majiyarta. Rubuta DAINA a kowane lokaci don dainawa.",
        "declined": "To: babu faɗakarwa. Kana iya tambayar Kasafi komai a kowane lokaci.",
        "stopped": "An gama: ba za ka sake karɓar faɗakarwar Kasafi ba. Har yanzu kana iya tambayar Kasafi a kowane "
                   "lokaci.",
        "none": "Ba ka da faɗakarwar Kasafi da za a daina. Kana iya tambayar Kasafi a kowane lokaci.",
        "lga_one": "Ƙaramar Hukumar {lga}", "lga_many": "Ƙananan Hukumomin {lgas}", "and": " da ",
        "more_q": "Yaya yanayin {hazard} yake a Ƙaramar Hukumar {lga} yau?",
        "more_outbreak": "Akwai ɓarkewar cuta a Sokoto yanzu?",
    },
}


def _w(lang: str) -> dict:
    return WORDS.get(lang, WORDS["ha"])


def norm(text: str) -> str:
    return " ".join(re.sub(r"[^\w\s'/ƙɗɓƴ]", " ", (text or "").lower()).split())


def hazards_in(text: str, numbers: bool = False) -> list[str]:
    """The hazards a message names (in HAZARDS order); with `numbers`, the menu's 1-5 too."""
    found = {h for h, pat in HAZARD_WORDS.items() if re.search(rf"(?i)\b(?:{pat})", text or "")}
    if ALL.search(text or ""):
        found |= set(HAZARDS)
    if numbers:
        for n in re.findall(r"(?<![\d.])([1-5])(?![\d.])", text or ""):
            found |= set(HAZARDS) if n == "5" else {HAZARDS[int(n) - 1]}
    return [h for h in HAZARDS if h in found]


def _join(items: list[str], lang: str) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + _w(lang)["and"] + items[-1]


def hazards_text(hazards: list[str], lang: str) -> str:
    return _join([NAMES.get(lang, NAMES["ha"])[h] for h in hazards], lang)


def lgas_text(lgas: list[str], lang: str) -> str:
    w, names = _w(lang), [name_of(p) or p for p in lgas]
    return w["lga_one"].format(lga=names[0]) if len(names) == 1 else w["lga_many"].format(lgas=_join(names, lang))


@dataclass
class Step:
    """What to reply: messages (text, buttons or None); or `ask`, a question to answer as usual."""
    messages: list[tuple[str, list | None]] = field(default_factory=list)
    ask: str = ""


def _confirm(store, key: str, lang: str, hazards: list[str], lgas: list[str], text: str) -> Step:
    store.set_pending_alert(key, {"stage": "confirm", "hazards": hazards, "lgas": lgas, "text": text[:1000]})
    w = _w(lang)
    return Step([(w["confirm"].format(hazards=hazards_text(hazards, lang), lgas=lgas_text(lgas, lang)),
                  BUTTONS.get(lang, BUTTONS["ha"]))])


def _gather(store, key: str, lang: str, hazards: list[str], lgas: list[str], text: str, on_file: str | None) -> Step:
    """Confirm when the hazards and LGAs are known; else ask for what is missing (the LGA on file fills a gap)."""
    if hazards and not lgas and on_file:
        lgas = [on_file]
    if hazards and lgas:
        return _confirm(store, key, lang, hazards, lgas, text)
    store.set_pending_alert(key, {"stage": "lga" if hazards else "menu", "hazards": hazards, "lgas": lgas,
                                  "text": text[:1000]})
    if hazards:
        return Step([(_w(lang)["ask_lga"].format(hazards=hazards_text(hazards, lang)), None)])
    return _menu(store, key, lang)


def _menu(store, key: str, lang: str) -> Step:
    w, sub = _w(lang), store.subscription(key)
    have = w["have"].format(hazards=hazards_text(sub["hazards"], lang), lgas=lgas_text(sub["lgas"], lang)) if sub else ""
    return Step([(w["menu"].format(have=have), None)])


def more_question(store, key: str, lang: str) -> str:
    """MORE: a question about the latest alert logged for one of the user's hazards and LGAs; '' when none."""
    sub = store.subscription(key)
    if not sub:
        return ""
    for row in store.alert_log(500):
        if row["status"] in ("sent", "dry_run") and row["hazard"] in sub["hazards"] and row["lga_pcode"] in sub["lgas"]:
            w = _w(lang)
            if row["hazard"] == "outbreak":
                return w["more_outbreak"]
            return w["more_q"].format(hazard=NAMES.get(lang, NAMES["ha"])[row["hazard"]],
                                      lga=name_of(row["lga_pcode"]) or row["lga_pcode"])
    return ""


def reply(text: str, button: str | None, key: str, lang: str, store, on_file: str | None = None) -> Step | None:
    """The alerts reply to this message, or None when it isn't about alerts (handled as usual)."""
    n, w = norm(text), _w(lang)
    pending = store.get_pending_alert(key)
    # the confirmation's buttons, or a typed Eh / A'a to it
    if pending and pending.get("stage") == "confirm" and (button in ("alert_yes", "alert_no", "alert_ask")
                                                          or (not button and (n in YES or n in NO))):
        store.set_pending_alert(key, None)
        if button == "alert_yes" or (not button and n in YES):
            sub = store.subscribe(key, pending["lgas"], pending["hazards"], lang if lang in WORDS else "ha")
            return Step([(w["done"].format(hazards=hazards_text(pending["hazards"], lang),
                                           lgas=lgas_text(pending["lgas"], lang)), None)]) if sub else None
        if button == "alert_ask":
            return Step(ask=pending.get("text", ""))
        return Step([(w["declined"], None)])
    if button in ("alert_yes", "alert_no", "alert_ask"):        # an old confirmation's button: nothing pending
        return Step([(w["declined"], None)]) if button == "alert_no" else _menu(store, key, lang)
    if n in STOP:
        store.set_pending_alert(key, None)
        return Step([(w["stopped"] if store.unsubscribe(key) else w["none"], None)])
    if n in MORE:
        q = more_question(store, key, lang)
        return Step(ask=q) if q else None
    if not text:
        return None
    if n in MENU:
        store.set_pending_alert(key, {"stage": "menu", "hazards": [], "lgas": [], "text": ""})
        return _menu(store, key, lang)
    if pending and pending.get("stage") in ("menu", "lga"):
        hazards = [h for h in HAZARDS if h in set(pending["hazards"]) | set(hazards_in(text, numbers=True))]
        lgas = sorted(set(pending["lgas"]) | set(lgas_in(text)))
        if hazards != pending["hazards"] or lgas != pending["lgas"]:
            return _gather(store, key, lang, hazards, lgas, pending.get("text") or text, on_file)
        store.set_pending_alert(key, None)       # nothing about alerts in it: the user moved on
    if INTENT.search(text):
        hazards, lgas = hazards_in(text), lgas_in(text)
        if hazards or re.search(r"(?i)\balerts?\b|faɗakarwa|fadakarwa", text):   # not "tell me if the budget ..."
            return _gather(store, key, lang, hazards, lgas, text, on_file)
    return None
