# Generated coverage run

Cases: cases-12062.json (draw seed 12062), form seed 1

156 cases: wrong 4 (2.6%), of them wrong agency 0 | median 4.5s

| family | wrong | of |
|---|---|---|
| compare | 0 | 19 |
| false_premise | 0 | 19 |
| lookup | 0 | 19 |
| lookup_lga | 0 | 19 |
| not_in_data | 2 | 19 |
| rank_lga | 0 | 3 |
| share | 1 | 19 |
| spend_quarter | 1 | 19 |
| split | 0 | 19 |
| trend | 0 | 1 |

| form | wrong | of |
|---|---|---|
| code_switched | 1 | 34 |
| followup | 0 | 21 |
| hausa | 0 | 23 |
| informal | 1 | 22 |
| template | 1 | 28 |
| typo | 1 | 28 |

```
Cost of this run:
  Baseten: 27 calls, 193,123 prompt tokens (59,008 cached), 10,436 output tokens -> $0.22
  Meta: 367 calls, 1,207,141 prompt tokens (731,965 cached), 278,696 output tokens -> $1.89
  models together: $2.11 (prices per 1M tokens from settings kasafi_price_*)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0)
peak memory: 262 MB
```

## lookup-01 (code_switched) ok (9.4s)

**Q:** Nawa aka approve wa Ministry for Religious Affairs a 2025 budget?

```
An amince da ₦11.26 biliyan ga Ministry for Religious Affairs a kasafin 2025 (jimilla) daga teburin Total Expenditure by Administrative Classification. Wannan adadi ne da aka ware a kasafi, ba adadin da aka kashe ba.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-02 (template) ok (8.3s)

**Q:** How much was approved for the State Judiciary in the 2024 budget?

```
The 2024 approved budget (total) for the State Judiciary was ₦7.49 billion. The 2024 actual spending (total) was ₦184.07 million.

📄 *Sources:* Sokoto State Government 2024 Approved Budget, p. 44; Sokoto State FY 2026 Budget, p. 18
```

## lookup-03 (followup) ok (10.3s)

**Q:** How much was approved for it in the 2026 budget?

```
The 2026 approved budget (total) for the Civil Service Commission is ₦403.14 million. This is the allocated amount for 2026, not actual spending.

• 2026 approved budget (total): ₦403.14 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
```

## lookup-04 (code_switched) ok (10.7s)

**Q:** Nawa Office of the SSG aka approve musu a 2025 budget?

```
An amince da jimillar ₦31.36 biliyan ga Office of the SSG a kasafin 2025. Wannan jimilla ce daga teburin Total Expenditure by Administrative Classification.

• 2025 kasafin da aka amince (albashi): ₦3.91 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State Budget Implementation Report Q3 2025, shafi 16; Budget Implementation Report Q4 2025, shafi 16
```

## lookup-05 (hausa) ok (13.3s)

**Q:** Nawa aka amince wa Ministry for Home Affairs a kasafin kudin 2026?

```
A kasafin 2026 da aka amince, jimillar Ministry for Home Affairs ne ₦6.11 biliyan. Wannan kuɗi ne da aka amince (budgeted), ba kuɗin da aka kashe ba. A watan Janairu zuwa Satumba 2025, an kashe ₦1.31 biliyan.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16
```

## lookup-06 (hausa) ok (14.3s)

**Q:** Nawa aka amince wa Ministry Careers & Special Services a kasafin kudin 2026?

```
An amince wa Ministry Careers & Special Services jimillar ₦26.37 biliyan a kasafin 2026, daga teburin Jimillar Kashewa ta Ma'aikata. Wannan kuɗi ne da aka amince da shi (budgeted), ba kuɗin da aka kashe ba.

• 2026 (albashi): ₦63.37 miliyan
• 2026 (kuɗin gudanarwa): ₦18.00 biliyan
• 2026 (manyan ayyuka): ₦8.30 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 19, 22, 25
```

## lookup-07 (template) ok (9.9s)

**Q:** How much was approved for the Ministry of Health in the 2025 budget?

```
The State Government approved ₦52.18 billion for the Ministry of Health in the 2025 budget. This is the allocated (budgeted) total from the Total Expenditure by Administrative Classification table.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12
```

## lookup-08 (template) ok (11.1s)

**Q:** How much was approved for the Ministry of Commerce and Industry in the 2026 budget?

```
The 2026 approved budget (total) for the Ministry of Commerce and Industry is ₦6.56 billion. In January–September 2025 the ministry spent ₦618.36 million.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
```

## lookup-09 (code_switched) ok (10.0s)

**Q:** Nawa Ministry of Justice ta samu a 2024 budget?

```
Ma'aikatar Shari'a ta samu jimilla ₦2.21 biliyan a kasafin 2024 da aka amince da shi, daga teburin Jimillar Kashe Kuɗi. Abin da aka kashe a 2024 (Q1–Q4 2024) ya kai ₦1.07 biliyan (42.5% na kasafin da aka sabunta).

• 2024 kasafin da aka amince (jimilla): ₦2.21 biliyan
• 2024 kasafin da aka sabunta (jimilla): ₦2.51 biliyan
• 2024 abin da aka kashe Q1–Q4 (jimilla): ₦1.07 biliyan (42.5% na kasafin da aka sabunta)

📄 *Madogara:* Sokoto State Government 2024 Approved Budget, shafi 44; Budget Performance Report Q4 2024, shafi 19
```

## lookup-10 (code_switched) ok (12.0s)

**Q:** Nawa aka approve wa Ministry for Higher Education a 2025 budget?

```
An amince da ₦19.15 biliyan ga Ministry for Higher Education a kasafin 2025 (jimilla). Wannan adadi kasafin da aka amince da shi ne, ba kudin da aka kashe ba. A Janairu–Satumba 2024 kacal, an kashe ₦7.13 biliyan.

• 2025 kasafin da aka amince da shi (manyan ayyuka): ₦6.60 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12, 16
```

## lookup-11 (followup) ok (11.5s)

**Q:** How much was approved for it in the 2026 budget?

```
₦149.52 billion was approved for the Administration Sector in the 2026 budget (total). ₦33.25 billion was spent in Q1-Q2 2026 only (20.8% of the revised budget).

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16; Budget Implementation Report Q2 2026, p. 15
```

## lookup-12 (code_switched) ok (9.8s)

**Q:** Nawa Ministry of Social Welfare & Community Development ta samu for 2026 budget?

```
Ma'aikatar Social Welfare & Community Development ta samu ₦5.11 biliyan a kasafin 2026 da aka amince (jimilla). Wannan kudi ne da aka ware a kasafi, ba kudin da aka kashe ba.

• 2025 kasafin da aka sabunta (jimilla): ₦7.72 biliyan
• 2025 abin da aka kashe (Janairu–Satumba 2025 kawai): ₦907.51 miliyan
• 2026 kasafin da aka amince (albashi): ₦117.84 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 19, 21
```

## lookup-13 (typo) ok (10.4s)

**Q:** How muc was approved for the Ministy for Local Government and Chieftancy in the 2026 budjet?

```
The Ministry for Local Government and Chieftancy was approved ₦1.36 billion for 2026 (total, allocated) from the Total Expenditure by Administrative Classification table. From January to September 2025 it had spent ₦134.95 million (spent, part-year only).

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19
```

## lookup-14 (typo) ok (8.4s)

**Q:** How much was aproved for the Ministry of Enery and Petroleum Resorces in the 2025 budget?

```
From the Total Expenditure by Administrative Classification table, the 2025 approved budget (total) for the Ministry of Energy and Petroleum Resources was ₦10.30 billion. This figure is the allocation, not actual spending.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11
```

## lookup-15 (typo) ok (9.5s)

**Q:** How much was aproved for the Law adn Justice in teh 2024 budget?

```
Law and Justice was approved for ₦9.70 billion in the 2024 budget (total). This figure is the approved allocation from the Total Expenditure table.

