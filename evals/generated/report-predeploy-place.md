# Generated coverage run

Cases: cases-657824.json (draw seed 657824), form seed 1

52 cases: wrong 10 (19.2%), of them wrong agency 0 | median 4.1s

| family | wrong | of |
|---|---|---|
| compare | 0 | 6 |
| false_premise | 1 | 6 |
| lookup | 0 | 6 |
| lookup_lga | 5 | 6 |
| not_in_data | 0 | 6 |
| rank_lga | 3 | 3 |
| share | 0 | 6 |
| spend_quarter | 0 | 6 |
| split | 1 | 6 |
| trend | 0 | 1 |

| form | wrong | of |
|---|---|---|
| code_switched | 2 | 11 |
| followup | 1 | 7 |
| hausa | 3 | 12 |
| informal | 1 | 4 |
| template | 2 | 10 |
| typo | 1 | 8 |

```
Cost of this run:
  Baseten: 22 calls, 184,404 prompt tokens (50,944 cached), 11,773 output tokens -> $0.22
  Meta: 123 calls, 422,445 prompt tokens (292,409 cached), 90,121 output tokens -> $0.59
  models together: $0.81 (prices per 1M tokens from settings kasafi_price_*)
  per answer (52 answers): $0.0114, 1.8 model calls
    Meta/plan               1.00 calls  $0.0038  (33%)
    Meta/read1              0.31 calls  $0.0032  (28%)
    Baseten/compose         0.23 calls  $0.0024  (21%)
    Baseten/read2           0.19 calls  $0.0019  (17%)
    Meta/completeness       0.06 calls  $0.0002  (1%)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0) | identical calls answered from the run's cache: 0
peak memory: 422 MB
```

## lookup-01 (code_switched) ok (10.6s)

**Q:** Nawa aka approve wa Ministry of Social Welfare & Community Development a 2025 budget?

```
An amince da jimilla na ₦7.08 biliyan ga Ministry of Social Welfare & Community Development a kasafin kuɗi na 2025 da aka amince da shi. Wannan ƙididdiga daga teburin jimillar kashe kuɗi ne ta ɓangaren gudanarwa (Total Expenditure by Administrative Classification).

• 2025 kasafin da aka amince da shi (jimilla): ₦7.08 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12
```

## lookup-02 (template) ok (10.5s)

**Q:** How much was approved for the Ministry for Local Government and Chieftancy in the 2026 budget?

```
The 2026 approved budget for the Ministry for Local Government and Chieftancy is ₦1.36 billion. This is the total expenditure allocation for the ministry in the Total Expenditure by Administrative Classification table.

• 2026 approved budget (total): ₦1.36 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19
```

## lookup-03 (followup) ok (7.7s)

**Q:** How much was approved for it in the 2026 budget?

```
₦969.94 million was approved for the Ministry of Solid Minerals and Natural Resources in the 2026 budget. This is the ministry's total expenditure figure from the Total Expenditure by Administrative Classification table.

• 2026 approved budget (total): ₦969.94 million
• 2026 approved budget (capital): ₦610.10 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## lookup-04 (code_switched) ok (7.5s)

**Q:** Nawa Ministry of Justice ta samu for 2024 budget?

```
An ware jimilla ₦2.21 biliyan ga Ministry of Justice a cikin kasafin kuɗi na 2024 da aka amince da shi. Wannan adadi jimilla ne na kashe kuɗi, daga teburin Total Expenditure by Administrative Classification.

• 2024 kasafin da aka amince da shi (jimilla): ₦2.21 biliyan

📄 *Madogara:* Sokoto State Government 2024 Approved Budget, shafi 44
```

## lookup-05 (hausa) ok (15.9s)

**Q:** Nawa aka amince wa Ministry of Livestocks and Fisheries Development a kasafin kudin 2025?

```
A kasafin kuɗin 2025 da aka amince da shi, jimillar kuɗin da aka amince wa Ministry of Animals and Fisheries Development (Ministry of Livestocks and Fisheries Development) ita ce ₦7.25 biliyan. Wannan ƙididdigar daga teburin Total Expenditure by Administrative Classification ce.

• 2025 kasafin da aka amince (jimilla): ₦7.25 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12
```

## lookup-06 (hausa) ok (9.4s)

**Q:** Nawa aka amince wa Ministry for Religious Affairs a budget na 2025?

```
An amince wa Ministry for Religious Affairs jimillar ₦11.26 biliyan a cikin kasafin 2025 da aka amince da shi. Wannan ita ce ƙadirar jimilla da aka amince da ita ga ma'aikatar (ciki har da hukumomin da ke ƙarƙashinta).

• 2025 kasafin da aka amince (jimilla): ₦11.26 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## split-01 (typo) ok (5.7s)

**Q:** Waht are teh personnel, overhead and capital allocations of the Ministry for Special Duties in 2026?

```
For Ministry for Special Duties, the approved budget (salaries) is ₦12.00 million.

*Ministry for Special Duties*:
• Personnel (salaries): approved budget ₦12.00 million
• Overhead (running costs): approved budget ₦195.50 million
• Capital: approved budget ₦622.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-02 (followup) ok (6.8s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
For Umaru Ali Shinkafi Polytechnic Sokoto, the approved budget (salaries) is ₦1.90 billion.

*Umaru Ali Shinkafi Polytechnic Sokoto*:
• Personnel (salaries): approved budget ₦1.90 billion
• Overhead (running costs): approved budget ₦453.00 million
• Capital: approved budget ₦2.43 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 27
```

