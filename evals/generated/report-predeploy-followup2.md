# Generated coverage run

Cases: cases-389326.json (draw seed 389326), form seed 1

52 cases: wrong 1 (1.9%), of them wrong agency 0 | median 6.2s

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
| code_switched | 0 | 11 |
| followup | 1 | 7 |
| hausa | 0 | 12 |
| informal | 0 | 4 |
| template | 0 | 10 |
| typo | 0 | 8 |

```
Cost of this run:
  Baseten: 25 calls, 225,319 prompt tokens (73,088 cached), 11,400 output tokens -> $0.25
  Meta: 120 calls, 403,817 prompt tokens (291,001 cached), 90,247 output tokens -> $0.57
  models together: $0.82 (prices per 1M tokens from settings kasafi_price_*)
  per answer (52 answers): $0.0114, 1.8 model calls
    Meta/plan               1.00 calls  $0.0038  (33%)
    Baseten/compose         0.27 calls  $0.0031  (27%)
    Meta/read1              0.25 calls  $0.0027  (23%)
    Baseten/read2           0.21 calls  $0.0017  (15%)
    Meta/completeness       0.06 calls  $0.0002  (1%)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0) | identical calls answered from the run's cache: 0
peak memory: 392 MB
```

## lookup-01 (code_switched) ok (13.2s)

**Q:** Ministry for Special Duties nawa aka approve musu a 2026 budget?

```
An amince da jimillar kuɗi ₦829.50 miliyan ga Ministry for Special Duties a cikin kasafin 2026 da aka amince da shi. Wannan jimillar ce daga teburin Jimillar Kashe Kuɗi ta Rukunin Gudanarwa.

• 2026 kasafin da aka amince da shi (jimilla): ₦829.50 miliyan
• 2026 kasafin da aka amince da shi - albashi: ₦12.00 miliyan
• 2026 kasafin da aka amince da shi - kuɗin gudanarwa: ₦195.50 miliyan
• 2026 kasafin da aka amince da shi - manyan ayyuka: ₦622.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 4, 16, 22
```

## lookup-02 (template) ok (9.5s)

**Q:** How much was approved for the Ministry of Health in the 2025 budget?

```
In the 2025 approved budget, ₦52.18 billion was approved for the Ministry of Health. This is the ministry's total expenditure (including its agencies).

• 2025 approved budget (total): ₦52.18 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12
```

## lookup-03 (followup) ok (8.5s)

**Q:** How much was approved for it in the 2025 budget?

```
The 2025 approved budget for the Ministry of Commerce and Industry (the ministry's total, its agencies included) was ₦6.06 billion.

• Ministry of Commerce and Industry, 2025 Approved Budget: ₦6.06 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## lookup-04 (code_switched) ok (11.8s)

**Q:** Nawa ne approved amount na Office of Head of Service for 2025 budget?

```
Office of Head of Service na Jihar Sokoto an ware masa kuɗi jimilla ₦3.41 biliyan a kasafin 2025 da aka amince da shi. Wannan adadin shi ne jimillar kashe kuɗi da aka amince da shi a teburin jimilla ta hanyar ma'aikata.

• 2025 kasafin da aka amince da shi (jimilla): ₦3.41 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-05 (hausa) ok (12.3s)

**Q:** Nawa aka amince wa State Judiciary a kasafin kudin 2025?

```
A kasafin kuɗin 2025 da aka amince wa, jimillar kuɗin da aka ware wa State Judiciary ita ce ₦6.28 biliyan. Wannan ita ce jimilla (total) kamar yadda aka rubuta a teburin kashe kuɗi ta hanyar ma'aikata.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12
```

## lookup-06 (hausa) ok (15.4s)

**Q:** Nawa aka amince wa Ministry for Skills Acquisition and Entrepreneurship Development a kasafin kudin 2026?

```
An amince wa Ministry for Skills Acquisition and Entrepreneurship Development jimillar ₦1.37 biliyan a kasafin kudin 2026 da aka amince.

• Ministry for Skills Acquisition and Entrepreneurship Development, 2026 Approved Budget: ₦1.37 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## split-01 (typo) ok (5.5s)

**Q:** What are teh personnel, overhead and capitl allocations of the Minstry of Humanitarian Affairs & Social Welfare in 2026?

```
For Ministry of Humanitarian Affairs & Social Welfare, the approved budget (salaries) is ₦117.84 million.

