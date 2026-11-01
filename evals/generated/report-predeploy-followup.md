# Generated coverage run

Cases: cases-435983.json (draw seed 435983), form seed 1

52 cases: wrong 1 (1.9%), of them wrong agency 0 | median 4.6s

| family | wrong | of |
|---|---|---|
| compare | 0 | 6 |
| false_premise | 0 | 6 |
| lookup | 0 | 6 |
| lookup_lga | 0 | 6 |
| not_in_data | 1 | 6 |
| rank_lga | 0 | 3 |
| share | 0 | 6 |
| spend_quarter | 0 | 6 |
| split | 0 | 6 |
| trend | 0 | 1 |

| form | wrong | of |
|---|---|---|
| code_switched | 1 | 11 |
| followup | 0 | 6 |
| hausa | 0 | 12 |
| informal | 0 | 4 |
| template | 0 | 11 |
| typo | 0 | 8 |

```
Cost of this run:
  Baseten: 19 calls, 159,670 prompt tokens (56,704 cached), 8,104 output tokens -> $0.17
  Meta: 117 calls, 380,895 prompt tokens (282,997 cached), 85,714 output tokens -> $0.53
  models together: $0.70 (prices per 1M tokens from settings kasafi_price_*)
  per answer (52 answers): $0.0092, 1.6 model calls
    Meta/plan               1.00 calls  $0.0037  (41%)
    Baseten/compose         0.21 calls  $0.0021  (23%)
    Meta/read1              0.19 calls  $0.0020  (22%)
    Baseten/read2           0.15 calls  $0.0012  (13%)
    Meta/completeness       0.06 calls  $0.0001  (1%)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0) | identical calls answered from the run's cache: 0
peak memory: 390 MB
```

## lookup-01 (code_switched) ok (10.5s)

**Q:** How much aka approve wa State Judiciary a 2024 budget?

```
An amince da jimilla na ₦7.49 biliyan ga State Judiciary a cikin kasafin 2024 da aka amince da shi. Wannan adadi na jimilla ne daga jadawalin Kashe Kuɗi Ta Rarraba Aiki-Gwamnati.

• 2024 kasafin da aka amince da shi (jimilla): ₦7.49 biliyan

📄 *Madogara:* Sokoto State Government 2024 Approved Budget, shafi 44
```

## lookup-02 (template) ok (6.7s)

**Q:** How much was approved for the Local Government Service Commission in the 2025 budget?

```
₦555.67 million was approved for the Local Government Service Commission in the 2025 budget. This is the total expenditure for the Commission including its agencies.

• 2025 approved budget (total): ₦555.67 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11
```

## lookup-03 (followup) ok (6.2s)

**Q:** How much was approved for it in the 2025 budget?

```
The Department of Establishment and Pensions was approved ₦16.17 billion in the 2025 approved budget. This is the approved (budgeted) allocation.

• Department of Establishment and Pensions, 2025 Approved Budget: ₦16.17 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## lookup-04 (code_switched) ok (6.9s)

**Q:** Nawa aka approve wa Ministry of Energy and Petroleum Resources a 2026 budget?

```
An amince da jimilla na kasafin kuɗi ₦23.33 biliyan ga Ministry of Energy and Petroleum Resources a kasafin 2026 da aka amince da shi (jimilla).

• 2026 kasafin da aka amince da shi (jimilla): ₦23.33 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## lookup-05 (hausa) ok (9.2s)

**Q:** Nawa aka amince wa Ministry of Innovation and Digital Economy a kasafin kudin 2025?

```
An amince wa Ma'aikatar Innovation and Digital Economy jimilla ₦1.35 biliyan a kasafin kuɗin 2025 da aka amince wa. Wannan shi ne jimillar kuɗin da aka ware wa ma'aikatar a matsayin kasafin da aka amince wa na 2025.

• 2025 kasafin da aka amince wa (jimilla): ₦1.35 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-06 (hausa) ok (7.4s)

**Q:** Nawa aka ware wa Government House a budget na 2025?

```
A budget na 2025 da aka amince, an ware wa Government House jimilla ₦14.03 biliyan. Wannan shi ne kasafin da aka ware (allocated), ba kashewa ba.

