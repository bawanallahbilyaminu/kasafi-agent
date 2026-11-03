"""The menu, the buttons under answers and the closing offer (2 Nov 2026): shortcuts into the same pipeline, not a
separate bot. The understanding step stays the main way in.

- The menu is a WhatsApp interactive list (developers.facebook.com, "Interactive list messages": at most 10 rows,
  row titles 24 characters, descriptions 72, the button 20). "menu" / "zaɓi" is read by the understanding step as
  kind 'menu'. A row tap enters the pipeline as a reading (a capability hint and a restatement), traced like any
  message. Rows that need a place use the point shared in the last 30 minutes, else send the location request.
  There is no alerts row while alerts are in dry run.
- Reply buttons under an answer (at most 3, titles of 20 characters or fewer) map to the existing commands, which
  still work typed.
- The closing offer: at most one short next step tied to what was just answered, never on emergencies, refusals or
  fixed replies.
"""

from __future__ import annotations

from app.agent.understand import Understanding

ROW_TITLE, ROW_DESC, BUTTON, SECTION, REPLY_TITLE, BODY_WITH_BUTTONS = 24, 72, 20, 24, 20, 1024

# (row id, needs a place, the reading the row enters the pipeline with)
ROWS: list[tuple[str, bool, Understanding | None]] = [
    ("menu_budget", True, Understanding(kind="new", capability="place_budget", level="lga", measure="projects",
                                        restatement="What is the government budgeting for my area?")),
    ("menu_facility", True, Understanding(kind="new", capability="facility", level="pin", measure="nearest",
                                          care="general", facility_level="any", ownership="any",
                                          restatement="Where is the nearest health facility to me?")),
    ("menu_place", True, Understanding(kind="new", capability="place_history", level="pin", time="past",
                                       measure="flooded", restatement="Has my farm (the pin) ever flooded, and how "
                                                                      "green has it been over the years?")),
    ("menu_outlook", True, Understanding(kind="new", capability="hazard", level="lga", time="forecast",
                                         measure="rain and flood",
                                         restatement="What is the rainfall and flood outlook for my LGA?")),
    ("menu_docs", False, None),
    ("menu_lang", False, None),
    ("menu_privacy", False, None),
    ("menu_about", False, None),
]
NEEDS_PLACE = {rid for rid, place, _ in ROWS if place}
READINGS = {rid: r for rid, _, r in ROWS if r is not None}

