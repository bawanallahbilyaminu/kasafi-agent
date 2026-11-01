# Generated coverage run

Cases: cases-836133.json (draw seed 836133), form seed 1

52 cases: wrong 1 (1.9%), of them wrong agency 0 | median 4.0s

| family | wrong | of |
|---|---|---|
| compare | 0 | 6 |
| false_premise | 0 | 6 |
| lookup | 0 | 6 |
| lookup_lga | 0 | 6 |
| not_in_data | 0 | 6 |
| rank_lga | 0 | 3 |
| share | 0 | 6 |
| spend_quarter | 1 | 6 |
| split | 0 | 6 |
| trend | 0 | 1 |

| form | wrong | of |
|---|---|---|
| code_switched | 0 | 11 |
| followup | 0 | 7 |
| hausa | 0 | 12 |
| informal | 0 | 4 |
| template | 0 | 10 |
| typo | 1 | 8 |

```
Cost of this run:
  Baseten: 28 calls, 260,786 prompt tokens (54,528 cached), 13,959 output tokens -> $0.33
  Meta: 128 calls, 415,123 prompt tokens (295,618 cached), 94,889 output tokens -> $0.60
  models together: $0.92 (prices per 1M tokens from settings kasafi_price_*)
  per answer (52 answers): $0.0133, 2.0 model calls
    Baseten/compose         0.27 calls  $0.0037  (27%)
    Meta/plan               1.00 calls  $0.0035  (26%)
    Meta/read1              0.29 calls  $0.0031  (23%)
    Baseten/read2           0.27 calls  $0.0026  (19%)
    Meta/completeness       0.17 calls  $0.0006  (4%)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0) | identical calls answered from the run's cache: 0
peak memory: 390 MB
```

## lookup-01 (code_switched) ok (5.7s)

**Q:** How much aka approve wa Economic Sector a 2025 budget?

```
An amince da jimilla ₦237.36 biliyan ga Economic Sector a kasafin 2025 da aka amince da shi. Wannan ƙididdiga ce ta jimillar kashewa (total expenditure) daga teburin Total Expenditure by Administrative Classification.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-02 (template) ok (9.0s)

**Q:** How much was approved for the Ministry for Local Government and Chieftancy in the 2025 budget?

```
The Ministry for Local Government and Chieftancy was approved ₦570.64 million in the 2025 budget (total allocation).

• 2025 approved budget (total): ₦570.64 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12
```

## lookup-03 (followup) ok (7.3s)

**Q:** How much was approved for it in the 2024 budget?

```
In the 2024 approved budget, ₦7.49 billion was approved for the State Judiciary (total expenditure).

• 2024 approved budget (total): ₦7.49 billion

📄 *Sources:* Sokoto State Government 2024 Approved Budget, p. 44
```

## lookup-04 (code_switched) ok (6.3s)

**Q:** Nawa aka approve wa Department of Establishment and Pensions a 2026 budget?

```
An amince da jimilla ta ₦11.84 biliyan ga Department of Establishment and Pensions a cikin kasafin kuɗi na 2026 da aka amince da shi. Wannan jimilla ce daga teburin jimillar kashe kuɗi na gwamnati (Total Expenditure) bisa ga rabe-raben gudanarwa.

• 2026 kasafin da aka amince (jimilla): ₦11.84 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16
```

## lookup-05 (hausa) ok (7.5s)

**Q:** Nawa aka amince wa Office of Auditor General a kasafin kudin 2026?

```
An amince wa Office of Auditor General jimillar ₦606.84 miliyan a kasafin kuɗin 2026 da aka amince wa. Wannan shi ne jimillar kasafin ma'aikatar gaba ɗaya (total) daga teburin Jimillar Kashewa ta Rarraba na Gudanarwa.

• 2026 kasafin da aka amince wa (jimilla): ₦606.84 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16
```

## lookup-06 (hausa) ok (6.5s)

**Q:** Nawa aka amince wa Ministry of Social Welfare & Community Development a kasafin kuɗin 2025?

```
A kasafin kuɗin 2025 da aka amince, jimillar kuɗin da aka ware wa Ministry of Social Welfare & Community Development ita ce ₦7.08 biliyan. Wannan ƙididdiga ce ta jimillar kashe kuɗi (total) daga [Table: Sokoto State Government 2025 Approved Budget - Total Expenditure by Administrative Classification].