• 2025 budget da aka amince (jimilla): ₦14.03 biliyan
• 2025 personnel (albashi) a ciki: ₦353.01 miliyan
• 2025 other recurrent a ciki: ₦9.68 biliyan
• 2025 capital a ciki: ₦3.99 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 2, 11
```

## split-01 (typo) ok (3.8s)

**Q:** What are teh personnel, overhead nad capital allocations of the Water Board in 2025?

```
For Water Board, the approved budget (salaries) is ₦604.38 million.

*Water Board*:
• Personnel (salaries): approved budget ₦604.38 million
• Overhead (running costs): approved budget ₦784.14 million
• Capital: approved budget ₦11.45 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-02 (template) ok (4.4s)

**Q:** What are the personnel, overhead and capital allocations of the State college of basic and remedial studies in 2025?

```
For State college of basic and remedial studies, the approved budget (salaries) is ₦233.11 million.

*State college of basic and remedial studies*:
• Personnel (salaries): approved budget ₦233.11 million
• Overhead (running costs): approved budget ₦23.93 million
• Capital: approved budget ₦1.60 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-03 (template) ok (4.7s)

**Q:** What are the personnel, overhead and capital allocations of the Pilgrims Welfare Agency in 2025?

```
For Pilgrims Welfare Agency, the approved budget (salaries) is ₦35.52 million.

*Pilgrims Welfare Agency*:
• Personnel (salaries): approved budget ₦35.52 million
• Overhead (running costs): approved budget ₦3.97 billion
• Capital: approved budget ₦1.10 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 14, 15
```

## split-04 (typo) ok (4.3s)

**Q:** What are teh personnel, overhead and capital alocations of the Livestock Development Programme in 2025?

```
For Livestock Development Programme, the approved budget (salaries) is ₦8.57 million.

*Livestock Development Programme*:
• Personnel (salaries): approved budget ₦8.57 million
• Overhead (running costs): approved budget ₦20.30 million
• Capital: approved budget ₦272.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-05 (hausa) ok (4.4s)

**Q:** Menene personnel, overhead da capital allocations na Sokoto Central Market a 2025?

```
Ga Sokoto Central Market, kasafin da aka amince (albashi) shi ne ₦20.23 miliyan.

*Sokoto Central Market*:
• Albashi: kasafin da aka amince ₦20.23 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦43.50 miliyan
• Manyan ayyuka: kasafin da aka amince ₦75.00 miliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 13, 14, 16
```

## split-06 (followup) ok (3.9s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
For Ministry for Basic Education, the approved budget (salaries) is ₦1.18 billion.

*Ministry for Basic Education*:
• Personnel (salaries): approved budget ₦1.18 billion
• Overhead (running costs): approved budget ₦4.92 billion
• Capital: approved budget ₦29.25 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## spend_quarter-01 (hausa) ok (3.7s)

**Q:** Nawa Ministry of Finance ta kashe har zuwa karshen Q4 2024, idan aka kwatanta da revised budget dinta?

```
Ga Ministry of Finance, abin da aka kashe zuwa yanzu (Q1–Q4) shi ne ₦26.11 biliyan.

*Ministry of Finance*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q4) ₦26.11 biliyan; kasafin da aka sabunta ₦30.06 biliyan; kason kasafin da aka sabunta da aka kashe 86.9% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 17
```

## spend_quarter-02 (template) ok (3.4s)

**Q:** How much had the Waziri Junaidu History and Culture Bureau spent by the end of Q2 2026, against its revised budget?

```
For Waziri Junaidu History and Culture Bureau, the spent so far (Q1–Q2) is ₦60.56 million.

*Waziri Junaidu History and Culture Bureau*:
• Total: spent so far (Q1–Q2) ₦60.56 million; revised budget ₦102.71 million

📄 *Sources:* Budget Implementation Report Q2 2026, p. 16
```

## spend_quarter-03 (template) ok (9.8s)

**Q:** How much had the UNDP spent by the end of Q4 2024, against its revised budget?

```
UNDP's 2024 revised budget was ₦5.00 million. By the end of Q4 2024 it had spent 0.00.

• UNDP, 2024 Revised Budget: ₦5.00 million
• UNDP, 2024 Performance Year to Date (Q1-Q4): 0.00

📄 *Sources:* Budget Performance Report Q4 2024, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## spend_quarter-04 (typo) ok (4.6s)

**Q:** How much had teh Office of the Special Adviser on Economic Matters spent by the end of Q3 2025, against its revised budjet?

```
For Office of the Special Adviser on Economic Matters, the spent so far (Q1–Q3) is ₦120.00 million.

