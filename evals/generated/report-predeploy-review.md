# Generated coverage run

Cases: cases-869187.json (draw seed 869187), form seed 1

52 cases: wrong 2 (3.8%), of them wrong agency 0 | median 4.3s

| family | wrong | of |
|---|---|---|
| compare | 0 | 6 |
| false_premise | 2 | 6 |
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
| hausa | 1 | 12 |
| informal | 1 | 4 |
| template | 0 | 10 |
| typo | 0 | 8 |

```
Cost of this run:
  Baseten: 19 calls, 172,006 prompt tokens (58,624 cached), 8,191 output tokens -> $0.19
  Meta: 114 calls, 365,196 prompt tokens (296,445 cached), 84,249 output tokens -> $0.49
  models together: $0.67 (prices per 1M tokens from settings kasafi_price_*)
  per answer (52 answers): $0.0088, 1.6 model calls
    Meta/plan               1.00 calls  $0.0034  (39%)
    Baseten/compose         0.19 calls  $0.0022  (25%)
    Meta/read1              0.15 calls  $0.0016  (19%)
    Baseten/read2           0.17 calls  $0.0014  (16%)
    Meta/completeness       0.04 calls  $0.0001  (1%)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0) | identical calls answered from the run's cache: 0
peak memory: 389 MB
```

## lookup-01 (code_switched) ok (8.3s)

**Q:** Nawa aka approve wa Office of Auditor General a 2025 budget?

```
An ware jimillar ₦542.84 miliyan ga Office of Auditor General a kasafin kuɗi na 2025 da aka amince da shi. Wannan adadi shi ne jimillar kashe kuɗi da aka amince da ita kamar yadda ta bayyana a jadawalin kashe kuɗin gwamnati ta hanyar ma'aikata.

• 2025 kasafin da aka amince dashi (jimilla): ₦542.84 miliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-02 (template) ok (10.3s)

**Q:** How much was approved for the Ministry for Skills Acquisition and Entrepreneurship Development in the 2026 budget?

```
The 2026 approved budget for the Ministry for Skills Acquisition and Entrepreneurship Development is ₦1.37 billion. It is the total allocation shown in the Total Expenditure by Administrative Classification table.

• 2026 approved budget (total): ₦1.37 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18
```

## lookup-03 (followup) ok (5.7s)

**Q:** How much was approved for it in the 2026 budget?

```
The Ministry of Science and Technology was approved ₦11.69 billion in the 2026 approved budget. This is the ministry's total, its agencies included.

• Ministry of Science and Technology, 2026 Approved Budget: ₦11.69 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## lookup-04 (code_switched) ok (9.1s)

**Q:** How much aka approve wa Ministry of Environment a budget na 2025?

```
An amince da jimillar ₦24.52 biliyan ga Ma'aikatar Muhalli a kasafin kuɗi na 2025. Wannan adadi ne daga teburin Jimillar Kashe Kuɗi ta Rarraba Gudanarwa.

• 2025 kasafin da aka amince da shi (jimilla): ₦24.52 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12
```

## lookup-05 (hausa) ok (7.1s)

**Q:** Nawa aka amince wa Sokoto State House of Assembly a kasafin kudin 2025?

```
An amince wa Sokoto State House of Assembly jimillar ₦9.37 biliyan a kasafin kuɗin 2025 da aka amince. Wannan ita ce jimillar kashe kuɗi (ministry total) da aka amince.

• Sokoto State House of Assembly, 2025 Approved Budget: ₦9.37 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## lookup-06 (hausa) ok (9.2s)

**Q:** Nawa aka amince wa Ministry of Education a kasafin kudin 2025?

```
An amince wa Ministry of Education jimilla na ₦59.59 biliyan a kasafin kuɗi na 2025 da aka amince da shi. Wannan adadi daga jedawalin Total Expenditure by Administrative Classification ne, wanda ya haɗa da ma'aikatar da hukumominta.

• 2025 kasafin da aka amince da shi (jimilla): ₦59.59 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12
```

## split-01 (typo) ok (3.3s)

**Q:** Waht are the personel, overhead and capial allocations of the Sokoto State Scholarship and Students Matters in 2025?

```
For Sokoto State Scholarship and Students Matters, the approved budget (salaries) is ₦39.78 million.