## split-03 (template) ok (6.4s)

**Q:** What are the personnel, overhead and capital allocations of the Government Printing Press in 2026?

```
For Government Printing Press, the approved budget (salaries) is ₦24.40 million.

*Government Printing Press*:
• Personnel (salaries): approved budget ₦24.40 million
• Overhead (running costs): approved budget ₦22.50 million
• Capital: approved budget ₦50.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-04 (typo) ok (5.9s)

**Q:** What are teh personnel, overhead adn capital allocations of the State Emergency Management Agency (SEMA) in 2025?

```
For State Emergency Management Agency (SEMA), the approved budget (salaries) is ₦3.60 million.

*State Emergency Management Agency (SEMA)*:
• Personnel (salaries): approved budget ₦3.60 million
• Overhead (running costs): approved budget ₦125.00 million
• Capital: approved budget ₦300.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 14, 15
```

## split-05 (hausa) ok (5.2s)

**Q:** Menene allocation na personnel, overhead da capital na Fertilizer and Agricultral Supplies Company a 2026?

```
Ga Fertilizer and Agricultral Supplies Company, kasafin da aka amince (albashi) shi ne ₦68.17 miliyan.

*Fertilizer and Agricultral Supplies Company*:
• Albashi: kasafin da aka amince ₦68.17 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦23.50 miliyan
• Manyan ayyuka: kasafin da aka amince ₦23.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 20, 22, 25
```

## split-06 (followup) WRONG: missing ['4,481,100,000.00', '47,090,000.00'] (19.6s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
The documents publish its 2025 personnel allocation; the overhead and capital totals for it aren't published in these documents. Its 2025 approved budget for personnel is ₦39.78 million. The documents show some overhead line-items for it (e.g. stationery, printing, maintenance) but not a summed overhead total, and no capital total for it.

• 2025 approved budget (personnel): ₦39.78 million

📄 *Sources:* Sokoto State Government 2025 Amended Budget, p. 64; Sokoto State Government 2025 Approved Budget, p. 13
```

## spend_quarter-01 (hausa) ok (4.6s)

**Q:** College of Agriculture Wurno ta kashe naira nawa har zuwa karshen Q2 2026, idan aka duba da revised budget nata?

```
Ga College of Agriculture Wurno, kasafin da aka sabunta shi ne ₦1.28 biliyan.

*College of Agriculture Wurno*:
• Jimilla: kasafin da aka sabunta ₦1.28 biliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦162.98 miliyan; kason kasafin da aka sabunta da aka kashe 12.7% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 16
```

## spend_quarter-02 (template) ok (3.4s)

**Q:** How much had the Ministry of Justice spent by the end of Q2 2026, against its revised budget?

```
For Ministry of Justice, the spent so far (Q1–Q2) is ₦902.45 million.

*Ministry of Justice*:
• Total: spent so far (Q1–Q2) ₦902.45 million; revised budget ₦6.09 billion; share of the revised budget spent 14.8% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 17
```

## spend_quarter-03 (template) ok (5.7s)

**Q:** How much had the Infectious Diseases Hospital Amanawa spent by the end of Q2 2026, against its revised budget?

```
For Infectious Diseases Hospital Amanawa, the revised budget is ₦73.00 million.

*Infectious Diseases Hospital Amanawa*:
• Total: revised budget ₦73.00 million; spent so far (Q1–Q2) ₦7.50 million; share of the revised budget spent 10.3% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## spend_quarter-04 (typo) ok (5.5s)

**Q:** How much had teh Works School Sokoto spent by the end of Q3 2025, againts its revised budget?

```
For Works School Sokoto, the revised budget is ₦25.40 million.

*Works School Sokoto*:
• Total: revised budget ₦25.40 million; spent so far (Q1–Q3) ₦7.99 million; share of the revised budget spent 31.5% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## spend_quarter-05 (code_switched) ok (4.9s)

**Q:** Ministry for Special Duties ta kashe nawa by the end of Q2 2026, against revised budget dinta?

```
Ga Ministry for Special Duties, kasafin da aka sabunta shi ne ₦829.50 miliyan.

*Ministry for Special Duties*:
• Jimilla: kasafin da aka sabunta ₦829.50 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦41.81 miliyan; kason kasafin da aka sabunta da aka kashe 5.0% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 15
```

## spend_quarter-06 (hausa) ok (4.5s)

**Q:** Nawa Office of the Special Adviser on Economic Matters ta kashe har zuwa karshen Q3 2025, idan aka dubi revised budget nata?

```
Ga Office of the Special Adviser on Economic Matters, kasafin da aka sabunta shi ne ₦805.00 miliyan.

*Office of the Special Adviser on Economic Matters*:
• Jimilla: kasafin da aka sabunta ₦805.00 miliyan; abin da aka kashe zuwa yanzu (Q1–Q3) ₦120.00 miliyan; kason kasafin da aka sabunta da aka kashe 14.9% (lissafin Kasafi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 18
```

## compare-01 (code_switched) ok (3.8s)

**Q:** Kwatanta Ministry of Works approved budget na 2025 da 2026 fa?