*Office of the Special Adviser on Economic Matters*:
• Total: spent so far (Q1–Q3) ₦120.00 million; revised budget ₦805.00 million; share of the revised budget spent 14.9% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## spend_quarter-05 (code_switched) ok (3.9s)

**Q:** Ministry of Transport ta spend nawa by end of Q3 2025 against revised budget dinta?

```
Ga Ministry of Transport, kasafin da aka sabunta shi ne ₦36.05 biliyan.

*Ministry of Transport*:
• Jimilla: kasafin da aka sabunta ₦36.05 biliyan; abin da aka kashe zuwa yanzu (Q1–Q3) ₦12.44 biliyan; kason kasafin da aka sabunta da aka kashe 34.5% (lissafin Kasafi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 18
```

## spend_quarter-06 (hausa) ok (5.1s)

**Q:** Nawa Local Government Pension Board ta kashe har karshen Q4 2024, idan aka kwatanta da revised budget nata?

```
Ga Local Government Pension Board, abin da aka kashe zuwa yanzu (Q1–Q4) shi ne ₦35.31 miliyan.

*Local Government Pension Board*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q4) ₦35.31 miliyan; kasafin da aka sabunta ₦57.68 miliyan; kason kasafin da aka sabunta da aka kashe 61.2% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 17
```

## compare-01 (code_switched) ok (9.1s)

**Q:** Kwatanta approved budget na Law and Justice for 2025 da 2026

```
Kasafin da aka amince da shi na Law and Justice ya karu daga shekarar 2025 zuwa 2026. A 2025 jimillar kasafin da aka amince da shi ita ce ₦10.74 biliyan, sai a 2026 ta koma ₦14.26 biliyan.

• 2025 approved budget (jimilla): ₦10.74 biliyan
• 2026 approved budget (jimilla): ₦14.26 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-02 (typo) ok (9.0s)

**Q:** Comapre the Econmoic Sector's aproved budget in 2025 and 2026.

```
The Economic Sector's approved budget (total) was ₦237.36 billion in 2025 and ₦316.04 billion in 2026. Both figures are the allocated totals from the Total Expenditure by Administrative Classification tables.

• 2025 approved budget (total): ₦237.36 billion
• 2026 approved budget (total): ₦316.04 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-03 (hausa) ok (3.0s)

**Q:** Kwatanta approved budget na Civil Service Commission a 2025 da 2026.

```
Ga Civil Service Commission, 2025 kasafin da aka amince shi ne ₦254.99 miliyan.

*Civil Service Commission*:
• Jimilla: 2025 kasafin da aka amince ₦254.99 miliyan; 2026 kasafin da aka amince ₦403.14 miliyan; bambanci +₦148.15 miliyan (+58.1%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-04 (hausa) ok (4.1s)

**Q:** Kwatanta budget din Ministry of Education da aka amince da shi a 2025 da kuma wanda aka amince da shi a 2026.

```
Ga Ministry of Education, 2025 kasafin da aka amince shi ne ₦59.59 biliyan.

