# Generated coverage run

Cases: cases-289565.json (draw seed 289565), form seed 1

156 cases: wrong 7 (4.5%), of them wrong agency 1 | median 4.3s

| family | wrong | of |
|---|---|---|
| compare | 0 | 19 |
| false_premise | 3 | 19 |
| lookup | 1 | 19 |
| lookup_lga | 0 | 19 |
| not_in_data | 2 | 19 |
| rank_lga | 0 | 3 |
| share | 0 | 19 |
| spend_quarter | 1 | 19 |
| split | 0 | 19 |
| trend | 0 | 1 |

| form | wrong | of |
|---|---|---|
| code_switched | 0 | 33 |
| followup | 1 | 26 |
| hausa | 3 | 21 |
| informal | 1 | 19 |
| template | 1 | 23 |
| typo | 1 | 34 |

```
Cost of this run:
  Baseten: 45 calls, 333,006 prompt tokens (107,904 cached), 22,060 output tokens -> $0.39
  Meta: 391 calls, 1,389,014 prompt tokens (759,403 cached), 304,982 output tokens -> $2.20
  models together: $2.59 (prices per 1M tokens from settings kasafi_price_*)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0)
```

## lookup-01 (hausa) ok (9.9s)

**Q:** Nawa aka amince wa Department of Establishment and Pensions a budget na 2026?

```
An amince wa Department of Establishment and Pensions jimilla ₦11.84 biliyan a kasafin 2026. Wannan kuɗi ne da aka amince da shi (budget), ba kuɗin da aka kashe ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16
```

## lookup-02 (typo) ok (9.0s)

**Q:** How mucch was apprroved for the Sokoto State Independent Electoral Commission in the 2026 budget?

```
₦460.48 million was approved for the Sokoto State Independent Electoral Commission in the 2026 approved budget. This is the commission's total allocation (all spending).

• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## lookup-03 (template) ok (8.1s)

**Q:** How much was approved for the Ministry for Skills Acquisition and Entrepreneurship Development in the 2025 budget?

```
From the Total Expenditure by Administrative Classification table, the 2025 approved budget (total) for the Ministry for Skills Acquisition and Entrepreneurship Development is ₦1.50 billion.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12
```

## lookup-04 (informal) ok (11.2s)

**Q:** how much did Ministry of Innovation and Digital Economy get in 2025 budget?

```
The Ministry of Innovation and Digital Economy was allocated ₦1.35 billion in the 2025 approved budget (total). This figure is from the Total Expenditure table.

• 2025 approved budget (personnel): ₦60.01 million
• 2025 approved budget (overhead): ₦143.88 million
• 2025 approved budget (capital): ₦1.14 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 13, 14, 16
```

## lookup-05 (template) ok (10.1s)

**Q:** How much was approved for the Ministry of Energy and Petroleum Resources in the 2026 budget?

```
From the Total Expenditure by Administrative Classification table, the 2026 approved budget (total) for the Ministry of Energy and Petroleum Resources is ₦23.33 billion.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
```

## lookup-06 (code_switched) ok (11.8s)

**Q:** Ministry of Water Resources ta samu nawa a 2025 budget?

```
Ma'aikatar Albarkatun Ruwa ta samu jimilla ₦20.32 biliyan a kasafin 2025 da aka amince da shi, wannan kuɗi ne da aka ware ba wanda aka kashe ba. Daga baya kasafin aka sabunta ya zama ₦26.50 biliyan, kuma abin da aka kashe daga Janairu zuwa Satumba 2025 shi ne ₦12.79 biliyan (48.2% na kasafin da aka sabunta).

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State Budget Implementation Report Q3 2025, shafi 18
```

## lookup-07 (code_switched) ok (13.1s)

**Q:** Local Government Service Commission ta samu nawa a 2025 budget?

```
Local Government Service Commission ta samu jimilla ₦555.67 miliyan a kasafin 2025 da aka amince da shi. Wannan kuɗin kasafi ne da aka ware, ba kuɗin da aka kashe ba.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-08 (code_switched) ok (12.3s)

**Q:** How much ne aka approve wa Ministry for Special Duties a 2025 budget?

```
An amince wa Ministry for Special Duties jimilla ₦423.00 miliyan a kasafin 2025. Wannan kudin da aka amince ne, ba kudin da aka kashe ba.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-09 (followup) ok (10.8s)

**Q:** And how much was approved for it in the 2025 budget?

```
The State Government approved ₦24.52 billion for the Ministry of Environment in the 2025 budget (total).

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12
```

## lookup-10 (code_switched) ok (10.8s)

**Q:** Nawa Ministry of Works ta samu a 2026 budget?

```
Ma'aikatar Ayyuka (Ministry of Works) ta samu ₦59.17 biliyan a kasafin 2026 da aka amince da shi (jimilla).

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## lookup-11 (hausa) ok (11.3s)

**Q:** Nawa aka amince wa Civil Service Commission a kasafin kudin 2025?

```
An amince wa Civil Service Commission jimilla ₦254.99 miliyan a kasafin 2025. Wannan kuɗi ne da aka amince (kasafi), ba kuɗin da aka kashe ba.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-12 (template) ok (10.5s)

**Q:** How much was approved for the Ministry of Finance in the 2025 budget?

```
The 2025 approved budget (total) for the Ministry of Finance is ₦47.75 billion. This figure is the allocation from the Total Expenditure by Administrative Classification table.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11
```

## lookup-13 (code_switched) ok (10.5s)

**Q:** Ministry for Women Affairs din, nawa aka approve musu a 2025 budget?

```
An approve jimilla ₦8.44 biliyan ga Ministry for Women Affairs a kasafin 2025. Wannan jimilla ce daga teburin Jimillar Kashe Kuɗi a Rukunin Gudanarwa.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12
```

## lookup-14 (template) ok (10.0s)

**Q:** How much was approved for the Ministry of Culture & Tourism in the 2025 budget?

```
The 2025 approved budget (total) for the Ministry of Culture & Tourism is ₦1.21 billion. This is an allocated figure from the Total Expenditure by Administrative Classification table.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11
```

## lookup-15 (code_switched) ok (12.3s)

**Q:** Ministry of Lands and Housing ta samu how much a budget na 2026?

```
Ma'aikatar Lands and Housing ta samu jimilla ₦35.78 biliyan a kasafin 2026 da aka amince. Wannan adadin da aka ware ne, ba abin da aka kashe ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## lookup-16 (code_switched) ok (11.4s)

**Q:** Nawa Ministry of Commerce and Industry ta samu for 2026 budget?

