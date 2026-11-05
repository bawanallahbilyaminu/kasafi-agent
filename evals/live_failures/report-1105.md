> Run on 5 Nov 2026 with Muse Spark Open on Fireworks for every step, including compose, so times run longer than live, where compose is on Muse Spark. lf590's WRONG below is false: its check pattern was damaged (fixed in questions_checks.json), and the answer does print 2026. That leaves 6 of 16 wrong.

# Open-question run: questions.json

16 questions: partial 9, answered 4, not found 3 | wrong 7 of 16 checked (lfB, lfC, lfB_ha, lfSN_ha, lfSNB, lfSNB_ha, lf590) | median 98.4s

```
plan          n=14 median  11.4s    10% of all time
line_search   n= 1 median   2.4s     0% of all time
read          n= 1 median   8.7s     1% of all time
read1         n= 1 median   7.4s     0% of all time
read2         n= 1 median   8.7s     1% of all time
page_search   n=12 median   2.7s     2% of all time
compose       n=12 median  15.5s    14% of all time
answer        n=12 median  19.0s    18% of all time
row readings: 2 model calls for 1 questions (2 = no retry)
```

## lfA: partial (search, 88.3s)

**Q:** How many schools are in Dange Shuni

_A: got only 91 public primary (+ pre-primary) as 'Newest figure'. ASC 23-24: primary 91 + 28 (p31), JSS 18 + 17 (p44), SSS 8 + 11 (p53) = 173; pre-primary 20 + 28 (p26) counted with primary; IQS only statewide (p22)_

_Answer check: pass_

```
Dange Shuni had *117* public schools in 2023/24.

• public pre-primary and primary schools: 91 (page 31)
• public junior secondary schools: 18 (page 44)
• public senior secondary schools: 8 (page 53)

Not added (the census counts a private school at each level it offers):
• private schools with primary classes: 28 (page 31)
• private schools with junior secondary classes: 17 (page 44)
• private schools with senior secondary classes: 11 (page 53)

The 2023/24 school census prints Dange Shuni figures by school level.

📄 *Sources:* Sokoto State Annual School Census 23-24 Report, p. 19, 21, 31, 44, 53
_Reply *show working* to see the rows and arithmetic._
```

## lfB: partial WRONG: missing ['\\A[^\\n]*\\b117\\b', '\\b91\\b', '\\b18\\b', '(?i:IQS|Islamiyya|Qur.?anic)', '\\b123\\b'] (search, 110.1s)

**Q:** I mean all the total schools primary, senior secondary and junior secondary and IQS

_B: answered about the BUDGET for Dange Shuni_

