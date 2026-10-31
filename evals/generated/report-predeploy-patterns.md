# Generated coverage run

Cases: cases-741719.json (draw seed 741719), form seed 1

52 cases: wrong 0 (0.0%), of them wrong agency 0 | median 5.4s

| family | wrong | of |
|---|---|---|
| compare | 0 | 6 |
| false_premise | 0 | 6 |
| lookup | 0 | 6 |
| lookup_lga | 0 | 6 |
| not_in_data | 0 | 6 |
| rank_lga | 0 | 3 |
| share | 0 | 6 |
| spend_quarter | 0 | 6 |
| split | 0 | 6 |
| trend | 0 | 1 |

| form | wrong | of |
|---|---|---|
| code_switched | 0 | 11 |
| followup | 0 | 7 |
| hausa | 0 | 12 |
| informal | 0 | 4 |
| template | 0 | 10 |
| typo | 0 | 8 |

```
Cost of this run:
  Baseten: 11 calls, 95,169 prompt tokens (17,408 cached), 4,000 output tokens -> $0.12
  Meta: 116 calls, 341,099 prompt tokens (290,158 cached), 86,602 output tokens -> $0.48
  models together: $0.59 (prices per 1M tokens from settings kasafi_price_*)
  per answer (52 answers): $0.0071, 1.4 model calls
    Meta/plan               1.00 calls  $0.0035  (50%)
    Baseten/compose         0.13 calls  $0.0015  (21%)
    Meta/read1              0.10 calls  $0.0010  (15%)
    Baseten/read2           0.08 calls  $0.0008  (11%)
    Meta/completeness       0.13 calls  $0.0003  (4%)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0) | identical calls answered from the run's cache: 0
peak memory: 263 MB
```

## lookup-01 (code_switched) ok (24.1s)

**Q:** Ministry of Science and Technology ta samu nawa a budget na 2025?

```
Ma'aikatar Kimiyya da Fasaha (Ministry of Science and Technology) ta samu jimillar ₦6.82 biliyan a matsayin kasafin 2025 da aka amince da shi (allocated). Wannan shi ne jimillar kashe kuɗi da aka ware mata a budget ɗin.

• 2025 kasafin da aka amincewa (jimilla): ₦6.82 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-02 (template) ok (17.8s)

**Q:** How much was approved for the Ministry for Women Affairs in the 2025 budget?

```
The Ministry for Women Affairs was approved a total of ₦8.44 billion in the 2025 Approved Budget. This is the total expenditure for the Ministry (including its agencies).

• 2025 approved budget (total): ₦8.44 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12
```

## lookup-03 (followup) ok (12.2s)

**Q:** How much was approved for it in the 2026 budget?

```
Law and Justice is in the 2026 approved budget. The approved total expenditure for Law and Justice in 2026 is ₦14.26 billion.

• 2026 approved budget (total): ₦14.26 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18
```

## lookup-04 (code_switched) ok (12.5s)

**Q:** How much aka approve wa Ministry of Social Welfare & Community Development for 2025 budget?

```
An ware wa Ma'aikatar Social Welfare & Community Development jimillar ₦7.08 biliyan a kasafin 2025 da aka amince da shi. Wannan jimilla ce daga teburin Total Expenditure by Administrative Classification.

• 2025 kasafin da aka amince da shi (jimilla): ₦7.08 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12
```

## lookup-05 (hausa) ok (14.9s)

**Q:** Nawa aka amince wa Ministry for Local Government and Chieftancy a kasafin kudin 2025?

```
An amince da jimilla ₦570.64 miliyan ga Ministry for Local Government and Chieftancy a kasafin kuɗin 2025 na Jihar Sokoto. Wannan ƙididdiga daga teburin Jimillar Kashe Kuɗi ne ta hanyar Rarraba Gudanarwa.

