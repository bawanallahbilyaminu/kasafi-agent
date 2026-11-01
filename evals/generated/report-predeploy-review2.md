# Generated coverage run

Cases: cases-63649.json (draw seed 63649), form seed 1

52 cases: wrong 0 (0.0%), of them wrong agency 0 | median 4.3s

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
  Baseten: 16 calls, 136,958 prompt tokens (42,880 cached), 6,493 output tokens -> $0.15
  Meta: 112 calls, 355,411 prompt tokens (300,143 cached), 85,119 output tokens -> $0.48
  models together: $0.63 (prices per 1M tokens from settings kasafi_price_*)
  per answer (52 answers): $0.0078, 1.5 model calls
    Meta/plan               1.00 calls  $0.0035  (45%)
    Baseten/compose         0.15 calls  $0.0018  (23%)
    Meta/read1              0.13 calls  $0.0014  (17%)
    Baseten/read2           0.15 calls  $0.0011  (14%)
    Meta/completeness       0.02 calls  $0.0001  (1%)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0) | identical calls answered from the run's cache: 0
peak memory: 388 MB
```

## lookup-01 (code_switched) ok (10.4s)

**Q:** Nawa aka approved wa Ministry of Water Resources a 2025 budget?

```
An amince wa Ma'aikatar Albarkatun Ruwa jimillar ₦20.32 biliyan a cikin kasafin 2025 da aka amince da shi. Wannan kuɗi ne jimilla na ma'aikatar gaba ɗaya ciki har da hukumominta, kamar yadda aka nuna a cikin Teburin Jimillar Kashe Kuɗi ta Rarrabuwar Gudanarwa.

• 2025 kasafin da aka amince da shi (jimilla): ₦20.32 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-02 (template) ok (7.5s)

**Q:** How much was approved for the Ministry of Budget and Economic Planning in the 2025 budget?

```
The Sokoto State Government approved ₦4.03 billion for the Ministry of Budget and Economic Planning in the 2025 budget. This is the ministry total including its agencies from the Total Expenditure by Administrative Classification table.

• 2025 approved budget (total): ₦4.03 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11
```

## lookup-03 (followup) ok (7.8s)

**Q:** How much was approved for it in the 2026 budget?

```
The 2026 approved budget for the Ministry of Works is ₦59.17 billion. This is the ministry's total, its agencies included, as shown in the 2026 Q1 implementation report's Original Budget column.

• Ministry of Works, 2026 Original Budget: ₦59.17 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## lookup-04 (code_switched) ok (8.7s)

**Q:** Nawa aka approve wa Ministry for Religious Affairs a 2026 budget?

```
An amince wa Ministry for Religious Affairs kuɗi ₦18.05 biliyan a kasafin 2026 da aka amince da shi. Wannan jimilla ce (total) daga teburin Total Expenditure by Administrative Classification.

• 2026 kasafin da aka amince (jimilla): ₦18.05 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16
```

## lookup-05 (hausa) ok (6.3s)

**Q:** Nawa aka amince wa Ministry of Energy and Petroleum Resources a cikin kasafin kudin 2026?

```
Gwamnatin Jihar Sokoto ta amince da jimillar ₦23.33 biliyan ga Ministry of Energy and Petroleum Resources a cikin kasafin kuɗi na 2026 da aka amince da shi. Wannan adadi jimilla ce daga teburin Total Expenditure by Administrative Classification.

• 2026 kasafin da aka amince da shi (jimilla): ₦23.33 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## lookup-06 (hausa) ok (10.1s)

**Q:** Nawa aka amince wa Ministry for Women Affairs a kasafin kudin 2026?

```
An amince wa Ministry for Women Affairs jimillar kuɗi ₦7.24 biliyan a kasafin kuɗin 2026 da aka amince da shi. Wannan shi ne jimillar kashewa da aka amince wa ma'aikatar a teburin Total Expenditure by Administrative Classification.

• 2026 approved budget (jimilla): ₦7.24 biliyan
• 2026 approved budget (manyan ayyuka): ₦4.34 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 26
```

## split-01 (typo) ok (4.6s)

**Q:** Waht are the personel, overhead and capital alocations of the Ministry for Higher Education in 2026?

