# Generated coverage run

Cases: cases-366119.json (draw seed 366119), form seed 1

156 cases: wrong 23 (14.7%), of them wrong agency 2 | median 4.2s

| family | wrong | of |
|---|---|---|
| compare | 1 | 19 |
| false_premise | 17 | 19 |
| lookup | 2 | 19 |
| lookup_lga | 0 | 19 |
| not_in_data | 0 | 19 |
| rank_lga | 0 | 3 |
| share | 0 | 19 |
| spend_quarter | 3 | 19 |
| split | 0 | 19 |
| trend | 0 | 1 |

| form | wrong | of |
|---|---|---|
| code_switched | 6 | 33 |
| followup | 2 | 26 |
| hausa | 4 | 21 |
| informal | 2 | 19 |
| template | 2 | 23 |
| typo | 7 | 34 |

```
Cost of this run:
  Baseten: 34 calls, 237,725 prompt tokens (62,976 cached), 15,443 output tokens -> $0.29
  Meta: 379 calls, 1,250,610 prompt tokens (741,166 cached), 287,787 output tokens -> $1.97
  models together: $2.26 (prices per 1M tokens from settings kasafi_price_*)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0)
```

## lookup-01 (hausa) ok (13.4s)

**Q:** Nawa aka amince wa Ministry of Culture & Tourism a budget na 2026?

```
An amince wa Ministry of Culture & Tourism jimilla ₦1.42 biliyan a kasafin 2026. Wannan kuɗin da aka amince ne, ba kuɗin da aka kashe ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
```

## lookup-02 (typo) ok (12.7s)

**Q:** How mouch was aproved for the Ministry Careers & Special Services in the 2026 budget?

```
The 2026 approved total for the Ministry Careers & Special Services is ₦26.37 billion. This is the budgeted amount from the Total Expenditure by Administrative Classification table.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
```

## lookup-03 (template) ok (7.4s)

**Q:** How much was approved for the Ministry of Youth and Sports Development in the 2025 budget?

```
The State Government approved ₦4.02 billion for the Ministry of Youth and Sports Development in the 2025 budget (total). This is the ministry total from the Total Expenditure by Administrative Classification table.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12
```

## lookup-04 (informal) ok (12.1s)

**Q:** how much for Ministry of Information in 2026 budget?

```
The 2026 approved budget (total) for the Ministry of Information including its agencies is ₦2.48 billion. The headquarters only is ₦1.58 billion.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
```

## lookup-05 (template) ok (10.6s)

**Q:** How much was approved for the Office of Auditor General in the 2024 budget?

```
₦425.34 million was approved (total) for the Office of Auditor General in the 2024 budget. Actual 2024 spending for the office was ₦309.97 million.

📄 *Sources:* Sokoto State Government 2024 Approved Budget, p. 41; Sokoto State FY 2026 Budget, p. 16
```

## lookup-06 (code_switched) ok (9.4s)

**Q:** How much aka approve wa Office of Head of Service a budget na 2024?

```
A teburin jimillar kashe kuɗi ta ma'aikata, an amince da jimilla ₦4.65 biliyan ga Office of Head of Service a kasafin 2024, wannan kasafin da aka amincewa ne ba kuɗin da aka kashe ba.

📄 *Madogara:* Sokoto State Government 2024 Approved Budget, shafi 7, 41
```

## lookup-07 (code_switched) WRONG: not found, though the data has it (3.7s)

**Q:** A 2026 budget, how much aka approve wa Ministry for Local Government and Chieftancy?

```
Kasafin bai buga wata hukuma mai suna "Ministry for Local Government and Chieftaincy Affairs" daidai ba. Ko kana nufin ɗaya daga cikin waɗannan: Ministry for Local Government and Chieftancy?
```

## lookup-08 (code_switched) ok (8.4s)

**Q:** Nawa aka approve wa Ministry of Livestocks and Fisheries Development a 2026 budget?

```
An ware ₦13.60 biliyan ga Ministry of Livestocks and Fisheries Development a kasafin 2026 da aka amince da shi (jimilla). Wannan adadi ne da aka tsara a kasafi, ba kuɗin da aka kashe ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
```

## lookup-09 (followup) ok (9.1s)

**Q:** How much was approved for it in the 2025 budget?

```
The 2025 approved budget (total) for the Ministry for Special Duties was ₦423.00 million, which is allocated money, not spent money. By September 2025 only (Q1–Q3 2025), the ministry had spent ₦59.83 million (18.5% of the revised budget).

• 2025 approved budget (personnel): ₦8.00 million
• 2025 approved budget (overhead): ₦155.00 million
• 2025 approved budget (capital): ₦260.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 12, 14, 15; Sokoto State Budget Implementation Report Q3 2025, p. 16
```

## lookup-10 (code_switched) ok (10.4s)

**Q:** Ministry of Science and Technology ta samu nawa for 2025 budget?

```
_Na yi amfani da kasafin 2025 da aka amince da shi._

Ma'aikatar Kimiyya da Fasaha ta samu ₦6.82 biliyan a kasafin 2025 da aka amince da shi (jimilla). Wannan adadin kasafin da aka ware ne, ba kuɗin da aka kashe ba.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-11 (hausa) ok (12.8s)

**Q:** Nawa aka amince wa Ministry for Religious Affairs a kasafin kudin 2026?

```
An amince wa Ministry for Religious Affairs jimillar ₦18.05 biliyan a kasafin kuɗi na 2026 da aka amince. Wannan adadi daga teburin Jimillar Kashewa ta rukunin gudanarwa ne, kuma kasafi ne da aka amince ba kuɍin da aka kashe ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16
```

## lookup-12 (template) ok (12.3s)

**Q:** How much was approved for the Ministry of Works in the 2026 budget?

```
The 2026 approved budget (total) for the Ministry of Works is ₦59.17 billion.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
```

## lookup-13 (code_switched) ok (13.2s)

**Q:** Nawa ne approved amount na Ministry of Solid Minerals and Natural Resources a 2026 budget?

```
Jimillar kasafin 2026 da aka amince wa Ministry of Solid Minerals and Natural Resources ita ce ₦969.94 miliyan. Wannan adadin kasafin da aka amince ne (allocated), daga teburin jimillar kashe kuɗi. Manyan ayyuka kaɗai a 2026 (approved budget) sun kai ₦610.10 miliyan.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## lookup-14 (template) ok (9.7s)

**Q:** How much was approved for the Ministry for Higher Education in the 2026 budget?

```
The Ministry for Higher Education was approved ₦33.99 billion for 2026 (total allocated, from the Total Expenditure by Administrative Classification table).

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18
```

## lookup-15 (code_switched) ok (11.0s)

**Q:** How much aka approve wa Civil Service Commission a 2026 budget?

```
An amince da ₦403.14 miliyan ga Civil Service Commission a kasafin 2026 (jimilla). Wannan adadi daga teburin jimillar kashe kuɗi ta ma'aikata ne.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16
```

## lookup-16 (code_switched) ok (11.2s)

**Q:** How much aka approve for Ministry of Agriculture & Natural Resource a 2025 budget?

```
Ma'aikatar Agriculture & Natural Resource ta samu jimilla ₦19.09 biliyan a kasafin 2025 da aka approve. Wannan kasafi ne da aka tsara, ba kuɗi da aka kashe ba.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-17 (typo) WRONG: WRONG AGENCY 014800100100 (7.3s)

**Q:** How much was aproved for the Sokoto State Independant Electoral Commission in the 2025 budget?

```
₦529.14 million was approved for the Sokoto State Independent Electoral Commission in the 2025 approved budget.

• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2025 Approved Budget: ₦529.14 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## lookup-18 (template) ok (10.2s)

**Q:** How much was approved for the Law and Justice in the 2025 budget?

```
The State Government approved ₦10.74 billion for Law and Justice as total expenditure in the 2025 budget, from the Total Expenditure by Administrative Classification table.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12
```

## lookup-19 (followup) ok (8.1s)

**Q:** How much was approved for it in the 2026 budget?

```
From the Total Expenditure by Administrative Classification table, the 2026 approved budget (total) for the Office of the SSG is ₦40.40 billion.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
```

## split-01 (code_switched) ok (3.3s)

**Q:** Menene personnel, overhead da capital allocations na Ministry for Special Duties for 2026?

```
*Ministry for Special Duties* (code 016700000000):
• Albashi: kasafin da aka amince ₦12.00 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦195.50 miliyan
• Manyan ayyuka: kasafin da aka amince ₦622.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 19, 22, 25
```

## split-02 (informal) ok (3.2s)

**Q:** personnel, overhead and capital for Ministry of Commerce and Industry in 2026 — how much?

```
*Ministry of Commerce and Industry* (code 022200000000):
• Personnel (salaries): approved budget ₦193.00 million
• Overhead (running costs): approved budget ₦2.16 billion
• Capital: approved budget ₦4.21 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 25
```

## split-03 (followup) ok (3.3s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
*Ministry of Information* (code 012300000000):
• Personnel (salaries): approved budget ₦399.95 million
• Overhead (running costs): approved budget ₦617.34 million
• Capital: approved budget ₦1.46 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-04 (hausa) ok (11.3s)

**Q:** Menene kasafin personnel, overhead da capital na Department for Security Matters a 2025?

```
Kasafin 2025 da aka amince wa na Department for Security Matters: personnel ₦51.37 miliyan, overhead ₦10.04 biliyan, da capital ₦481.00 miliyan. Waɗannan kuɗaɗen da aka ware ne (budgeted), ba kuɗaɗen da aka kashe ba.

• Department for Security Matters (hukuma ɗaya, albashi, code 017000100200) [Personnel Expenditure by Administrative Classification], 2025 Approved Budget: ₦51.37 miliyan
• Department for Security Matters (hukuma ɗaya, kuɗin gudanarwa, code 017000100200), 2025 Approved Budget: ₦10.04 biliyan
• Department for Security Matters (hukuma ɗaya, manyan ayyuka, code 017000100200) [Capital Expenditure by Administrative Classification], 2025 Approved Budget: ₦481.00 miliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 13, 14, 16
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## split-05 (typo) ok (4.1s)

**Q:** What are teh personel, overhead and capitel allocations of the Tenancy Control and Safety of Person Agency in 2025?

```
*Tenancy Control and Safety of Person Agency* (code 032600700500):
• Personnel (salaries): approved budget ₦18.00 million
• Overhead (running costs): approved budget ₦61.00 million
• Capital: approved budget ₦72.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-06 (template) ok (3.0s)

**Q:** What are the personnel, overhead and capital allocations of the Pilgrims Welfare Agency in 2025?

```
*Pilgrims Welfare Agency* (code 011103700100):
• Personnel (salaries): approved budget ₦35.52 million
• Overhead (running costs): approved budget ₦3.97 billion
• Capital: approved budget ₦1.10 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 14, 15
```

## split-07 (informal) ok (3.4s)

**Q:** How much did Ministry of Transport get for personnel, overhead and capital in 2026?

```
*Ministry of Transport* (code 022900000000):
• Personnel (salaries): approved budget ₦100.00 million
• Overhead (running costs): approved budget ₦3.10 billion
• Capital: approved budget ₦47.67 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-08 (template) ok (7.7s)

**Q:** What are the personnel, overhead and capital allocations of the JUDICIAL SERVICE COMMISSION in 2026?

```
*JUDICIAL SERVICE COMMISSION* (code 031801100100):
• Personnel (salaries): approved budget ₦118.01 million
• Overhead (running costs): approved budget ₦128.50 million
• Capital: approved budget ₦310.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 24, 26
```

## split-09 (template) ok (4.7s)

**Q:** What are the personnel, overhead and capital allocations of the Rima Radio in 2026?

```
*Rima Radio* (code 012300400100):
• Personnel (salaries): approved budget ₦142.97 million
• Overhead (running costs): approved budget ₦32.78 million
• Capital: approved budget ₦275.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 22, 25
```

## split-10 (template) ok (4.1s)

**Q:** What are the personnel, overhead and capital allocations of the Ministry of Humanitarian Affairs & Social Welfare in 2025?

```
*Ministry of Humanitarian Affairs & Social Welfare* (code 055600100100):
• Personnel (salaries): approved budget ₦94.11 million
• Overhead (running costs): approved budget ₦2.19 billion
• Capital: approved budget ₦4.80 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 14, 15, 17
```

## split-11 (followup) ok (7.7s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
The Livestock Development Programme's 2025 approved allocations were ₦8.57 million for personnel (salaries), ₦20.30 million for overhead (running costs), and ₦272.00 million for capital. These are budgeted amounts, not actual spending.

• Livestock Development Programme (one agency or unit, personnel (salaries), code 026800200100) [Personnel Expenditure by Administrative Classification], 2025 Approved Budget: ₦8.57 million
• Livestock Development Programme (one agency or unit, overhead (running costs), code 026800200100) [Other Non-Debt Recurrent Expenditure by Fund Source], 2025 Approved Budget: ₦20.30 million
• Livestock Development Programme (one agency or unit, capital, code 026800200100) [Capital Expenditure by Administrative Classification], 2025 Approved Budget: ₦272.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
_Reply *show working* to see the rows and arithmetic._
```

## split-12 (typo) ok (5.0s)

**Q:** What are teh personnel, overhead and captial allocations of the State Emergency Managment Agency (SEMA) in 2025?

```
*State Emergency Management Agency (SEMA)* (code 011100800100):
• Personnel (salaries): approved budget ₦3.60 million
• Overhead (running costs): approved budget ₦125.00 million
• Capital: approved budget ₦300.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12, 14, 15
```

## split-13 (template) ok (12.5s)

**Q:** What are the personnel, overhead and capital allocations of the Ministry of Budget and Economic Planning in 2025?

```
*Ministry of Budget and Economic Planning* (code 023800000000):
• Personnel (salaries): approved budget ₦146.66 million
• Overhead (running costs): approved budget ₦1.90 billion
• Capital: approved budget ₦1.98 billion
Not in the documents:
• Ministry of Budget and Economic Planning Personnel (salaries) 2025 revised budget: the budget prints no Personnel (salaries) line for it
• Ministry of Budget and Economic Planning Overhead (running costs) 2025 revised budget: the budget prints no Overhead (running costs) line for it
• Ministry of Budget and Economic Planning Capital 2025 revised budget: the budget prints no Capital line for it

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 14, 16
```

## split-14 (code_switched) ok (4.4s)

**Q:** Nawa ne personnel, overhead da capital allocations na Fertilizer and Agricultral Supplies Company for 2025?

```
*Fertilizer and Agricultral Supplies Company* (code 021511000100):
• Albashi: kasafin da aka amince ₦37.51 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦23.50 miliyan
• Manyan ayyuka: kasafin da aka amince ₦98.00 miliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 13, 14, 16
```