```
Ma'aikatar Kasuwanci da Masana'antu ta samu ₦6.56 biliyan a kasafin 2026 da aka amince da shi (jimilla). Wannan adadin kasafi ne da aka tanada, ba kuɗi da aka kashe ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## lookup-17 (typo) WRONG: not found, though the data has it (3.5s)

**Q:** How much was apprroved for the Adminstration Sector in the 2026 budget?

```
The budget doesn't print an agency named exactly "Administration". Do you mean one of these: Administration Sector?
```

## lookup-18 (template) ok (9.5s)

**Q:** How much was approved for the Office of Head of Service in the 2025 budget?

```
The 2025 approved budget (total) for the Office of Head of Service was ₦3.41 billion. This figure is the approved allocation from the Total Expenditure table.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11
```

## lookup-19 (followup) ok (8.8s)

**Q:** How much was approved for it in the 2025 budget?

```
The 2025 approved budget (total) for the Sokoto State House of Assembly was ₦9.37 billion. By Q1–Q4 2025, ₦4.68 billion had been spent (49.9% of the final budget).

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Budget Implementation Report Q4 2025, p. 16
```

## split-01 (code_switched) ok (3.8s)

**Q:** Abeg, what are the personnel, overhead da capital allocations na Department for Rural Roads for 2025?

```
*Department for Rural Roads* (code 023405700100):
• Albashi: kasafin da aka amince ₦34.59 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦33.95 miliyan
• Manyan ayyuka: kasafin da aka amince ₦25.49 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 13, 14, 16
```

## split-02 (informal) ok (3.9s)

**Q:** What's 2026 personnel, overhead & capital for Sultan Maccido Institute for Qur'ani & General Studies?

```
*Sultan Maccido Institute for Qur'ani & General Studies* (code 051700260100):
• Personnel (salaries): approved budget ₦458.44 million
• Overhead (running costs): approved budget ₦134.00 million
• Capital: approved budget ₦430.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 27
```

## split-03 (followup) ok (3.5s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
*Fire Service* (code 012400800100):
• Personnel (salaries): approved budget ₦250.77 million
• Overhead (running costs): approved budget ₦94.06 million
• Capital: approved budget ₦343.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-04 (hausa) ok (3.5s)

**Q:** Menene kasafin personnel, overhead da capital na State Agricultural Development Project a 2026?

```
*State Agricultural Development Project* (code 021510200100):
• Albashi: kasafin da aka amince ₦294.88 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦30.20 miliyan
• Manyan ayyuka: kasafin da aka amince ₦350.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 20, 22, 25
```

## split-05 (typo) ok (4.1s)

**Q:** What are teh personnel, overhead and capial allocations of the College of Nursing Sciences, Tambuwal in 2025?

```
*College of Nursing Sciences, Tambuwal* (code 052110400200):
• Personnel (salaries): approved budget ₦194.52 million
• Overhead (running costs): approved budget ₦30.50 million
• Capital: approved budget ₦515.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 17
```

## split-06 (template) ok (3.5s)

**Q:** What are the personnel, overhead and capital allocations of the Ministry of Humanitarian Affairs & Social Welfare in 2026?

```
*Ministry of Humanitarian Affairs & Social Welfare* (code 055600100100):
• Personnel (salaries): approved budget ₦117.84 million
• Overhead (running costs): approved budget ₦1.28 billion
• Capital: approved budget ₦3.72 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 27
```

## split-07 (informal) ok (16.7s)

**Q:** Personnel, overhead and capital for State Newspaper Comp.(The PATH) in 2025?

```
*State Newspaper Comp.(The PATH)* (code 012305500100):
• Personnel (salaries): approved budget ₦83.08 million; spent so far (Q1–Q4) ₦82.98 million
• Overhead (running costs): approved budget ₦18.00 million; spent so far (Q1–Q4) ₦2.25 million
• Capital: approved budget ₦209.00 million; spent so far (Q1–Q4) ₦11.05 million
Not in the documents:
• State Newspaper Comp.(The PATH) Personnel (salaries) 2025 revised budget: the budget prints no Personnel (salaries) line for it
• State Newspaper Comp.(The PATH) Overhead (running costs) 2025 revised budget: the budget prints no Overhead (running costs) line for it
• State Newspaper Comp.(The PATH) Capital 2025 revised budget: the budget prints no Capital line for it

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 14, 16; Budget Implementation Report Q4 2025, p. 20, 24, 28
```

## split-08 (template) ok (3.4s)

**Q:** What are the personnel, overhead and capital allocations of the Sokoto State Public Service Institute in 2026?

```
*Sokoto State Public Service Institute* (code 012500100200):
• Personnel (salaries): approved budget ₦0.00
• Overhead (running costs): approved budget ₦95.00 million
• Capital: approved budget ₦0.00

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-09 (template) ok (4.7s)

**Q:** What are the personnel, overhead and capital allocations of the Primary Health Care Development Agency in 2025?

```
*Primary Health Care Development Agency* (code 052100300100):
• Personnel (salaries): approved budget ₦707.84 million
• Overhead (running costs): approved budget ₦569.00 million
• Capital: approved budget ₦11.92 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 17
```

## split-10 (template) ok (4.1s)

**Q:** What are the personnel, overhead and capital allocations of the State Emergency Management Agency (SEMA) in 2026?

```
*State Emergency Management Agency (SEMA)* (code 011100800100):
• Personnel (salaries): approved budget ₦4.30 million
• Overhead (running costs): approved budget ₦120.00 million
• Capital: approved budget ₦1.20 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 21, 25
```

## split-11 (followup) ok (2.6s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
*Ministry for Home Affairs* (code 012400000000):
• Personnel (salaries): approved budget ₦1.31 billion
• Overhead (running costs): approved budget ₦158.37 million
• Capital: approved budget ₦638.86 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 14, 16
```

## split-12 (typo) ok (3.0s)

**Q:** What are teh presonnel, overhead and capital alocations of the Ministry for Women Affairs in 2025?

```
*Ministry for Women Affairs* (code 051400000000):
• Personnel (salaries): approved budget ₦108.21 million
• Overhead (running costs): approved budget ₦665.10 million
• Capital: approved budget ₦7.67 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-13 (template) ok (3.6s)

**Q:** What are the personnel, overhead and capital allocations of the Specialist Hospital in 2025?

```
*Specialist Hospital* (code 052102600100):
• Personnel (salaries): approved budget ₦2.76 billion
• Overhead (running costs): approved budget ₦111.00 million
• Capital: approved budget ₦848.75 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 17
```

## split-14 (code_switched) ok (3.5s)

**Q:** Fertilizer and Agricultral Supplies Company ta samu nawa in 2026 for personnel, overhead da capital?

```
*Fertilizer and Agricultral Supplies Company* (code 021511000100):
• Albashi: kasafin da aka amince ₦68.17 miliyan; kasafin da aka sabunta ₦68.17 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦25.92 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦23.50 miliyan; kasafin da aka sabunta ₦23.50 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦3.50 miliyan
• Manyan ayyuka: kasafin da aka amince ₦23.00 miliyan; kasafin da aka sabunta ₦23.00 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦0.00

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 20, 22, 25; Budget Implementation Report Q2 2026, shafi 20, 23, 26
```

## split-15 (followup) ok (4.7s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
*Sokoto Central Market* (code 022205500100):
• Personnel (salaries): approved budget ₦59.47 million
• Overhead (running costs): approved budget ₦43.50 million
• Capital: approved budget ₦75.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-16 (hausa) ok (3.2s)

**Q:** Menene kason personnel, overhead da capital na Ministry of Youth and Sports Development a 2025?

```
*Ministry of Youth and Sports Development* (code 051300000000):
• Albashi: kasafin da aka amince ₦96.29 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦1.45 biliyan
• Manyan ayyuka: kasafin da aka amince ₦2.48 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 13, 15, 16
```

## split-17 (code_switched) ok (4.0s)

**Q:** State Bureau of Statistics 2025 budget, nawa ne personnel, overhead and capital allocation?

```
*State Bureau of Statistics* (code 023800400100):
• Albashi: kasafin da aka amince ₦34.72 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦124.00 miliyan
• Manyan ayyuka: kasafin da aka amince ₦150.00 miliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 13, 15, 16
```