*Ministry of Education*:
• Jimilla: 2025 kasafin da aka amince ₦59.59 biliyan; 2026 kasafin da aka amince ₦68.95 biliyan; bambanci +₦9.36 biliyan (+15.7%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-05 (template) ok (3.2s)

**Q:** Compare the Ministry of Justice's approved budget in 2025 and 2026.

```
For Ministry of Justice, the 2025 approved budget is ₦4.46 billion.

*Ministry of Justice*:
• Total: 2025 approved budget ₦4.46 billion; 2026 approved budget ₦6.09 billion; change +₦1.63 billion (+36.5%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-06 (hausa) ok (3.3s)

**Q:** Kwatanta kasafin kuɗin da aka amince da shi na Office of Head of Service a 2025 da 2026.

```
Ga Office of Head of Service, 2025 kasafin da aka amince shi ne ₦3.41 biliyan.

*Office of Head of Service*:
• Jimilla: 2025 kasafin da aka amince ₦3.41 biliyan; 2026 kasafin da aka amince ₦10.44 biliyan; bambanci +₦7.03 biliyan (+206.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## share-01 (code_switched) ok (3.8s)

**Q:** Ministry of Health 2026 approved budget din, what share ne capital?

```
Ga Ministry of Health, kasafin da aka amince (manyan ayyuka) shi ne ₦104.64 biliyan.

*Ministry of Health*:
• Manyan ayyuka: kasafin da aka amince ₦104.64 biliyan; 84.1% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦124.41 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 27
```

## share-02 (hausa) ok (3.8s)

**Q:** Kashi nawa na approved budget na 2026 na Department for Rural Electrification ne capital?

```
Ga Department for Rural Electrification, kasafin da aka amince (manyan ayyuka) shi ne ₦1.12 biliyan.

*Department for Rural Electrification*:
• Manyan ayyuka: kasafin da aka amince ₦1.12 biliyan; 90.3% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦1.25 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## share-03 (typo) ok (4.2s)

**Q:** What sahre of the State Libary Board's 2026 aproved budget is capital?

```
For State Library Board, the approved budget (capital) is ₦300.00 million.

*State Library Board*:
• Capital: approved budget ₦300.00 million; 84.5% of its total (Kasafi's calculation)
• Total: approved budget ₦355.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 27
```

## share-04 (informal) ok (5.2s)

**Q:** What's the capital share of Ministry of Youth and Sports Development's 2026 approved budget?

```
For Ministry of Youth and Sports Development, the approved budget (capital) is ₦13.68 billion.

*Ministry of Youth and Sports Development*:
• Capital: approved budget ₦13.68 billion; 80.2% of its total (Kasafi's calculation)
• Total: approved budget ₦17.06 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-05 (template) ok (4.4s)

**Q:** What share of the POVERTY REDUCTION PROGRAMME's 2026 approved budget is capital?

```
For POVERTY REDUCTION PROGRAMME, the approved budget (capital) is ₦1.70 billion.

*POVERTY REDUCTION PROGRAMME*:
• Capital: approved budget ₦1.70 billion; 76.0% of its total (Kasafi's calculation)
• Total: approved budget ₦2.24 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 25
```

## share-06 (code_switched) ok (4.1s)

**Q:** Nawa ne share na capital a cikin 2026 approved budget na Shari’a Court of Appeal?

```
Ga Shari’a Court of Appeal, kasafin da aka amince (manyan ayyuka) shi ne ₦951.06 miliyan.

*Shari’a Court of Appeal*:
• Manyan ayyuka: kasafin da aka amince ₦951.06 miliyan; 39.5% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦2.41 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 26
```

## false_premise-01 (informal) ok (4.0s)

**Q:** Why'd State Judiciary budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For State Judiciary, the 2025 approved budget is ₦6.28 billion.

*State Judiciary*:
• Total: 2025 approved budget ₦6.28 billion; 2026 approved budget ₦8.17 billion; change +₦1.89 billion (+30.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-02 (typo) ok (3.6s)

**Q:** Why did teh Ministry of Education's aproved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Education, the 2025 approved budget is ₦59.59 billion.

*Ministry of Education*:
• Total: 2025 approved budget ₦59.59 billion; 2026 approved budget ₦68.95 billion; change +₦9.36 billion (+15.7%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-03 (informal) ok (3.6s)

**Q:** why'd the Ministry of Justice budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Justice, the 2025 approved budget is ₦4.46 billion.

*Ministry of Justice*:
• Total: 2025 approved budget ₦4.46 billion; 2026 approved budget ₦6.09 billion; change +₦1.63 billion (+36.5%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-04 (hausa) ok (4.7s)

**Q:** Me ya sa approved budget na Office of the SSG ya ragu daga 2025 zuwa 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
Ga Office of the SSG, 2025 kasafin da aka amince (albashi) shi ne ₦3.91 biliyan.

*Office of the SSG*:
• Albashi: 2025 kasafin da aka amince ₦3.91 biliyan; 2026 kasafin da aka amince ₦4.86 biliyan; bambanci +₦949.77 miliyan (+24.3%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦7.23 biliyan; 2026 kasafin da aka amince ₦9.18 biliyan; bambanci +₦1.95 biliyan (+27.0%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦20.22 biliyan; 2026 kasafin da aka amince ₦26.36 biliyan; bambanci +₦6.14 biliyan (+30.4%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦31.36 biliyan; 2026 kasafin da aka amince ₦40.40 biliyan; bambanci +₦9.04 biliyan (+28.8%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 12, 14, 15; Sokoto State FY 2026 Budget, shafi 16, 19, 22, 25
```

## false_premise-05 (followup) ok (3.8s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Science and Technology, the 2025 approved budget is ₦6.82 billion.

*Ministry of Science and Technology*:
• Total: 2025 approved budget ₦6.82 billion; 2026 approved budget ₦11.69 billion; change +₦4.87 billion (+71.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-06 (typo) ok (3.7s)

**Q:** Why did teh Government House's aproved budget fall form 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Government House, the 2025 approved budget is ₦14.03 billion.

*Government House*:
• Total: 2025 approved budget ₦14.03 billion; 2026 approved budget ₦18.53 billion; change +₦4.50 billion (+32.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## not_in_data-01 (code_switched) ok (4.5s)

**Q:** Nawa ne Ministry for Religious Affairs ta spend a Q4 2026?

```
Ba a cikin takardun ba:
• Ministry for Religious Affairs 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Ministry for Religious Affairs 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-02 (code_switched) ok (4.1s)

**Q:** Nawa Female Education Board ta spend a Q1 2027?

```
Ba a cikin takardun ba:
• Female Education Board 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Female Education Board 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-03 (followup) ok (19.2s)

**Q:** How much is its approved budget for 2028?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Local Government Audit, 2028 Out-Year Estimate: ₦185.57 million [1]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
```

## not_in_data-04 (code_switched) WRONG: no mention of what exists (2024–2026) (14.6s)

**Q:** Nawa ne approved budget din Rural Water and Sanitation Agency for 2028?

```
⚠️ Ban samo takardar da ta fi dacewa ba (Sokoto State 2028 Approved Budget). Amsar da ke ƙasa daga wasu takardun da nake da su ce, ba daga waccan ba.

Na sami takardun da suka shafi tambayarka, amma ban iya tabbatar da alƙaluman ba. Duba madogarar nan:

[1] Sokoto State FY 2026 Budget, shafi 41
[5] Sokoto State FY 2026 Budget, shafi 17
```

## not_in_data-05 (followup) ok (3.0s)

**Q:** How much did it spend in Q4 2026?

```
Not in the documents:
• Ministry of Finance 2026 spent in Q4: the latest implementation report is Q2 2026
• Ministry of Finance 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
```

## not_in_data-06 (followup) ok (4.5s)

**Q:** How much did it spend in Q4 2026?

```
Not in the documents:
• Sultan AbdulRahman College of H/Tech. 2026 spent in Q4: the latest implementation report is Q2 2026
• Sultan AbdulRahman College of H/Tech. 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
```

## rank_lga-01 (code_switched) ok (5.2s)

**Q:** Which 3 LGAs ne a Sokoto with the most IDPs?

```
Ta ƙaramar hukuma (22), mafi yawa:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-02 (informal) ok (4.7s)

**Q:** Top 5 LGAs in Sokoto with most IDPs?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143
4. Tureta: 15,068
5. Shagari: 14,850

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-03 (template) ok (4.8s)

**Q:** Which 10 LGAs in Sokoto have the most IDPs?

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

## lookup_lga-01 (template) ok (5.6s)

**Q:** How many IDPs are there in Kware LGA?

```
IOM DTM counts *1,039* IDPs in Kware (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (template) ok (5.3s)

**Q:** How many IDPs are there in Dange-Shuni LGA?

```
IOM DTM counts *4,615* IDPs in Dange Shuni (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-03 (typo) ok (6.1s)

**Q:** How mnay IDPs aer there in Wamako LGA?

```
IOM DTM counts *4,026* IDPs in Wamakko (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-04 (hausa) ok (5.8s)

**Q:** IDPs nawa ne a Sokoto North LGA?

```
IOM DTM ta ƙidaya *2,274* 'yan gudun hijira a Sokoto North (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-05 (code_switched) ok (5.5s)

**Q:** How many IDPs ne a Tureta LGA?

```
IOM DTM ta ƙidaya *15,068* 'yan gudun hijira a Tureta (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-06 (hausa) ok (4.8s)

**Q:** IDPs nawa ne suke a Kebbe LGA?

```
IOM DTM ta ƙidaya *4,252* 'yan gudun hijira a Kebbe (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
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