## split-15 (followup) ok (3.7s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
*Sokoto State contributory health care mgt agency* (code 052100200100):
• Personnel (salaries): approved budget ₦14.39 million
• Overhead (running costs): approved budget ₦66.50 million
• Capital: approved budget ₦218.50 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21, 24, 27
```

## split-16 (hausa) ok (3.4s)

**Q:** Nawa ne personnel, overhead da capital allocations na Ministry for Higher Education a 2025?

```
*Ministry for Higher Education* (code 056900000000):
• Albashi: kasafin da aka amince ₦6.92 biliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦5.64 biliyan
• Manyan ayyuka: kasafin da aka amince ₦6.60 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 13, 15, 16
```

## split-17 (code_switched) ok (2.7s)

**Q:** Sokoto State Public Service Institute na 2026, how much be personnel, overhead da capital allocation?

```
*Sokoto State Public Service Institute* (code 012500100200):
• Albashi: kasafin da aka amince ₦0.00
• Kuɗin gudanarwa: kasafin da aka amince ₦95.00 miliyan
• Manyan ayyuka: kasafin da aka amince ₦0.00

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 19, 22, 25
```

## split-18 (followup) ok (3.8s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
*Sokoto Road Maintenance Agency* (code 023400400100):
• Personnel (salaries): approved budget ₦43.00 million
• Overhead (running costs): approved budget ₦12.25 million
• Capital: approved budget ₦400.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 14, 16
```

## split-19 (template) ok (3.1s)

**Q:** What are the personnel, overhead and capital allocations of the Ministry of Finance in 2026?

```
*Ministry of Finance* (code 022000000000):
• Personnel (salaries): approved budget ₦2.10 billion
• Overhead (running costs): approved budget ₦8.94 billion
• Capital: approved budget ₦9.47 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 22, 25
```

## spend_quarter-01 (typo) ok (4.9s)

**Q:** How much had the Orthopedic Hospital Wamakko spnet by the end of Q4 2024, agianst its revised budget?

```
*Orthopedic Hospital Wamakko* (code 052104100100):
• Total: revised budget ₦670.43 million; spent so far (Q1–Q4) ₦355.43 million; share of the revised budget spent 53.0% (Kasafi's calculation)

📄 *Sources:* Budget Performance Report Q4 2024, p. 20
```

## spend_quarter-02 (hausa) WRONG: not found, though the data has it (3.8s)

**Q:** Nawa Maryam Abacha W& Child. Hospital ta kashe har zuwa karshen Q4 2024, idan aka duba da revised budget dinta?

```
Kasafin bai buga wata hukuma mai suna "Maryam Abacha Women and Children Hospital" daidai ba. Ko kana nufin ɗaya daga cikin waɗannan: Maryam Abacha W& Child. Hospital?
```

## spend_quarter-03 (code_switched) ok (3.8s)

**Q:** Primary Health Care Development Agency ta spend nawa by end of Q4 2024 against revised budget ɗinta?

```
*Primary Health Care Development Agency* (code 052100300100):
• Jimilla: kasafin da aka sabunta ₦2.55 biliyan; abin da aka kashe zuwa yanzu (Q1–Q4) ₦1.02 biliyan; kason kasafin da aka sabunta da aka kashe 40.0% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 20
```

## spend_quarter-04 (code_switched) WRONG: not found, though the data has it (3.9s)

**Q:** Sultan AbdulRahman College of H/Tech. ta spend nawa by end of Q4 2024 against revised budget dinta?

```
Kasafin bai buga wata hukuma mai suna "Sultan Abdulrahman College of Health Technology" daidai ba. Ko kana nufin ɗaya daga cikin waɗannan: Sultan AbdulRahman College of H/Tech.?
```

## spend_quarter-05 (typo) ok (3.6s)

**Q:** How much had the Department for Resident Comunity and Advocacy spent by teh end of Q2 2026, against its revised budget?

```
*Department for Resident Community and Advocacy* (code 016102100700):
• Total: spent so far (Q1–Q2) ₦62.50 million; revised budget ₦937.00 million; share of the revised budget spent 6.7% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 15
```

## spend_quarter-06 (hausa) ok (3.5s)

**Q:** Ministry of Information ta kashe kudi nawa har zuwa karshen Q3 2025, idan aka kwatanta da revised budget dinta?

```
*Ministry of Information* (code 012300000000):
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q3) ₦1.33 biliyan; kasafin da aka sabunta ₦2.64 biliyan; kason kasafin da aka sabunta da aka kashe 50.4% (lissafin Kasafi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 16
```

## spend_quarter-07 (informal) WRONG: missing ['123,000,000.00'] (4.5s)

**Q:** how much had UNDP spent by end of Q2 2026 vs its revised budget?

