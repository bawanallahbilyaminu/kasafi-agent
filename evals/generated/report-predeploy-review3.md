# Generated coverage run

Cases: cases-44377.json (draw seed 44377), form seed 1

52 cases: wrong 1 (1.9%), of them wrong agency 0 | median 4.0s

| family | wrong | of |
|---|---|---|
| compare | 0 | 6 |
| false_premise | 1 | 6 |
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
| informal | 0 | 4 |
| template | 0 | 10 |
| typo | 0 | 8 |

```
Cost of this run:
  Baseten: 12 calls, 95,908 prompt tokens (24,320 cached), 5,276 output tokens -> $0.12
  Meta: 113 calls, 350,584 prompt tokens (302,220 cached), 85,593 output tokens -> $0.47
  models together: $0.59 (prices per 1M tokens from settings kasafi_price_*)
  per answer (52 answers): $0.0070, 1.4 model calls
    Meta/plan               1.00 calls  $0.0035  (50%)
    Baseten/compose         0.13 calls  $0.0015  (21%)
    Meta/read1              0.13 calls  $0.0011  (16%)
    Baseten/read2           0.10 calls  $0.0007  (10%)
    Meta/completeness       0.04 calls  $0.0001  (2%)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0) | identical calls answered from the run's cache: 0
peak memory: 389 MB
```

## lookup-01 (code_switched) ok (7.9s)

**Q:** Nawa aka approve wa State Judiciary a 2025 budget?

```
A kasafin 2025 da aka amince da shi, jimillar kuɗaɗen State Judiciary da aka amince da su ita ce ₦6.28 biliyan. Wannan adadi jimilla ne daga teburin Jimillar Kashe Kuɗi ta Ƙasa-Ƙasa na Gudanarwa.

• 2025 kasafin da aka amince (jimilla): ₦6.28 biliyan
• 2025 kasafin da aka amince (manyan ayyuka): ₦3.13 biliyan
• 2025 kasafin da aka amince (albashi): ₦1.23 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12, 13, 16
```

## lookup-02 (template) ok (6.3s)

**Q:** How much was approved for the Social Sector in the 2026 budget?

```
For the Social Sector, ₦278.88 billion was approved in the 2026 budget as total expenditure.

• 2026 approved budget (total): ₦278.88 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18
```

## lookup-03 (followup) ok (6.0s)

**Q:** How much was approved for it in the 2025 budget?

```
The 2025 approved budget for the Ministry of Culture & Tourism (the ministry's total, its agencies included) was ₦1.21 billion. This is the allocated (budgeted) amount.

• Ministry of Culture & Tourism, 2025 Approved Budget: ₦1.21 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## lookup-04 (code_switched) ok (8.7s)

**Q:** Nawa aka approve wa Ministry of Energy and Petroleum Resources a 2026 budget?

```
An amince da jimillar ₦23.33 biliyan ga Ministry of Energy and Petroleum Resources a kasafin 2026 da aka amince da shi. Wannan ƙididdigar jimillar kashe kuɗaɗe ce ta ma’aikatar daga teburin Total Expenditure by Administrative Classification.

• 2026 kasafin da aka amince da shi (jimilla): ₦23.33 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## lookup-05 (hausa) ok (7.7s)

**Q:** Nawa aka amince wa Sokoto State House of Assembly a kasafin kudin 2025?

```
An amince wa Sokoto State House of Assembly jimillar kasafin kuɗin 2025 (ministry total) ₦9.37 biliyan. Wannan adadin shi ne abin da aka amince da shi, ba abin da aka kashe ba.

• Sokoto State House of Assembly, 2025 Approved Budget: ₦9.37 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## lookup-06 (hausa) ok (5.9s)

**Q:** Nawa aka amince wa Ministry of Water Resources a kasafin kudin 2026?

```
An amince wa Ministry of Water Resources jimlar ₦44.99 biliyan a kasafin kuɗin 2026 da aka amince da shi (total).

• 2026 kasafin da aka amince (jimilla): ₦44.99 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## split-01 (typo) ok (4.0s)

**Q:** What are teh personnel, overhaed and capital allocations of the Sokoto State Housing Cooperation in 2026?

