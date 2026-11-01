"""The farmer's place-history answer (docs/place-history.md §5), written in code from the numbers, like the hazard
summaries: nothing a model could invent.

1. A progress line for a first request (the satellite images take about a minute).
2. The summary, two or three sentences in the user's language: how green the plot was this season against its
   own history and the rain; whether water was seen (never "never flooded"); the trends when there are enough
   years. A place that isn't vegetation (built-up, bare, water) is said to be what the 2021 land-cover map
   labels it, with no greenness claim.
3. The plot outline (approximate, from the image; or the 1 ha circle, said so), the resolution, the years and
   the clear-image counts.
4. Context from the library: NiMet's seasonal prediction for the LGA, the NIHSA outlook, and this year's
   agriculture, irrigation and erosion lines for the LGA from the structured core.
5. The referral line (the ADP extension service). No causes, inputs, varieties or dates.
The per-year figures go once into "show working".
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from app.place import history as H
from app.place.fit import MIN_YEARS
from app.place.floods import classify_water, flood_evidence
from app.place.outline import Outline, plot_outline
from app.place.raster import circle

from app.place.water import OVERRIDES as WATER_BODIES      # data/geo/water_bodies.yaml (KASAFI_GEO_DIR on the server)


def water_body_name(lat: float, lon: float, lang: str, path: Path = WATER_BODIES) -> str:
    """The named water body the pin lies in, or '': the water-body layer (app/place/water.py: JRC bodies named
    from OSM, with data/geo/water_bodies.yaml overriding), or the yaml's own radius rule without a layer."""
    from app.place import water as W
    if path != WATER_BODIES:
        return W.override_name(lat, lon, lang, path)
    try:
        return W.name_at(lon, lat, lang)
    except Exception as e:                      # noqa: BLE001 - a name is extra
        log.warning("place: water-body name failed: %s", type(e).__name__)
        return ""

log = logging.getLogger(__name__)

# a place-history question: a place word with a history word, or the feature's own name
PLACE_WORDS = re.compile(r"(?i)\b(?:farm\w*|plots?|fields?|land|fadama|pond|dam|lake|reservoir|river\s*bank|spot|"
                         r"gona\w*|gonata|fili\w*|tafki\w*|madatsa\w*|dam[iu]n?|wuri\w*|ƙasa|kasa|kogi)\b")
HISTORY_WORDS = re.compile(r"(?i)\b(?:how green|greenness|green\b|vegetation|history|over the years|years?\b|"
                           r"since\s+20\d\d|20(?:1[5-9]|2\d)\b|satellite|flooded|under water|flood history|"
                           r"bare soil|erosion|dried?\s+up|drying|koriya\w*|ciyayi|tarihi\w*|shekar\w*|tun\s+20\d\d|"
                           r"tauraron?\s+ɗan\s+adam|tauraron?\s+dan\s+adam|ambaliya\w*|ruwa\s+ya\s+(?:rufe|kama)|"
                           r"ya\s+bushe|ƙasa\s+mara|hamada)\b")
EXPLICIT = re.compile(r"(?i)\b(?:place history|tarihin wuri|tarihin gona\w*|tarihin fili\w*)\b")
WATER_WORDS = re.compile(r"(?i)\b(?:pond|dam\b|lake|reservoir|flood\w*|under water|water\b|fadama|wet\b|"
                         r"tafki\w*|madatsa\w*|ambaliya\w*|ruwa\w*|kogi)\b")
NOT_PLACE = re.compile(r"(?i)\b(?:budget\w*|allocat\w*|kasafi\w*|naira|spen[dt]\w*|expenditure|project\w*|aikin?|"
                       r"ware|kashe|kuɗi|kudi|forecast|tomorrow|gobe|today|yau|hospital|asibiti|clinic|idps?|"
                       r"displac\w*|'yan\s+gudun\s+hijira|gudun\s+hijira)\b|₦")


def place_route(question: str, english: str = "") -> str:
    """'place' for a question about what the satellite record shows of a spot over the years; '' otherwise (a
    budget line for farms, tomorrow's rain, a facility stay on their own paths)."""
    text = f"{question} {english}"
    if NOT_PLACE.search(text):
        return ""
    if EXPLICIT.search(text):
        return "place"
    if PLACE_WORDS.search(text) and HISTORY_WORDS.search(text):
        return "place"
    return ""


def water_asked(text: str) -> bool:
    return bool(WATER_WORDS.search(text or ""))


@dataclass
class PlaceAnswer:
    text: str
    found: bool
    working: str = ""
    partial: bool = False
    specs: list[dict] = field(default_factory=list)      # the chart and the map (app/place/images.py)
    needs_pin: bool = False                               # no point known: ask for the pin
    needs_size: bool = False                              # no outline could be drawn: ask the farm's size or corners
    history: H.History | None = None
    outline: Outline | None = None
    timing: dict[str, float] = field(default_factory=dict)


MONTHS = {
    "en": ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
           "November", "December"),
    "ha": ("Janairu", "Fabrairu", "Maris", "Afrilu", "Mayu", "Yuni", "Yuli", "Agusta", "Satumba", "Oktoba",
           "Nuwamba", "Disamba"),
}