```
Ga Ministry of Works, 2025 kasafin da aka amince shi ne ₦59.39 biliyan.

*Ministry of Works*:
• Jimilla: 2025 kasafin da aka amince ₦59.39 biliyan; 2026 kasafin da aka amince ₦59.17 biliyan; bambanci -₦227.66 miliyan (-0.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-02 (typo) ok (10.2s)

**Q:** Comapre the Law and Justice's aproved budget in 2025 and 2026.

```
Law and Justice's approved budget was ₦10.74 billion in 2025 and ₦14.26 billion in 2026. Both figures are the Total Expenditure by Administrative Classification for the ministry total including its agencies.

• 2025 approved budget (total): ₦10.74 billion
• 2026 approved budget (total): ₦14.26 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-03 (hausa) ok (3.2s)

**Q:** Kwatanta kasafin kuɗin da aka amince da shi na Sokoto State House of Assembly a 2025 da 2026.

```
Ga Sokoto State House of Assembly, 2025 kasafin da aka amince shi ne ₦9.37 biliyan.

*Sokoto State House of Assembly*:
• Jimilla: 2025 kasafin da aka amince ₦9.37 biliyan; 2026 kasafin da aka amince ₦12.26 biliyan; bambanci +₦2.89 biliyan (+30.8%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-04 (hausa) ok (3.2s)

**Q:** Kwatanta kasafin kuɗin Ministry Careers & Special Services da aka amince da shi a 2025 da 2026.

```
Ga Ministry Careers & Special Services, 2025 kasafin da aka amince shi ne ₦10.57 biliyan.