• 2025 kasafin da aka amince (jimilla): ₦7.08 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12
```

## split-01 (typo) ok (3.5s)

**Q:** Waht are the personel, overhead and capital allocatons of the State Agency for Normadic Education1 in 2026?

```
For State Agency for Normadic Education, the approved budget (salaries) is ₦289.00 million.

*State Agency for Normadic Education*:
• Personnel (salaries): approved budget ₦289.00 million
• Overhead (running costs): approved budget ₦102.00 million
• Capital: approved budget ₦383.42 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 27
```

## split-02 (followup) ok (17.8s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
For College of Nursing Sciences, the approved budget (salaries) is ₦432.34 million.

*College of Nursing Sciences*:
• Personnel (salaries): approved budget ₦432.34 million
• Overhead (running costs): approved budget ₦16.00 million
• Capital: approved budget ₦615.00 million
Not in the documents:
• College of Nursing Sciences Personnel (salaries) 2025 revised budget: the budget prints no Personnel (salaries) line for it
• College of Nursing Sciences Overhead (running costs) 2025 revised budget: the budget prints no Overhead (running costs) line for it
• College of Nursing Sciences Capital 2025 revised budget: the budget prints no Capital line for it

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 17
```

## split-03 (template) ok (3.1s)

**Q:** What are the personnel, overhead and capital allocations of the ZAKAT and Endowment Agency (WAQF) in 2025?

```
For ZAKAT and Endowment Agency (WAQF), the approved budget (salaries) is ₦11.45 million.

*ZAKAT and Endowment Agency (WAQF)*:
• Personnel (salaries): approved budget ₦11.45 million
• Overhead (running costs): approved budget ₦874.90 million
• Capital: approved budget ₦610.20 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 14, 16
```

## split-04 (typo) ok (3.0s)

**Q:** What are the personnel, overhaed and capital allcations of teh College of Agriculture Wurno in 2026?

```
For College of Agriculture Wurno, the approved budget (salaries) is ₦195.08 million.

*College of Agriculture Wurno*:
• Personnel (salaries): approved budget ₦195.08 million
• Overhead (running costs): approved budget ₦156.00 million
• Capital: approved budget ₦929.70 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 22, 25
```

## split-05 (hausa) ok (18.7s)

**Q:** Nawa ne kudin personnel, overhead da capital da aka ware wa Ministry for Religious Affairs a 2025?

```
Ga Ministry for Religious Affairs, kasafin da aka amince (albashi) shi ne ₦117.15 miliyan.

*Ministry for Religious Affairs*:
• Albashi: kasafin da aka amince ₦117.15 miliyan; 1.0% na jimillarsa (lissafin Kasafi)
• Kuɗin gudanarwa: kasafin da aka amince ₦3.14 biliyan; 27.9% na jimillarsa (lissafin Kasafi)
• Manyan ayyuka: kasafin da aka amince ₦8.00 biliyan; 71.1% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦11.26 biliyan
Ba a cikin takardun ba:
• Ministry for Religious Affairs Albashi 2025 kasafin da aka sabunta: kasafin bai buga layin Albashi nasa ba
• Ministry for Religious Affairs Kuɗin gudanarwa 2025 kasafin da aka sabunta: kasafin bai buga layin Kuɗin gudanarwa nasa ba
• Ministry for Religious Affairs Manyan ayyuka 2025 kasafin da aka sabunta: kasafin bai buga layin Manyan ayyuka nasa ba
• Ministry for Religious Affairs 2025 kasafin da aka sabunta: kasafin bai buga layin Jimilla nasa ba

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 13, 14, 16
```

## split-06 (followup) ok (3.1s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
For Ministry of Justice, the approved budget (salaries) is ₦864.15 million.

*Ministry of Justice*:
• Personnel (salaries): approved budget ₦864.15 million
• Overhead (running costs): approved budget ₦1.52 billion
• Capital: approved budget ₦3.71 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 24, 26
```

## spend_quarter-01 (hausa) ok (3.1s)

**Q:** Nawa SSG'S Office ya kashe har zuwa ƙarshen Q2 2026, idan aka kwatanta da revised budget ɗinsa?

```
Ga Office of the SSG, kasafin da aka sabunta shi ne ₦39.40 biliyan.