```
For Sokoto State Housing Cooperation, the approved budget (salaries) is ₦26.45 million.

*Sokoto State Housing Cooperation*:
• Personnel (salaries): approved budget ₦26.45 million
• Overhead (running costs): approved budget ₦20.00 million
• Capital: approved budget ₦330.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-02 (followup) ok (3.5s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
For State Emergency Management Agency (SEMA), the approved budget (salaries) is ₦3.60 million.

*State Emergency Management Agency (SEMA)*:
• Personnel (salaries): approved budget ₦3.60 million
• Overhead (running costs): approved budget ₦125.00 million
• Capital: approved budget ₦300.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 14, 15
```

## split-03 (template) ok (4.1s)

**Q:** What are the personnel, overhead and capital allocations of the Ministry of Commerce and Industry in 2026?

```
For Ministry of Commerce and Industry, the approved budget (salaries) is ₦193.00 million.

*Ministry of Commerce and Industry*:
• Personnel (salaries): approved budget ₦193.00 million
• Overhead (running costs): approved budget ₦2.16 billion
• Capital: approved budget ₦4.21 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 25
```

## split-04 (typo) ok (4.0s)

**Q:** What are the personnel, overhaed and capial allocations of the State Newspaper Comp.(The PATH) in 2026?

```
For State Newspaper Comp.(The PATH), the approved budget (salaries) is ₦70.08 million.

*State Newspaper Comp.(The PATH)*:
• Personnel (salaries): approved budget ₦70.08 million
• Overhead (running costs): approved budget ₦20.50 million
• Capital: approved budget ₦209.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-05 (hausa) ok (3.5s)

**Q:** Menene personnel, overhead da capital allocations na Fertilizer and Agricultral Supplies Company a 2025?

```
Ga Fertilizer and Agricultral Supplies Company, kasafin da aka amince (albashi) shi ne ₦37.51 miliyan.

*Fertilizer and Agricultral Supplies Company*:
• Albashi: kasafin da aka amince ₦37.51 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦23.50 miliyan
• Manyan ayyuka: kasafin da aka amince ₦98.00 miliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 13, 14, 16
```

## split-06 (followup) ok (3.2s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
For Ministry for Women Affairs, the approved budget (salaries) is ₦108.21 million.

*Ministry for Women Affairs*:
• Personnel (salaries): approved budget ₦108.21 million
• Overhead (running costs): approved budget ₦665.10 million
• Capital: approved budget ₦7.67 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## spend_quarter-01 (hausa) ok (3.9s)

**Q:** Nawa Ministry of Innovation and Digital Economy ta kashe har zuwa karshen Q4 2024, idan aka kwatanta da revised budget dinta?

```
Ga Ministry of Innovation and Digital Economy, abin da aka kashe zuwa yanzu (Q1–Q4) shi ne ₦318.66 miliyan.

*Ministry of Innovation and Digital Economy*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q4) ₦318.66 miliyan; kasafin da aka sabunta ₦1.23 biliyan; kason kasafin da aka sabunta da aka kashe 25.9% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 18
```

## spend_quarter-02 (template) ok (3.9s)

**Q:** How much had the AFFORESTATION PROGRAMME spent by the end of Q3 2025, against its revised budget?

```
For AFFORESTATION PROGRAMME, the spent so far (Q1–Q3) is ₦15.63 million.

*AFFORESTATION PROGRAMME*:
• Total: spent so far (Q1–Q3) ₦15.63 million; revised budget ₦26.34 million

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 17
```

## spend_quarter-03 (template) ok (3.3s)

**Q:** How much had the Ministry of Water Resources spent by the end of Q4 2024, against its revised budget?

```
For Ministry of Water Resources, the spent so far (Q1–Q4) is ₦12.90 billion.

*Ministry of Water Resources*:
• Total: spent so far (Q1–Q4) ₦12.90 billion; revised budget ₦19.20 billion

📄 *Sources:* Budget Performance Report Q4 2024, p. 18
```

## spend_quarter-04 (typo) ok (3.4s)

**Q:** How muhc had the Law Reform Commision spent by the end of Q4 2024, aginst its revised budget?

```
For Law Reform Commission, the spent so far (Q1–Q4) is ₦50.90 million.