📄 *Sources:* Sokoto State Government 2024 Approved Budget, p. 44
```

## lookup-16 (template) ok (6.7s)

**Q:** How much was approved for the Fiscal Responsibility Commission in the 2026 budget?

```
₦60.99 million was approved for the Fiscal Responsibility Commission in the 2026 budget. This is the total allocated budget figure.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
```

## lookup-17 (followup) ok (9.4s)

**Q:** How much was approved for it in the 2025 budget?

```
From the Total Expenditure by Administrative Classification table, the State Government approved ₦4.03 billion for the Ministry of Budget and Economic Planning in the 2025 budget (total). This is the approved allocation, not actual spending.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11
```

## lookup-18 (typo) ok (10.3s)

**Q:** How much was apporved for the Ministry of Educaton in the 2025 budget?

```
The State Government approved ₦59.59 billion for the Ministry of Education in the 2025 budget (total). This is the allocated amount, not spent money, from the Total Expenditure by Administrative Classification table.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12
```

## lookup-19 (informal) ok (10.5s)

**Q:** How much did Ministry of Innovation and Digital Economy get in 2026 budget?

```
From the Total Expenditure table, the Ministry of Innovation and Digital Economy was allocated ₦3.59 billion in the 2026 approved budget (total). It spent ₦362.76 million in January–September 2025.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
```

## split-01 (typo) ok (2.8s)

**Q:** What are teh personnel, overhead and capital alocations of the State Universal Basic Education Board (SUBEB) in 2026?

```
*State Universal Basic Education Board (SUBEB)* (code 051700300100):
• Personnel (salaries): approved budget ₦314.91 million
• Overhead (running costs): approved budget ₦1.27 billion
• Capital: approved budget ₦9.15 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 27
```

## split-02 (followup) ok (4.1s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
*Ministry of Livestocks and Fisheries Development* (code 026800000000):
• Personnel (salaries): approved budget ₦928.40 million
• Overhead (running costs): approved budget ₦130.75 million
• Capital: approved budget ₦6.84 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-03 (template) ok (5.1s)

**Q:** What are the personnel, overhead and capital allocations of the Livestock Development Programme in 2026?

```
*Livestock Development Programme* (code 026800200100):
• Personnel (salaries): approved budget ₦13.14 million
• Overhead (running costs): approved budget ₦20.91 million
• Capital: approved budget ₦334.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-04 (typo) ok (3.4s)

**Q:** What are teh personnel, overhead and capial allocations of the Orthopedic Hospital Wamakko in 2026?

```
*Orthopedic Hospital Wamakko* (code 052104100100):
• Personnel (salaries): approved budget ₦630.72 million
• Overhead (running costs): approved budget ₦48.75 million
• Capital: approved budget ₦590.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 27
```

## split-05 (hausa) ok (4.7s)

**Q:** Menene rabon personnel, overhead da capital na Pilgrims Welfare Agency a 2026?

```
*Pilgrims Welfare Agency* (code 011103700100):
• Albashi: kasafin da aka amince ₦35.52 miliyan; kasafin da aka sabunta ₦35.52 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦21.42 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦3.93 biliyan; kasafin da aka sabunta ₦3.93 biliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦498.50 miliyan
• Manyan ayyuka: kasafin da aka amince ₦1.12 biliyan; kasafin da aka sabunta ₦1.12 biliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦124.57 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 19, 22, 25; Budget Implementation Report Q2 2026, shafi 19, 22, 26
```

## split-06 (followup) ok (4.6s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
*Ministry for Basic Education* (code 051700100100):
• Personnel (salaries): approved budget ₦1.18 billion
• Overhead (running costs): approved budget ₦4.92 billion
• Capital: approved budget ₦29.25 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-07 (typo) ok (3.7s)

**Q:** What are teh personnel, overhaed and capital allocations of the Sultan Maccido Institute for Qur'ani & General Studies in 2026?

```
*Sultan Maccido Institute for Qur'ani & General Studies* (code 051700260100):
• Personnel (salaries): approved budget ₦458.44 million
• Overhead (running costs): approved budget ₦134.00 million
• Capital: approved budget ₦430.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 27
```

## split-08 (followup) ok (3.2s)

**Q:** And what are its personnel, overhead and capital allocations in 2026?

```
*Ministry for Higher Education* (code 056900000000):
• Personnel (salaries): approved budget ₦6.72 billion
• Overhead (running costs): approved budget ₦6.65 billion
• Capital: approved budget ₦20.62 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 27
```

## split-09 (typo) ok (3.7s)

**Q:** What are the personnel, overhaed and capial allocations of the Shari’a Court of Appeal in 2025?