*Ministry Careers & Special Services*:
• Jimilla: 2025 kasafin da aka amince ₦10.57 biliyan; 2026 kasafin da aka amince ₦26.37 biliyan; bambanci +₦15.80 biliyan (+149.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-05 (template) ok (3.8s)

**Q:** Compare the State Judiciary's approved budget in 2025 and 2026.

```
For State Judiciary, the 2025 approved budget is ₦6.28 billion.

*State Judiciary*:
• Total: 2025 approved budget ₦6.28 billion; 2026 approved budget ₦8.17 billion; change +₦1.89 billion (+30.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-06 (hausa) ok (3.0s)

**Q:** Kwatanta kasafin kudin Ministry for Home Affairs da aka amince da shi a 2025 da kuma a 2026.

```
Ga Ministry for Home Affairs, 2025 kasafin da aka amince shi ne ₦2.11 biliyan.

*Ministry for Home Affairs*:
• Jimilla: 2025 kasafin da aka amince ₦2.11 biliyan; 2026 kasafin da aka amince ₦6.11 biliyan; bambanci +₦4.01 biliyan (+190.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## share-01 (code_switched) ok (4.7s)

**Q:** Wannan 2026 approved budget na State Universal Basic Education Board (SUBEB), what share ne na capital?

```
Ga State Universal Basic Education Board (SUBEB), kasafin da aka amince (albashi) shi ne ₦314.91 miliyan.

*State Universal Basic Education Board (SUBEB)*:
• Albashi: kasafin da aka amince ₦314.91 miliyan; 2.9% na jimillarsa (lissafin Kasafi)
• Kuɗin gudanarwa: kasafin da aka amince ₦1.27 biliyan; 11.8% na jimillarsa (lissafin Kasafi)
• Manyan ayyuka: kasafin da aka amince ₦9.15 biliyan; 85.2% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦10.73 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 21, 24, 27
```

## share-02 (hausa) ok (4.0s)

**Q:** Kashi nawa na approved budget na Female Education Board na 2026 ne na capital?

```
Ga Female Education Board, kasafin da aka amince (manyan ayyuka) shi ne ₦650.00 miliyan.

*Female Education Board*:
• Manyan ayyuka: kasafin da aka amince ₦650.00 miliyan; 56.1% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦1.16 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 27
```

## share-03 (typo) ok (3.7s)

**Q:** What sahre of the State Agency for Normadic Education1's 2026 approved budjet is capial?

```
For State Agency for Normadic Education, the approved budget (capital) is ₦383.42 million.

*State Agency for Normadic Education*:
• Capital: approved budget ₦383.42 million; 49.5% of its total (Kasafi's calculation)
• Total: approved budget ₦774.42 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 27
```

## share-04 (informal) ok (3.8s)

**Q:** What's the capital share of Ministry of Agriculture & Natural Resource's 2026 approved budget?

```
For Ministry of Agriculture & Natural Resource, the approved budget (capital) is ₦14.93 billion.

*Ministry of Agriculture & Natural Resource*:
• Capital: approved budget ₦14.93 billion; 87.6% of its total (Kasafi's calculation)
• Total: approved budget ₦17.05 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 25
```

## share-05 (template) ok (3.8s)

**Q:** What share of the Hisbah Board Sokoto's 2026 approved budget is capital?

```
For Hisbah Board Sokoto, the approved budget (capital) is ₦294.00 million.

*Hisbah Board Sokoto*:
• Capital: approved budget ₦294.00 million; 33.0% of its total (Kasafi's calculation)
• Total: approved budget ₦889.67 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 25
```

## share-06 (code_switched) ok (3.5s)

**Q:** Wane share na Ministry of Energy and Petroleum Resources approved budget na 2026 ne capital?

```
Ga Ministry of Energy and Petroleum Resources, kasafin da aka amince (manyan ayyuka) shi ne ₦22.47 biliyan.

*Ministry of Energy and Petroleum Resources*:
• Manyan ayyuka: kasafin da aka amince ₦22.47 biliyan; 96.3% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦23.33 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## false_premise-01 (informal) ok (2.8s)

**Q:** Why'd the Ministry for Local Government and Chieftancy's approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry for Local Government and Chieftancy, the 2025 approved budget (salaries) is ₦145.67 million.

*Ministry for Local Government and Chieftancy*:
• Personnel (salaries): 2025 approved budget ₦145.67 million; 2026 approved budget ₦190.67 million; change +₦45.00 million (+30.9%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦211.97 million; 2026 approved budget ₦317.96 million; change +₦105.99 million (+50.0%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦213.00 million; 2026 approved budget ₦850.44 million; change +₦637.44 million (+299.3%) (Kasafi's calculation)
• Total: 2025 approved budget ₦570.64 million; 2026 approved budget ₦1.36 billion; change +₦788.43 million (+138.2%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 14, 15, 17; Sokoto State FY 2026 Budget, p. 19, 21, 24, 27
```

## false_premise-02 (typo) ok (3.2s)

**Q:** Why did teh Office of Auditor General's aproved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Office of Auditor General, the 2025 approved budget is ₦542.84 million.

*Office of Auditor General*:
• Total: 2025 approved budget ₦542.84 million; 2026 approved budget ₦606.84 million; change +₦64.00 million (+11.8%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## false_premise-03 (informal) ok (3.3s)

**Q:** Why'd the Office of the SSG's approved budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Office of the SSG, the 2025 approved budget is ₦31.36 billion.

*Office of the SSG*:
• Total: 2025 approved budget ₦31.36 billion; 2026 approved budget ₦40.40 billion; change +₦9.04 billion (+28.8%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## false_premise-04 (hausa) WRONG: error TypeError (26.9s)

**Q:** Me ya sa kasafin kudin Social Sector da aka amince da shi ya ragu daga 2025 zuwa 2026?

```
-
```

## false_premise-05 (followup) ok (2.8s)

**Q:** Why did its approved budget rise from 2025 to 2026?

```
It didn't rise: the approved budget fell from 2025 to 2026, so there is no rise to explain.
For Ministry of Finance, the 2025 approved budget is ₦47.75 billion.

*Ministry of Finance*:
• Total: 2025 approved budget ₦47.75 billion; 2026 approved budget ₦40.27 billion; change -₦7.47 billion (-15.7%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-06 (typo) ok (3.0s)

**Q:** Why did teh Ministry of Commerce and Industrys approved budjet fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Commerce and Industry, the 2025 approved budget is ₦6.06 billion.

*Ministry of Commerce and Industry*:
• Total: 2025 approved budget ₦6.06 billion; 2026 approved budget ₦6.56 billion; change +₦503.51 million (+8.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## not_in_data-01 (code_switched) ok (12.1s)

**Q:** Approved budget na Sokoto State Housing Cooperation for 2028 nawa ne?

```
⚠️ Ban samo takardar da ta fi dacewa ba (Sokoto State Government 2028 Approved Budget). Amsar da ke ƙasa daga wasu takardun da nake da su ce, ba daga waccan ba.

Kasafin da aka amince da shi na 2028 bai buga a cikin takardun ba. Abin da aka buga don Sokoto State Housing Cooperation shi ne kimar shekarun gaba (Out-Year Estimate) ta 2028: ₦376.45 miliyan. Wannan kima daga teburin jimillar kashe kuɗi ne (Total Expenditure).

• 2028 kimar shekarun gaba (jimilla): ₦376.45 miliyan
• 2026 kasafin da aka amince da shi (jimilla): ₦376.45 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
```

## not_in_data-02 (code_switched) ok (7.7s)

**Q:** Nawa be approved budget na Ministry of Budget and Economic Planning for 2028?

```
⚠️ Ban samo takardar da ta fi dacewa ba (Sokoto State 2028 Approved Budget). Amsar da ke ƙasa daga wasu takardun da nake da su ce, ba daga waccan ba.

Kasafin 2028 da aka amince da shi na Ministry of Budget and Economic Planning bai bayyana a cikin takardun nan ba. Abin da ya bayyana shi ne ƙiyasin shekarar 2028 (Out-Year Estimate) na jimillar kashe kuɗi: ₦5.85 biliyan. Wannan ƙiyasi ne, ba kasafin da aka amince da shi ba.

• 2028 ƙiyasin shekara mai zuwa (jimilla): ₦5.85 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## not_in_data-03 (followup) ok (3.8s)

**Q:** How much did it spend in Q4 2026?

```
Not in the documents:
• House of Assembly Service Commission 2026 spent in Q4: the latest implementation report is Q2 2026
```

## not_in_data-04 (code_switched) ok (11.6s)

**Q:** Nawa approved budget na Department for Rural Electrification for 2028?

```
⚠️ Ban samo takardar da ta fi dacewa ba (Sokoto State 2028 Approved Budget). Amsar da ke ƙasa daga wasu takardun da nake da su ce, ba daga waccan ba.

A cikin waɗannan takardu ba a buga ƙayyadadden kasafin da aka amince da shi na 2028 na Department for Rural Electrification ba. Abin da ake da shi shi ne ƙiyasin shekarar 2028 da aka sanya a cikin kasafin 2026, wanda jimillarsa ta kai ₦1.38 biliyan. Wannan ƙiyasi ne, ba kasafin da aka amince da shi ba.

• 2028 ƙiyasin shekara (jimilla): ₦1.38 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## not_in_data-05 (followup) ok (4.3s)

**Q:** How much did it spend in Q4 2026?

```
Not in the documents:
• State Emergency Management Agency (SEMA) 2026 spent in Q4: the latest implementation report is Q2 2026
• State Emergency Management Agency (SEMA) 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
• State Emergency Management Agency (SEMA) 2026 share of the revised budget spent: the latest implementation report is Q2 2026
```

## not_in_data-06 (followup) ok (3.9s)

**Q:** How much did it spend in Q4 2026?

```
Not in the documents:
• Shehu Shagari Collage of Education Sokoto 2026 spent in Q4: the latest implementation report is Q2 2026
• Shehu Shagari Collage of Education Sokoto 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
```

## rank_lga-01 (code_switched) WRONG: missing ['40,729', '19,151', '17,143', '15,068', '14,850', '14,047', '8,953', '8,406', '8,277', '4,615'] (3.2s)

**Q:** Abeg, which 10 LGAs ne a Sokoto da get most IDPs?

```
*koriyar damina a ƙololuwa ta gonaki (MODIS NDVI, mita 250, kashi na 90 na hotunan Yuni–Oktoba): ƙananan hukumomi 23 na Jihar Sokoto, 2025*

Mafi yawan gonakin Jihar Sokoto sun kasance ba su yi koriya kamar yadda aka saba ba a 2025; Tangaza ce ƙaramar hukuma mafi ƙarancin koriya, duk da cewa ruwan samanta ya wuce yadda aka saba.

A ƙananan hukumomi 23 na Jihar Sokoto, koriyar ƙololuwa na 2025 ya tashi daga 0.21 (Tangaza) zuwa 0.40 (Sokoto North); matsakaici 0.26. Mafi koriya: Sokoto North (0.40), Bodinga (0.33), Sokoto South (0.30). Mafi ƙarancin koriya: Tangaza (0.21), Gudu (0.21), Tambuwal (0.21).

Idan aka kwatanta kowace gunduma da shekarunta da ruwan saman daminar: babu gundumar da ta bambanta da shekarunta da ruwan sama; gundumomi 23 ba su da isassun shekaru don kwatancen ruwan sama.

Lokaci 2001–2026; ƙuduri 250 m. Gonaki kawai (ESA WorldCover 2021).

*Jeri (23 ƙananan hukumomi)*
Mafi girma:
1. Sokoto North: 0.40 (lura 5)
2. Bodinga: 0.33 (lura 5)
3. Sokoto South: 0.30 (lura 5)
4. Dange Shuni: 0.29 (lura 5)
5. Yabo: 0.29 (lura 5)
Mafi ƙanƙanta:
19. Gwadabawa: 0.22 (lura 5)
20. Binji: 0.22 (lura 5)
21. Tambuwal: 0.21 (lura 4)
22. Gudu: 0.21 (lura 5)
23. Tangaza: 0.21 (lura 5)

Ana haɗa layukan kasafi ne a kowace ƙaramar hukuma: tambaya game da ƙaramar hukuma ɗaya don ganin nata.

Kasafi yana bayyana abin da hotunan tauraron ɗan adam suka nuna ne; ba ya yanke hukunci kan dalilai ko aikin kowa.

Madogara: MODIS 13Q1 v061 (Terra and Aqua), Microsoft Planetary Computer; iyakoki: gundumomin GRID3 da ƙananan hukumomin OCHA COD-AB.
```

## rank_lga-02 (informal) WRONG: missing ['40,729', '19,151', '17,143'] (3.9s)

**Q:** Which 3 LGAs in Sokoto have most IDPs?

```
*peak rainy-season greenness of cropland (MODIS NDVI, 250 m, 90th percentile of June–October composites): the 23 LGAs of Sokoto State, 2025*

Most of Sokoto State's farmland was less green than usual in 2025; Tangaza was the least green LGA, although its rain was above usual.

Across the 23 LGAs of Sokoto State, the 2025 peak greenness ranged from 0.21 (Tangaza) to 0.40 (Sokoto North); the median was 0.26. Greenest: Sokoto North (0.40), Bodinga (0.33), Sokoto South (0.30). Least green: Tangaza (0.21), Gudu (0.21), Tambuwal (0.21).

Against each ward's own years and that season's rain: no ward stood out against its own years and the rain; 23 wards had too few years for a rain comparison.

Period 2001–2026; resolution 250 m. Cropland only (ESA WorldCover 2021).

*Ranking (23 LGAs)*
Highest:
1. Sokoto North: 0.40 (5 obs)
2. Bodinga: 0.33 (5 obs)
3. Sokoto South: 0.30 (5 obs)
4. Dange Shuni: 0.29 (5 obs)
5. Yabo: 0.29 (5 obs)
Lowest:
19. Gwadabawa: 0.22 (5 obs)
20. Binji: 0.22 (5 obs)
21. Tambuwal: 0.21 (4 obs)
22. Gudu: 0.21 (5 obs)
23. Tangaza: 0.21 (5 obs)

Budget lines are linked per LGA: ask about one LGA to see its lines.

Kasafi reports what the satellite record shows; it makes no judgement of causes or of anyone's work.

Sources: MODIS 13Q1 v061 (Terra and Aqua), Microsoft Planetary Computer; boundaries GRID3 wards and OCHA COD-AB LGAs.
```

## rank_lga-03 (template) WRONG: missing ['40,729', '19,151', '17,143', '15,068', '14,850'] (3.4s)

**Q:** Which 5 LGAs in Sokoto have the most IDPs?

```
*peak rainy-season greenness of cropland (MODIS NDVI, 250 m, 90th percentile of June–October composites): the 23 LGAs of Sokoto State, 2025*

Most of Sokoto State's farmland was less green than usual in 2025; Tangaza was the least green LGA, although its rain was above usual.

Across the 23 LGAs of Sokoto State, the 2025 peak greenness ranged from 0.21 (Tangaza) to 0.40 (Sokoto North); the median was 0.26. Greenest: Sokoto North (0.40), Bodinga (0.33), Sokoto South (0.30). Least green: Tangaza (0.21), Gudu (0.21), Tambuwal (0.21).

Against each ward's own years and that season's rain: no ward stood out against its own years and the rain; 23 wards had too few years for a rain comparison.

Period 2001–2026; resolution 250 m. Cropland only (ESA WorldCover 2021).

*Ranking (23 LGAs)*
Highest:
1. Sokoto North: 0.40 (5 obs)
2. Bodinga: 0.33 (5 obs)
3. Sokoto South: 0.30 (5 obs)
4. Dange Shuni: 0.29 (5 obs)
5. Yabo: 0.29 (5 obs)
Lowest:
19. Gwadabawa: 0.22 (5 obs)
20. Binji: 0.22 (5 obs)
21. Tambuwal: 0.21 (4 obs)
22. Gudu: 0.21 (5 obs)
23. Tangaza: 0.21 (5 obs)

Budget lines are linked per LGA: ask about one LGA to see its lines.

Kasafi reports what the satellite record shows; it makes no judgement of causes or of anyone's work.

Sources: MODIS 13Q1 v061 (Terra and Aqua), Microsoft Planetary Computer; boundaries GRID3 wards and OCHA COD-AB LGAs.
```

## lookup_lga-01 (template) ok (6.4s)

**Q:** How many IDPs are there in Kebbe LGA?

```
IOM DTM counts *4,252* IDPs in Kebbe (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (template) WRONG: missing ['4,486'] (3.1s)

**Q:** How many IDPs are there in Sokoto South LGA?

```
*peak rainy-season greenness of cropland (MODIS NDVI, 250 m, 90th percentile of June–October composites): wards of Sokoto South LGA, 2025*

Most of Sokoto South LGA's farmland was less green than usual in 2025; Gagi B was the least green ward, although its rain was above usual.

Across wards of Sokoto South LGA, the 2025 peak greenness ranged from 0.24 (Gagi B) to 0.37 (Gagi C); the median was 0.31. Greenest: Gagi C (0.37), Tudun Wada A (0.35), Gagi A (0.31). Least green: Gagi B (0.24), Tudun Wada B (0.28), Gagi A (0.31).

Against each ward's own years and that season's rain: no ward stood out against its own years and the rain; 5 wards had too few years for a rain comparison.

Period 2001–2026; resolution 250 m. Cropland only (ESA WorldCover 2021).

*Ranking (5 wards)*
Highest:
1. Gagi C: 0.37 (5 obs)
2. Tudun Wada A: 0.35 (5 obs)
3. Gagi A: 0.31 (5 obs)
4. Tudun Wada B: 0.28 (5 obs)
5. Gagi B: 0.24 (5 obs)

No 2026 budget line names Sokoto South; statewide lines that may cover it:
• Agriculture: ₦23,674,744,186 across 58 statewide lines
• Irrigation and dams: ₦12,455,921,920 across 17 statewide lines
• Erosion and drainage: ₦5,069,000,000 across 14 statewide lines
• Environment and forestry: ₦1,605,000,000 across 17 statewide lines
(Sokoto State FY 2026 Budget; statewide lines are not split by LGA)

Kasafi reports what the satellite record shows; it makes no judgement of causes or of anyone's work.

Sources: MODIS 13Q1 v061 (Terra and Aqua), Microsoft Planetary Computer; boundaries GRID3 wards and OCHA COD-AB LGAs.
```

## lookup_lga-03 (typo) WRONG: missing ['1,039'] (2.9s)

**Q:** How mnay IDPs are thare in Kware LGA?

```
*peak rainy-season greenness of cropland (MODIS NDVI, 250 m, 90th percentile of June–October composites): wards of Kware LGA, 2025*

Most of Kware LGA's farmland was less green than usual in 2025; Bankanu was the least green ward, although its rain was above usual.

Across wards of Kware LGA, the 2025 peak greenness ranged from 0.20 (Bankanu) to 0.38 (Tsaki Walakae); the median was 0.29. Greenest: Tsaki Walakae (0.38), Basansan (0.36), Gidan Rugga More (0.35). Least green: Bankanu (0.20), Sabon Birni (0.20), Kware (0.23).

Against each ward's own years and that season's rain: no ward stood out against its own years and the rain; 11 wards had too few years for a rain comparison.

Period 2001–2026; resolution 250 m. Cropland only (ESA WorldCover 2021).

*Ranking (11 wards)*
Highest:
1. Tsaki Walakae: 0.38 (5 obs)
2. Basansan: 0.36 (5 obs)
3. Gidan Rugga More: 0.35 (5 obs)
4. Tunga Mallamawa: 0.32 (5 obs)
5. Durbawa: 0.30 (5 obs)
Lowest:
7. Gandu: 0.29 (5 obs)
8. Hamma Ali Marabawa: 0.25 (5 obs)
9. Kware: 0.23 (5 obs)
10. Sabon Birni: 0.20 (5 obs)
11. Bankanu: 0.20 (5 obs)

No 2026 budget line names Kware; statewide lines that may cover it:
• Agriculture: ₦23,674,744,186 across 58 statewide lines
• Irrigation and dams: ₦12,455,921,920 across 17 statewide lines
• Erosion and drainage: ₦5,069,000,000 across 14 statewide lines
• Environment and forestry: ₦1,605,000,000 across 17 statewide lines
(Sokoto State FY 2026 Budget; statewide lines are not split by LGA)

Kasafi reports what the satellite record shows; it makes no judgement of causes or of anyone's work.

Sources: MODIS 13Q1 v061 (Terra and Aqua), Microsoft Planetary Computer; boundaries GRID3 wards and OCHA COD-AB LGAs.
```

## lookup_lga-04 (hausa) WRONG: missing ['3,386'] (2.8s)

**Q:** IDPs nawa ne suke a Silame LGA?

```
*koriyar damina a ƙololuwa ta gonaki (MODIS NDVI, mita 250, kashi na 90 na hotunan Yuni–Oktoba): gundumomin Ƙaramar Hukumar Silame, 2025*

Mafi yawan gonakin Ƙaramar Hukumar Silame sun kasance ba su yi koriya kamar yadda aka saba ba a 2025; Kubodu ce gunduma mafi ƙarancin koriya, duk da cewa ruwan samanta ya wuce yadda aka saba.

A gundumomin Ƙaramar Hukumar Silame, koriyar ƙololuwa na 2025 ya tashi daga 0.19 (Kubodu) zuwa 0.33 (Gaukai); matsakaici 0.27. Mafi koriya: Gaukai (0.33), Katami North (0.31), Maje (0.30). Mafi ƙarancin koriya: Kubodu (0.19), Jekanadu (0.24), Silame (0.24).

Idan aka kwatanta kowace gunduma da shekarunta da ruwan saman daminar: babu gundumar da ta bambanta da shekarunta da ruwan sama; gundumomi 10 ba su da isassun shekaru don kwatancen ruwan sama.

Lokaci 2001–2026; ƙuduri 250 m. Gonaki kawai (ESA WorldCover 2021).

*Jeri (10 gundumomi)*
Mafi girma:
1. Gaukai: 0.33 (lura 5)
2. Katami North: 0.31 (lura 5)
3. Maje: 0.30 (lura 5)
4. Labani: 0.28 (lura 5)
5. Gande: 0.27 (lura 5)
Mafi ƙanƙanta:
6. Marafa: 0.25 (lura 5)
7. Katami South: 0.25 (lura 4)
8. Silame: 0.24 (lura 5)
9. Jekanadu: 0.24 (lura 5)
10. Kubodu: 0.19 (lura 5)

Babu layin kasafin 2026 da ya ambaci Silame; layukan faɗin jiha da ka iya shafarta:
• Noma: ₦23,674,744,186 a layuka 58 na faɗin jiha
• Ban ruwa da madatsu: ₦12,455,921,920 a layuka 17 na faɗin jiha
• Zaizayar ƙasa da magudanai: ₦5,069,000,000 a layuka 14 na faɗin jiha
• Muhalli da gandun daji: ₦1,605,000,000 a layuka 17 na faɗin jiha
(Sokoto State FY 2026 Budget; ba a raba layukan faɗin jiha bisa ƙaramar hukuma ba)

Kasafi yana bayyana abin da hotunan tauraron ɗan adam suka nuna ne; ba ya yanke hukunci kan dalilai ko aikin kowa.

Madogara: MODIS 13Q1 v061 (Terra and Aqua), Microsoft Planetary Computer; iyakoki: gundumomin GRID3 da ƙananan hukumomin OCHA COD-AB.
```

## lookup_lga-05 (code_switched) WRONG: missing ['1,014'] (3.7s)

**Q:** How many IDPs ne a Gada LGA?

```
*koriyar damina a ƙololuwa ta gonaki (MODIS NDVI, mita 250, kashi na 90 na hotunan Yuni–Oktoba): gundumomin Ƙaramar Hukumar Gada, 2025*

Mafi yawan gonakin Ƙaramar Hukumar Gada sun kasance ba su yi koriya kamar yadda aka saba ba a 2025; Kaddi ce gunduma mafi ƙarancin koriya, duk da cewa ruwan samanta ya wuce yadda aka saba.

A gundumomin Ƙaramar Hukumar Gada, koriyar ƙololuwa na 2025 ya tashi daga 0.20 (Kaddi) zuwa 0.32 (Kadassaka); matsakaici 0.25. Mafi koriya: Kadassaka (0.32), Kyadawa Holai (0.29), Gada (0.27). Mafi ƙarancin koriya: Kaddi (0.20), Dukamaje (0.20), Gilbadi (0.22).

Idan aka kwatanta kowace gunduma da shekarunta da ruwan saman daminar: babu gundumar da ta bambanta da shekarunta da ruwan sama; gundumomi 11 ba su da isassun shekaru don kwatancen ruwan sama.

Lokaci 2001–2026; ƙuduri 250 m. Gonaki kawai (ESA WorldCover 2021).

*Jeri (11 gundumomi)*
Mafi girma:
1. Kadassaka: 0.32 (lura 5)
2. Kyadawa Holai: 0.29 (lura 5)
3. Gada: 0.27 (lura 5)
4. Tsitse: 0.26 (lura 5)
5. Kadadi: 0.26 (lura 5)
Mafi ƙanƙanta:
7. Kwarma: 0.24 (lura 5)
8. Kaffe: 0.22 (lura 5)
9. Gilbadi: 0.22 (lura 5)
10. Dukamaje: 0.20 (lura 5)
11. Kaddi: 0.20 (lura 5)

Babu layin kasafin 2026 da ya ambaci Gada; layukan faɗin jiha da ka iya shafarta:
• Noma: ₦23,674,744,186 a layuka 58 na faɗin jiha
• Ban ruwa da madatsu: ₦12,455,921,920 a layuka 17 na faɗin jiha
• Zaizayar ƙasa da magudanai: ₦5,069,000,000 a layuka 14 na faɗin jiha
• Muhalli da gandun daji: ₦1,605,000,000 a layuka 17 na faɗin jiha
(Sokoto State FY 2026 Budget; ba a raba layukan faɗin jiha bisa ƙaramar hukuma ba)

Kasafi yana bayyana abin da hotunan tauraron ɗan adam suka nuna ne; ba ya yanke hukunci kan dalilai ko aikin kowa.

Madogara: MODIS 13Q1 v061 (Terra and Aqua), Microsoft Planetary Computer; iyakoki: gundumomin GRID3 da ƙananan hukumomin OCHA COD-AB.
```

## lookup_lga-06 (hausa) WRONG: missing ['8,277'] (2.9s)

**Q:** IDPs nawa ne a Rabah LGA?

```
*koriyar damina a ƙololuwa ta gonaki (MODIS NDVI, mita 250, kashi na 90 na hotunan Yuni–Oktoba): gundumomin Ƙaramar Hukumar Rabah, 2025*

Mafi yawan gonakin Ƙaramar Hukumar Rabah sun kasance ba su yi koriya kamar yadda aka saba ba a 2025; Tursa ce gunduma mafi ƙarancin koriya, duk da cewa ruwan samanta ya wuce yadda aka saba.

A gundumomin Ƙaramar Hukumar Rabah, koriyar ƙololuwa na 2025 ya tashi daga 0.23 (Tursa) zuwa 0.32 (Tofa); matsakaici 0.28. Mafi koriya: Tofa (0.32), Gandi 2 (0.32), Gandi 1 (0.29). Mafi ƙarancin koriya: Tursa (0.23), Tsamiya (0.23), Yarstakuwa (0.24).

Idan aka kwatanta kowace gunduma da shekarunta da ruwan saman daminar: babu gundumar da ta bambanta da shekarunta da ruwan sama; gundumomi 11 ba su da isassun shekaru don kwatancen ruwan sama.

Lokaci 2001–2026; ƙuduri 250 m. Gonaki kawai (ESA WorldCover 2021).

*Jeri (11 gundumomi)*
Mafi girma:
1. Tofa: 0.32 (lura 5)
2. Gandi 2: 0.32 (lura 5)
3. Gandi 1: 0.29 (lura 5)
4. Kurya: 0.28 (lura 5)
5. Goddodi: 0.28 (lura 5)
Mafi ƙanƙanta:
7. Rarah: 0.26 (lura 5)
8. Rabah: 0.25 (lura 5)
9. Yarstakuwa: 0.24 (lura 5)
10. Tsamiya: 0.23 (lura 5)
11. Tursa: 0.23 (lura 5)

Babu layin kasafin 2026 da ya ambaci Rabah; layukan faɗin jiha da ka iya shafarta:
• Noma: ₦23,674,744,186 a layuka 58 na faɗin jiha
• Ban ruwa da madatsu: ₦12,455,921,920 a layuka 17 na faɗin jiha
• Zaizayar ƙasa da magudanai: ₦5,069,000,000 a layuka 14 na faɗin jiha
• Muhalli da gandun daji: ₦1,605,000,000 a layuka 17 na faɗin jiha
(Sokoto State FY 2026 Budget; ba a raba layukan faɗin jiha bisa ƙaramar hukuma ba)

Kasafi yana bayyana abin da hotunan tauraron ɗan adam suka nuna ne; ba ya yanke hukunci kan dalilai ko aikin kowa.

Madogara: MODIS 13Q1 v061 (Terra and Aqua), Microsoft Planetary Computer; iyakoki: gundumomin GRID3 da ƙananan hukumomin OCHA COD-AB.
```

## trend-01 (template) ok (5.1s)

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