W = {
    "en": {
        "need_pin": "To look at a place's history I need the spot itself: tap the button below and send the pin of "
                    "your farm or plot (or the pond, dam or field you mean).",
        "progress": "🛰️ I'm checking about {n} years of satellite images for this spot. I'll send it in about a "
                    "minute.",
        "head": "*What the satellite record shows for this spot ({lga} LGA)*",
        "peak": "This rainy season ({year}) the plot was {green} ({n} years with enough clear images, {first}–{last}). "
                "June–October rain was {rain}, and the greenness is {verdict}.",
        "green_words": {"above": "greener than usual", "near": "about as green as in normal years",
                        "below": "less green than usual"},
        "rain_words": {"above": "more than usual", "near": "about the usual", "below": "less than usual"},
        "verdict": {"normal": "normal for the rain it got", "below": "less than the rain would suggest",
                    "none": "not compared with the rain (5 years are needed)"},
        "peak_thin": "This rainy season ({year}) had too few clear satellite images at this spot ({obs}; {need} are "
                     "needed here) to judge it; the {n} years with enough ({first}–{last}) are in the details.",
        "few_years": "Only {n} of the years since {first} have enough clear images at this spot ({need} or more in the "
                     "season), so Kasafi makes no comparison with the rain and no trend; the figures are in the "
                     "details.",
        "trend": "Since {first}, peak greenness {g}{bsi}.",
        "trend_words": {"rising": "has been rising", "falling": "has been falling",
                        "no clear change": "shows no clear change"},
        "bsi_words": {"rising": " and dry-season bare soil has been spreading", "falling":
                      " and dry-season bare soil has been shrinking", "no clear change":
                      " and dry-season bare soil shows no clear change"},
        "kind_map": "The 2021 satellite land-cover map (ESA WorldCover) labels this spot *{kind}*, so Kasafi makes "
                    "no greenness comparison for it.",
        "kind_low": "This spot's peak greenness stayed under 0.2 on the NDVI scale in most years (little "
                    "vegetation; the 2021 land-cover map labels it {lc}), so Kasafi makes no greenness comparison "
                    "for it.",
        "kinds": {"built-up area": "built-up", "bare ground": "bare ground", "open water": "open water",
                  "little vegetation": "little vegetation"},
        "on_water": "This spot is open water: the JRC record (1984–2020) saw water in {occ}% of the months it "
                    "observed, and Sentinel-2 saw water there in {when}.",
        "water_seen": "Open water was seen at this spot in {when}.",
        "water_none": "No open water was seen at this spot in the satellite images (February–October, "
                      "{first}–{last}).",
        "water_caveat": "Floods under crops, short floods and floods under cloud can be missed.",
        "nearest": "The nearest water body is {km} km from your pin ({ha} ha; water in {occ}% of the months JRC "
                   "observed, 1984–2020); Sentinel-2 saw water there in {when}.",
        "nearest_named": "The nearest water body is {name}, {km} km from your pin ({ha} ha; water in {occ}% of the "
                         "months JRC observed, 1984–2020); Sentinel-2 saw water there in {when}.",
        "nearest_none": "No water body (water in half the months JRC observed, 1984–2020) lies within 2 km of "
                        "your pin.",
        "outline_sam": "Plot outline: about {ha} ha, drawn from the satellite image (SAM 3.1, 10 m): approximate, "
                       "not a boundary.",
        "outline_circle": "No plot outline could be drawn from the satellite image, so the figures are for a "
                          "circle of about 1 ha around your pin.",
        "outline_given": "Plot shape: the circle of {ha} ha you gave, around your pin (no outline could be drawn "
                         "from the satellite image).",
        "outline_corners": "Plot shape: about {ha} ha, from your {n} corner pins: approximate, not a boundary.",
        "ask_size": "I couldn't draw this farm's outline from the satellite image. How big is the farm, in acres or "
                    "hectares (for example «3 acres» or «2 ha»)? Or send the pins of its 3 to 6 corners, then say "
                    "*done*. If you don't know, say *skip* and I'll use a circle of about 1 ha around your pin.",
        "corner_got": "📍 Corner pin {n} received. Send the others (3 to 6 in all), then say *done*.",
        "corner_few": "I have {n} corner pin(s); a plot needs at least 3. Send the others, or give the farm's size "
                      "in acres or hectares.",
        "corner_bad": "Those {n} pins don't make a sensible plot ({why}). Send the corners again in order, or give "
                      "the farm's size in acres or hectares.",
        "corner_why": {"too_small": "under 0.1 ha", "too_big": "over 50 ha", "too_thin": "a thin strip",
                       "not_a_shape": "the lines cross", "too_many": "more than 6 pins", "too_few": "fewer than 3 pins"},
        "shape_set": "Got it: a plot of about {ha} ha from your {n} corner pins. {next}",
        "size_set": "Got it: a circle of {ha} ha around your pin. {next}",
        "shape_next": "Ask me about it, for example «How green was my farm in 2024?».",
        "size_bad": "I didn't catch a size. Say it like «3 acres» or «2 ha», send the corner pins, or say *skip*.",
        "resolution": "Sentinel-2: greenness (NDVI) and water (NDWI) at 10 m, bare soil (BSI) and the cloud mask "
                      "at 20 m; water record (JRC) at 30 m; rain from Open-Meteo's ~9 km grid.",
        "years": "Years {first}–{last}; clear rainy-season images per year: {counts}.",
        "context": "*From the documents*",
        "scope_local": " — {lga} LGA",
        "scope_state": " — for Sokoto State (the document gives no line for {lga} LGA)",
        "no_context": "No seasonal prediction, flood outlook or {year} budget line for {lga} LGA is in the "
                      "library for this.",
        "budget": "{year} budget lines for {lga} LGA (agriculture, irrigation, erosion):",
        "budget_row": "• {name}: ₦{amount} ({title}, p. {page})",
        "referral": "For advice on what to plant or apply, ask the agricultural extension workers (Sokoto ADP). "
                    "Kasafi only reports what the images show.",
        "sources": "Sources: Copernicus Sentinel-2 L2A and Sentinel-1 RTC via Microsoft Planetary Computer; JRC "
                   "Global Surface Water v1.3; ESA WorldCover 2021; Open-Meteo archive (ERA5-Land); UNOSAT flood "
                   "maps via HDX (CC BY-SA).",
        "working_head": "Per year (rainy season June–October): clear images, peak greenness (NDVI 90th "
                        "percentile), June–October rain, rain-adjusted flag, months with open water, dry-season "
                        "bare soil (BSI median, February–April).",
        "working_row": "{year}: {obs} clear images, NDVI {p90}, rain {rain} mm, {flag}; water months: {months}; "
                       "BSI {bsi}",
        "flag_words": {"normal": "normal variation", "below": "below what the rain predicts", "": "no rain fit",
                       "thin": "too few clear images"},
        "none": "–",
        "fit_line": "Rain fit over {years}: greenness = {a} + {b} × rain (mm); residual SD {sd}.",
        "turbid": "Note: Sentinel-2's cloud mask also hides bright, muddy water, so water in the rainy months can "
                  "be under-counted here.",
        "nearest_working": "Nearest water body ({km} km, {ha} ha): water months per year {months}.",
        "and": " and ", "in": "in ", "mostly": "mostly ",
        "flood_radar": "Radar (Sentinel-1) saw flood water at this spot: {items}",
        "flood_radar_item": "flood water seen on {n} of {total} radar passes in {year} ({dates})",
        "flood_radar_all": "water on every July–October radar pass in {first}–{last} ({n} of {n})",
        "flood_head": "This spot is normally dry; flood water was seen in {years}: {items}.",
        "permanent": "This spot is permanent open water{name}: water in the dry season and the rainy season in most "
                     "years; JRC saw water in {occ}% of the months it observed (1984–2020){radar}{maps}.",
        "seasonal": "This spot is seasonal water: under water in most rainy seasons ({years}) and dry in the dry "
                    "season{radar}{maps}.",
        "water_radar": "; radar saw water on {n} of {total} July–October passes in {first}–{last}",
        "water_maps": "; it is inside the UN flood map's water extent of {periods}",
        "name_in": " ({name})",
        "flood_none_nomaps": "No flood water was seen at this spot in {first}–{last}: on none of the {passes} "
                             "July–October radar passes (Sentinel-1) and in no clear Sentinel-2 image; no official "
                             "satellite flood map for Sokoto is loaded yet.",
        "flood_official": "it lies inside the UN satellite flood map of {period} (UNOSAT)",
        "flood_optical": "Sentinel-2 saw water in {when}",
        "flood_none": "No flood water was seen at this spot in {first}–{last}: on none of the {passes} July–October "
                      "radar passes (Sentinel-1), in no clear Sentinel-2 image, and in no official satellite flood "
                      "map covering Sokoto ({maps}).",
        "flood_reason": "Floods under crops read bright on radar and green in optical images, short floods fall "
                        "between passes, and optical water under cloud is masked, so a flood can still be missed.",
        "maps_covered": "UNOSAT, October 2022, September and November 2024",
        "radar_working": "{year}: {total} radar passes July–October, under water on {dates}; VV dB per pass {db}",
        "radar_reference": "Radar rule: a pass counts as open water when the plot's VV is under {thr} dB and at least "
                           "{darker} dB under its dry-season reference ({ref} dB, the median of {n} February–April "
                           "passes in {seasons}); smooth dry sand is dark all year and is not counted.",
        "radar_reference_water": "Radar rule for a water body: a pass counts as water when the plot's VV is under "
                                 "{thr} dB (dry-season reference {ref} dB over {n} passes in {seasons}).",
        "official_working": "Official flood maps touching the plot: {items}",
        "short_months": ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
    },
    "ha": {
        "need_pin": "Don in duba tarihin wuri ina buƙatar wurin kansa: danna maɓallin da ke ƙasa ka aiko da wurin "
                    "gonarka ko filinka (ko tafki, madatsar ruwa ko filin da kake nufi).",
        "progress": "🛰️ Ina duba hotunan tauraron ɗan adam na kusan shekaru {n} na wannan wuri. Zan aiko nan da "
                    "kusan minti ɗaya.",
        "head": "*Abin da hotunan tauraron ɗan adam suka nuna game da wannan wuri (Ƙaramar Hukumar {lga})*",
        "peak": "A daminar {year} gonar ta kasance {green} (shekaru {n} masu isassun hotuna bayyanannu, "
                "{first}–{last}). Ruwan saman Yuni–Oktoba ya kasance {rain}, kuma koriyar {verdict}.",
        "green_words": {"above": "ta fi koriya fiye da yadda aka saba", "near": "kamar yadda take a shekarun da aka saba",
                        "below": "ba ta yi koriya kamar yadda aka saba ba"},
        "rain_words": {"above": "fiye da yadda aka saba", "near": "kamar yadda aka saba", "below": "ƙasa da yadda aka saba"},
        "verdict": {"normal": "ta dace da ruwan saman da aka samu", "below": "ta yi ƙasa da abin da ruwan saman ya nuna",
                    "none": "ba a kwatanta ta da ruwan sama ba (ana buƙatar shekaru 5)"},
        "peak_thin": "Daminar {year} ba ta da isassun hotuna bayyanannu na tauraron ɗan adam a wannan wuri ({obs}; "
                     "ana buƙatar {need} a nan) don a yanke hukunci; shekaru {n} masu isassun hotuna ({first}–{last}) "
                     "suna cikin bayanin.",
        "few_years": "Shekaru {n} ne kawai tun {first} suke da isassun hotuna bayyanannu a wannan wuri ({need} ko "
                     "fiye a damina), saboda haka Kasafi bai kwatanta da ruwan sama ba, bai kuma bayyana yanayin "
                     "canji ba; alƙaluman suna cikin bayanin.",
        "trend": "Tun {first}, koriyar ƙololuwa {g}{bsi}.",
        "trend_words": {"rising": "tana ƙaruwa", "falling": "tana raguwa", "no clear change": "ba ta nuna canji a fili"},
        "bsi_words": {"rising": ", ƙasa mara ciyayi ta rani kuma tana faɗaɗa", "falling":
                      ", ƙasa mara ciyayi ta rani kuma tana raguwa", "no clear change":
                      ", ƙasa mara ciyayi ta rani kuma ba ta nuna canji a fili"},
        "kind_map": "Taswirar yanayin ƙasa ta tauraron ɗan adam ta 2021 (ESA WorldCover) ta nuna wannan wuri a "
                    "matsayin *{kind}*, saboda haka Kasafi bai kwatanta koriyarsa ba.",
        "kind_low": "Koriyar wannan wuri a ƙololuwa ta kasance ƙasa da 0.2 a ma'aunin NDVI a mafi yawan shekaru "
                    "(ciyayi kaɗan; taswirar yanayin ƙasa ta 2021 ta nuna shi a matsayin {lc}), saboda haka Kasafi "
                    "bai kwatanta koriyarsa ba.",
        "kinds": {"built-up area": "wurin gine-gine", "bare ground": "ƙasa mara ciyayi", "open water": "ruwa a fili",
                  "little vegetation": "ciyayi kaɗan"},
        "on_water": "Wannan wuri ruwa ne a fili: bayanan JRC (1984–2020) sun ga ruwa a kashi {occ}% na watannin da "
                    "aka lura, kuma Sentinel-2 ta ga ruwa a nan a {when}.",
        "water_seen": "An ga ruwa a fili a wannan wuri a {when}.",
        "water_none": "Ba a ga ruwa a fili a wannan wuri a hotunan tauraron ɗan adam ba (Fabrairu–Oktoba, "
                      "{first}–{last}).",
        "water_caveat": "Ambaliya a ƙarƙashin shuke-shuke, gajeriyar ambaliya da ambaliya a ƙarƙashin gajimare na "
                        "iya ɓacewa.",
        "nearest": "Tafkin ruwa mafi kusa yana da nisan kilomita {km} daga wurinka (hekta {ha}; ruwa a kashi {occ}% na "
                   "watannin da JRC ta lura, 1984–2020); Sentinel-2 ta ga ruwa a can a {when}.",
        "nearest_named": "Tafkin ruwa mafi kusa shi ne {name}, kilomita {km} daga wurinka (hekta {ha}; ruwa a kashi "
                         "{occ}% na watannin da JRC ta lura, 1984–2020); Sentinel-2 ta ga ruwa a can a {when}.",
        "nearest_none": "Babu tafkin ruwa (ruwa a rabin watannin da JRC ta lura, 1984–2020) a cikin kilomita 2 daga "
                        "wurinka.",
        "outline_sam": "Iyakar gona: kusan hekta {ha}, an zana ta daga hoton tauraron ɗan adam (SAM 3.1, mita 10): "
                       "kiyasi ce, ba iyakar mallaka ba.",
        "outline_circle": "Ba a iya zana iyakar gona daga hoton tauraron ɗan adam ba, saboda haka alƙaluman na "
                          "da'ira ce ta kusan hekta 1 kewaye da wurinka.",
        "outline_given": "Siffar gona: da'irar hekta {ha} da ka bayar, kewaye da wurinka (ba a iya zana iyaka daga "
                         "hoton tauraron ɗan adam ba).",
        "outline_corners": "Siffar gona: kusan hekta {ha}, daga wuraren kusurwoyi {n} da ka aiko: kiyasi ce, ba "
                           "iyakar mallaka ba.",
        "ask_size": "Ban iya zana iyakar wannan gona daga hoton tauraron ɗan adam ba. Girman gonar nawa ne, a "
                    "kadada (acre) ko hekta (misali «kadada 3» ko «hekta 2»)? Ko ka aiko da wuraren kusurwoyinta 3 "
                    "zuwa 6, sannan ka ce *an gama*. Idan ba ka sani ba, ka ce *tsallake*, zan yi amfani da da'ira ta "
                    "kusan hekta 1 kewaye da wurinka.",
        "corner_got": "📍 An karɓi wurin kusurwa na {n}. Aiko da sauran (3 zuwa 6 gaba ɗaya), sannan ka ce *an gama*.",
        "corner_few": "Ina da wurin kusurwa {n}; gona tana buƙatar aƙalla 3. Aiko da sauran, ko ka faɗi girman gonar a "
                      "kadada ko hekta.",
        "corner_bad": "Waɗannan wurare {n} ba su yi siffar gona mai ma'ana ba ({why}). Aiko da kusurwoyin a jere, ko ka "
                      "faɗi girman gonar a kadada ko hekta.",
        "corner_why": {"too_small": "ƙasa da hekta 0.1", "too_big": "sama da hekta 50", "too_thin": "siriri ce",
                       "not_a_shape": "layukan sun ketare juna", "too_many": "fiye da wurare 6", "too_few": "ƙasa da wurare 3"},
        "shape_set": "An gama: gona ta kusan hekta {ha} daga wuraren kusurwoyi {n} da ka aiko. {next}",
        "size_set": "An gama: da'irar hekta {ha} kewaye da wurinka. {next}",
        "shape_next": "Tambaye ni game da ita, misali «Yaya koriyar gonata a 2024?».",
        "size_bad": "Ban gane girman ba. Faɗi shi kamar «kadada 3» ko «hekta 2», aiko da wuraren kusurwoyi, ko ka ce "
                    "*tsallake*.",
        "resolution": "Sentinel-2: koriya (NDVI) da ruwa (NDWI) a mita 10, ƙasa mara ciyayi (BSI) da matakin "
                      "gajimare a mita 20; bayanan ruwa (JRC) a mita 30; ruwan sama daga ragar Open-Meteo ta kusan "
                      "kilomita 9.",
        "years": "Shekaru {first}–{last}; hotuna bayyanannu na damina a kowace shekara: {counts}.",
        "context": "*Daga takardu*",
        "scope_local": " — Ƙaramar Hukumar {lga}",
        "scope_state": " — na Jihar Sokoto (takardar ba ta da layi na Ƙaramar Hukumar {lga})",
        "no_context": "Babu hasashen damina, hasashen ambaliya ko layin kasafin {year} na Ƙaramar Hukumar {lga} "
                      "a ɗakin karatu kan wannan.",
        "budget": "Layukan kasafin {year} na Ƙaramar Hukumar {lga} (noma, ban ruwa, zaizayar ƙasa):",
        "budget_row": "• {name}: ₦{amount} ({title}, shafi na {page})",
        "referral": "Don shawara kan abin da za a shuka ko abin da za a yi amfani da shi, ka tuntuɓi ma'aikatan "
                    "hidimar noma (Sokoto ADP). Kasafi yana bayyana abin da hotunan suka nuna ne kawai.",
        "sources": "Madogara: Copernicus Sentinel-2 L2A da Sentinel-1 RTC ta Microsoft Planetary Computer; JRC "
                   "Global Surface Water v1.3; ESA WorldCover 2021; Open-Meteo archive (ERA5-Land); taswirorin "
                   "ambaliya na UNOSAT ta HDX (CC BY-SA).",
        "working_head": "Kowace shekara (damina Yuni–Oktoba): hotuna bayyanannu, koriya a ƙololuwa (NDVI kashi 90), "
                        "ruwan sama na Yuni–Oktoba, alamar kwatancen ruwan sama, watannin da aka ga ruwa, ƙasa mara "
                        "ciyayi ta rani (matsakaicin BSI, Fabrairu–Afrilu).",
        "working_row": "{year}: hotuna bayyanannu {obs}, NDVI {p90}, ruwan sama mm {rain}, {flag}; watannin ruwa: "
                       "{months}; BSI {bsi}",
        "flag_words": {"normal": "bambanci na yau da kullum", "below": "ƙasa da abin da ruwan saman ya nuna",
                       "": "babu kwatancen ruwan sama", "thin": "hotuna bayyanannu kaɗan ne"},
        "none": "–",
        "fit_line": "Kwatancen ruwan sama a {years}: koriya = {a} + {b} × ruwan sama (mm); SD na saura {sd}.",
        "turbid": "Lura: matakin gajimare na Sentinel-2 yana ɓoye ruwa mai laka mai haske ma, saboda haka ana iya "
                  "ƙidaya ruwan watannin damina ƙasa da yadda yake a nan.",
        "nearest_working": "Tafkin ruwa mafi kusa (kilomita {km}, hekta {ha}): watannin ruwa a kowace shekara {months}.",
        "and": " da ", "in": "a ", "mostly": "galibi ",
        "flood_radar": "Radar (Sentinel-1) ta ga ruwan ambaliya a wannan wuri: {items}",
        "flood_radar_item": "an ga ruwan ambaliya a {n} cikin {total} na hotunan radar a {year} ({dates})",
        "flood_radar_all": "ruwa a kowane hoton radar na Yuli–Oktoba a {first}–{last} ({n} cikin {n})",
        "flood_head": "Wannan wuri a kullum bushe yake; an ga ruwan ambaliya a {years}: {items}.",
        "permanent": "Wannan wuri ruwa ne na dindindin a fili{name}: ruwa a rani da damina a mafi yawan shekaru; JRC "
                     "ta ga ruwa a kashi {occ}% na watannin da ta lura (1984–2020){radar}{maps}.",
        "seasonal": "Wannan wuri ruwan damina ne: yana ƙarƙashin ruwa a mafi yawan daminoni ({years}) kuma ya bushe "
                    "a rani{radar}{maps}.",
        "water_radar": "; radar ta ga ruwa a {n} cikin {total} na hotunan Yuli–Oktoba a {first}–{last}",
        "water_maps": "; yana cikin faɗin ruwan taswirar ambaliya ta MDD ta {periods}",
        "name_in": " ({name})",
        "flood_none_nomaps": "Ba a ga ruwan ambaliya a wannan wuri ba a {first}–{last}: ba a cikin ɗaya daga cikin "
                             "hotunan radar {passes} na Yuli–Oktoba (Sentinel-1) ba, ba kuma a cikin wani hoton "
                             "Sentinel-2 bayyananne ba; ba a riga an ɗora wata taswirar ambaliya ta tauraron ɗan adam "
                             "ta hukuma ta Sokoto ba.",
        "flood_official": "yana cikin taswirar ambaliya ta tauraron ɗan adam ta MDD (UNOSAT) ta {period}",
        "flood_optical": "Sentinel-2 ta ga ruwa a {when}",
        "flood_none": "Ba a ga ruwan ambaliya a wannan wuri ba a {first}–{last}: ba a cikin ɗaya daga cikin hotunan "
                      "radar {passes} na Yuli–Oktoba (Sentinel-1) ba, ba a cikin wani hoton Sentinel-2 bayyananne "
                      "ba, ba kuma a cikin wata taswirar ambaliya ta hukuma da ta rufe Sokoto ba ({maps}).",
        "flood_reason": "Ambaliya a ƙarƙashin shuke-shuke tana bayyana da haske a radar da kuma kore a hotunan "
                        "gani, gajeriyar ambaliya tana faɗuwa tsakanin hotuna, kuma ruwa a ƙarƙashin gajimare yana "
                        "ɓoyuwa, saboda haka ambaliya na iya ɓacewa.",
        "maps_covered": "UNOSAT, Oktoba 2022, Satumba da Nuwamba 2024",
        "radar_working": "{year}: hotunan radar {total} na Yuli–Oktoba, ƙarƙashin ruwa a {dates}; VV dB a kowane "
                         "hoto {db}",
        "radar_reference": "Ƙa'idar radar: hoto yana ƙidaya a matsayin ruwa a fili idan VV na gonar ya yi ƙasa da {thr} "
                           "dB kuma aƙalla {darker} dB ƙasa da ma'aunin raninta ({ref} dB, matsakaicin hotuna {n} na "
                           "Fabrairu–Afrilu a {seasons}); yashi bushasshe mai santsi duhu ne a kowane lokaci, ba a "
                           "ƙidaya shi.",
        "radar_reference_water": "Ƙa'idar radar ta tafkin ruwa: hoto yana ƙidaya a matsayin ruwa idan VV na gonar ya yi "
                                 "ƙasa da {thr} dB (ma'aunin rani {ref} dB a hotuna {n} na {seasons}).",
        "official_working": "Taswirorin ambaliya na hukuma da suka taɓa gonar: {items}",
        "short_months": ("Jan", "Fab", "Mar", "Afr", "May", "Yun", "Yul", "Agu", "Sat", "Okt", "Nuw", "Dis"),
    },
}