WORDS = {
    "en": {
        "body": "What would you like to do? Pick one, or just type or send a voice note with your question.",
        "button": "Open menu",
        "section": "Kasafi",
        "rows": {
            "menu_budget": ("Budget for my area", "What the state budget gives your LGA, by sector"),
            "menu_facility": ("Nearest health facility", "The closest clinics and hospitals, by road time"),
            "menu_place": ("Farm or place history", "Satellite record of your spot: floods, greenness"),
            "menu_outlook": ("Rain and flood outlook", "Official seasonal rainfall and flood outlooks"),
            "menu_docs": ("Ask about a document", "Budgets, reports and surveys, with the page as proof"),
            "menu_lang": ("Change language", "Hausa or English"),
            "menu_privacy": ("My data and privacy", "What Kasafi keeps and how to delete it"),
            "menu_about": ("About Kasafi", "Who made it and how it works"),
        },
        "need_place": {
            "menu_budget": "Send your location and I'll show what the budget gives your area.",
            "menu_facility": "Send your location and I'll find the nearest health facilities by road.",
            "menu_place": "Send the location of your farm or place and I'll check its satellite record.",
            "menu_outlook": "Send your location and I'll give the rainfall and flood outlook for your area.",
        },
        "docs": "Ask me about any public document: budgets, budget performance reports, plans, surveys. For "
                "example:\n• How much is the 2026 health budget?\n• What does the MICS say about birth "
                "registration in Sokoto?\n• How much of the 2025 education budget was spent?",
        "lang": "Which language should I reply in?",
        "privacy": "What Kasafi keeps:\n• Your language choice, your consent and today's usage counts.\n• Your last "
                   "5 questions and answers, for follow-ups (90 days).\n• Never your phone number: you are known by "
                   "a coded key.\n• A location you send stays in memory for 30 minutes; only your LGA is kept.\n"
                   "• Voice notes are deleted after they are turned into text.\n\nTo delete everything, send "
                   "*DELETE MY DATA*.\n\nPrivacy policy: {url}",
        "about": "Who are you and what can you do?",
        "type_menu": "Type *menu* any time to see what I can do.",
        "anything_else": "Anything else?",
        "buttons": {"working": "Show working", "brief": "Full brief (PDF)", "lang": "Hausa",
                    "location": "Send location", "menu": "Menu"},
        "send_location": "Send your location with the button below.",
        "offers": {"place_budget": "Want the same for another year? Just name it.",
                   "budget": "Want the same for another year?",
                   "statistics": "Want the figure for another LGA or year?",
                   "place_history_pin": "Want your ward's record too?",
                   "place_history": "Want the same for another ward or LGA?",
                   "hazard": "Want the outlook for another LGA?"},
    },
    "ha": {
        "body": "Me kuke so ku yi? Ku zaɓi ɗaya, ko kawai ku rubuta tambayarku ko ku aiko da saƙon murya.",
        "button": "Buɗe zaɓuɓɓuka",
        "section": "Kasafi",
        "rows": {
            "menu_budget": ("Kasafin yankina", "Abin da kasafin jiha ya ware wa ƙaramar hukumarku"),
            "menu_facility": ("Asibiti mafi kusa", "Asibitoci da cibiyoyin lafiya mafi kusa ta hanya"),
            "menu_place": ("Tarihin gona ko wuri", "Abin da tauraron ɗan adam ya gani: ambaliya, kore"),
            "menu_outlook": ("Hasashen ruwa, ambaliya", "Hasashen damina da ambaliya na hukuma"),
            "menu_docs": ("Tambaya game da takarda", "Kasafi, rahotanni da bincike, tare da shafin shaida"),
            "menu_lang": ("Sauya harshe", "Hausa ko Turanci"),
            "menu_privacy": ("Bayanaina da sirri", "Abin da Kasafi ke ajiyewa da yadda ake goge shi"),
            "menu_about": ("Game da Kasafi", "Wanda ya yi shi da yadda yake aiki"),
        },
        "need_place": {
            "menu_budget": "Ku aiko da wurinku, in nuna muku abin da kasafin kuɗi ya ware wa yankinku.",
            "menu_facility": "Ku aiko da wurinku, in nemo cibiyoyin lafiya mafi kusa ta hanya.",
            "menu_place": "Ku aiko da wurin gonarku ko wurin, in duba tarihinsa a hotunan tauraron ɗan adam.",
            "menu_outlook": "Ku aiko da wurinku, in faɗa muku hasashen ruwan sama da ambaliya na yankinku.",
        },
        "docs": "Ku tambaye ni game da kowace takardar gwamnati ta jama'a: kasafin kuɗi, rahoton aiwatar da kasafi, "
                "tsare-tsare, bincike. Misali:\n• Nawa aka ware wa lafiya a kasafin 2026?\n• Me MICS ta ce game da "
                "rajistar haihuwa a Sokoto?\n• Nawa aka kashe daga kasafin ilimi na 2025?",
        "lang": "Da wane harshe zan riƙa amsa?",
        "privacy": "Abin da Kasafi ke ajiyewa:\n• Harshen da kuka zaɓa, amincewarku da ƙididdigar amfanin yau.\n"
                   "• Tambayoyinku 5 na ƙarshe da amsoshinsu, don tambayoyin biyo baya (kwana 90).\n• Ba a taɓa "
                   "ajiye lambar wayarku ba: ana gane ku da wata lamba ta sirri.\n• Wurin da kuka aiko yana zama a "
                   "ƙwaƙwalwa na minti 30; ƙaramar hukumarku kaɗai ake ajiyewa.\n• Ana goge saƙon murya bayan an "
                   "mayar da shi rubutu.\n\nDon goge komai, ku aika *GOGE BAYANAI NA*.\n\nManufar sirri: {url}",
        "about": "Kai wanene, me za ka iya yi?",
        "type_menu": "Ku rubuta *menu* a kowane lokaci don ganin abin da zan iya yi.",
        "anything_else": "Akwai wani abu kuma?",
        "buttons": {"working": "Nuna lissafi", "brief": "Cikakken rahoto PDF", "lang": "English",
                    "location": "Aiko da wuri", "menu": "Zaɓuɓɓuka"},
        "send_location": "Ku aiko da wurinku da maɓallin da ke ƙasa.",
        "offers": {"place_budget": "Kuna so na wata shekara? Ku faɗi shekarar kawai.",
                   "budget": "Kuna so na wata shekara?",
                   "statistics": "Kuna so na wata ƙaramar hukuma ko shekara?",
                   "place_history_pin": "Kuna so na gundumarku ma?",
                   "place_history": "Kuna so na wata gunduma ko ƙaramar hukuma?",
                   "hazard": "Kuna so na wata ƙaramar hukuma?"},
    },
}

