# Generated coverage run

Cases: cases-688656.json (draw seed 688656), form seed 1

156 cases: wrong 10 (6.4%), of them wrong agency 2 | median 4.2s

| family | wrong | of |
|---|---|---|
| compare | 0 | 19 |
| false_premise | 3 | 19 |
| lookup | 0 | 19 |
| lookup_lga | 0 | 19 |
| not_in_data | 3 | 19 |
| rank_lga | 0 | 3 |
| share | 2 | 19 |
| spend_quarter | 1 | 19 |
| split | 1 | 19 |
| trend | 0 | 1 |

| form | wrong | of |
|---|---|---|
| code_switched | 2 | 34 |
| followup | 2 | 21 |
| hausa | 0 | 23 |
| informal | 4 | 22 |
| template | 0 | 28 |
| typo | 2 | 28 |

```
Cost of this run:
  Baseten: 41 calls, 297,957 prompt tokens (76,544 cached), 18,161 output tokens -> $0.37
  Meta: 399 calls, 1,431,361 prompt tokens (738,531 cached), 303,787 output tokens -> $2.27
  models together: $2.63 (prices per 1M tokens from settings kasafi_price_*)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0)
peak memory: 262 MB
```

## lookup-01 (code_switched) ok (11.8s)

**Q:** Nawa aka approve wa Ministry of Youth and Sports Development a 2025 budget?

```
An amince wa Ministry of Youth and Sports Development jimilla ₦4.02 biliyan a kasafin 2025. Wannan adadin kasafi ne da aka amince da shi, ba kuɗi da aka kashe ba.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12
```

## lookup-02 (template) ok (8.7s)

**Q:** How much was approved for the Ministry Careers & Special Services in the 2025 budget?

```
The 2025 approved budget (total) for Ministry Careers & Special Services is ₦10.57 billion.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11
```

## lookup-03 (followup) ok (10.1s)

**Q:** And how much was approved for it in the 2025 budget?

```
The 2025 approved budget (total) for the Department of Establishment and Pensions is ₦16.17 billion from the Total Expenditure by Administrative Classification table. By Q1–Q4 2025 the department had spent ₦12.54 billion (98.9% of the final budget).

• 2025 approved budget (personnel): ₦15.97 billion
• 2025 approved budget (overhead): ₦205.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 13, 14; Budget Implementation Report Q4 2025, p. 17
```

## lookup-04 (code_switched) ok (10.6s)

**Q:** Nawa aka approve wa Local Government Service Commission for 2025 budget?

```
Daga teburin Jimillar Kashe ta Ma'aikata, an amince da jimillar ₦555.67 miliyan ga Local Government Service Commission a kasafin 2025. Abin da aka kashe a Q1–Q4 2025 ya kai ₦98.19 miliyan (17.7% na kasafin ƙarshe).

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Budget Implementation Report Q4 2025, shafi 16
```

## lookup-05 (hausa) ok (10.1s)

**Q:** Nawa aka amince wa Ministry of Justice a kasafin kudin 2026?

```
An amince wa Ministry of Justice ₦6.09 biliyan a kasafin 2026 (jimilla, daga teburin Total Expenditure by Administrative Classification). Wannan kuɗi ne da aka amince, ba wanda aka kashe ba; a Janairu–Satumba 2025 aka kashe ₦2.15 biliyan.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
```

## lookup-06 (hausa) ok (10.2s)

**Q:** Nawa aka amince wa Ministry of Budget and Economic Planning a kasafin kudin 2025?

```
A kasafin 2025 (jimilla), an amince wa Ministry of Budget and Economic Planning ₦4.03 biliyan. Wannan adadin kasafin da aka amince da shi ne, ba kuɗi da aka kashe ba.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-07 (template) ok (9.9s)

**Q:** How much was approved for the State Judiciary in the 2025 budget?

```
The State Government approved ₦6.28 billion for the State Judiciary in the 2025 budget. This is the total allocated (budgeted) amount from the Total Expenditure by Administrative Classification table.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12
```

## lookup-08 (template) ok (9.6s)

**Q:** How much was approved for the Office of Head of Service in the 2024 budget?

```
The approved total for the Office of Head of Service in the 2024 budget was ₦4.65 billion. This figure is the approved allocation (total) from the Total Expenditure table.

• 2024 approved budget (total): ₦4.65 billion

📄 *Sources:* Sokoto State Government 2024 Approved Budget, p. 41
```

## lookup-09 (code_switched) ok (12.9s)

**Q:** Ministry of Innovation and Digital Economy ta samu nawa a budget na 2025?

```
Ma'aikatar Innovation and Digital Economy ta samu ₦1.35 biliyan a kasafin 2025 da aka amince da shi (jimilla). Wannan adadin da aka ware ne, ba wanda aka kashe ba.

• 2025 kasafin da aka amince (albashi): ₦60.01 miliyan
• 2025 kasafin da aka amince (kuɗin gudanarwa): ₦143.88 miliyan
• 2025 kasafin da aka amince (manyan ayyuka): ₦1.14 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 13, 14, 16
```

## lookup-10 (code_switched) ok (9.2s)

**Q:** Ministry of Water Resources ta samu nawa a 2025 budget?

```
Ma'aikatar Albarkatun Ruwa ta samu jimilla ₦20.32 biliyan a kasafin 2025 da aka amince da shi. Daga Janairu zuwa Satumba 2025 an kashe ₦12.79 biliyan (48.2% na kasafin da aka sabunta).

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State Budget Implementation Report Q3 2025, shafi 18
```

## lookup-11 (followup) ok (9.3s)

**Q:** How much was approved for it in the 2026 budget?

```
The 2026 approved budget (total) for the Ministry of Lands and Housing is ₦35.78 billion. Of that, ₦34.90 billion is capital.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## lookup-12 (code_switched) ok (10.6s)

**Q:** Nawa aka approve wa Ministry of Agriculture & Natural Resource a 2026 budget?

```
An amince da jimilla ₦17.05 biliyan ga Ministry of Agriculture & Natural Resource a kasafin 2026. Wannan kuɗi ne da aka amince da shi a kasafi, ba kuɗi da aka kashe ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## lookup-13 (typo) ok (10.3s)

**Q:** How much was apprroved for the Office of the SSG in the 2024 budjet?

```
The Office of the SSG was allocated ₦13.79 billion as its 2024 approved budget (total) from the Total Expenditure by Administrative Classification table. It spent ₦31.48 billion in (Q1–Q4 2024) (87.0% of the revised budget).

📄 *Sources:* Sokoto State Government 2024 Approved Budget, p. 40; Budget Performance Report Q4 2024, p. 16
```

## lookup-14 (typo) ok (8.1s)

**Q:** How muhc was aproved for the Civil Service Commission in the 2026 budget?

```
The 2026 approved budget (total) for the Civil Service Commission is ₦403.14 million. This figure is the allocation shown in the Total Expenditure by Administrative Classification table.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
```

## lookup-15 (typo) ok (8.5s)

**Q:** How mch was aproved for the Ministry of Environment in the 2024 budjet?

```
The 2024 approved budget (total) for the Ministry of Environment was ₦4.79 billion. Full-year spending in 2024 was ₦3.97 billion (Q1–Q4 2024).

