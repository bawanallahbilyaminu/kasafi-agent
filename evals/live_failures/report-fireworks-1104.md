> Run on 4 Nov 2026 (the `multi-part` branch, before its merge) with Muse Spark Open on Fireworks: Baseten had started returning 402 that day and the calls fell through to Fireworks, where answers took 2-3 times longer (median 57 s) and several hit the answer loop's limit. Four of the six misses (lfB, lfC, lfE, lfE2) failed the same way with the multi-part switch off, so they are host latency, not that change. The same set scored 11/13 on 3 Nov (`report.md`) and 11-13/13 over three overnight runs (`docs/overnight-report.md`).

# Open-question run: questions.json

13 questions: partial 8, not found 3, answered 2 | wrong 6 of 13 checked (lfB, lfC, lfD, lfE, lfE2, lfSNB_ha) | median 57.0s

```
plan          n=13 median   6.8s    11% of all time
page_search   n=11 median   1.3s     2% of all time
compose       n=11 median  31.3s    36% of all time
answer        n=11 median  31.4s    39% of all time
```

## lfA: partial (search, 51.7s)

**Q:** How many schools are in Dange Shuni

_A: got only 91 public primary (+ pre-primary) as 'Newest figure'. ASC 23-24: primary 91 + 28 (p31), JSS 18 + 17 (p44), SSS 8 + 11 (p53) = 173; pre-primary 20 + 28 (p26) counted with primary; IQS only statewide (p22)_

_Answer check: pass_

```
Dange Shuni had *117* public schools in 2023/24 across the three levels counted as separate schools.

• public pre-primary and primary schools in Dange Shuni: 91 (page 19)
• public junior secondary schools in Dange Shuni: 18 (page 44)
• public senior secondary schools in Dange Shuni: 8 (page 53)

Not added (the census counts a private school at each level it offers):
• private schools with primary classes in Dange Shuni: 28 (page 31)
• private schools with junior secondary classes in Dange Shuni: 17 (page 44)
• private schools with senior secondary classes in Dange Shuni: 11 (page 53)

Sokoto State Annual School Census 2023/24 gives separate figures for Dange Shuni by level and ownership.

📄 *Sources:* Sokoto State Annual School Census 23-24 Report, p. 19, 21, 26, 31, 44, 53
_Reply *show working* to see the rows and arithmetic._
```

## lfB: partial WRONG: missing ['\\b123\\b'] (search, 83.0s)

**Q:** I mean all the total schools primary, senior secondary and junior secondary and IQS

_B: answered about the BUDGET for Dange Shuni_

_Answer check: revise (private primary schools in Dange Shuni LGA, 2023/2024 (if applicable); private junior secondary schools in Dange Shuni LGA, 2023/2024) → revise ()_

```
Dange Shuni LGA had *117* public and private primary, junior secondary and senior secondary schools in 2023/24.

• public primary schools (public Pre-Primary and Primary) in Dange Shuni LGA: 91 (page 19)
• public junior secondary schools in Dange Shuni LGA: 18 (page 44)
• public senior secondary schools in Dange Shuni LGA: 8 (page 53)

Not added (the census counts a private school at each level it offers):
• private primary schools in Dange Shuni LGA: 28 (page 31)
• private junior secondary schools in Dange Shuni LGA: 17 (page 44)
• private senior secondary schools in Dange Shuni LGA: 11 (page 53)

Evidence prints Dange Shuni's schools by level for 2023/24. It gives the public total for each level. For IQS the report gives only a state total, not an LGA figure, so no Dange Shuni IQS number is published in these documents.

📄 *Sources:* Sokoto State Annual School Census 23-24 Report, p. 19, 22, 31, 44, 53
```

## lfC: partial WRONG: missing ['\\A[^\\n]*\\b117\\b', '\\b91\\b', '\\b18\\b'] (search, 85.7s)

**Q:** Am talking about schools not budget

_C: '91 public primary schools… I didn't find this in the pages I read', with '0 figure(s) found' in show working_

_Answer check: revise (public primary schools in Dange Shuni LGA (2023/24); private primary schools in Dange Shuni LGA (2023/24) where counted separately; junior secondary schools in Dange Shuni LGA (2023/24) - public; juni) → fail (number of primary schools in Dange Shuni LGA in 2023/24; number of junior secondary schools in Dange Shuni LGA in 2023/24; number of IQS schools in Dange Shuni LGA in 2023/24)_