## split-18 (followup) ok (3.9s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
*Umaru Ali Shinkafi Polytechnic Sokoto* (code 056901800100):
• Personnel (salaries): approved budget ₦1.90 billion
• Overhead (running costs): approved budget ₦453.00 million
• Capital: approved budget ₦2.43 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 27
```

## split-19 (template) ok (3.7s)

**Q:** What are the personnel, overhead and capital allocations of the Water Board in 2025?

```
*Water Board* (code 025210200100):
• Personnel (salaries): approved budget ₦604.38 million
• Overhead (running costs): approved budget ₦784.14 million
• Capital: approved budget ₦11.45 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## spend_quarter-01 (typo) ok (4.2s)

**Q:** How much had the Shehu Shagari Collage of Education Sokoto spent by teh end of Q3 2025, agaist its revised budgte?

```
*Shehu Shagari Collage of Education Sokoto* (code 056900300100):
• Total: spent so far (Q1–Q3) ₦2.52 billion; revised budget ₦3.47 billion; share of the revised budget spent 72.5% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 19
```

## spend_quarter-02 (hausa) ok (3.4s)

**Q:** Nawa Department for Security Matters ta kashe har zuwa ƙarshen Q3 2025, idan aka kwatanta da revised budget ɗinta?

```
*Department for Security Matters* (code 017000100200):
• Jimilla: kasafin da aka sabunta ₦10.57 biliyan; abin da aka kashe zuwa yanzu (Q1–Q3) ₦6.78 biliyan; kason kasafin da aka sabunta da aka kashe 64.2% (lissafin Kasafi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 17
```

## spend_quarter-03 (code_switched) ok (3.4s)

**Q:** Nawa Primary School Staff Pension Board ta spend by end of Q4 2024 against revised budget dinta?

```
*Primary School Staff Pension Board* (code 011103500200):
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q4) ₦36.30 miliyan; kasafin da aka sabunta ₦79.84 miliyan; kason kasafin da aka sabunta da aka kashe 45.5% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 16
```

## spend_quarter-04 (code_switched) ok (3.4s)

**Q:** College of Agriculture Wurno ya spend nawa by the end of Q4 2024 against revised budget dinsa?

```
*College of Agriculture Wurno* (code 021502100100):
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q4) ₦236.09 miliyan; kasafin da aka sabunta ₦708.85 miliyan; kason kasafin da aka sabunta da aka kashe 33.3% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 17
```

## spend_quarter-05 (typo) ok (3.5s)

**Q:** How much had teh State Agricultural Development Project spent by the end of Q2 2026, against its revissed budjet?

```
*State Agricultural Development Project* (code 021510200100):
• Total: revised budget ₦675.08 million; spent so far (Q1–Q2) ₦161.86 million; share of the revised budget spent 24.0% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 16
```

## spend_quarter-06 (hausa) WRONG: missing ['31,402,977,832.03', '36,084,264,104.10'] (12.0s)

**Q:** SSG'S Office ya kashe kudi nawa har zuwa karshen Q4 2024, idan aka duba da revised budget dinsa?

```
Ofishin SSG jimillar kasafin 2024 da aka sabunta ya kai ₦36.17 biliyan. Har ƙarshen Q4 2024 (Q1–Q4 2024) ya kashe ₦31.48 biliyan, wato (87.0% na kasafin da aka sabunta).

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 16
```

## spend_quarter-07 (informal) ok (5.0s)

**Q:** how much had Works School Sokoto spent by end Q3 2025 vs its revised budget?

```
*Works School Sokoto* (code 023405400100):
• Total: spent so far (Q1–Q3) ₦7.99 million; revised budget ₦25.40 million; share of the revised budget spent 31.5% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## spend_quarter-08 (hausa) ok (3.9s)

**Q:** Ministry of Energy and Petroleum Resources ta kashe nawa har zuwa karshen Q4 2024, idan aka kwatanta da revised budget dinta?

```
*Ministry of Energy and Petroleum Resources* (code 023100000000):
• Jimilla: kasafin da aka sabunta ₦7.39 biliyan; abin da aka kashe zuwa yanzu (Q1–Q4) ₦2.84 biliyan; kason kasafin da aka sabunta da aka kashe 38.4% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 18
```

## spend_quarter-09 (followup) ok (3.9s)

**Q:** How much had it spent by the end of Q2 2026, against its revised budget?

```
*Liaison Office ABUJA* (code 016102100200):
• Total: revised budget ₦87.18 million; spent so far (Q1–Q2) ₦31.28 million; share of the revised budget spent 35.9% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 15
```

## spend_quarter-10 (hausa) ok (3.2s)

**Q:** Nawa Ministry for Women Affairs ta kashe har zuwa karshen Q2 2026, idan aka kwatanta da revised budget dinta?

```
*Ministry for Women Affairs* (code 051400000000):
• Jimilla: kasafin da aka sabunta ₦7.24 biliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦388.37 miliyan; kason kasafin da aka sabunta da aka kashe 5.4% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 17
```

## spend_quarter-11 (code_switched) ok (12.0s)

**Q:** Agency for Inter-Governmental and Multilateral Affairs ta spend nawa by end of Q2 2026 against revised budget dinta?

```
Agency for Inter-Governmental and Multilateral Affairs tana da kasafin 2026 da aka yi wa kwaskwarima na ₦134.00 miliyan. Zuwa karshen Q2 2026 ba ta kashe komai ba. Adadin kasafin da aka ware ne, adadin kashewa kuma shi ne abin da aka kashe a zahiri.

• Agency for Inter-Governmental and Multilateral Affairs (hukuma ɗaya, duk kashe kuɗi (jimilla), code 023800800100) [Total Expenditure by Administrative Classification], 2026 Revised Budget: ₦134.00 miliyan
• Agency for Inter-Governmental and Multilateral Affairs (hukuma ɗaya, duk kashe kuɗi (jimilla), code 023800800100) [Total Expenditure by Administrative Classification], 2026 Performance Year to Date (Q1-Q2): 0.00

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 17
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## spend_quarter-12 (informal) ok (2.7s)

**Q:** how much had Sultan Maccido Institute for Qur'ani & General Studies spent by end of Q2 2026 vs its revised budget?

```
*Sultan Maccido Institute for Qur'ani & General Studies* (code 051700260100):
• Total: revised budget ₦1.02 billion; spent so far (Q1–Q2) ₦277.12 million; share of the revised budget spent 27.1% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 17
```

## spend_quarter-13 (template) ok (3.4s)

**Q:** How much had the Sokoto Erosion and Watershed Management Agency (SEWMA) spent by the end of Q3 2025, against its revised budget?

```
*Sokoto Erosion and Watershed Management Agency (SEWMA)* (code 053501600200):
• Total: spent so far (Q1–Q3) ₦0.00; revised budget ₦161.67 million; share of the revised budget spent 0.0% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 19
```

## spend_quarter-14 (code_switched) ok (2.8s)

**Q:** Ministry of Finance ta kashe nawa by end of Q4 2024 against revised budget dinta?

```
*Ministry of Finance* (code 022000000000):
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q4) ₦26.11 biliyan; kasafin da aka sabunta ₦30.06 biliyan; kason kasafin da aka sabunta da aka kashe 86.9% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 17
```

## spend_quarter-15 (typo) ok (3.4s)

**Q:** How much had teh Agency for Persons Living With Disabilities spent by the end of Q2 2026, againts its revised budjet?