📄 *Sources:* Sokoto State Government 2024 Approved Budget, p. 45; Sokoto State FY 2026 Budget, p. 18; Budget Performance Report Q4 2024, p. 20
```

## lookup-16 (template) ok (12.2s)

**Q:** How much was approved for the Ministry for Religious Affairs in the 2026 budget?

```
The 2026 approved budget (total) for the Ministry for Religious Affairs is ₦18.05 billion from the Total Expenditure by Administrative Classification table. Spending for January–September 2025 was ₦6.81 billion, which is spent, not allocated.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
```

## lookup-17 (followup) ok (9.2s)

**Q:** How much was approved for it in the 2025 budget?

```
The 2025 approved budget (total) for the Ministry for Special Duties is ₦423.00 million. This is the allocated amount from the Total Expenditure table.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11
```

## lookup-18 (typo) ok (11.9s)

**Q:** How much was aproved for the Ministry for Skils Acquisition and Entrepreneurship Development in the 2025 budjet?

```
The ministry was allocated ₦1.50 billion in the 2025 approved budget (total). It spent ₦30.50 million on capital in Q1–Q4 2025 (2.5% of the final budget).

• 2025 approved budget (capital): ₦1.20 billion
• 2025 approved budget (overhead): ₦297.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 15, 16; Budget Implementation Report Q4 2025, p. 29
```

## lookup-19 (informal) ok (10.5s)

**Q:** How much did Ministry of Livestocks and Fisheries Development get in the 2026 budget?

```
The Ministry of Livestocks and Fisheries Development was allocated ₦13.60 billion in the 2026 approved budget (total). It spent ₦2.92 billion in January–September 2025 only.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18
```

## split-01 (typo) ok (4.0s)

**Q:** What are teh personnel, overhead and captal allocations of the Surveyor General Office in 2026?

```
*Surveyor General Office* (code 025300300100):
• Personnel (salaries): approved budget ₦17.62 million
• Overhead (running costs): approved budget ₦67.70 million
• Capital: approved budget ₦286.50 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-02 (followup) ok (3.4s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
*Hisbah Board Sokoto* (code 017200700200):
• Personnel (salaries): approved budget ₦257.17 million
• Overhead (running costs): approved budget ₦338.50 million
• Capital: approved budget ₦294.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-03 (template) ok (4.3s)

**Q:** What are the personnel, overhead and capital allocations of the Ministry for Basic Education in 2025?

```
*Ministry for Basic Education* (code 051700100100):
• Personnel (salaries): approved budget ₦1.18 billion
• Overhead (running costs): approved budget ₦4.92 billion
• Capital: approved budget ₦29.25 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-04 (typo) ok (3.0s)

**Q:** What are the personnel, overhaed and capial allocations of the Ministry of Livestocks and Fisheries Development in 2025?

```
*Ministry of Livestocks and Fisheries Development* (code 026800000000):
• Personnel (salaries): approved budget ₦928.40 million
• Overhead (running costs): approved budget ₦130.75 million
• Capital: approved budget ₦6.84 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-05 (hausa) ok (3.8s)

**Q:** Menene allocation na personnel, overhead da capital da aka bai wa Tenancy Control and Safety of Person Agency a shekarar 2026?

```
*Tenancy Control and Safety of Person Agency* (code 032600700500):
• Albashi: kasafin da aka amince ₦20.00 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦61.00 miliyan
• Manyan ayyuka: kasafin da aka amince ₦72.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 21, 24, 26
```

## split-06 (followup) WRONG: missing ['7,073,000,000.00', '22,558,500,000.00'] (15.6s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
The SSG's Office has a 2026 approved personnel allocation of ₦4.82 billion. Its 2026 overhead and capital totals were not found in the evidence.

• 2026 approved budget (personnel): ₦4.82 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19
```

## split-07 (typo) ok (3.9s)

**Q:** What are teh personnel, overhead and capial allocations of the Shehu Shagari University of Education in 2025?

```
*Shehu Shagari University of Education* (code 056905600100):
• Personnel (salaries): approved budget ₦506.18 million
• Overhead (running costs): approved budget ₦837.00 million
• Capital: approved budget ₦1.59 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-08 (followup) ok (3.9s)

**Q:** And what are its personnel, overhead and capital allocations in 2026?

```
*Primary School Staff Pension Board* (code 011103500200):
• Personnel (salaries): approved budget ₦39.34 million
• Overhead (running costs): approved budget ₦21.00 million
• Capital: approved budget ₦0.00

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-09 (typo) ok (3.3s)

**Q:** What are teh personnel, overhead and captial allocations of the Fire Service in 2026?

```
*Fire Service* (code 012400800100):
• Personnel (salaries): approved budget ₦250.77 million
• Overhead (running costs): approved budget ₦94.06 million
• Capital: approved budget ₦343.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-10 (hausa) ok (3.6s)

**Q:** Menene kason personnel, overhead da capital na International Fund for Agriculture a 2025?

```
A 2025, an ware wa International Fund for Agriculture (code 021510200200) ₦252.81 miliyan: ₦33.68 miliyan na albashi, ₦49.13 miliyan na kuɗin gudanarwa, da ₦170.00 miliyan na manyan ayyuka. A 2024 an ware masa ₦55.81 miliyan (kasafin ƙarshe), kuma an kashe ₦35.88 miliyan a duk shekarar (64.3%). Zuwa ƙarshen Disamba 2025, an kashe ₦39.60 miliyan (15.7% na kasafinsa). Yana da manyan ayyuka 2; ga mafi girma a ƙasa.

Mafi girma:
• Purchase of fertilizer, insecticides, herbicides, pumping machines, seeds IFAD CASP (counterpart), State Wide: ₦150.00 miliyan
• Rehabilitation of offices in 23 LGAs and sustainance of former programme (CBARDP), State Wide: ₦20.00 miliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 13, 14, 16, 33; Budget Performance Report Q4 2024, shafi 17; Budget Implementation Report Q4 2025, shafi 17
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## split-11 (typo) ok (2.8s)

**Q:** What are teh personnel, overhead and capital alocations of the Ministry of Transport in 2026?

```
*Ministry of Transport* (code 022900000000):
• Personnel (salaries): approved budget ₦100.00 million
• Overhead (running costs): approved budget ₦3.10 billion
• Capital: approved budget ₦47.67 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-12 (followup) ok (4.5s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
*House of Assembly Service Commission* (code 011200400100):
• Personnel (salaries): approved budget ₦65.78 million
• Overhead (running costs): approved budget ₦26.80 million
• Capital: approved budget ₦19.40 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 14, 15
```

## split-13 (typo) ok (3.4s)

**Q:** What are teh personnel, overhead and capiatl allocations of the Agency for Persons Living With Disabilites in 2026?

```
*Agency for Persons Living With Disabilities* (code 051300300100):
• Personnel (salaries): approved budget ₦827.90 million
• Overhead (running costs): approved budget ₦1.00 billion
• Capital: approved budget ₦1.24 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 26
```

## split-14 (hausa) ok (12.4s)

**Q:** Nawa ne kudin personnel, overhead da capital na Shehu Shagari Collage of Education Sokoto a 2025?

```
*Shehu Shagari Collage of Education Sokoto* (code 056900300100):
• Albashi: kasafin da aka amince ₦2.46 biliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦41.47 miliyan
• Manyan ayyuka: kasafin da aka amince ₦975.20 miliyan
Ba a cikin takardun ba:
• Shehu Shagari Collage of Education Sokoto Albashi 2025 kasafin da aka sabunta: kasafin bai buga layin Albashi nasa ba
• Shehu Shagari Collage of Education Sokoto Kuɗin gudanarwa 2025 kasafin da aka sabunta: kasafin bai buga layin Kuɗin gudanarwa nasa ba
• Shehu Shagari Collage of Education Sokoto Manyan ayyuka 2025 kasafin da aka sabunta: kasafin bai buga layin Manyan ayyuka nasa ba

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 13, 15, 16
```

## split-15 (informal) ok (11.1s)

**Q:** Personnel, overhead & capital for Ministry of Budget and Economic Planning in 2025?

```
In 2025 the Ministry of Budget and Economic Planning was allocated ₦146.66 million for personnel, ₦1.90 billion for overhead and ₦1.98 billion for capital. It spent ₦146.54 million on personnel (99.9% of the final budget) in Q1–Q4 2025, ₦712.18 million on overhead (37.6% of the final budget) in Q1–Q4 2025 and ₦213.87 million on capital (11.9% of the final budget) in Q1–Q4 2025. Original Budget figures are allocations and Year to Date figures are spent.

• 2025 final budget (personnel): ₦146.66 million
• 2025 final budget (overhead): ₦1.90 billion
• 2025 final budget (capital): ₦1.80 billion

📄 *Sources:* Budget Implementation Report Q4 2025, p. 21, 25, 29
```

## split-16 (hausa) ok (4.0s)

**Q:** Nawa aka ware wa Government Printing Press a 2026 don personnel, overhead da capital?

```
*Government Printing Press* (code 012400900100):
• Albashi: kasafin da aka amince ₦24.40 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦22.50 miliyan
• Manyan ayyuka: kasafin da aka amince ₦50.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 19, 22, 25
```

## split-17 (followup) ok (2.9s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
*Sultan Maccido Institute for Qur'ani & General Studies* (code 051700260100):
• Personnel (salaries): approved budget ₦132.00 million
• Overhead (running costs): approved budget ₦142.05 million
• Capital: approved budget ₦4.32 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-18 (typo) ok (4.1s)

**Q:** What are the personel, overheard and capital allocations of the Sokoto State Rima Televiosn (Rtv) in 2026?

```
*Sokoto State Rima Televiosn (Rtv)* (code 012300300100):
• Personnel (salaries): approved budget ₦100.86 million
• Overhead (running costs): approved budget ₦18.96 million
• Capital: approved budget ₦30.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-19 (hausa) ok (3.9s)

**Q:** Menene kason personnel, overhead da capital da aka ware wa Female Education Board a 2025?

```
*Female Education Board* (code 051705700100):
• Albashi: kasafin da aka amince ₦45.35 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦425.65 miliyan
• Manyan ayyuka: kasafin da aka amince ₦670.00 miliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 13, 15, 16
```

## spend_quarter-01 (hausa) ok (12.1s)

**Q:** Nawa Hospitals Services Magt. Board ta kashe har zuwa karshen Q3 2025, idan aka kwatanta da revised budget dinta?

```
Revised budget na Hospitals Services Magt. Board na 2025 (jimilla) ₦4.40 biliyan ne. Har ƙarshen Q3 2025 (Q1–Q3) ta kashe ₦3.76 biliyan, wato 85.6% na kasafin da aka sabunta. Ragowar kuɗi ₦635.35 miliyan ne.

• 2025 Q3 da aka kashe (jimilla): ₦1.17 biliyan (Q3 2025 kaɗai)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 19
```

## spend_quarter-02 (template) ok (3.8s)

**Q:** How much had the Bureau for Public Procurement and Price Intelligence spent by the end of Q3 2025, against its revised budget?

```
*Bureau for Public Procurement and Price Intelligence* (code 011101000100):
• Total: revised budget ₦217.61 million; spent so far (Q1–Q3) ₦36.61 million; share of the revised budget spent 16.8% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 16
```

## spend_quarter-03 (template) ok (8.5s)

**Q:** How much had the Livestock Development Programme spent by the end of Q3 2025, against its revised budget?

```
The Livestock Development Programme's revised budget for 2025 was ₦300.87 million. By the end of Q3 2025 it had spent ₦43.60 million.

• Livestock Development Programme (one agency or unit, all spending (total), code 026800200100) [Total Expenditure by Administrative Classification], 2025 Revised Budget: ₦300.87 million
• Livestock Development Programme (one agency or unit, all spending (total), code 026800200100) [Total Expenditure by Administrative Classification], 2025 Performance Year to Date (Q1-Q3): ₦43.60 million

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
_Reply *show working* to see the rows and arithmetic._
```

## spend_quarter-04 (typo) ok (3.9s)

**Q:** How much had the College of Nursing Sciences, Tambuwal spnet by the end of Q4 2024, against its revsied budget?

```
*College of Nursing Sciences, Tambuwal* (code 052110400200):
• Total: revised budget ₦547.02 million; spent so far (Q1–Q4) ₦193.76 million; share of the revised budget spent 35.4% (Kasafi's calculation)

📄 *Sources:* Budget Performance Report Q4 2024, p. 20
```

## spend_quarter-05 (code_switched) ok (3.4s)

**Q:** Rural Water and Sanitation Agency ta kashe nawa by the end of Q4 2024, against revised budget dinta?

```
*Rural Water and Sanitation Agency* (code 025210300100):
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q4) ₦78.03 miliyan; kasafin da aka sabunta ₦672.50 miliyan; kason kasafin da aka sabunta da aka kashe 11.6% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 18
```

## spend_quarter-06 (hausa) ok (3.3s)

**Q:** Nawa Sokoto Road Maintenance Agency ta kashe har zuwa karshen Q3 2025, idan aka kwatanta da revised budget dinta?

```
*Sokoto Road Maintenance Agency* (code 023400400100):
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q3) ₦168.82 miliyan; kasafin da aka sabunta ₦455.25 miliyan; kason kasafin da aka sabunta da aka kashe 37.1% (lissafin Kasafi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 18
```

## spend_quarter-07 (informal) ok (3.3s)

**Q:** how much did Department for Human Rights spend by end Q2 2026 vs its revised budget?

```
*Department for Human Rights* (code 016102100500):
• Total: revised budget ₦94.80 million; spent so far (Q1–Q2) ₦2.50 million; share of the revised budget spent 2.6% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 15
```

## spend_quarter-08 (followup) ok (3.2s)

**Q:** How much had it spent by the end of Q4 2024, against its revised budget?

```
*Primary Health Care Development Agency* (code 052100300100):
• Total: revised budget ₦2.55 billion; spent so far (Q1–Q4) ₦1.02 billion; share of the revised budget spent 40.0% (Kasafi's calculation)

📄 *Sources:* Budget Performance Report Q4 2024, p. 20
```

## spend_quarter-09 (typo) ok (3.3s)

**Q:** How muhc had the Sokoto Central Market spent by teh end of Q3 2025, against its revised budget?

```
*Sokoto Central Market* (code 022205500100):
• Total: revised budget ₦138.73 million; spent so far (Q1–Q3) ₦0.00; share of the revised budget spent 0.0% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 17
```

## spend_quarter-10 (informal) ok (3.9s)

**Q:** how much had State Universal Basic Education Board (SUBEB) spent by end of Q2 2026 vs its revised budget?

```
*State Universal Basic Education Board (SUBEB)* (code 051700300100):
• Total: revised budget ₦10.73 billion; spent so far (Q1–Q2) ₦418.46 million; share of the revised budget spent 3.9% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 17
```

## spend_quarter-11 (hausa) ok (8.7s)

**Q:** Nawa International Fund for Agriculture ya kashe har zuwa karshen Q4 2024 idan aka kwatanta da revised budget dinsa?

```
International Fund for Agriculture ta kashe ₦35.88 miliyan daga cikin revised budget na 2024 mai ₦55.81 miliyan har zuwa karshen Q4 2024. Wannan 64.3% (lissafin Kasafi) na kasafin da aka kashe ne.

• International Fund for Agriculture (hukuma ɗaya, duk kashe kuɗi (jimilla), code 021510200200) [Total Expenditure by Administrative Classification], 2024 Revised Budget: ₦55.81 miliyan
• International Fund for Agriculture (hukuma ɗaya, duk kashe kuɗi (jimilla), code 021510200200) [Total Expenditure by Administrative Classification], 2024 Performance Year to Date (Q1-Q4): ₦35.88 miliyan

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 17
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## spend_quarter-12 (followup) WRONG: missing ['323,000,138.00'] (9.4s)

**Q:** How much had it spent by the end of Q3 2025 against its revised budget?

```
By the end of Q3 2025 (Q1–Q3 only) the Ministry had spent ₦59.83 million. That is 18.5% of its revised budget, so this is spent money, not the budgeted amount.

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 16
```

## spend_quarter-13 (informal) ok (3.2s)

**Q:** How much did State Library Board spend by end of Q3 2025 vs its revised budget?

```
*State Library Board* (code 051700800100):
• Total: spent so far (Q1–Q3) ₦127.28 million; revised budget ₦309.93 million; share of the revised budget spent 41.1% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 19
```

## spend_quarter-14 (code_switched) ok (4.0s)

**Q:** Nawa Community and Social Development Agency ta spend by the end of Q3 2025 against revised budget dinta?

```
*Community and Social Development Agency* (code 016102100600):
• Jimilla: kasafin da aka sabunta ₦630.00 miliyan; abin da aka kashe zuwa yanzu (Q1–Q3) ₦1.80 miliyan; kason kasafin da aka sabunta da aka kashe 0.3% (lissafin Kasafi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 16
```

## spend_quarter-15 (code_switched) ok (3.8s)

**Q:** Office of the Deputy Governor ta spend nawa by the end of Q2 2026 against revised budget dinta?

```
*Office of the Deputy Governor* (code 011100100200):
• Jimilla: kasafin da aka sabunta ₦1.71 biliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦519.95 miliyan; kason kasafin da aka sabunta da aka kashe 30.4% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 15
```

## spend_quarter-16 (template) ok (9.1s)

**Q:** How much had the POVERTY REDUCTION PROGRAMME spent by the end of Q2 2026, against its revised budget?

```
• Share (↑ ÷ ↓): 1.0% (Kasafi's calculation)

• POVERTY REDUCTION PROGRAMME (one agency or unit, all spending (total), code 011102000100) [Total Expenditure by Administrative Classification], 2026 Performance Year to Date (Q1-Q2): ₦21.63 million ↑
• POVERTY REDUCTION PROGRAMME (one agency or unit, all spending (total), code 011102000100) [Total Expenditure by Administrative Classification], 2026 Revised Budget: ₦2.24 billion ↓

📄 *Sources:* Budget Implementation Report Q2 2026, p. 15
_Reply *show working* to see the rows and arithmetic._
```

## spend_quarter-17 (informal) ok (3.7s)

**Q:** How much had Ministry for Local Government and Chieftancy spent by end of Q2 2026 vs its revised budget?

```
*Ministry for Local Government and Chieftancy* (code 055100000000):
• Total: spent so far (Q1–Q2) ₦99.36 million; revised budget ₦1.36 billion; share of the revised budget spent 7.3% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## spend_quarter-18 (template) ok (4.2s)

**Q:** How much had the Department for Security Matters spent by the end of Q3 2025, against its revised budget?

```
*Department for Security Matters* (code 017000100200):
• Total: spent so far (Q1–Q3) ₦6.78 billion; revised budget ₦10.57 billion; share of the revised budget spent 64.2% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 17
```

## spend_quarter-19 (template) ok (8.3s)

**Q:** How much had the Social Investment Programme spent by the end of Q3 2025, against its revised budget?

```
The Social Investment Programme's 2025 revised budget was ₦364.00 million. By the end of Q3 2025 it had spent ₦329.76 million, which is 90.6% (Kasafi's calculation) of the revised budget.

• Social Investment Programme (one agency or unit, all spending (total), code 023800300400) [Total Expenditure by Administrative Classification], 2025 Revised Budget: ₦364.00 million
• Social Investment Programme (one agency or unit, all spending (total), code 023800300400) [Total Expenditure by Administrative Classification], 2025 Performance Year to Date (Q1-Q3): ₦329.76 million

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
_Reply *show working* to see the rows and arithmetic._
```

## compare-01 (code_switched) ok (3.6s)

**Q:** Kwatanta mana approved budget na Government House, 2025 da 2026 fa?

```
*Government House* (code 011100000000):
• Jimilla: 2025 kasafin da aka amince ₦14.03 biliyan; 2026 kasafin da aka amince ₦18.53 biliyan; bambanci +₦4.50 biliyan (+32.1%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-02 (typo) ok (3.2s)

**Q:** Comapre the Ministry for Special Duites's aproved budget in 2025 and 2026.

```
*Ministry for Special Duties* (code 016700000000):
• Total: 2025 approved budget ₦423.00 million; 2026 approved budget ₦829.50 million; change +₦406.50 million (+96.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-03 (hausa) ok (2.9s)

**Q:** Kwatanta approved budget na Ministry of Environment a 2025 da kuma 2026.

```
*Ministry of Environment* (code 053500000000):
• Jimilla: 2025 kasafin da aka amince ₦24.52 biliyan; 2026 kasafin da aka amince ₦20.77 biliyan; bambanci -₦3.75 biliyan (-15.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-04 (hausa) ok (3.6s)

**Q:** Kwatanta kasafin kuɗin Ministry of Commerce and Industry da aka amince da shi a 2025 da 2026.

```
*Ministry of Commerce and Industry* (code 022200000000):
• Jimilla: 2025 kasafin da aka amince ₦6.06 biliyan; 2026 kasafin da aka amince ₦6.56 biliyan; bambanci +₦503.51 miliyan (+8.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-05 (template) ok (2.4s)

**Q:** Compare the Local Government Service Commission's approved budget in 2025 and 2026.

```
*Local Government Service Commission* (code 014900000000):
• Total: 2025 approved budget ₦555.67 million; 2026 approved budget ₦746.52 million; change +₦190.85 million (+34.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-06 (hausa) ok (2.7s)

**Q:** Kwatanta approved budget na Ministry for Higher Education a 2025 da 2026.

```
*Ministry for Higher Education* (code 056900000000):
• Jimilla: 2025 kasafin da aka amince ₦19.15 biliyan; 2026 kasafin da aka amince ₦33.99 biliyan; bambanci +₦14.83 biliyan (+77.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-07 (hausa) ok (3.2s)

**Q:** Kwatanta approved budget na Sokoto State Independent Electoral Commission a 2025 da 2026?

```
*Sokoto State Independent Electoral Commission* (code 014800000000):
• Jimilla: 2025 kasafin da aka amince ₦529.14 miliyan; 2026 kasafin da aka amince ₦460.48 miliyan; bambanci -₦68.67 miliyan (-13.0%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-08 (template) ok (2.9s)

**Q:** Compare the Ministry for Skills Acquisition and Entrepreneurship Development's approved budget in 2025 and 2026.

```
*Ministry for Skills Acquisition and Entrepreneurship Development* (code 028900000000):
• Total: 2025 approved budget ₦1.50 billion; 2026 approved budget ₦1.37 billion; change -₦125.00 million (-8.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-09 (template) ok (3.1s)

**Q:** Compare the Ministry of Works's approved budget in 2025 and 2026.

```
*Ministry of Works* (code 023400000000):
• Total: 2025 approved budget ₦59.39 billion; 2026 approved budget ₦59.17 billion; change -₦227.66 million (-0.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-10 (informal) ok (3.2s)

**Q:** Ministry for Women Affairs approved budget 2025 vs 2026 - compare?

```
*Ministry for Women Affairs* (code 051400000000):
• Total: 2025 approved budget ₦8.44 billion; 2026 approved budget ₦7.24 billion; change -₦1.21 billion (-14.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-11 (typo) ok (11.6s)

**Q:** Compare teh Administration Sector's approved budjet in 2025 and 2026.

```
The Administration Sector approved budget (total) was ₦103.22 billion in 2025 and ₦149.52 billion in 2026. Both figures are from Total Expenditure by Administrative Classification tables.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-12 (code_switched) ok (3.6s)

**Q:** Kwatanta approved budget na Ministry for Religious Affairs na 2025 da 2026 fa?

```
*Ministry for Religious Affairs* (code 017200000000):
• Jimilla: 2025 kasafin da aka amince ₦11.26 biliyan; 2026 kasafin da aka amince ₦18.05 biliyan; bambanci +₦6.79 biliyan (+60.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-13 (template) ok (3.6s)

**Q:** Compare the Ministry of Innovation and Digital Economy's approved budget in 2025 and 2026.

```
*Ministry of Innovation and Digital Economy* (code 027900000000):
• Total: 2025 approved budget ₦1.35 billion; 2026 approved budget ₦3.59 billion; change +₦2.24 billion (+166.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-14 (template) ok (3.0s)

**Q:** Compare the Department of Establishment and Pensions's approved budget in 2025 and 2026.

```
*Department of Establishment and Pensions* (code 017300000000):
• Total: 2025 approved budget ₦16.17 billion; 2026 approved budget ₦11.84 billion; change -₦4.33 billion (-26.8%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-15 (code_switched) ok (3.5s)

**Q:** Kwatanta approved budget na Fiscal Responsibility Commission a 2025 da 2026 mana?

```
*Fiscal Responsibility Commission* (code 025000000000):
• Jimilla: 2025 kasafin da aka amince ₦58.99 miliyan; 2026 kasafin da aka amince ₦60.99 miliyan; bambanci +₦2.00 miliyan (+3.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-16 (informal) ok (7.3s)

**Q:** Law and Justice approved budget 2025 vs 2026 - compare?

```
The approved budget for Law and Justice was ₦10.74 billion in 2025 and ₦14.26 billion in 2026. That is an increase of ₦3.52 billion (Kasafi's calculation), or 32.8% (Kasafi's calculation).

• Law and Justice (ministry total including its agencies, all spending (total), code 030000000000), 2025 Approved Budget: ₦10.74 billion
• Law and Justice (ministry total including its agencies, all spending (total), code 030000000000), 2026 Approved Budget: ₦14.26 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
_Reply *show working* to see the rows and arithmetic._
```

## compare-17 (typo) ok (3.9s)

**Q:** Comprae the Ministry of Information's aproved budget in 2025 and 2026.

```
*Ministry of Information* (code 012300000000):
• Total: 2025 approved budget ₦2.64 billion; 2026 approved budget ₦2.48 billion; change -₦160.40 million (-6.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-18 (template) ok (3.1s)

**Q:** Compare the Ministry of Solid Minerals and Natural Resources's approved budget in 2025 and 2026.

```
*Ministry of Solid Minerals and Natural Resources* (code 023300000000):
• Total: 2025 approved budget ₦479.09 million; 2026 approved budget ₦969.94 million; change +₦490.85 million (+102.5%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-19 (hausa) ok (3.2s)

**Q:** Kwatanta kasafin kudin Ministry of Agriculture & Natural Resource da aka amince da shi a 2025 da 2026.

```
*Ministry of Agriculture & Natural Resource* (code 021500000000):
• Jimilla: 2025 kasafin da aka amince ₦19.09 biliyan; 2026 kasafin da aka amince ₦17.05 biliyan; bambanci -₦2.04 biliyan (-10.7%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## share-01 (code_switched) ok (3.9s)

**Q:** Surveyor General Office 2026 approved budget din, kashi nawa ne capital?

```
*Surveyor General Office* (code 025300300100):
• Manyan ayyuka: kasafin da aka amince ₦286.50 miliyan; 77.1% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦371.82 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 26
```

## share-02 (hausa) ok (3.7s)

**Q:** Kashi nawa na aminceccen kasafin 2026 na Tenancy Control and Safety of Person Agency ne na capital?

```
*Tenancy Control and Safety of Person Agency* (code 032600700500):
• Manyan ayyuka: kasafin da aka amince ₦72.00 miliyan; 47.1% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦153.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 26
```

## share-03 (typo) ok (3.7s)

**Q:** What share of the Arabic and Islmic Education Board's 2026 aproved budget is capial?

```
*Arabic and Islamic Education Board* (code 051705800100):
• Capital: approved budget ₦840.00 million; 26.6% of its total (Kasafi's calculation)
• Total: approved budget ₦3.16 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 27
```

## share-04 (informal) ok (3.4s)

**Q:** capital share of Ministry of Health's 2026 budget?

```
*Ministry of Health* (code 052100000000):
• Capital: approved budget ₦104.64 billion; 84.1% of its total (Kasafi's calculation)
• Total: approved budget ₦124.41 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 27
```

## share-05 (template) ok (3.9s)

**Q:** What share of the International Fund for Agriculture's 2026 approved budget is capital?

```
*International Fund for Agriculture* (code 021510200200):
• Capital: approved budget ₦170.00 million; 56.5% of its total (Kasafi's calculation)
• Total: approved budget ₦301.08 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 25
```

## share-06 (code_switched) ok (3.9s)

**Q:** Ministry of Finance 2026 approved budget din, wane share ne capital?

```
*Ministry of Finance* (code 022000000000):
• Manyan ayyuka: kasafin da aka amince ₦9.47 biliyan; 23.5% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦40.27 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 25
```

## share-07 (typo) ok (4.7s)

**Q:** What shrae of the Water Board's 2026 aproved budget is capitol?

```
*Water Board* (code 025210200100):
• Capital: approved budget ₦28.30 billion; 91.3% of its total (Kasafi's calculation)
• Total: approved budget ₦30.98 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-08 (informal) WRONG: WRONG AGENCY 025300000000 (3.7s)

**Q:** how much of Min of Lands and Housing's 2026 approved budget is capital?

```
*Min of Lands and Housing* (code 025300000000):
• Capital: approved budget ₦34.90 billion; 97.6% of its total (Kasafi's calculation)
• Total: approved budget ₦35.78 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-09 (code_switched) ok (4.1s)

**Q:** Sultan Maccido Institute for Qur'ani & General Studies 2026 approved budget din nan, kashi nawa ne capital?

```
*Sultan Maccido Institute for Qur'ani & General Studies* (code 051700260100):
• Manyan ayyuka: kasafin da aka amince ₦430.00 miliyan; 42.1% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦1.02 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 27
```

## share-10 (template) ok (4.1s)

**Q:** What share of the Sokoto State contributory health care mgt agency's 2026 approved budget is capital?

```
*Sokoto State contributory health care mgt agency* (code 052100200100):
• Capital: approved budget ₦218.50 million; 73.0% of its total (Kasafi's calculation)
• Total: approved budget ₦299.39 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 27
```

## share-11 (code_switched) WRONG: not found, though the data has it (4.0s)

**Q:** Ministry for Basic Education 2026 approved budget din, what share ne capital?

```
Kasafin bai buga wata hukuma mai suna "Ministry of Basic and Secondary Education" daidai ba. Ko kana nufin ɗaya daga cikin waɗannan: Ministry for Basic Education?
```

## share-12 (typo) ok (5.5s)

**Q:** Waht share of teh College of Agriculture Wurno's 2026 approved budjet is capital?

```
*College of Agriculture Wurno* (code 021502100100):
• Capital: approved budget ₦929.70 million; 72.6% of its total (Kasafi's calculation)
• Total: approved budget ₦1.28 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 25
```

## share-13 (hausa) ok (3.9s)

**Q:** Kashi nawa na kasafin kudin 2026 da aka amince wa House of Assembly Service Commission ne na capital?

```
*House of Assembly Service Commission* (code 011200400100):
• Manyan ayyuka: kasafin da aka amince ₦525.50 miliyan; 82.9% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦634.28 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-14 (followup) ok (3.9s)

**Q:** What share of its 2026 approved budget is capital?

```
*Ministry of Justice* (code 032600000000):
• Capital: approved budget ₦3.71 billion; 60.8% of its total (Kasafi's calculation)
• Total: approved budget ₦6.09 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-15 (code_switched) ok (4.8s)

**Q:** Wane share ne capital daga 2026 approved budget na Sokoto State Public Service Institute?

```
*Sokoto State Public Service Institute* (code 012500100200):
• Manyan ayyuka: kasafin da aka amince ₦0.00; 0.0% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦95.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-16 (code_switched) ok (3.9s)

**Q:** Ministry of Information 2026 approved budget dinnan, share na capital din nawa ne?

```
*Ministry of Information* (code 012300000000):
• Manyan ayyuka: kasafin da aka amince ₦1.46 biliyan; 59.0% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦2.48 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-17 (code_switched) ok (3.2s)

**Q:** Sokoto Road Maintenance Agency 2026 approved budget din nan, what share ne capital?

```
*Sokoto Road Maintenance Agency* (code 023400400100):
• Manyan ayyuka: kasafin da aka amince ₦400.00 miliyan; 86.0% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦465.10 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## share-18 (informal) ok (4.3s)

**Q:** How much of the Department for Rural Roads's 2026 approved budget is capital?

```
*Department for Rural Roads* (code 023405700100):
• Capital: approved budget ₦15.47 billion; 99.0% of its total (Kasafi's calculation)
• Total: approved budget ₦15.63 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-19 (typo) ok (8.4s)

**Q:** What shrae of the POVERTY REDUCTION PROGRAMME's 2026 approved budgget is capial?

```
Capital is ₦1.70 billion of the POVERTY REDUCTION PROGRAMME's 2026 approved total of ₦2.24 billion. That is 76.0% (Kasafi's calculation) capital, on an approved-budget basis.

• POVERTY REDUCTION PROGRAMME (one agency or unit, capital, code 011102000100), 2026 Approved Budget: ₦1.70 billion ↑
• POVERTY REDUCTION PROGRAMME (one agency or unit, all spending (total), code 011102000100) [Total Expenditure by Administrative Classification], 2026 Approved Budget: ₦2.24 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 25
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-01 (informal) ok (3.7s)

**Q:** Why'd the Ministry of Education's approved budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry of Education* (code 051700000000):
• Total: 2025 approved budget ₦59.59 billion; 2026 approved budget ₦68.95 billion; change +₦9.36 billion (+15.7%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-02 (typo) ok (11.6s)

**Q:** Why did teh Civil Service Comission's approved budjet fall from 2025 to 2026?

```
The Civil Service Commission's approved budget did not fall. It rose from ₦254.99 million in 2025 to ₦403.14 million in 2026 (Kasafi's calculation: 58.1%). Budget documents show figures but do not explain reasons for changes.

• Civil Service Commission (ministry total including its agencies, all spending (total), code 014700000000), 2025 Approved Budget: ₦254.99 million
• Civil Service Commission (ministry total including its agencies, all spending (total), code 014700000000), 2026 Approved Budget: ₦403.14 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-03 (informal) ok (3.9s)

**Q:** Why'd Government House's approved budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Government House* (code 011100000000):
• Personnel (salaries): 2025 approved budget ₦353.01 million; 2026 approved budget ₦444.25 million; change +₦91.24 million (+25.8%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦9.68 billion; 2026 approved budget ₦11.44 billion; change +₦1.76 billion (+18.2%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦3.99 billion; 2026 approved budget ₦6.64 billion; change +₦2.65 billion (+66.3%) (Kasafi's calculation)
• Total: 2025 approved budget ₦14.03 billion; 2026 approved budget ₦18.53 billion; change +₦4.50 billion (+32.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 12, 14, 15; Sokoto State FY 2026 Budget, p. 16, 19, 21, 25
```

## false_premise-04 (hausa) ok (4.0s)

**Q:** Me ya sa approved budget na Ministry Careers & Special Services ya ragu daga 2025 zuwa 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
*Ministry Careers & Special Services* (code 017000000000):
• Albashi: 2025 kasafin da aka amince ₦51.37 miliyan; 2026 kasafin da aka amince ₦63.37 miliyan; bambanci +₦12.00 miliyan (+23.4%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦10.04 biliyan; 2026 kasafin da aka amince ₦18.00 biliyan; bambanci +₦7.96 biliyan (+79.3%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦481.00 miliyan; 2026 kasafin da aka amince ₦8.30 biliyan; bambanci +₦7.82 biliyan (+1626.6%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦10.57 biliyan; 2026 kasafin da aka amince ₦26.37 biliyan; bambanci +₦15.80 biliyan (+149.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 13, 14, 16; Sokoto State FY 2026 Budget, shafi 16, 19, 22, 25
```

## false_premise-05 (followup) ok (10.2s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
The Ministry’s approved budget did not fall — its 2025 approved budget was ₦6.82 billion and its 2026 approved budget was ₦11.69 billion; the evidence shows an increase, so no reason for a fall is given.

• 2025 approved budget (total): ₦6.82 billion
• 2026 approved budget (total): ₦11.69 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-06 (typo) WRONG: not found, though the data has it (14.9s)

**Q:** Why did teh Ministry of Works's aproved budget rise from 2025 to 2026?

```
I can read your question two ways. Which do you mean?
```

## false_premise-07 (template) ok (3.2s)

**Q:** Why did the Ministry of Youth and Sports Development's approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry of Youth and Sports Development* (code 051300000000):
• Total: 2025 approved budget ₦4.02 billion; 2026 approved budget ₦17.06 billion; change +₦13.03 billion (+323.8%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-08 (template) ok (12.7s)

**Q:** Why did the Ministry for Religious Affairs's approved budget fall from 2025 to 2026?

```
The Ministry for Religious Affairs's approved budget did not fall. Its ministry total rose from ₦11.26 billion in 2025 to ₦18.05 billion in 2026, a rise of ₦6.79 billion 60.3% (Kasafi's calculation).

• Ministry for Religious Affairs (ministry total including its agencies, all spending (total), code 017200000000), 2025 Approved Budget: ₦11.26 billion
• Ministry for Religious Affairs (ministry total including its agencies, all spending (total), code 017200000000), 2026 Approved Budget: ₦18.05 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-09 (followup) ok (3.6s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Fiscal Responsibility Commission* (code 025000000000):
• Total: 2025 approved budget ₦58.99 million; 2026 approved budget ₦60.99 million; change +₦2.00 million (+3.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-10 (code_switched) ok (3.1s)

**Q:** Me ya sa Ministry of Culture & Tourism approved budget ya fall daga 2025 to 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
*Ministry of Culture & Tourism* (code 023600000000):
• Albashi: 2025 kasafin da aka amince ₦107.91 miliyan; 2026 kasafin da aka amince ₦103.35 miliyan; bambanci -₦4.56 miliyan (-4.2%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦341.10 miliyan; 2026 kasafin da aka amince ₦532.80 miliyan; bambanci +₦191.70 miliyan (+56.2%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦761.00 miliyan; 2026 kasafin da aka amince ₦788.59 miliyan; bambanci +₦27.59 miliyan (+3.6%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦1.21 biliyan; 2026 kasafin da aka amince ₦1.42 biliyan; bambanci +₦214.73 miliyan (+17.7%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 13, 14, 16; Sokoto State FY 2026 Budget, shafi 17, 20, 23, 26
```

## false_premise-11 (template) ok (3.5s)

**Q:** Why did the Ministry of Water Resources's approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry of Water Resources* (code 025200000000):
• Total: 2025 approved budget ₦20.32 billion; 2026 approved budget ₦44.99 billion; change +₦24.67 billion (+121.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-12 (hausa) ok (3.3s)

**Q:** Me ya sa approved budget na Ministry for Home Affairs ya ragu daga 2025 zuwa 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
*Ministry for Home Affairs* (code 012400000000):
• Albashi: 2025 kasafin da aka amince ₦1.31 biliyan; 2026 kasafin da aka amince ₦2.11 biliyan; bambanci +₦804.86 miliyan (+61.5%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦158.37 miliyan; 2026 kasafin da aka amince ₦1.42 biliyan; bambanci +₦1.26 biliyan (+794.2%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦638.86 miliyan; 2026 kasafin da aka amince ₦2.58 biliyan; bambanci +₦1.94 biliyan (+304.2%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦2.11 biliyan; 2026 kasafin da aka amince ₦6.11 biliyan; bambanci +₦4.01 biliyan (+190.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 13, 14, 16; Sokoto State FY 2026 Budget, shafi 16, 19, 22, 25
```

## false_premise-13 (code_switched) ok (13.8s)

**Q:** Me ya sa approved budget na Department of Establishment and Pensions ya rise daga 2025 to 2026?

```
Kasafin da aka amince wa Ma'aikata bai ƙaru ba daga 2025 zuwa 2026, ya ragu ne. Jimilla ta 2025 ita ce ₦16.17 biliyan, jimilla ta 2026 kuma ita ce ₦11.84 biliyan.

• 2025 kashe (Janairu–Satumba 2025 kawai): ₦10.77 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## false_premise-14 (hausa) ok (11.5s)

**Q:** Me ya sa approved budget na Office of Auditor General ya sauka daga 2025 zuwa 2026?

```
Kasafin Office of Auditor General da aka amince da shi bai sauka ba daga 2025 zuwa 2026. Ya karu daga ₦542.84 miliyan a 2025 zuwa ₦606.84 miliyan a 2026.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## false_premise-15 (followup) ok (3.6s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry of Justice* (code 032600000000):
• Personnel (salaries): 2025 approved budget ₦760.15 million; 2026 approved budget ₦864.15 million; change +₦104.00 million (+13.7%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦1.23 billion; 2026 approved budget ₦1.52 billion; change +₦295.00 million (+24.1%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦2.48 billion; 2026 approved budget ₦3.71 billion; change +₦1.23 billion (+49.7%) (Kasafi's calculation)
• Total: 2025 approved budget ₦4.46 billion; 2026 approved budget ₦6.09 billion; change +₦1.63 billion (+36.5%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 13, 15, 16; Sokoto State FY 2026 Budget, p. 18, 20, 24, 26
```

## false_premise-16 (informal) WRONG: didn't correct a premise the figures contradict (13.5s)

**Q:** Why did the Ministry for Higher Education's approved budget drop from 2025 to 2026?

```
From Total Expenditure by Administrative Classification, the Ministry for Higher Education was allocated ₦19.15 billion as the 2025 approved budget (total). It was allocated ₦33.99 billion as the 2026 approved budget (total). So the evidence shows an increase, not a drop, and it gives no reason for a drop.

• 2025 approved budget (total): ₦19.15 billion
• 2025 revised budget (total): ₦19.26 billion
• 2026 approved budget (total): ₦33.99 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-17 (typo) ok (11.6s)

**Q:** Why did the Socail Sector's aproved budget fall from 2025 to 2026?

```
The Social Sector's approved budget (total) did not fall from 2025 to 2026. It was ₦175.57 billion in the 2025 approved budget, and ₦278.88 billion in the 2026 approved budget. Both figures are from the Total Expenditure by Administrative Classification table.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-18 (informal) WRONG: didn't correct a premise the figures contradict (16.6s)

**Q:** why did Ministry of Agriculture & Natural Resource's budget go up from 2025 to 2026?

```
• Difference (2026 Approved Budget vs 2025 Approved Budget): -₦2.04 billion (-10.7%) (Kasafi's calculation)

• Ministry of Agriculture & Natural Resource (ministry total including its agencies, all spending (total), code 021500000000), 2025 Approved Budget: ₦19.09 billion
• Ministry of Agriculture & Natural Resource (ministry total including its agencies, all spending (total), code 021500000000), 2026 Approved Budget: ₦17.05 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-19 (followup) ok (3.8s)

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

## not_in_data-01 (code_switched) ok (3.7s)

**Q:** JUDICIAL SERVICE COMMISSION ta spend nawa in Q4 2026?

```
Ba a cikin takardun ba:
• JUDICIAL SERVICE COMMISSION 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• JUDICIAL SERVICE COMMISSION 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-02 (code_switched) ok (3.1s)

**Q:** Pilgrims Welfare Agency ta spend nawa a Q4 2026?

```
Ba a cikin takardun ba:
• Pilgrims Welfare Agency 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Pilgrims Welfare Agency 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Pilgrims Welfare Agency 2026 kason kasafin da aka sabunta da aka kashe: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-03 (followup) ok (4.2s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Parks and Gardens Agency 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Parks and Gardens Agency 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Parks and Gardens Agency 2027 share of the revised budget spent: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-04 (code_switched) ok (4.5s)

**Q:** Office of Auditor General ta spend nawa a Q4 2026?

```
Ba a cikin takardun ba:
• Office of Auditor General 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Office of Auditor General 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-05 (followup) ok (4.3s)

**Q:** How much did it spend in Q4 2026?

```
Not in the documents:
• Civil Service Commission 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
• Civil Service Commission 2026 spent in Q4: the latest implementation report is Q2 2026
```

## not_in_data-06 (followup) ok (3.2s)

**Q:** And how much did it spend in Q1 2027?

```
Not in the documents:
• Shari’a Court of Appeal 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Shari’a Court of Appeal 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-07 (template) ok (18.6s)

**Q:** How much is the State Agricultural Development Project's approved budget for 2028?

```
The 2026 budget document does not show a 2028 approved budget; it shows a 2028 out-year estimate (projection) for the State Agricultural Development Project of ₦620.08 million. That figure is a projection, not an approved allocation.

• State Agricultural Development Project (one agency or unit, all spending (total), code 021510200100), 2028 Out-Year Estimate: ₦620.08 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## not_in_data-08 (informal) ok (4.0s)

**Q:** SOSACAT spent how much in Q1 2027?

```
Not in the documents:
• SOSACAT 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• SOSACAT 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-09 (typo) ok (4.4s)

**Q:** How muhc did the Goverment House spend in Q4 2026?

```
Not in the documents:
• Government House 2026 spent in Q4: the latest implementation report is Q2 2026
```

## not_in_data-10 (template) ok (4.3s)

**Q:** How much did the College of Nursing Sciences spend in Q1 2027?

```
Not in the documents:
• College of Nursing Sciences 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• College of Nursing Sciences 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-11 (code_switched) ok (3.7s)

**Q:** Law Reform Commission ta spend nawa for Q1 2027?

```
Ba a cikin takardun ba:
• Law Reform Commission 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Law Reform Commission 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-12 (typo) WRONG: WRONG AGENCY 012400000000 (11.0s)

**Q:** How much is the Ministry for Home Affaris's aproved budget for 2028?

```
The 2026 budget does not show a 2028 approved budget, only a 2028 out-year estimate. The Ministry for Home Affairs (ministry total including its agencies) is projected at ₦2.77 billion for 2028.

• Ministry for Home Affairs (ministry total including its agencies, all spending (total), code 012400000000), 2028 Out-Year Estimate: ₦2.77 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## not_in_data-13 (code_switched) ok (4.6s)

**Q:** State Bureau of Statistics ta kashe how much in Q1 2027?

```
Ba a cikin takardun ba:
• State Bureau of Statistics 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• State Bureau of Statistics 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-14 (code_switched) ok (4.6s)

**Q:** Local Government Audit ya spend nawa a Q1 2027?

```
Ba a cikin takardun ba:
• Local Government Audit 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Local Government Audit 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Local Government Audit 2027 kason kasafin da aka sabunta da aka kashe: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-15 (informal) ok (12.9s)

**Q:** What's the State Universal Basic Education Board (SUBEB)'s approved budget for 2028?

```
SUBEB's 2028 figure shown is ₦8.89 billion. It is printed as a 2028 Out-Year Estimate, not an approved budget.

• State Universal Basic Education Board (SUBEB) (one agency or unit, all spending (total), code 051700300100), 2028 Out-Year Estimate: ₦8.89 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18
_Reply *show working* to see the rows and arithmetic._
```

## not_in_data-16 (typo) ok (4.5s)

**Q:** How much did teh Sokoto Geographical Information Systmes spend in Q1 2027?

```
Not in the documents:
• Sokoto Geographical Information Systems 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Sokoto Geographical Information Systems 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-17 (informal) ok (10.5s)

**Q:** How much approved budget for Agency for Persons Living With Disabilities in 2028?

```
⚠️ I couldn't get the document that fits best (Sokoto State 2028 Approved Budget). The answer below is from other documents I have, not from that one.

The 2028 figure for the Agency for Persons Living With Disabilities is ₦3.12 billion as an out-year estimate (total) in the 2026 budget. It is not a separate 2028 approved budget, only a projection for 2028.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18
```

## not_in_data-18 (code_switched) WRONG: no mention of what exists (2024–2026) (11.8s)

**Q:** Nawa ne Infectious Diseases Hospital Amanawa approved budget for 2028?

```
⚠️ Ban samo takardar da ta fi dacewa ba (Sokoto State 2028 Approved Budget). Amsar da ke ƙasa daga wasu takardun da nake da su ce, ba daga waccan ba.

Jimillar ƙiyasin 2028 na Infectious Diseases Hospital Amanawa ₦73.00 miliyan ne. Wannan adadi ƙiyasin shekara mai zuwa ne daga kasafin 2026.

• 2028 ƙiyasin shekara mai zuwa (jimilla): ₦73.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
```

## not_in_data-19 (informal) WRONG: no mention of what exists (Q2 2026) (10.7s)

**Q:** how much did the Livestock Development Programme spend in Q1 2027?

```
I couldn't find the document needed on the trusted sites (Sokoto State Budget Implementation Report Q1 2027). I've logged it for our team to review.
```

## rank_lga-01 (code_switched) ok (5.5s)

**Q:** Wanne 10 LGAs ne in Sokoto have the most IDPs?

```
Ta ƙaramar hukuma (22), mafi yawa:
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

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-02 (informal) ok (6.0s)

**Q:** Top 5 LGAs with most IDPs in Sokoto?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143
4. Tureta: 15,068
5. Shagari: 14,850

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-03 (template) ok (4.2s)

**Q:** Which 3 LGAs in Sokoto have the most IDPs?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-01 (template) ok (5.8s)

**Q:** How many IDPs are there in Gwadabawa LGA?

```
IOM DTM counts *8,406* IDPs in Gwadabawa (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (template) ok (4.7s)

**Q:** How many IDPs are there in Gudu LGA?

```
IOM DTM counts *3,147* IDPs in Gudu (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-03 (typo) ok (4.4s)

**Q:** How mnay IDPs are tehre in Wamako LGA?

```
IOM DTM counts *4,026* IDPs in Wamakko (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-04 (hausa) ok (5.4s)

**Q:** IDPs guda nawa ne a Illela LGA?

```
IOM DTM ta ƙidaya *8,953* 'yan gudun hijira a Illela (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-05 (code_switched) ok (4.6s)

**Q:** Nawa IDPs ne in Tangaza LGA?

```
IOM DTM ta ƙidaya *19,151* 'yan gudun hijira a Tangaza (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-06 (hausa) ok (5.3s)

**Q:** IDPs nawa ne a Rabah LGA?

```
IOM DTM ta ƙidaya *8,277* 'yan gudun hijira a Rabah (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-07 (code_switched) ok (4.9s)

**Q:** IDPs nawa ne in Gada LGA?

```
IOM DTM ta ƙidaya *1,014* 'yan gudun hijira a Gada (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-08 (followup) ok (6.2s)

**Q:** How many IDPs are there?

```
IOM DTM counts *619* IDPs in Binji (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-09 (followup) ok (5.9s)

**Q:** How many IDPs are there?

```
IOM DTM counts *14,850* IDPs in Shagari (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-10 (code_switched) ok (5.3s)

**Q:** How many IDPs ne suke a Tureta LGA?

```
IOM DTM ta ƙidaya *15,068* 'yan gudun hijira a Tureta (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-11 (code_switched) ok (4.9s)

**Q:** How many IDPs ne a Isa LGA?

```
IOM DTM ta ƙidaya *14,047* 'yan gudun hijira a Isa (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-12 (hausa) ok (4.7s)

**Q:** 'Yan gudun hijira (IDPs) nawa ne a Silame LGA?

```
IOM DTM ta ƙidaya *3,386* 'yan gudun hijira a Silame (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-13 (code_switched) ok (3.9s)

**Q:** How many IDPs ne a Dange-Shuni LGA?

```
IOM DTM ta ƙidaya *4,615* 'yan gudun hijira a Dange Shuni (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-14 (followup) ok (3.9s)

**Q:** How many IDPs are in it?

```
IOM DTM counts *4,252* IDPs in Kebbe (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-15 (template) ok (4.1s)

**Q:** How many IDPs are there in Tambuwal LGA?

```
IOM DTM counts *17,143* IDPs in Tambuwal (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-16 (informal) ok (5.3s)

**Q:** how many IDPs in Wurno LGA?

```
IOM DTM counts *2,128* IDPs in Wurno (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-17 (typo) ok (4.9s)

**Q:** How mnay IDPs aer there in Sokoto South LGA?

```
IOM DTM counts *4,486* IDPs in Sokoto South (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-18 (informal) ok (4.1s)

**Q:** how many IDPs in Kware LGA?

```
IOM DTM counts *1,039* IDPs in Kware (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-19 (code_switched) ok (4.2s)

**Q:** How many IDPs ne a Goronyo LGA?

```
IOM DTM ta ƙidaya *1,926* 'yan gudun hijira a Goronyo (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## trend-01 (template) ok (5.4s)

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

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```
