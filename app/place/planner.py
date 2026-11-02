"""The planner's place-history answer for a ward, an LGA or the state (docs/place-history.md §5, step 3), from
the precomputed ward_history table (app/place/area.py), written in code:

1. Summary: a first sentence in plain words (most units about as usual, the one that stood out and its rain),
   then which wards (or LGAs, for the state) stand out on the measure asked, with the period and the
   resolution; for greenness, which stood out against their own years and that season's rain; low-data units
   marked, never filled.
2. A ward choropleth map (app/place/images.py: area_map).
3. The ranking: top and bottom five with figures; every unit in "show working".
4. The budget link: this year's agriculture, irrigation, erosion and environment lines for the LGA from the
   structured core (neutral, no verdicts); when no line names the LGA, the statewide totals that may cover it.
Flood answers lead with the UN satellite flood map (official, 375 m, dated) and give radar as a lower bound.
Planner answers show the values (a farmer's answer does not).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import date

from app.place import fit as fitting
from app.place.area import STATE

log = logging.getLogger(__name__)

MEASURES = {
    "greenness": {"measure": "modis_peak", "first": 2001, "pct": False, "fmt": "{:.2f}",
                  "en": "peak rainy-season greenness of cropland (MODIS NDVI, 250 m, 90th percentile of June–October "
                        "composites)", "ha": "koriyar damina a ƙololuwa ta gonaki (MODIS NDVI, mita 250, kashi na 90 na "
                                            "hotunan Yuni–Oktoba)",
                  "high_en": "greenest", "low_en": "least green", "high_ha": "mafi koriya", "low_ha": "mafi ƙarancin koriya"},
    "flood": {"measure": "s1_flood_share", "first": 2017, "pct": True, "fmt": "{:.1%}",
              "en": "open floodwater seen by radar on normally dry cropland, a lower bound (Sentinel-1, 200 m, "
                    "August–October passes: misses water under crops and floods between passes)",
              "ha": "ruwan ambaliya a fili da radar ta gani a gonakin da a kullum suka bushe, ƙaramin kiyasi (Sentinel-1, "
                    "mita 200, hotunan Agusta–Oktoba: yana rasa ruwa a ƙarƙashin shuke-shuke da ambaliya tsakanin hotuna)",
              "high_en": "most open floodwater", "low_en": "least", "high_ha": "mafi yawan ruwan ambaliya a fili", "low_ha": "mafi ƙaranci"},
    "flood_map": {"measure": "unosat_share", "first": 2022, "pct": True, "fmt": "{:.0%}",
                  "en": "share of cropland inside the UN satellite flood map (UNOSAT, VIIRS 375 m)",
                  "ha": "kashin gonakin da ke cikin taswirar ambaliya ta tauraron ɗan adam ta MDD (UNOSAT, mita 375)",
                  "high_en": "most inside the flood map", "low_en": "least inside", "high_ha": "mafi yawa a cikin taswirar",
                  "low_ha": "mafi ƙaranci"},
    "water": {"measure": "jrc_recurrence_share", "first": 0, "pct": True, "fmt": "{:.0%}",
              "en": "share of cropland with water in half the years 1984–2020 (JRC, 30 m)",
              "ha": "kashin gonakin da ruwa ya kasance a rabin shekarun 1984–2020 (JRC, mita 30)",
              "high_en": "most often under water", "low_en": "least", "high_ha": "mafi yawan ruwa", "low_ha": "mafi ƙaranci"},
    "bare": {"measure": "bsi_share", "first": 2017, "pct": True, "fmt": "{:.0%}",
             "en": "share of cropland reading as bare soil in the dry season (Sentinel-2 BSI, 200 m)",
             "ha": "kashin gonakin da suka nuna ƙasa mara ciyayi a rani (Sentinel-2 BSI, mita 200)",
             "high_en": "most bare", "low_en": "least bare", "high_ha": "mafi ƙasa mara ciyayi", "low_ha": "mafi ƙaranci"},
    "rain": {"measure": "rain_season_mm", "first": 2001, "pct": False, "fmt": "{:.0f} mm",
             "en": "June–October rain at the ward's centre (Open-Meteo archive, ~9 km grid)",
             "ha": "ruwan sama na Yuni–Oktoba a tsakiyar gunduma (Open-Meteo, raga ~kilomita 9)",
             "high_en": "wettest", "low_en": "driest", "high_ha": "mafi ruwa", "low_ha": "mafi bushewa"},
}
MEASURE_WORDS = [
    ("flood_map", re.compile(r"(?i)\b(?:un\s+(?:satellite\s+)?flood\s+map|unosat|flood\s+map|taswirar\s+ambaliya)\b")),
    ("water", re.compile(r"(?i)\b(?:jrc|(?:often|usually|regularly)\s+under\s+water|surface\s+water|standing\s+water|"
                         r"ponds?|wetland|fadama|ruwa(?:n)?\s+(?:fili|tafki)|ruwa\s+ke\s+yawan|yawan\s+ruwa|tafk\w*)\b")),
    ("flood", re.compile(r"(?i)\b(?:flood\w*|under\s+water|inundat\w*|ambaliya\w*|ruwa\s+ya\s+rufe)\b")),
    ("bare", re.compile(r"(?i)\b(?:bare\s+soil|bare\b|erosion|sand|degrad\w*|ƙasa\s+mara\s+ciyayi|kasa\s+mara\s+ciyayi|hamada|zaizay\w*)\b")),
    ("greenness", re.compile(r"(?i)\b(?:green\w*|vegetat\w*|crop\s+(?:cover|growth)|crops?|farm(?:ing|land)?|ndvi|koriya\w*|ciyayi|"
                             r"shuke-?shuke|noma|amfanin\s+gona)\b")),
    ("rain", re.compile(r"(?i)\b(?:rain(?:fall)?|ruwan\s+sama|damina)\b")),
]
AREA_WORDS = re.compile(r"(?i)\b(?:wards?|lgas?|local\s+government\w*|across|which\s+(?:wards?|lgas?|areas?|parts?)|"
                        r"state-?wide|the\s+state|sokoto\s+state|all\s+(?:wards|lgas)|gundum\w*|ƙaramar\s+hukuma\w*|"
                        r"karamar\s+hukuma\w*|ƙananan\s+hukumomi|kananan\s+hukumomi|jihar?\s+sokoto|fa[ɗd]in\s+jiha\w*|"
                        r"wa[ɗd]anne\b)\b")
MY_FARM = re.compile(r"(?i)\b(?:my\s+(?:farm|plot|land|field)|gonata|gona\s+ta|filina|wannan\s+wuri|this\s+spot)\b")
MY_WARD = re.compile(r"(?i)\b(?:my\s+(?:ward|area|village|community|neighbou?rhood)|(?:around\s+)?here|unguwata|unguwa\s+ta|"
                     r"gundumata|gunduma\s+ta|yankina|yanki\s+na|ƙauyena|kauyena|garina|(?:a\s+)?nan\b)\b")
MY_LGA = re.compile(r"(?i)\b(?:my\s+(?:lga|local\s+government(?:\s+area)?)|ƙaramar\s+hukumata|karamar\s+hukumata|"
                    r"ƙaramar\s+hukuma\s+ta|karamar\s+hukuma\s+ta)\b")
STATE_WORDS = re.compile(r"(?i)\b(?:the\s+state|state-?wide|sokoto\s+state|all\s+(?:wards|lgas)|which\s+lgas|jihar?\s+sokoto|"
                         r"fa[ɗd]in\s+jiha\w*|dukkan\s+(?:gundumomi|ƙananan|kananan))\b")
TREND = re.compile(r"(?i)\b(?:over\s+the\s+years|over\s+time|evolv\w*|chang\w*|trend\w*|since\s+(?:19|20)\d\d|"
                   r"(?:the\s+)?last\s+\d+\s+years|history|tun\s+(?:shekaru|shekarar|20\d\d)|ya\s+canza|ta\s+canza|"
                   r"sun\s+canza|canji|tarihi\w*|cikin\s+shekaru)\b")
MINE = MY_FARM                                                 # kept for callers
TOP_N = 5
NEAR = {"greenness": 0.05, "bare": 0.05, "rain": 0.15}        # within this of the unit's own usual: "about as usual"
LITTLE_SHARE = 0.01                                           # a flood share under this is "little"


@dataclass
class AreaAnswer:
    text: str
    found: bool
    working: str = ""
    partial: bool = False
    specs: list[dict] = field(default_factory=list)
    level: str = ""              # the units compared: ward | lga
    unit: str = ""               # the LGA pcode, or NG034 for the state
    measure: str = ""
    year: int = 0
    needs_pin: bool = False      # 'my ward' with no location on file: the pin first, then the answer


W = {
    "en": {
        "head": "*{label}: {area}, {year}* — experimental",
        "head_noyear": "*{label}: {area}* — experimental",
        "area_lga": "wards of {lga} LGA", "area_state": "the 23 LGAs of Sokoto State", "area_state_wards": "the 244 wards of Sokoto State",
        "of_lga": "{lga} LGA's", "of_state": "Sokoto State's",
        "summary": "Across {area}, the {year} {short} ranged from {lo} ({lo_unit}) to {hi} ({hi_unit}); the median was "
                   "{med}. {high_word}: {top}. {low_word}: {bottom}.",
        "summary_noyear": "Across {area}, the {short} ranges from {lo} ({lo_unit}) to {hi} ({hi_unit}); the median is "
                          "{med}. {high_word}: {top}. {low_word}: {bottom}.",
        "short": {"greenness": "peak greenness", "flood": "open-floodwater share of normally dry cropland (radar)",
                  "flood_map": "share of cropland inside the UN flood map", "water": "share of cropland often under water",
                  "bare": "bare-soil share of cropland", "rain": "June–October rain"},
        # the plain first sentence
        "plain_green": "Most of {of} farmland was {how} in {year}; {low} was the least green {unit}{rain}.",
        "plain_green_how": {"near": "about as green as usual", "above": "greener than usual", "below": "less green than usual"},
        "plain_green_rain_how": {"near": "about as green as the rain would suggest", "above": "greener than the rain would suggest",
                                 "below": "less green than the rain would suggest"},
        "head_plain": "*{short}: {area}{year}* — experimental",
        "head_ward": "*{short}: {ward} ward{likely}, {lga} LGA* — experimental",
        "likely": " (likely)",
        "ward_scope": "Your pin is in {ward} ward{likely} of {lga} LGA, so this answer is about that ward, compared with the "
                      "whole of {lga} LGA and the state.",
        "ward_scope_no_ward": "Your location gives {lga} LGA but not a ward, so this answer is about the LGA's wards.",
        "trend_head": "Since {first}, {ward}'s {what} {dir}; {lga} LGA's {lga_dir}, and the state's {state_dir} "
                      "({first}–{last}, {n} years with normal data).",
        "trend_dir": {"rising": "has been rising", "falling": "has been falling", "no clear change": "shows no clear change",
                      "": "has too few years to call"},
        "trend_unit": "Since {first}, {of} farmland greenness {dir} ({n} years with normal data).",
        "ward_year": "In {year} {ward} was {how}: {value} against its usual {usual}. {lga} LGA's wards ranged {lo}–{hi}, "
                     "with {ward} {rank} of {m}; the state's cropland median was {state}.",
        "ward_green_how": {"near": "about as green as usual", "above": "greener than usual", "below": "less green than usual"},
        "ward_green_rain_how": {"near": "about as green as the rain would suggest", "above": "greener than the rain would suggest",
                                "below": "less green than the rain would suggest"},
        "ward_year_norain": "In {year} {ward} was {how}: {value} against its usual {usual}.",
        "skipped_years": "{why}, so {year} is the latest year with normal data.",
        "thin_years": "{years} {verb} too few clear images so far",
        "unfinished_years": "{years}'s season {verb} not complete in the satellite catalogue yet (composites to {last})",
        "unfinished_verb": {"one": "is", "many": "are"},
        "skipped_verb": {"one": "has", "many": "have"},
        "missing_units": "{no_crop} {what} have no cropland in the 2021 land-cover map; {no_data} {what_data} have no data that year.",
        "missing_crop_only": "{no_crop} {what} have no cropland in the 2021 land-cover map, so they carry no value.",
        "missing_data_only": "{no_data} {what} have no data for that year.",
        "working_series": "Series ({measure}, {res}): {rows}",
        "plain_rain_clause": {"below": ", but its rain was also low", "above": ", although its rain was above usual",
                              "near": ", although its rain was about usual", "": ""},
        "plain_bare": "Most of {of} farmland showed {how} bare soil in the dry season of {year}; {top} was the most bare {unit}.",
        "plain_bare_how": {"near": "about as much", "above": "more", "below": "less"},
        "plain_rain": "Rain in {year} was {how} across most of {of} {units}; {top} was the wettest {unit} and {low} the driest.",
        "plain_rain_how": {"near": "about usual", "above": "above usual", "below": "below usual"},
        "plain_rain_same": "Rain in {year} was {how} for {of} {units}: {val} for all of them, because the ~9 km rain "
                           "grid gives every ward of an LGA the figure at the LGA's centre.",
        "plain_flood_little": "Radar saw little open floodwater on {of} normally dry farmland in {year}: under 1% of "
                              "cropland in most {units}; {top} had the most ({val}).",
        "plain_flood_some": "Radar saw open floodwater on {of} normally dry farmland in {year}: {top} had the most "
                            "({val}); {low} the least ({lo_val}).",
        "plain_map": "The UN satellite flood map of {period} covered {state_val} of {of} cropland; {top} had the most "
                     "farmland inside it ({val}) and {low} the least ({lo_val}).",
        "plain_water": "{few} of {of} {units} have farmland that is often under water; {top} has the most ({val}).",
        "plain_water_few": {"few": "Few", "some": "Some", "many": "Many"},
        "rain_adj": "Against each {unit}'s own years and that season's rain: {parts}.",
        "rain_below": "{units} were less green than the rain would suggest",
        "rain_above": "{units} were greener than usual for the rain",
        "rain_adj_none": "no {unit} stood out against its own years and the rain",
        "rain_adj_units": "{n} {what} had too few years for a rain comparison",
        "low_data": "Low data: {units} ({n} or fewer observations that year) are marked ~ and not ranked.",
        "resolution": "Period {period}; resolution {res}. Cropland only (ESA WorldCover 2021).",
        "ranking_head": "*Ranking ({n} {what})*",
        "top_head": "Highest:", "bottom_head": "Lowest:",
        "row": "{i}. {name}: {value} ({n} obs)",
        "working_head": "All {what}, {measure}, {year}: value (observations behind it; ~ low data; rain flag where fitted).",
        "working_measure": "Measure: {label}. Period {period}; resolution {res}. Cropland only (ESA WorldCover 2021).",
        "working_row": "{name} [{code}]: {value} ({n}){flag}",
        "flag_below": " below-rain", "flag_above": " above-rain",
        # floods: the official map first, radar as a lower bound
        "map_label": "UN satellite flood map of {period} (UNOSAT, VIIRS 375 m)",
        "radar_head": "*Open floodwater seen by radar, a lower bound* (Sentinel-1, 200 m; misses water under crops and "
                      "floods between passes)",
        "radar_summary": "Across {area}, the {year} share ranged from {lo} ({lo_unit}) to {hi} ({hi_unit}); median {med}. "
                         "Most: {top}. Least: {bottom}.",
        "differ": "The two differ because the UN map (VIIRS, a 5-day composite at 375 m) counts flooded and wet ground "
                  "including under crops, while radar counts only smooth open water on the dates of its passes, so the "
                  "radar share is always the lower one.",
        "no_map_year": "No UN satellite flood map covers Sokoto for {year} (maps loaded: October 2022, September and "
                       "November 2024), so only the radar lower bound is shown.",
        # the budget link
        "budget_head": "*{year} budget lines for {lga} LGA (agriculture, irrigation, erosion, environment)*",
        "budget_row": "• {name}: ₦{amount} ({title}, p. {page})",
        "budget_none": "No {year} budget line names {lga}; statewide lines that may cover it:",
        "budget_group": "• {group}: ₦{amount} across {n} statewide lines",
        "budget_groups": {"agriculture": "Agriculture", "irrigation": "Irrigation and dams", "erosion": "Erosion and drainage",
                          "environment": "Environment and forestry"},
        "budget_source": "({title}; statewide lines are not split by LGA)",
        "budget_nothing": "No {year} budget line names {lga}, and no statewide agriculture, irrigation, erosion or "
                          "environment line was found.",
        "budget_state": "Budget lines are linked per LGA: ask about one LGA to see its lines.",
        "none": "No precomputed satellite measures are loaded for {area} yet.",
        "no_year": "No {short} is available for {year}; the years loaded run {first}–{last}.",
        "sources": "Sources: {source}; boundaries GRID3 wards and OCHA COD-AB LGAs.",
        "neutral": "Kasafi reports what the satellite record shows; it makes no judgement of causes or of anyone's work.",
        "and": " and ", "ward": "ward", "wards": "wards", "lga": "LGA", "lgas": "LGAs",
        "unit_of": {"ward": "ward", "lga": "LGA"},
    },
    "ha": {
        "head": "*{label}: {area}, {year}* — na gwaji",
        "head_noyear": "*{label}: {area}* — na gwaji",
        "area_lga": "gundumomin Ƙaramar Hukumar {lga}", "area_state": "ƙananan hukumomi 23 na Jihar Sokoto",
        "area_state_wards": "gundumomi 244 na Jihar Sokoto",
        "of_lga": "Ƙaramar Hukumar {lga}", "of_state": "Jihar Sokoto",
        "summary": "A {area}, {short} na {year} ya tashi daga {lo} ({lo_unit}) zuwa {hi} ({hi_unit}); matsakaici {med}. "
                   "{high_word}: {top}. {low_word}: {bottom}.",
        "summary_noyear": "A {area}, {short} ya tashi daga {lo} ({lo_unit}) zuwa {hi} ({hi_unit}); matsakaici {med}. "
                          "{high_word}: {top}. {low_word}: {bottom}.",
        "short": {"greenness": "koriyar ƙololuwa", "flood": "kashin gonakin da radar ta ga ruwan ambaliya a fili",
                  "flood_map": "kashin gonaki a cikin taswirar ambaliya ta MDD", "water": "kashin gonakin da ruwa ke yawan rufewa",
                  "bare": "kashin ƙasa mara ciyayi a gonaki", "rain": "ruwan sama na Yuni–Oktoba"},
        "plain_green": "Mafi yawan gonakin {of} sun kasance {how} a {year}; {low} ce {unit} mafi ƙarancin koriya{rain}.",
        "plain_green_how": {"near": "kamar yadda aka saba a koriya", "above": "sun fi koriya fiye da yadda aka saba",
                            "below": "ba su yi koriya kamar yadda aka saba ba"},
        "plain_green_rain_how": {"near": "kamar yadda ruwan sama ya nuna a koriya", "above": "sun fi koriya fiye da yadda ruwan sama ya nuna",
                                 "below": "ba su yi koriya kamar yadda ruwan sama ya nuna ba"},
        "head_plain": "*{short}: {area}{year}* — na gwaji",
        "head_ward": "*{short}: gundumar {ward}{likely}, Ƙaramar Hukumar {lga}* — na gwaji",
        "likely": " (wataƙila)",
        "ward_scope": "Wurinka yana gundumar {ward}{likely} ta Ƙaramar Hukumar {lga}, saboda haka wannan amsa ta wannan gunduma ce, "
                      "an kwatanta ta da dukkan Ƙaramar Hukumar {lga} da jihar.",
        "ward_scope_no_ward": "Wurinka ya nuna Ƙaramar Hukumar {lga} amma ba gunduma ba, saboda haka wannan amsa ta gundumomin ƙaramar hukumar ce.",
        "trend_head": "Tun {first}, {what} a {ward} {dir}; ta Ƙaramar Hukumar {lga} {lga_dir}, ta jiha kuma {state_dir} "
                      "({first}–{last}, shekaru {n} masu bayanai na yau da kullum).",
        "trend_dir": {"rising": "tana ƙaruwa", "falling": "tana raguwa", "no clear change": "ba ta nuna canji a fili",
                      "": "ba ta da isassun shekaru"},
        "trend_unit": "Tun {first}, koriyar gonakin {of} {dir} (shekaru {n} masu bayanai na yau da kullum).",
        "ward_year": "A {year} {ward} ta kasance {how}: {value} idan aka kwatanta da yadda ta saba {usual}. Gundumomin Ƙaramar "
                     "Hukumar {lga} sun tashi daga {lo} zuwa {hi}, {ward} ta {rank} cikin {m}; matsakaicin jiha kuma {state}.",
        "ward_green_how": {"near": "kamar yadda ta saba a koriya", "above": "ta fi koriya fiye da yadda ta saba",
                           "below": "ba ta yi koriya kamar yadda ta saba ba"},
        "ward_green_rain_how": {"near": "kamar yadda ruwan sama ya nuna a koriya", "above": "ta fi koriya fiye da yadda ruwan sama ya nuna",
                                "below": "ba ta yi koriya kamar yadda ruwan sama ya nuna ba"},
        "ward_year_norain": "A {year} {ward} ta kasance {how}: {value} idan aka kwatanta da yadda ta saba {usual}.",
        "skipped_years": "{why}, saboda haka {year} ce shekara ta ƙarshe mai bayanai na yau da kullum.",
        "thin_years": "{years} {verb} da hotuna bayyanannu kaɗan ne har yanzu",
        "unfinished_years": "daminar {years} {verb} cika a tarihin tauraron ɗan adam ba tukuna (hotuna har zuwa {last})",
        "unfinished_verb": {"one": "ba ta", "many": "ba su"},
        "skipped_verb": {"one": "tana", "many": "suna"},
        "missing_units": "{what} {no_crop} ba su da gona a taswirar yanayin ƙasa ta 2021; {what_data} {no_data} ba su da bayanai a shekarar.",
        "missing_crop_only": "{what} {no_crop} ba su da gona a taswirar yanayin ƙasa ta 2021, saboda haka ba su da ƙima.",
        "missing_data_only": "{what} {no_data} ba su da bayanai na shekarar.",
        "working_series": "Jerin ({measure}, {res}): {rows}",
        "plain_rain_clause": {"below": ", amma ruwan samanta ma ya yi ƙaranci", "above": ", duk da cewa ruwan samanta ya wuce yadda aka saba",
                              "near": ", duk da cewa ruwan samanta ya kasance kamar yadda aka saba", "": ""},
        "plain_bare": "Mafi yawan gonakin {of} sun nuna ƙasa mara ciyayi {how} a ranin {year}; {top} ce {unit} mafi ƙasa mara ciyayi.",
        "plain_bare_how": {"near": "kamar yadda aka saba", "above": "fiye da yadda aka saba", "below": "ƙasa da yadda aka saba"},
        "plain_rain": "Ruwan sama na {year} ya kasance {how} a mafi yawan {units} na {of}; {top} ce {unit} mafi ruwa, {low} kuma mafi bushewa.",
        "plain_rain_how": {"near": "kamar yadda aka saba", "above": "sama da yadda aka saba", "below": "ƙasa da yadda aka saba"},
        "plain_rain_same": "Ruwan sama na {year} ya kasance {how} ga {units} na {of}: {val} ga dukkansu, domin ragar ruwan "
                           "sama ta kusan kilomita 9 tana ba kowace gunduma ta ƙaramar hukuma adadin tsakiyar ƙaramar hukumar.",
        "plain_flood_little": "Radar ta ga ɗan ruwan ambaliya kaɗan a fili a gonakin {of} da a kullum suka bushe a {year}: ƙasa da "
                              "kashi 1% na gonaki a mafi yawan {units}; {top} ce ta fi yawa ({val}).",
        "plain_flood_some": "Radar ta ga ruwan ambaliya a fili a gonakin {of} da a kullum suka bushe a {year}: {top} ce ta fi "
                            "yawa ({val}); {low} ce mafi ƙaranci ({lo_val}).",
        "plain_map": "Taswirar ambaliya ta tauraron ɗan adam ta MDD ta {period} ta rufe {state_val} na gonakin {of}; {top} ce ta fi "
                     "yawan gonaki a cikinta ({val}), {low} kuma mafi ƙaranci ({lo_val}).",
        "plain_water": "{few} daga cikin {units} na {of} ne ke da gonakin da ruwa ke yawan rufewa; {top} ce ta fi yawa ({val}).",
        "plain_water_few": {"few": "Kaɗan", "some": "Wasu", "many": "Da yawa"},
        "rain_adj": "Idan aka kwatanta kowace {unit} da shekarunta da ruwan saman daminar: {parts}.",
        "rain_below": "{units} sun yi ƙasa da abin da ruwan saman ya nuna",
        "rain_above": "{units} sun fi koriya fiye da yadda ruwan saman ya nuna",
        "rain_adj_none": "babu {unit_of} da ta bambanta da shekarunta da ruwan sama",
        "rain_adj_units": "{what} {n} ba su da isassun shekaru don kwatancen ruwan sama",
        "unit_of": {"ward": "gundumar", "lga": "ƙaramar hukumar"},
        "low_data": "Ƙarancin bayanai: {units} (lura {n} ko ƙasa a shekarar) an yi musu alamar ~ kuma ba a jera su ba.",
        "resolution": "Lokaci {period}; ƙuduri {res}. Gonaki kawai (ESA WorldCover 2021).",
        "ranking_head": "*Jeri ({n} {what})*",
        "top_head": "Mafi girma:", "bottom_head": "Mafi ƙanƙanta:",
        "row": "{i}. {name}: {value} (lura {n})",
        "working_head": "Dukkan {what}, {measure}, {year}: ƙima (lura a bayanta; ~ ƙarancin bayanai; alamar ruwan sama inda aka kwatanta).",
        "working_measure": "Ma'auni: {label}. Lokaci {period}; ƙuduri {res}. Gonaki kawai (ESA WorldCover 2021).",
        "working_row": "{name} [{code}]: {value} ({n}){flag}",
        "flag_below": " ƙasa-da-ruwan-sama", "flag_above": " sama-da-ruwan-sama",
        "map_label": "Taswirar ambaliya ta tauraron ɗan adam ta MDD ta {period} (UNOSAT, VIIRS mita 375)",
        "radar_head": "*Ruwan ambaliya a fili da radar ta gani, ƙaramin kiyasi* (Sentinel-1, mita 200; yana rasa ruwa a "
                      "ƙarƙashin shuke-shuke da ambaliya tsakanin hotuna)",
        "radar_summary": "A {area}, kashin {year} ya tashi daga {lo} ({lo_unit}) zuwa {hi} ({hi_unit}); matsakaici {med}. "
                         "Mafi yawa: {top}. Mafi ƙaranci: {bottom}.",
        "differ": "Sun bambanta domin taswirar MDD (VIIRS, haɗin kwanaki 5 a mita 375) tana ƙidaya ƙasa da ruwa ya rufe ko ya "
                  "jiƙa har da ƙarƙashin shuke-shuke, amma radar tana ƙidaya ruwa a fili mai santsi ne kawai a ranakun "
                  "hotunanta, saboda haka kashin radar koyaushe shi ne ƙarami.",
        "no_map_year": "Babu taswirar ambaliya ta MDD da ta rufe Sokoto a {year} (taswirorin da aka ɗora: Oktoba 2022, Satumba "
                       "da Nuwamba 2024), saboda haka ƙaramin kiyasin radar ne kawai aka nuna.",
        "budget_head": "*Layukan kasafin {year} na Ƙaramar Hukumar {lga} (noma, ban ruwa, zaizayar ƙasa, muhalli)*",
        "budget_row": "• {name}: ₦{amount} ({title}, shafi na {page})",
        "budget_none": "Babu layin kasafin {year} da ya ambaci {lga}; layukan faɗin jiha da ka iya shafarta:",
        "budget_group": "• {group}: ₦{amount} a layuka {n} na faɗin jiha",
        "budget_groups": {"agriculture": "Noma", "irrigation": "Ban ruwa da madatsu", "erosion": "Zaizayar ƙasa da magudanai",
                          "environment": "Muhalli da gandun daji"},
        "budget_source": "({title}; ba a raba layukan faɗin jiha bisa ƙaramar hukuma ba)",
        "budget_nothing": "Babu layin kasafin {year} da ya ambaci {lga}, ba kuma wani layin faɗin jiha na noma, ban ruwa, "
                          "zaizayar ƙasa ko muhalli da aka samu ba.",
        "budget_state": "Ana haɗa layukan kasafi ne a kowace ƙaramar hukuma: tambaya game da ƙaramar hukuma ɗaya don ganin nata.",
        "none": "Ba a riga an ɗora ma'aunan tauraron ɗan adam na {area} ba.",
        "no_year": "Babu {short} na {year}; shekarun da aka ɗora {first}–{last}.",
        "sources": "Madogara: {source}; iyakoki: gundumomin GRID3 da ƙananan hukumomin OCHA COD-AB.",
        "neutral": "Kasafi yana bayyana abin da hotunan tauraron ɗan adam suka nuna ne; ba ya yanke hukunci kan dalilai ko aikin kowa.",
        "and": " da ", "ward": "gunduma", "wards": "gundumomi", "lga": "ƙaramar hukuma", "lgas": "ƙananan hukumomi",
    },
}
BUDGET_TERMS = ["agric", "irrigat", "erosion", "environment", "fadama", "farm", "flood", "gully", "dam ", "dams", "forest"]
STATEWIDE_GROUPS = {                       # the statewide totals offered when no line names the LGA
    "agriculture": ["agric", "farm", "fadama", "seed", "livestock", "fertili", "crop"],
    "irrigation": ["irrigat", "dam ", "dams", "canal", "canel"],
    "erosion": ["erosion", "gully", "drainage"],
    "environment": ["environment", "forest", "desertif", "tree plant", "afforest"],
}


def _t(lang: str) -> dict:
    return W["ha" if lang == "ha" else "en"]


# --- the route ------------------------------------------------------------------------------------------------------

def area_route(question: str, english: str = "", place: dict | None = None) -> tuple[str, str] | None:
    """(level, unit) when a place-history question is about an area, not the user's pin: ('ward', wardcode) for
    'my ward / here / my area' with a pin or saved location, ('lga', pcode) for 'my LGA' or an LGA named,
    ('state', NG034) only for the state, Sokoto or 'all wards / which LGAs'; None otherwise."""
    from app.hazards.advisories import lgas_in
    from app.place.answer import NOT_PLACE, place_route
    text = f"{question} {english}"
    if MY_FARM.search(text) or NOT_PLACE.search(text):
        return None
    measure = measure_word(text)              # a satellite measure must be named: "most IDPs by LGA" is not ours
    place = place or {}
    # the scope comes from the user's own words: the planner's English rewrite spells the place on file out
    # ("in Kware LGA, Sokoto State"), which must never turn "my ward" into the LGA or the state
    own = question if (MY_WARD.search(question) or MY_LGA.search(question) or STATE_WORDS.search(question)) else text
    if measure is not None and STATE_WORDS.search(own) and not lgas_in(own):
        return ("state", STATE)                                   # 'the state', 'faɗin jihar Sokoto': only these
    if measure is not None and not STATE_WORDS.search(own):
        if MY_WARD.search(own) and place.get("wardcode"):        # 'my ward' is the narrower scope: it wins
            return ("ward", str(place["wardcode"]))
        if MY_LGA.search(own) and place.get("lga_pcode"):
            return ("lga", str(place["lga_pcode"]))
        if MY_WARD.search(own) and place.get("lga_pcode"):     # no ward known: the LGA, said as such in the answer
            return ("lga", str(place["lga_pcode"]))
        if (MY_WARD.search(own) or MY_LGA.search(own)) and not lgas_in(own):
            return ("ward", "")                               # nothing on file: the answer asks for the pin
    lgas = lgas_in(text)
    if not (AREA_WORDS.search(text) or lgas):
        return None
    if not (place_route(text) or measure is not None and
            re.search(r"(?i)\b(?:wards?|lgas?|gundum|hukum|which|wa[ɗd]anne|most|least|mafi|share|kashi)\b", text)):
        return None
    if lgas and not re.search(r"(?i)\b(?:all\s+lgas|which\s+lgas|the\s+state|state-?wide|sokoto\s+state|"
                              r"ƙananan\s+hukumomi|kananan\s+hukumomi|jihar?\s+sokoto)\b", text):
        return ("lga", lgas[0])
    return ("state", STATE)


def measure_word(text: str) -> str | None:
    """The measure a question names, or None when it names none."""
    for key, pat in MEASURE_WORDS:
        if pat.search(text):
            return key
    return None


def measure_asked(text: str) -> str:
    return measure_word(text) or "greenness"


def year_asked(text: str, today: date) -> int | None:
    m = re.findall(r"\b((?:19|20)\d\d)\b", re.sub(r"(?i)\bsince\s+(?:19|20)\d\d|\btun\s+20\d\d", " ", text))
    return int(m[0]) if m else None


def trend_asked(text: str) -> bool:
    return bool(TREND.search(text or ""))


SEASON_LAST_DOY = 289          # app/place/area.py: the last Terra composite of the June–October season


def season_complete(conn, year: int, today: date) -> tuple[bool, int]:
    """(complete, last composite's day of year) for a MODIS season from the 'modis_season_last_doy' rows the
    precompute writes (scripts/precompute_area.py --layers season). Without a row, a past year counts as complete
    and the current year never does: the October composites are published in mid-November, so the calendar alone
    can't say (1 Nov 2026: 17 composites to 30 September, the three October ones missing)."""
    row = conn.execute("SELECT value FROM ward_history WHERE measure = 'modis_season_last_doy' AND level = 'state' "
                       "AND unit = %s AND year = %s", (STATE, year)).fetchone()
    if row is None or row[0] is None:
        return year < today.year, 0
    last = int(row[0])
    return last >= SEASON_LAST_DOY, last


def headline_year(conn, measure: str, compare: str, loaded: list[int], today: date) -> tuple[int, list[int], list[tuple[int, int]]]:
    """The latest year with normal data: a complete season in the catalogue (season_complete) and at least 60 % of
    the median observation count for the level. Never a thin year like 2025 (five composites) and never a season
    the catalogue hasn't finished (2026 until mid-November). Returns (year, thin years skipped, unfinished years
    skipped as (year, last day of year)), so the answer says why."""
    counts = {}
    for y in loaded:
        row = conn.execute("SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY n_obs) FROM ward_history WHERE measure = %s "
                           "AND level = %s AND year = %s AND n_obs IS NOT NULL", (measure, compare, y)).fetchone()
        counts[y] = float(row[0]) if row and row[0] is not None else None
    known = sorted(c for c in counts.values() if c is not None)
    need = 0.6 * known[len(known) // 2] if known else 0.0
    season = {y: season_complete(conn, y, today) for y in loaded if y >= today.year - 1}
    done = [y for y in loaded if season.get(y, (True, 0))[0]]
    normal = [y for y in done if counts.get(y) is None or counts[y] >= need]
    y = max(normal) if normal else max(done) if done else loaded[-1]
    later = [x for x in loaded if x > y]
    # the current year's season is 'not complete yet'; an earlier year the catalogue stopped short on (2025: day
    # 177) has 'too few clear images so far', like a year of thin counts
    unfinished = [(x, season[x][1]) for x in later if x == today.year and x in season and not season[x][0]]
    thin = [x for x in later if x not in dict(unfinished) and
            ((counts.get(x) is not None and counts[x] < need) or (x in season and not season[x][0]))]
    return y, thin, unfinished


def doy_text(doy: int, year: int, lang: str) -> str:
    """'30 September' for a day of year (the composite's start day)."""
    from datetime import timedelta
    d = date(year, 1, 1) + timedelta(days=max(doy, 1) - 1)
    months = {"en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                     "November", "December"],
              "ha": ["Janairu", "Fabrairu", "Maris", "Afrilu", "Mayu", "Yuni", "Yuli", "Agusta", "Satumba", "Oktoba",
                     "Nuwamba", "Disamba"]}[lang if lang == "ha" else "en"]
    return f"{d.day} {months[d.month - 1]}"


# --- the data ---------------------------------------------------------------------------------------------------------

def rows_for(conn, measure: str, level: str, year: int, within: str | None) -> list[tuple[str, str, float | None, int | None]]:
    """(unit code, name, value, n_obs) for every unit of the level (wards of an LGA when `within`)."""
    if level == "ward":
        q = ("SELECT h.unit, w.name, h.value, h.n_obs FROM ward_history h JOIN ward w ON w.wardcode = h.unit WHERE "
             "h.level = 'ward' AND h.measure = %s AND h.year = %s" + (" AND w.lga_pcode = %s" if within else "") +
             " ORDER BY w.name")
        args = (measure, year, within) if within else (measure, year)
    else:
        q = ("SELECT h.unit, l.name, h.value, h.n_obs FROM ward_history h JOIN lga l ON l.pcode = h.unit WHERE "
             "h.level = 'lga' AND h.measure = %s AND h.year = %s ORDER BY l.name")
        args = (measure, year)
    return [(r[0], r[1], None if r[2] is None else float(r[2]), r[3]) for r in conn.execute(q, args).fetchall()]


def years_loaded(conn, measure: str, level: str) -> list[int]:
    return [r[0] for r in conn.execute("SELECT DISTINCT year FROM ward_history WHERE measure = %s AND level = %s "
                                       "AND value IS NOT NULL ORDER BY year", (measure, level)).fetchall()]


def series(conn, measure: str, level: str, unit: str) -> dict[int, float]:
    """A unit's yearly values, without its low-data years (under 60% of its own median observation count:
    MODIS 2025 has 5 composites against a usual 16–20, so it never enters a rain fit or a trend)."""
    rows = conn.execute(
        "SELECT year, value, n_obs FROM ward_history WHERE measure = %s AND level = %s AND unit = %s AND value IS NOT "
        "NULL AND year > 0 ORDER BY year", (measure, level, unit)).fetchall()
    return drop_low_data({r[0]: (float(r[1]), r[2]) for r in rows})


def drop_low_data(rows: dict[int, tuple[float, int | None]]) -> dict[int, float]:
    import math
    counts = sorted(n for _, n in rows.values() if n is not None)
    if not counts:
        return {y: v for y, (v, _) in rows.items()}
    need = max(2, math.ceil(0.6 * counts[len(counts) // 2]))
    return {y: v for y, (v, n) in rows.items() if n is None or n >= need}


def usual_of(conn, measure: str, level: str, units: list[str], year: int) -> dict[str, float | None]:
    """Per unit: the median of its other years (its 'usual'), or None with fewer than three."""
    out = {}
    for u in units:
        vals = sorted(v for y, v in series(conn, measure, level, u).items() if y != year)
        out[u] = vals[len(vals) // 2] if len(vals) >= 3 else None
    return out


def versus_usual(value: float | None, usual: float | None, key: str) -> str:
    """'above' | 'near' | 'below' | '' against the unit's own usual: rain by share, the rest by difference."""
    if value is None or usual is None:
        return ""
    if key == "rain":
        if usual <= 0:
            return ""
        return "above" if value > usual * (1 + NEAR["rain"]) else "below" if value < usual * (1 - NEAR["rain"]) else "near"
    tol = NEAR.get(key, 0.05)
    return "above" if value > usual + tol else "below" if value < usual - tol else "near"


def rain_flags(conn, level: str, units: list[str], year: int) -> dict[str, str]:
    """Per unit: 'below' | 'above' | 'normal' | '' from a rain fit of its own MODIS peaks against its rain."""
    out = {}
    for u in units:
        peaks, rains = series(conn, "modis_peak", level, u), series(conn, "rain_season_mm", level, u)
        pts = {y: (peaks[y], rains[y]) for y in peaks if y in rains}
        f = fitting.rain_fit(pts)
        if f is None or year not in f.flags:
            out[u] = ""
            continue
        r = f.residuals[year]
        out[u] = "below" if f.flags[year] == "below" else ("above" if f.sd > 1e-6 and r > f.sd else "normal")
    return out


def low_data_cut(rows: list[tuple], measure: str) -> int:
    """Units with n_obs at or under this are marked low-data: under 60% of the median count, as for a pin."""
    import math
    counts = sorted(n for _, _, v, n in rows if n is not None and v is not None)
    if not counts or measure in ("jrc_recurrence_share", "unosat_share", "rain_season_mm"):
        return -1
    med = counts[len(counts) // 2]
    return max(2, math.ceil(0.6 * med)) - 1


def map_period(year: int, lang: str) -> str:
    """The UN maps' dates in a year ('1–25 October 2022'; '5–9 September and 9–13 November 2024')."""
    from app.place.answer import period_text
    from app.place.floods import load_maps
    g = load_maps()
    if g is None or not len(g):
        return str(year)
    periods = sorted({(str(a), str(b)) for a, b in zip(g["period_start"], g["period_end"]) if str(a)[:4] == str(year)})
    if not periods:
        return str(year)
    return _t(lang)["and"].join(period_text(a, b, lang) for a, b in periods)


# --- the answer ---------------------------------------------------------------------------------------------------------

def _fmt(spec: dict, v: float | None) -> str:
    return "–" if v is None else spec["fmt"].format(v)


def _names(items: list[tuple[str, str, float | None, int | None]], spec: dict, lang: str) -> str:
    return ", ".join(f"{name} ({_fmt(spec, v)})" for _, name, v, _ in items)


@dataclass
class Block:
    """One measure's ranking for one year: the pieces an answer is composed from."""
    key: str
    spec: dict
    year: int
    rows: list
    ranked: list
    low: list
    missing: list
    cut: int
    median: float | None
    flags: dict[str, str] = field(default_factory=dict)
    usual: dict[str, float | None] = field(default_factory=dict)


def block_for(conn, key: str, compare: str, within: str | None, year: int, with_usual: bool = True) -> Block | None:
    spec = MEASURES[key]
    rows = rows_for(conn, spec["measure"], compare, year, within)
    if not rows or all(v is None for _, _, v, _ in rows):
        return None
    cut = low_data_cut(rows, spec["measure"])
    ranked = sorted([r for r in rows if r[2] is not None and (r[3] is None or r[3] > cut)], key=lambda r: -r[2])
    low = [r for r in rows if r[2] is not None and r[3] is not None and r[3] <= cut]
    missing = [r for r in rows if r[2] is None]
    values = [r[2] for r in ranked]
    med = sorted(values)[len(values) // 2] if values else None
    b = Block(key, spec, year, rows, ranked, low, missing, cut, med)
    if key == "greenness" and year:
        b.flags = rain_flags(conn, compare, [r[0] for r in ranked], year)
    if with_usual and key in NEAR and year:
        b.usual = usual_of(conn, spec["measure"], compare, [r[0] for r in ranked], year)
    return b


def plain_sentence(conn, b: Block, lang: str, compare: str, level: str, unit: str, of: str) -> str:
    """The first sentence in plain words, as the hazard summaries do: most units against their own usual, the
    one that stood out, and (for greenness) its rain."""
    t = _t(lang)
    if not b.ranked:
        return ""
    unit_word = t["ward"] if compare == "ward" else t["lga"]
    units_word = t["wards"] if compare == "ward" else t["lgas"]
    top, low = b.ranked[0], b.ranked[-1]
    if b.key in ("greenness", "bare", "rain"):
        how = plain_class(b)
        if b.key == "greenness":
            rain = ""
            rains = series(conn, "rain_season_mm", compare, low[0])
            if b.year in rains:
                others = sorted(v for y, v in rains.items() if y != b.year)
                rain = versus_usual(rains[b.year], others[len(others) // 2] if len(others) >= 3 else None, "rain")
            words = t["plain_green_rain_how"] if b.flags and any(b.flags.values()) else t["plain_green_how"]
            return t["plain_green"].format(of=of, how=words[how], year=b.year, low=low[1], unit=unit_word,
                                           rain=t["plain_rain_clause"][rain])
        if b.key == "bare":
            return t["plain_bare"].format(of=of, how=t["plain_bare_how"][how], year=b.year, top=top[1], unit=unit_word)
        if top[2] - low[2] < 1.0:                          # wards of one LGA share its centre's rain (~9 km grid)
            return t["plain_rain_same"].format(year=b.year, how=t["plain_rain_how"][how], of=of, units=units_word,
                                               val=_fmt(b.spec, top[2]))
        return t["plain_rain"].format(year=b.year, how=t["plain_rain_how"][how], of=of, units=units_word, top=top[1],
                                      unit=unit_word, low=low[1])
    if b.key == "flood":
        little = sum(1 for r in b.ranked if r[2] < LITTLE_SHARE) * 2 >= len(b.ranked)
        key = "plain_flood_little" if little else "plain_flood_some"
        return t[key].format(of=of, year=b.year, units=units_word, top=top[1], val=_fmt(b.spec, top[2]), low=low[1],
                             lo_val=_fmt(b.spec, low[2]))
    if b.key == "flood_map":
        whole = conn.execute("SELECT value FROM ward_history WHERE measure = 'unosat_share' AND level = %s AND unit = %s "
                             "AND year = %s", ("lga" if level == "lga" else "state", unit, b.year)).fetchone()
        return t["plain_map"].format(period=map_period(b.year, lang), state_val=_fmt(b.spec, float(whole[0])) if whole else
                                     _fmt(b.spec, b.median), of=of, top=top[1], val=_fmt(b.spec, top[2]), low=low[1],
                                     lo_val=_fmt(b.spec, low[2]))
    if b.key == "water":
        share = sum(1 for r in b.ranked if r[2] >= 0.02) / len(b.ranked)
        few = "few" if share < 0.34 else "some" if share < 0.67 else "many"
        return t["plain_water"].format(few=t["plain_water_few"][few], of=of, units=units_word, top=top[1], val=_fmt(b.spec, top[2]))
    return ""


def plain_class(b: Block) -> str:
    """The class the plain sentence states, from the same numbers as the details: for greenness, the rain-adjusted
    flags when any ward was fitted (most 'normal' -> 'about as green as the rain would suggest'; a majority below
    or above -> that), else each unit against its own usual. The summary can never say 'less green than usual'
    while the rain check found nothing standing out."""
    if b.key == "greenness" and b.flags and any(b.flags.values()):
        fitted = [f for f in b.flags.values() if f]
        below, above = fitted.count("below"), fitted.count("above")
        if below * 2 > len(fitted):
            return "below"
        if above * 2 > len(fitted):
            return "above"
        return "near"
    kinds = [versus_usual(r[2], b.usual.get(r[0]), b.key) for r in b.ranked]
    kinds = [k for k in kinds if k]
    return max(("near", "above", "below"), key=lambda k: kinds.count(k)) if kinds else "near"


def summary_lines(b: Block, lang: str, area: str, what: str, radar_block: bool = False) -> list[str]:
    """The figures sentence, the rain-adjusted sentence (greenness) and the low-data line."""
    t = _t(lang)
    spec, y = b.spec, b.year
    lines = []
    if b.ranked:
        top, bottom = b.ranked[:3], b.ranked[-3:][::-1] if len(b.ranked) > 3 else []
        if radar_block:
            lines.append(t["radar_summary"].format(
                area=area, year=y, lo=_fmt(spec, b.ranked[-1][2]), lo_unit=b.ranked[-1][1], hi=_fmt(spec, b.ranked[0][2]),
                hi_unit=b.ranked[0][1], med=_fmt(spec, b.median), top=_names(top, spec, lang),
                bottom=_names(bottom, spec, lang) or "–"))
        else:
            lines.append((t["summary"] if y else t["summary_noyear"]).format(
                area=area, year=y, short=t["short"][b.key], lo=_fmt(spec, b.ranked[-1][2]), lo_unit=b.ranked[-1][1],
                hi=_fmt(spec, b.ranked[0][2]), hi_unit=b.ranked[0][1], med=_fmt(spec, b.median),
                high_word=spec[f"high_{'ha' if lang == 'ha' else 'en'}"].capitalize(), top=_names(top, spec, lang),
                low_word=spec[f"low_{'ha' if lang == 'ha' else 'en'}"].capitalize(), bottom=_names(bottom, spec, lang) or "–"))
    if b.key == "greenness" and y and b.flags:
        names = {r[0]: r[1] for r in b.ranked}
        below = [names[u] for u, f in b.flags.items() if f == "below"]
        above = [names[u] for u, f in b.flags.items() if f == "above"]
        unfit = sum(1 for f in b.flags.values() if f == "")
        kind = "ward" if what == t["wards"] else "lga"
        parts = []
        if below:
            parts.append(t["rain_below"].format(units=", ".join(below)))
        if above:
            parts.append(t["rain_above"].format(units=", ".join(above)))
        if not parts:
            parts.append(t["rain_adj_none"].format(unit=t[kind], unit_of=t["unit_of"][kind]))
        if unfit:
            parts.append(t["rain_adj_units"].format(n=unfit, what=what))
        s = t["rain_adj"].format(unit=t[kind], parts="; ".join(parts))
        lines.append(s[0].upper() + s[1:])
    if b.low:
        lines.append(t["low_data"].format(units=", ".join(r[1] for r in b.low[:6]) + (" …" if len(b.low) > 6 else ""), n=b.cut))
    return lines


def ranking_lines(b: Block, lang: str, what: str) -> str:
    t = _t(lang)
    spec = b.spec
    rank_lines = [t["ranking_head"].format(n=len(b.ranked), what=what), t["top_head"]]
    rank_lines += [t["row"].format(i=i, name=r[1], value=_fmt(spec, r[2]), n=r[3] if r[3] is not None else "–")
                   for i, r in enumerate(b.ranked[:TOP_N], 1)]
    if len(b.ranked) > TOP_N:
        rank_lines.append(t["bottom_head"])
        rank_lines += [t["row"].format(i=len(b.ranked) - j, name=r[1], value=_fmt(spec, r[2]), n=r[3] if r[3] is not None else "–")
                       for j, r in enumerate(reversed(b.ranked[-TOP_N:]))][::-1]
    return "\n".join(rank_lines)


def working_lines(b: Block, lang: str, what: str, period: str) -> list[str]:
    t = _t(lang)
    spec = b.spec
    working = [t["working_head"].format(what=what, measure=spec["measure"], year=b.year or period)]
    for code, name, v, n in sorted(b.rows, key=lambda r: (r[2] is None, -(r[2] or 0))):
        flag = {"below": t["flag_below"], "above": t["flag_above"]}.get(b.flags.get(code, ""), "")
        lowmark = "~" if (n is not None and n <= b.cut and v is not None) else ""
        working.append(t["working_row"].format(name=name, code=code, value=lowmark + _fmt(spec, v), n=n if n is not None else "–",
                                               flag=flag))
    if b.missing:
        working.append(f"({len(b.missing)} {what}: no value)")
    return working


def area_answer(conn, question: str, english: str, lang: str, level: str, unit: str, today: date,
                measure_key: str | None = None, year: int | None = None, place: dict | None = None) -> AreaAnswer:
    from app.sources.lga_names import name_of
    t = _t(lang)
    text = f"{question} {english}"
    key = measure_key or measure_asked(text)
    spec = MEASURES[key]
    measure = spec["measure"]
    if level == "ward":
        return ward_answer(conn, question, english, lang, unit, today, key, year, place or {})
    compare = "ward" if level == "lga" else ("ward" if re.search(r"(?i)\bwards?\b|gundum", text) and level == "state" else "lga")
    within = unit if level == "lga" else None
    area = (t["area_lga"].format(lga=name_of(unit)) if level == "lga" else
            t["area_state_wards"] if compare == "ward" else t["area_state"])
    of = t["of_lga"].format(lga=name_of(unit)) if level == "lga" else t["of_state"]
    loaded = years_loaded(conn, measure, compare)
    map_years = years_loaded(conn, "unosat_share", compare) if key == "flood" else []
    if not loaded:
        return AreaAnswer(t["none"].format(area=area), False, level=compare, unit=unit, measure=measure)
    want = year if year is not None else year_asked(text, today)
    if spec["first"] == 0:
        y = 0
    elif want is not None and want in loaded:
        y = want
    elif want is not None:
        return AreaAnswer(t["no_year"].format(short=t["short"][key], year=want, first=loaded[0], last=loaded[-1]), False,
                          level=compare, unit=unit, measure=measure)
    elif key == "flood" and map_years:                   # no year named: the latest year with an official map
        y, skipped, unfinished = max(map_years), [], []
    else:                                                # the latest year with normal data: never a thin year
        y, skipped, unfinished = headline_year(conn, measure, compare, loaded, today)
    if want is not None or spec["first"] == 0 or (key == "flood" and map_years):
        skipped, unfinished = [], []
    what = t["wards"] if compare == "ward" else t["lgas"]
    period = f"{loaded[0]}–{loaded[-1]}" if spec["first"] else "1984–2020"      # the years actually loaded
    res = {"greenness": "250 m", "flood": "200 m", "flood_map": "375 m", "water": "30 m", "bare": "200 m", "rain": "~9 km"}[key]
    lines: list[str] = []
    working: list[str] = []
    specs: list[dict] = []
    partial = False
    # floods: the official map leads when the year has one; radar follows as a lower bound
    lead_key = "flood_map" if key == "flood" and y in map_years else key
    main = block_for(conn, lead_key, compare, within, y)
    if main is None:
        return AreaAnswer(t["none"].format(area=area), False, level=compare, unit=unit, measure=measure, year=y)
    label = (t["map_label"].format(period=map_period(y, lang)) if lead_key == "flood_map" and y else
             spec[lang if lang == "ha" else "en"] if lead_key == key else MEASURES[lead_key][lang if lang == "ha" else "en"])
    short = t["short"][lead_key]
    lines.append(t["head_plain"].format(short=short[0].upper() + short[1:], area=area, year=f", {y}" if y else ""))
    if place and (place.get("lga_pcode") == unit) and MY_WARD.search(text) and not place.get("wardcode"):
        lines.append(t["ward_scope_no_ward"].format(lga=name_of(unit)))
    plain = plain_sentence(conn, main, lang, compare, level, unit, of)
    if plain:
        lines.append(plain)
    if trend_asked(text) and lead_key == key and spec["first"]:         # 'over the years': the unit's own trend first
        lines.append(trend_sentence(conn, lang, measure, "lga" if level == "lga" else "state", unit, of))
    lines.append(skipped_line(t, lang, y, skipped, unfinished))
    lines += summary_lines(main, lang, area, what)
    lines.append(missing_line(conn, main, lang, compare, within, what))
    lines.append(ranking_lines(main, lang, what))
    working.append(t["working_measure"].format(label=label, period=period if lead_key == key else f"{min(map_years)}–{max(map_years)}",
                                               res="375 m" if lead_key == "flood_map" else res))
    working += working_lines(main, lang, what, period)
    specs.append({"kind": "area_map", "measure": MEASURES[lead_key]["measure"], "key": lead_key, "year": y, "level": compare,
                  "unit": unit})
    partial = bool(main.missing)
    if key == "flood":
        radar = block_for(conn, "flood", compare, within, y, with_usual=False) if lead_key == "flood_map" else None
        if radar is not None:
            lines.append(t["radar_head"])
            lines += summary_lines(radar, lang, area, what, radar_block=True)
            lines.append(t["differ"])
            working += working_lines(radar, lang, what, period)
            specs.append({"kind": "area_map", "measure": "s1_flood_share", "key": "flood", "year": y, "level": compare, "unit": unit})
            partial = partial or bool(radar.missing)
        elif lead_key == "flood":
            lines.append(t["no_map_year"].format(year=y))
    # the budget link
    lines.append(budget_block(conn, lang, level, unit, today))
    lines.append(t["neutral"])
    sources = [conn.execute("SELECT source FROM ward_history WHERE measure = %s LIMIT 1", (s["measure"],)).fetchone()[0]
               for s in specs]
    lines.append(t["sources"].format(source="; ".join(dict.fromkeys(sources))))
    return AreaAnswer("\n\n".join(x for x in lines if x), True, "\n".join(working), partial=partial, specs=specs,
                      level=compare, unit=unit, measure=MEASURES[lead_key]["measure"], year=y)


def skipped_line(t: dict, lang: str, y: int, thin: list[int], unfinished: list[tuple[int, int]]) -> str:
    """Why later years don't lead: too few clear images (2025), or a season the catalogue hasn't finished (2026)."""
    parts = []
    if unfinished:
        s = t["unfinished_years"].format(years=", ".join(str(x) for x, _ in unfinished),
                                         last=t["and"].join(doy_text(d, x, lang) for x, d in unfinished if d),
                                         verb=t["unfinished_verb"]["one" if len(unfinished) == 1 else "many"])
        if not all(d for _, d in unfinished):      # no catalogue row: the reason without a date
            s = s[:s.rindex(" (")]
        parts.append(s)
    if thin:
        parts.append(t["thin_years"].format(years=", ".join(str(x) for x in thin),
                                            verb=t["skipped_verb"]["one" if len(thin) == 1 else "many"]))
    if not parts:
        return ""
    s = t["skipped_years"].format(why="; ".join(parts), year=y)
    return s[0].upper() + s[1:]


def trend_of(conn, measure: str, level: str, unit: str) -> tuple[str, int, int, int]:
    """(direction, first year, last year, years) of a unit's series without its low-data years."""
    vals = series(conn, measure, level, unit)
    if not vals:
        return "", 0, 0, 0
    tr = fitting.trend(vals)
    years = sorted(vals)
    return (tr[0] if tr else ""), years[0], years[-1], len(years)


def trend_sentence(conn, lang: str, measure: str, level: str, unit: str, of: str) -> str:
    t = _t(lang)
    d, first, last, n = trend_of(conn, measure, level, unit)
    if not n:
        return ""
    return t["trend_unit"].format(first=first, of=of, dir=t["trend_dir"][d], n=n)


def coverage(conn, compare: str, within: str | None, rows: list[tuple], cut: int) -> dict[str, int]:
    """The units of the level (the wards of an LGA, all wards, or the LGAs): how many carry a value that year, how
    many have no cropland in the land-cover map (so no row at all), how many are low data, and how many have no
    data for another reason. The answer's missing line and the map's caption both come from this."""
    if compare == "ward":
        q = "SELECT wardcode FROM ward" + (" WHERE lga_pcode = %s" if within else "")
        units = {r[0] for r in conn.execute(q, (within,) if within else ()).fetchall()}
    else:
        units = {r[0] for r in conn.execute("SELECT pcode FROM lga").fetchall()}
    valued = {r[0] for r in rows if r[2] is not None and (r[3] is None or r[3] > cut)}
    low = {r[0] for r in rows if r[2] is not None and r[3] is not None and r[3] <= cut}
    no_crop = {r[0] for r in conn.execute(
        "SELECT unit FROM ward_history WHERE measure = 'cropland_cells' AND level = %s AND value = 0", (compare,)).fetchall()}
    no_crop &= units - valued - low
    no_data = units - valued - low - no_crop
    return {"total": len(units), "valued": len(valued), "low": len(low), "no_crop": len(no_crop), "no_data": len(no_data)}


def missing_line(conn, b: Block, lang: str, compare: str, within: str | None, what: str) -> str:
    """Why units are missing from the ranking: no cropland in the land-cover map, or no data that year."""
    t = _t(lang)
    c = coverage(conn, compare, within, b.rows, b.cut)
    if not c["no_crop"] and not c["no_data"]:
        return ""
    if c["no_data"] == 0:
        return t["missing_crop_only"].format(no_crop=c["no_crop"], what=what)
    if c["no_crop"] == 0:
        return t["missing_data_only"].format(no_data=c["no_data"], what=what)
    return t["missing_units"].format(no_crop=c["no_crop"], what=what, no_data=c["no_data"], what_data=what)


def ward_answer(conn, question: str, english: str, lang: str, wardcode: str, today: date, key: str,
                year: int | None, place: dict) -> AreaAnswer:
    """'My ward', 'here', 'my area' with a pin: that ward against its LGA and the state. 'Over the years' gives the
    trend over all years with normal data; a single year only when one is asked; otherwise the latest year with
    normal data, said why. The ward and LGA used are named, 'likely' when the pin sits near a ward border."""
    from app.sources.lga_names import name_of
    t = _t(lang)
    text = f"{question} {english}"
    spec = MEASURES[key]
    measure = spec["measure"]
    if not wardcode:
        from app.place.answer import W as PW
        return AreaAnswer(PW["ha" if lang == "ha" else "en"]["need_pin"], False, level="ward", needs_pin=True)
    row = conn.execute("SELECT name, lga_pcode FROM ward WHERE wardcode = %s", (wardcode,)).fetchone()
    if row is None:
        return AreaAnswer(t["none"].format(area=t["ward"]), False, level="ward", unit=wardcode, measure=measure)
    ward, lga_pcode = row
    lga = name_of(lga_pcode)
    likely = t["likely"] if place.get("ward_likely") else ""
    loaded = years_loaded(conn, measure, "ward")
    if not loaded:
        return AreaAnswer(t["none"].format(area=f"{ward}, {lga}"), False, level="ward", unit=wardcode, measure=measure)
    want = year if year is not None else year_asked(text, today)
    if want is not None and want not in loaded:
        return AreaAnswer(t["no_year"].format(short=t["short"][key], year=want, first=loaded[0], last=loaded[-1]), False,
                          level="ward", unit=wardcode, measure=measure)
    y, skipped, unfinished = (want, [], []) if want is not None else headline_year(conn, measure, "ward", loaded, today)
    short = t["short"][key]
    lines = [t["head_ward"].format(short=short[0].upper() + short[1:], ward=ward, likely=likely, lga=lga),
             t["ward_scope"].format(ward=ward, likely=likely, lga=lga)]
    wanted_trend = trend_asked(text) or want is None
    trend_line = ""
    if wanted_trend and spec["first"]:
        wd, first, last, n = trend_of(conn, measure, "ward", wardcode)
        ld = trend_of(conn, measure, "lga", lga_pcode)[0]
        sd = trend_of(conn, measure, "state", STATE)[0]
        if n:
            what = ("farmland greenness" if lang != "ha" else "koriyar gonaki") if key == "greenness" else short
            trend_line = t["trend_head"].format(first=first, last=last, n=n, ward=ward, dir=t["trend_dir"][wd],
                                                lga=lga, lga_dir=t["trend_dir"][ld], state_dir=t["trend_dir"][sd],
                                                what=what)
    # what was asked leads: a trend question opens with the trend; otherwise the year's finding comes first and
    # the trend follows as context (2 Nov: 'Has this area ever flooded' opened with a greenness trend)
    if trend_line and trend_asked(text):
        lines.append(trend_line)
        trend_line = ""
    # the headline year: the ward against its own usual, its LGA's wards and the state
    rows = rows_for(conn, measure, "ward", y, lga_pcode)
    cut = low_data_cut(rows, measure)
    ranked = sorted([r for r in rows if r[2] is not None and (r[3] is None or r[3] > cut)], key=lambda r: -r[2])
    mine = next((r for r in rows if r[0] == wardcode), None)
    usual = usual_of(conn, measure, "ward", [wardcode], y).get(wardcode)
    flags = rain_flags(conn, "ward", [wardcode], y) if key == "greenness" else {}
    state_row = conn.execute("SELECT value FROM ward_history WHERE measure = %s AND level = 'state' AND unit = %s AND year = %s",
                             (measure, STATE, y)).fetchone()
    if mine is not None and mine[2] is not None:
        b = Block(key, spec, y, rows, [mine], [], [], cut, mine[2], flags, {wardcode: usual})
        how_key = plain_class(b)
        words = (t["ward_green_rain_how"] if flags.get(wardcode) else t["ward_green_how"]) if key == "greenness" else \
            t["plain_rain_how"] if key == "rain" else t["plain_bare_how"]
        how = words.get(how_key, how_key)
        pos = next((i for i, r in enumerate(ranked, 1) if r[0] == wardcode), None)
        if ranked and pos is not None and state_row and state_row[0] is not None:
            lines.append(t["ward_year"].format(year=y, ward=ward, how=how, value=_fmt(spec, mine[2]), usual=_fmt(spec, usual),
                                               lga=lga, lo=_fmt(spec, ranked[-1][2]), hi=_fmt(spec, ranked[0][2]), rank=pos,
                                               m=len(ranked), state=_fmt(spec, float(state_row[0]))))
        else:
            lines.append(t["ward_year_norain"].format(year=y, ward=ward, how=how, value=_fmt(spec, mine[2]), usual=_fmt(spec, usual)))
    if trend_line:
        lines.append(trend_line)
    lines.append(skipped_line(t, lang, y, skipped, unfinished))
    res = {"greenness": "250 m", "flood": "200 m", "flood_map": "375 m", "water": "30 m", "bare": "200 m", "rain": "~9 km"}[key]
    period = f"{loaded[0]}–{loaded[-1]}" if spec["first"] else "1984–2020"
    lines.append(budget_block(conn, lang, "lga", lga_pcode, today))
    lines.append(t["neutral"])
    source = conn.execute("SELECT source FROM ward_history WHERE measure = %s LIMIT 1", (measure,)).fetchone()[0]
    lines.append(t["sources"].format(source=source))
    working = [t["working_measure"].format(label=spec[lang if lang == "ha" else "en"], period=period, res=res)]
    for lvl, u, name in (("ward", wardcode, ward), ("lga", lga_pcode, lga), ("state", STATE, "Sokoto State")):
        rows_s = conn.execute("SELECT year, value, n_obs FROM ward_history WHERE measure = %s AND level = %s AND unit = %s "
                              "AND year > 0 ORDER BY year", (measure, lvl, u)).fetchall()
        working.append(t["working_series"].format(measure=f"{name}, {measure}", res=res, rows="; ".join(
            f"{yy} {_fmt(spec, float(v)) if v is not None else '–'} ({n if n is not None else '–'})" for yy, v, n in rows_s)))
    if flags:
        working.append(t["working_row"].format(name=ward, code=wardcode, value=_fmt(spec, mine[2] if mine else None),
                                               n=mine[3] if mine else "–", flag={"below": t["flag_below"], "above": t["flag_above"]}.get(flags.get(wardcode, ""), "")))
    specs = [{"kind": "area_map", "measure": measure, "key": key, "year": y, "level": "ward", "unit": lga_pcode,
              "highlight": wardcode}]
    return AreaAnswer("\n\n".join(x for x in lines if x), True, "\n".join(working), specs=specs, level="ward",
                      unit=wardcode, measure=measure, year=y)


def statewide_totals(conn, year: int | None = None) -> tuple[dict[str, tuple[int, float]], str, int] | None:
    """Per group (agriculture, irrigation, erosion, environment): (lines, approved total) among the budget's
    statewide project lines, with the document id and year; None without a project list."""
    from app.agent.analysis import STATEWIDE, _col, _terms_sql, budget_doc
    picked = budget_doc(conn, year, need_projects=True)
    if not picked:
        return None
    doc, yr = picked
    cur = _col(f"approved_{yr}")
    out = {}
    for group, terms in STATEWIDE_GROUPS.items():
        cond, a = _terms_sql(terms)
        n, s = conn.execute(f"SELECT count(*), sum({cur}) FROM projects p WHERE doc_id = %s AND location_code = %s AND "
                            f"COALESCE({cur}, 0) > 0 AND {cond}", [doc, STATEWIDE] + a).fetchone()
        if n:
            out[group] = (int(n), float(s or 0))
    return out, doc, yr


def budget_block(conn, lang: str, level: str, unit: str, today: date) -> str:
    """The LGA's lines; when none names it, the statewide totals that may cover it (never just 'no line')."""
    from app.agent.analysis import _titles, lga_projects
    from app.sources.lga_names import name_of
    t = _t(lang)
    if level != "lga":
        return t["budget_state"]
    lga = name_of(unit)
    try:
        res = lga_projects(conn, {"lga": lga, "terms": BUDGET_TERMS})
    except Exception as e:                      # noqa: BLE001 - the link is extra
        log.warning("place: budget link failed: %s", type(e).__name__)
        return ""
    if res is not None and res.found and res.rows:
        rows = [t["budget_row"].format(name=r.name, amount=f"{r.amount:,.0f}", title=res.titles.get(r.doc_id, r.doc_id), page=r.page)
                for r in res.rows[:6]]
        return t["budget_head"].format(year=res.year, lga=res.subject) + "\n" + "\n".join(rows)
    year = getattr(res, "year", 0) or today.year
    try:
        totals = statewide_totals(conn, year if getattr(res, "year", 0) else None)
    except Exception as e:                      # noqa: BLE001
        log.warning("place: statewide totals failed: %s", type(e).__name__)
        totals = None
    if not totals or not totals[0]:
        return t["budget_nothing"].format(year=year, lga=lga)
    groups, doc, yr = totals
    title = _titles(conn, {doc}).get(doc, doc)
    rows = [t["budget_group"].format(group=t["budget_groups"][g], amount=f"{s:,.0f}", n=n) for g, (n, s) in groups.items()]
    return t["budget_none"].format(year=yr, lga=lga) + "\n" + "\n".join(rows) + "\n" + t["budget_source"].format(title=title)