```
The 2026 budget expects ₦78.92 billion from Aid And Grants. By the end of June 2026, ₦8.39 billion had been received (10.6%). In 2025, ₦4.67 billion was budgeted (revised) and ₦0.00 received by September.

Main parts:
• Grants: ₦76.42 billion
• Aid: ₦2.50 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 12; Budget Implementation Report Q2 2026, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## spend_quarter-08 (hausa) ok (3.8s)

**Q:** Nawa Pilgrims Welfare Agency ta kashe har zuwa ƙarshen Q4 2024, idan aka kwatanta da revised budget ɗinta?

```
*Pilgrims Welfare Agency* (code 011103700100):
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q4) ₦57.14 miliyan; kasafin da aka sabunta ₦73.72 miliyan; kason kasafin da aka sabunta da aka kashe 77.5% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 16
```

## spend_quarter-09 (followup) ok (3.6s)

**Q:** How much had it spent by the end of Q2 2026, against its revised budget?

```
*Sultan Maccido Institute for Qur'ani & General Studies* (code 051700260100):
• Total: revised budget ₦1.02 billion; spent so far (Q1–Q2) ₦277.12 million; share of the revised budget spent 27.1% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 17
```

## spend_quarter-10 (hausa) ok (3.5s)

**Q:** Nawa Female Education Board ta kashe har zuwa karshen Q2 2026, idan aka kwatanta da revised budget dinta?

```
*Female Education Board* (code 051705700100):
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q2) ₦63.82 miliyan; kasafin da aka sabunta ₦1.16 biliyan; kason kasafin da aka sabunta da aka kashe 5.5% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 17
```

## spend_quarter-11 (code_switched) ok (3.5s)

**Q:** Tenancy Control and Safety of Person Agency ta spend nawa by end of Q3 2025 against revised budget dinta?

```
*Tenancy Control and Safety of Person Agency* (code 032600700500):
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q3) ₦13.59 miliyan; kasafin da aka sabunta ₦151.00 miliyan; kason kasafin da aka sabunta da aka kashe 9.0% (lissafin Kasafi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 18
```

## spend_quarter-12 (informal) ok (3.6s)

**Q:** How much did Board of Internal Revenue spend by end Q4 2024 vs its revised budget?

```
*Board of Internal Revenue* (code 022000800100):
• Total: spent so far (Q1–Q4) ₦0.00; revised budget ₦1.20 billion; share of the revised budget spent 0.0% (Kasafi's calculation)

📄 *Sources:* Budget Performance Report Q4 2024, p. 17
```

## spend_quarter-13 (template) ok (4.3s)

**Q:** How much had the Government House spent by the end of Q2 2026, against its revised budget?

```
*Government House* (code 011100000000):
• Total: revised budget ₦18.53 billion; spent so far (Q1–Q2) ₦3.74 billion; share of the revised budget spent 20.2% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 15
```

## spend_quarter-14 (code_switched) ok (4.1s)

**Q:** SUSTAINABLE DEVELOPMENT GOALS (SDG) ta kashe nawa by the end of Q4 2024, against its revised budget?

```
*SUSTAINABLE DEVELOPMENT GOALS (SDG)* (code 023800600200):
• Jimilla: kasafin da aka sabunta ₦23.00 miliyan; abin da aka kashe zuwa yanzu (Q1–Q4) ₦13.75 miliyan; kason kasafin da aka sabunta da aka kashe 59.8% (lissafin Kasafi)

📄 *Madogara:* Budget Performance Report Q4 2024, shafi 18
```

## spend_quarter-15 (typo) ok (4.3s)

**Q:** How much had the Goverment Printing Press spent by teh end of Q2 2026, against its revised budet?

```
*Government Printing Press* (code 012400900100):
• Total: spent so far (Q1–Q2) ₦13.40 million; revised budget ₦96.90 million; share of the revised budget spent 13.8% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 16
```

## spend_quarter-16 (followup) ok (11.2s)

**Q:** How much had it spent by the end of Q2 2026, against its revised budget?

```
SUBEB had spent ₦418.46 million in Q1–Q2 2026, which was 3.9% of its revised budget. Its 2026 revised budget (total) was ₦10.73 billion.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 56
```

## spend_quarter-17 (template) ok (3.8s)

**Q:** How much had the Works School Sokoto spent by the end of Q3 2025, against its revised budget?

```
*Works School Sokoto* (code 023405400100):
• Total: spent so far (Q1–Q3) ₦7.99 million; revised budget ₦25.40 million; share of the revised budget spent 31.5% (Kasafi's calculation)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## spend_quarter-18 (hausa) ok (4.6s)

**Q:** Nawa State Newspaper Comp.(The PATH) ta kashe har zuwa karshen Q2 2026, idan aka duba da revised budget dinta?

```
*State Newspaper Comp.(The PATH)* (code 012305500100):
• Jimilla: kasafin da aka sabunta ₦299.58 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦57.61 miliyan; kason kasafin da aka sabunta da aka kashe 19.2% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 15
```

## spend_quarter-19 (followup) ok (2.7s)

**Q:** How much had it spent by the end of Q2 2026, against its revised budget?

```
*Agency for Industrial Development* (code 022205400200):
• Total: revised budget ₦129.34 million; spent so far (Q1–Q2) ₦11.20 million; share of the revised budget spent 8.7% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 16
```

## compare-01 (followup) ok (3.4s)

**Q:** How does its approved budget in 2025 compare to 2026?

```
*Ministry of Environment* (code 053500000000):
• Total: 2025 approved budget ₦24.52 billion; 2026 approved budget ₦20.77 billion; change -₦3.75 billion (-15.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-02 (informal) ok (3.8s)

**Q:** compare Ministry of Commerce and Industry's approved budget for 2025 vs 2026?

```
*Ministry of Commerce and Industry* (code 022200000000):
• Total: 2025 approved budget ₦6.06 billion; 2026 approved budget ₦6.56 billion; change +₦503.51 million (+8.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-03 (template) ok (3.4s)

**Q:** Compare the Ministry of Energy and Petroleum Resources's approved budget in 2025 and 2026.

```
*Ministry of Energy and Petroleum Resources* (code 023100000000):
• Total: 2025 approved budget ₦10.30 billion; 2026 approved budget ₦23.33 billion; change +₦13.04 billion (+126.6%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-04 (followup) ok (2.9s)

**Q:** How about compare its approved budget in 2025 and 2026?

```
*Government House* (code 011100000000):
• Total: 2025 approved budget ₦14.03 billion; 2026 approved budget ₦18.53 billion; change +₦4.50 billion (+32.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-05 (informal) ok (3.3s)

**Q:** Ministry of Culture & Tourism approved budget 2025 vs 2026?

```
*Ministry of Culture & Tourism* (code 023600000000):
• Total: 2025 approved budget ₦1.21 billion; 2026 approved budget ₦1.42 billion; change +₦214.73 million (+17.7%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-06 (followup) ok (3.1s)

**Q:** How does its approved budget in 2025 compare to 2026?

```
*Ministry for Home Affairs* (code 012400000000):
• Total: 2025 approved budget ₦2.11 billion; 2026 approved budget ₦6.11 billion; change +₦4.01 billion (+190.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-07 (followup) ok (3.2s)

**Q:** Compare its approved budget in 2025 and 2026?

```
*Ministry of Social Welfare & Community Development* (code 055600000000):
• Total: 2025 approved budget ₦7.08 billion; 2026 approved budget ₦5.11 billion; change -₦1.97 billion (-27.8%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 19
```

## compare-08 (typo) WRONG: not found, though the data has it (3.4s)

**Q:** Compare teh Administration Sector's aproved budjet in 2025 and 2026.

```
The budget doesn't print an agency named exactly "Administration". Do you mean one of these: Administration Sector?
```

## compare-09 (code_switched) ok (3.7s)

**Q:** Kwatanta State Judiciary approved budget na 2025 da na 2026 mana?

```
*State Judiciary* (code 031800000000):
• Jimilla: 2025 kasafin da aka amince ₦6.28 biliyan; 2026 kasafin da aka amince ₦8.17 biliyan; bambanci +₦1.89 biliyan (+30.1%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-10 (typo) ok (13.3s)

**Q:** Compare the Socail Sector's aproved budget in 2025 and 2026.

```
The Social Sector approved budget (total) was ₦175.57 billion in 2025 and ₦278.88 billion in 2026. Both figures are allocated budgets from the Total Expenditure by Administrative Classification tables.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-11 (followup) ok (3.2s)

**Q:** Compare its approved budget in 2025 and 2026.

```
*Ministry for Religious Affairs* (code 017200000000):
• Total: 2025 approved budget ₦11.26 billion; 2026 approved budget ₦18.05 billion; change +₦6.79 billion (+60.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-12 (hausa) ok (3.2s)

**Q:** Kwatanta kasafin kudin Ministry for Higher Education da aka amince da shi a 2025 da 2026.

```
*Ministry for Higher Education* (code 056900000000):
• Jimilla: 2025 kasafin da aka amince ₦19.15 biliyan; 2026 kasafin da aka amince ₦33.99 biliyan; bambanci +₦14.83 biliyan (+77.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-13 (informal) ok (4.2s)

**Q:** Ministry of Works approved budget 2025 vs 2026?

```
*Ministry of Works* (code 023400000000):
• Total: 2025 approved budget ₦59.39 billion; 2026 approved budget ₦59.17 billion; change -₦227.66 million (-0.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-14 (informal) ok (10.3s)

**Q:** Economic Sector approved budget 2025 vs 2026?

```
The Economic Sector approved budget (total) was ₦237.36 billion in 2025. It was ₦316.04 billion in 2026.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-15 (typo) ok (3.6s)

**Q:** Compare teh Ministry of Lands and Housings approved budjet in 2025 and 2026.

```
*Min of Lands and Housing* (code 025300000000):
• Total: 2025 approved budget ₦47.46 billion; 2026 approved budget ₦35.78 billion; change -₦11.69 billion (-24.6%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 17
```

## compare-16 (code_switched) ok (4.0s)

**Q:** Abeg compare mana approved budget na Department of Establishment and Pensions na 2025 da 2026?

```
*Department of Establishment and Pensions* (code 017300000000):
• Jimilla: 2025 kasafin da aka amince ₦16.17 biliyan; 2026 kasafin da aka amince ₦11.84 biliyan; bambanci -₦4.33 biliyan (-26.8%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-17 (typo) ok (3.3s)

**Q:** Comapre the Ministry for Special Duties's aproved budget in 2025 and 2026.

```
*Ministry for Special Duties* (code 016700000000):
• Total: 2025 approved budget ₦423.00 million; 2026 approved budget ₦829.50 million; change +₦406.50 million (+96.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-18 (code_switched) ok (3.1s)

**Q:** Kwatanta Ministry of Finance approved budget na 2025 da 2026.

```
*Ministry of Finance* (code 022000000000):
• Jimilla: 2025 kasafin da aka amince ₦47.75 biliyan; 2026 kasafin da aka amince ₦40.27 biliyan; bambanci -₦7.47 biliyan (-15.7%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## compare-19 (typo) ok (3.1s)

**Q:** Comapre the Office of Head of Servcie's aproved budget in 2025 and 2026.

```
*Office of Head of Service* (code 012500000000):
• Total: 2025 approved budget ₦3.41 billion; 2026 approved budget ₦10.44 billion; change +₦7.03 billion (+206.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## share-01 (template) ok (3.8s)

**Q:** What share of the Sokoto State Independent Electoral Commission's 2026 approved budget is capital?

```
*Sokoto State Independent Electoral Commission* (code 014800000000):
• Capital: approved budget ₦225.71 million; 49.0% of its total (Kasafi's calculation)
• Total: approved budget ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 25
```

## share-02 (code_switched) ok (3.9s)

**Q:** Ministry of Health approved budget na 2026, what share ne capital?

```
*Ministry of Health* (code 052100000000):
• Manyan ayyuka: kasafin da aka amince ₦104.64 biliyan; 84.1% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦124.41 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 27
```

## share-03 (hausa) ok (4.4s)

**Q:** Kashi nawa ne na capital a cikin kasafin 2026 da aka amince wa Ministry for Home Affairs?

```
*Ministry for Home Affairs* (code 012400000000):
• Manyan ayyuka: kasafin da aka amince ₦2.58 biliyan; 42.3% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦6.11 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-04 (followup) ok (5.0s)

**Q:** What share of its 2026 approved budget is capital?

```
*Sokoto Central Market* (code 022205500100):
• Capital: approved budget ₦75.00 million; 42.1% of its total (Kasafi's calculation)
• Total: approved budget ₦177.97 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-05 (code_switched) ok (4.2s)

**Q:** Commodity Board approved budget na 2026, what share ne capital?

```
*Commodity Board* (code 022200200100):
• Manyan ayyuka: kasafin da aka amince ₦650.00 miliyan; 96.4% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦673.97 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## share-06 (code_switched) ok (3.7s)

**Q:** 2026 approved budget na Primary School Staff Pension Board, kashi nawa ne capital?

```
*Primary School Staff Pension Board* (code 011103500200):
• Manyan ayyuka: kasafin da aka amince ₦0.00; 0.0% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦60.34 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 25
```

## share-07 (followup) ok (3.6s)

**Q:** What share of its 2026 approved budget is capital?

```
*State Emergency Management Agency (SEMA)* (code 011100800100):
• Capital: approved budget ₦1.20 billion; 90.6% of its total (Kasafi's calculation)
• Total: approved budget ₦1.32 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 25
```

## share-08 (hausa) ok (4.5s)

**Q:** Cikin kasafin kudin Sokoto State University na 2026 da aka amince da shi, kashi nawa ne na jari (capital)?

```
*Sokoto State University* (code 056900400100):
• Manyan ayyuka: kasafin da aka amince ₦3.50 biliyan; 61.3% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦5.71 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 27
```

## share-09 (informal) ok (4.6s)

**Q:** State Agency for Normadic Education1's 2026 budget — how much of it is capital?

```
*State Agency for Normadic Education* (code 051701100100):
• Capital: approved budget ₦383.42 million; 49.5% of its total (Kasafi's calculation)
• Total: approved budget ₦774.42 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 27
```

## share-10 (typo) ok (5.1s)

**Q:** What shaer of the Ministry of Innovation and Digital Economy's 2026 aproved budget is capital?

```
*Ministry of Innovation and Digital Economy* (code 027900000000):
• Capital: approved budget ₦2.75 billion; 76.6% of its total (Kasafi's calculation)
• Total: approved budget ₦3.59 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-11 (followup) ok (3.5s)

**Q:** What share of its 2026 approved budget is capital?

```
*Water Board* (code 025210200100):
• Capital: approved budget ₦28.30 billion; 91.3% of its total (Kasafi's calculation)
• Total: approved budget ₦30.98 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-12 (followup) ok (3.3s)

**Q:** What share of its 2026 approved budget is capital?

```
*Poultry Development Agency* (code 026800300100):
• Capital: approved budget ₦236.00 million; 78.1% of its total (Kasafi's calculation)
• Total: approved budget ₦302.14 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-13 (followup) ok (4.0s)

**Q:** What share of its 2026 approved budget is capital?

```
*Ministry of Transport* (code 022900000000):
• Capital: approved budget ₦47.67 billion; 93.7% of its total (Kasafi's calculation)
• Total: approved budget ₦50.87 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-14 (informal) ok (4.2s)

**Q:** How much of Specialist Hospital's 2026 budget is capital?

```
*Specialist Hospital* (code 052102600100):
• Capital: approved budget ₦632.30 million; 16.2% of its total (Kasafi's calculation)
• Total: approved budget ₦3.91 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 27
```

## share-15 (template) ok (3.6s)

**Q:** What share of the Sokoto Urban & Reg. Planning Department's 2026 approved budget is capital?

```
*Sokoto Urban & Reg. Planning Department* (code 025300500100):
• Capital: approved budget ₦926.00 million; 83.7% of its total (Kasafi's calculation)
• Total: approved budget ₦1.11 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-16 (code_switched) ok (3.8s)

**Q:** Approved budget na State High Court na 2026, what share is capital?

```
*State High Court* (code 031805100100):
• Manyan ayyuka: kasafin da aka amince ₦2.13 biliyan; 41.0% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦5.21 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 26
```

## share-17 (followup) ok (4.9s)

**Q:** What share of its 2026 approved budget is capital?

```
*Ministry of Science and Technology* (code 022800000000):
• Capital: approved budget ₦9.02 billion; 77.2% of its total (Kasafi's calculation)
• Total: approved budget ₦11.69 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-18 (typo) ok (3.5s)

**Q:** What shre of the Ministry of Livestocks and Fisheries Developmnet's 2026 approved budget is capital?

```
*Ministry of Livestocks and Fisheries Development* (code 026800000000):
• Capital: approved budget ₦12.26 billion; 90.2% of its total (Kasafi's calculation)
• Total: approved budget ₦13.60 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
```

## share-19 (template) ok (4.0s)

**Q:** What share of the Government Printing Press's 2026 approved budget is capital?

```
*Government Printing Press* (code 012400900100):
• Capital: approved budget ₦50.00 million; 51.6% of its total (Kasafi's calculation)
• Total: approved budget ₦96.90 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 25
```

## false_premise-01 (hausa) WRONG: didn't correct a premise the figures contradict (3.6s)

**Q:** Me ya sa approved budget na Ministry of Science and Technology ya ragu daga 2025 zuwa 2026?

```
*Ministry of Science and Technology* (code 022800000000):
• Jimilla: 2025 kasafin da aka amince ₦6.82 biliyan; 2026 kasafin da aka amince ₦11.69 biliyan; bambanci +₦4.87 biliyan (+71.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## false_premise-02 (typo) WRONG: didn't correct a premise the figures contradict (3.3s)

**Q:** Why did the Ministry of Water Resoruces's aproved budget fall from 2025 to 2026?

```
*Ministry of Water Resources* (code 025200000000):
• Total: 2025 approved budget ₦20.32 billion; 2026 approved budget ₦44.99 billion; change +₦24.67 billion (+121.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-03 (code_switched) WRONG: didn't correct a premise the figures contradict (3.8s)

**Q:** Me ya sa State Judiciary approved budget ya fall daga 2025 to 2026?

```
*State Judiciary* (code 031800000000):
• Albashi: 2025 kasafin da aka amince ₦1.23 biliyan; 2026 kasafin da aka amince ₦1.60 biliyan; bambanci +₦368.50 miliyan (+29.9%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦1.92 biliyan; 2026 kasafin da aka amince ₦3.18 biliyan; bambanci +₦1.26 biliyan (+65.8%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦3.13 biliyan; 2026 kasafin da aka amince ₦3.39 biliyan; bambanci +₦262.63 miliyan (+8.4%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦6.28 biliyan; 2026 kasafin da aka amince ₦8.17 biliyan; bambanci +₦1.89 biliyan (+30.1%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12, 13, 15, 16; Sokoto State FY 2026 Budget, shafi 18, 20, 23, 26
```

## false_premise-04 (informal) ok (8.5s)

**Q:** why did Ministry for Special Duties budget drop from 2025 to 2026?

```
The Ministry for Special Duties budget did not drop from 2025 to 2026. Its approved total was ₦423.00 million in 2025 and ₦829.50 million in 2026, an increase of ₦406.50 million (Kasafi's calculation).

• Ministry for Special Duties (ministry total including its agencies, all spending (total), code 016700000000), 2025 Approved Budget: ₦423.00 million
• Ministry for Special Duties (ministry total including its agencies, all spending (total), code 016700000000), 2026 Approved Budget: ₦829.50 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-05 (code_switched) WRONG: didn't correct a premise the figures contradict (3.7s)

**Q:** Why Ministry of Youth and Sports Development approved budget din ya fall daga 2025 to 2026?

```
*Ministry of Youth and Sports Development* (code 051300000000):
• Jimilla: 2025 kasafin da aka amince ₦4.02 biliyan; 2026 kasafin da aka amince ₦17.06 biliyan; bambanci +₦13.03 biliyan (+323.8%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## false_premise-06 (followup) WRONG: didn't correct a premise the figures contradict (3.4s)

**Q:** Why did its approved budget rise from 2025 to 2026?

```
*Ministry of Information* (code 012300000000):
• Personnel (salaries): 2025 approved budget ₦382.95 million; 2026 approved budget ₦399.95 million; change +₦17.00 million (+4.4%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦768.74 million; 2026 approved budget ₦617.34 million; change -₦151.40 million (-19.7%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦1.49 billion; 2026 approved budget ₦1.46 billion; change -₦26.00 million (-1.7%) (Kasafi's calculation)
• Total: 2025 approved budget ₦2.64 billion; 2026 approved budget ₦2.48 billion; change -₦160.40 million (-6.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 12, 14, 16; Sokoto State FY 2026 Budget, p. 16, 19, 22, 25
```

## false_premise-07 (template) WRONG: didn't correct a premise the figures contradict (4.2s)

**Q:** Why did the Sokoto State Independent Electoral Commission's approved budget rise from 2025 to 2026?

```
*Sokoto State Independent Electoral Commission* (code 014800000000):
• Total: 2025 approved budget ₦529.14 million; 2026 approved budget ₦460.48 million; change -₦68.67 million (-13.0%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## false_premise-08 (code_switched) WRONG: didn't correct a premise the figures contradict (4.1s)

**Q:** Me yasa Ministry of Lands and Housing approved budget ya rise daga 2025 to 2026?

```
*Min of Lands and Housing* (code 025300000000):
• Jimilla: 2025 kasafin da aka amince ₦47.46 biliyan; 2026 kasafin da aka amince ₦35.78 biliyan; bambanci -₦11.69 biliyan (-24.6%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 17
```

## false_premise-09 (template) WRONG: didn't correct a premise the figures contradict (3.7s)

**Q:** Why did the Ministry of Solid Minerals and Natural Resources's approved budget fall from 2025 to 2026?

```
*Ministry of Solid Minerals and Natural Resources* (code 023300000000):
• Total: 2025 approved budget ₦479.09 million; 2026 approved budget ₦969.94 million; change +₦490.85 million (+102.5%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-10 (informal) WRONG: didn't correct a premise the figures contradict (3.4s)

**Q:** why did the Fiscal Responsibility Commission's approved budget fall from 2025 to 2026?

```
*Fiscal Responsibility Commission* (code 025000000000):
• Personnel (salaries): 2025 approved budget ₦9.44 million; 2026 approved budget ₦11.44 million; change +₦2.00 million (+21.2%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦35.30 million; 2026 approved budget ₦35.30 million; change ₦0.00 (0.0%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦14.25 million; 2026 approved budget ₦14.25 million; change ₦0.00 (0.0%) (Kasafi's calculation)
• Total: 2025 approved budget ₦58.99 million; 2026 approved budget ₦60.99 million; change +₦2.00 million (+3.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 13, 14, 16; Sokoto State FY 2026 Budget, p. 17, 20, 23, 26
```

## false_premise-11 (followup) ok (9.3s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
The Office of the Auditor General's approved budget did not fall. It rose from ₦542.84 million in 2025 to ₦606.84 million in 2026, a rise of ₦64.00 million (Kasafi's calculation) / (lissafin Kasafi). Budget documents give reasons for changes only as figures, not explanations.

• Office of Auditor General (ministry total including its agencies, all spending (total), code 014000000000), 2025 Approved Budget: ₦542.84 million
• Office of Auditor General (ministry total including its agencies, all spending (total), code 014000000000), 2026 Approved Budget: ₦606.84 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-12 (typo) WRONG: didn't correct a premise the figures contradict (3.6s)

**Q:** Why did teh Ministry for Skils Acquisition and Entrepreneurship Developmet's approved budget rise from 2025 to 2026?

```
*Ministry for Skills Acquisition and Entrepreneurship Development* (code 028900000000):
• Total: 2025 approved budget ₦1.50 billion; 2026 approved budget ₦1.37 billion; change -₦125.00 million (-8.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-13 (typo) WRONG: not found, though the data has it (13.2s)

**Q:** Why did the Administation Sector's aproved budget fall from 2025 to 2026?

```
I can read your question two ways. Which do you mean?
```

## false_premise-14 (typo) WRONG: didn't correct a premise the figures contradict (13.2s)

**Q:** Why did teh Ministry of Finance's approved budjet rise from 2025 to 2026?

```
The Ministry of Finance total allocated (approved budget) was ₦47.75 billion in 2025 and ₦40.27 billion in 2026, so the evidence shows a fall not a rise. Spending in January–September 2025 was ₦19.12 billion (January–September 2025 only). The evidence gives no reason for the change.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-15 (code_switched) WRONG: didn't correct a premise the figures contradict (4.3s)

**Q:** Me ya sa Office of Head of Service approved budget ya fall daga 2025 to 2026?

```
*Office of Head of Service* (code 012500000000):
• Albashi: 2025 kasafin da aka amince ₦975.99 miliyan; 2026 kasafin da aka amince ₦1.31 biliyan; bambanci +₦333.08 miliyan (+34.1%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦875.00 miliyan; 2026 kasafin da aka amince ₦1.46 biliyan; bambanci +₦580.80 miliyan (+66.4%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦1.55 biliyan; 2026 kasafin da aka amince ₦7.67 biliyan; bambanci +₦6.12 biliyan (+393.3%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦3.41 biliyan; 2026 kasafin da aka amince ₦10.44 biliyan; bambanci +₦7.03 biliyan (+206.4%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 12, 14, 16; Sokoto State FY 2026 Budget, shafi 16, 19, 22, 25
```

## false_premise-16 (followup) WRONG: didn't correct a premise the figures contradict (3.6s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
*Ministry of Commerce and Industry* (code 022200000000):
• Personnel (salaries): 2025 approved budget ₦122.77 million; 2026 approved budget ₦193.00 million; change +₦70.23 million (+57.2%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦1.04 billion; 2026 approved budget ₦2.16 billion; change +₦1.12 billion (+107.5%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦4.89 billion; 2026 approved budget ₦4.21 billion; change -₦686.27 million (-14.0%) (Kasafi's calculation)
• Total: 2025 approved budget ₦6.06 billion; 2026 approved budget ₦6.56 billion; change +₦503.51 million (+8.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 13, 14, 16; Sokoto State FY 2026 Budget, p. 17, 20, 23, 25
```

## false_premise-17 (hausa) WRONG: missing ['24,523,772,920.28', '20,769,471,936.00'] (14.4s)

**Q:** Me ya sa approved budget na Ministry of Environment ya karu daga 2025 zuwa 2026?

```
• Bambanci (2026 Approved Budget vs 2025 Approved Budget): -₦4.30 biliyan (-18.6%) (lissafin Kasafi)

• Ministry of Environment (ma'aikata tare da hukumominta, manyan ayyuka, code 053500000000), 2025 Approved Budget: ₦23.08 biliyan
• Ministry of Environment (ma'aikata tare da hukumominta, manyan ayyuka, code 053500000000), 2026 Approved Budget: ₦18.77 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 27
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## false_premise-18 (hausa) WRONG: didn't correct a premise the figures contradict (3.5s)

**Q:** Me ya sa approved budget na Ministry of Energy and Petroleum Resources ya ragu daga 2025 zuwa 2026?

```
*Ministry of Energy and Petroleum Resources* (code 023100000000):
• Jimilla: 2025 kasafin da aka amince ₦10.30 biliyan; 2026 kasafin da aka amince ₦23.33 biliyan; bambanci +₦13.04 biliyan (+126.6%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 17
```

## false_premise-19 (typo) WRONG: WRONG AGENCY 014700100100 (14.3s)

**Q:** Why did teh Civil Service Commision's aproved budget fall from 2025 to 2026?

```
The Civil Service Commission's approved budget did not fall. It was ₦254.99 million in 2025 and ₦403.14 million in 2026. The 2026 figure is higher than the 2025 figure.

• Civil Service Commission (one agency or unit, all spending (total), code 014700100100), 2025 Approved Budget: ₦254.99 million
• Civil Service Commission (one agency or unit, all spending (total), code 014700100100), 2026 Approved Budget: ₦403.14 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## not_in_data-01 (hausa) ok (4.1s)

**Q:** Nawa Sokoto State University ta kashe a Q4 2026?

```
Ba a cikin takardun ba:
• Sokoto State University 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Sokoto State University 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-02 (template) ok (3.4s)

**Q:** How much did the College of Agriculture Wurno spend in Q1 2027?

```
Not in the documents:
• College of Agriculture Wurno 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• College of Agriculture Wurno 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-03 (hausa) ok (5.1s)

**Q:** Nawa Umaru Ali Shinkafi Polytechnic Sokoto ta kashe a Q4 2026?

```
Ba a cikin takardun ba:
• Umaru Ali Shinkafi Polytechnic Sokoto 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Umaru Ali Shinkafi Polytechnic Sokoto 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Umaru Ali Shinkafi Polytechnic Sokoto 2026 kason kasafin da aka sabunta da aka kashe: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-04 (typo) ok (15.9s)

**Q:** How mucch is the Ministry for Basic Educaton's approved budget for 2028?

```
⚠️ I couldn't get the document that fits best (Sokoto State Government 2028 Approved Budget). The answer below is from other documents I have, not from that one.

_Assumption: 2028 budget year is in the future relative to today (2026-10-30) and is not in the catalog; the latest available budget is 2026._

There is no 2028 approved budget in the evidence, only a 2028 out-year estimate published in the 2026 budget. The Ministry for Basic Education's 2028 out-year estimate (total) is ₦570.00 million.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 76
```

## not_in_data-05 (typo) ok (4.2s)

**Q:** How much did the Sokoto State Housing Cooperaton spned in Q1 2027?

```
Not in the documents:
• Sokoto State Housing Cooperation 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Sokoto State Housing Cooperation 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-06 (hausa) ok (3.6s)

**Q:** Nawa Ministry for Women Affairs ta kashe a Q4 2026?

```
Ba a cikin takardun ba:
• Ministry for Women Affairs 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Ministry for Women Affairs 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Ministry for Women Affairs 2026 kason kasafin da aka sabunta da aka kashe: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-07 (code_switched) ok (3.8s)

**Q:** Nawa House of Assembly Service Commission ta spend a Q1 2027?

```
Ba a cikin takardun ba:
• House of Assembly Service Commission 2027 abin da aka kashe zuwa yanzu (Q1–Q1): babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• House of Assembly Service Commission 2027 abin da aka kashe a Q1: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
• House of Assembly Service Commission 2027 kason kasafin da aka sabunta da aka kashe: babu rahoton aiwatarwa na 2027 a ɗakin karatu tukuna; mafi sabo shi ne Q2 2026
```

## not_in_data-08 (typo) ok (3.5s)

**Q:** How much did teh State Enviromental Protection Agency spend in Q1 2027?

```
Not in the documents:
• State Environmental Protection Agency 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• State Environmental Protection Agency 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• State Environmental Protection Agency 2027 share of the revised budget spent: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-09 (informal) ok (3.4s)

**Q:** how much did Sokoto State Scholarship and Students Matters spend in Q4 2026?

```
Not in the documents:
• Sokoto State Scholarship and Students Matters 2026 spent in Q4: the latest implementation report is Q2 2026
• Sokoto State Scholarship and Students Matters 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
• Sokoto State Scholarship and Students Matters 2026 share of the revised budget spent: the latest implementation report is Q2 2026
```

## not_in_data-10 (typo) ok (8.1s)

**Q:** How muhc is the Fiscal Responsibilty Commission's approved budget for 2028?

```
The 2026 budget prints a 2028 figure of ₦58.99 million for the Fiscal Responsibility Commission. This is the 2028 Out-Year Estimate, not a 2028 approved budget.

• Fiscal Responsibility Commission (one agency or unit, all spending (total), code 025000100100), 2028 Out-Year Estimate: ₦58.99 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## not_in_data-11 (informal) ok (3.6s)

**Q:** What'd Sokoto Engineering Construction Company spend in Q4 2026?

```
Not in the documents:
• Sokoto Engineering Construction Company 2026 spent in Q4: the latest implementation report is Q2 2026
• Sokoto Engineering Construction Company 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
```

## not_in_data-12 (code_switched) ok (4.2s)

**Q:** Nawa Rural Water and Sanitation Agency ta spend a Q4 2026?

```
Ba a cikin takardun ba:
• Rural Water and Sanitation Agency 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Rural Water and Sanitation Agency 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Rural Water and Sanitation Agency 2026 kason kasafin da aka sabunta da aka kashe: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-13 (informal) ok (5.2s)

**Q:** how much did State Agency for Normadic Education1 spend in Q1 2027?

```
Not in the documents:
• State Agency for Normadic Education1 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• State Agency for Normadic Education1 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• State Agency for Normadic Education1 2027 share of the revised budget spent: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-14 (followup) ok (4.1s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Infectious Diseases Hospital Amanawa 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Infectious Diseases Hospital Amanawa 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-15 (typo) ok (8.9s)

**Q:** How muhc is the Departmant for IDPs Matters's aproved budget for 2028?

```
The 2026 budget prints ₦5.58 billion for the Department for IDPs Matters in the 2028 column. That 2028 figure is an out-year estimate, not an approved budget.

• Department for IDPs Matters (one agency or unit, all spending (total), code 016102100800), 2028 Out-Year Estimate: ₦5.58 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## not_in_data-16 (typo) ok (4.5s)

**Q:** How mcuh did teh ZAKAT and Endowment Agency (WAQF) spend in Q4 2026?

```
Not in the documents:
• ZAKAT and Endowment Agency (WAQF) 2026 spent in Q4: the latest implementation report is Q2 2026
```

## not_in_data-17 (followup) ok (8.5s)

**Q:** How much did it spend in Q4 2026?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• AFFORESTATION PROGRAMME (one agency or unit, all spending (total), code 021510900100, Total Expenditure by Administrative Classification), 2026 Q2 Performance: ₦6.07 million [1]
• AFFORESTATION PROGRAMME (one agency or unit, all spending (total), code 021510900100, Total Expenditure by Administrative Classification), 2026 Q1 Performance: ₦5.82 million [2]

📄 *Sources:* Budget Implementation Report Q2 2026, p. 16; Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## not_in_data-18 (template) ok (13.9s)

**Q:** How much is the Waziri Junaidu History and Culture Bureau's approved budget for 2028?

```
⚠️ I couldn't get the document that fits best (Sokoto State 2028 Approved Budget). The answer below is from other documents I have, not from that one.

The Waziri Junaidu History and Culture Bureau has a 2028 figure (total) of ₦112.71 million.

• 2028 out-year estimate (total): ₦112.71 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
```

## not_in_data-19 (code_switched) ok (4.4s)

**Q:** Nawa Sokoto College of Legal & Islamic St. ta spend a Q4 2026?

```
Ba a cikin takardun ba:
• Sokoto College of Legal & Islamic St. 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Sokoto College of Legal & Islamic St. 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Sokoto College of Legal & Islamic St. 2026 kason kasafin da aka sabunta da aka kashe: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## rank_lga-01 (followup) ok (4.9s)

**Q:** Which 3 LGAs there have the most IDPs?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-02 (typo) ok (4.8s)

**Q:** Which 10 LGAs in Sokoto hvae the msot IDPs?

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

## rank_lga-03 (hausa) ok (10.3s)

**Q:** Wadannene LGAs 5 a Sokoto da ke da IDPs mafi yawa?

```
📊 Alƙaluma mafi sabo: *181,526 IDPs* – internally displaced persons (DTM baseline, all displacement reasons), Sokoto State (IOM Displacement Tracking Matrix, Round 18, reporting date 2025-10-31).

Daga kowace majiya:
• IOM Displacement Tracking Matrix: 181,526 IDPs – internally displaced persons (DTM baseline, all displacement reasons), Sokoto State; Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 40,729 IDPs – in Sabon Birni, the most of its 22 LGAs (then Tangaza 19,151; Tambuwal 17,143; Tureta 15,068; Shagari 14,850); Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 88,562 IDPs – the round before, Sokoto State; Round 17, reporting date 2025-05-31 (IOM DTM API (Baseline))

Ban samu ba: Sokoto State Bureau of Statistics, JIPS, DRC, REACH, UNHCR Nigeria Forcibly Displaced Populations Dashboard, UN OCHA Nigeria.

📄 *Madogara:* IOM DTM API (Baseline)
```

## lookup_lga-01 (typo) ok (5.2s)

**Q:** How mnay IDPs are thre in Tangaza LGA?

```
IOM DTM counts *19,151* IDPs in Tangaza (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (typo) ok (4.8s)

**Q:** How mnay IDPs are thre in Sokoto North LGA?

```
IOM DTM counts *2,274* IDPs in Sokoto North (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-03 (hausa) ok (5.5s)

**Q:** IDPs nawa ne a Tureta LGA?

```
IOM DTM ta ƙidaya *15,068* 'yan gudun hijira a Tureta (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-04 (code_switched) ok (4.5s)

**Q:** How many IDPs ne a Shagari LGA?

```
IOM DTM ta ƙidaya *14,850* 'yan gudun hijira a Shagari (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-05 (template) ok (5.4s)

**Q:** How many IDPs are there in Kware LGA?

```
IOM DTM counts *1,039* IDPs in Kware (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-06 (code_switched) ok (5.2s)

**Q:** How many IDPs ne a Tambuwal LGA?

```
IOM DTM ta ƙidaya *17,143* 'yan gudun hijira a Tambuwal (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-07 (informal) ok (5.1s)

**Q:** how many IDPs in Bodinga LGA?

```
IOM DTM counts *1,990* IDPs in Bodinga (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-08 (typo) ok (5.6s)

**Q:** How mnay IDPs are thre in Kebbe LGA?

```
IOM DTM counts *4,252* IDPs in Kebbe (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-09 (typo) ok (4.7s)

**Q:** How mnay IDPs aer there in Illela LGA?

```
IOM DTM counts *8,953* IDPs in Illela (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-10 (hausa) ok (4.3s)

**Q:** IDPs nawa ne suke a Wamako LGA?

```
IOM DTM ta ƙidaya *4,026* 'yan gudun hijira a Wamakko (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-11 (typo) ok (4.2s)

**Q:** How mnay IDPs aer there in Wurno LGA?

```
IOM DTM counts *2,128* IDPs in Wurno (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-12 (code_switched) ok (5.4s)

**Q:** How many IDPs ne suke a Gada LGA?

```
IOM DTM ta ƙidaya *1,014* 'yan gudun hijira a Gada (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-13 (code_switched) ok (4.4s)

**Q:** How many IDPs ne suke a Silame LGA?

```
IOM DTM ta ƙidaya *3,386* 'yan gudun hijira a Silame (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-14 (informal) ok (5.0s)

**Q:** how many IDPs in Binji LGA?

```
IOM DTM counts *619* IDPs in Binji (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-15 (code_switched) ok (5.1s)

**Q:** IDPs nawa are there in Isa LGA?

```
IOM DTM ta ƙidaya *14,047* 'yan gudun hijira a Isa (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-16 (informal) ok (4.6s)

**Q:** IDP count for Dange-Shuni LGA?

```
IOM DTM counts *4,615* IDPs in Dange Shuni (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-17 (template) ok (4.5s)

**Q:** How many IDPs are there in Goronyo LGA?

```
IOM DTM counts *1,926* IDPs in Goronyo (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-18 (typo) ok (6.5s)

**Q:** Hoe many IDPs are ther in Sabon Birni LGA?

```
IOM DTM counts *40,729* IDPs in Sabon Birni (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-19 (typo) ok (5.4s)

**Q:** How mnay IDPs are thre in Gwadabawa LGA?

```
IOM DTM counts *8,406* IDPs in Gwadabawa (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## trend-01 (typo) ok (4.5s)

**Q:** How has teh number of IDPs in Sokoto Sate changed over the last DTM rounde?

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