• 2025 kasafin da aka amince da shi (jimilla): ₦570.64 miliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12
```

## lookup-06 (hausa) ok (21.3s)

**Q:** Nawa aka amince wa Ministry of Education a budget na 2026?

```
An amince wa Ministry of Education (jimillar ma'aikatar da hukumominta) ₦68.95 biliyan a kasafin 2026 da aka amince da shi. Wannan jimilla ce daga jadawalin jimillar kashe kuɗi ta rabon gudanarwa.

• 2026 kasafin da aka amince da shi (jimilla): ₦68.95 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
```

## split-01 (typo) ok (7.2s)

**Q:** What are teh personnel, overhead and capial allocations of the Department for Rural Roads in 2026?

```
For Department for Rural Roads, the approved budget (salaries) is ₦28.59 million.

*Department for Rural Roads*:
• Personnel (salaries): approved budget ₦28.59 million
• Overhead (running costs): approved budget ₦133.95 million
• Capital: approved budget ₦15.47 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-02 (followup) ok (6.5s)

**Q:** And what are its personnel, overhead and capital allocations in 2026?

```
For Ministry for Religious Affairs, the approved budget (salaries) is ₦358.38 million.

*Ministry for Religious Affairs*:
• Personnel (salaries): approved budget ₦358.38 million
• Overhead (running costs): approved budget ₦4.30 billion
• Capital: approved budget ₦13.39 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-03 (template) ok (7.1s)

**Q:** What are the personnel, overhead and capital allocations of the Ministry for Home Affairs in 2026?

```
For Ministry for Home Affairs, the approved budget (salaries) is ₦2.11 billion.

*Ministry for Home Affairs*:
• Personnel (salaries): approved budget ₦2.11 billion
• Overhead (running costs): approved budget ₦1.42 billion
• Capital: approved budget ₦2.58 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-04 (typo) ok (7.4s)

**Q:** What are teh personnel, overhead and capital allocatons of the Primary School Staff Pension Board in 2026?

```
For Primary School Staff Pension Board, the approved budget (salaries) is ₦39.34 million.

*Primary School Staff Pension Board*:
• Personnel (salaries): approved budget ₦39.34 million
• Overhead (running costs): approved budget ₦21.00 million
• Capital: approved budget ₦0.00

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-05 (hausa) ok (7.5s)

**Q:** Menene kudin personnel, overhead da capital da aka ware wa Sokoto State House of Assembly a 2025?

```
Ga Sokoto State House of Assembly, kasafin da aka amince (albashi) shi ne ₦1.15 biliyan.

*Sokoto State House of Assembly*:
• Albashi: kasafin da aka amince ₦1.15 biliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦4.82 biliyan
• Manyan ayyuka: kasafin da aka amince ₦3.41 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12, 14, 15
```

## split-06 (followup) ok (7.0s)

**Q:** And what are its personnel, overhead and capital allocations in 2025?

```
For Female Education Board, the approved budget (salaries) is ₦45.35 million.

*Female Education Board*:
• Personnel (salaries): approved budget ₦45.35 million
• Overhead (running costs): approved budget ₦425.65 million
• Capital: approved budget ₦670.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## spend_quarter-01 (hausa) ok (6.8s)

**Q:** Noma Children Hospital ya kashe kudi nawa har zuwa karshen Q2 2026, idan aka kwatanta da revised budget dinsa?

```
Ga Noma Children Hospital, kasafin da aka sabunta shi ne ₦350.44 miliyan.

*Noma Children Hospital*:
• Jimilla: kasafin da aka sabunta ₦350.44 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦163.92 miliyan; kason kasafin da aka sabunta da aka kashe 46.8% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 18
```

## spend_quarter-02 (template) ok (3.9s)

**Q:** How much had the Department of Estbalishment and Pensions spent by the end of Q2 2026, against its revised budget?

```
For Department of Establishment and Pensions, the spent so far (Q1–Q2) is ₦7.07 billion.

*Department of Establishment and Pensions*:
• Total: spent so far (Q1–Q2) ₦7.07 billion; revised budget ₦11.84 billion; share of the revised budget spent 59.7% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 16
```

## spend_quarter-03 (template) ok (4.2s)

**Q:** How much had the Local Government Pension Board spent by the end of Q3 2025, against its revised budget?

```
For Local Government Pension Board, the spent so far (Q1–Q3) is ₦29.34 million.

*Local Government Pension Board*:
• Total: spent so far (Q1–Q3) ₦29.34 million; revised budget ₦407.68 million; share of the revised budget spent 7.2% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 17
```

## spend_quarter-04 (typo) ok (4.7s)

**Q:** How mcuh had teh Social Investment Programme spent by the end of Q4 2024, against its revised budget?

```
For Social Investment Programme, the revised budget is ₦303.86 million.

*Social Investment Programme*:
• Total: revised budget ₦303.86 million; spent so far (Q1–Q4) ₦303.86 million; share of the revised budget spent 100.0% (Kasafi's calculation)

📄 *Sources:* Budget Performance Report Q4 2024, p. 18
```

## spend_quarter-05 (code_switched) ok (3.9s)

**Q:** Sokoto State University ta kashe nawa by end of Q2 2026 against revised budget dinta?

```
Ga Sokoto State University, abin da aka kashe zuwa yanzu (Q1–Q2) shi ne ₦1.31 biliyan.

*Sokoto State University*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q2) ₦1.31 biliyan; kasafin da aka sabunta ₦5.71 biliyan; kason kasafin da aka sabunta da aka kashe 23.0% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 18
```

## spend_quarter-06 (hausa) ok (5.1s)

**Q:** Nawa State Agricultural Development Project ya kashe har zuwa karshen Q4 2024 idan aka kwatanta da revised budget dinsa?

```
Ga State Agricultural Development Project, kasafin da aka sabunta shi ne ₦254.88 miliyan.

*State Agricultural Development Project*:
• Jimilla: kasafin da aka sabunta ₦254.88 miliyan; abin da aka kashe zuwa yanzu (Q1–Q4) ₦242.36 miliyan; kason kasafin da aka sabunta da aka kashe 95.1% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 17
```

## compare-01 (code_switched) ok (4.5s)

**Q:** Kwatanta State Judiciary approved budget na 2025 da 2026 fa?

```
Ga State Judiciary, 2025 kasafin da aka amince shi ne ₦6.28 biliyan.

*State Judiciary*:
• Jimilla: 2025 kasafin da aka amince ₦6.28 biliyan; 2026 kasafin da aka amince ₦8.17 biliyan; bambanci +₦1.89 biliyan (+30.1%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-02 (typo) ok (4.2s)

**Q:** Comprae the Sokoto State House of Assemby's approved budget in 2025 and 2026.

```
For Sokoto State House of Assembly, the 2025 approved budget is ₦9.37 billion.

*Sokoto State House of Assembly*:
• Total: 2025 approved budget ₦9.37 billion; 2026 approved budget ₦12.26 billion; change +₦2.89 billion (+30.8%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-03 (hausa) ok (3.7s)

**Q:** Kwatanta kasafin kudin da aka amince wa Ministry of Energy and Petroleum Resources a 2025 da 2026.

```
Ga Ministry of Energy and Petroleum Resources, 2025 kasafin da aka amince shi ne ₦10.30 biliyan.

*Ministry of Energy and Petroleum Resources*:
• Jimilla: 2025 kasafin da aka amince ₦10.30 biliyan; 2026 kasafin da aka amince ₦23.33 biliyan; bambanci +₦13.04 biliyan (+126.6%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-04 (hausa) ok (4.2s)

**Q:** Kwatanta kasafin kudin Sokoto State Independent Electoral Commission da aka amince da shi a 2025 da 2026.

```
Ga Sokoto State Independent Electoral Commission, 2025 kasafin da aka amince shi ne ₦529.14 miliyan.

*Sokoto State Independent Electoral Commission*:
• Jimilla: 2025 kasafin da aka amince ₦529.14 miliyan; 2026 kasafin da aka amince ₦460.48 miliyan; bambanci -₦68.67 miliyan (-13.0%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-05 (template) ok (4.0s)

**Q:** Compare the Fiscal Responsibility Commission's approved budget in 2025 and 2026.

```
For Fiscal Responsibility Commission, the 2025 approved budget is ₦58.99 million.

*Fiscal Responsibility Commission*:
• Total: 2025 approved budget ₦58.99 million; 2026 approved budget ₦60.99 million; change +₦2.00 million (+3.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-06 (hausa) ok (4.2s)

**Q:** Kwatanta kasafin kudin Department of Establishment and Pensions da aka amince da shi a 2025 da 2026.

```
Ga Department of Establishment and Pensions, 2025 kasafin da aka amince shi ne ₦16.17 biliyan.

*Department of Establishment and Pensions*:
• Jimilla: 2025 kasafin da aka amince ₦16.17 biliyan; 2026 kasafin da aka amince ₦11.84 biliyan; bambanci -₦4.33 biliyan (-26.8%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## share-01 (code_switched) ok (6.0s)

**Q:** ZAKAT and Endowment Agency (WAQF) 2026 approved budget din, what share ne capital?

```
Ga ZAKAT and Endowment Agency (WAQF), kasafin da aka amince (manyan ayyuka) shi ne ₦2.79 biliyan.

*ZAKAT and Endowment Agency (WAQF)*:
• Manyan ayyuka: kasafin da aka amince ₦2.79 biliyan; 66.9% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦4.17 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-02 (hausa) ok (4.9s)

**Q:** Kashi nawa na approved budget na Sokoto State Housing Cooperation na 2026 ne capital?

```
Ga Sokoto State Housing Cooperation, kasafin da aka amince (manyan ayyuka) shi ne ₦330.00 miliyan.

*Sokoto State Housing Cooperation*:
• Manyan ayyuka: kasafin da aka amince ₦330.00 miliyan; 87.7% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦376.45 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 26
```

## share-03 (typo) ok (6.4s)

**Q:** What shrae of the Ministy of Budget and Economic Planning's 2026 approved budgte is capital?

```
For Ministry of Budget and Economic Planning, the approved budget (capital) is ₦2.22 billion.

*Ministry of Budget and Economic Planning*:
• Capital: approved budget ₦2.22 billion; 41.8% of its total (Kasafi's calculation)
• Total: approved budget ₦5.32 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-04 (informal) ok (3.7s)

**Q:** How much of the Ministry of Health's 2026 approved budget is capital?

```
For Ministry of Health, the approved budget (capital) is ₦104.64 billion.

*Ministry of Health*:
• Capital: approved budget ₦104.64 billion; 84.1% of its total (Kasafi's calculation)
• Total: approved budget ₦124.41 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 27
```

## share-05 (template) ok (4.6s)

**Q:** What share of the State Newspaper Comp.(The PATH)'s 2026 approved budget is capital?

```
For State Newspaper Comp.(The PATH), the approved budget (capital) is ₦209.00 million.

*State Newspaper Comp.(The PATH)*:
• Capital: approved budget ₦209.00 million; 69.8% of its total (Kasafi's calculation)
• Total: approved budget ₦299.58 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 25
```

## share-06 (code_switched) ok (4.2s)

**Q:** Ministry of Commerce and Industry 2026 approved budget din, kashi nawa ne capital?

```
Ga Ministry of Commerce and Industry, kasafin da aka amince (manyan ayyuka) shi ne ₦4.21 biliyan.

*Ministry of Commerce and Industry*:
• Manyan ayyuka: kasafin da aka amince ₦4.21 biliyan; 64.1% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦6.56 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 25
```

## false_premise-01 (informal) ok (4.3s)

**Q:** Why did Ministry of Works's approved budget go up from 2025 to 2026?

```
It didn't rise: the approved budget fell from 2025 to 2026, so there is no rise to explain.
For Ministry of Works, the 2025 approved budget is ₦59.39 billion.

*Ministry of Works*:
• Total: 2025 approved budget ₦59.39 billion; 2026 approved budget ₦59.17 billion; change -₦227.66 million (-0.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-02 (typo) ok (4.3s)

**Q:** Why did teh Ministry of Science and Technology's approved budjet fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Science and Technology, the 2025 approved budget (salaries) is ₦1.32 billion.

*Ministry of Science and Technology*:
• Personnel (salaries): 2025 approved budget ₦1.32 billion; 2026 approved budget ₦1.65 billion; change +₦334.88 million (+25.5%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦689.10 million; 2026 approved budget ₦1.01 billion; change +₦323.90 million (+47.0%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦4.81 billion; 2026 approved budget ₦9.02 billion; change +₦4.21 billion (+87.5%) (Kasafi's calculation)
• Total: 2025 approved budget ₦6.82 billion; 2026 approved budget ₦11.69 billion; change +₦4.87 billion (+71.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 13, 14, 16; Sokoto State FY 2026 Budget, p. 17, 20, 23, 26
```

## false_premise-03 (informal) ok (3.7s)

**Q:** why did Ministry of Commerce and Industry's approved budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Commerce and Industry, the 2025 approved budget (salaries) is ₦122.77 million.

*Ministry of Commerce and Industry*:
• Personnel (salaries): 2025 approved budget ₦122.77 million; 2026 approved budget ₦193.00 million; change +₦70.23 million (+57.2%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦1.04 billion; 2026 approved budget ₦2.16 billion; change +₦1.12 billion (+107.5%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦4.89 billion; 2026 approved budget ₦4.21 billion; change -₦686.27 million (-14.0%) (Kasafi's calculation)
• Total: 2025 approved budget ₦6.06 billion; 2026 approved budget ₦6.56 billion; change +₦503.51 million (+8.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 13, 14, 16; Sokoto State FY 2026 Budget, p. 17, 20, 23, 25
```

## false_premise-04 (hausa) ok (5.1s)

**Q:** Me ya sa kasafin kudin Ministry for Religious Affairs da aka amince da shi ya ragu daga 2025 zuwa 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
Ga Ministry for Religious Affairs, 2025 kasafin da aka amince shi ne ₦11.26 biliyan.

*Ministry for Religious Affairs*:
• Jimilla: 2025 kasafin da aka amince ₦11.26 biliyan; 2026 kasafin da aka amince ₦18.05 biliyan; bambanci +₦6.79 biliyan (+60.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## false_premise-05 (followup) ok (5.6s)

**Q:** Why did its approved budget rise from 2025 to 2026?

```
It didn't rise: the approved budget fell from 2025 to 2026, so there is no rise to explain.
For Min of Lands and Housing, the 2025 approved budget (salaries) is ₦313.60 million.

*Min of Lands and Housing*:
• Personnel (salaries): 2025 approved budget ₦313.60 million; 2026 approved budget ₦316.08 million; change +₦2.48 million (+0.8%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦190.70 million; 2026 approved budget ₦557.20 million; change +₦366.50 million (+192.2%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦46.96 billion; 2026 approved budget ₦34.90 billion; change -₦12.05 billion (-25.7%) (Kasafi's calculation)
• Total: 2025 approved budget ₦47.46 billion; 2026 approved budget ₦35.78 billion; change -₦11.69 billion (-24.6%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 13, 15, 16; Sokoto State FY 2026 Budget, p. 17, 20, 23, 26
```

## false_premise-06 (typo) ok (4.3s)

**Q:** Why did teh Ministry of Education's aproved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Education, the 2025 approved budget is ₦59.59 billion.

*Ministry of Education*:
• Total: 2025 approved budget ₦59.59 billion; 2026 approved budget ₦68.95 billion; change +₦9.36 billion (+15.7%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## not_in_data-01 (code_switched) ok (5.3s)

**Q:** Nawa the Primary School Staff Pension Board ta spend in Q1 2027?

```
Ba a cikin takardun ba:
• Primary School Staff Pension Board 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Primary School Staff Pension Board 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-02 (code_switched) ok (4.3s)

**Q:** Government House ta spend nawa for Q1 2027?

```
Ba a cikin takardun ba:
• Government House 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Government House 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Government House 2027 kason kasafin da aka sabunta da aka kashe: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-03 (followup) ok (5.2s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Local Government Audit 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Local Government Audit 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-04 (code_switched) ok (23.7s)

**Q:** Nawa ne approved budget na Ministry for Home Affairs for 2028?

```
⚠️ Ban samo takardar da ta fi dacewa ba (Sokoto State 2028 Approved Budget). Amsar da ke ƙasa daga wasu takardun da nake da su ce, ba daga waccan ba.

Takardar kasafin 2026 da aka bayar ba ta ƙunshi ƙididdigar approved budget na 2028 ba. Abin da ake da shi shi ne ƙiyasin shekarar 2028 (Out-Year Estimate) na Ministry for Home Affairs: ₦2.77 biliyan.

• 2028 ƙiyasin shekaru masu zuwa (jimilla): ₦2.77 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16
```

## not_in_data-05 (followup) ok (4.6s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Rural Water and Sanitation Agency 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Rural Water and Sanitation Agency 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Rural Water and Sanitation Agency 2027 share of the revised budget spent: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-06 (followup) ok (5.6s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Shehu Shagari University of Education 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Shehu Shagari University of Education 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## rank_lga-01 (code_switched) ok (7.5s)

**Q:** Waɗanne 3 LGAs ne have most IDPs a Sokoto?

```
Ta ƙaramar hukuma (22), mafi yawa:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-02 (informal) ok (6.0s)

**Q:** Top 10 LGAs with most IDPs in Sokoto?

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

## rank_lga-03 (template) ok (5.7s)

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

## lookup_lga-01 (template) ok (6.0s)

**Q:** How many IDPs are there in Wamako LGA?

```
IOM DTM counts *4,026* IDPs in Wamakko (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (template) ok (4.4s)

**Q:** How many IDPs are there in Tangaza LGA?

```
IOM DTM counts *19,151* IDPs in Tangaza (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-03 (typo) ok (6.5s)

**Q:** How mnay IDPs aer there in Isa LGA?

```
IOM DTM counts *14,047* IDPs in Isa (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-04 (hausa) ok (5.7s)

**Q:** IDPs nawa ne a Goronyo LGA?

```
IOM DTM ta ƙidaya *1,926* 'yan gudun hijira a Goronyo (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-05 (code_switched) ok (7.8s)

**Q:** How many IDPs ne a Illela LGA?

```
IOM DTM ta ƙidaya *8,953* 'yan gudun hijira a Illela (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-06 (hausa) ok (5.5s)

**Q:** IDPs guda nawa ne suke a Tureta LGA?

```
IOM DTM ta ƙidaya *15,068* 'yan gudun hijira a Tureta (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## trend-01 (template) ok (5.0s)

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