```
*Agency for Persons Living With Disabilities* (code 051300300100):
• Total: revised budget ₦3.07 billion; spent so far (Q1–Q2) ₦270.61 million; share of the revised budget spent 8.8% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 17
```

## spend_quarter-16 (followup) ok (2.8s)

**Q:** How much had it spent by the end of Q3 2025, against its revised budget?

```
*Ministry for Skills Acquisition and Entrepreneurship Development* (code 028900000000):
• Total: spent so far (Q1–Q3) ₦65.50 million; share of the revised budget spent 4.4% (Kasafi's calculation); revised budget ₦1.50 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## spend_quarter-17 (template) ok (3.3s)

**Q:** How much had the Ministry of Science and Technology spent by the end of Q2 2026, against its revised budget?

```
*Ministry of Science and Technology* (code 022800000000):
• Total: revised budget ₦11.69 billion; spent so far (Q1–Q2) ₦1.53 billion; share of the revised budget spent 13.1% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 16
```

## spend_quarter-18 (hausa) ok (9.9s)

**Q:** Nawa Livestock Development Programme ta kashe har zuwa karshen Q3 2025 idan aka kwatanta da revised budget nata?

```
• Kaso (↑ ÷ ↓): 14.5% (lissafin Kasafi)

• Livestock Development Programme (hukuma ɗaya, duk kashe kuɗi (jimilla), code 026800200100) [Total Expenditure by Administrative Classification], 2025 Performance Year to Date (Q1-Q3): ₦43.60 miliyan ↑
• Livestock Development Programme (hukuma ɗaya, duk kashe kuɗi (jimilla), code 026800200100) [Total Expenditure by Administrative Classification], 2025 Revised Budget: ₦300.87 miliyan ↓

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## spend_quarter-19 (followup) ok (4.7s)

**Q:** How much had it spent by the end of Q3 2025, against its revised budget?

```
*Maryam Abacha W& Child. Hospital* (code 052102600200):
• Total: revised budget ₦803.93 million; spent so far (Q1–Q3) ₦667.43 million; share of the revised budget spent 83.0% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 19
```

## compare-01 (followup) ok (9.6s)

**Q:** How does its approved budget in 2025 compare with that in 2026?

```
Law and Justice's approved budget (total) was ₦10.74 billion in 2025. It was ₦14.26 billion in 2026.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18; Sokoto State Government 2025 Approved Budget, p. 12
```

## compare-02 (informal) ok (2.8s)

**Q:** How much approved budget did the Ministry for Skills Acquisition and Entrepreneurship Development get in 2025 vs 2026?