*Office of the SSG*:
• Jimilla: kasafin da aka sabunta ₦39.40 biliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦5.71 biliyan; kason kasafin da aka sabunta da aka kashe 14.5% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 15
```

## spend_quarter-02 (template) ok (3.3s)

**Q:** How much had the SUSTAINABLE DEVELOPMENT GOALS (SDG) spent by the end of Q2 2026, against its revised budget?

```
For SUSTAINABLE DEVELOPMENT GOALS (SDG), the revised budget is ₦42.00 million.

*SUSTAINABLE DEVELOPMENT GOALS (SDG)*:
• Total: revised budget ₦42.00 million; spent so far (Q1–Q2) ₦1.00 million; share of the revised budget spent 2.4% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 17
```

## spend_quarter-03 (template) ok (3.3s)

**Q:** How much had the Office of the Deputy Governor spent by the end of Q2 2026, against its revised budget?

```
For Office of the Deputy Governor, the revised budget is ₦1.71 billion.

*Office of the Deputy Governor*:
• Total: revised budget ₦1.71 billion; spent so far (Q1–Q2) ₦519.95 million; share of the revised budget spent 30.4% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 15
```

## spend_quarter-04 (typo) WRONG: missing ['679,769,984.28'] (3.1s)

**Q:** How much had teh State Enviromental Protection Agency spent by the end of Q3 2025, agianst its revised budget?

```
For State Environmental Protection Agency, the spent so far (Q1–Q3) is ₦516.54 million.

*State Environmental Protection Agency*:
• Total: spent so far (Q1–Q3) ₦516.54 million; share of the revised budget spent 76.0% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 19
```

## spend_quarter-05 (code_switched) ok (4.2s)

**Q:** Ministry of Livestocks and Fisheries Development ta spend nawa by end of Q3 2025 against revised budget dinta?

```
Ga Ministry of Livestocks and Fisheries Development, abin da aka kashe zuwa yanzu (Q1–Q3) shi ne ₦2.95 biliyan.