# reply-button ids under answers -> what they do (the same commands typed words run)
BTN_WORKING, BTN_BRIEF, BTN_LANG, BTN_LOCATION, BTN_MENU = "btn_working", "btn_brief", "btn_lang", "btn_location", \
    "btn_menu"


def words(lang: str) -> dict:
    return WORDS.get(lang, WORDS["ha"])


def menu_payload(lang: str) -> dict:
    """The list message: its body, button and one section of rows (no alerts row while alerts are in dry run)."""
    w = words(lang)
    rows = [{"id": rid, "title": w["rows"][rid][0], "description": w["rows"][rid][1]} for rid, _, _ in ROWS]
    return {"body": w["body"], "button": w["button"], "sections": [{"title": w["section"], "rows": rows}]}


def row_of(msg: dict) -> str | None:
    """The menu row a list reply chose ('menu_budget'), or None."""
    inter = msg.get("interactive") or {}
    if inter.get("type") != "list_reply":
        return None
    rid = (inter.get("list_reply") or {}).get("id") or ""
    return rid if rid in {r for r, _, _ in ROWS} else None


def reading_for(row: str) -> Understanding | None:
    """A fresh copy of the row's reading (it is annotated as it goes through the pipeline)."""
    r = READINGS.get(row)
    return Understanding(**{k: v for k, v in r.to_dict().items()}) if r is not None else None


def answer_buttons(lang: str, *, working: bool, brief: bool, other_lang: bool, needs_location: bool
                   ) -> list[tuple[str, str]]:
    """At most 3 reply buttons that apply to this answer; 'Menu' only when nothing else does."""
    b = words(lang)["buttons"]
    out = ([(BTN_WORKING, b["working"])] if working else []) + ([(BTN_BRIEF, b["brief"])] if brief else []) + \
        ([(BTN_LANG, b["lang"])] if other_lang else []) + ([(BTN_LOCATION, b["location"])] if needs_location else [])
    return out[:3] or [(BTN_MENU, b["menu"])]


def closing_offer(lang: str, u: Understanding | None, text: str) -> str:
    """One short offer of the natural next step for this answer, or '' (no reading, or the answer already ends
    with a question)."""
    if u is None or text.rstrip().endswith("?"):
        return ""
    o = words(lang)["offers"]
    if u.capability == "place_history":
        return o["place_history_pin"] if u.level == "pin" else o["place_history"]
    return o.get(u.capability, "")