```
*Ministry for Skills Acquisition and Entrepreneurship Development* (code 028900000000):
• Total: 2025 approved budget ₦1.50 billion; 2026 approved budget ₦1.37 billion; change -₦125.00 million (-8.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-03 (template) ok (3.2s)

**Q:** Compare the Civil Service Commission's approved budget in 2025 and 2026.

```
*Civil Service Commission* (code 014700000000):
• Total: 2025 approved budget ₦254.99 million; 2026 approved budget ₦403.14 million; change +₦148.15 million (+58.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-04 (followup) ok (3.6s)

**Q:** How does its approved budget in 2025 compare to 2026?

```
*Ministry of Education* (code 051700000000):
• Total: 2025 approved budget ₦59.59 billion; 2026 approved budget ₦68.95 billion; change +₦9.36 billion (+15.7%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-05 (informal) ok (3.3s)

**Q:** Government House approved budget, 2025 vs 2026?

```
*Government House* (code 011100000000):
• Total: 2025 approved budget ₦14.03 billion; 2026 approved budget ₦18.53 billion; change +₦4.50 billion (+32.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-06 (followup) ok (3.1s)

**Q:** Compare its approved budget in 2025 and 2026.

```
*Ministry of Works* (code 023400000000):
• Total: 2025 approved budget ₦59.39 billion; 2026 approved budget ₦59.17 billion; change -₦227.66 million (-0.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-07 (followup) ok (3.1s)

**Q:** Compare its approved budget in 2025 and 2026?

```
*Local Government Service Commission* (code 014900000000):
• Total: 2025 approved budget ₦555.67 million; 2026 approved budget ₦746.52 million; change +₦190.85 million (+34.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-08 (typo) ok (3.5s)

**Q:** Compre the Ministry of Transports approved budjet in 2025 and 2026.

```
*Ministry of Transport* (code 022900000000):
• Total: 2025 approved budget ₦3.65 billion; 2026 approved budget ₦50.87 billion; change +₦47.21 billion (+1292.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-09 (code_switched) ok (3.3s)

**Q:** Kwatanta mana Office of Auditor General approved budget na 2025 da 2026?

```
*Office of Auditor General* (code 014000000000):
• Jimilla: 2025 kasafin da aka amince ₦542.84 miliyan; 2026 kasafin da aka amince ₦606.84 miliyan; bambanci +₦64.00 miliyan (+11.8%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-10 (typo) ok (2.8s)

**Q:** Comapare the Ministry of Enviroment's approved budjet in 2025 and 2026.

```
*Ministry of Environment* (code 053500000000):
• Total: 2025 approved budget ₦24.52 billion; 2026 approved budget ₦20.77 billion; change -₦3.75 billion (-15.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-11 (followup) ok (3.2s)

**Q:** And what was its approved budget in 2025 compared to 2026?

```
*Fiscal Responsibility Commission* (code 025000000000):
• Total: 2025 approved budget ₦58.99 million; 2026 approved budget ₦60.99 million; change +₦2.00 million (+3.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-12 (hausa) ok (3.0s)

**Q:** Kwatanta approved budget na Ministry of Commerce and Industry a 2025 da 2026.

```
*Ministry of Commerce and Industry* (code 022200000000):
• Jimilla: 2025 kasafin da aka amince ₦6.06 biliyan; 2026 kasafin da aka amince ₦6.56 biliyan; bambanci +₦503.51 miliyan (+8.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-13 (informal) ok (3.2s)

**Q:** Assembly's approved budget 2025 vs 2026?

```
*Sokoto State House of Assembly* (code 011200000000):
• Total: 2025 approved budget ₦9.37 billion; 2026 approved budget ₦12.26 billion; change +₦2.89 billion (+30.8%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-14 (informal) ok (3.0s)

**Q:** Ministry for Local Government and Chieftancy approved budget - 2025 vs 2026?

```
*Ministry for Local Government and Chieftancy* (code 055100000000):
• Total: 2025 approved budget ₦570.64 million; 2026 approved budget ₦1.36 billion; change +₦788.43 million (+138.2%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 19
```

## compare-15 (typo) ok (4.3s)

**Q:** Compare the Office of Haed of Servcie's approved budjet in 2025 and 2026.

```
*Office of Head of Service* (code 012500000000):
• Total: 2025 approved budget ₦3.41 billion; 2026 approved budget ₦10.44 billion; change +₦7.03 billion (+206.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-16 (code_switched) ok (11.6s)

**Q:** Compare approved budget na Social Sector a 2025 da 2026 fa?

```
Kasafin Social Sector da aka amince da shi (jimilla) a 2025 shi ne ₦175.57 biliyan. Kasafin da aka amince da shi (jimilla) a 2026 shi ne ₦278.88 biliyan. Abin da aka kashe a 2025 (Janairu-Satumba 2025 kawai) shi ne ₦63.25 biliyan.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-17 (typo) ok (3.6s)

**Q:** Compre the Ministry of Culture & Tourism's aproved budget in 2025 and 2026.

```
*Ministry of Culture & Tourism* (code 023600000000):
• Total: 2025 approved budget ₦1.21 billion; 2026 approved budget ₦1.42 billion; change +₦214.73 million (+17.7%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-18 (code_switched) ok (3.5s)

**Q:** Kwatanta Office of the SSG approved budget for 2025 da kuma 2026 fa?

```
*Office of the SSG* (code 016100000000):
• Jimilla: 2025 kasafin da aka amince ₦31.36 biliyan; 2026 kasafin da aka amince ₦40.40 biliyan; bambanci +₦9.04 biliyan (+28.8%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-19 (typo) ok (2.9s)

**Q:** Compare teh Ministry for Special Duties's aproved budget in 2025 and 2026.

```
*Ministry for Special Duties* (code 016700000000):
• Total: 2025 approved budget ₦423.00 million; 2026 approved budget ₦829.50 million; change +₦406.50 million (+96.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## share-01 (template) ok (3.6s)

**Q:** What share of the Ministry of Science and Technology's 2026 approved budget is capital?

```
*Ministry of Science and Technology* (code 022800000000):
• Capital: approved budget ₦9.02 billion; 77.2% of its total (Kasafi's calculation)
• Total: approved budget ₦11.69 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-02 (code_switched) ok (4.4s)

**Q:** Approved budget na 2026 na Ministry for Local Government and Chieftancy, what share ne capital?

```
*Ministry for Local Government and Chieftancy* (code 055100000000):
• Manyan ayyuka: kasafin da aka amince ₦850.44 miliyan; 62.6% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦1.36 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 19, 27
```

## share-03 (hausa) ok (4.4s)

**Q:** Nawa ne kaso na capital a cikin approved budget na 2026 na State Agency for Normadic Education1?

```
*State Agency for Normadic Education* (code 051701100100):
• Manyan ayyuka: kasafin da aka amince ₦383.42 miliyan; 49.5% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦774.42 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 27
```

## share-04 (followup) ok (3.5s)

**Q:** What share of its 2026 approved budget is capital?

```
*Ministry of Energy and Petroleum Resources* (code 023100000000):
• Capital: approved budget ₦22.47 billion; 96.3% of its total (Kasafi's calculation)
• Total: approved budget ₦23.33 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-05 (code_switched) ok (3.3s)

**Q:** House of Assembly Service Commission 2026 approved budget din, what share ne capital?

```
*House of Assembly Service Commission* (code 011200400100):
• Manyan ayyuka: kasafin da aka amince ₦525.50 miliyan; 82.9% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦634.28 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-06 (code_switched) ok (3.3s)

**Q:** Approved budget na Sokoto State House of Assembly na 2026, what share is capital?

```
*Sokoto State House of Assembly* (code 011200000000):
• Manyan ayyuka: kasafin da aka amince ₦4.66 biliyan; 38.0% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦12.26 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-07 (followup) ok (4.2s)

**Q:** What share of its 2026 approved budget there is capital?

```
*Ministry of Budget and Economic Planning* (code 023800000000):
• Capital: approved budget ₦2.22 billion; 41.8% of its total (Kasafi's calculation)
• Total: approved budget ₦5.32 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-08 (hausa) ok (3.6s)

**Q:** Kashi nawa daga cikin aminceccen kasafin kudin 2026 na State Universal Basic Education Board (SUBEB) ne kudin jari (capital)?

```
*State Universal Basic Education Board (SUBEB)* (code 051700300100):
• Manyan ayyuka: kasafin da aka amince ₦9.15 biliyan; 85.2% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦10.73 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 27
```

## share-09 (informal) ok (3.2s)

**Q:** How much of the Department for Rural Water's 2026 approved budget is capital?

```
*Department for Rural Water* (code 025210400100):
• Capital: approved budget ₦3.21 billion; 88.9% of its total (Kasafi's calculation)
• Total: approved budget ₦3.62 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-10 (typo) ok (4.9s)

**Q:** What sahre of the Sokoto State Univeristy's 2026 approved budjet is capital?

```
*Sokoto State University* (code 056900400100):
• Capital: approved budget ₦3.50 billion; 61.3% of its total (Kasafi's calculation)
• Total: approved budget ₦5.71 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 27
```

## share-11 (followup) ok (4.2s)

**Q:** What share of its 2026 approved budget is capital?

```
*Parks and Gardens Agency* (code 053500200100):
• Capital: approved budget ₦4.07 billion; 97.9% of its total (Kasafi's calculation)
• Total: approved budget ₦4.15 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 27
```

## share-12 (followup) ok (3.6s)

**Q:** What share of its 2026 approved budget is capital?

```
*Ministry of Solid Minerals and Natural Resources* (code 023300000000):
• Capital: approved budget ₦610.10 million; 62.9% of its total (Kasafi's calculation)
• Total: approved budget ₦969.94 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-13 (followup) ok (3.6s)

**Q:** What share of its 2026 approved budget is capital?

```
*Department for Security Matters* (code 017000100200):
• Capital: approved budget ₦8.30 billion; 31.5% of its total (Kasafi's calculation)
• Total: approved budget ₦26.37 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 25
```

## share-14 (informal) ok (3.7s)

**Q:** Of the Ministry of Humanitarian Affairs & Social Welfare's 2026 approved budget, what's the capital share?

```
*Ministry of Humanitarian Affairs & Social Welfare* (code 055600100100):
• Capital: approved budget ₦3.72 billion; 72.7% of its total (Kasafi's calculation)
• Total: approved budget ₦5.11 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 27
```

## share-15 (template) ok (3.3s)

**Q:** What share of the Poultry Development Agency's 2026 approved budget is capital?

```
*Poultry Development Agency* (code 026800300100):
• Capital: approved budget ₦236.00 million; 78.1% of its total (Kasafi's calculation)
• Total: approved budget ₦302.14 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-16 (code_switched) ok (4.8s)

**Q:** Wani share ne capital a cikin 2026 approved budget na Ministry of Agriculture & Natural Resource?

```
*Ministry of Agriculture & Natural Resource* (code 021500000000):
• Manyan ayyuka: kasafin da aka amince ₦14.93 biliyan; 87.6% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦17.05 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 25
```

## share-17 (followup) ok (3.1s)

**Q:** What share of its 2026 approved budget is capital?

```
*Ministry of Transport* (code 022900000000):
• Capital: approved budget ₦47.67 billion; 93.7% of its total (Kasafi's calculation)
• Total: approved budget ₦50.87 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-18 (typo) ok (4.0s)

**Q:** What sahre of the Fisccal Responsibility Commission's 2026 approved budgte is capital?

```
*Fiscal Responsibility Commission* (code 025000000000):
• Capital: approved budget ₦14.25 million; 23.4% of its total (Kasafi's calculation)
• Total: approved budget ₦60.99 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-19 (template) ok (4.4s)

**Q:** What share of the Department for Rural Electrification's 2026 approved budget is capital?

```
*Department for Rural Electrification* (code 023100100200):
• Capital: approved budget ₦1.12 billion; 90.3% of its total (Kasafi's calculation)
• Total: approved budget ₦1.25 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## false_premise-01 (hausa) ok (3.6s)

**Q:** Me ya sa kasafin kudin Ministry of Solid Minerals and Natural Resources da aka amince da shi ya ragu daga 2025 zuwa 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
*Ministry of Solid Minerals and Natural Resources* (code 023300000000):
• Albashi: 2025 kasafin da aka amince ₦56.34 miliyan; 2026 kasafin da aka amince ₦45.34 miliyan; bambanci -₦11.00 miliyan (-19.5%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦139.25 miliyan; 2026 kasafin da aka amince ₦314.50 miliyan; bambanci +₦175.25 miliyan (+125.9%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦283.50 miliyan; 2026 kasafin da aka amince ₦610.10 miliyan; bambanci +₦326.60 miliyan (+115.2%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦479.09 miliyan; 2026 kasafin da aka amince ₦969.94 miliyan; bambanci +₦490.85 miliyan (+102.5%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 13, 15, 16; Sokoto State FY 2026 Budget, shafi 17, 20, 23, 26
```

## false_premise-02 (typo) ok (11.2s)

**Q:** Why did teh Local Government Service Commision's aproved budget fall from 2025 to 2026?

```
The Commission's approved budget did not fall. It rose from ₦555.67 million in 2025 to ₦746.52 million in 2026 (Kasafi's calculation) ₦190.85 million (Kasafi's calculation) 34.3%.

• Local Government Service Commission (ministry total including its agencies, all spending (total), code 014900000000), 2025 Approved Budget: ₦555.67 million
• Local Government Service Commission (ministry total including its agencies, all spending (total), code 014900000000), 2026 Approved Budget: ₦746.52 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-03 (code_switched) ok (2.7s)

**Q:** Abeg why Ministry Careers & Special Services approved budget ya fall daga 2025 to 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
*Ministry Careers & Special Services* (code 017000000000):
• Albashi: 2025 kasafin da aka amince ₦51.37 miliyan; 2026 kasafin da aka amince ₦63.37 miliyan; bambanci +₦12.00 miliyan (+23.4%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦10.04 biliyan; 2026 kasafin da aka amince ₦18.00 biliyan; bambanci +₦7.96 biliyan (+79.3%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦481.00 miliyan; 2026 kasafin da aka amince ₦8.30 biliyan; bambanci +₦7.82 biliyan (+1626.6%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦10.57 biliyan; 2026 kasafin da aka amince ₦26.37 biliyan; bambanci +₦15.80 biliyan (+149.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 13, 14, 16; Sokoto State FY 2026 Budget, shafi 16, 19, 22, 25
```

## false_premise-04 (informal) ok (16.2s)

**Q:** why did the Ministry of Lands and Housing's approved budget go up from 2025 to 2026?

```
The Ministry of Lands and Housing's approved budget did not go up. Its all spending (total) was ₦47.46 billion in the 2025 Approved Budget and ₦35.78 billion in the 2026 Original Budget.

• Ministry of Lands and Housing (ministry total including its agencies, all spending (total), code 025300000000), 2025 Approved Budget: ₦47.46 billion
• Ministry of Lands and Housing (ministry total including its agencies, all spending (total), code 025300000000), 2026 Original Budget: ₦35.78 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Budget Implementation Report Q2 2026, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-05 (code_switched) ok (5.0s)

**Q:** Me yasa Sokoto State House of Assembly approved budget ya fall daga 2025 to 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
*Sokoto State House of Assembly* (code 011200000000):
• Albashi: 2025 kasafin da aka amince ₦1.15 biliyan; 2026 kasafin da aka amince ₦1.60 biliyan; bambanci +₦450.00 miliyan (+39.3%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦4.82 biliyan; 2026 kasafin da aka amince ₦6.00 biliyan; bambanci +₦1.18 biliyan (+24.4%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦3.41 biliyan; 2026 kasafin da aka amince ₦4.66 biliyan; bambanci +₦1.26 biliyan (+36.9%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦9.37 biliyan; 2026 kasafin da aka amince ₦12.26 biliyan; bambanci +₦2.89 biliyan (+30.8%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 12, 14, 15; Sokoto State FY 2026 Budget, shafi 16, 19, 22, 25
```

## false_premise-06 (followup) ok (12.0s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
The Ministry of Health's approved budget did not fall from 2025 to 2026. The 2025 approved budget (total) was ₦52.18 billion (allocated), and the 2026 approved budget (total) was ₦124.41 billion (allocated). Spending in January–September 2025 only was ₦14.06 billion (spent).

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-07 (template) ok (15.0s)

**Q:** Why did the Ministry of Finance's approved budget rise from 2025 to 2026?

```
The Ministry of Finance's approved budget did not rise from 2025 to 2026. It was ₦47.75 billion in 2025 and ₦40.27 billion in 2026.

• Ministry of Finance (ministry total including its agencies, all spending (total), code 022000000000), 2025 Approved Budget: ₦47.75 billion
• Ministry of Finance (ministry total including its agencies, all spending (total), code 022000000000), 2026 Approved Budget: ₦40.27 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-08 (code_switched) ok (3.2s)

**Q:** Me ya sa Ministry for Local Government and Chieftancy approved budget ya fall daga 2025 to 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
*Ministry for Local Government and Chieftancy* (code 055100000000):
• Albashi: 2025 kasafin da aka amince ₦145.67 miliyan; 2026 kasafin da aka amince ₦190.67 miliyan; bambanci +₦45.00 miliyan (+30.9%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦211.97 miliyan; 2026 kasafin da aka amince ₦317.96 miliyan; bambanci +₦105.99 miliyan (+50.0%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦213.00 miliyan; 2026 kasafin da aka amince ₦850.44 miliyan; bambanci +₦637.44 miliyan (+299.3%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦570.64 miliyan; 2026 kasafin da aka amince ₦1.36 biliyan; bambanci +₦788.43 miliyan (+138.2%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12, 14, 15, 17; Sokoto State FY 2026 Budget, shafi 19, 21, 24, 27
```

## false_premise-09 (template) WRONG: didn't correct a premise the figures contradict (16.8s)

**Q:** Why did the Ministry of Works's approved budget rise from 2025 to 2026?

```
The Ministry of Works total was ₦59.39 billion in the 2025 approved budget. It shows ₦50.52 billion as the 2025 revised budget and ₦59.17 billion as the 2026 approved budget. The tables do not give a reason why the figure changed.

• 2025 approved budget (capital): ₦58.71 billion
• 2025 revised budget (capital): ₦49.84 billion
• 2026 approved budget (capital): ₦58.13 billion
• 2025 spending January-September only (total): ₦9.15 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 16; Sokoto State FY 2026 Budget, p. 17, 26
```

## false_premise-10 (informal) WRONG: WRONG AGENCY 016100100100 (19.9s)

**Q:** why'd the Office of the SSG's approved budget fall from 2025 to 2026?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• SSG'S Office (code 016100100100, Capital Expenditure by Project), 2025 Revised Budget: ₦100.00 million [1]
• SSG'S Office (code 016100100100, Capital Expenditure by Project), 2026 Approved Budget: 0.00 [1]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 51
```

## false_premise-11 (followup) ok (3.8s)

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

## false_premise-12 (typo) ok (14.9s)

**Q:** Why did teh Economic Sector's aproved budget fall from 2025 to 2026?

```
The Economic Sector's approved budget did not fall. Its total allocation rose from ₦237.36 billion in 2025 to ₦316.04 billion in 2026, 33.1% (Kasafi's calculation).

• Economic Sector (ministry total including its agencies, all spending (total), code 020000000000), 2025 Original Budget: ₦237.36 billion
• Economic Sector (ministry total including its agencies, all spending (total), code 020000000000), 2026 Original Budget: ₦316.04 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 17; Sokoto State Budget Implementation Report Q1 2026, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-13 (typo) ok (3.8s)

**Q:** Why did the Goverment House's approved budget fall form 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Government House* (code 011100000000):
• Personnel (salaries): 2025 approved budget ₦353.01 million; 2026 approved budget ₦444.25 million; change +₦91.24 million (+25.8%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦9.68 billion; 2026 approved budget ₦11.44 billion; change +₦1.76 billion (+18.2%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦3.99 billion; 2026 approved budget ₦6.64 billion; change +₦2.65 billion (+66.3%) (Kasafi's calculation)
• Total: 2025 approved budget ₦14.03 billion; 2026 approved budget ₦18.53 billion; change +₦4.50 billion (+32.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 12, 14, 15; Sokoto State FY 2026 Budget, p. 16, 19, 21, 25
```

## false_premise-14 (typo) ok (10.5s)

**Q:** Why did teh Civil Service Commision's approved budjet fall from 2025 to 2026?

```
The Civil Service Commission's approved budget did not fall. It rose from ₦254.99 million in 2025 to ₦403.14 million in 2026, a rise of ₦148.15 million (Kasafi's calculation).

• Civil Service Commission (ministry total including its agencies, all spending (total), code 014700000000), 2025 Approved Budget: ₦254.99 million
• Civil Service Commission (ministry total including its agencies, all spending (total), code 014700000000), 2026 Approved Budget: ₦403.14 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-15 (code_switched) ok (3.8s)

**Q:** Me yasa approved budget na Ministry of Commerce and Industry ya fall daga 2025 to 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
*Ministry of Commerce and Industry* (code 022200000000):
• Albashi: 2025 kasafin da aka amince ₦122.77 miliyan; 2026 kasafin da aka amince ₦193.00 miliyan; bambanci +₦70.23 miliyan (+57.2%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦1.04 biliyan; 2026 kasafin da aka amince ₦2.16 biliyan; bambanci +₦1.12 biliyan (+107.5%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦4.89 biliyan; 2026 kasafin da aka amince ₦4.21 biliyan; bambanci -₦686.27 miliyan (-14.0%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦6.06 biliyan; 2026 kasafin da aka amince ₦6.56 biliyan; bambanci +₦503.51 miliyan (+8.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 13, 14, 16; Sokoto State FY 2026 Budget, shafi 17, 20, 23, 25
```

## false_premise-16 (followup) ok (3.3s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry of Science and Technology* (code 022800000000):
• Total: 2025 approved budget ₦6.82 billion; 2026 approved budget ₦11.69 billion; change +₦4.87 billion (+71.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-17 (hausa) WRONG: not found, though the data has it (16.3s)

**Q:** Me ya sa approved budget na Law and Justice ya fadi daga 2025 zuwa 2026?

```
Zan iya fahimtar tambayarka ta hanyoyi biyu. Wanne kake nufi?
```

## false_premise-18 (hausa) ok (2.8s)

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

## false_premise-19 (typo) ok (13.8s)

**Q:** Why did the Office of Auditor Genral's aproveed budget fall from 2025 to 2026?

```
The budget did not fall from 2025 to 2026. The 2025 approved allocation (total) was ₦542.84 million and the 2026 approved allocation (total) was ₦606.84 million.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## not_in_data-01 (hausa) ok (4.8s)

**Q:** Nawa ne kasafin kudin Water Board da aka amince da shi na 2028?

```
Ba a cikin takardun ba:
• Water Board 2028 kasafin da aka amince: kasafin 2028 ba ya cikin ɗakin karatu (kasafin da ke akwai: 2024–2026)
```

## not_in_data-02 (template) ok (10.1s)

**Q:** How much did the Ministry of Environment spend in Q4 2026?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Ministry of Environment (ministry total including its agencies, capital, code 053500000000, Capital Expenditure by Administrative Classification), 2026 Q2 Performance: ₦7.84 billion [1]
• Ministry of Environment (ministry total including its agencies, capital, code 053500000000, Capital Expenditure by Administrative Classification), 2026 Q1 Performance: ₦12.50 million [2]
• Ministry of Environment (one agency or unit, capital, code 053500100100, Capital Expenditure by Administrative Classification), 2026 Q2 Performance: ₦7.84 billion [1]

📄 *Sources:* Budget Implementation Report Q2 2026, p. 28; Sokoto State Budget Implementation Report Q1 2026, p. 29
```

## not_in_data-03 (hausa) WRONG: no mention of what exists (Q2 2026) (11.6s)

**Q:** Nawa SSG'S Office ya kashe a Q4 2026?

```
Ban samo takardar da ake buƙata a shafukan da na amince da su ba (Sokoto State Budget Implementation Report Q4 2026). Na ajiye buƙatar domin ma'aikatanmu su duba.
```

## not_in_data-04 (typo) ok (3.7s)

**Q:** How muhc did the Female Education Board spned in Q4 2026?

```
Not in the documents:
• Female Education Board 2026 spent in Q4: the latest implementation report is Q2 2026
• Female Education Board 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
```

## not_in_data-05 (typo) ok (4.4s)

**Q:** How muhc did the Social Cash Tranfer Unit spend in Q1 2027?

```
Not in the documents:
• Social Cash Transfer Unit 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Social Cash Transfer Unit 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-06 (hausa) ok (4.2s)

**Q:** Nawa Agency for Industrial Development ta kashe a Q4 2026?

```
Ba a cikin takardun ba:
• Agency for Industrial Development 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Agency for Industrial Development 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-07 (code_switched) ok (3.3s)

**Q:** Nawa Ministry for Skills Acquisition and Entrepreneurship Development ta spend in Q4 2026?

```
Ba a cikin takardun ba:
• Ministry for Skills Acquisition and Entrepreneurship Development 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-08 (typo) ok (3.6s)

**Q:** How much did teh Ministry of Informaton spend in Q4 2026?

```
Not in the documents:
• Ministry of Information 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
• Ministry of Information 2026 spent in Q4: the latest implementation report is Q2 2026
```

## not_in_data-09 (informal) ok (11.9s)

**Q:** What's POVERTY REDUCTION PROGRAMME's approved budget for 2028?

```
⚠️ I couldn't get the document that fits best (Sokoto State Government 2028 Approved Budget). The answer below is from other documents I have, not from that one.

POVERTY REDUCTION PROGRAMME's 2028 figure is a total out-year estimate of ₦2.61 billion. It is shown in the Total Expenditure by Administrative Classification table. This is a budgeted estimate, not actual spending.

• 2028 out-year estimate (personnel): ₦39.79 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 19
```

## not_in_data-10 (typo) ok (4.6s)

**Q:** How mucj did the Shehu Shagari Univeristy of Education spnd in Q4 2026?

```
Not in the documents:
• Shehu Shagari University of Education 2026 spent in Q4: the latest implementation report is Q2 2026
```

## not_in_data-11 (informal) ok (9.7s)

**Q:** Parks and Gardens Agency's approved budget for 2028 — how much?

```
The Parks and Gardens Agency total is shown as ₦5.80 billion for 2028. This figure is the 2028 Out-Year Estimate in the 2026 budget, not a 2028 approved budget.

• Parks and Gardens Agency (one agency or unit, all spending (total), code 053500200100), 2028 Out-Year Estimate: ₦5.80 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19
_Reply *show working* to see the rows and arithmetic._
```

## not_in_data-12 (code_switched) ok (3.1s)

**Q:** Ministry of Science and Technology ta spend nawa in Q4 2026?

```
Ba a cikin takardun ba:
• Ministry of Science and Technology 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Ministry of Science and Technology 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Ministry of Science and Technology 2026 kason kasafin da aka sabunta da aka kashe: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-13 (informal) ok (5.0s)

**Q:** how much did State Newspaper Comp.(The PATH) spend in Q4 2026?

```
Not in the documents:
• State Newspaper Comp.(The PATH) 2026 spent in Q4: the latest implementation report is Q2 2026
```

## not_in_data-14 (followup) ok (13.3s)

**Q:** How much is its approved budget for 2028?

```
⚠️ I couldn't get the document that fits best (IFAD Approved Budget 2028 or Sokoto State 2028 Approved Budget if the question meant Sokoto State). The answer below is from other documents I have, not from that one.

The International Fund for Agriculture has a 2028 figure (total) of ₦131.08 million. It is shown as a 2028 Out-Year Estimate in the 2026 budget, not as a 2028 approved budget.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
```

## not_in_data-15 (typo) ok (5.3s)

**Q:** How mucj did the Commodity Board spned in Q1 2027?

```
Not in the documents:
• Commodity Board 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Commodity Board 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-16 (typo) ok (9.1s)

**Q:** How muhc is the Teachers Service Board(Secondary Edu. Board)'s aproved budget for 2028?

```
The 2026 budget prints only a 2028 projection for the Teachers Service Board (Secondary Edu. Board), not a 2028 approved budget. That 2028 projection is ₦7.46 billion.

• Teachers Service Board(Secondary Edu. Board) (one agency or unit, all spending (total), code 051705400200), 2028 Out-Year Estimate: ₦7.46 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18
_Reply *show working* to see the rows and arithmetic._
```

## not_in_data-17 (followup) WRONG: no mention of what exists (2024–2026) (11.8s)

**Q:** How much is its approved budget for 2028?

```
⚠️ I couldn't get the document that fits best (Sokoto State Government 2028 Approved Budget). The answer below is from other documents I have, not from that one.

No 2028 approved budget is shown in the evidence, only a 2028 out-year estimate from the 2026 budget. That total expenditure estimate for the Ministry of Budget and Economic Planning is ₦5.85 billion.

• 2028 out-year estimate (total): ₦5.85 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
```

## not_in_data-18 (template) ok (3.4s)

**Q:** How much did the Ministry of Transport spend in Q1 2027?

```
Not in the documents:
• Ministry of Transport 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• Ministry of Transport 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-19 (code_switched) ok (10.7s)

**Q:** Nawa Nigeria CARES- Fadama Programme ta spend a Q4 2026?

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• Nigeria CARES- Fadama Programme (one agency or unit, overhead (running costs), code 021510200300, Overhead Expenditure by Administrative Classification), 2026 Performance Year to Date (Q1-Q2): ₦800,000.00 [1]
• Nigeria CARES- Fadama Programme (one agency or unit, capital, code 021510200300, Capital Expenditure by Administrative Classification), 2026 Q2 Performance: 0.00 [2]
• Nigeria CARES- Fadama Programme (one agency or unit, all spending (total), code 021510200300, Total Expenditure by Administrative Classification), 2026 Q2 Performance: ₦600,000.00 [3]

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 16, 23, 26
```

## rank_lga-01 (followup) ok (5.2s)

**Q:** Which 10 LGAs there have the most IDPs?

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

## rank_lga-02 (typo) ok (6.2s)

**Q:** Which 5 LGAs ni Sokoto hvae the most IDPs?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143
4. Tureta: 15,068
5. Shagari: 14,850

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-03 (hausa) ok (4.5s)

**Q:** Wadanne LGAs 3 ne a Sokoto da suka fi yawan IDPs?

```
Ta ƙaramar hukuma (22), mafi yawa:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-01 (typo) ok (4.9s)

**Q:** How mnay IDPs aer there in Dange-Shuni LGA?

```
IOM DTM counts *4,615* IDPs in Dange Shuni (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (typo) ok (4.9s)

**Q:** How mnay IDPs aer there in Sokoto South LGA?

```
IOM DTM counts *4,486* IDPs in Sokoto South (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-03 (hausa) ok (4.4s)

**Q:** IDPs nawa ne suke a Bodinga LGA?

```
IOM DTM ta ƙidaya *1,990* 'yan gudun hijira a Bodinga (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-04 (code_switched) ok (5.6s)

**Q:** How many IDPs ne a Kware LGA?

```
IOM DTM ta ƙidaya *1,039* 'yan gudun hijira a Kware (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-05 (template) ok (7.2s)

**Q:** How many IDPs are there in Shagari LGA?

```
IOM DTM counts *14,850* IDPs in Shagari (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-06 (code_switched) ok (5.5s)

**Q:** Sokoto North LGA fa, how many IDPs are there?

```
IOM DTM ta ƙidaya *2,274* 'yan gudun hijira a Sokoto North (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-07 (informal) ok (5.8s)

**Q:** how many IDPs in Kebbe LGA?

```
IOM DTM counts *4,252* IDPs in Kebbe (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-08 (typo) ok (4.3s)

**Q:** How mnay IDPs are thre in Binji LGA?

```
IOM DTM counts *619* IDPs in Binji (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-09 (typo) ok (5.9s)

**Q:** How mnay IDPs are thre in Wamako LGA?

```
IOM DTM counts *4,026* IDPs in Wamakko (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-10 (hausa) ok (4.1s)

**Q:** Adadin IDPs nawa ne a Gwadabawa LGA?

```
IOM DTM ta ƙidaya *8,406* 'yan gudun hijira a Gwadabawa (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-11 (typo) ok (5.2s)

**Q:** How mnay IDPs aer there in Isa LGA?

```
IOM DTM counts *14,047* IDPs in Isa (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-12 (code_switched) ok (6.5s)

**Q:** IDPs nawa are there in Tangaza LGA?

```
IOM DTM ta ƙidaya *19,151* 'yan gudun hijira a Tangaza (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-13 (code_switched) ok (5.4s)

**Q:** Nawa IDPs are there in Tureta LGA?

```
IOM DTM ta ƙidaya *15,068* 'yan gudun hijira a Tureta (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-14 (informal) ok (5.3s)

**Q:** how many IDPs in Illela LGA?

```
IOM DTM counts *8,953* IDPs in Illela (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-15 (code_switched) ok (5.4s)

**Q:** How many IDPs ne a Goronyo LGA?

```
IOM DTM ta ƙidaya *1,926* 'yan gudun hijira a Goronyo (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-16 (informal) ok (5.8s)

**Q:** how many IDPs in Wurno LGA?

```
IOM DTM counts *2,128* IDPs in Wurno (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-17 (template) ok (5.7s)

**Q:** How many IDPs are there in Silame LGA?

```
IOM DTM counts *3,386* IDPs in Silame (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-18 (typo) ok (6.1s)

**Q:** How mnay IDPs are there ni Rabah LGA?

```
IOM DTM counts *8,277* IDPs in Rabah (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-19 (typo) ok (5.3s)

**Q:** How mnay IDPs aer there in Sabon Birni LGA?

```
IOM DTM counts *40,729* IDPs in Sabon Birni (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## trend-01 (typo) ok (4.3s)

**Q:** How has teh numer of IDPs in Sokoto State changed over the last DTM rounds?

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

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```