*Ministry of Livestocks and Fisheries Development*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q3) ₦2.95 biliyan; kasafin da aka sabunta ₦6.29 biliyan; kason kasafin da aka sabunta da aka kashe 46.9% (lissafin Kasafi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 18
```

## spend_quarter-06 (hausa) ok (2.5s)

**Q:** Nawa Sokoto State Public Service Institute ta kashe har zuwa karshen Q3 2025, idan aka duba revised budget dinta?

```
Ga Sokoto State Public Service Institute, kasafin da aka sabunta shi ne ₦135.00 miliyan.

*Sokoto State Public Service Institute*:
• Jimilla: kasafin da aka sabunta ₦135.00 miliyan; abin da aka kashe zuwa yanzu (Q1–Q3) ₦0.00; kason kasafin da aka sabunta da aka kashe 0.0% (lissafin Kasafi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 16
```

## compare-01 (code_switched) ok (3.2s)

**Q:** Kwatanta Ministry of Finance approved budget na 2025 da 2026 fa?

```
Ga Ministry of Finance, 2025 kasafin da aka amince shi ne ₦47.75 biliyan.

*Ministry of Finance*:
• Jimilla: 2025 kasafin da aka amince ₦47.75 biliyan; 2026 kasafin da aka amince ₦40.27 biliyan; bambanci -₦7.47 biliyan (-15.7%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-02 (typo) ok (2.9s)

**Q:** Compare teh Local Goverment Service Commission's aproved budget in 2025 and 2026.

```
For Local Government Service Commission, the 2025 approved budget is ₦555.67 million.

*Local Government Service Commission*:
• Total: 2025 approved budget ₦555.67 million; 2026 approved budget ₦746.52 million; change +₦190.85 million (+34.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-03 (hausa) ok (4.8s)

**Q:** Kwatanta kasafin kuɗin Ministry of Water Resources da aka amince da shi a 2025 da 2026.

```
Ga Ministry of Water Resources, 2025 kasafin da aka amince shi ne ₦20.32 biliyan.

*Ministry of Water Resources*:
• Jimilla: 2025 kasafin da aka amince ₦20.32 biliyan; 2026 kasafin da aka amince ₦44.99 biliyan; bambanci +₦24.67 biliyan (+121.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-04 (hausa) ok (2.6s)

**Q:** Kwatanta budget ɗin da aka amince wa Ministry for Women Affairs a 2025 da 2026.

```
Ga Ministry for Women Affairs, 2025 kasafin da aka amince shi ne ₦8.44 biliyan.

*Ministry for Women Affairs*:
• Jimilla: 2025 kasafin da aka amince ₦8.44 biliyan; 2026 kasafin da aka amince ₦7.24 biliyan; bambanci -₦1.21 biliyan (-14.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-05 (template) ok (3.4s)

**Q:** Compare the Ministry for Local Government and Chieftancy's approved budget in 2025 and 2026.

```
For Ministry for Local Government and Chieftancy, the 2025 approved budget is ₦570.64 million.

*Ministry for Local Government and Chieftancy*:
• Total: 2025 approved budget ₦570.64 million; 2026 approved budget ₦1.36 billion; change +₦788.43 million (+138.2%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 19
```

## compare-06 (hausa) ok (3.2s)

**Q:** Kwatanta approved budget din Ministry of Innovation and Digital Economy a 2025 da 2026.

```
Ga Ministry of Innovation and Digital Economy, 2025 kasafin da aka amince shi ne ₦1.35 biliyan.

*Ministry of Innovation and Digital Economy*:
• Jimilla: 2025 kasafin da aka amince ₦1.35 biliyan; 2026 kasafin da aka amince ₦3.59 biliyan; bambanci +₦2.24 biliyan (+166.1%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## share-01 (code_switched) ok (3.2s)

**Q:** 2026 approved budget na Fertilizer and Agricultral Supplies Company, what share ne capital?

```
Ga Fertilizer and Agricultral Supplies Company, kasafin da aka amince (manyan ayyuka) shi ne ₦23.00 miliyan.

*Fertilizer and Agricultral Supplies Company*:
• Manyan ayyuka: kasafin da aka amince ₦23.00 miliyan; 20.1% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦114.67 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 25
```

## share-02 (hausa) ok (2.0s)

**Q:** Kashi nawa na kasafin kudin Water Board na 2026 da aka amince da shi na babban jari ne?

```
Ga Water Board, kasafin da aka amince (manyan ayyuka) shi ne ₦28.30 biliyan.

*Water Board*:
• Manyan ayyuka: kasafin da aka amince ₦28.30 biliyan; 91.3% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦30.98 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## share-03 (typo) ok (11.2s)

**Q:** What sahre of teh Orthopedic Hospital Wamakko's 2026 approved budget is capital?

```
Capital is ₦590.00 million out of the Hospital's total 2026 approved budget of ₦1.27 billion. That is 46.5% (Kasafi's calculation) capital, of the 2026 approved budget.

• Orthopedic Hospital Wamakko (capital), 2026 Approved Budget: ₦590.00 million ↑
• Orthopedic Hospital Wamakko, 2026 Approved Budget: ₦1.27 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 27
_Reply *show working* to see the rows and arithmetic._
```

## share-04 (informal) ok (3.3s)

**Q:** Of Tenancy Control and Safety of Person Agency's 2026 approved budget, how much is capital?

```
For Tenancy Control and Safety of Person Agency, the approved budget (capital) is ₦72.00 million.

*Tenancy Control and Safety of Person Agency*:
• Capital: approved budget ₦72.00 million; 47.1% of its total (Kasafi's calculation)
• Total: approved budget ₦153.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-05 (template) ok (3.2s)

**Q:** What share of the Ministry of Agriculture & Natural Resource's 2026 approved budget is capital?

```
For Ministry of Agriculture & Natural Resource, the approved budget (capital) is ₦14.93 billion.

*Ministry of Agriculture & Natural Resource*:
• Capital: approved budget ₦14.93 billion; 87.6% of its total (Kasafi's calculation)
• Total: approved budget ₦17.05 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 25
```

## share-06 (code_switched) ok (3.8s)

**Q:** Department for Rural Water approved budget na 2026 din, kashi nawa ne capital?

```
Ga Department for Rural Water, kasafin da aka amince (manyan ayyuka) shi ne ₦3.21 biliyan.

*Department for Rural Water*:
• Manyan ayyuka: kasafin da aka amince ₦3.21 biliyan; 88.9% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦3.62 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## false_premise-01 (informal) ok (18.4s)

**Q:** Why'd Fiscal Responsibility Commission's budget drop from 2025 to 2026?

```
The Fiscal Responsibility Commission's budget did not drop. Its total allocation rose from ₦58.99 million in the 2025 approved budget to ₦60.99 million in the 2026 approved budget, ₦2.00 million (Kasafi's calculation). The documents give no reason for a drop because there was no drop.

• Fiscal Responsibility Commission, 2025 Approved Budget: ₦58.99 million
• Fiscal Responsibility Commission, 2026 Approved Budget: ₦60.99 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-02 (typo) ok (22.4s)

**Q:** Why did the Offcie of Audtior General's approved budgte fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Office of Auditor General, the 2025 approved budget (salaries) is ₦267.84 million.

*Office of Auditor General*:
• Personnel (salaries): 2025 approved budget ₦267.84 million; 2026 approved budget ₦357.84 million; change +₦90.00 million (+33.6%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦275.00 million; 2026 approved budget ₦249.00 million; change -₦26.00 million (-9.5%) (Kasafi's calculation)
• Total: 2025 approved budget ₦542.84 million; 2026 approved budget ₦606.84 million; change +₦64.00 million (+11.8%) (Kasafi's calculation)
Not in the documents:
• Office of Auditor General Capital 2025 approved budget: the budget prints no Capital line for it
• Office of Auditor General Capital 2026 approved budget: the budget prints no Capital line for it

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 12, 14; Sokoto State FY 2026 Budget, p. 16, 19, 22
```

## false_premise-03 (informal) ok (21.0s)

**Q:** why did Ministry of Energy and Petroleum Resources's budget drop from 2025 to 2026?

```
_Assumption: compared approved budgets for 2025 and 2026._

The Ministry of Energy and Petroleum Resources's budget did not drop from 2025 to 2026. Its approved total rose from ₦10.30 billion in 2025 to ₦23.33 billion in 2026, a change of 126.6% (Kasafi's calculation). The documents do not publish reasons for budget changes, so why it changed is not found.

• Ministry of Energy and Petroleum Resources, 2025 Approved Budget: ₦10.30 billion
• Ministry of Energy and Petroleum Resources, 2026 Approved Budget: ₦23.33 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-04 (hausa) ok (3.4s)

**Q:** Me ya sa approved budget na Ministry for Home Affairs ya ragu daga 2025 zuwa 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
Ga Ministry for Home Affairs, 2025 kasafin da aka amince (albashi) shi ne ₦1.31 biliyan.

*Ministry for Home Affairs*:
• Albashi: 2025 kasafin da aka amince ₦1.31 biliyan; 2026 kasafin da aka amince ₦2.11 biliyan; bambanci +₦804.86 miliyan (+61.5%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦158.37 miliyan; 2026 kasafin da aka amince ₦1.42 biliyan; bambanci +₦1.26 biliyan (+794.2%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦638.86 miliyan; 2026 kasafin da aka amince ₦2.58 biliyan; bambanci +₦1.94 biliyan (+304.2%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦2.11 biliyan; 2026 kasafin da aka amince ₦6.11 biliyan; bambanci +₦4.01 biliyan (+190.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 13, 14, 16; Sokoto State FY 2026 Budget, shafi 16, 19, 22, 25
```

## false_premise-05 (followup) ok (3.0s)

**Q:** Why did its approved budget rise from 2025 to 2026?

```
It didn't rise: the approved budget fell from 2025 to 2026, so there is no rise to explain.
For Ministry of Environment, the 2025 approved budget is ₦24.52 billion.

*Ministry of Environment*:
• Total: 2025 approved budget ₦24.52 billion; 2026 approved budget ₦20.77 billion; change -₦3.75 billion (-15.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-06 (typo) ok (4.0s)

**Q:** Why did the Local Goverment Service Commision's approved budjet fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Local Government Service Commission, the 2025 approved budget is ₦555.67 million.

*Local Government Service Commission*:
• Total: 2025 approved budget ₦555.67 million; 2026 approved budget ₦746.52 million; change +₦190.85 million (+34.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## not_in_data-01 (code_switched) ok (3.8s)

**Q:** Nawa Social Cash Transfer Unit ta spend a Q1 2027?

```
Ba a cikin takardun ba:
• Social Cash Transfer Unit 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Social Cash Transfer Unit 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-02 (code_switched) ok (3.9s)

**Q:** Sokoto State Scholarship and Students Matters ta spend nawa for Q4 2026?

```
Ba a cikin takardun ba:
• Sokoto State Scholarship and Students Matters 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Sokoto State Scholarship and Students Matters 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-03 (followup) ok (4.0s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Department of Establishment and Pensions 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Department of Establishment and Pensions 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-04 (code_switched) ok (4.7s)

**Q:** Nawa Ministry of Environment ta spend a Q1 2027?

```
Ba a cikin takardun ba:
• Ministry of Environment 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Ministry of Environment 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Ministry of Environment 2027 kason kasafin da aka sabunta da aka kashe: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-05 (followup) ok (3.5s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• SUSTAINABLE DEVELOPMENT GOALS (SDG) 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• SUSTAINABLE DEVELOPMENT GOALS (SDG) 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• SUSTAINABLE DEVELOPMENT GOALS (SDG) 2027 share of the revised budget spent: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-06 (followup) ok (3.7s)

**Q:** And how much did it spend in Q1 2027?

```
Not in the documents:
• Drugs and Medical Supplies Mgt. Agency 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Drugs and Medical Supplies Mgt. Agency 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Drugs and Medical Supplies Mgt. Agency 2027 share of the revised budget spent: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## rank_lga-01 (code_switched) ok (5.8s)

**Q:** Wadanne 3 LGAs ne in Sokoto with the most IDPs?

```
Ta ƙaramar hukuma (22), mafi yawa:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-02 (informal) ok (3.9s)

**Q:** top 10 LGAs with most IDPs in Sokoto?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143
4. Tureta: 15,068
5. Shagari: 14,850
6. Isa: 14,047
7. Illela: 8,953
8. Gwadabawa: 8,406
9. Rabah: 8,277
10. Dange-Shuni: 4,615

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-03 (template) ok (4.0s)

**Q:** Which 5 LGAs in Sokoto have the most IDPs?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143
4. Tureta: 15,068
5. Shagari: 14,850

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-01 (template) ok (4.3s)

**Q:** How many IDPs are there in Kware LGA?

```
IOM DTM counts *1,039* IDPs in Kware (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (template) ok (4.4s)

**Q:** How many IDPs are there in Gwadabawa LGA?

```
IOM DTM counts *8,406* IDPs in Gwadabawa (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-03 (typo) ok (5.0s)

**Q:** How many IDPs aer there ni Binji LGA?

```
IOM DTM counts *619* IDPs in Binji (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-04 (hausa) ok (5.3s)

**Q:** IDPs nawa ne a Goronyo LGA?

```
IOM DTM ta ƙidaya *1,926* 'yan gudun hijira a Goronyo (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-05 (code_switched) ok (4.2s)

**Q:** How many IDPs ne a Illela LGA?

```
IOM DTM ta ƙidaya *8,953* 'yan gudun hijira a Illela (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-06 (hausa) ok (4.3s)

**Q:** IDPs guda nawa ne a Silame LGA?

```
IOM DTM ta ƙidaya *3,386* 'yan gudun hijira a Silame (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## trend-01 (template) ok (5.7s)

**Q:** How has the number of IDPs in Sokoto State changed over the last DTM rounds?

```
Sokoto State, by round:
• Round 18 (2025-10-31): 181,526
• Round 17 (2025-05-31): 88,562
• Round 16 (2024-11-30): 99,729
• Round 15 (2024-09-30): 96,232
• Round 14 (2024-04-30): 117,568
• Round 13 (2023-12-31): 94,729
• Round 12 (2023-10-31): 67,936
• Round 11 (2022-12-31): 65,393
• Round 10 (2022-10-31): 52,850
• Round 9 (2021-12-31): 72,106
• Round 8 (2021-09-30): 71,289
• Round 7 (2021-07-30): 113,186
• Round 6 (2021-02-01): 45,308
• Round 5 (2020-12-31): 90,804
• Round 4 (2020-08-30): 36,595
• Round 2 (2019-10-30): 43,976
• Round 1 (2019-08-30): 36,153

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```