*Sokoto State Scholarship and Students Matters*:
• Personnel (salaries): approved budget ₦39.78 million
• Overhead (running costs): approved budget ₦4.48 billion
• Capital: approved budget ₦47.09 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-02 (followup) ok (4.2s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
For Sokoto State Independent Electoral Commission, the approved budget (salaries) is ₦128.76 million.

*Sokoto State Independent Electoral Commission*:
• Personnel (salaries): approved budget ₦128.76 million
• Overhead (running costs): approved budget ₦106.00 million
• Capital: approved budget ₦225.71 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-03 (template) ok (4.3s)

**Q:** What are the personnel, overhead and capital allocations of the State High Court in 2025?

```
For State High Court, the approved budget (salaries) is ₦540.00 million.

*State High Court*:
• Personnel (salaries): approved budget ₦540.00 million
• Overhead (running costs): approved budget ₦1.19 billion
• Capital: approved budget ₦1.79 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-04 (typo) ok (3.6s)

**Q:** What are the personnel, overhed and capital allcations of the State Newspaper Comp.(The PATH) in 2025?

```
For State Newspaper Comp.(The PATH), the approved budget (salaries) is ₦83.08 million.

*State Newspaper Comp.(The PATH)*:
• Personnel (salaries): approved budget ₦83.08 million
• Overhead (running costs): approved budget ₦18.00 million
• Capital: approved budget ₦209.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 14, 16
```

## split-05 (hausa) ok (3.3s)

**Q:** Menene kason personnel, overhead da capital da aka ware wa Ministry of Energy and Petroleum Resources a 2026?

```
Ga Ministry of Energy and Petroleum Resources, kasafin da aka amince (albashi) shi ne ₦147.61 miliyan.

*Ministry of Energy and Petroleum Resources*:
• Albashi: kasafin da aka amince ₦147.61 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦711.31 miliyan
• Manyan ayyuka: kasafin da aka amince ₦22.47 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 20, 23, 26
```

## split-06 (followup) ok (3.7s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
For Ministry of Justice, the approved budget (salaries) is ₦864.15 million.

*Ministry of Justice*:
• Personnel (salaries): approved budget ₦864.15 million
• Overhead (running costs): approved budget ₦1.52 billion
• Capital: approved budget ₦3.71 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 24, 26
```

## spend_quarter-01 (hausa) ok (3.7s)

**Q:** Nawa Shehu Shagari University of Education ta kashe har zuwa karshen Q2 2026, idan aka kwatanta da revised budget nata?

```
Ga Shehu Shagari University of Education, abin da aka kashe zuwa yanzu (Q1–Q2) shi ne ₦350.75 miliyan.

*Shehu Shagari University of Education*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q2) ₦350.75 miliyan; kasafin da aka sabunta ₦6.98 biliyan; kason kasafin da aka sabunta da aka kashe 5.0% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 18
```

## spend_quarter-02 (template) ok (2.8s)

**Q:** How much had the Ministry of Health spent by the end of Q3 2025, against its revised budget?

```
For Ministry of Health, the spent so far (Q1–Q3) is ₦14.06 billion.

*Ministry of Health*:
• Total: spent so far (Q1–Q3) ₦14.06 billion; revised budget ₦46.37 billion; share of the revised budget spent 30.3% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 19
```

## spend_quarter-03 (template) ok (3.5s)

**Q:** How much had the Arabic and Islamic Education Board spent by the end of Q2 2026, against its revised budget?

```
For Arabic and Islamic Education Board, the spent so far (Q1–Q2) is ₦882.10 million.

*Arabic and Islamic Education Board*:
• Total: spent so far (Q1–Q2) ₦882.10 million; revised budget ₦3.16 billion; share of the revised budget spent 27.9% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 17
```

## spend_quarter-04 (typo) ok (3.6s)

**Q:** How much had the JUDICIAL SERVICE COMMISSION spent by the enf of Q2 2026, agianst its revised budget?

```
For JUDICIAL SERVICE COMMISSION, the revised budget is ₦556.51 million.

*JUDICIAL SERVICE COMMISSION*:
• Total: revised budget ₦556.51 million; spent so far (Q1–Q2) ₦76.97 million; share of the revised budget spent 13.8% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 17
```

## spend_quarter-05 (code_switched) ok (3.5s)

**Q:** Department for Rural Roads ta spend nawa by end of Q2 2026 against revised budget dinta?

```
Ga Department for Rural Roads, abin da aka kashe zuwa yanzu (Q1–Q2) shi ne ₦7.03 biliyan.

*Department for Rural Roads*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q2) ₦7.03 biliyan; kasafin da aka sabunta ₦14.63 biliyan; kason kasafin da aka sabunta da aka kashe 48.0% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 16
```

## spend_quarter-06 (hausa) ok (3.6s)

**Q:** Nawa Min of Lands and Housing ta kashe har zuwa karshen Q2 2026, idan aka kwatanta da revised budget dinta?

```
Ga Min of Lands and Housing, kasafin da aka sabunta shi ne ₦42.63 biliyan.

*Min of Lands and Housing*:
• Jimilla: kasafin da aka sabunta ₦42.63 biliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦13.72 biliyan; kason kasafin da aka sabunta da aka kashe 32.2% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 17
```

## compare-01 (code_switched) ok (4.8s)

**Q:** Kwatanta approved budget na Sokoto State Independent Electoral Commission a 2025 da 2026.

```
Ga Sokoto State Independent Electoral Commission, 2025 kasafin da aka amince shi ne ₦529.14 miliyan.

*Sokoto State Independent Electoral Commission*:
• Jimilla: 2025 kasafin da aka amince ₦529.14 miliyan; 2026 kasafin da aka amince ₦460.48 miliyan; bambanci -₦68.67 miliyan (-13.0%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-02 (typo) ok (2.9s)

**Q:** Comapre the Ministry of Scince and Technology's aproved budget in 2025 and 2026.

```
For Ministry of Science and Technology, the 2025 approved budget is ₦6.82 billion.

*Ministry of Science and Technology*:
• Total: 2025 approved budget ₦6.82 billion; 2026 approved budget ₦11.69 billion; change +₦4.87 billion (+71.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-03 (hausa) ok (4.3s)

**Q:** Kwatanta approved budget ɗin Ministry for Religious Affairs na 2025 da na 2026.

```
Ga Ministry for Religious Affairs, 2025 kasafin da aka amince shi ne ₦11.26 biliyan.

*Ministry for Religious Affairs*:
• Jimilla: 2025 kasafin da aka amince ₦11.26 biliyan; 2026 kasafin da aka amince ₦18.05 biliyan; bambanci +₦6.79 biliyan (+60.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-04 (hausa) ok (3.6s)

**Q:** Kwatanta budget din Ministry of Water Resources da aka amince da shi a 2025 da 2026.

```
Ga Ministry of Water Resources, 2025 kasafin da aka amince shi ne ₦20.32 biliyan.

*Ministry of Water Resources*:
• Jimilla: 2025 kasafin da aka amince ₦20.32 biliyan; 2026 kasafin da aka amince ₦44.99 biliyan; bambanci +₦24.67 biliyan (+121.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-05 (template) ok (3.1s)

**Q:** Compare the Ministry of Social Welfare & Community Development's approved budget in 2025 and 2026.

```
For Ministry of Social Welfare & Community Development, the 2025 approved budget is ₦7.08 billion.

*Ministry of Social Welfare & Community Development*:
• Total: 2025 approved budget ₦7.08 billion; 2026 approved budget ₦5.11 billion; change -₦1.97 billion (-27.8%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 19
```

## compare-06 (hausa) ok (3.5s)

**Q:** Kwatanta approved budget na Ministry of Education a 2025 da 2026.

```
Ga Ministry of Education, 2025 kasafin da aka amince shi ne ₦59.59 biliyan.

*Ministry of Education*:
• Jimilla: 2025 kasafin da aka amince ₦59.59 biliyan; 2026 kasafin da aka amince ₦68.95 biliyan; bambanci +₦9.36 biliyan (+15.7%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## share-01 (code_switched) ok (3.0s)

**Q:** Approved budget na Commodity Board na 2026, kashi nawa ne capital?

```
Ga Commodity Board, kasafin da aka amince (manyan ayyuka) shi ne ₦650.00 miliyan.

*Commodity Board*:
• Manyan ayyuka: kasafin da aka amince ₦650.00 miliyan; 96.4% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦673.97 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## share-02 (hausa) ok (3.9s)

**Q:** Kashi nawa na kasafin kudin Department for Rural Water na 2026 da aka amince da shi ne na capital?

```
Ga Department for Rural Water, kasafin da aka amince (manyan ayyuka) shi ne ₦3.21 biliyan.

*Department for Rural Water*:
• Manyan ayyuka: kasafin da aka amince ₦3.21 biliyan; 88.9% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦3.62 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## share-03 (typo) ok (3.9s)

**Q:** What sahre of the Agnecy for Persons Living With Disabilities's 2026 approved budget is captial?

```
For Agency for Persons Living With Disabilities, the approved budget (capital) is ₦1.24 billion.

*Agency for Persons Living With Disabilities*:
• Capital: approved budget ₦1.24 billion; 40.4% of its total (Kasafi's calculation)
• Total: approved budget ₦3.07 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-04 (informal) ok (3.1s)

**Q:** What's the capital share of Ministry for Religious Affairs's 2026 approved budget?

```
For Ministry for Religious Affairs, the approved budget (capital) is ₦13.39 billion.

*Ministry for Religious Affairs*:
• Capital: approved budget ₦13.39 billion; 74.2% of its total (Kasafi's calculation)
• Total: approved budget ₦18.05 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 25
```

## share-05 (template) ok (3.2s)

**Q:** What share of the Female Education Board's 2026 approved budget is capital?

```
For Female Education Board, the approved budget (capital) is ₦650.00 million.

*Female Education Board*:
• Capital: approved budget ₦650.00 million; 56.1% of its total (Kasafi's calculation)
• Total: approved budget ₦1.16 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 27
```

## share-06 (code_switched) ok (3.6s)

**Q:** Approved budget na Ministry of Culture & Tourism na 2026, what share is capital?

```
Ga Ministry of Culture & Tourism, kasafin da aka amince (manyan ayyuka) shi ne ₦788.59 miliyan.

*Ministry of Culture & Tourism*:
• Manyan ayyuka: kasafin da aka amince ₦788.59 miliyan; 55.3% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦1.42 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## false_premise-01 (informal) WRONG: didn't correct a premise the figures contradict (13.1s)

**Q:** Why'd Government House's budget drop from 2025 to 2026?

```
_Assumption: used approved budgets for 2025 and 2026 for comparison._

The documents don't explain a drop, and they don't show one. Government House's approved total was ₦14.03 billion in 2025 and ₦18.53 billion in 2026, which is higher in 2026. The budgets don't give reasons for changes to this line.

• 2025 approved budget (total): ₦14.03 billion
• 2026 approved budget (total): ₦18.53 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## false_premise-02 (typo) ok (3.2s)

**Q:** Why did teh Ministry for Local Government and Chieftancy's approved budget fall form 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry for Local Government and Chieftancy, the 2025 approved budget is ₦570.64 million.

*Ministry for Local Government and Chieftancy*:
• Total: 2025 approved budget ₦570.64 million; 2026 approved budget ₦1.36 billion; change +₦788.43 million (+138.2%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 19
```

## false_premise-03 (informal) ok (3.8s)

**Q:** Why did Ministry of Lands and Housing's approved budget go up from 2025 to 2026?

```
It didn't rise: the approved budget fell from 2025 to 2026, so there is no rise to explain.
For Min of Lands and Housing, the 2025 approved budget is ₦47.46 billion.

*Min of Lands and Housing*:
• Total: 2025 approved budget ₦47.46 billion; 2026 approved budget ₦35.78 billion; change -₦11.69 billion (-24.6%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-04 (hausa) WRONG: missing ['9,371,828,223.24', '12,257,369,417.24'] (16.1s)

**Q:** Me ya sa kasafin kudin da Sokoto State House of Assembly ta amince da shi ya ragu daga 2025 zuwa 2026?

```
Kasafin kudin da aka amince da shi bai ragu ba daga 2025 zuwa 2026. A 2025 jimillar kashe kudi da aka amince da shi ₦526.88 biliyan, a 2026 kuma ₦758.70 biliyan. Takardun kasafin kudi lambobi kawai suke buga wa, ba su bayyana dalilin sauyin ba, don haka babu raguwa da za a bayyana dalilinta. 44.0% (lissafin Kasafi).

• Total Expenditure, 2025 Approved Budget: ₦526.88 biliyan
• Total Expenditure, 2026 Approved Budget: ₦758.70 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 1; Sokoto State FY 2026 Budget, shafi 1
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## false_premise-05 (followup) ok (3.4s)

**Q:** Why did its approved budget rise from 2025 to 2026?

```
It didn't rise: the approved budget fell from 2025 to 2026, so there is no rise to explain.
For Ministry of Finance, the 2025 approved budget is ₦47.75 billion.

*Ministry of Finance*:
• Total: 2025 approved budget ₦47.75 billion; 2026 approved budget ₦40.27 billion; change -₦7.47 billion (-15.7%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-06 (typo) ok (3.2s)

**Q:** Why did the Civil Servise Commission's approved budjet fall form 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Civil Service Commission, the 2025 approved budget is ₦254.99 million.

*Civil Service Commission*:
• Total: 2025 approved budget ₦254.99 million; 2026 approved budget ₦403.14 million; change +₦148.15 million (+58.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## not_in_data-01 (code_switched) ok (12.9s)

**Q:** Nawa ne approved budget na Ministry of Innovation and Digital Economy for 2028?

```
⚠️ Ban samo takardar da ta fi dacewa ba (Sokoto State Government 2028 Approved Budget). Amsar da ke ƙasa daga wasu takardun da nake da su ce, ba daga waccan ba.

Ba a buga kasafin da aka amince da shi na 2028 a cikin waɗannan takardun ba. Abin da aka buga a matsayin hasashen 2028 na Ma'aikatar Innovation and Digital Economy (jimilla) shi ne ₦3.34 biliyan. Wannan hasashe ne daga kasafin 2026 da aka amince da shi, ba kasafin 2028 da aka amince da shi ba.

• 2028 hasashen shekara mai zuwa (jimilla) na Ma'aikatar Innovation and Digital Economy: ₦3.34 biliyan
• 2026 kasafin da aka amince da shi (jimilla) na ma'aikatar: ₦3.59 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## not_in_data-02 (code_switched) ok (4.5s)

**Q:** Office of the Accountant General ta spend nawa for Q1 2027?

```
Ba a cikin takardun ba:
• Office of the Accountant General 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Office of the Accountant General 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-03 (followup) ok (3.8s)

**Q:** How much did it spend in Q4 2026?

```
Not in the documents:
• College of Nursing Sciences 2026 spent in Q4: the latest implementation report is Q2 2026
• College of Nursing Sciences 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
```

## not_in_data-04 (code_switched) ok (12.4s)

**Q:** Nawa ne approved budget din Ministry of Energy and Petroleum Resources for 2028?

```
⚠️ Ban samo takardar da ta fi dacewa ba (Sokoto State Approved Budget 2028). Amsar da ke ƙasa daga wasu takardun da nake da su ce, ba daga waccan ba.

Takardar kasafin 2026 da aka bayar ba ta ƙunshi approved budget na 2028 ba. Abin da aka buga shi ne 2028 Out-Year Estimate (kiyasi) na Ministry of Energy and Petroleum Resources, wanda jimillarsa ₦30.52 biliyan ce a teburin jimillar kashe kuɗi. Wannan kiyasi ne, ba kasafin da aka amince da shi na 2028 ba.

• 2028 (kiyasi, jimilla): ₦30.52 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## not_in_data-05 (followup) ok (4.4s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Department of Establishment and Pensions 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Department of Establishment and Pensions 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-06 (followup) ok (4.6s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Ministry of Youth and Sports Development 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Ministry of Youth and Sports Development 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## rank_lga-01 (code_switched) ok (5.1s)

**Q:** Wadanne 5 LGAs ne in Sokoto have the most IDPs?

```
Ta ƙaramar hukuma (22), mafi yawa:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143
4. Tureta: 15,068
5. Shagari: 14,850

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-02 (informal) ok (5.0s)

**Q:** Which 10 LGAs in Sokoto have most IDPs?

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

## rank_lga-03 (template) ok (4.3s)

**Q:** Which 3 LGAs in Sokoto have the most IDPs?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-01 (template) ok (5.6s)

**Q:** How many IDPs are there in Goronyo LGA?

```
IOM DTM counts *1,926* IDPs in Goronyo (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (template) ok (5.1s)

**Q:** How many IDPs are there in Illela LGA?

```
IOM DTM counts *8,953* IDPs in Illela (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-03 (typo) ok (4.7s)

**Q:** How many IDPs aer there ni Sokoto South LGA?

```
IOM DTM counts *4,486* IDPs in Sokoto South (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-04 (hausa) ok (5.7s)

**Q:** IDPs guda nawa ne a Gada LGA?

```
IOM DTM ta ƙidaya *1,014* 'yan gudun hijira a Gada (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-05 (code_switched) ok (4.8s)

**Q:** How many IDPs suke a Sokoto North LGA?

```
IOM DTM ta ƙidaya *2,274* 'yan gudun hijira a Sokoto North (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-06 (hausa) ok (4.5s)

**Q:** IDPs nawa ne a Bodinga LGA?

```
IOM DTM ta ƙidaya *1,990* 'yan gudun hijira a Bodinga (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## trend-01 (template) ok (4.9s)

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