```
For Ministry for Higher Education, the approved budget (salaries) is ₦6.72 billion.

*Ministry for Higher Education*:
• Personnel (salaries): approved budget ₦6.72 billion
• Overhead (running costs): approved budget ₦6.65 billion
• Capital: approved budget ₦20.62 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 27
```

## split-02 (followup) ok (3.8s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
For Primary Health Care Development Agency, the approved budget (salaries) is ₦919.21 million.

*Primary Health Care Development Agency*:
• Personnel (salaries): approved budget ₦919.21 million
• Overhead (running costs): approved budget ₦399.00 million
• Capital: approved budget ₦5.80 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 27
```

## split-03 (template) ok (9.4s)

**Q:** What are the personnel, overhead and capital allocations of the Ministry of Culture & Tourism in 2026?

```
For Ministry of Culture & Tourism, the approved budget (salaries) is ₦103.35 million.

*Ministry of Culture & Tourism*:
• Personnel (salaries): approved budget ₦103.35 million
• Overhead (running costs): approved budget ₦532.80 million
• Capital: approved budget ₦788.59 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-04 (typo) ok (4.1s)

**Q:** What are teh personel, overhead and captal allocations of the Commodity Board in 2026?

```
For Commodity Board, the approved budget (salaries) is ₦7.37 million.

*Commodity Board*:
• Personnel (salaries): approved budget ₦7.37 million
• Overhead (running costs): approved budget ₦16.60 million
• Capital: approved budget ₦650.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-05 (hausa) ok (4.1s)

**Q:** Menene kason personnel, overhead da capital na Ministry for Basic Education a 2025?

```
Ga Ministry for Basic Education, kasafin da aka amince (albashi) shi ne ₦1.18 biliyan.

*Ministry for Basic Education*:
• Albashi: kasafin da aka amince ₦1.18 biliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦4.92 biliyan
• Manyan ayyuka: kasafin da aka amince ₦29.25 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 13, 15, 16
```

## split-06 (followup) ok (3.6s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
For Ministry for Women Affairs, the approved budget (salaries) is ₦108.21 million.

*Ministry for Women Affairs*:
• Personnel (salaries): approved budget ₦108.21 million
• Overhead (running costs): approved budget ₦665.10 million
• Capital: approved budget ₦7.67 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## spend_quarter-01 (hausa) ok (3.5s)

**Q:** Bureau for Public Procurement and Price Intelligence ta kashe kudi nawa har zuwa karshen Q3 2025 idan aka duba da revised budget nata?

```
Ga Bureau for Public Procurement and Price Intelligence, abin da aka kashe zuwa yanzu (Q1–Q3) shi ne ₦36.61 miliyan.