*Law Reform Commission*:
• Total: spent so far (Q1–Q4) ₦50.90 million; revised budget ₦81.15 million; share of the revised budget spent 62.7% (Kasafi's calculation)

📄 *Sources:* Budget Performance Report Q4 2024, p. 19
```

## spend_quarter-05 (code_switched) ok (3.1s)

**Q:** Sultan AbdulRahman College of H/Tech. ta kashe nawa by the end of Q2 2026, against revised budget nata?

```
Ga Sultan AbdulRahman College of H/Tech., abin da aka kashe zuwa yanzu (Q1–Q2) shi ne ₦282.54 miliyan.

*Sultan AbdulRahman College of H/Tech.*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q2) ₦282.54 miliyan; kasafin da aka sabunta ₦2.27 biliyan

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 18
```

## spend_quarter-06 (hausa) ok (4.1s)

**Q:** Nawa Poultry Development Agency ta kashe har zuwa karshen Q4 2024, idan aka kwatanta da revised budget dinta?

```
Ga Poultry Development Agency, kasafin da aka sabunta shi ne ₦34.92 miliyan.

*Poultry Development Agency*:
• Jimilla: kasafin da aka sabunta ₦34.92 miliyan; abin da aka kashe zuwa yanzu (Q1–Q4) ₦20.91 miliyan; kason kasafin da aka sabunta da aka kashe 59.9% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 19
```

## compare-01 (code_switched) ok (10.7s)

**Q:** Kwatanta Law and Justice approved budget na 2025 da 2026, which one pass?

```
Kasafin Law and Justice na 2025 da aka amince da shi jimilla ₦10.74 biliyan ne, na 2026 kuma jimilla ₦14.26 biliyan ne. Saboda haka kasafin 2026 ya fi na 2025 yawa. Dukkan kuɗaɗen biyu jimilla ne daga teburin Total Expenditure by Administrative Classification.

• 2025 approved budget (jimilla): ₦10.74 biliyan
• 2026 approved budget (jimilla): ₦14.26 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18; Sokoto State Government 2025 Approved Budget, shafi 12
```

## compare-02 (typo) ok (3.3s)

**Q:** Comare the Ministry of Livestocks and Fisheries Development's aproved budget in 2025 and 2026.

```
For Ministry of Livestocks and Fisheries Development, the 2025 approved budget is ₦7.89 billion.