BUDGET_TERMS = ["agric", "irrigat", "erosion", "fadama", "farm", "dam ", "dams", "flood", "gully", "seed"]


def _t(lang: str) -> dict:
    return W["ha" if lang == "ha" else "en"]


def _fmt(v, nd: int = 2) -> str:
    return "–" if v is None else f"{v:.{nd}f}"


def months_text(months: list[int], lang: str) -> str:
    """'February–April and September–October' from [2, 3, 4, 9, 10]."""
    names = MONTHS["ha" if lang == "ha" else "en"]
    if not months:
        return ""
    runs: list[list[int]] = [[months[0]]]
    for m in months[1:]:
        if m == runs[-1][-1] + 1:
            runs[-1].append(m)
        else:
            runs.append([m])
    parts = [names[r[0] - 1] if len(r) == 1 else f"{names[r[0] - 1]}–{names[r[-1] - 1]}" for r in runs]
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + _t(lang)["and"] + parts[-1]


def when_text(years: dict[int, H.YearRow], lang: str) -> str:
    """'February–April and September–October in 2019–2026' when the months repeat; else per year."""
    seen = {y: r.water_months for y, r in sorted(years.items()) if r.water_months}
    if not seen:
        return ""
    ys = sorted(seen)
    counts: dict[int, int] = {}
    for y in ys:
        for m in seen[y]:
            counts[m] = counts.get(m, 0) + 1
    usual = sorted(m for m, c in counts.items() if c * 2 >= len(ys))        # months wet in at least half the years
    span = f"{ys[0]}–{ys[-1]}" if len(ys) > 2 and ys[-1] - ys[0] == len(ys) - 1 else ", ".join(str(y) for y in ys)
    if usual and len(ys) >= 3:
        every = all(set(usual) <= set(seen[y]) for y in ys)
        return f"{'' if every else _t(lang)['mostly']}{months_text(usual, lang)} {_t(lang)['in']}{span}"
    return "; ".join(f"{y} ({months_text(ms, lang)})" for y, ms in seen.items())