*Ministry of Humanitarian Affairs & Social Welfare*:
• Personnel (salaries): approved budget ₦117.84 million
• Overhead (running costs): approved budget ₦1.28 billion
• Capital: approved budget ₦3.72 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 27
```

## split-02 (followup) ok (5.5s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
For Ministry of Finance, the approved budget (salaries) is ₦2.10 billion.

*Ministry of Finance*:
• Personnel (salaries): approved budget ₦2.10 billion
• Overhead (running costs): approved budget ₦8.94 billion
• Capital: approved budget ₦9.47 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 22, 25
```

## split-03 (template) ok (8.3s)

**Q:** What are the personnel, overhead and capital allocations of the Department for Rural Roads in 2025?

```
For Department for Rural Roads, the approved budget (salaries) is ₦34.59 million.

*Department for Rural Roads*:
• Personnel (salaries): approved budget ₦34.59 million
• Overhead (running costs): approved budget ₦33.95 million
• Capital: approved budget ₦25.49 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 14, 16
```

## split-04 (typo) ok (14.7s)

**Q:** What are teh personnel, overhead and captial allocations of the Water Board in 2026?

```
For Water Board, the approved budget (salaries) is ₦764.93 million.

*Water Board*:
• Personnel (salaries): approved budget ₦764.93 million
• Overhead (running costs): approved budget ₦1.92 billion
• Capital: approved budget ₦28.30 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-05 (hausa) ok (9.6s)

**Q:** Menene kason personnel, overhead da capital na Ministry of Livestocks and Fisheries Development a 2025?

```
Ga Ministry of Livestocks and Fisheries Development, kasafin da aka amince (albashi) shi ne ₦928.40 miliyan.

*Ministry of Livestocks and Fisheries Development*:
• Albashi: kasafin da aka amince ₦928.40 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦130.75 miliyan
• Manyan ayyuka: kasafin da aka amince ₦6.84 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 13, 15, 16
```

## split-06 (followup) ok (7.4s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
For House of Assembly Service Commission, the approved budget (salaries) is ₦65.78 million.

*House of Assembly Service Commission*:
• Personnel (salaries): approved budget ₦65.78 million
• Overhead (running costs): approved budget ₦43.00 million
• Capital: approved budget ₦525.50 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## spend_quarter-01 (hausa) ok (7.0s)

**Q:** Nawa NGOs and Donors Agency ta kashe har zuwa karshen Q4 2024, idan aka kwatanta da revised budget nata?

```
Ga NGOs and Donors Agency, abin da aka kashe zuwa yanzu (Q1–Q4) shi ne ₦21.15 miliyan.

*NGOs and Donors Agency*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q4) ₦21.15 miliyan; kasafin da aka sabunta ₦26.00 miliyan; kason kasafin da aka sabunta da aka kashe 81.4% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 16
```

## spend_quarter-02 (template) ok (6.9s)

**Q:** How much had the Rima Radio spent by the end of Q4 2024, against its revised budget?

```
For Rima Radio, the spent so far (Q1–Q4) is ₦116.11 million.

*Rima Radio*:
• Total: spent so far (Q1–Q4) ₦116.11 million; revised budget ₦211.47 million

📄 *Sources:* Budget Performance Report Q4 2024, p. 16
```

## spend_quarter-03 (template) ok (3.4s)

**Q:** How much had the Department for Human Rights spent by the end of Q2 2026, against its revised budget?

```
For Department for Human Rights, the spent so far (Q1–Q2) is ₦2.50 million.

*Department for Human Rights*:
• Total: spent so far (Q1–Q2) ₦2.50 million; revised budget ₦94.80 million

📄 *Sources:* Budget Implementation Report Q2 2026, p. 15
```

## spend_quarter-04 (typo) ok (3.0s)

**Q:** How mch had the Ministry of Informaton spent by the end of Q3 2025, aginst its revised budget?

```
For Ministry of Information, the spent so far (Q1–Q3) is ₦1.33 billion.

*Ministry of Information*:
• Total: spent so far (Q1–Q3) ₦1.33 billion; revised budget ₦2.64 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 16
```

## spend_quarter-05 (code_switched) ok (4.0s)

**Q:** Department for Security Matters ta spend nawa by end of Q3 2025 against revised budget nata?

```
Ga Department for Security Matters, abin da aka kashe zuwa yanzu (Q1–Q3) shi ne ₦6.78 biliyan.

