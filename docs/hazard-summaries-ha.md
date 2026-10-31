# Hazard summaries in Hausa: every template, for correction

Generated from `app/hazards/summary.py` and `app/hazards/categories.py` by `scripts/summary_templates_doc.py`. Correct the Hausa column here; Kasafi copies the corrections into the code and regenerates this file.

- `{...}` are filled in by the code: `{place}`, `{day}`, `{cat}` (a category name, below), `{meaning}` (an official meaning, below), `{lga}`, `{worst}`, `{n}`, `{a}` / `{b}` / `{x}` (multiples), `{other}` (today / tomorrow), `{when}`, `{src}`, `{date}`, `{point}`, `{period}`, `{level}`.
- A summary is 2-3 sentences: the meaning sentence, then the driver with the comparisons (joined with “; ”), then the official warning status.
- Text marked *(fassarar bayanin US EPA)* or *(fassarar bayanin NWS)* is Kasafi's translation of the official English wording, shown as such in every answer.

## Places and days

| Key | Hausa | English |
|---|---|---|
| `place_state` | Jihar Sokoto | Sokoto State |
| `place_lga` | Ƙaramar Hukumar {lga} | {lga} LGA |
| `place_named` | {place} (Ƙaramar Hukumar {lga}) | {place} ({lga} LGA) |
| `today` | yau | today |
| `tomorrow` | gobe | tomorrow |
| `in_lga` | A {lga},  | In {lga},  |

## Dust and air quality

| Key | Hausa | English |
|---|---|---|
| `air` | Ingancin iska a {place} {day} *{cat}* ne a ma'aunin US AQI; US EPA ta bayyana shi da “{meaning}” (fassarar bayanin US EPA). | Air quality in {place} {day} is *{cat}* on the US AQI, which the US EPA describes as “{meaning}”. |
| `air_state` | A faɗin Jihar Sokoto {day}, ingancin iska galibi *{cat}* ne (ƙananan hukumomi {n} cikin 23); US EPA ta bayyana shi da “{meaning}” (fassarar bayanin US EPA); ya fi muni a {worst} (*{wcat}*). | Across Sokoto State {day}, air quality is mostly *{cat}* ({n} of 23 LGAs), which the US EPA describes as “{meaning}”; it is worst in {worst} (*{wcat}*). |
| `air_driver.PM2.5` | Ƙananan ƙwayoyi (PM2.5) ne suka ƙayyade AQI | Fine particles (PM2.5) set the AQI |
| `air_driver.PM10` | Ƙura (PM10) ce ta ƙayyade AQI | Coarse dust (PM10) sets the AQI |
| `air_mult` | {driver}: {mult} | {driver}: {mult} |
| `both` | PM2.5 ya kai kusan ninki {a}, PM10 kuma kusan ninki {b} na iyakar WHO ta yini | PM2.5 is about {a} times and PM10 about {b} times the WHO daily guideline |
| `one` | {name} ya kai kusan ninki {x} na iyakar WHO ta yini, {other} kuma yana cikin iyakar | {name} is about {x} times the WHO daily guideline, {other} within it |
| `neither` | PM2.5 da PM10 suna cikin iyakokin WHO na yini | PM2.5 and PM10 are within the WHO daily guidelines |

## Heat

| Key | Hausa | English |
|---|---|---|
| `heat` | Zafi a {place} {day} ya kai *{cat}* a ma'aunin zafi na US National Weather Service; NWS ta bayyana shi da “{meaning}” (fassarar bayanin NWS). | Heat in {place} {day} reaches *{cat}* on the US National Weather Service heat index scale, which the NWS describes as “{meaning}”. |
| `heat_below` | Zafi a {place} {day} bai kai matakin 'A kula' na ma'aunin zafi na US National Weather Service ba. | Heat in {place} {day} stays below the US National Weather Service heat index Caution level. |
| `heat_state` | A faɗin Jihar Sokoto {day}, zafi ya kai *{cat}* a inda ya fi (a {worst}); NWS ta bayyana shi da “{meaning}” (fassarar bayanin NWS); {danger}. | Across Sokoto State {day}, heat reaches *{cat}* at worst (in {worst}), which the US National Weather Service describes as “{meaning}”; {danger}. |
| `danger_n.0` | babu ƙaramar hukumar da ke matakin Haɗari ko sama | no LGA is at Danger or above |
| `danger_n.1` | ƙaramar hukuma 1 cikin 23 ce ke matakin Haɗari ko sama | 1 of the 23 LGAs is at Danger or above |
| `danger_n.n` | ƙananan hukumomi {n} cikin 23 suna matakin Haɗari ko sama | {n} of the 23 LGAs are at Danger or above |
| `heat_driver.air_temperature` | Zafin iskar kanta ne ya kawo shi (iskar ta bushe sosai da danshi ba zai ƙara masa ba) | It comes from the air temperature itself (the air is too dry for humidity to add to it) |
| `heat_driver.heat_index` | Zafi da danshi tare ne suka kawo shi | It comes from heat and humidity together |