# --- the summary ------------------------------------------------------------------------------------------------

def summary(h: H.History, lang: str, today: date) -> str:
    t = _t(lang)
    lines: list[str] = []
    usable = h.usable_years()
    this = today.year
    if h.water_type == "permanent" or (h.water_type is None and h.on_water):
        pass                                              # the water sentence says what it is
    elif not h.vegetated:
        if h.kind == "little vegetation":
            lines.append(t["kind_low"].format(lc=h.landcover or "–"))
        else:
            lines.append(t["kind_map"].format(kind=t["kinds"][h.kind]))
    elif len(usable) < MIN_YEARS:                         # fewer than 5: no fit, no trend
        lines.append(t["few_years"].format(n=len(usable), first=min(h.years), need=h.obs_needed))
    else:
        median = sorted(h.years[y].ndvi_p90 for y in usable)[len(usable) // 2]
        rains = sorted(h.years[y].rain_season_mm for y in usable if h.years[y].rain_season_mm is not None)
        rain_median = rains[len(rains) // 2] if rains else None
        latest = max(usable)
        r = h.years[this] if this in h.years else h.years[latest]
        if this in usable and r.rain_season_mm is not None and rain_median:
            # plain words only: the figures are in the details
            green = "above" if r.ndvi_p90 > median + 0.05 else "below" if r.ndvi_p90 < median - 0.05 else "near"
            rain = ("above" if r.rain_season_mm > rain_median * 1.15 else
                    "below" if r.rain_season_mm < rain_median * 0.85 else "near")
            flag = h.fit.flags.get(this, "none") if h.fit else "none"
            lines.append(t["peak"].format(year=this, green=t["green_words"][green], n=len(usable), first=usable[0],
                                          last=usable[-1], rain=t["rain_words"][rain], verdict=t["verdict"][flag]))
        else:
            lines.append(t["peak_thin"].format(year=this, obs=h.years[this].season_obs if this in h.years else 0,
                                               need=h.obs_needed, n=len(usable), first=usable[0], last=usable[-1]))
        if "greenness" in h.trends:
            g = t["trend_words"][h.trends["greenness"][0]]
            bsi = t["bsi_words"][h.trends["bare_soil"][0]] if "bare_soil" in h.trends else ""
            lines.append(t["trend"].format(first=usable[0], g=g, bsi=bsi))
    lines.append(water_sentence(h, lang))
    return " ".join(lines)


def _short_date(iso: str, lang: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {_t(lang)['short_months'][d.month - 1]}"


def period_text(start: str, end: str, lang: str) -> str:
    """'5–9 September 2024', or '27 October – 13 November 2024' across months."""
    a, b = date.fromisoformat(start), date.fromisoformat(end)
    names = MONTHS["ha" if lang == "ha" else "en"]
    if a.month == b.month and a.year == b.year:
        return f"{a.day}–{b.day} {names[a.month - 1]} {a.year}"
    return f"{a.day} {names[a.month - 1]} – {b.day} {names[b.month - 1]} {b.year}"


def flood_sentence(h: H.History, lang: str) -> str:
    """By the cell's water type (app.place.floods.classify_water): permanent or seasonal water is said to be that,
    with its radar passes and the UN maps' water extent; only a normally dry cell with water in a wet season is
    called a flood; otherwise 'no flood water seen' with the reason, never 'never flooded'."""
    from app.place.floods import FloodEvidence, classify_water, flood_years, optical_years
    t = _t(lang)
    ev: FloodEvidence = h.floods
    kind = h.water_type or classify_water(h, ev)
    years = sorted(h.years)
    radar_all = [r for r in ev.radar.values() if r.passes]
    radar_part = ""
    if radar_all and any(r.water for r in radar_all):
        ry = sorted(ev.radar)
        radar_part = t["water_radar"].format(n=sum(r.water_passes for r in radar_all), total=sum(r.passes for r in radar_all),
                                             first=ry[0], last=ry[-1])
    maps_part = t["water_maps"].format(periods=", ".join(period_text(m["period_start"], m["period_end"], lang)
                                                          for m in ev.official)) if ev.official else ""
    if kind == "permanent":
        occ = h.jrc.get("occurrence")
        s = t["permanent"].format(name=t["name_in"].format(name=h.water_name) if h.water_name else "",
                                  occ=f"{occ:.0f}" if occ is not None else "–", radar=radar_part, maps=maps_part)
    elif kind == "seasonal":
        wet = sorted(set(optical_years(h)) | set(ev.radar_years_with_water()))
        s = t["seasonal"].format(years=", ".join(str(y) for y in wet), radar=radar_part, maps=maps_part)
    elif kind == "flood":
        parts: list[str] = []
        radar_items = radar_text(ev.radar, lang)
        if radar_items:
            parts.append(t["flood_radar"].format(items=radar_items))
        when = when_text({y: r for y, r in h.years.items() if y in optical_years(h)}, lang)
        if when:
            parts.append(t["flood_optical"].format(when=when))
        for m in ev.official:
            parts.append(t["flood_official"].format(period=period_text(m["period_start"], m["period_end"], lang)))
        s = t["flood_head"].format(years=", ".join(str(y) for y in flood_years(h, ev)), items="; ".join(parts)) + \
            " " + t["flood_reason"]
    else:
        passes = sum(r.passes for r in ev.radar.values())
        ry = sorted(ev.radar) or years
        s = t["flood_none" if ev.maps_loaded else "flood_none_nomaps"].format(
            first=ry[0], last=ry[-1], passes=passes, maps=t["maps_covered"]) + " " + t["flood_reason"]
        if ev.official:                                   # inside a UN map's water extent, yet never water here
            extent = t["water_maps"].format(periods=", ".join(period_text(m["period_start"], m["period_end"], lang)
                                                               for m in ev.official)).lstrip("; ")
            s += " " + extent[0].upper() + extent[1:] + "."
    return s + nearest_sentence(h, lang)


def radar_text(rows: dict, lang: str) -> str:
    """'every pass in 2017–2026 (96 of 96)' for a water body; else each year with water, its count and dates (four
    at most, else the first and last)."""
    t = _t(lang)
    wet = {y: r for y, r in sorted(rows.items()) if r.water}
    if not wet:
        return ""
    full = [y for y, r in wet.items() if r.water_passes == r.passes]
    if full and len(full) == len(rows) and len(full) >= 3:
        n = sum(r.passes for r in rows.values())
        return t["flood_radar_all"].format(first=full[0], last=full[-1], n=n)
    items = []
    for y, r in wet.items():
        ds = [_short_date(d, lang) for d in r.water]
        dates = ", ".join(ds) if len(ds) <= 4 else f"{ds[0]} – {ds[-1]}"
        items.append(t["flood_radar_item"].format(n=r.water_passes, total=r.passes, year=y, dates=dates))
    return "; ".join(items)


def water_sentence(h: H.History, lang: str) -> str:
    if h.floods is not None:
        return flood_sentence(h, lang)
    t = _t(lang)
    years = sorted(h.years)
    when = when_text(h.years, lang)
    if h.on_water:
        occ = h.jrc.get("occurrence")
        s = t["on_water"].format(occ=f"{occ:.0f}" if occ is not None else "–", when=when or t["none"])
    elif when:
        s = t["water_seen"].format(when=when) + " " + t["water_caveat"]
    else:
        s = t["water_none"].format(first=years[0] + (1 if h.years[years[0]].season_obs == 0 else 0), last=years[-1]) \
            + " " + t["water_caveat"]
    return s + nearest_sentence(h, lang)


def nearest_name(nw: dict, lang: str) -> str:
    return str(nw.get("name_ha" if lang == "ha" else "name") or nw.get("name") or "")


def nearest_sentence(h: H.History, lang: str) -> str:
    t = _t(lang)
    s = ""
    if h.nearest_water:
        nw = h.nearest_water
        nh = nw.get("history")
        nwhen = when_text(nh.years, lang) if nh else ""
        name = nearest_name(nw, lang)
        s += " " + t["nearest_named" if name else "nearest"].format(
            name=name, km=f"{nw['distance_m'] / 1000:.1f}", ha=nw["area_ha"], occ=nw["occurrence"], when=nwhen or t["none"])
    return s


def details(h: H.History, lang: str) -> str:
    """The per-year figures, once, for 'show working'."""
    t = _t(lang)
    out = [t["working_head"]]
    for y in sorted(h.years):
        r = h.years[y]
        if r.season_obs == 0 and r.dry_obs == 0 and not r.water_months:
            continue
        flag = ("thin" if not r.usable else (h.fit.flags.get(y, "") if h.fit else ""))
        out.append(t["working_row"].format(
            year=y, obs=r.season_obs, p90=_fmt(r.ndvi_p90, 3), rain=f"{r.rain_season_mm:.0f}" if r.rain_season_mm
            is not None else t["none"], flag=t["flag_words"][flag], months=months_text(r.water_months, lang) or
            t["none"], bsi=_fmt(r.bsi_dry, 3)))
    if h.fit:
        out.append(t["fit_line"].format(years=f"{h.fit.years[0]}–{h.fit.years[-1]}", a=_fmt(h.fit.intercept, 3),
                                        b=f"{h.fit.slope * 100:.3f}/100", sd=_fmt(h.fit.sd, 3)))
    if h.water_seen:
        out.append(t["turbid"])
    if h.floods is not None:
        from app.place.radar import DARKER_DB, WATER_DB
        ref = getattr(h.floods, "reference", None)
        if ref is not None and h.floods.radar:
            out.append(t["radar_reference_water" if h.on_water else "radar_reference"].format(
                thr=f"{WATER_DB:.0f}", darker=f"{DARKER_DB:.0f}", ref=f"{ref.vv_db:.1f}" if ref.vv_db is not None
                else t["none"], n=ref.passes, seasons=ref.seasons or t["none"]))
        for y, r in sorted(h.floods.radar.items()):
            if r.passes:
                out.append(t["radar_working"].format(
                    year=y, total=r.passes, dates=", ".join(_short_date(d, lang) for d in r.water) or t["none"],
                    db=", ".join(f"{_short_date(d, lang)} {v:.0f}" for d, v in sorted(r.vv_db.items()))))
        if h.floods.official:
            out.append(t["official_working"].format(items="; ".join(
                f"{m['source']} {m['code']} ({period_text(m['period_start'], m['period_end'], lang)}, {m.get('licence', '')})"
                for m in h.floods.official)))
    if h.nearest_water and h.nearest_water.get("history"):
        nw = h.nearest_water
        months = "; ".join(f"{y} ({months_text(r.water_months, lang)})" for y, r in sorted(nw["history"].years.items())
                           if r.water_months) or t["none"]
        out.append(t["nearest_working"].format(km=f"{nw['distance_m'] / 1000:.1f}", ha=nw["area_ha"], months=months))
    out.append(t["sources"])
    return "\n".join(out)


def outline_line(o: Outline | None, lang: str) -> str:
    """Which shape the figures are for: the satellite outline, the circle of the size given, the corner pins, or
    the 1 ha circle."""
    t = _t(lang)
    if o is None or o.method == "circle":
        return t["outline_circle"]
    if o.method == "given_circle":
        return t["outline_given"].format(ha=f"{o.area_ha:g}")
    if o.method == "corners":
        return t["outline_corners"].format(ha=f"{o.area_ha:.1f}", n=o.corners or "")
    return t["outline_sam"].format(ha=f"{o.area_ha:.1f}")


def facts_line(h: H.History, lang: str) -> str:
    t = _t(lang)
    years = [y for y in sorted(h.years) if h.years[y].season_obs or h.years[y].dry_obs]
    counts = ", ".join(f"{y} {h.years[y].season_obs}" for y in years)
    return t["resolution"] + "\n" + t["years"].format(first=years[0] if years else "–", last=years[-1] if years
                                                       else "–", counts=counts)


# --- context from the library ----------------------------------------------------------------------------------

def library_context(conn, lang: str, lga: str, lga_pcode: str, today: date) -> str:
    """NiMet's seasonal prediction for the LGA, the NIHSA outlook, and this year's agriculture, irrigation and
    erosion lines for the LGA from the structured core; quoted and cited, no verdicts."""
    from app.agent.analysis import lga_projects
    from app.hazards import read
    from app.hazards.official import outlook_answer
    t = _t(lang)
    parts: list[str] = []
    where = read.Where("lga", lga_pcode, lga) if lga_pcode else read.Where("state")
    for which, most in (("climate", 5), ("flood", 3)):
        try:
            oa = outlook_answer(conn, which, lang, where, question="rainfall season" if which == "climate" else "")
        except Exception as e:                      # noqa: BLE001 - the context is extra
            log.warning("place: outlook context failed: %s", type(e).__name__)
            oa = None
        if oa is not None and oa.found:
            parts.append(outlook_block(oa.text, lga, lang, most))
    if lga:
        try:
            res = lga_projects(conn, {"lga": lga, "terms": BUDGET_TERMS})
        except Exception as e:                      # noqa: BLE001
            log.warning("place: budget context failed: %s", type(e).__name__)
            res = None
        if res is not None and res.found and res.rows:
            rows = [t["budget_row"].format(name=r.name, amount=f"{r.amount:,.0f}", title=res.titles.get(r.doc_id, r.doc_id),
                                           page=r.page) for r in res.rows[:5]]
            parts.append(t["budget"].format(year=res.year, lga=res.subject) + "\n" + "\n".join(rows))
        else:                                       # no line names the LGA: the statewide totals that may cover it
            from app.place.planner import budget_block
            if lga_pcode and (block := budget_block(conn, lang, "lga", lga_pcode, today)):
                parts.append(block)
    if not parts:
        return t["no_context"].format(year=today.year, lga=lga or "–")
    return t["context"] + "\n" + "\n\n".join(parts)


def outlook_block(text: str, lga: str, lang: str, most: int) -> str:
    """An outlook answer's lines, kept honest about scope: the items that name the LGA (or its zone) under the
    LGA's heading; when the document only speaks of the state, the statewide items under 'for Sokoto State',
    never presented as local."""
    t = _t(lang)
    lines = [ln for ln in text.splitlines() if ln.strip()]
    head = lines[0].split(" — ")[0] if lines else ""
    source = [ln for ln in lines[1:] if ln.startswith("*")][:1]
    items = [ln for ln in lines if ln.startswith("•")]
    cite = [ln for ln in lines if ln.startswith("📄")][:1]
    key = re.sub(r"[^a-z]", "", lga.lower())[:5]
    local = [ln for ln in items if key and key in re.sub(r"[^a-z]", "", ln.lower())] if lga else []
    if local:
        return "\n".join([head + t["scope_local"].format(lga=lga)] + source + local[:most] + cite)
    return "\n".join([head + t["scope_state"].format(lga=lga or "–")] + source + items[:most] + cite)


# --- the whole answer -------------------------------------------------------------------------------------------

def first_request(conn, lat: float, lon: float, today: date) -> bool:
    if conn is None:
        return True
    cached = H._load(conn, H.cell_id(lat, lon))
    return any(not H._fresh(cached.get(("s2", y)), y, today) for y in range(H.GOOD_FROM, today.year + 1))


async def place_answer(conn, settings, question: str, english: str, lang: str, place: dict | None,
                       today: date, notify=None, ask_size: bool = False) -> PlaceAnswer:
    """`place` may carry a `shape` the user gave (app/place/shape.py: a circle of a size, or corner pins, or
    {"declined": True}); it is used instead of the satellite outline. With `ask_size`, a pin whose outline SAM 3.1
    can't draw gets the size question (needs_size) before the satellite history is read."""
    t = _t(lang)
    if not place or place.get("lat") is None or place.get("lon") is None:
        return PlaceAnswer(t["need_pin"], False, needs_pin=True)
    lat, lon = float(place["lat"]), float(place["lon"])
    lga, pcode = str(place.get("lga") or ""), str(place.get("lga_pcode") or "")
    shape = place.get("shape") or {}
    timing: dict[str, float] = {}
    t0 = time.perf_counter()
    if shape.get("geometry"):
        outline = Outline.from_shape(shape)
    else:
        outline = await plot_outline(conn, settings, lat, lon, today=today)
        if ask_size and not outline.is_plot and not shape.get("declined"):
            return PlaceAnswer(t["ask_size"], False, needs_size=True, outline=outline)
    if notify is not None and first_request(conn, lat, lon, today):
        await notify(t["progress"].format(n=today.year - H.GOOD_FROM + 1))
    timing["outline"] = time.perf_counter() - t0
    t1 = time.perf_counter()
    h = await asyncio.to_thread(H.point_history, conn, lat, lon, today=today,
                                polygon=outline.geometry if outline.is_plot else None,
                                water=water_asked(f"{question} {english}"))
    timing["history"] = time.perf_counter() - t1
    t3 = time.perf_counter()
    h.floods = await asyncio.to_thread(flood_evidence, conn, lat, lon,
                                       outline.geometry if outline.is_plot else circle(lon, lat), today=today,
                                       on_water=h.on_water)
    h.water_type = classify_water(h, h.floods)
    if h.water_type in ("permanent", "seasonal"):
        h.water_name = water_body_name(lat, lon, lang)
    timing["floods"] = time.perf_counter() - t3
    t2 = time.perf_counter()
    context = library_context(conn, lang, lga, pcode, today) if conn is not None else ""
    timing["context"] = time.perf_counter() - t2
    text = "\n\n".join(x for x in [t["head"].format(lga=lga or "–"), summary(h, lang, today),
                                   outline_line(outline, lang) + "\n" + facts_line(h, lang), context,
                                   t["referral"], t["sources"]] if x)
    given = {"shape": shape} if shape.get("geometry") else {}      # the user's shape, in memory only, for the map
    specs = [{"kind": "place_chart", "lat": lat, "lon": lon, "lga": lga, **given},
             {"kind": "place_map", "lat": lat, "lon": lon, "lga": lga, **given}]
    timing["total"] = time.perf_counter() - t0
    log.info("place answer: %s LGA, %s, %d usable years, outline %s, %.1fs", lga or "?", h.kind or "vegetated",
             len(h.usable_years()), outline.method, timing["total"])
    return PlaceAnswer(text, True, details(h, lang), specs=specs, history=h, outline=outline, timing=timing)
