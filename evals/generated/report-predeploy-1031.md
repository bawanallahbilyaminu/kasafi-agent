# Generated coverage run

Cases: cases-912479.json (draw seed 912479), form seed 1031

52 cases: wrong 6 (11.5%), of them wrong agency 0 | median 5.0s

| family | wrong | of |
|---|---|---|
| compare | 0 | 6 |
| false_premise | 0 | 6 |
| lookup | 0 | 6 |
| lookup_lga | 5 | 6 |
| not_in_data | 0 | 6 |
| rank_lga | 1 | 3 |
| share | 0 | 6 |
| spend_quarter | 0 | 6 |
| split | 0 | 6 |
| trend | 0 | 1 |

| form | wrong | of |
|---|---|---|
| code_switched | 1 | 15 |
| followup | 1 | 7 |
| hausa | 3 | 11 |
| informal | 0 | 6 |
| template | 0 | 8 |
| typo | 1 | 5 |

```
Cost of this run:
  Baseten: 26 calls, 220,720 prompt tokens (66,304 cached), 12,111 output tokens -> $0.25
  Meta: 86 calls, 421,523 prompt tokens (318,657 cached), 58,383 output tokens -> $0.42
  models together: $0.68 (prices per 1M tokens from settings kasafi_price_*)
  per answer (52 answers): $0.0131, 2.2 model calls
    Meta/plan               1.00 calls  $0.0038  (29%)
    Baseten/compose         0.27 calls  $0.0031  (23%)
    Meta/topic              0.40 calls  $0.0022  (17%)
    Meta/read1              0.25 calls  $0.0022  (17%)
    Baseten/read2           0.23 calls  $0.0018  (14%)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0) | identical calls answered from the run's cache: 0
peak memory: 258 MB
```

## lookup-01 (hausa) ok (17.2s)

**Q:** Nawa aka amince wa Ministry of Youth and Sports Development a kasafin kudin 2025?

```
An amince wa Ministry of Youth and Sports Development jimillar ₦4.02 biliyan a kasafin kuɗin 2025. Wannan adadi daga teburin Total Expenditure by Administrative Classification ne kuma shi ne jimillar kasafin da aka amince wa ma’aikatar a shekarar 2025.

• 2025 jimilla da aka amince (total): ₦4.02 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12
```

## lookup-02 (followup) ok (9.0s)

**Q:** How much was approved for it in the 2025 budget?

```
The Ministry of Lands and Housing was allocated ₦47.46 billion in the 2025 approved budget (total expenditure). This is the budget approved at the start of the year, not what was later spent.

• 2025 approved budget (total): ₦47.46 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12
```

## lookup-03 (code_switched) ok (12.6s)

**Q:** Nawa aka approve wa Office of Auditor General a 2025 budget?

```
Jimillar kuɗin da aka amince wa Office of Auditor General a kasafin kuɗi na 2025 wadda aka amince da ita ita ce ₦542.84 miliyan. Wannan adadi daga teburin Jimillar Kashe Kuɗi ne ta Rukunin Gudanarwa.

• 2025 approved budget (jimilla): ₦542.84 miliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-04 (code_switched) ok (9.4s)

**Q:** Nawa Ministry for Women Affairs ta samu a 2025 budget?

```
Ma'aikatar Harkokin Mata ta samu ₦8.44 biliyan a kasafin 2025 da aka amince da shi. Wannan jimilla ce ta kashe kuɗaɗe gaba ɗaya (Total Expenditure) daga teburin Rarraba ta Ma'aikata.

• 2025 kasafin da aka amince da shi (jimilla): ₦8.44 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12
```

## lookup-05 (followup) ok (9.1s)

**Q:** How much was approved for it in the 2026 budget?

```
The Local Government Service Commission was allocated ₦746.52 million as its total budget for 2026. This is the 2026 Approved Budget figure for Total Expenditure.