```
Dange Shuni LGA had *19* senior secondary schools in 2023/24.

• public senior secondary schools in Dange Shuni LGA: 8 (page 53)
• private senior secondary schools in Dange Shuni LGA: 11 (page 53)

⚠️ Not found as written in the cited pages: IQS. Check these names against the source.

📄 *Sources:* Sokoto State Annual School Census 23-24 Report, p. 53
```

## lfD: not found WRONG: missing ['15,675|\\b7\\b'] (search, 83.5s)

**Q:** Was Wamakko LGA affected by floods in 2025, according to NEMA?

_D: 'Yes, Sokoto State is listed…' then 'can't tell about Wamakko'. NEMA's 2025 reports never name Wamakko: 7 LGAs and 8 wards, 15,675 people (24 Sep sitrep p3)_

_Answer check: revise (Whether Wamakko LGA in Sokoto State was listed as affected by floods in 2025 according to NEMA (yes/no and any NEMA figures for Wamakko LGA)) → fail (Whether Wamakko LGA was listed as an affected LGA in Sokoto State in 2025 according to NEMA's LGA segregation table, and if so the 2025 figures for Wamakko LGA: affected persons, displaced persons, ho)_

```
I couldn't give a checked answer to that: Whether Wamakko LGA was listed as an affected LGA in Sokoto State in according to NEMA's LGA segregation table, and if so the figures for Wamakko LGA: affected persons, displaced persons, houses and farmlands affected. The documents I read were 2025 FLOOD DATA: IMPACT SEGREGATION BY LOCAL GOVERNMENT AREAS; 2025 Floods National Emergency Operations Center (NEOC) National Secretariat Situation Report: as of 26th September 2025; 2025 Floods National Emergency Operations Center (NEOC) National Secretariat Situation Report: as of 2nd September 2025.
```

## lfD_ha: partial (search, 34.2s)

**Q:** Shin ambaliya ta shafi Ƙaramar Hukumar Wamakko a 2025, a cewar NEMA?

_D in Hausa_

_Answer check: pass_

```
Takardun NEMA da aka bayar ba su rubuta sunan Ƙaramar Hukumar Wamakko ba a matsayin wadda ambaliya ta shafa a 2025. Abin da takardun ke bayarwa shi ne na Jihar Sokoto gabadaya: a ranar 2 ga Satumba 2025 ƙananan hukumomi 3 ne aka ce ambaliya ta shafa, mutane 1,916 ne aka ce abin ya shafa, sai a ranar 24 ga Satumba 2025 ƙananan hukumomi 7, mutane 15,675. Jerin ƙananan hukumomi 30 da suka fi shafa da aka buga har 12 ga Satumba 2025 bai haɗa da Wamakko ba.

• Jihar Sokoto a 2 ga Satumba 2025: ƙananan hukumomi 3 da aka shafa, mutane 1,916 da aka shafa
• Jihar Sokoto a 24 ga Satumba 2025: ƙananan hukumomi 7 da aka shafa, mutane 15,675 da aka shafa

📄 *Madogara:* NATIONAL EMERGENCY MANAGEMENT AGENCY: 2025 FLOOD DASHBOARD, shafi 1, 2; 2025 FLOOD DATA: IMPACT SEGREGATION BY LOCAL GOVERNMENT AREAS, shafi 1; 2025 Floods National Emergency Operations Center (NEOC) National Secretariat Situation Report: as of 2nd September 2025, shafi 2; 2025 Floods National Emergency Operations Center (NEOC) National Secretariat Situation Report: as of 26th September 2025, shafi 3
```

## lfE: not found WRONG: missing ['102K|102,000|97,928'] (search, 28.8s)

**Q:** How many people in Sokoto State were affected by floods in October 2024?

_E: satellite hectares. NEMA: 102K (14 and 21 Oct), 97,928 (2 Oct)_

_Answer check: revise (Number of people in Sokoto State affected by floods in October 2024) → fail (people affected by floods in Sokoto State in October 2024 - number of people)_

```
I couldn't give a checked answer to that: people affected by floods in Sokoto State in October - number of people.
```

## lfE2: not found WRONG: missing ['102K|102,000|97,928|98K'] (search, 37.6s)

**Q:** I asked about people, not hectares of land

_E as a correction_

_Answer check: revise (number of people affected by floods in Sokoto State in 2024 - no figure given and no statement that sources lack it) → fail (people affected by floods in Sokoto State in 2024 (number of people))_

```
I couldn't give a checked answer to that: people affected by floods in Sokoto State in (number of people).
```

## lfA_ha: answered (search, 56.1s)

**Q:** Makarantu nawa ne a Dange Shuni?

_A in Hausa_

_Answer check: pass_

```
Dange Shuni tana da *117* makarantun gwamnati a 2023/24.

• makarantun firamare na gwamnati (haɗe da masu koyar da pre-primary): 91 (shafi 31)
• makarantun ƙaramar sakandare (JSS) na gwamnati: 18 (shafi 44)
• makarantun babbar sakandare (SSS) na gwamnati: 8 (shafi 53)

Ba a haɗa ba (ƙidayar tana ƙidaya makarantar mai zaman kanta a kowane mataki da take da shi):
• makarantun masu zaman kansu masu ajin firamare: 28 (shafi 31)
• makarantun masu zaman kansu masu ajin ƙaramar sakandare: 17 (shafi 44)
• makarantun masu zaman kansu masu ajin babbar sakandare: 11 (shafi 53)

A ƙidayar makarantun 2023/24, Dange Shuni tana da makarantun gwamnati 117 da aka ƙirga daban-daban: firamare 91, ƙaramar sakandare 18 da babbar sakandare 8.

📄 *Madogara:* Sokoto State Annual School Census 23-24 Report, shafi 21, 26, 31, 44, 53, 89
_Ku rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## lfB_ha: partial (search, 54.7s)

**Q:** Ina nufin duka makarantun: firamare, ƙaramar sakandare, babbar sakandare da IQS

_B in Hausa: IQS only statewide (123 primary, p22), said in one line_

_Answer check: pass_

```
Ƙaramar Hukumar Dange Shuni tana da *117* makarantun gwamnati a 2023/24

• makarantun firamare na gwamnati a Dange Shuni: 91 (shafi 31)
• makarantun ƙaramar sakandare na gwamnati a Dange Shuni: 18 (shafi 44)
• makarantun babbar sakandare na gwamnati a Dange Shuni: 8 (shafi 53)

Takardun da aka bayar ba su raba makarantun IQS (Islamiyya Integrated) bisa ƙaramar hukuma ba; sun bayar da jimillar jiha ne kawai: makarantun Islamiyya Integrated na firamare 123 a faɗin Jihar Sokoto.

• jimillar gwamnati a Dange Shuni: 117 (firarmare 91, ƙaramar sakandare 18, babbar sakandare 8)
• IQS na jihar Sokoto: 123 (Islamiyya Integrated na firamare) - ba a buga na Dange Shuni ba

📄 *Madogara:* Sokoto State Annual School Census 23-24 Report, shafi 22, 31, 44, 53, 89
_Ku rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## lfSN: partial (search, 58.1s)

**Q:** How many schools are in Sokoto North

_Live after the 3 Nov deploy: the main answer listed only private JSS 8 and SSS 6; the total was in show working. ASC: public 23 (p31) + 23 (p44) + 14 (p53) = 60; private 14, 8, 6 not added_

_Answer check: pass_

```
Sokoto North had *60* public schools in 2023/24 across the three levels shown.

• public primary schools (including pre-primary) in Sokoto North: 23 (page 31)
• public junior secondary schools in Sokoto North: 23 (page 44)
• public senior secondary schools in Sokoto North: 14 (page 53)

Not added (the census counts a private school at each level it offers):
• private primary schools in Sokoto North: 14 (page 31)
• private junior secondary schools in Sokoto North: 8 (page 44)
• private senior secondary schools in Sokoto North: 6 (page 53)

The 2023/24 Sokoto State Annual School Census gives school numbers by LGA and level for 2023/24. The figures below are the numbers it prints for Sokoto North for each level and ownership.

• Pre-primary and primary are counted together as public "Pre-Primary and Primary" schools in the census totals

📄 *Sources:* Sokoto State Annual School Census 23-24 Report, p. 19, 21, 31, 44, 53
_Reply *show working* to see the rows and arithmetic._
```

## lfSN_ha: answered (search, 65.7s)

**Q:** Makarantu nawa ne a Sokoto North?

_Sokoto North in Hausa_

_Answer check: pass_

```
Sokoto North na da *60* makarantun gwamnati a 2023/24 (Pre-Primary da Primary, JSS da SSS tare)

• makarantun gwamnati na Pre-Primary da Primary (ana ƙirgawa tare): 23 (shafi 31)
• makarantun gwamnati na Junior Secondary (JSS): 23 (shafi 44)
• makarantun gwamnati na Senior Secondary (SSS): 14 (shafi 53)

Ba a haɗa ba (ƙidayar tana ƙidaya makarantar mai zaman kanta a kowane mataki da take da shi):
• makarantun masu zaman kansu na Primary: 14 (shafi 31)
• makarantun masu zaman kansu na Junior Secondary (JSS): 8 (shafi 44)
• makarantun masu zaman kansu na Senior Secondary (SSS): 6 (shafi 53)

A cikin rahoton Ƙididdigar Makarantu ta Shekara ta 2023/24, an rarraba makarantun Sokoto North gwargwadon mataki da mallaka.

📄 *Madogara:* Sokoto State Annual School Census 23-24 Report, shafi 31, 44, 53
_Ku rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## lfSNB: partial (search, 61.3s)

**Q:** I mean all the schools, primary, junior secondary, senior secondary and IQS

_The check stopped an invented IQS figure for Sokoto North: the census has IQS only for the whole state (123 primary, p22)_

_Answer check: pass_

```
Sokoto North had *60* public schools in 2023/24.

• public primary schools in Sokoto North (2023/24): 23 (page 19)
• public junior secondary schools in Sokoto North (2023/24): 23 (page 44)
• public senior secondary schools in Sokoto North (2023/24): 14 (page 53)

Not added (the census counts a private school at each level it offers):
• private schools with primary classes in Sokoto North (2023/24): 14 (page 31)
• private schools with junior secondary classes in Sokoto North (2023/24): 8 (page 44)
• private schools with senior secondary classes in Sokoto North (2023/24): 6 (page 53)

The census gives Islamiyya Integrated (IQS) schools only for the whole state, not by LGA: 123 primary IQS schools, 6 junior secondary IQS schools and 6 Science & Technical IQS schools.

📄 *Sources:* Sokoto State Annual School Census 23-24 Report, p. 19, 22, 31, 44, 53
_Reply *show working* to see the rows and arithmetic._
```

## lfSNB_ha: partial WRONG: missing ['(?i:IQS|Islamiyya)', '\\b123\\b'] (search, 57.0s)

**Q:** Ina nufin duka makarantun: firamare, ƙaramar sakandare, babbar sakandare da IQS

_The same in Hausa_

_Answer check: pass_

```
Sokoto North tana da makarantun gwamnati *60* a 2023/24.

• makarantun firamare na gwamnati a Sokoto North: 23 (shafi 31)
• makarantun ƙaramar sakandare (JSS) na gwamnati a Sokoto North: 23 (shafi 44)
• makarantun babbar sakandare (SSS) na gwamnati a Sokoto North: 14 (shafi 53)

Ba a haɗa ba (ƙidayar tana ƙidaya makarantar mai zaman kanta a kowane mataki da take da shi):
• makarantun firamare masu zaman kansu a Sokoto North – suna da azuzuwan firamare: 14 (shafi 31)
• makarantun ƙaramar sakandare masu zaman kansu a Sokoto North – suna da azuzuwan: 8 (shafi 44)
• makarantun babbar sakandare masu zaman kansu a Sokoto North – suna da azuzuwan S: 6 (shafi 53)

Sokoto North tana da makarantun gwamnati 60 a rahoton ƙidayar makarantu na 2023/24: firamare 23, ƙaramar sakandare 23, babbar sakandare 14.

📄 *Madogara:* Sokoto State Annual School Census 23-24 Report, shafi 19, 22, 31, 44, 53
_Ku rubuta *nuna lissafi* don ganin layukan da lissafin._
```