## Rain

| Key | Hausa | English |
|---|---|---|
| `rain` | Ana sa ran ruwan sama *{cls}* a {place} {day} (rabe-raben WMO). | {place} expects *{cls}* rain {day} (WMO rainfall intensity class). |
| `rain_none` | Ba a sa ran ruwan sama a {place} {day} ba. | {place} expects no rain {day}. |
| `rain_state` | {wet} {day}, mafi yawa a {worst} (*{cls}*, rabe-raben WMO). | {wet} {day}, the most in {worst} (*{cls}*, WMO rainfall intensity class). |
| `wet_n.1` | Ƙaramar hukuma 1 cikin 23 ce ke sa ran ruwan sama | 1 of the 23 LGAs expects rain |
| `wet_n.n` | Ƙananan hukumomi {n} cikin 23 suna sa ran ruwan sama | {n} of the 23 LGAs expect rain |
| `rain_state_none` | Babu ƙaramar hukuma a Jihar Sokoto da ke sa ran ruwan sama {day}. | No LGA in Sokoto State expects rain {day}. |

## Rivers

| Key | Hausa | English |
|---|---|---|
| `river` | A samfurin GloFAS, {point} yana *{level}* a {period}. | By the GloFAS model, the {point} is *{level}* for {period}. |
| `river_none` | Babu hasashen koguna na {place} {day}. | There is no river forecast for {place} {day}. |
| `levels.low` | ƙasa da yadda aka saba | low |
| `levels.normal` | kamar yadda aka saba | normal |
| `levels.high` | sama da yadda aka saba | high |
| `levels.very_high` | sama sosai da yadda aka saba | very high |
| `parts.early` | farkon | early |
| `parts.mid` | tsakiyar | mid |
| `parts.late` | ƙarshen | late |
| `months` | Janairu, Fabrairu, Maris, Afrilu, Mayu, Yuni, Yuli, Agusta, Satumba, Oktoba, Nuwamba, Disamba | January, February, March, April, May, June, July, August, September, October, November, December |

## Fires

| Key | Hausa | English |
|---|---|---|
| `fires` | Tauraron ɗan adam ya gano alamun zafi {n} (na iya zama gobarar daji, gona ko wata) a {place} a awa 24 da suka wuce. | Satellites detected {n} heat sources (could be bush, farm or other fires) in {place} in the last 24 hours. |
| `fires_none` | Tauraron ɗan adam bai gano alamun zafi (gobara) a {place} a awa 24 da suka wuce ba. | Satellites detected no heat sources (fires) in {place} in the last 24 hours. |

## Comparisons and rank

| Key | Hausa | English |
|---|---|---|
| `trend.air.up` | {other} zai fi muni{cat} | {other} looks worse{cat} |
| `trend.air.down` | {other} zai fi kyau{cat} | {other} looks better{cat} |
| `trend.air.same` | {other} zai yi kama da haka | {other} looks similar |
| `trend.heat.up` | {other} ya fi zafi{cat} | {other} is hotter{cat} |
| `trend.heat.down` | {other} bai kai haka zafi ba{cat} | {other} is cooler{cat} |
| `trend.heat.same` | {other} kusan haka yake | {other} is about the same |
| `trend_cat` |  (*{cat}*) |  (*{cat}*) |
| `rank_top` | {place} na cikin 5 mafi muni a cikin ƙananan hukumomi 23 | {place} is among the 5 worst of the 23 LGAs |
| `rank_low` | {place} na cikin 5 da abin ya fi sauƙi a cikin ƙananan hukumomi 23 | {place} is among the 5 least affected of the 23 LGAs |