*Department for Security Matters*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q3) ₦6.78 biliyan; kasafin da aka sabunta ₦10.57 biliyan

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 17
```

## spend_quarter-06 (hausa) ok (3.7s)

**Q:** Nawa Ministry of Budget and Economic Planning ta kashe har zuwa karshen Q3 2025, idan aka kwatanta da revised budget dinta?

```
Ga Ministry of Budget and Economic Planning, kasafin da aka sabunta shi ne ₦3.84 biliyan.

*Ministry of Budget and Economic Planning*:
• Jimilla: kasafin da aka sabunta ₦3.84 biliyan; abin da aka kashe zuwa yanzu (Q1–Q3) ₦723.62 miliyan; kason kasafin da aka sabunta da aka kashe 18.8% (lissafin Kasafi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 18
```

## compare-01 (code_switched) ok (4.0s)

**Q:** Kwatanta approved budget na Ministry for Special Duties, 2025 vs 2026 fa?

```
Ga Ministry for Special Duties, 2025 kasafin da aka amince shi ne ₦423.00 miliyan.

*Ministry for Special Duties*:
• Jimilla: 2025 kasafin da aka amince ₦423.00 miliyan; 2026 kasafin da aka amince ₦829.50 miliyan; bambanci +₦406.50 miliyan (+96.1%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-02 (typo) ok (3.1s)

**Q:** Comapre the Ministry of Justcie's aproved budget in 2025 and 2026.

```
For Ministry of Justice, the 2025 approved budget is ₦4.46 billion.

*Ministry of Justice*:
• Total: 2025 approved budget ₦4.46 billion; 2026 approved budget ₦6.09 billion; change +₦1.63 billion (+36.5%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-03 (hausa) ok (2.8s)

**Q:** Kwatanta approved budget ɗin Ministry for Local Government and Chieftancy's a 2025 da 2026?

```
Ga Ministry for Local Government and Chieftancy, 2025 kasafin da aka amince shi ne ₦570.64 miliyan.

*Ministry for Local Government and Chieftancy*:
• Jimilla: 2025 kasafin da aka amince ₦570.64 miliyan; 2026 kasafin da aka amince ₦1.36 biliyan; bambanci +₦788.43 miliyan (+138.2%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 19
```

## compare-04 (hausa) ok (4.5s)

**Q:** Kwatanta approved budget na Ministry Careers & Special Services a 2025 da 2026.

```
Ga Ministry Careers & Special Services, 2025 kasafin da aka amince shi ne ₦10.57 biliyan.

*Ministry Careers & Special Services*:
• Jimilla: 2025 kasafin da aka amince ₦10.57 biliyan; 2026 kasafin da aka amince ₦26.37 biliyan; bambanci +₦15.80 biliyan (+149.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-05 (template) ok (10.1s)

**Q:** Compare the Administration Sector's approved budget in 2025 and 2026.

```
The Administration Sector's approved budget (total expenditure by administrative classification) was ₦103.22 billion in 2025 and ₦149.52 billion in 2026. The 2026 approved figure is higher than the 2025 approved figure.

• 2025 approved budget (total): ₦103.22 billion
• 2026 approved budget (total): ₦149.52 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16; Sokoto State Government 2025 Approved Budget, p. 11
```

## compare-06 (hausa) ok (3.5s)

**Q:** Kwatanta kasafin kudin da aka amince wa Ministry of Lands and Housing a 2025 da 2026.

```
Ga Min of Lands and Housing, 2025 kasafin da aka amince shi ne ₦47.46 biliyan.

*Min of Lands and Housing*:
• Jimilla: 2025 kasafin da aka amince ₦47.46 biliyan; 2026 kasafin da aka amince ₦35.78 biliyan; bambanci -₦11.69 biliyan (-24.6%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 17
```

## share-01 (code_switched) ok (3.6s)

**Q:** Approved budget na 2026 na Ministry for Home Affairs, what share ne capital?

```
Ga Ministry for Home Affairs, kasafin da aka amince (manyan ayyuka) shi ne ₦2.58 biliyan.

*Ministry for Home Affairs*:
• Manyan ayyuka: kasafin da aka amince ₦2.58 biliyan; 42.3% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦6.11 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-02 (hausa) ok (3.7s)

**Q:** Cikin approved budget na State High Court na 2026, kaso nawa ne na capital?

```
Ga State High Court, kasafin da aka amince (manyan ayyuka) shi ne ₦2.13 biliyan.

*State High Court*:
• Manyan ayyuka: kasafin da aka amince ₦2.13 biliyan; 41.0% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦5.21 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 26
```

## share-03 (typo) ok (3.2s)

**Q:** What sahre of the Ministry of Healt's 2026 aproved budget is capital?

```
For Ministry of Health, the approved budget (capital) is ₦104.64 billion.

*Ministry of Health*:
• Capital: approved budget ₦104.64 billion; 84.1% of its total (Kasafi's calculation)
• Total: approved budget ₦124.41 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 27
```

## share-04 (informal) ok (5.0s)

**Q:** What part of the State Emergency Management Agency (SEMA)'s 2026 approved budget is capital?

```
For State Emergency Management Agency (SEMA), the approved budget (capital) is ₦1.20 billion.

*State Emergency Management Agency (SEMA)*:
• Capital: approved budget ₦1.20 billion; 90.6% of its total (Kasafi's calculation)
• Total: approved budget ₦1.32 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 25
```

## share-05 (template) ok (4.8s)

**Q:** What share of the Ministry of Youth and Sports Development's 2026 approved budget is capital?

```
For Ministry of Youth and Sports Development, the approved budget (capital) is ₦13.68 billion.

*Ministry of Youth and Sports Development*:
• Capital: approved budget ₦13.68 billion; 80.2% of its total (Kasafi's calculation)
• Total: approved budget ₦17.06 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-06 (code_switched) ok (4.1s)

**Q:** Ministry for Higher Education approved budget na 2026, kashi nawa ne capital?

```
Ga Ministry for Higher Education, kasafin da aka amince (manyan ayyuka) shi ne ₦20.62 biliyan.

*Ministry for Higher Education*:
• Manyan ayyuka: kasafin da aka amince ₦20.62 biliyan; 60.7% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦33.99 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 27
```

## false_premise-01 (informal) ok (4.2s)

**Q:** Why'd the Ministry of Transport's approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Transport, the 2025 approved budget is ₦3.65 billion.

*Ministry of Transport*:
• Total: 2025 approved budget ₦3.65 billion; 2026 approved budget ₦50.87 billion; change +₦47.21 billion (+1292.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-02 (typo) ok (3.9s)

**Q:** Why did teh State Judiciary's aproved budget fall form 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For State Judiciary, the 2025 approved budget is ₦6.28 billion.

*State Judiciary*:
• Total: 2025 approved budget ₦6.28 billion; 2026 approved budget ₦8.17 billion; change +₦1.89 billion (+30.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-03 (informal) ok (3.6s)

**Q:** Why'd the Ministry for Special Duties's approved budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry for Special Duties, the 2025 approved budget is ₦423.00 million.

*Ministry for Special Duties*:
• Total: 2025 approved budget ₦423.00 million; 2026 approved budget ₦829.50 million; change +₦406.50 million (+96.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## false_premise-04 (hausa) ok (3.3s)

**Q:** Me ya sa approved budget na Ministry Careers & Special Services ya ragu daga 2025 zuwa 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
Ga Ministry Careers & Special Services, 2025 kasafin da aka amince (albashi) shi ne ₦51.37 miliyan.

*Ministry Careers & Special Services*:
• Albashi: 2025 kasafin da aka amince ₦51.37 miliyan; 2026 kasafin da aka amince ₦63.37 miliyan; bambanci +₦12.00 miliyan (+23.4%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦10.04 biliyan; 2026 kasafin da aka amince ₦18.00 biliyan; bambanci +₦7.96 biliyan (+79.3%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦481.00 miliyan; 2026 kasafin da aka amince ₦8.30 biliyan; bambanci +₦7.82 biliyan (+1626.6%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦10.57 biliyan; 2026 kasafin da aka amince ₦26.37 biliyan; bambanci +₦15.80 biliyan (+149.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 13, 14, 16; Sokoto State FY 2026 Budget, shafi 16, 19, 22, 25
```

## false_premise-05 (followup) ok (12.4s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
The Local Government Service Commission's approved budget did not fall. It rose from ₦555.67 million in 2025 to ₦746.52 million in 2026, a change of 34.3% (Kasafi's calculation). Budgets show amounts only, not reasons for the change.

• Local Government Service Commission, 2025 Approved Budget: ₦555.67 million
• Local Government Service Commission, 2026 Approved Budget: ₦746.52 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-06 (typo) ok (11.4s)

**Q:** Why did teh Economic Sector's aproved budget fall from 2025 to 2026?

```
The Economic Sector's approved budget did not fall. It was ₦237.36 billion in the 2025 approved budget and rose to ₦316.04 billion in the 2026 approved budget, an increase of ₦78.68 billion (Kasafi's calculation). The budget documents do not give reasons for changes.

• Economic Sector, 2025 Approved Budget: ₦237.36 billion
• Economic Sector, 2026 Approved Budget: ₦316.04 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## not_in_data-01 (code_switched) ok (14.7s)

**Q:** How much ne approved budget na Orthopedic Hospital Wamakko for 2028?

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• Orthopedic Hospital Wamakko, 2028 Out-Year Estimate: ₦1.28 biliyan [1]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
```

## not_in_data-02 (code_switched) ok (4.0s)

**Q:** Nawa Department for Rural Roads ta spend a Q4 2026?

```
Ba a cikin takardun ba:
• Department for Rural Roads 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Department for Rural Roads 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-03 (followup) ok (4.2s)

**Q:** How much did it spend there in Q4 2026?

```
Not in the documents:
• Ministry for Local Government and Chieftancy 2026 spent in Q4: the latest implementation report is Q2 2026
• Ministry for Local Government and Chieftancy 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
```

## not_in_data-04 (code_switched) ok (15.2s)

**Q:** Nawa ne approved budget na Rural Water and Sanitation Agency for 2028?

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• Rural Water and Sanitation Agency, 2028 Out-Year Estimate: ₦62.00 miliyan [1]
• Rural Water and Sanitation Agency (manyan ayyuka), 2028 Out-Year Estimate: 0.00 [2]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## not_in_data-05 (followup) ok (4.2s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• State Library Board 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• State Library Board 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-06 (followup) WRONG: no mention of what exists (2024–2026) (13.0s)

**Q:** How much is its approved budget for 2028?

```
⚠️ I couldn't get the document that fits best (Sokoto State Government 2028 Approved Budget). The answer below is from other documents I have, not from that one.

The documents do not print a 2028 approved budget for the Agency for Industrial Development (found="partial"). The only figure shown for the Agency is its 2026 approved budget total of ₦129.34 million. The 2028 figure in the 2026 budget papers is only an out-year estimate for later planning, and the excerpts here do not show that estimate for this Agency.

• 2026 approved budget (total) for Agency for Industrial Development: ₦129.34 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 5
```

## rank_lga-01 (code_switched) ok (10.3s)

**Q:** Wadanne 3 LGAs ne in Sokoto get the most IDPs?

```
Ta ƙaramar hukuma (22), mafi yawa:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-02 (informal) ok (6.5s)

**Q:** top 5 LGAs with most IDPs in Sokoto?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143
4. Tureta: 15,068
5. Shagari: 14,850

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-03 (template) ok (6.2s)

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

## lookup_lga-01 (template) ok (6.3s)

**Q:** How many IDPs are there in Dange-Shuni LGA?

```
IOM DTM counts *4,615* IDPs in Dange Shuni (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (template) ok (6.6s)

**Q:** How many IDPs are there in Sokoto South LGA?

```
IOM DTM counts *4,486* IDPs in Sokoto South (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-03 (typo) ok (7.0s)

**Q:** How mnay IDPs are ther in Isa LGA?

```
IOM DTM counts *14,047* IDPs in Isa (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-04 (hausa) ok (6.8s)

**Q:** IDPs nawa ne a Kware LGA?

```
IOM DTM ta ƙidaya *1,039* 'yan gudun hijira a Kware (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-05 (code_switched) ok (6.0s)

**Q:** IDPs nawa are there a Gada LGA?

```
IOM DTM ta ƙidaya *1,014* 'yan gudun hijira a Gada (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-06 (hausa) ok (8.2s)

**Q:** Adadin IDPs a Binji LGA nawa ne?

```
IOM DTM ta ƙidaya *619* 'yan gudun hijira a Binji (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## trend-01 (template) ok (7.7s)

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
