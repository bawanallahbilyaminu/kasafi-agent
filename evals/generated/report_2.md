# Generated coverage run

42 cases: wrong 2 | median 5.3s

| family | wrong | of |
|---|---|---|
| compare | 0 | 5 |
| false_premise | 0 | 5 |
| lookup | 0 | 5 |
| lookup_lga | 0 | 5 |
| not_in_data | 0 | 5 |
| rank_lga | 0 | 1 |
| share | 1 | 5 |
| spend_quarter | 1 | 5 |
| split | 0 | 5 |
| trend | 0 | 1 |

| form | wrong | of |
|---|---|---|
| code_switched | 0 | 12 |
| followup | 0 | 6 |
| hausa | 0 | 5 |
| informal | 1 | 3 |
| template | 1 | 11 |
| typo | 0 | 5 |

## lookup-01 (hausa) ok (15.8s)

**Q:** Nawa aka amince wa Ministry of Education a kasafin kudin 2026?

```
An amince wa Ministry of Education jimilla ₦68.95 biliyan a kasafin kudin 2026 (kudin da aka amince, ba kudin da aka kashe ba).

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
```

## lookup-02 (typo) ok (10.1s)

**Q:** How mch was aproved for the Ministry for Higher Education in the 2026 budget?

```
The 2026 approved budget (total) for the Ministry for Higher Education is ₦33.99 billion. By Q2 2026, ₦5.15 billion had been spent (January–June 2026 only).

• 2026 Q1–Q2 spent (total, January–June 2026 only, 15.3% of the revised budget): ₦5.15 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18; Budget Implementation Report Q2 2026, p. 17
```

## lookup-03 (template) ok (13.0s)

**Q:** How much was approved for the Ministry of Information in the 2026 budget?

```
The State Government approved ₦2.48 billion for the Ministry of Information in the 2026 budget (total). This figure is allocated (budgeted), not spent.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
```

## lookup-04 (informal) ok (8.4s)

**Q:** How much did Sokoto State House of Assembly get in the 2026 budget?

```
Sokoto State House of Assembly was allocated ₦12.26 billion as its 2026 approved budget (total). This is from the Total Expenditure by Administrative Classification table.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
```

## lookup-05 (template) ok (12.8s)

**Q:** How much was approved for the Economic Sector in the 2026 budget?

```
The 2026 approved budget (total) for the Economic Sector is ₦316.04 billion. This is the allocated amount from the Total Expenditure by Administrative Classification table, not actual spending.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
```

## split-01 (code_switched) ok (4.2s)

**Q:** Nawa ne personnel, overhead da capital allocations na Department for Rural Roads in 2026?

```
*Department for Rural Roads* (code 023405700100):
• Albashi: kasafin da aka amince ₦28.59 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦133.95 miliyan
• Manyan ayyuka: kasafin da aka amince ₦15.47 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 20, 23, 26
```

## split-02 (code_switched) ok (3.3s)

**Q:** Sokoto State Independent Electoral Commission ta samu nawa for personnel, overhead da capital a 2026?

```
*Sokoto State Independent Electoral Commission* (code 014800000000):
• Albashi: kasafin da aka amince ₦128.76 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦106.00 miliyan
• Manyan ayyuka: kasafin da aka amince ₦225.71 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 19, 22, 25
```

## split-03 (code_switched) ok (4.4s)

**Q:** Personnel, overhead da capital allocation na Female Education Board a 2026 din nawa ne?

```
*Female Education Board* (code 051705700100):
• Albashi: kasafin da aka amince ₦47.45 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦462.05 miliyan
• Manyan ayyuka: kasafin da aka amince ₦650.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 21, 24, 27
```

## split-04 (followup) ok (3.7s)

**Q:** What are its personnel, overhead and capital allocations in 2026?