## Official warning status (the last sentence)

| Key | Hausa | English |
|---|---|---|
| `status_none` | Babu gargaɗin hukuma mai aiki daga NEMA, SEMA ko Ma'aikatar Lafiya (an duba {when}). | No official warning is in force from NEMA, SEMA or the Ministry of Health (checked {when}). |
| `status_stale` | Babu gargaɗin hukuma mai aiki lokacin da aka duba gargaɗin NEMA, SEMA da Ma'aikatar Lafiya na ƙarshe ({when}). | No official warning was in force when NEMA, SEMA and Ministry of Health alerts were last checked ({when}). |
| `status_unchecked` | Kasafi bai samu damar duba gargaɗin NEMA, SEMA ko Ma'aikatar Lafiya ba tukuna. | Kasafi hasn't yet been able to check NEMA, SEMA or Ministry of Health alerts. |
| `status_live` | Akwai gargaɗin hukuma daga {src} mai aiki (an fitar {date}); an kawo shi a ƙasa. | An official {src} warning is in force (issued {date}), quoted below. |
| `when_today` | {t} yau | {t} today |
| `when_yesterday` | jiya {t} | yesterday {t} |

## US EPA: what each AQI category means (fassarar bayanin US EPA)

Quoted in English from AirNow “AQI Basics”; the Hausa is Kasafi's translation.

| Category | Hausa name | Hausa meaning (translation) | Official English |
|---|---|---|---|
| `good` | Mai kyau | Ingancin iska yana da gamsarwa, kuma gurɓacewar iska ba ta da haɗari ko kuma kaɗan ne | Air quality is satisfactory, and air pollution poses little or no risk |
| `moderate` | Matsakaici | Ingancin iska abin karɓa ne. Sai dai akwai yiwuwar haɗari ga wasu mutane, musamman waɗanda gurɓatacciyar iska ke shafa fiye da kima | Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution |
| `unhealthy_sensitive` | Mara kyau ga masu rauni | Mutane masu rauni na iya fuskantar illa ga lafiya. Ba a cika tsammanin sauran jama'a za su shafu ba | Members of sensitive groups may experience health effects. The general public is less likely to be affected |
| `unhealthy` | Mara kyau | Wasu daga cikin jama'a na iya fuskantar illa ga lafiya; masu rauni na iya fuskantar illa mafi tsanani | Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects |
| `very_unhealthy` | Mara kyau sosai | Faɗakarwar lafiya: haɗarin illa ga lafiya ya ƙaru ga kowa | Health alert: The risk of health effects is increased for everyone |
| `hazardous` | Mai haɗari | Gargaɗin lafiya na yanayin gaggawa: kowa zai fi yiwuwa ya shafu | Health warning of emergency conditions: everyone is more likely to be affected |

## US National Weather Service: what each heat index category means (fassarar bayanin NWS)

Quoted in English from the NWS heat index chart; the Hausa is Kasafi's translation.

| Category | Hausa name | Hausa meaning (translation) | Official English |
|---|---|---|---|
| `caution` | A kula | Gajiya na iya faruwa idan aka daɗe a cikin zafin da/ko aka yi aiki | Fatigue possible with prolonged exposure and/or physical activity |
| `extreme_caution` | A kula sosai | Bugun rana, murɗewar tsoka da/ko gajiyar zafi na iya faruwa idan aka daɗe a ciki da/ko aka yi aiki | Sunstroke, muscle cramps, and/or heat exhaustion possible with prolonged exposure and/or physical activity |
| `danger` | Haɗari | Bugun rana, murɗewar tsoka da/ko gajiyar zafi suna da yiwuwa. Bugun zafi na iya faruwa idan aka daɗe a ciki da/ko aka yi aiki | Sunstroke, muscle cramps, and/or heat exhaustion likely. Heatstroke possible with prolonged exposure and/or physical activity |
| `extreme_danger` | Babban haɗari | Bugun zafi yana da matuƙar yiwuwa | Heat stroke highly likely |

## Other category names

| Key | Hausa | English |
|---|---|---|
| `below` | ƙasa da matakin 'A kula' | below Caution |
| `light` | kaɗan | light |
| `heavy` | mai yawa | heavy |
| `violent` | mai tsanani | violent |
| `none` | babu ruwan sama | no rain |