_Answer check: revise (named_part_missing: IQS is named by the user but not in the answer (give its figure, or the higher level's figure with one line saying the documents have it only there, or say it isn't in the document) → no second answer ()_

```
• primary: 119 (page 31)
• junior secondary: 35 (page 44)
• senior secondary: 19 (page 53)

No total: primary, junior secondary, senior secondary could not be found in the cited row, so the parts aren't added up.

📄 *Sources:* Sokoto State Annual School Census 23-24 Report, p. 19, 22, 31, 53
```

## lfC: not found WRONG: missing ['\\A[^\\n]*\\b117\\b', '\\b91\\b', '\\b18\\b'] (search, 169.8s)

**Q:** Am talking about schools not budget

_C: '91 public primary schools… I didn't find this in the pages I read', with '0 figure(s) found' in show working_

_Answer check: skipped ()_

```
Looking this up took too long and I didn't finish. Please ask again in a little while.
```

## lfD: partial (search, 47.2s)

**Q:** Was Wamakko LGA affected by floods in 2025, according to NEMA?

_D: 'Yes, Sokoto State is listed…' then 'can't tell about Wamakko'. NEMA's 2025 reports never name Wamakko: 7 LGAs and 8 wards, 15,675 people (24 Sep sitrep p3)_

_Answer check: pass_

```
NEMA's 2025 flood reports give no figure for Wamakko LGA specifically. They do not name which LGAs in Sokoto were affected. For Sokoto State as a whole they list 1,916 affected persons in 3 LGAs as of 2 September 2025 and 15,675 affected persons in 7 LGAs as of 24 September 2025.

• Sokoto State as of 2 September 2025: 3 affected LGAs, 1,916 affected persons
• Sokoto State as of 24 September 2025: 7 affected LGAs, 15,675 affected persons
• Nigeria as of 12 September 2025: 25 States affected, 89 LGAs affected

📎 Related: NATIONAL EMERGENCY MANAGEMENT AGENCY: 2025 FLOOD DASHBOARD also covers this (flood impact, displacement and affected population, humanitarian needs).

📄 *Sources:* NATIONAL EMERGENCY MANAGEMENT AGENCY: 2025 FLOOD DASHBOARD, p. 1; 2025 FLOOD DATA: IMPACT SEGREGATION BY LOCAL GOVERNMENT AREAS, p. 1; 2025 Floods National Emergency Operations Center (NEOC) National Secretariat Situation Report: as of 2nd September 2025, p. 2; 2025 Floods National Emergency Operations Center (NEOC) National Secretariat Situation Report: as of 26th September 2025, p. 3
```

## lfD_ha: partial (search, 31.7s)

**Q:** Shin ambaliya ta shafi Ƙaramar Hukumar Wamakko a 2025, a cewar NEMA?

_D in Hausa_

_Answer check: pass_

```
Takardun NEMA da aka bayar ba su bayar da adadi ga Ƙaramar Hukumar Wamakko ba. Sun bayar da adadi ga Jihar Sokoto gaba ɗaya: a ranar 2 ga Satumba 2025 LGAs 3 da mutane 1,916 da suka shafa, a ranar 24 ga Satumba 2025 LGAs 7 da mutane 15,675 da suka shafa. Ba a ambaci sunayen ƙananan hukumomin ba, don haka ba za a iya tabbatar da ko Wamakko tana ciki ba daga waɗannan takardun.

• Jihar Sokoto — 2 ga Satumba 2025: LGAs da abin ya shafa 3, mutane da abin ya shafa 1,916, mutane da suka rasa matsuguni 626, gidaje da abin ya shafa 175
• Jihar Sokoto — 24 ga Satumba 2025: LGAs da abin ya shafa 7, mutane da abin ya shafa 15,675, mutane da suka rasa matsuguni 4,566, gidaje da abin ya shafa 1,161
• Nigeriya — 12 ga Satumba 2025: mutane da abin ya shafa 325,321 a jihohi 25 da LGAs 89

📄 *Madogara:* NATIONAL EMERGENCY MANAGEMENT AGENCY: 2025 FLOOD DASHBOARD, shafi 1; 2025 Floods National Emergency Operations Center (NEOC) National Secretariat Situation Report: as of 2nd September 2025, shafi 2; 2025 Floods National Emergency Operations Center (NEOC) National Secretariat Situation Report: as of 26th September 2025, shafi 3
```

## lfE: answered (search, 49.9s)

**Q:** How many people in Sokoto State were affected by floods in October 2024?

_E: satellite hectares. NEMA: 102K (14 and 21 Oct), 97,928 (2 Oct)_

_Answer check: pass_

```
In October 2024, Sokoto State was listed as one of the most affected states. The NEOC dashboard printed Sokoto: 102K persons affected as of 21 October 2024 and as of 14 October 2024, and 97,928 persons affected as of 1 October 2024.

• Sokoto: 102K persons affected as of 21 October 2024 (printed on page)
• Sokoto: 102K persons affected as of 14 October 2024 (printed on page)
• Sokoto: 97,928 persons affected as of 1 October 2024 (printed on page)

📄 *Sources:* 2024 Floods National Emergency Operations Center (NEOC) National Secretariat Situation Report: No.4 (as of 22nd October, 2024), p. 2; 2024 Floods National Emergency Operations Center (NEOC) National Secretariat Situation Report: No.3 (as of 12th October, 2024), p. 2; 2024 Floods National Emergency Operations Center (NEOC) National Secretariat Situation Report: No.2 (as of 2ND October, 2024), p. 2
```

## lfE2: answered (search, 56.2s)

**Q:** I asked about people, not hectares of land

_E as a correction_

_Answer check: pass_

```
NEMA's 2024 flood reports give Sokoto State figures by date in October 2024. As of 14 October 2024 the dashboard printed Sokoto: 102K persons affected, and as of 21 October 2024 it also printed 102K. As of 2 October 2024 it printed 97,928 affected persons.

• As of 14 October 2024 (printed on dashboard): 102K - Sokoto affected persons
• As of 21 October 2024 (printed on dashboard): 102K - Sokoto affected persons
• As of 2 October 2024: 97,928 - Sokoto affected persons

📄 *Sources:* 2024 Floods National Emergency Operations Center (NEOC) National Secretariat Situation Report: No.3 (as of 12th October, 2024), p. 2; 2024 Floods National Emergency Operations Center (NEOC) National Secretariat Situation Report: No.2 (as of 2ND October, 2024), p. 2; 2024 Floods National Emergency Operations Center (NEOC) National Secretariat Situation Report: No.4 (as of 22nd October, 2024), p. 2
```

## lfA_ha: partial (search, 92.0s)

**Q:** Makarantu nawa ne a Dange Shuni?

_A in Hausa_

_Answer check: pass_

```
Dange Shuni na da makarantu *117* na gwamnati a 2023/24 idan aka haɗa firamare/pre-primary, JSS da SSS.

• makarantun gwamnati na firamare da pre-primary (makaranta ɗaya): 91 (shafi 19)
• makarantun gwamnati na ƙaramar sakandare (JSS) kaɗai: 18 (shafi 44)
• makarantun gwamnati na babbar sakandare (SSS) kaɗai: 8 (shafi 53)

Har ila yau akwai makarantun masu zaman kansu masu bayar da kowane mataki: 28 masu ajin pre-primary, 28 masu ajin firamare, 17 masu ajin JSS da 11 masu ajin SSS; waɗannan ƙididdigar masu zaman kansu na iya ƙidaya makaranta ɗaya sau da yawa idan tana bayar da matakai da yawa. Takardun binciken ba su wallafa jimillar makarantu na Dange Shuni a matsayin lamba guda ba.

• Makarantun masu zaman kansu masu ajin JSS a Dange Shuni: 17
• Makarantun masu zaman kansu masu ajin SSS a Dange Shuni: 11

📄 *Madogara:* Sokoto State Annual School Census 23-24 Report, shafi 19, 26, 31, 44, 53
_Ku rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## lfB_ha: partial WRONG: missing ['(?i:IQS|Islamiyya)', '\\b123\\b'] (search, 104.8s)

**Q:** Ina nufin duka makarantun: firamare, ƙaramar sakandare, babbar sakandare da IQS

_B in Hausa: IQS only statewide (123 primary, p22), said in one line_

_Answer check: revise (IQS schools a Dange Shuni; named_part_missing: IQS is named by the user but not in the answer (give its figure, or the higher level's figure with one line saying the documents have it only there, or s) → fail (named_part_missing: IQS is named by the user but not in the answer (give its figure, or the higher level's figure with one line saying the documents have it only there, or say it isn't in the document)_

```
Ƙaramar Hukumar Dange Shuni tana da makarantun gwamnati *117* a 2023/24.

• firamare: 91 (shafi 19)
• ƙaramar sakandare: 18 (shafi 44)
• babbar sakandare: 8 (shafi 53)

Wannan ya haɗa da firamare 91, ƙaramar sakandare 18 da babbar sakandare 8.

_Ban ga shekara ba, don haka na yi amfani da Ƙidayar Makarantu ta 2023/24 mafi sabo._

📄 *Madogara:* Sokoto State Annual School Census 23-24 Report, shafi 19, 22, 31, 44
```

## lfSN: partial (search, 65.5s)

**Q:** How many schools are in Sokoto North

_Live after the 3 Nov deploy: the main answer listed only private JSS 8 and SSS 6; the total was in show working. ASC: public 23 (p31) + 23 (p44) + 14 (p53) = 60; private 14, 8, 6 not added_

_Answer check: pass_

```
Sokoto North had *60* public schools in 2023/24.

• public Pre-Primary and Primary schools: 23 (page 19)
• public Junior Secondary schools: 23 (page 44)
• public Senior Secondary schools: 14 (page 53)

Not added (the census counts a private school at each level it offers):
• private primary schools (also counted at JSS/SSS if school offers multiple level: 14 (page 31)
• private Junior Secondary schools (also counted at other levels): 8 (page 44)
• private Senior Secondary schools (also counted at other levels): 6 (page 53)

📄 *Sources:* Sokoto State Annual School Census 23-24 Report, p. 19, 31, 44, 53
_Reply *show working* to see the rows and arithmetic._
```

## lfSN_ha: not found WRONG: missing ['\\A[^\\n]*\\b60\\b', '\\b23\\b', '\\b14\\b'] (search, 169.3s)

**Q:** Makarantu nawa ne a Sokoto North?

_Sokoto North in Hausa_

_Answer check: skipped ()_

```
Na ɗauki lokaci mai tsawo ina nema ban gama ba. Don Allah a sake tambaya nan gaba kaɗan.
```

## lfSNB: partial WRONG: missing ['(?i:IQS|Islamiyya)', '\\b123\\b'] (search, 110.2s)

**Q:** I mean all the schools, primary, junior secondary, senior secondary and IQS

_The check stopped an invented IQS figure for Sokoto North: the census has IQS only for the whole state (123 primary, p22)_

_Answer check: revise (named_part_missing: IQS is named by the user but not in the answer (give its figure, or the higher level's figure with one line saying the documents have it only there, or say it isn't in the document) → no second answer ()_

```
Sokoto North had *60* public schools in 2023/24.

• primary: 23 (page 19)
• junior secondary: 23 (page 44)
• senior secondary: 14 (page 53)

📄 *Sources:* Sokoto State Annual School Census 23-24 Report, p. 19, 22, 44, 53
```

## lfSNB_ha: partial WRONG: missing ['(?i:IQS|Islamiyya)', '\\b123\\b'] (search, 116.5s)

**Q:** Ina nufin duka makarantun: firamare, ƙaramar sakandare, babbar sakandare da IQS

_The same in Hausa_

_Answer check: revise (IQS schools in Sokoto North 2023/24; named_part_missing: IQS is named by the user but not in the answer (give its figure, or the higher level's figure with one line saying the documents have it only t) → no second answer ()_

```
Sokoto North tana da makarantun gwamnati *60* a 2023/24.

• primary: 23 (shafi 19)
• JSS: 23 (shafi 44)
• SSS: 14 (shafi 53)

📄 *Madogara:* Sokoto State Annual School Census 23-24 Report, shafi 19, 22, 31, 44, 53
```

## lfPHC: answered (search, 171.4s)

**Q:** What is the state of PHCs in sokoto state?

_4 Nov live: a deep analysis read 11 budgets and statements and lost the PHC MSP 2020, the EmONC assessment, the health AOP and ROP (Fireworks readers timed out and were dropped in silence), then said 'Not found: number of PHC facilities, staff by cadre, immunisation coverage'; it also gave 934 registry facilities of all types as PHCs. Expected: the sector's own documents read first (MSP, EmONC), unread sources said, registry counts primary-level only._

_Answer check: pass_

```
Sokoto State had 894 primary-level facilities in the registry in 2024 (GRID3/NHFR registry, Nov 2024) and 586 functional facilities across four zones (EmONC, 2026, p. 37), while the 2020 minimum standard assessment found 207 of 379 available facilities required upgrade and 26 new facilities needed to be built to meet the standard (MSP, 2020, p. 7).
Against the same standard, 78 nurse/midwives were available compared with 244 required (MSP, 2020, p. 6), and 46 medical officers were required, within a total of 3,395 frontline staff available.
The Primary Health Care Development Agency's approved budget was ₦7.12 billion in 2026 (FY 2026 Budget, p. 18), representing 5.9% of the health allocation that year (FY 2026 Budget, p. 32), down from 26.6% in 2025 to 5.9% in 2026 (FY 2026 Budget, p. 27; 2025 Approved Budget, p. 19; FY 2026 Budget, p. 32) on a calculated basis; actual spending was 78.1% of its final budget in 2023 (2025 Approved Budget, p. 12), 40.0% in 2024 (Budget Performance Q4 2024, p. 20), 11.3% in 2025 (Budget Implementation Q4 2025, p. 19) and 22.4% spent so far in Q1-Q3 2026 (BIQ 2026, p. 18).
Service coverage in 2024 was 26.4% of women receiving antenatal care from skilled providers and fewer than 13% delivering in facilities or with skilled attendants, with 2021 figures of 30.5% for skilled antenatal coverage (MTSS, 2025, p. 18), 14% delivering in facilities and 11% of children 12-23 months fully immunized.
The 2025 Safe Deliveries Initiative targets equipping and staffing 92 primary healthcare facilities across all 23 LGAs.
```

## lf586: not found (search, 114.7s)

**Q:** How much was released for MNCH from the local government budget in Sokoto State?

_5 Nov live, trace 586 (a real tester): 'No line in the documents is exactly that…' with three state lines at 0.00 (BIR Q3 2025 and the 2026 budget), no word that only state documents are held, the planned health AOP / MTSS / ROP unread, the check skipped on a 30 s timeout. Expected: the lead says the library has no LGA budgets, only the state's; never a list of 0.00 nearest lines; the state documents' own MNCH figures offered as the state's (MTSS p. 12: Free Maternal and Child Healthcare (MNCH+N) 960,000,000)._

_Answer check: revise (amount released for MNCH from local government budget) → no second answer ()_

```
I don't have Sokoto's local government (LGA) budgets, only the state budget and its reports, and the state documents I read don't give a figure for this.
```

## lf590: answered WRONG: missing ['\x082026\x08'] (search, 66.8s)

**Q:** Tell me about the Ministry of Innovation and Digital Economy in Sokoto State

_5 Nov live, trace 590 (a real tester): a deep analysis of 17 documents covered 2024 only; its 17 figures were on their cited pages but the code check counted 0 of 17 (house-style amounts), the check said revise, no second round ran and the brief was cut to one sentence. Expected: the structured budget core first (the 2026 approved total with personnel, overhead and capital, spending so far, 2025), then what the documents add; never 2024 only._

_Answer check: revise (work or mandate of the Ministry) → pass_

```
For Ministry of Innovation and Digital Economy, the approved budget (salaries) is ₦60.01 million.

*Ministry of Innovation and Digital Economy*:
• Personnel (salaries): approved budget ₦60.01 million; spent so far (Q1–Q3) ₦47.28 million; share of the revised budget spent 45.0% (Kasafi's calculation)
• Overhead (running costs): approved budget ₦778.47 million; spent so far (Q1–Q3) ₦62.04 million; share of the revised budget spent 7.5% (Kasafi's calculation)
• Capital: approved budget ₦2.75 billion; spent so far (Q1–Q3) ₦105.82 million; share of the revised budget spent 3.8% (Kasafi's calculation)
• Total: approved budget ₦3.59 billion; spent so far (Q1–Q3) ₦215.14 million; share of the revised budget spent 5.8% (Kasafi's calculation)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 20, 23, 26; Budget Implementation Report - 2026 Quarter 3, p. 16, 20, 23, 27
```