```
*Ministry of Water Resources* (code 025200000000):
• Personnel (salaries): approved budget ₦1.03 billion
• Overhead (running costs): approved budget ₦3.11 billion
• Capital: approved budget ₦40.86 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-05 (code_switched) ok (3.9s)

**Q:** Sokoto Urban & Reg. Planning Department a 2026, menene personnel, overhead and capital allocations dinsu?

```
*Sokoto Urban & Reg. Planning Department* (code 025300500100):
• Albashi: kasafin da aka amince ₦79.94 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦100.50 miliyan
• Manyan ayyuka: kasafin da aka amince ₦926.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 20, 23, 26
```

## spend_quarter-01 (hausa) ok (4.2s)

**Q:** Nawa Commodity Board ta kashe har zuwa karshen Q2 2026, idan aka kwatanta da revised budget dinta?

```
*Commodity Board* (code 022200200100):
• Jimilla: kasafin da aka sabunta ₦673.97 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦4.97 miliyan; kason kasafin da aka sabunta da aka kashe 0.7% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 16
```

## spend_quarter-02 (template) ok (13.2s)

**Q:** How much had the SUSTAINABLE DEVELOPMENT GOALS (SDG) spent by the end of Q2 2026, against its revised budget?

```
The SUSTAINABLE DEVELOPMENT GOALS (SDG) had a 2026 revised budget of ₦42.00 million. By the end of Q2 2026 it had spent ₦1.00 million. That is 2.4% spent (Kasafi's calculation).

• SUSTAINABLE DEVELOPMENT GOALS (SDG) (one agency or unit, all spending (total), code 023800600200) [Total Expenditure by Administrative Classification], 2026 Revised Budget: ₦42.00 million
• SUSTAINABLE DEVELOPMENT GOALS (SDG) (one agency or unit, all spending (total), code 023800600200) [Total Expenditure by Administrative Classification], 2026 Performance Year to Date (Q1-Q2): ₦1.00 million

📄 *Sources:* Budget Implementation Report Q2 2026, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## spend_quarter-03 (code_switched) ok (11.8s)

**Q:** Ministry of Budget and Economic Planning ta kashe nawa by the end of Q2 2026 against revised budget dinta?

```
Ma'aikatar ta kashe ₦541.38 miliyan a Q1–Q2 2026 (10.2% na kasafin da aka sabunta). Kasafin da aka sabunta (jimilla) ₦5.32 biliyan ne.

• 2026 Q2 kadai (jimilla): ₦435.83 miliyan

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 17
```

## spend_quarter-04 (template) WRONG: missing ['4,859,011.52', '81,758,005.00'] (13.1s)

**Q:** How much had the Bureau for Public Procurement and Price Intelligence spent by the end of Q2 2026, against its revised budget?

```
The Bureau's 2026 revised capital budget was ₦20.00 million, with Q1–Q2 spending of - (0.0% of the revised budget). The evidence shows only this capital component, not the Bureau's total spending.

• 2026 revised budget (capital): ₦20.00 million
• Q1–Q2 2026 spent (capital, Q1–Q2 2026): - (0.0% of the revised budget)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 26
```

## spend_quarter-05 (code_switched) ok (14.2s)

**Q:** Department for Security Matters ta kashe nawa by the end of Q2 2026, against its revised budget?

```
Department for Security Matters ta kashe ₦7.61 biliyan (jimilla, Q1–Q2 2026 kawai). Wannan 20.5% na kasafin da aka sabunta ne. Kasafin da aka sabunta (jimilla) ₦37.15 biliyan ne, shi aka ware, ba abin da aka kashe ba.

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 16
```

## compare-01 (code_switched) ok (3.7s)

**Q:** Compare approved budget na Ministry of Justice a 2025 da 2026 fa?

```
*Ministry of Justice* (code 032600000000):
• Jimilla: 2025 kasafin da aka amince ₦4.46 biliyan; 2026 kasafin da aka amince ₦6.09 biliyan; bambanci +₦1.63 biliyan (+36.5%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-02 (typo) ok (3.7s)

**Q:** Comapre the Ministry of Innovation and Digtal Economy's aproved budget in 2025 and 2026.

```
*Ministry of Innovation and Digital Economy* (code 027900000000):
• Total: 2025 approved budget ₦1.35 billion; 2026 approved budget ₦3.59 billion; change +₦2.24 billion (+166.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-03 (template) ok (3.4s)

**Q:** Compare the Fiscal Responsibility Commission's approved budget in 2025 and 2026.

```
*Fiscal Responsibility Commission* (code 025000000000):
• Total: 2025 approved budget ₦58.99 million; 2026 approved budget ₦60.99 million; change +₦2.00 million (+3.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-04 (followup) ok (4.6s)

**Q:** How did its approved budget compare in 2025 and 2026?

```
*Ministry for Women Affairs* (code 051400000000):
• Total: 2025 approved budget ₦8.44 billion; 2026 approved budget ₦7.24 billion; change -₦1.21 billion (-14.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-05 (code_switched) ok (3.2s)

**Q:** Kwatanta mana Government House approved budget na 2025 and 2026.

```
*Government House* (code 011100000000):
• Jimilla: 2025 kasafin da aka amince ₦14.03 biliyan; 2026 kasafin da aka amince ₦18.53 biliyan; bambanci +₦4.50 biliyan (+32.1%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## share-01 (informal) WRONG: missing ['20.0%'] (9.4s)

**Q:** How much of Sokoto State Rima Televiosn (Rtv)'s 2026 approved budget is capital?

```
Sokoto State Rima Television (RTV)'s capital allocation in the 2026 approved budget is ₦30.00 million. This is the agency's capital budget figure.

• Sokoto State Rima Televiosn (Rtv) (one agency or unit, capital, code 012300300100), 2026 Approved Budget: ₦30.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 25
_Reply *show working* to see the rows and arithmetic._
```

## share-02 (followup) ok (8.4s)

**Q:** What share of its 2026 approved budget is capital?

```
The Poultry Development Agency's 2026 approved capital budget is ₦236.00 million out of its total 2026 approved budget of ₦302.14 million. 78.1% of its 2026 approved budget is capital expenditure (Kasafi's calculation).

• Poultry Development Agency (one agency or unit, capital, code 026800300100) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦236.00 million ↑
• Poultry Development Agency (one agency or unit, all spending (total), code 026800300100) [Total Expenditure by Administrative Classification], 2026 Approved Budget: ₦302.14 million ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
_Reply *show working* to see the rows and arithmetic._
```

## share-03 (hausa) ok (11.4s)

**Q:** Wane kaso na kasafin kudin Commodity Board da aka amince da shi na 2026 na babban aiki ne?

```
Babban aiki shine mafi girman kaso na kasafin Commodity Board da aka amince da shi na 2026. Kasafin babban aiki da aka amince da shi ₦650.00 miliyan ne, daga cikin jimillar kasafin hukumar da aka amince da shi ₦673.97 miliyan. Wannan yayi daidai da 96.4% na kasafin da aka amince da shi (lissafin Kasafi).

• Commodity Board (hukuma ɗaya, manyan ayyuka, code 022200200100) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦650.00 miliyan ↑
• Commodity Board (hukuma ɗaya, duk kashe kuɗi (jimilla), code 022200200100) [Total Expenditure by Administrative Classification], 2026 Approved Budget: ₦673.97 miliyan ↓

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## share-04 (typo) ok (9.1s)

**Q:** What shrae of the Sokoto State SME Developmant Agency's 2026 approved budget is capital?

```
The Agency's 2026 approved capital budget is ₦100.00 million out of its total 2026 approved budget of ₦1.48 billion. This is 6.7% (Kasafi's calculation) of the Agency's 2026 approved budget.

• Sokoto State SME Development Agency (one agency or unit, capital, code 022205100100) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦100.00 million ↑
• Sokoto State SME Development Agency (one agency or unit, all spending (total), code 022205100100) [Total Expenditure by Administrative Classification], 2026 Approved Budget: ₦1.48 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
_Reply *show working* to see the rows and arithmetic._
```

## share-05 (template) ok (10.1s)

**Q:** What share of the Fiscal Responsibility Commission's 2026 approved budget is capital?

```
The Commission's 2026 approved capital budget is ₦14.25 million out of its total 2026 approved budget of ₦60.99 million. That is 23.4% capital (Kasafi's calculation). Both figures are allocated (budgeted), not spent.

• Fiscal Responsibility Commission (one agency or unit, capital, code 025000100100) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦14.25 million ↑
• Fiscal Responsibility Commission (one agency or unit, all spending (total), code 025000100100) [Total Expenditure by Administrative Classification], 2026 Approved Budget: ₦60.99 million ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-01 (informal) ok (4.0s)

**Q:** Why did Ministry for Special Duties's approved budget drop from 2025 to 2026?

```
*Ministry for Special Duties* (code 016700000000):
• Personnel (salaries): 2025 approved budget ₦8.00 million; 2026 approved budget ₦12.00 million; change +₦4.00 million (+50.0%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦155.00 million; 2026 approved budget ₦195.50 million; change +₦40.50 million (+26.1%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦260.00 million; 2026 approved budget ₦622.00 million; change +₦362.00 million (+139.2%) (Kasafi's calculation)
• Total: 2025 approved budget ₦423.00 million; 2026 approved budget ₦829.50 million; change +₦406.50 million (+96.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 12, 14, 15; Sokoto State FY 2026 Budget, p. 16, 19, 22, 25
```

## false_premise-02 (template) ok (13.0s)

**Q:** Why did the Social Sector's approved budget fall from 2025 to 2026?

```
The Social Sector's approved budget did not fall. It was ₦175.57 billion in the 2025 approved budget and ₦278.88 billion in the 2026 original/approved budget, an increase of ₦103.31 billion (Kasafi's calculation) / (lissafin Kasafi).

• Social Sector (ministry total including its agencies, all spending (total), code 050000000000), 2025 Approved Budget: ₦175.57 billion
• Social Sector (ministry total including its agencies, all spending (total), code 050000000000), 2026 Original Budget: ₦278.88 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Budget Implementation Report Q2 2026, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-03 (template) ok (10.6s)

**Q:** Why did the Office of Auditor General's approved budget fall from 2025 to 2026?

```
The Office of Auditor General's budget did not fall. Its approved total was ₦542.84 million in 2025 and ₦606.84 million in 2026, an increase of ₦64.00 million 11.8% (Kasafi's calculation).

• Office of Auditor General (ministry total including its agencies, all spending (total), code 014000000000), 2025 Approved Budget: ₦542.84 million
• Office of Auditor General (ministry total including its agencies, all spending (total), code 014000000000), 2026 Approved Budget: ₦606.84 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-04 (template) ok (11.7s)

**Q:** Why did the Economic Sector's approved budget fall from 2025 to 2026?

```
The Economic Sector's approved budget did not fall. Its Total Expenditure allocation rose from ₦237.36 billion in 2025 to ₦316.04 billion in 2026 (Kasafi's calculation). Both figures are budgeted allocations, not spent amounts.

• Economic Sector (ministry total including its agencies, all spending (total), code 020000000000), 2025 Original Budget: ₦237.36 billion
• Economic Sector (ministry total including its agencies, all spending (total), code 020000000000), 2026 Original Budget: ₦316.04 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 17; Sokoto State Budget Implementation Report Q1 2026, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-05 (followup) ok (17.0s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
The evidence does not show a fall from 2025 to 2026. The 2025 approved budget (total) was ₦4.02 billion and the 2026 approved budget (total) was ₦17.06 billion. No reason for the change was found in the evidence.

• 2025 revised budget (total): ₦4.22 billion
• January–September 2025 spending (total): ₦1.17 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## not_in_data-01 (typo) ok (3.7s)

**Q:** How muhc did the Sokoto Road Maintenace Agency spend in Q4 2026?

```
Not in the documents:
• Sokoto Road Maintenance Agency 2026 spent in Q4: the latest implementation report is Q2 2026
• Sokoto Road Maintenance Agency 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
```

## not_in_data-02 (template) ok (5.0s)

**Q:** How much did the College of Nursing Sciences spend in Q4 2026?

```
Not in the documents:
• College of Nursing Sciences 2026 spent in Q4: the latest implementation report is Q2 2026
```

## not_in_data-03 (code_switched) ok (4.9s)

**Q:** Ministry of Culture & Tourism ta spend nawa in Q4 2026?

```
Ba a cikin takardun ba:
• Ministry of Culture & Tourism 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-04 (followup) ok (3.8s)

**Q:** How much did it spend in Q4 2026?

```
Not in the documents:
• College of Agriculture Wurno 2026 spent in Q4: the latest implementation report is Q2 2026
• College of Agriculture Wurno 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
• College of Agriculture Wurno 2026 share of the revised budget spent: the latest implementation report is Q2 2026
```

## not_in_data-05 (hausa) ok (3.9s)

**Q:** Nawa ne Infectious Diseases Hospital Amanawa ta kashe a Q4 2026?

```
Ba a cikin takardun ba:
• Infectious Diseases Hospital Amanawa 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Infectious Diseases Hospital Amanawa 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## rank_lga-01 (code_switched) ok (7.2s)

**Q:** Wadanne 5 LGAs ne a Sokoto have the most IDPs?

```
Ta ƙaramar hukuma (22), mafi yawa:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143
4. Tureta: 15,068
5. Shagari: 14,850

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-01 (followup) ok (5.1s)

**Q:** How many IDPs are in it?

```
IOM DTM counts *3,386* IDPs in Silame (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (template) ok (4.9s)

**Q:** How many IDPs are there in Shagari LGA?

```
IOM DTM counts *14,850* IDPs in Shagari (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-03 (typo) ok (5.4s)

**Q:** How mnay IDPs are thre in Bodinga LGA?

```
IOM DTM counts *1,990* IDPs in Bodinga (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-04 (hausa) ok (5.2s)

**Q:** Adadin IDPs a Tureta LGA nawa ne?

```
IOM DTM ta ƙidaya *15,068* 'yan gudun hijira a Tureta (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-05 (code_switched) ok (5.1s)

**Q:** Nawa IDPs ne a Goronyo LGA?

```
IOM DTM ta ƙidaya *1,926* 'yan gudun hijira a Goronyo (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## trend-01 (code_switched) ok (6.0s)

**Q:** Yawan IDPs na Sokoto State fa, how has it changed a last DTM rounds?

```
Jihar Sokoto, ta zagaye:
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
Jihar Sokoto, ta zagaye:
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
Jihar Sokoto, ta zagaye:
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

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```