*Ministry of Livestocks and Fisheries Development*:
• Total: 2025 approved budget ₦7.89 billion; 2026 approved budget ₦13.60 billion; change +₦5.71 billion (+72.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-03 (hausa) ok (3.0s)

**Q:** Kwatanta approved budget na Department of Establishment and Pensions a 2025 da 2026.

```
Ga Department of Establishment and Pensions, 2025 kasafin da aka amince shi ne ₦16.17 biliyan.

*Department of Establishment and Pensions*:
• Jimilla: 2025 kasafin da aka amince ₦16.17 biliyan; 2026 kasafin da aka amince ₦11.84 biliyan; bambanci -₦4.33 biliyan (-26.8%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-04 (hausa) ok (3.0s)

**Q:** Kwatanta approved budget na Ministry of Agriculture & Natural Resource a 2025 da 2026.

```
Ga Ministry of Agriculture & Natural Resource, 2025 kasafin da aka amince shi ne ₦19.09 biliyan.

*Ministry of Agriculture & Natural Resource*:
• Jimilla: 2025 kasafin da aka amince ₦19.09 biliyan; 2026 kasafin da aka amince ₦17.05 biliyan; bambanci -₦2.04 biliyan (-10.7%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-05 (template) ok (2.9s)

**Q:** Compare the Sokoto State House of Assembly's approved budget in 2025 and 2026.

```
For Sokoto State House of Assembly, the 2025 approved budget is ₦9.37 billion.

*Sokoto State House of Assembly*:
• Total: 2025 approved budget ₦9.37 billion; 2026 approved budget ₦12.26 billion; change +₦2.89 billion (+30.8%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-06 (hausa) ok (3.3s)

**Q:** Kwatanta kasafin kudin Sokoto State Independent Electoral Commission da aka amince da shi a 2025 da 2026.

```
Ga Sokoto State Independent Electoral Commission, 2025 kasafin da aka amince shi ne ₦529.14 miliyan.

*Sokoto State Independent Electoral Commission*:
• Jimilla: 2025 kasafin da aka amince ₦529.14 miliyan; 2026 kasafin da aka amince ₦460.48 miliyan; bambanci -₦68.67 miliyan (-13.0%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## share-01 (code_switched) ok (3.3s)

**Q:** Share nawa ne capital a 2026 approved budget na Sokoto Road Maintenance Agency?

```
Ga Sokoto Road Maintenance Agency, kasafin da aka amince (manyan ayyuka) shi ne ₦400.00 miliyan.

*Sokoto Road Maintenance Agency*:
• Manyan ayyuka: kasafin da aka amince ₦400.00 miliyan; 86.0% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦465.10 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## share-02 (hausa) ok (3.8s)

**Q:** A cikin approved budget na 2026 na College of Nursing Sciences, kashi nawa ne na capital?

```
Ga College of Nursing Sciences, kasafin da aka amince (manyan ayyuka) shi ne ₦1.10 biliyan.

*College of Nursing Sciences*:
• Manyan ayyuka: kasafin da aka amince ₦1.10 biliyan; 66.5% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦1.65 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 27
```

## share-03 (typo) ok (4.1s)

**Q:** What shrae of the Law Refrom Commission's 2026 approved budget is capital?

```
For Law Reform Commission, the approved budget (capital) is ₦605.17 million.

*Law Reform Commission*:
• Capital: approved budget ₦605.17 million; 69.7% of its total (Kasafi's calculation)
• Total: approved budget ₦868.16 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-04 (informal) ok (3.1s)

**Q:** Hisbah Board Sokoto's 2026 approved budget — what's the capital share?

```
For Hisbah Board Sokoto, the approved budget (capital) is ₦294.00 million.

*Hisbah Board Sokoto*:
• Capital: approved budget ₦294.00 million; 33.0% of its total (Kasafi's calculation)
• Total: approved budget ₦889.67 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 25
```

## share-05 (template) ok (3.8s)

**Q:** What share of the Ministry of Commerce and Industry's 2026 approved budget is capital?

```
For Ministry of Commerce and Industry, the approved budget (capital) is ₦4.21 billion.

*Ministry of Commerce and Industry*:
• Capital: approved budget ₦4.21 billion; 64.1% of its total (Kasafi's calculation)
• Total: approved budget ₦6.56 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 25
```

## share-06 (code_switched) ok (3.7s)

**Q:** State Universal Basic Education Board (SUBEB) 2026 approved budget din, what share ne capital?

```
Ga State Universal Basic Education Board (SUBEB), kasafin da aka amince (manyan ayyuka) shi ne ₦9.15 biliyan.

*State Universal Basic Education Board (SUBEB)*:
• Manyan ayyuka: kasafin da aka amince ₦9.15 biliyan; 85.2% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦10.73 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 27
```

## false_premise-01 (informal) ok (3.4s)

**Q:** Why'd the Ministry of Budget and Economic Planning's approved budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Budget and Economic Planning, the 2025 approved budget is ₦4.03 billion.

*Ministry of Budget and Economic Planning*:
• Total: 2025 approved budget ₦4.03 billion; 2026 approved budget ₦5.32 billion; change +₦1.29 billion (+32.0%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-02 (typo) ok (3.6s)

**Q:** Why did teh Ministry for Special Duties's aproved budget fall form 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry for Special Duties, the 2025 approved budget is ₦423.00 million.

*Ministry for Special Duties*:
• Total: 2025 approved budget ₦423.00 million; 2026 approved budget ₦829.50 million; change +₦406.50 million (+96.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## false_premise-03 (informal) ok (3.6s)

**Q:** Why did Sokoto State Independent Electoral Commission's approved budget go up from 2025 to 2026?

```
It didn't rise: the approved budget fell from 2025 to 2026, so there is no rise to explain.
For Sokoto State Independent Electoral Commission, the 2025 approved budget is ₦529.14 million.

*Sokoto State Independent Electoral Commission*:
• Total: 2025 approved budget ₦529.14 million; 2026 approved budget ₦460.48 million; change -₦68.67 million (-13.0%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## false_premise-04 (hausa) WRONG: didn't correct a premise the figures contradict (16.5s)

**Q:** Me yasa approved budget na Civil Service Commission ya sauka daga 2025 zuwa 2026?

```
Kasafin da aka amince da shi na Civil Service Commission bai sauka ba daga 2025 zuwa 2026. A 2025 an amince da ₦254.99 miliyan, a 2026 kuma an amince da ₦403.14 miliyan. Bambancin shi ne ₦148.15 miliyan (lissafin Kasafi), wato karuwa ta 58.1% (lissafin Kasafi).

• Civil Service Commission, 2025 Approved Budget: ₦254.99 miliyan
• Civil Service Commission, 2026 Approved Budget: ₦403.14 miliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## false_premise-05 (followup) ok (4.2s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Health, the 2025 approved budget is ₦52.18 billion.

*Ministry of Health*:
• Total: 2025 approved budget ₦52.18 billion; 2026 approved budget ₦124.41 billion; change +₦72.23 billion (+138.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-06 (typo) ok (4.3s)

**Q:** Why did the Ministry of Innovation and Digital Economy's approved budet fall form 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Innovation and Digital Economy, the 2025 approved budget (salaries) is ₦60.01 million.

*Ministry of Innovation and Digital Economy*:
• Personnel (salaries): 2025 approved budget ₦60.01 million; 2026 approved budget ₦60.01 million; change ₦0.00 (0.0%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦143.88 million; 2026 approved budget ₦778.47 million; change +₦634.58 million (+441.0%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦1.14 billion; 2026 approved budget ₦2.75 billion; change +₦1.61 billion (+140.3%) (Kasafi's calculation)
• Total: 2025 approved budget ₦1.35 billion; 2026 approved budget ₦3.59 billion; change +₦2.24 billion (+166.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 13, 14, 16; Sokoto State FY 2026 Budget, p. 17, 20, 23, 26
```

## not_in_data-01 (code_switched) ok (3.9s)

**Q:** Bureau for Public Procurement and Price Intelligence ta spend nawa a Q1 2027?

```
Ba a cikin takardun ba:
• Bureau for Public Procurement and Price Intelligence 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• Bureau for Public Procurement and Price Intelligence 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-02 (code_switched) ok (4.2s)

**Q:** State Agricultural Development Project ta spend nawa in Q1 2027?

```
Ba a cikin takardun ba:
• State Agricultural Development Project 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• State Agricultural Development Project 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-03 (followup) ok (3.9s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Agency for Community Engagement 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Agency for Community Engagement 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-04 (code_switched) ok (4.1s)

**Q:** ZAKAT and Endowment Agency (WAQF) ta spend nawa in Q1 2027?

```
Ba a cikin takardun ba:
• ZAKAT and Endowment Agency (WAQF) 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• ZAKAT and Endowment Agency (WAQF) 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-05 (followup) ok (11.9s)

**Q:** How much is its approved budget for 2028?

```
The 2026 Budget does not contain a 2028 approved budget for the Waziri Junaidu History and Culture Bureau. It prints only a 2028 projection of ₦112.71 million for the Bureau, which is not an approved budget.

• Waziri Junaidu History and Culture Bureau, 2028 Out-Year Estimate: ₦112.71 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## not_in_data-06 (followup) ok (3.8s)

**Q:** How much did it spend in Q4 2026?

```
Not in the documents:
• Ministry of Justice 2026 spent in Q4: the latest implementation report is Q2 2026
• Ministry of Justice 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
```

## rank_lga-01 (code_switched) ok (4.9s)

**Q:** Which 5 LGAs a Sokoto ne ke da IDPs mafi yawa?

```
Ta ƙaramar hukuma (22), mafi yawa:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143
4. Tureta: 15,068
5. Shagari: 14,850

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-02 (informal) ok (4.7s)

**Q:** Top 3 LGAs in Sokoto with most IDPs?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-03 (template) ok (4.2s)

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

## lookup_lga-01 (template) ok (4.5s)

**Q:** How many IDPs are there in Gwadabawa LGA?

```
IOM DTM counts *8,406* IDPs in Gwadabawa (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (template) ok (4.2s)

**Q:** How many IDPs are there in Gudu LGA?

```
IOM DTM counts *3,147* IDPs in Gudu (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-03 (typo) ok (5.2s)

**Q:** How mnay IDPs aer there in Bodinga LGA?

```
IOM DTM counts *1,990* IDPs in Bodinga (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-04 (hausa) ok (5.1s)

**Q:** IDPs nawa ne a Illela LGA?

```
IOM DTM ta ƙidaya *8,953* 'yan gudun hijira a Illela (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-05 (code_switched) ok (5.9s)

**Q:** How many IDPs ne a Tangaza LGA?

```
IOM DTM ta ƙidaya *19,151* 'yan gudun hijira a Tangaza (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-06 (hausa) ok (5.0s)

**Q:** IDPs nawa ne a Rabah LGA?

```
IOM DTM ta ƙidaya *8,277* 'yan gudun hijira a Rabah (Round 18, reporting date 2025-10-31).

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

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```