```
*Shari’a Court of Appeal* (code 031805500100):
• Personnel (salaries): approved budget ₦597.63 million
• Overhead (running costs): approved budget ₦655.00 million
• Capital: approved budget ₦1.04 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-10 (hausa) ok (3.9s)

**Q:** Menene kason personnel, overhead da capital na Ministry of Science and Technology a 2026?

```
*Ministry of Science and Technology* (code 022800000000):
• Albashi: kasafin da aka amince ₦1.65 biliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦1.01 biliyan
• Manyan ayyuka: kasafin da aka amince ₦9.02 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 20, 23, 26
```

## split-11 (typo) ok (4.8s)

**Q:** What are teh personnel, overhead and capital alocations of the Agency for Persons Living With Disabilites in 2025?

```
*Agency for Persons Living With Disabilities* (code 051300300100):
• Personnel (salaries): approved budget ₦26.33 million
• Overhead (running costs): approved budget ₦363.10 million
• Capital: approved budget ₦400.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-12 (followup) ok (4.3s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
*Ministry of Transport* (code 022900000000):
• Personnel (salaries): approved budget ₦100.00 million
• Overhead (running costs): approved budget ₦3.10 billion
• Capital: approved budget ₦47.67 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-13 (typo) ok (4.2s)

**Q:** What aer the personnel, overhaed and capital allocatons of the Surveyor General Office in 2026?

```
*Surveyor General Office* (code 025300300100):
• Personnel (salaries): approved budget ₦17.62 million
• Overhead (running costs): approved budget ₦67.70 million
• Capital: approved budget ₦286.50 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-14 (hausa) ok (4.3s)

**Q:** Menene rabon personnel, overhead da capital na Ministry of Commerce and Industry a 2026?

```
*Ministry of Commerce and Industry* (code 022200000000):
• Albashi: kasafin da aka amince ₦193.00 miliyan; kasafin da aka sabunta ₦193.00 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦69.17 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦2.16 biliyan; kasafin da aka sabunta ₦1.25 biliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦43.64 miliyan
• Manyan ayyuka: kasafin da aka amince ₦4.21 biliyan; kasafin da aka sabunta ₦4.11 biliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦0.00

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 20, 23, 25; Budget Implementation Report Q2 2026, shafi 20, 23, 27
```

## split-15 (informal) ok (4.0s)

**Q:** How much for Commodity Board personnel, overhead, capital in 2025?

```
*Commodity Board* (code 022200200100):
• Personnel (salaries): approved budget ₦5.37 million
• Overhead (running costs): approved budget ₦16.60 million
• Capital: approved budget ₦0.00

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 14, 16
```

## split-16 (hausa) ok (3.4s)

**Q:** Menene personnel, overhead da capital allocations na Office of Head of Service a 2025?

```
*Office of Head of Service* (code 012500000000):
• Albashi: kasafin da aka amince ₦975.99 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦875.00 miliyan
• Manyan ayyuka: kasafin da aka amince ₦1.55 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12, 14, 16
```

## split-17 (followup) ok (4.0s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
*Ministry of Environment* (code 053500000000):
• Personnel (salaries): approved budget ₦660.37 million
• Overhead (running costs): approved budget ₦786.00 million
• Capital: approved budget ₦23.08 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 14, 15, 17
```

## split-18 (typo) ok (3.4s)

**Q:** What are teh personnel, overhead and capital alocations of the Ministry for Women Affairs in 2025?

```
*Ministry for Women Affairs* (code 051400000000):
• Personnel (salaries): approved budget ₦108.21 million
• Overhead (running costs): approved budget ₦665.10 million
• Capital: approved budget ₦7.67 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-19 (hausa) ok (3.7s)

**Q:** Menene kasafin personnel, overhead da capital na State Bureau of Statistics a 2026?

```
*State Bureau of Statistics* (code 023800400100):
• Albashi: kasafin da aka amince ₦42.00 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦502.00 miliyan
• Manyan ayyuka: kasafin da aka amince ₦480.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 20, 23, 26
```

## spend_quarter-01 (hausa) ok (4.0s)

**Q:** Nawa Department for Rural Electrification ta kashe har zuwa karshen Q3 2025, idan aka kwatanta da revised budget nata?

```
*Department for Rural Electrification* (code 023100100200):
• Jimilla: kasafin da aka sabunta ₦1.40 biliyan; abin da aka kashe zuwa yanzu (Q1–Q3) ₦132.95 miliyan; kason kasafin da aka sabunta da aka kashe 9.5% (lissafin Kasafi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 17
```

## spend_quarter-02 (template) ok (3.6s)

**Q:** How much had the Ministry of Livestocks and Fisheries Development spent by the end of Q4 2024, against its revised budget?

```
*Ministry of Livestocks and Fisheries Development* (code 026800000000):
• Total: revised budget ₦9.27 billion; spent so far (Q1–Q4) ₦1.15 billion; share of the revised budget spent 12.4% (Kasafi's calculation)

📄 *Sources:* Budget Performance Report Q4 2024, p. 19
```

## spend_quarter-03 (template) ok (4.3s)

**Q:** How much had the SOSACAT spent by the end of Q4 2024, against its revised budget?

```
*SOSACAT* (code 011103300100):
• Total: revised budget ₦38.95 million; spent so far (Q1–Q4) ₦28.45 million; share of the revised budget spent 73.0% (Kasafi's calculation)

📄 *Sources:* Budget Performance Report Q4 2024, p. 16
```

## spend_quarter-04 (typo) ok (4.3s)

**Q:** How mch had the Sokoto Engineering Construction Company spent by the end of Q3 2025, agianst its revised budet?

```
*Sokoto Engineering Construction Company* (code 023405600100):
• Total: revised budget ₦30.99 million; spent so far (Q1–Q3) ₦16.81 million; share of the revised budget spent 54.2% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## spend_quarter-05 (code_switched) ok (4.3s)

**Q:** State Universal Basic Education Board (SUBEB) ta spend nawa by end of Q4 2024 against revised budget dinta?

```
*State Universal Basic Education Board (SUBEB)* (code 051700300100):
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q4) ₦4.23 biliyan; kasafin da aka sabunta ₦4.71 biliyan; kason kasafin da aka sabunta da aka kashe 89.9% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 19
```

## spend_quarter-06 (hausa) ok (3.8s)

**Q:** Nawa Ministry for Women Affairs ta kashe har zuwa karshen Q2 2026, idan aka duba da revised budget dinta?

```
*Ministry for Women Affairs* (code 051400000000):
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q2) ₦388.37 miliyan; kasafin da aka sabunta ₦7.24 biliyan; kason kasafin da aka sabunta da aka kashe 5.4% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 17
```

## spend_quarter-07 (informal) ok (3.9s)

**Q:** how much had the Ministry of Innovation and Digital Economy spent by end of Q2 2026 vs its revised budget?

```
*Ministry of Innovation and Digital Economy* (code 027900000000):
• Total: revised budget ₦3.59 billion; spent so far (Q1–Q2) ₦197.88 million; share of the revised budget spent 5.5% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 16
```

## spend_quarter-08 (followup) ok (4.4s)

**Q:** How much had it spent by the end of Q3 2025 against its revised budget?

```
*Drugs and Medical Supplies Mgt. Agency* (code 052111400300):
• Total: spent so far (Q1–Q3) ₦5.30 million; revised budget ₦122.70 million; share of the revised budget spent 4.3% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 19
```

## spend_quarter-09 (typo) ok (3.9s)

**Q:** How much had teh Ministry of Works spent by the end of Q2 2026, aginst its revised budgte?

```
*Ministry of Works* (code 023400000000):
• Total: spent so far (Q1–Q2) ₦9.63 billion; revised budget ₦58.17 billion; share of the revised budget spent 16.6% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 16
```

## spend_quarter-10 (informal) WRONG: missing ['1,106,444,390.00'] (4.4s)

**Q:** how much had Sokoto Urban & Reg. Planning Department spent by end Q2 2026 vs its revised budget?

```
*Sokoto Urban & Reg. Planning Department* (code 025300500100):
• Total: spent so far (Q1–Q2) ₦75.34 million; share of the revised budget spent 6.8% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 17
```

## spend_quarter-11 (hausa) ok (3.8s)

**Q:** State Agency for Normadic Education1 ta kashe kudi nawa har zuwa karshen Q4 2024, idan aka kwatanta da revised budget dinta?

```
*State Agency for Normadic Education* (code 051701100100):
• Jimilla: kasafin da aka sabunta ₦602.81 miliyan; abin da aka kashe zuwa yanzu (Q1–Q4) ₦235.08 miliyan; kason kasafin da aka sabunta da aka kashe 39.0% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 19
```

## spend_quarter-12 (followup) ok (3.9s)

**Q:** How much had it spent by the end of Q3 2025, against its revised budget?

```
*Liaison Office ABUJA* (code 016102100200):
• Total: spent so far (Q1–Q3) ₦52.41 million; revised budget ₦77.18 million; share of the revised budget spent 67.9% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 16
```

## spend_quarter-13 (informal) ok (4.9s)

**Q:** How much did the Sokoto State contributory health care mgt agency spend by end of Q2 2026 vs its revised budget?

```
*Sokoto State contributory health care mgt agency* (code 052100200100):
• Total: revised budget ₦299.39 million; spent so far (Q1–Q2) ₦142.30 million; share of the revised budget spent 47.5% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## spend_quarter-14 (code_switched) ok (3.8s)

**Q:** Pilgrims Welfare Agency ta kashe nawa by the end of Q2 2026 against revised budget nata?

```
*Pilgrims Welfare Agency* (code 011103700100):
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q2) ₦644.49 miliyan; kasafin da aka sabunta ₦5.09 biliyan; kason kasafin da aka sabunta da aka kashe 12.7% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 15
```

## spend_quarter-15 (code_switched) ok (3.5s)

**Q:** Sokoto State Scholarship and Students Matters ta spend nawa by end of Q3 2025 against revised budget dinta?

```
*Sokoto State Scholarship and Students Matters* (code 056905500100):
• Jimilla: kasafin da aka sabunta ₦4.57 biliyan; abin da aka kashe zuwa yanzu (Q1–Q3) ₦1.36 biliyan; kason kasafin da aka sabunta da aka kashe 29.7% (lissafin Kasafi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 19
```

## spend_quarter-16 (template) ok (3.9s)

**Q:** How much had the Ministry of Environment spent by the end of Q3 2025, against its revised budget?

```
*Ministry of Environment* (code 053500000000):
• Total: spent so far (Q1–Q3) ₦7.59 billion; revised budget ₦21.04 billion; share of the revised budget spent 36.1% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 19
```

## spend_quarter-17 (informal) ok (4.7s)

**Q:** How much did Ministry of Agriculture & Natural Resource spend by end of Q4 2024 vs its revised budget?

```
*Ministry of Agriculture & Natural Resource* (code 021500000000):
• Total: revised budget ₦33.11 billion; spent so far (Q1–Q4) ₦17.18 billion; share of the revised budget spent 51.9% (Kasafi's calculation)

📄 *Sources:* Budget Performance Report Q4 2024, p. 17
```

## spend_quarter-18 (template) ok (3.6s)

**Q:** How much had the Sultan AbdulRahman College of H/Tech. spent by the end of Q4 2024, against its revised budget?

```
*Sultan AbdulRahman College of H/Tech.* (code 052110600100):
• Total: revised budget ₦1.16 billion; spent so far (Q1–Q4) ₦417.66 million; share of the revised budget spent 35.9% (Kasafi's calculation)

📄 *Sources:* Budget Performance Report Q4 2024, p. 20
```

## spend_quarter-19 (template) ok (3.9s)

**Q:** How much had the Ministry of Humanitarian Affairs & Social Welfare spent by the end of Q3 2025, against its revised budget?

```
*Ministry of Humanitarian Affairs & Social Welfare* (code 055600100100):
• Total: spent so far (Q1–Q3) ₦907.51 million; revised budget ₦7.72 billion; share of the revised budget spent 11.8% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 19
```

## compare-01 (code_switched) ok (3.8s)

**Q:** Kwatanta approved budget na Ministry for Women Affairs na 2025 da 2026?

```
*Ministry for Women Affairs* (code 051400000000):
• Jimilla: 2025 kasafin da aka amince ₦8.44 biliyan; 2026 kasafin da aka amince ₦7.24 biliyan; bambanci -₦1.21 biliyan (-14.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-02 (typo) ok (3.8s)

**Q:** Compare the Ministry of Comerce and Industry's aproved budget in 2025 and 2026.

```
*Ministry of Commerce and Industry* (code 022200000000):
• Total: 2025 approved budget ₦6.06 billion; 2026 approved budget ₦6.56 billion; change +₦503.51 million (+8.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-03 (hausa) ok (4.3s)

**Q:** Kwatanta approved budget na Ministry of Culture & Tourism a 2025 da 2026.

```
*Ministry of Culture & Tourism* (code 023600000000):
• Jimilla: 2025 kasafin da aka amince ₦1.21 biliyan; 2026 kasafin da aka amince ₦1.42 biliyan; bambanci +₦214.73 miliyan (+17.7%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-04 (hausa) ok (13.9s)

**Q:** Kwatanta approved budget na Social Sector a 2025 da 2026.

```
Daga teburin jimillar kashe kuɗi ta rabe-raben ma'aikata, kasafin Social Sector da aka amince da shi (jimilla) a 2025 shi ne ₦175.57 biliyan, a 2026 kuma shi ne ₦278.88 biliyan.

• 2025 (approved budget, jimilla): ₦175.57 biliyan
• 2026 (approved budget, jimilla): ₦278.88 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-05 (template) ok (4.0s)

**Q:** Compare the Sokoto State Independent Electoral Commission's approved budget in 2025 and 2026.

```
*Sokoto State Independent Electoral Commission* (code 014800000000):
• Total: 2025 approved budget ₦529.14 million; 2026 approved budget ₦460.48 million; change -₦68.67 million (-13.0%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-06 (hausa) ok (3.6s)

**Q:** Kwatanta kasafin kudin Department of Establishment and Pensions da aka amince da shi a 2025 da 2026.

```
*Department of Establishment and Pensions* (code 017300000000):
• Jimilla: 2025 kasafin da aka amince ₦16.17 biliyan; 2026 kasafin da aka amince ₦11.84 biliyan; bambanci -₦4.33 biliyan (-26.8%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-07 (hausa) ok (3.3s)

**Q:** Kwatanta budget na Ministry for Special Duties da aka amince da shi a 2025 da kuma a 2026.

```
*Ministry for Special Duties* (code 016700000000):
• Jimilla: 2025 kasafin da aka amince ₦423.00 miliyan; 2026 kasafin da aka amince ₦829.50 miliyan; bambanci +₦406.50 miliyan (+96.1%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-08 (template) ok (4.4s)

**Q:** Compare the Ministry of Solid Minerals and Natural Resources's approved budget in 2025 and 2026.

```
*Ministry of Solid Minerals and Natural Resources* (code 023300000000):
• Total: 2025 approved budget ₦479.09 million; 2026 approved budget ₦969.94 million; change +₦490.85 million (+102.5%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-09 (template) ok (4.0s)

**Q:** Compare the Ministry of Health's approved budget in 2025 and 2026.

```
*Ministry of Health* (code 052100000000):
• Total: 2025 approved budget ₦52.18 billion; 2026 approved budget ₦124.41 billion; change +₦72.23 billion (+138.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-10 (informal) ok (3.8s)

**Q:** Local Government Service Commission budget 2025 vs 2026?

```
*Local Government Service Commission* (code 014900000000):
• Total: 2025 approved budget ₦555.67 million; 2026 approved budget ₦746.52 million; change +₦190.85 million (+34.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-11 (typo) ok (3.0s)

**Q:** Comapre teh Ministry of Information's approved budget in 2025 and 2026.

```
*Ministry of Information* (code 012300000000):
• Total: 2025 approved budget ₦2.64 billion; 2026 approved budget ₦2.48 billion; change -₦160.40 million (-6.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-12 (code_switched) ok (10.7s)

**Q:** Kwatanta approved budget na Economic Sector na 2025 da 2026 fa?

```
Daga teburin Jimillar Kashe Kudi ta Rarrabuwar Ma'aikatu, kasafin 2025 da aka amince da shi na Fannin Tattalin Arziki (jimilla) shi ne ₦237.36 biliyan. Kasafin 2026 da aka amince da shi na fannin (jimilla) shi ne ₦316.04 biliyan.

• 2025 kasafin da aka amince (jimilla): ₦237.36 biliyan
• 2026 kasafin da aka amince (jimilla): ₦316.04 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-13 (template) ok (4.1s)

**Q:** Compare the Ministry for Skills Acquisition and Entrepreneurship Development's approved budget in 2025 and 2026.

```
*Ministry for Skills Acquisition and Entrepreneurship Development* (code 028900000000):
• Total: 2025 approved budget ₦1.50 billion; 2026 approved budget ₦1.37 billion; change -₦125.00 million (-8.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-14 (template) ok (4.3s)

**Q:** Compare the Ministry of Education's approved budget in 2025 and 2026.

```
*Ministry of Education* (code 051700000000):
• Total: 2025 approved budget ₦59.59 billion; 2026 approved budget ₦68.95 billion; change +₦9.36 billion (+15.7%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-15 (code_switched) ok (3.4s)

**Q:** Kwatanta approved budget na Ministry of Social Welfare & Community Development a 2025 da 2026 fa?

```
*Ministry of Social Welfare & Community Development* (code 055600000000):
• Jimilla: 2025 kasafin da aka amince ₦7.08 biliyan; 2026 kasafin da aka amince ₦5.11 biliyan; bambanci -₦1.97 biliyan (-27.8%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 19
```

## compare-16 (informal) ok (3.6s)

**Q:** State Judiciary's approved budget in 2025 vs 2026?

```
*State Judiciary* (code 031800000000):
• Total: 2025 approved budget ₦6.28 billion; 2026 approved budget ₦8.17 billion; change +₦1.89 billion (+30.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-17 (typo) ok (3.6s)

**Q:** Comapre the Ministry of Youth and Sports Developmet's approved budjet in 2025 and 2026.

```
*Ministry of Youth and Sports Development* (code 051300000000):
• Total: 2025 approved budget ₦4.02 billion; 2026 approved budget ₦17.06 billion; change +₦13.03 billion (+323.8%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-18 (template) ok (3.0s)

**Q:** Compare the Ministry of Works's approved budget in 2025 and 2026.

```
*Ministry of Works* (code 023400000000):
• Total: 2025 approved budget ₦59.39 billion; 2026 approved budget ₦59.17 billion; change -₦227.66 million (-0.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-19 (hausa) ok (3.8s)

**Q:** Kwatanta approved budget na Ministry of Water Resources a 2025 da 2026.

```
*Ministry of Water Resources* (code 025200000000):
• Jimilla: 2025 kasafin da aka amince ₦20.32 biliyan; 2026 kasafin da aka amince ₦44.99 biliyan; bambanci +₦24.67 biliyan (+121.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## share-01 (code_switched) ok (2.9s)

**Q:** JUDICIAL SERVICE COMMISSION 2026 approved budget din, wani share ne capital?

```
*JUDICIAL SERVICE COMMISSION* (code 031801100100):
• Manyan ayyuka: kasafin da aka amince ₦310.00 miliyan; 55.7% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦556.51 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 26
```

## share-02 (hausa) ok (4.0s)

**Q:** Wane kaso na kasafin kudin 2026 da aka amincewa na Ministry of Energy and Petroleum Resources ne kudin jari (capital)?

```
*Ministry of Energy and Petroleum Resources* (code 023100000000):
• Manyan ayyuka: kasafin da aka amince ₦22.47 biliyan; 96.3% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦23.33 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## share-03 (typo) WRONG: missing ['20.1%'] (13.5s)

**Q:** What sahre of the Fertilizer and Agricultral Supplies Company's 2026 aproved budget is capitla?

```
The evidence shows only the capital part of the Fertilizer and Agricultral Supplies Company's 2026 approved budget, which is ₦23.00 million. The company's total 2026 approved budget is not shown in the evidence, so its capital share cannot be given.

• 2026 approved budget, capital: ₦23.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 25
```

## share-04 (informal) ok (5.0s)

**Q:** Water Board's 2026 budget — how much of it is capital?

```
*Water Board* (code 025210200100):
• Capital: approved budget ₦28.30 billion; 91.3% of its total (Kasafi's calculation)
• Total: approved budget ₦30.98 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-05 (template) ok (4.3s)

**Q:** What share of the House of Assembly Service Commission's 2026 approved budget is capital?

```
*House of Assembly Service Commission* (code 011200400100):
• Capital: approved budget ₦525.50 million; 82.9% of its total (Kasafi's calculation)
• Total: approved budget ₦634.28 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 25
```

## share-06 (code_switched) ok (4.6s)

**Q:** Wannan 2026 approved budget na Sokoto College of Legal & Islamic St., what share ne capital?

```
*Sokoto College of Legal & Islamic St.* (code 032600600500):
• Albashi: kasafin da aka amince ₦193.92 miliyan; 17.7% na jimillarsa (lissafin Kasafi)
• Kuɗin gudanarwa: kasafin da aka amince ₦133.50 miliyan; 12.2% na jimillarsa (lissafin Kasafi)
• Manyan ayyuka: kasafin da aka amince ₦770.00 miliyan; 70.2% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦1.10 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 21, 24, 26
```

## share-07 (typo) ok (4.6s)

**Q:** What shrae of the Tenancy Control and Safety of Person Agency's 2026 approved budjet is capital?

```
*Tenancy Control and Safety of Person Agency* (code 032600700500):
• Capital: approved budget ₦72.00 million; 47.1% of its total (Kasafi's calculation)
• Total: approved budget ₦153.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-08 (informal) ok (4.8s)

**Q:** How much of Agency for Persons Living With Disabilities's 2026 budget is capital?

```
*Agency for Persons Living With Disabilities* (code 051300300100):
• Capital: approved budget ₦1.24 billion; 40.4% of its total (Kasafi's calculation)
• Total: approved budget ₦3.07 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-09 (code_switched) ok (4.2s)

**Q:** Approved budget na 2026 na Ministry of Livestocks and Fisheries Development, kaso nawa ne capital?

```
*Ministry of Livestocks and Fisheries Development* (code 026800000000):
• Manyan ayyuka: kasafin da aka amince ₦12.26 biliyan; 90.2% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦13.60 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 26
```

## share-10 (template) ok (3.9s)

**Q:** What share of the Law Reform Commission's 2026 approved budget is capital?

```
*Law Reform Commission* (code 032600200100):
• Capital: approved budget ₦605.17 million; 69.7% of its total (Kasafi's calculation)
• Total: approved budget ₦868.16 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-11 (code_switched) ok (5.3s)

**Q:** State Emergency Management Agency (SEMA) 2026 approved budget din, what share ne capital?

```
*State Emergency Management Agency (SEMA)* (code 011100800100):
• Manyan ayyuka: kasafin da aka amince ₦1.20 biliyan; 90.6% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦1.32 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-12 (typo) ok (3.9s)

**Q:** What shrae of the Sokoto State Housing Cooperation's 2026 aproved budjet is capital?

```
*Sokoto State Housing Cooperation* (code 025300400100):
• Capital: approved budget ₦330.00 million; 87.7% of its total (Kasafi's calculation)
• Total: approved budget ₦376.45 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-13 (hausa) ok (5.5s)

**Q:** Kashi nawa na kasafin 2026 da aka amince wa Ministry of Innovation and Digital Economy ne na capital?

```
*Ministry of Innovation and Digital Economy* (code 027900000000):
• Manyan ayyuka: kasafin da aka amince ₦2.75 biliyan; 76.6% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦3.59 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## share-14 (followup) ok (4.3s)

**Q:** What share of its 2026 approved budget is capital?

```
*International Fund for Agriculture* (code 021510200200):
• Capital: approved budget ₦170.00 million; 56.5% of its total (Kasafi's calculation)
• Total: approved budget ₦301.08 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 25
```

## share-15 (code_switched) ok (4.6s)

**Q:** Ministry for Home Affairs 2026 approved budget din, what share ne capital?

```
*Ministry for Home Affairs* (code 012400000000):
• Manyan ayyuka: kasafin da aka amince ₦2.58 biliyan; 42.3% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦6.11 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-16 (code_switched) ok (4.2s)

**Q:** Wannan 2026 approved budget na Ministry of Culture & Tourism, kashi nawa ne capital?

```
*Ministry of Culture & Tourism* (code 023600000000):
• Manyan ayyuka: kasafin da aka amince ₦788.59 miliyan; 55.3% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦1.42 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## share-17 (code_switched) ok (4.8s)

**Q:** 2026 approved budget na State Newspaper Comp.(The PATH), nawa ne share na capital?

```
*State Newspaper Comp.(The PATH)* (code 012305500100):
• Manyan ayyuka: kasafin da aka amince ₦209.00 miliyan; 69.8% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦299.58 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-18 (informal) ok (4.2s)

**Q:** of the Livestock Development Programme's 2026 budget, how much is capital?

```
*Livestock Development Programme* (code 026800200100):
• Capital: approved budget ₦334.00 million; 90.7% of its total (Kasafi's calculation)
• Total: approved budget ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-19 (typo) ok (4.1s)

**Q:** What sahre of the State Hihg Court's 2026 approved budget is capial?

```
*State High Court* (code 031805100100):
• Capital: approved budget ₦2.13 billion; 41.0% of its total (Kasafi's calculation)
• Total: approved budget ₦5.21 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## false_premise-01 (informal) ok (4.5s)

**Q:** Why did Sokoto State Independent Electoral Commission's approved budget go up from 2025 to 2026?

```
It didn't rise: the approved budget fell from 2025 to 2026, so there is no rise to explain.
*Sokoto State Independent Electoral Commission* (code 014800000000):
• Personnel (salaries): 2025 approved budget ₦102.43 million; 2026 approved budget ₦128.76 million; change +₦26.33 million (+25.7%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦76.00 million; 2026 approved budget ₦106.00 million; change +₦30.00 million (+39.5%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦350.71 million; 2026 approved budget ₦225.71 million; change -₦125.00 million (-35.6%) (Kasafi's calculation)
• Total: 2025 approved budget ₦529.14 million; 2026 approved budget ₦460.48 million; change -₦68.67 million (-13.0%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 12, 14, 16; Sokoto State FY 2026 Budget, p. 16, 19, 22, 25
```

## false_premise-02 (typo) ok (4.2s)

**Q:** Why did teh Ministry of Informaton's approved budjet rise from 2025 to 2026?

```
It didn't rise: the approved budget fell from 2025 to 2026, so there is no rise to explain.
*Ministry of Information* (code 012300000000):
• Personnel (salaries): 2025 approved budget ₦382.95 million; 2026 approved budget ₦399.95 million; change +₦17.00 million (+4.4%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦768.74 million; 2026 approved budget ₦617.34 million; change -₦151.40 million (-19.7%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦1.49 billion; 2026 approved budget ₦1.46 billion; change -₦26.00 million (-1.7%) (Kasafi's calculation)
• Total: 2025 approved budget ₦2.64 billion; 2026 approved budget ₦2.48 billion; change -₦160.40 million (-6.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 12, 14, 16; Sokoto State FY 2026 Budget, p. 16, 19, 22, 25
```

## false_premise-03 (informal) ok (4.6s)

**Q:** why did Ministry of Science and Technology's approved budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry of Science and Technology* (code 022800000000):
• Personnel (salaries): 2025 approved budget ₦1.32 billion; 2026 approved budget ₦1.65 billion; change +₦334.88 million (+25.5%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦689.10 million; 2026 approved budget ₦1.01 billion; change +₦323.90 million (+47.0%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦4.81 billion; 2026 approved budget ₦9.02 billion; change +₦4.21 billion (+87.5%) (Kasafi's calculation)
• Total: 2025 approved budget ₦6.82 billion; 2026 approved budget ₦11.69 billion; change +₦4.87 billion (+71.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 13, 14, 16; Sokoto State FY 2026 Budget, p. 17, 20, 23, 26
```

## false_premise-04 (hausa) ok (3.9s)

**Q:** Me ya sa approved budget na Ministry of Education ya fadi daga 2025 zuwa 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
*Ministry of Education* (code 051700000000):
• Jimilla: 2025 kasafin da aka amince ₦59.59 biliyan; 2026 kasafin da aka amince ₦68.95 biliyan; bambanci +₦9.36 biliyan (+15.7%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## false_premise-05 (followup) ok (4.2s)

**Q:** Why did its approved budget rise from 2025 to 2026?

```
It didn't rise: the approved budget fell from 2025 to 2026, so there is no rise to explain.
*Ministry of Social Welfare & Community Development* (code 055600000000):
• Personnel (salaries): 2025 approved budget ₦94.11 million; 2026 approved budget ₦117.84 million; change +₦23.73 million (+25.2%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦2.19 billion; 2026 approved budget ₦1.28 billion; change -₦909.50 million (-41.6%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦4.80 billion; 2026 approved budget ₦3.72 billion; change -₦1.08 billion (-22.5%) (Kasafi's calculation)
• Total: 2025 approved budget ₦7.08 billion; 2026 approved budget ₦5.11 billion; change -₦1.97 billion (-27.8%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 14, 15, 17; Sokoto State FY 2026 Budget, p. 19, 21, 24, 27
```

## false_premise-06 (typo) ok (4.2s)

**Q:** Why did teh Ministry of Youth and Sports Development's aproved budget fall form 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry of Youth and Sports Development* (code 051300000000):
• Personnel (salaries): 2025 approved budget ₦96.29 million; 2026 approved budget ₦910.76 million; change +₦814.47 million (+845.8%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦1.45 billion; 2026 approved budget ₦2.46 billion; change +₦1.02 billion (+70.1%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦2.48 billion; 2026 approved budget ₦13.68 billion; change +₦11.20 billion (+451.7%) (Kasafi's calculation)
• Total: 2025 approved budget ₦4.02 billion; 2026 approved budget ₦17.06 billion; change +₦13.03 billion (+323.8%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 13, 15, 16; Sokoto State FY 2026 Budget, p. 18, 21, 24, 26
```

## false_premise-07 (template) ok (5.0s)

**Q:** Why did the Ministry of Solid Minerals and Natural Resources's approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry of Solid Minerals and Natural Resources* (code 023300000000):
• Total: 2025 approved budget ₦479.09 million; 2026 approved budget ₦969.94 million; change +₦490.85 million (+102.5%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-08 (template) ok (4.2s)

**Q:** Why did the Ministry of Environment's approved budget rise from 2025 to 2026?

```
It didn't rise: the approved budget fell from 2025 to 2026, so there is no rise to explain.
*Ministry of Environment* (code 053500000000):
• Personnel (salaries): 2025 approved budget ₦660.37 million; 2026 approved budget ₦780.60 million; change +₦120.23 million (+18.2%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦786.00 million; 2026 approved budget ₦1.22 billion; change +₦429.00 million (+54.6%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦23.08 billion; 2026 approved budget ₦18.77 billion; change -₦4.30 billion (-18.6%) (Kasafi's calculation)
• Total: 2025 approved budget ₦24.52 billion; 2026 approved budget ₦20.77 billion; change -₦3.75 billion (-15.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 14, 15, 17; Sokoto State FY 2026 Budget, p. 18, 21, 24, 27
```

## false_premise-09 (followup) ok (4.1s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry for Home Affairs* (code 012400000000):
• Personnel (salaries): 2025 approved budget ₦1.31 billion; 2026 approved budget ₦2.11 billion; change +₦804.86 million (+61.5%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦158.37 million; 2026 approved budget ₦1.42 billion; change +₦1.26 billion (+794.2%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦638.86 million; 2026 approved budget ₦2.58 billion; change +₦1.94 billion (+304.2%) (Kasafi's calculation)
• Total: 2025 approved budget ₦2.11 billion; 2026 approved budget ₦6.11 billion; change +₦4.01 billion (+190.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 13, 14, 16; Sokoto State FY 2026 Budget, p. 16, 19, 22, 25
```

## false_premise-10 (code_switched) ok (15.8s)

**Q:** Me yasa Department of Establishment and Pensions approved budget ya rise daga 2025 to 2026?

```
Kasafin da aka amince da shi bai tashi ba, ya ragu ne. A 2025 jimillar Department of Establishment and Pensions ₦16.17 biliyan ce, a 2026 kuma ₦11.84 biliyan ce (lissafin Kasafi). Dukkanin kudaden biyu kasafin da aka amince da shi ne (allocated), ba kudaden da aka kashe ba.

• Department of Establishment and Pensions (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 017300000000), 2025 Approved Budget: ₦16.17 biliyan
• Department of Establishment and Pensions (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 017300000000), 2026 Approved Budget: ₦11.84 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## false_premise-11 (template) ok (3.7s)

**Q:** Why did the Ministry of Livestocks and Fisheries Development's approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry of Livestocks and Fisheries Development* (code 026800000000):
• Total: 2025 approved budget ₦7.89 billion; 2026 approved budget ₦13.60 billion; change +₦5.71 billion (+72.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-12 (hausa) ok (14.5s)

**Q:** Me ya sa approved budget na Law and Justice ya sauka daga 2025 zuwa 2026?

```
Ba a samu raguwa ba. Kasafin Law and Justice na 2025 ya karu zuwa kasafin 2026, don haka tambayar raguwa ba ta dace ba.

• Law and Justice (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 030000000000), 2025 Approved Budget: ₦10.74 biliyan
• Law and Justice (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 030000000000), 2026 Approved Budget: ₦14.26 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## false_premise-13 (code_switched) ok (3.5s)

**Q:** Me yasa approved budget na Ministry of Commerce and Industry ya drop daga 2025 to 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
*Ministry of Commerce and Industry* (code 022200000000):
• Albashi: 2025 kasafin da aka amince ₦122.77 miliyan; 2026 kasafin da aka amince ₦193.00 miliyan; bambanci +₦70.23 miliyan (+57.2%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦1.04 biliyan; 2026 kasafin da aka amince ₦2.16 biliyan; bambanci +₦1.12 biliyan (+107.5%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦4.89 biliyan; 2026 kasafin da aka amince ₦4.21 biliyan; bambanci -₦686.27 miliyan (-14.0%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦6.06 biliyan; 2026 kasafin da aka amince ₦6.56 biliyan; bambanci +₦503.51 miliyan (+8.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 13, 14, 16; Sokoto State FY 2026 Budget, shafi 17, 20, 23, 25
```

## false_premise-14 (hausa) ok (5.1s)

**Q:** Me ya sa approved budget na Ministry for Special Duties ya ragu daga 2025 zuwa 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
*Ministry for Special Duties* (code 016700000000):
• Albashi: 2025 kasafin da aka amince ₦8.00 miliyan; 2026 kasafin da aka amince ₦12.00 miliyan; bambanci +₦4.00 miliyan (+50.0%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦155.00 miliyan; 2026 kasafin da aka amince ₦195.50 miliyan; bambanci +₦40.50 miliyan (+26.1%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦260.00 miliyan; 2026 kasafin da aka amince ₦622.00 miliyan; bambanci +₦362.00 miliyan (+139.2%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦423.00 miliyan; 2026 kasafin da aka amince ₦829.50 miliyan; bambanci +₦406.50 miliyan (+96.1%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 12, 14, 15; Sokoto State FY 2026 Budget, shafi 16, 19, 22, 25
```

## false_premise-15 (followup) ok (4.9s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry of Health* (code 052100000000):
• Personnel (salaries): 2025 approved budget ₦12.62 billion; 2026 approved budget ₦15.29 billion; change +₦2.67 billion (+21.2%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦3.30 billion; 2026 approved budget ₦4.47 billion; change +₦1.17 billion (+35.3%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦36.26 billion; 2026 approved budget ₦104.64 billion; change +₦68.39 billion (+188.6%) (Kasafi's calculation)
• Total: 2025 approved budget ₦52.18 billion; 2026 approved budget ₦124.41 billion; change +₦72.23 billion (+138.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 13, 15, 16; Sokoto State FY 2026 Budget, p. 18, 21, 24, 27
```

## false_premise-16 (informal) ok (4.1s)

**Q:** Why did the Ministry for Religious Affairs's approved budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry for Religious Affairs* (code 017200000000):
• Personnel (salaries): 2025 approved budget ₦117.15 million; 2026 approved budget ₦358.38 million; change +₦241.23 million (+205.9%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦3.14 billion; 2026 approved budget ₦4.30 billion; change +₦1.16 billion (+36.9%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦8.00 billion; 2026 approved budget ₦13.39 billion; change +₦5.39 billion (+67.4%) (Kasafi's calculation)
• Total: 2025 approved budget ₦11.26 billion; 2026 approved budget ₦18.05 billion; change +₦6.79 billion (+60.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 13, 14, 16; Sokoto State FY 2026 Budget, p. 16, 19, 22, 25
```

## false_premise-17 (typo) ok (4.3s)

**Q:** Why did teh Ministry for Local Government and Chieftancy's approved budjet fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry for Local Government and Chieftancy* (code 055100000000):
• Personnel (salaries): 2025 approved budget ₦145.67 million; 2026 approved budget ₦190.67 million; change +₦45.00 million (+30.9%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦211.97 million; 2026 approved budget ₦317.96 million; change +₦105.99 million (+50.0%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦213.00 million; 2026 approved budget ₦850.44 million; change +₦637.44 million (+299.3%) (Kasafi's calculation)
• Total: 2025 approved budget ₦570.64 million; 2026 approved budget ₦1.36 billion; change +₦788.43 million (+138.2%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 14, 15, 17; Sokoto State FY 2026 Budget, p. 19, 21, 24, 27
```

## false_premise-18 (informal) ok (4.1s)

**Q:** Why did Ministry of Energy and Petroleum Resources's approved budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry of Energy and Petroleum Resources* (code 023100000000):
• Total: 2025 approved budget ₦10.30 billion; 2026 approved budget ₦23.33 billion; change +₦13.04 billion (+126.6%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-19 (followup) ok (4.1s)

**Q:** Why did its approved budget rise from 2025 to 2026?

```
It didn't rise: the approved budget fell from 2025 to 2026, so there is no rise to explain.
*Ministry for Women Affairs* (code 051400000000):
• Total: 2025 approved budget ₦8.44 billion; 2026 approved budget ₦7.24 billion; change -₦1.21 billion (-14.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## not_in_data-01 (code_switched) ok (3.8s)

**Q:** Nawa Teachers Service Board(Secondary Edu. Board) ta spend a Q1 2027?

```
Ba a cikin takardun ba:
• Teachers Service Board(Secondary Edu. Board) 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Teachers Service Board(Secondary Edu. Board) 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-02 (code_switched) WRONG: no mention of what exists (2024–2026) (11.5s)

**Q:** Sokoto Engineering Construction Company approved budget for 2028 nawa ne?

```
⚠️ Ban samo takardar da ta fi dacewa ba (Sokoto State Government 2028 Approved Budget). Amsar da ke ƙasa daga wasu takardun da nake da su ce, ba daga waccan ba.

Sokoto Engineering Construction Company ta samu ₦55.95 miliyan a shekarar 2028 kamar yadda teburin Jimillar Kashewa ta Ma'aikata ya nuna. Wannan adadi kimanta kasafi ne na 2028, ba kuɗin da aka kashe ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## not_in_data-03 (followup) ok (5.3s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Department of Establishment and Pensions 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Department of Establishment and Pensions 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Department of Establishment and Pensions 2027 share of the revised budget spent: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-04 (code_switched) ok (12.7s)

**Q:** Nawa ne State Bureau of Statistics approved budget for 2028?

```
Jimillar State Bureau of Statistics na 2028 da aka nuna a kasafin 2026 ita ce ₦1.84 biliyan. Wannan adadin tsarin hasashe ne na 2028, ba kasafin 2028 da aka amince da shi ba.

• State Bureau of Statistics (hukuma ɗaya, duk kashe kuɗi (jimilla), code 023800400100), 2028 Out-Year Estimate: ₦1.84 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## not_in_data-05 (followup) ok (4.5s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Office of the SSG 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Office of the SSG 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-06 (followup) ok (4.2s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Sokoto Erosion and Watershed Management Agency (SEWMA) 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Sokoto Erosion and Watershed Management Agency (SEWMA) 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-07 (template) WRONG: no mention of what exists (Q2 2026) (13.3s)

**Q:** How much did the Local Government Service Commission spend in Q1 2027?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Local Government Service Commission (ministry total including its agencies, code 014900000000, Total Revenue (including Capital Receipts) by Administrative Classification), 2027 Out-Year Estimate: 0.00 [1]
• Local Government Service Commission (ministry total including its agencies, code 014900000000, Total Revenue (including Capital Receipts) by Administrative Classification), 2027 Out-Year Estimate: ₦2.00 million [2]
• Local Government Service Commission (ministry total including its agencies, code 014900000000, Total Revenue (including Capital Receipts) by Administrative Classification), 2025 Performance January to September: 0.00 [2]

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 5; Sokoto State FY 2026 Budget, p. 7
```

## not_in_data-08 (informal) ok (4.2s)

**Q:** How much did the Arabic and Islamic Education Board spend in Q4 2026?

```
Not in the documents:
• Arabic and Islamic Education Board 2026 spent in Q4: the latest implementation report is Q2 2026
• Arabic and Islamic Education Board 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
• Arabic and Islamic Education Board 2026 share of the revised budget spent: the latest implementation report is Q2 2026
```

## not_in_data-09 (typo) ok (12.1s)

**Q:** How much is the ZAKAT and Endowmant Agency (WAQF)'s aproved budget for 2028?

```
The ZAKAT and Endowment Agency (WAQF)'s figure for 2028 is ₦5.34 billion. In the 2026 budget this is shown as a 2028 Out-Year Estimate, not an approved budget.

• ZAKAT and Endowment Agency (WAQF) (one agency or unit, all spending (total), code 017200700100), 2028 Out-Year Estimate: ₦5.34 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## not_in_data-10 (template) ok (11.3s)

**Q:** How much did the International Fund for Agriculture spend in Q4 2026?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• International Fund for Agriculture (one agency or unit, all spending (total), code 021510200200, Total Expenditure by Administrative Classification), 2026 Q2 Performance: ₦11.93 million [1]
• International Fund for Agriculture (one agency or unit, all spending (total), code 021510200200, Total Expenditure by Administrative Classification), 2026 Q1 Performance: ₦11.63 million [2]
• International Fund for Agriculture (one agency or unit, all spending (total), code 021510200200, Total Expenditure by Administrative Classification), 2026 Performance Year to Date (Q1-Q2): ₦23.56 million [1]

📄 *Sources:* Budget Implementation Report Q2 2026, p. 16; Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## not_in_data-11 (code_switched) ok (4.3s)

**Q:** Nawa House of Assembly Service Commission ta spend a Q1 2027?

```
Ba a cikin takardun ba:
• House of Assembly Service Commission 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• House of Assembly Service Commission 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-12 (typo) ok (5.1s)

**Q:** How muhc did the Liaison Office ABUJA sepnd in Q1 2027?

```
Not in the documents:
• Liaison Office ABUJA 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Liaison Office ABUJA 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Liaison Office ABUJA 2027 share of the revised budget spent: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-13 (code_switched) ok (15.1s)

**Q:** How much be approved budget na State college of basic and remedial studies for 2028?

```
Babu aminceccen kasafin 2028 a wannan takarda; hasashen 2028 kawai aka buga. Hasashen 2028 na State college of basic and remedial studies (duka kashewa) shine ₦3.21 biliyan.

• State college of basic and remedial studies (hukuma ɗaya, duk kashe kuɗi (jimilla), code 056900500100), 2028 Out-Year Estimate: ₦3.21 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## not_in_data-14 (code_switched) ok (4.7s)

**Q:** Nawa Primary School Staff Pension Board ta spend a Q1 2027?

```
Ba a cikin takardun ba:
• Primary School Staff Pension Board 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Primary School Staff Pension Board 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-15 (informal) ok (4.0s)

**Q:** how much did Livestock Development Programme spend in Q1 2027?

```
Not in the documents:
• Livestock Development Programme 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Livestock Development Programme 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-16 (typo) ok (4.7s)

**Q:** How mouch did the Departmant for Rural Roads spend in Q1 2027?

```
Not in the documents:
• Department for Rural Roads 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Department for Rural Roads 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-17 (informal) ok (4.5s)

**Q:** Min of Lands and Housing spent how much in Q4 2026?

```
Not in the documents:
• Min of Lands and Housing 2026 spent in Q4: the latest implementation report is Q2 2026
```

## not_in_data-18 (code_switched) ok (5.1s)

**Q:** Parks and Gardens Agency ta spend nawa a Q4 2026?

```
Ba a cikin takardun ba:
• Parks and Gardens Agency 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Parks and Gardens Agency 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Parks and Gardens Agency 2026 kason kasafin da aka sabunta da aka kashe: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-19 (informal) ok (3.9s)

**Q:** how much did the Sokoto State Housing Cooperation spend in Q1 2027?

```
Not in the documents:
• Sokoto State Housing Cooperation 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Sokoto State Housing Cooperation 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## rank_lga-01 (code_switched) ok (6.8s)

**Q:** Which LGAs 5 ne da most IDPs a Sokoto?

```
Ta ƙaramar hukuma (22), mafi yawa:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143
4. Tureta: 15,068
5. Shagari: 14,850

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-02 (informal) ok (6.5s)

**Q:** Top 10 Sokoto LGAs with most IDPs?

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

## rank_lga-03 (template) ok (6.1s)

**Q:** Which 3 LGAs in Sokoto have the most IDPs?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-01 (template) ok (5.5s)

**Q:** How many IDPs are there in Isa LGA?

```
IOM DTM counts *14,047* IDPs in Isa (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (template) ok (6.0s)

**Q:** How many IDPs are there in Gwadabawa LGA?

```
IOM DTM counts *8,406* IDPs in Gwadabawa (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-03 (typo) ok (4.5s)

**Q:** How mnay IDPs are ther in Tangaza LGA?

```
IOM DTM counts *19,151* IDPs in Tangaza (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-04 (hausa) ok (5.7s)

**Q:** IDPs nawa ne suke a Binji LGA?

```
IOM DTM ta ƙidaya *619* 'yan gudun hijira a Binji (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-05 (code_switched) ok (5.4s)

**Q:** Nawa IDPs are there in Sabon Birni LGA?

```
IOM DTM ta ƙidaya *40,729* 'yan gudun hijira a Sabon Birni (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-06 (hausa) ok (5.2s)

**Q:** 'Yan gudun hijira nawa ne a Gudu LGA?

```
IOM DTM ta ƙidaya *3,147* 'yan gudun hijira a Gudu (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-07 (code_switched) ok (5.8s)

**Q:** IDPs nawa ne there in Kebbe LGA?

```
IOM DTM ta ƙidaya *4,252* 'yan gudun hijira a Kebbe (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-08 (followup) ok (5.5s)

**Q:** How many IDPs are there in it?

```
IOM DTM counts *4,486* IDPs in Sokoto South (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-09 (followup) ok (6.2s)

**Q:** How many IDPs are there in it?

```
IOM DTM counts *2,274* IDPs in Sokoto North (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-10 (code_switched) ok (5.2s)

**Q:** Nawa IDPs ne there in Dange-Shuni LGA?

```
IOM DTM ta ƙidaya *4,615* 'yan gudun hijira a Dange Shuni (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-11 (code_switched) ok (4.8s)

**Q:** IDPs nawa ne in Goronyo LGA?

```
IOM DTM ta ƙidaya *1,926* 'yan gudun hijira a Goronyo (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-12 (hausa) ok (7.2s)

**Q:** Adadin IDPs nawa ne a Silame LGA?

```
IOM DTM ta ƙidaya *3,386* 'yan gudun hijira a Silame (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-13 (code_switched) ok (6.6s)

**Q:** How many IDPs ne a Tureta LGA?

```
IOM DTM ta ƙidaya *15,068* 'yan gudun hijira a Tureta (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-14 (followup) ok (5.6s)

**Q:** How many IDPs are there?

```
IOM DTM counts *8,953* IDPs in Illela (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-15 (template) ok (6.0s)

**Q:** How many IDPs are there in Gada LGA?

```
IOM DTM counts *1,014* IDPs in Gada (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-16 (informal) ok (5.2s)

**Q:** how many IDPs are in Shagari LGA?

```
IOM DTM counts *14,850* IDPs in Shagari (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-17 (typo) ok (5.0s)

**Q:** How mnay IDPs aer there in Tambuwal LGA?

```
IOM DTM counts *17,143* IDPs in Tambuwal (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-18 (informal) ok (5.0s)

**Q:** How many IDPs in Bodinga LGA?

```
IOM DTM counts *1,990* IDPs in Bodinga (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-19 (code_switched) ok (6.1s)

**Q:** Nawa IDPs are there a Kware LGA?

```
IOM DTM ta ƙidaya *1,039* 'yan gudun hijira a Kware (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## trend-01 (template) ok (6.6s)

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