• 2026 approved budget (total): ₦746.52 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
```

## lookup-06 (code_switched) ok (10.2s)

**Q:** A 2026 budget, how much aka approve wa Department of Establishment and Pensions?

```
A kasafin 2026 da aka amince da shi, an ware jimilla ₦11.84 biliyan ga Department of Establishment and Pensions. Wannan adadi ne da aka amince da shi a matsayin jimillar kashewa ta ma'aikatar a shekarar 2026.

• 2026 jimilla da aka amince da ita (jimilla): ₦11.84 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16
```

## split-01 (template) ok (4.5s)

**Q:** What are the personnel, overhead and capital allocations of the ZAKAT and Endowment Agency (WAQF) in 2025?

```
*ZAKAT and Endowment Agency (WAQF)* (code 017200700100):
• Personnel (salaries): approved budget ₦11.45 million
• Overhead (running costs): approved budget ₦874.90 million
• Capital: approved budget ₦610.20 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 14, 16
```

## split-02 (informal) ok (4.1s)

**Q:** personnel, overhead and capital for Sokoto College of Legal & Islamic St. in 2026 - how much each?

```
*Sokoto College of Legal & Islamic St.* (code 032600600500):
• Personnel (salaries): approved budget ₦193.92 million
• Overhead (running costs): approved budget ₦133.50 million
• Capital: approved budget ₦770.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 26
```

## split-03 (template) ok (22.0s)

**Q:** What are the personnel, overhead and capital allocations of the Sokoto State contributory health care mgt agency in 2025?

```
The 2025 personnel allocation is ₦11.95 million from the 2025 approved budget. The 2025 overhead allocation shown is ₦70.50 million and the 2025 capital allocation shown is ₦152.00 million; both are 2025 Revised figures from the 2026 budget tables.

• Sokoto State contributory health care mgt agency (one agency or unit, personnel (salaries), code 052100200100), 2025 Approved Budget: ₦11.95 million
• Sokoto State contributory health care mgt agency (one agency or unit, overhead (running costs), code 052100200100) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2025 Revised Budget: ₦70.50 million
• Sokoto State contributory health care mgt agency (one agency or unit, capital, code 052100200100) [Capital Expenditure by Administrative Classification], 2025 Revised Budget: ₦152.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13; Sokoto State FY 2026 Budget, p. 24, 27
_Reply *show working* to see the rows and arithmetic._
```

## split-04 (typo) ok (4.0s)

**Q:** What are teh personnel, overhead and capital allocatios of the Sokoto State House of Assembly in 2026?

```
*Sokoto State House of Assembly* (code 011200000000):
• Personnel (salaries): approved budget ₦1.60 billion
• Overhead (running costs): approved budget ₦6.00 billion
• Capital: approved budget ₦4.66 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-05 (informal) ok (4.5s)

**Q:** What's the 2026 personnel, overhead and capital split for Primary School Staff Pension Board?

```
*Primary School Staff Pension Board* (code 011103500200):
• Personnel (salaries): approved budget ₦39.34 million
• Overhead (running costs): approved budget ₦21.00 million
• Capital: approved budget ₦0.00

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-06 (informal) ok (12.5s)

**Q:** Sokoto State University personnel, overhead & capital for 2025?

```
Sokoto State University's 2025 allocation was ₦2.29 billion for personnel, ₦110.50 million for overhead, and ₦1.11 billion for capital. These are budgeted (approved/original budget) figures for 2025.