*Bureau for Public Procurement and Price Intelligence*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q3) ₦36.61 miliyan; kasafin da aka sabunta ₦217.61 miliyan; kason kasafin da aka sabunta da aka kashe 16.8% (lissafin Kasafi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 16
```

## spend_quarter-02 (template) ok (3.7s)

**Q:** How much had the Department for Rural Roads spent by the end of Q4 2024, against its revised budget?

```
For Department for Rural Roads, the spent so far (Q1–Q4) is ₦471.27 million.

*Department for Rural Roads*:
• Total: spent so far (Q1–Q4) ₦471.27 million; revised budget ₦3.26 billion

📄 *Sources:* Budget Performance Report Q4 2024, p. 18
```

## spend_quarter-03 (template) ok (3.5s)

**Q:** How much had the Agency for Malaria Control spent by the end of Q3 2025, against its revised budget?

```
For Agency for Malaria Control, the revised budget is ₦114.69 million.

*Agency for Malaria Control*:
• Total: revised budget ₦114.69 million; spent so far (Q1–Q3) ₦50.81 million; share of the revised budget spent 44.3% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 19
```

## spend_quarter-04 (typo) ok (3.4s)

**Q:** How much had teh Ministry of Livestocks and Fisheries Developmet spent by the end of Q3 2025, against its revised budjet?

```
For Ministry of Livestocks and Fisheries Development, the revised budget is ₦6.29 billion.

*Ministry of Livestocks and Fisheries Development*:
• Total: revised budget ₦6.29 billion; spent so far (Q1–Q3) ₦2.95 billion; share of the revised budget spent 46.9% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## spend_quarter-05 (code_switched) ok (3.7s)

**Q:** Government House ta kashe nawa by the end of Q2 2026 against its revised budget?

```
Ga Government House, abin da aka kashe zuwa yanzu (Q1–Q2) shi ne ₦3.74 biliyan.

*Government House*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q2) ₦3.74 biliyan; kasafin da aka sabunta ₦18.53 biliyan; kason kasafin da aka sabunta da aka kashe 20.2% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 15
```

## spend_quarter-06 (hausa) ok (3.4s)

**Q:** Nawa Arabic and Islamic Education Board ta kashe har zuwa karshen Q4 2024 idan aka duba da revised budget dinta?

```
Ga Arabic and Islamic Education Board, kasafin da aka sabunta shi ne ₦2.42 biliyan.

*Arabic and Islamic Education Board*:
• Jimilla: kasafin da aka sabunta ₦2.42 biliyan; abin da aka kashe zuwa yanzu (Q1–Q4) ₦1.34 biliyan; kason kasafin da aka sabunta da aka kashe 55.4% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 19
```

## compare-01 (code_switched) ok (3.6s)

**Q:** Fiscal Responsibility Commission approved budget na 2025 da 2026, compare su mana.

```
Ga Fiscal Responsibility Commission, 2025 kasafin da aka amince shi ne ₦58.99 miliyan.

*Fiscal Responsibility Commission*:
• Jimilla: 2025 kasafin da aka amince ₦58.99 miliyan; 2026 kasafin da aka amince ₦60.99 miliyan; bambanci +₦2.00 miliyan (+3.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-02 (typo) ok (2.8s)

**Q:** Comapre the Ministry of Culture & Tourism's aproved budget in 2025 and 2026.

```
For Ministry of Culture & Tourism, the 2025 approved budget is ₦1.21 billion.

*Ministry of Culture & Tourism*:
• Total: 2025 approved budget ₦1.21 billion; 2026 approved budget ₦1.42 billion; change +₦214.73 million (+17.7%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-03 (hausa) ok (3.6s)

**Q:** Kwatanta kasafin kudin Ministry of Environment da aka amince da shi a 2025 da 2026.

```
Ga Ministry of Environment, 2025 kasafin da aka amince shi ne ₦24.52 biliyan.

*Ministry of Environment*:
• Jimilla: 2025 kasafin da aka amince ₦24.52 biliyan; 2026 kasafin da aka amince ₦20.77 biliyan; bambanci -₦3.75 biliyan (-15.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-04 (hausa) ok (2.8s)

**Q:** Kwatanta kasafin kudin Civil Service Commission da aka amince da shi a 2025 da 2026.

```
Ga Civil Service Commission, 2025 kasafin da aka amince shi ne ₦254.99 miliyan.

*Civil Service Commission*:
• Jimilla: 2025 kasafin da aka amince ₦254.99 miliyan; 2026 kasafin da aka amince ₦403.14 miliyan; bambanci +₦148.15 miliyan (+58.1%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-05 (template) ok (2.5s)

**Q:** Compare the Ministry for Religious Affairs's approved budget in 2025 and 2026.

```
For Ministry for Religious Affairs, the 2025 approved budget is ₦11.26 billion.

*Ministry for Religious Affairs*:
• Total: 2025 approved budget ₦11.26 billion; 2026 approved budget ₦18.05 billion; change +₦6.79 billion (+60.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-06 (hausa) ok (3.4s)

**Q:** Kwatanta kasafin kudin Ministry of Youth and Sports Development da aka amince da shi a 2025 da 2026.

```
Ga Ministry of Youth and Sports Development, 2025 kasafin da aka amince shi ne ₦4.02 biliyan.

*Ministry of Youth and Sports Development*:
• Jimilla: 2025 kasafin da aka amince ₦4.02 biliyan; 2026 kasafin da aka amince ₦17.06 biliyan; bambanci +₦13.03 biliyan (+323.8%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## share-01 (code_switched) ok (4.0s)

**Q:** Approved budget na Sokoto State House of Assembly na 2026, what share ne capital?

```
Ga Sokoto State House of Assembly, kasafin da aka amince (manyan ayyuka) shi ne ₦4.66 biliyan.

*Sokoto State House of Assembly*:
• Manyan ayyuka: kasafin da aka amince ₦4.66 biliyan; 38.0% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦12.26 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-02 (hausa) ok (3.6s)

**Q:** Kashi nawa na kasafin 2026 da aka amince wa Ministry for Local Government and Chieftancy ne na capital?

```
Ga Ministry for Local Government and Chieftancy, kasafin da aka amince (manyan ayyuka) shi ne ₦850.44 miliyan.

*Ministry for Local Government and Chieftancy*:
• Manyan ayyuka: kasafin da aka amince ₦850.44 miliyan; 62.6% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦1.36 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 19, 27
```

## share-03 (typo) ok (5.1s)

**Q:** What sahre of the State collge of basic and remedial studies's 2026 approved budet is capital?

```
For State college of basic and remedial studies, the approved budget (capital) is ₦4.18 billion.

*State college of basic and remedial studies*:
• Capital: approved budget ₦4.18 billion; 95.0% of its total (Kasafi's calculation)
• Total: approved budget ₦4.40 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 27
```

## share-04 (informal) ok (3.2s)

**Q:** How much of Department for Rural Electrification's 2026 approved budget is capital?

```
For Department for Rural Electrification, the approved budget (capital) is ₦1.12 billion.

*Department for Rural Electrification*:
• Capital: approved budget ₦1.12 billion; 90.3% of its total (Kasafi's calculation)
• Total: approved budget ₦1.25 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-05 (template) ok (4.0s)

**Q:** What share of the Rima Radio's 2026 approved budget is capital?

```
For Rima Radio, the approved budget (capital) is ₦275.00 million.

*Rima Radio*:
• Capital: approved budget ₦275.00 million; 61.0% of its total (Kasafi's calculation)
• Total: approved budget ₦450.75 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 25
```

## share-06 (code_switched) ok (4.4s)

**Q:** Ministry for Basic Education 2026 approved budget dinnan, kashi nawa ne capital?

```
Ga Ministry for Basic Education, kasafin da aka amince (manyan ayyuka) shi ne ₦34.19 biliyan.

*Ministry for Basic Education*:
• Manyan ayyuka: kasafin da aka amince ₦34.19 biliyan; 78.6% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦43.50 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 27
```

## false_premise-01 (informal) ok (3.7s)

**Q:** why did Ministry Careers & Special Services's approved budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry Careers & Special Services, the 2025 approved budget is ₦10.57 billion.

*Ministry Careers & Special Services*:
• Total: 2025 approved budget ₦10.57 billion; 2026 approved budget ₦26.37 billion; change +₦15.80 billion (+149.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## false_premise-02 (typo) ok (3.3s)

**Q:** Why did the Ministry for Specail Duties's approved budjet fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry for Special Duties, the 2025 approved budget is ₦423.00 million.

*Ministry for Special Duties*:
• Total: 2025 approved budget ₦423.00 million; 2026 approved budget ₦829.50 million; change +₦406.50 million (+96.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## false_premise-03 (informal) ok (3.3s)

**Q:** Why did the Ministry of Innovation and Digital Economy's approved budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Innovation and Digital Economy, the 2025 approved budget is ₦1.35 billion.

*Ministry of Innovation and Digital Economy*:
• Total: 2025 approved budget ₦1.35 billion; 2026 approved budget ₦3.59 billion; change +₦2.24 billion (+166.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-04 (hausa) ok (11.0s)

**Q:** Me ya sa approved budget na Administration Sector ya ragu daga 2025 zuwa 2026?

```
Approved budget na Administration Sector bai ragu ba, ya ƙaru ne daga 2025 zuwa 2026. A 2025 an amince da ₦103.22 biliyan, a 2026 kuma an amince da ₦149.52 biliyan. Takardun kasafin kuɗi ba su bayyana dalilin canjin ba, 44.9% (lissafin Kasafi).

• Administration Sector, 2025 Approved Budget: ₦103.22 biliyan
• Administration Sector, 2026 Approved Budget: ₦149.52 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## false_premise-05 (followup) ok (3.2s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Solid Minerals and Natural Resources, the 2025 approved budget is ₦479.09 million.

*Ministry of Solid Minerals and Natural Resources*:
• Total: 2025 approved budget ₦479.09 million; 2026 approved budget ₦969.94 million; change +₦490.85 million (+102.5%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-06 (typo) ok (4.5s)

**Q:** Why did teh Ministry of Transport's approved budjet fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Transport, the 2025 approved budget is ₦3.65 billion.

*Ministry of Transport*:
• Total: 2025 approved budget ₦3.65 billion; 2026 approved budget ₦50.87 billion; change +₦47.21 billion (+1292.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## not_in_data-01 (code_switched) ok (5.3s)

**Q:** Orthopedic Hospital Wamakko ta spend nawa in Q1 2027?

```
Ba a cikin takardun ba:
• Orthopedic Hospital Wamakko 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Orthopedic Hospital Wamakko 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-02 (code_switched) ok (13.0s)

**Q:** Nawa ne approved budget na Umaru Ali Shinkafi Polytechnic Sokoto for 2028?

```
⚠️ Ban samo takardar da ta fi dacewa ba (Sokoto State 2028 Approved Budget). Amsar da ke ƙasa daga wasu takardun da nake da su ce, ba daga waccan ba.

Kasafin da aka amince da shi (approved budget) na 2028 na Umaru Ali Shinkafi Polytechnic Sokoto ba a wallafa shi a cikin waɗannan takardun ba. Abin da takardun suka wallafa shi ne hasashen shekarar 2028 (out-year estimate) wanda jimillarsa ta kai ₦5.19 biliyan.

• 2028 hasashen shekara (jimilla): ₦5.19 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
```

## not_in_data-03 (followup) ok (9.5s)

**Q:** How much is its approved budget for 2028?

```
⚠️ I couldn't get the document that fits best (Sokoto State 2028 Approved Budget). The answer below is from other documents I have, not from that one.

The 2026 Approved Budget only prints a projection for 2028. The Hospitals Services Magt. Board's 2028 Out-Year Estimate (total) is ₦5.58 billion. The actual 2028 Approved Budget figure wasn't found in these documents.

• 2028 Out-Year Estimate (total): ₦5.58 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18
```

## not_in_data-04 (code_switched) ok (4.5s)

**Q:** How much Noma Children Hospital ta kashe in Q4 2026?

```
Ba a cikin takardun ba:
• Noma Children Hospital 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Noma Children Hospital 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Noma Children Hospital 2026 kason kasafin da aka sabunta da aka kashe: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-05 (followup) ok (3.9s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Shehu Shagari Collage of Education Sokoto 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Shehu Shagari Collage of Education Sokoto 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-06 (followup) ok (3.4s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Office of Head of Service 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Office of Head of Service 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## rank_lga-01 (code_switched) ok (5.2s)

**Q:** Top 10 LGAs a Sokoto with most IDPs su ne wa?

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

## rank_lga-02 (informal) ok (4.9s)

**Q:** top 3 LGAs with most IDPs in Sokoto?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-03 (template) ok (4.9s)

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

## lookup_lga-01 (template) ok (5.2s)

**Q:** How many IDPs are there in Illela LGA?

```
IOM DTM counts *8,953* IDPs in Illela (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (template) ok (5.3s)

**Q:** How many IDPs are there in Isa LGA?

```
IOM DTM counts *14,047* IDPs in Isa (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-03 (typo) ok (5.6s)

**Q:** How mnay IDPs aer there in Gudu LGA?

```
IOM DTM counts *3,147* IDPs in Gudu (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-04 (hausa) ok (4.9s)

**Q:** Nawa ne adadin 'yan gudun hijira a Wurno LGA?

```
IOM DTM ta ƙidaya *2,128* 'yan gudun hijira a Wurno (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-05 (code_switched) ok (5.6s)

**Q:** How many IDPs ne a Goronyo LGA?

```
IOM DTM ta ƙidaya *1,926* 'yan gudun hijira a Goronyo (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-06 (hausa) ok (5.2s)

**Q:** Adadin IDPs nawa ne a Silame LGA?

```
IOM DTM ta ƙidaya *3,386* 'yan gudun hijira a Silame (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## trend-01 (template) ok (5.8s)

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