• Sokoto State University (one agency or unit, personnel (salaries), code 056900400100), 2025 Approved Budget: ₦2.29 billion
• Sokoto State University (one agency or unit, overhead (running costs), code 056900400100), 2025 Original Budget: ₦110.50 million
• Sokoto State University (one agency or unit, capital, code 056900400100), 2025 Original Budget: ₦1.11 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13; Sokoto State Budget Implementation Report Q3 2025, p. 27; Budget Implementation Report Q4 2025, p. 30
_Reply *show working* to see the rows and arithmetic._
```

## spend_quarter-01 (followup) ok (4.0s)

**Q:** How much had it spent by the end of Q2 2026, against its revised budget?

```
*Office of the Accountant General* (code 022000700100):
• Total: spent so far (Q1–Q2) ₦1.49 billion; revised budget ₦21.52 billion; share of the revised budget spent 6.9% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 16
```

## spend_quarter-02 (followup) ok (4.5s)

**Q:** How much had it spent by the end of Q3 2025, against its revised budget?

```
*Ministry of Youth and Sports Development* (code 051300000000):
• Total: spent so far (Q1–Q3) ₦1.17 billion; revised budget ₦4.22 billion; share of the revised budget spent 27.7% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## spend_quarter-03 (template) ok (13.2s)

**Q:** How much had the Ministry of Works spent by the end of Q3 2025, against its revised budget?

```
By the end of Q3 2025 the Ministry of Works (total including its agencies) had spent ₦9.15 billion of its 2025 revised budget of ₦50.52 billion — 18.1% of the revised budget.

• 2025 Revised Budget (total): ₦50.52 billion
• 2025 Performance Year to Date (Q1-Q3) (total): ₦9.15 billion (18.1% of the revised budget)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 17
```

## spend_quarter-04 (code_switched) ok (14.2s)

**Q:** Poultry Development Agency ta spend nawa by end of Q3 2025 against revised budget nata?

```
Poultry Development Agency ta kashe jimilla ₦6.02 miliyan daga watan Janairu zuwa Satumba 2025 (Q1-Q3). Wannan kashewar daga kasafin da aka sabunta na 2025 ne wanda jimillarsa ₦345.42 miliyan. Adadin da aka kashe shi ne na jimilla, ba albashi ko kuɗin gudanarwa kaɗai ba.

• 2025 kasafin da aka sabunta (jimilla): ₦345.42 miliyan
• 2025 aiki Janairu-Satumba / Q1-Q3 (jimilla): ₦6.02 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
```

## spend_quarter-05 (informal) ok (4.4s)

**Q:** How much did Sokoto State SME Development Agency spend by end of Q4 2024 vs its revised budget?

```
*Sokoto State SME Development Agency* (code 022205100100):
• Total: revised budget ₦2.75 billion; spent so far (Q1–Q4) ₦2.56 billion; share of the revised budget spent 93.2% (Kasafi's calculation)

📄 *Sources:* Budget Performance Report Q4 2024, p. 18
```

## spend_quarter-06 (code_switched) ok (3.4s)

**Q:** Nawa ZAKAT and Endowment Agency (WAQF) ta spend by the end of Q2 2026, against its revised budget?

```
*ZAKAT and Endowment Agency (WAQF)* (code 017200700100):
• Jimilla: kasafin da aka sabunta ₦4.17 biliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦275.18 miliyan; kason kasafin da aka sabunta da aka kashe 6.6% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 16
```

## compare-01 (code_switched) ok (4.6s)

**Q:** Kwatanta approved budget na Ministry of Lands and Housing a 2025 da 2026 fa.

```
*Min of Lands and Housing* (code 025300000000):
• Jimilla: 2025 kasafin da aka amince ₦47.46 biliyan; 2026 kasafin da aka amince ₦35.78 biliyan; bambanci -₦11.69 biliyan (-24.6%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 17
```

## compare-02 (typo) ok (3.6s)

**Q:** Comapre the Ministry of Transprot's approved budjet in 2025 and 2026.

```
*Ministry of Transport* (code 022900000000):
• Total: 2025 approved budget ₦3.65 billion; 2026 approved budget ₦50.87 billion; change +₦47.21 billion (+1292.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-03 (hausa) ok (3.0s)

**Q:** Kwatanta approved budget na Ministry of Culture & Tourism a 2025 da 2026.

```
*Ministry of Culture & Tourism* (code 023600000000):
• Jimilla: 2025 kasafin da aka amince ₦1.21 biliyan; 2026 kasafin da aka amince ₦1.42 biliyan; bambanci +₦214.73 miliyan (+17.7%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-04 (code_switched) ok (5.2s)

**Q:** Kwatanta approved budget na Ministry of Innovation and Digital Economy a 2025 da 2026 mana?

```
*Ministry of Innovation and Digital Economy* (code 027900000000):
• Jimilla: 2025 kasafin da aka amince ₦1.35 biliyan; 2026 kasafin da aka amince ₦3.59 biliyan; bambanci +₦2.24 biliyan (+166.1%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-05 (code_switched) ok (4.0s)

**Q:** Kwatanta approved budget na Ministry of Environment for 2025 da 2026 fa.

```
*Ministry of Environment* (code 053500000000):
• Jimilla: 2025 kasafin da aka amince ₦24.52 biliyan; 2026 kasafin da aka amince ₦20.77 biliyan; bambanci -₦3.75 biliyan (-15.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-06 (followup) ok (4.3s)

**Q:** Compare its approved budget in 2025 and 2026?

```
*Ministry of Youth and Sports Development* (code 051300000000):
• Total: 2025 approved budget ₦4.02 billion; 2026 approved budget ₦17.06 billion; change +₦13.03 billion (+323.8%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## share-01 (hausa) ok (4.5s)

**Q:** Kashi nawa cikin approved budget na State Newspaper Comp.(The PATH) na 2026 ne na capital?

```
*State Newspaper Comp.(The PATH)* (code 012305500100):
• Manyan ayyuka: kasafin da aka amince ₦209.00 miliyan; 69.8% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦299.58 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-02 (hausa) ok (4.5s)

**Q:** Kashi nawa na kasafin kudin POVERTY REDUCTION PROGRAMME na shekarar 2026 da aka amince da shi ne na aikin jari?

```
*POVERTY REDUCTION PROGRAMME* (code 011102000100):
• Manyan ayyuka: kasafin da aka amince ₦1.70 biliyan; 76.0% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦2.24 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-03 (template) ok (4.9s)

**Q:** What share of the Ministry of Livestocks and Fisheries Development's 2026 approved budget is capital?

```
*Ministry of Livestocks and Fisheries Development* (code 026800000000):
• Capital: approved budget ₦12.26 billion; 90.2% of its total (Kasafi's calculation)
• Total: approved budget ₦13.60 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-04 (template) ok (4.0s)

**Q:** What share of the Law Reform Commission's 2026 approved budget is capital?

```
*Law Reform Commission* (code 032600200100):
• Capital: approved budget ₦605.17 million; 69.7% of its total (Kasafi's calculation)
• Total: approved budget ₦868.16 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-05 (code_switched) ok (4.8s)

**Q:** Ministry of Innovation and Digital Economy 2026 approved budget din nan, kashi nawa ne capital?

```
*Ministry of Innovation and Digital Economy* (code 027900000000):
• Manyan ayyuka: kasafin da aka amince ₦2.75 biliyan; 76.6% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦3.59 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## share-06 (hausa) ok (5.1s)

**Q:** Kashi nawa na approved budget na 2026 na Umaru Ali Shinkafi Polytechnic Sokoto ne capital?

```
*Umaru Ali Shinkafi Polytechnic Sokoto* (code 056901800100):
• Manyan ayyuka: kasafin da aka amince ₦2.43 biliyan; 50.8% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦4.79 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 27
```

## false_premise-01 (template) ok (15.5s)

**Q:** Why did the Department of Establishment and Pensions's approved budget rise from 2025 to 2026?

```
The Department of Establishment and Pensions's approved budget did not rise from 2025 to 2026. It was ₦16.17 billion in the 2025 approved budget and ₦11.84 billion in the 2026 approved budget. The documents give the allocations only and do not state a reason.

• Department of Establishment and Pensions (ministry total including its agencies, all spending (total), code 017300000000), 2025 Approved Budget: ₦16.17 billion
• Department of Establishment and Pensions (ministry total including its agencies, all spending (total), code 017300000000), 2026 Approved Budget: ₦11.84 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-02 (followup) ok (4.5s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Office of Head of Service* (code 012500000000):
• Personnel (salaries): 2025 approved budget ₦975.99 million; 2026 approved budget ₦1.31 billion; change +₦333.08 million (+34.1%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦875.00 million; 2026 approved budget ₦1.46 billion; change +₦580.80 million (+66.4%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦1.55 billion; 2026 approved budget ₦7.67 billion; change +₦6.12 billion (+393.3%) (Kasafi's calculation)
• Total: 2025 approved budget ₦3.41 billion; 2026 approved budget ₦10.44 billion; change +₦7.03 billion (+206.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 12, 14, 16; Sokoto State FY 2026 Budget, p. 16, 19, 22, 25
```

## false_premise-03 (template) ok (4.1s)

**Q:** Why did the Ministry of Transport's approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry of Transport* (code 022900000000):
• Total: 2025 approved budget ₦3.65 billion; 2026 approved budget ₦50.87 billion; change +₦47.21 billion (+1292.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-04 (informal) ok (4.1s)

**Q:** Why'd the Ministry for Women Affairs's approved budget go up from 2025 to 2026?

```
It didn't rise: the approved budget fell from 2025 to 2026, so there is no rise to explain.
*Ministry for Women Affairs* (code 051400000000):
• Total: 2025 approved budget ₦8.44 billion; 2026 approved budget ₦7.24 billion; change -₦1.21 billion (-14.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-05 (hausa) ok (3.4s)

**Q:** Me ya sa approved budget na Ministry of Budget and Economic Planning ya ragu daga 2025 zuwa 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
*Ministry of Budget and Economic Planning* (code 023800000000):
• Albashi: 2025 kasafin da aka amince ₦146.66 miliyan; 2026 kasafin da aka amince ₦172.61 miliyan; bambanci +₦25.95 miliyan (+17.7%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦1.90 biliyan; 2026 kasafin da aka amince ₦2.92 biliyan; bambanci +₦1.03 biliyan (+54.1%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦1.98 biliyan; 2026 kasafin da aka amince ₦2.22 biliyan; bambanci +₦237.91 miliyan (+12.0%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦4.03 biliyan; 2026 kasafin da aka amince ₦5.32 biliyan; bambanci +₦1.29 biliyan (+32.0%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 13, 14, 16; Sokoto State FY 2026 Budget, shafi 17, 20, 23, 26
```

## false_premise-06 (code_switched) ok (4.3s)

**Q:** Why Ministry of Livestocks and Fisheries Development approved budget ya fadi from 2025 to 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
*Ministry of Livestocks and Fisheries Development* (code 026800000000):
• Jimilla: 2025 kasafin da aka amince ₦7.89 biliyan; 2026 kasafin da aka amince ₦13.60 biliyan; bambanci +₦5.71 biliyan (+72.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## not_in_data-01 (code_switched) ok (14.9s)

**Q:** How much be approved budget na Office of the Special Adviser on Economic Matters for 2028?

```
Babu kasafin 2028 da aka amince da shi a cikin takardun. Abin da aka buga wa Office of the Special Adviser on Economic Matters a matsayin hasashen 2028 shi ne ₦812.00 miliyan. Wannan hasashe ne, ba kasafin da aka amince da shi ba.

• Office of the Special Adviser on Economic Matters (hukuma ɗaya, duk kashe kuɗi (jimilla), code 023800700100), 2028 Out-Year Estimate: ₦812.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## not_in_data-02 (code_switched) ok (4.5s)

**Q:** Nawa Ministry of Solid Minerals and Natural Resources ta spend a Q1 2027?

```
Ba a cikin takardun ba:
• Ministry of Solid Minerals and Natural Resources 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Ministry of Solid Minerals and Natural Resources 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Ministry of Solid Minerals and Natural Resources 2027 kason kasafin da aka sabunta da aka kashe: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-03 (code_switched) ok (4.7s)

**Q:** How much ne approved budget na Nigeria CARES- Fadama Programme for 2028?

```
Ba a cikin takardun ba:
• Nigeria CARES- Fadama Programme 2028 kasafin da aka amince: kasafin 2028 ba ya cikin ɗakin karatu (kasafin da ke akwai: 2024–2026)
```

## not_in_data-04 (code_switched) ok (4.4s)

**Q:** Nawa Office of the Accountant General ya spend a Q4 2026?

```
Ba a cikin takardun ba:
• Office of the Accountant General 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Office of the Accountant General 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Office of the Accountant General 2026 kason kasafin da aka sabunta da aka kashe: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-05 (typo) ok (14.2s)

**Q:** How much is teh Ministry of Budget and Economic Planning's aproved budget for 2028?

```
⚠️ I couldn't get the document that fits best (Sokoto State Government 2028 Approved Budget). The answer below is from other documents I have, not from that one.

The 2026 budget does not show a 2028 approved budget. It shows a 2028 out-year estimate for the Ministry of Budget and Economic Planning of ₦5.85 billion as total expenditure. This is a forward estimate, not the 2028 approved budget.

• 2028 out-year estimate (total): ₦5.85 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
```

## not_in_data-06 (hausa) ok (18.0s)

**Q:** Nawa ne budget din Min of Lands and Housing da aka amince da shi na 2028?

```
⚠️ Ban samo takardar da ta fi dacewa ba (Sokoto State Government 2028 Approved Budget). Amsar da ke ƙasa daga wasu takardun da nake da su ce, ba daga waccan ba.

Ba a samu kasafin 2028 da aka amince da shi na Ministry of Lands and Housing a cikin hujjojin ba; abin da aka buga a cikin kasafin 2026 shi ne hasashen 2028 (Out-Year Estimate) wanda jimillarsa ₦21.63 biliyan ne.

• 2028 hasashen shekara mai zuwa (jimilla) a cikin kasafin 2026: ₦21.63 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## rank_lga-01 (template) ok (6.7s)

**Q:** Which 3 LGAs in Sokoto have the most IDPs?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-02 (informal) ok (5.8s)

**Q:** Top 5 LGAs in Sokoto with the most IDPs?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143
4. Tureta: 15,068
5. Shagari: 14,850

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-03 (hausa) WRONG: missing ['14,047', '8,953', '8,406', '8,277', '4,615'] (12.8s)

**Q:** Wadanne LGAs 10 ne a Sokoto da suka fi yawan IDPs?

```
📊 Alƙaluma mafi sabo: *176,099 individuals* – internally displaced persons, Sokoto State (UNHCR Nigeria Forcibly Displaced Populations Dashboard, 1 October 2026).

Daga kowace majiya:
• UNHCR Nigeria Forcibly Displaced Populations Dashboard: 176,099 individuals – internally displaced persons, Sokoto State; 1 October 2026 (Forcibly Displaced Populations 1 October 2026, shafi 1)
• IOM Displacement Tracking Matrix: 181,526 IDPs – internally displaced persons (DTM baseline, all displacement reasons), Sokoto State; Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 40,729 IDPs – in Sabon Birni, the most of its 22 LGAs (then Tangaza 19,151; Tambuwal 17,143; Tureta 15,068; Shagari 14,850); Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 88,562 IDPs – the round before, Sokoto State; Round 17, reporting date 2025-05-31 (IOM DTM API (Baseline))

Ban samu ba: Sokoto State Bureau of Statistics, JIPS, DRC, REACH, UN OCHA Nigeria.

📄 *Madogara:* Forcibly Displaced Populations 1 October 2026, shafi 1; IOM DTM API (Baseline)
```

## lookup_lga-01 (followup) WRONG: missing ['3,147'] (16.0s)

**Q:** How many IDPs are there?

```
📊 Newest figure: *176,099 individuals* – internally displaced persons, Sokoto State (UNHCR Nigeria Forcibly Displaced Populations Dashboard, 1 October 2026).

By source:
• UNHCR Nigeria Forcibly Displaced Populations Dashboard: 176,099 individuals – internally displaced persons, Sokoto State; 1 October 2026 (Forcibly Displaced Populations 1 October 2026, p. 1)
• IOM Displacement Tracking Matrix: 181,526 IDPs – internally displaced persons (DTM baseline, all displacement reasons), Sokoto State; Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 40,729 IDPs – in Sabon Birni, the most of its 22 LGAs (then Tangaza 19,151; Tambuwal 17,143; Tureta 15,068; Shagari 14,850); Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 88,562 IDPs – the round before, Sokoto State; Round 17, reporting date 2025-05-31 (IOM DTM API (Baseline))

Couldn't get: Sokoto State Bureau of Statistics, JIPS, DRC, REACH, UN OCHA Nigeria.

📄 *Sources:* Forcibly Displaced Populations 1 October 2026, p. 1; IOM DTM API (Baseline)
```

## lookup_lga-02 (hausa) WRONG: missing ['4,615'] (13.5s)

**Q:** IDPs nawa ne a Dange-Shuni LGA?

```
📊 Alƙaluma mafi sabo: *181,526 IDPs* – internally displaced persons (DTM baseline, all displacement reasons), Sokoto State (IOM Displacement Tracking Matrix, Round 18, reporting date 2025-10-31).

Daga kowace majiya:
• IOM Displacement Tracking Matrix: 181,526 IDPs – internally displaced persons (DTM baseline, all displacement reasons), Sokoto State; Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 40,729 IDPs – in Sabon Birni, the most of its 22 LGAs (then Tangaza 19,151; Tambuwal 17,143; Tureta 15,068; Shagari 14,850); Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 88,562 IDPs – the round before, Sokoto State; Round 17, reporting date 2025-05-31 (IOM DTM API (Baseline))

Ban samu ba: Sokoto State Bureau of Statistics, JIPS, DRC, REACH, UNHCR Nigeria Forcibly Displaced Populations Dashboard, UN OCHA Nigeria.

📄 *Madogara:* IOM DTM API (Baseline)
```

## lookup_lga-03 (typo) WRONG: missing ['4,252'] (11.7s)

**Q:** How mnay IDPs aer there in Kebbe LGA?

```
📊 Newest figure: *181,526 IDPs* – internally displaced persons (DTM baseline, all displacement reasons), Sokoto State (IOM Displacement Tracking Matrix, Round 18, reporting date 2025-10-31).

By source:
• IOM Displacement Tracking Matrix: 181,526 IDPs – internally displaced persons (DTM baseline, all displacement reasons), Sokoto State; Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 40,729 IDPs – in Sabon Birni, the most of its 22 LGAs (then Tangaza 19,151; Tambuwal 17,143; Tureta 15,068; Shagari 14,850); Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 88,562 IDPs – the round before, Sokoto State; Round 17, reporting date 2025-05-31 (IOM DTM API (Baseline))

Couldn't get: Sokoto State Bureau of Statistics, JIPS, DRC, REACH, UNHCR Nigeria Forcibly Displaced Populations Dashboard, UN OCHA Nigeria.

📄 *Sources:* IOM DTM API (Baseline)
```

## lookup_lga-04 (hausa) WRONG: missing ['2,274'] (14.5s)

**Q:** IDPs nawa ne a Sokoto North LGA?

```
📊 Alƙaluma mafi sabo: *2,076 households* – IDP households residing in the city, Sokoto town (Sokoto State Bureau of Statistics, JIPS, DRC, March 2026).

Daga kowace majiya:
• Sokoto State Bureau of Statistics, JIPS, DRC: 2,076 households – IDP households residing in the city, Sokoto town; March 2026 (Durable Solutions for Displacement Affected Communities in Sokoto Town, Nigeria, shafi 6)
• Sokoto State Bureau of Statistics, JIPS, DRC: over 10,700 individuals – IDP individuals residing in the city, Sokoto town; March 2026 (Durable Solutions for Displacement Affected Communities in Sokoto Town, Nigeria, shafi 6)
• Sokoto State Bureau of Statistics, JIPS, DRC: over 181,500 people – people forcibly displaced across the state, Sokoto State; March 2026 (Durable Solutions for Displacement Affected Communities in Sokoto Town, Nigeria, shafi 6)
• IOM Displacement Tracking Matrix: 181,526 IDPs – internally displaced persons (DTM baseline, all displacement reasons), Sokoto State; Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 40,729 IDPs – in Sabon Birni, the most of its 22 LGAs (then Tangaza 19,151; Tambuwal 17,143; Tureta 15,068; Shagari 14,850); Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 88,562 IDPs – the round before, Sokoto State; Round 17, reporting date 2025-05-31 (IOM DTM API (Baseline))

ℹ️ Sokoto State Bureau of Statistics, JIPS, DRC: findings cover Sokoto town only, not the whole state.

Ban samu ba: REACH, UNHCR Nigeria Forcibly Displaced Populations Dashboard, UN OCHA Nigeria.

📄 *Madogara:* Durable Solutions for Displacement Affected Communities in Sokoto Town, Nigeria, shafi 6; IOM DTM API (Baseline)
```

## lookup_lga-05 (code_switched) WRONG: missing ['14,047'] (12.4s)

**Q:** IDPs nawa ne there in Isa LGA?

```
📊 Alƙaluma mafi sabo: *181,526 IDPs* – internally displaced persons (DTM baseline, all displacement reasons), Sokoto State (IOM Displacement Tracking Matrix, Round 18, reporting date 2025-10-31).

Daga kowace majiya:
• IOM Displacement Tracking Matrix: 181,526 IDPs – internally displaced persons (DTM baseline, all displacement reasons), Sokoto State; Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 40,729 IDPs – in Sabon Birni, the most of its 22 LGAs (then Tangaza 19,151; Tambuwal 17,143; Tureta 15,068; Shagari 14,850); Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 88,562 IDPs – the round before, Sokoto State; Round 17, reporting date 2025-05-31 (IOM DTM API (Baseline))

Ban samu ba: Sokoto State Bureau of Statistics, JIPS, DRC, REACH, UNHCR Nigeria Forcibly Displaced Populations Dashboard, UN OCHA Nigeria.

📄 *Madogara:* IOM DTM API (Baseline)
```

## lookup_lga-06 (typo) ok (14.4s)

**Q:** How many IDPs aer there ni Tureta LGA?

```
📊 Newest figure: *176,099 individuals* – internally displaced persons, Sokoto State (UNHCR Nigeria Forcibly Displaced Populations Dashboard, 1 October 2026).

By source:
• UNHCR Nigeria Forcibly Displaced Populations Dashboard: 176,099 individuals – internally displaced persons, Sokoto State; 1 October 2026 (Forcibly Displaced Populations 1 October 2026, p. 1)
• IOM Displacement Tracking Matrix: 181,526 IDPs – internally displaced persons (DTM baseline, all displacement reasons), Sokoto State; Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 40,729 IDPs – in Sabon Birni, the most of its 22 LGAs (then Tangaza 19,151; Tambuwal 17,143; Tureta 15,068; Shagari 14,850); Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 88,562 IDPs – the round before, Sokoto State; Round 17, reporting date 2025-05-31 (IOM DTM API (Baseline))

Couldn't get: Sokoto State Bureau of Statistics, JIPS, DRC, REACH, UN OCHA Nigeria.

📄 *Sources:* Forcibly Displaced Populations 1 October 2026, p. 1; IOM DTM API (Baseline)
```

## trend-01 (hausa) ok (8.5s)

**Q:** Yaya adadin IDPs a Sokoto State ya canza a ƴan DTM rounds na ƙarshe?

```
Jihar Sokoto, ta zagaye:
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

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```
