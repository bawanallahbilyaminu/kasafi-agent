# Generated coverage run

42 cases: wrong 1 | median 4.8s

| family | wrong | of |
|---|---|---|
| compare | 0 | 5 |
| false_premise | 0 | 5 |
| lookup | 0 | 5 |
| lookup_lga | 0 | 5 |
| not_in_data | 0 | 5 |
| rank_lga | 0 | 1 |
| share | 1 | 5 |
| spend_quarter | 0 | 5 |
| split | 0 | 5 |
| trend | 0 | 1 |

| form | wrong | of |
|---|---|---|
| code_switched | 0 | 12 |
| followup | 0 | 6 |
| hausa | 0 | 5 |
| informal | 1 | 3 |
| template | 0 | 11 |
| typo | 0 | 5 |

## lookup-01 (hausa) ok (14.5s)

**Q:** Nawa aka amince wa Ministry of Education a kasafin kudin 2026?

```
An amince wa Ministry of Education jimilla ₦68.95 biliyan a kasafin kuɗi na 2026. Wannan jimilla ce daga teburin Total Expenditure by Administrative Classification.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
```

## lookup-02 (typo) ok (9.2s)

**Q:** How mch was aproved for the Ministry for Higher Education in the 2026 budget?

```
The State Government approved ₦33.99 billion as total for the Ministry for Higher Education in the 2026 budget. This is the allocated (budgeted) amount from the Total Expenditure table.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18
```

## lookup-03 (template) ok (12.7s)

**Q:** How much was approved for the Ministry of Information in the 2026 budget?

```
The State Government approved ₦2.48 billion for the Ministry of Information in the 2026 budget (total, from the Total Expenditure by Administrative Classification table). This total includes its agencies, while the headquarters alone was approved ₦1.58 billion.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
```

## lookup-04 (informal) ok (10.5s)

**Q:** How much did Sokoto State House of Assembly get in the 2026 budget?

```
The Sokoto State House of Assembly was allocated ₦12.26 billion in the 2026 approved budget (total). By Q1–Q2 2026 (January–June only), it had spent ₦1.77 billion (14.4% of the revised budget).

• Headquarters 2026 approved budget (total): ₦11.62 billion
• House of Assembly Service Commission 2026 approved budget (total): ₦634.28 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16; Budget Implementation Report Q2 2026, p. 15
```

## lookup-05 (template) ok (12.3s)

**Q:** How much was approved for the Economic Sector in the 2026 budget?

```
The 2026 approved budget (total) for the Economic Sector is ₦316.04 billion. This figure is from the Total Expenditure by Administrative Classification table. It is the allocated (budgeted) amount, not spending.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
```

## split-01 (code_switched) ok (3.7s)

**Q:** Nawa ne personnel, overhead da capital allocations na Department for Rural Roads in 2026?

```
*Department for Rural Roads* (code 023405700100):
• Albashi: kasafin da aka amince ₦28.59 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦133.95 miliyan
• Manyan ayyuka: kasafin da aka amince ₦15.47 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 20, 23, 26
```

## split-02 (code_switched) ok (3.8s)

**Q:** Sokoto State Independent Electoral Commission ta samu nawa for personnel, overhead da capital a 2026?

```
*Sokoto State Independent Electoral Commission* (code 014800000000):
• Albashi: kasafin da aka amince ₦128.76 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦106.00 miliyan
• Manyan ayyuka: kasafin da aka amince ₦225.71 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 19, 22, 25
```

## split-03 (code_switched) ok (2.9s)

**Q:** Personnel, overhead da capital allocation na Female Education Board a 2026 din nawa ne?

```
*Female Education Board* (code 051705700100):
• Albashi: kasafin da aka amince ₦47.45 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦462.05 miliyan
• Manyan ayyuka: kasafin da aka amince ₦650.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 21, 24, 27
```

## split-04 (followup) ok (3.5s)

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

## spend_quarter-02 (template) ok (4.2s)

**Q:** How much had the SUSTAINABLE DEVELOPMENT GOALS (SDG) spent by the end of Q2 2026, against its revised budget?

```
*SUSTAINABLE DEVELOPMENT GOALS (SDG)* (code 023800600200):
• Total: revised budget ₦42.00 million; spent so far (Q1–Q2) ₦1.00 million; share of the revised budget spent 2.4% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 17
```

## spend_quarter-03 (code_switched) ok (3.9s)

**Q:** Ministry of Budget and Economic Planning ta kashe nawa by the end of Q2 2026 against revised budget dinta?

```
*Ministry of Budget and Economic Planning* (code 023800000000):
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q2) ₦541.38 miliyan; kasafin da aka sabunta ₦5.32 biliyan; kason kasafin da aka sabunta da aka kashe 10.2% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 17
```

## spend_quarter-04 (template) ok (3.8s)

**Q:** How much had the Bureau for Public Procurement and Price Intelligence spent by the end of Q2 2026, against its revised budget?

```
*Bureau for Public Procurement and Price Intelligence* (code 011101000100):
• Total: revised budget ₦81.76 million; spent so far (Q1–Q2) ₦4.86 million; share of the revised budget spent 5.9% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 15
```

## spend_quarter-05 (code_switched) ok (3.9s)

**Q:** Department for Security Matters ta kashe nawa by the end of Q2 2026, against its revised budget?

```
*Department for Security Matters* (code 017000100200):
• Jimilla: kasafin da aka sabunta ₦37.15 biliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦7.61 biliyan; kason kasafin da aka sabunta da aka kashe 20.5% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 16
```

## compare-01 (code_switched) ok (2.9s)

**Q:** Compare approved budget na Ministry of Justice a 2025 da 2026 fa?

```
*Ministry of Justice* (code 032600000000):
• Jimilla: 2025 kasafin da aka amince ₦4.46 biliyan; 2026 kasafin da aka amince ₦6.09 biliyan; bambanci +₦1.63 biliyan (+36.5%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-02 (typo) ok (3.2s)

**Q:** Comapre the Ministry of Innovation and Digtal Economy's aproved budget in 2025 and 2026.

```
*Ministry of Innovation and Digital Economy* (code 027900000000):
• Total: 2025 approved budget ₦1.35 billion; 2026 approved budget ₦3.59 billion; change +₦2.24 billion (+166.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-03 (template) ok (3.6s)

**Q:** Compare the Fiscal Responsibility Commission's approved budget in 2025 and 2026.

```
*Fiscal Responsibility Commission* (code 025000000000):
• Total: 2025 approved budget ₦58.99 million; 2026 approved budget ₦60.99 million; change +₦2.00 million (+3.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## compare-04 (followup) ok (3.4s)

**Q:** How did its approved budget compare in 2025 and 2026?

```
*Ministry for Women Affairs* (code 051400000000):
• Total: 2025 approved budget ₦8.44 billion; 2026 approved budget ₦7.24 billion; change -₦1.21 billion (-14.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-05 (code_switched) ok (3.3s)

**Q:** Kwatanta mana Government House approved budget na 2025 and 2026.

```
*Government House* (code 011100000000):
• Jimilla: 2025 kasafin da aka amince ₦14.03 biliyan; 2026 kasafin da aka amince ₦18.53 biliyan; bambanci +₦4.50 biliyan (+32.1%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## share-01 (informal) WRONG: missing ['20.0%'] (3.4s)

**Q:** How much of Sokoto State Rima Televiosn (Rtv)'s 2026 approved budget is capital?

```
*Sokoto State Rima Televiosn (Rtv)* (code 012300300100):
• Capital: approved budget ₦30.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 25
```

## share-02 (followup) ok (11.9s)

**Q:** What share of its 2026 approved budget is capital?

```
Capital expenditure is ₦236.00 million of the Poultry Development Agency's 2026 approved total of ₦302.14 million. That is 78.1% (Kasafi's calculation) capital.

• Poultry Development Agency (one agency or unit, capital, code 026800300100) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦236.00 million ↑
• Poultry Development Agency (one agency or unit, all spending (total), code 026800300100) [Total Expenditure by Administrative Classification], 2026 Approved Budget: ₦302.14 million ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 26
_Reply *show working* to see the rows and arithmetic._
```

## share-03 (hausa) ok (10.4s)

**Q:** Wane kaso na kasafin kudin Commodity Board da aka amince da shi na 2026 na babban aiki ne?

```
Babban aiki shine mafi yawan kasafin Commodity Board na 2026 da aka amince da shi. An amince da ₦650.00 miliyan na babban aiki daga jimillar ₦673.97 miliyan, wanda ya kai 96.4% (lissafin Kasafi).

• Commodity Board (hukuma ɗaya, manyan ayyuka, code 022200200100) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦650.00 miliyan ↑
• Commodity Board (hukuma ɗaya, duk kashe kuɗi (jimilla), code 022200200100) [Total Expenditure by Administrative Classification], 2026 Approved Budget: ₦673.97 miliyan ↓

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## share-04 (typo) ok (9.5s)

**Q:** What shrae of the Sokoto State SME Developmant Agency's 2026 approved budget is capital?

```
Capital is ₦100.00 million of the Agency's 2026 approved total of ₦1.48 billion. That is 6.7% (Kasafi's calculation) of the 2026 approved budget.

• Sokoto State SME Development Agency (one agency or unit, capital, code 022205100100) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦100.00 million ↑
• Sokoto State SME Development Agency (one agency or unit, all spending (total), code 022205100100) [Total Expenditure by Administrative Classification], 2026 Approved Budget: ₦1.48 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
_Reply *show working* to see the rows and arithmetic._
```

## share-05 (template) ok (12.9s)

**Q:** What share of the Fiscal Responsibility Commission's 2026 approved budget is capital?

```
Capital is ₦14.25 million out of the Commission's 2026 approved total of ₦60.99 million. That is 23.4% (Kasafi's calculation) of its 2026 approved budget.

• Fiscal Responsibility Commission (one agency or unit, capital, code 025000100100) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦14.25 million ↑
• Fiscal Responsibility Commission (one agency or unit, all spending (total), code 025000100100) [Total Expenditure by Administrative Classification], 2026 Approved Budget: ₦60.99 million ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-01 (informal) ok (14.2s)

**Q:** Why did Ministry for Special Duties's approved budget drop from 2025 to 2026?

```
The Ministry for Special Duties's approved budget did not drop. Its total allocation rose from ₦423.00 million in 2025 to ₦829.50 million in 2026, ₦406.50 million (Kasafi's calculation).

• Ministry for Special Duties (ministry total including its agencies, all spending (total), code 016700000000), 2025 Approved Budget: ₦423.00 million
• Ministry for Special Duties (ministry total including its agencies, all spending (total), code 016700000000), 2026 Approved Budget: ₦829.50 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-02 (template) ok (13.5s)

**Q:** Why did the Social Sector's approved budget fall from 2025 to 2026?

```
The Social Sector's approved budget did not fall. Its total approved allocation rose from ₦175.57 billion in 2025 to ₦278.88 billion in 2026, a rise of ₦103.31 billion (Kasafi's calculation).

• Social Sector (ministry total including its agencies, all spending (total), code 050000000000), 2025 Original Budget: ₦175.57 billion
• Social Sector (ministry total including its agencies, all spending (total), code 050000000000), 2026 Original Budget: ₦278.88 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18; Budget Implementation Report Q2 2026, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-03 (template) ok (13.4s)

**Q:** Why did the Office of Auditor General's approved budget fall from 2025 to 2026?

```
The Office of Auditor General's budget did not fall. Its approved total rose from ₦542.84 million in 2025 to ₦606.84 million in 2026, a rise of ₦64.00 million (Kasafi's calculation) or 11.8% (Kasafi's calculation).

• Office of Auditor General (ministry total including its agencies, all spending (total), code 014000000000), 2025 Approved Budget: ₦542.84 million
• Office of Auditor General (ministry total including its agencies, all spending (total), code 014000000000), 2026 Approved Budget: ₦606.84 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-04 (template) ok (10.5s)

**Q:** Why did the Economic Sector's approved budget fall from 2025 to 2026?

```
_Assumption: compared 2025 approved budget with 2026 approved budget._

The Economic Sector's approved budget did not fall. It was ₦237.36 billion in the 2025 approved budget and ₦316.04 billion in the 2026 approved budget, an increase of ₦78.68 billion (Kasafi's calculation). Both figures are approved allocations (total expenditure).

• Economic Sector (ministry total including its agencies, all spending (total), code 020000000000), 2025 Approved Budget: ₦237.36 billion
• Economic Sector (ministry total including its agencies, all spending (total), code 020000000000), 2026 Approved Budget: ₦316.04 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-05 (followup) ok (3.6s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
*Ministry of Youth and Sports Development* (code 051300000000):
• Total: 2025 approved budget ₦4.02 billion; 2026 approved budget ₦17.06 billion; change +₦13.03 billion (+323.8%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## not_in_data-01 (typo) ok (4.5s)

**Q:** How muhc did the Sokoto Road Maintenace Agency spend in Q4 2026?

```
Not in the documents:
• Sokoto Road Maintenance Agency 2026 spent in Q4: the latest implementation report is Q2 2026
```

## not_in_data-02 (template) ok (5.4s)

**Q:** How much did the College of Nursing Sciences spend in Q4 2026?

```
Not in the documents:
• College of Nursing Sciences 2026 spent in Q4: the latest implementation report is Q2 2026
• College of Nursing Sciences 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
```

## not_in_data-03 (code_switched) ok (4.2s)

**Q:** Ministry of Culture & Tourism ta spend nawa in Q4 2026?

```
Ba a cikin takardun ba:
• Ministry of Culture & Tourism 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Ministry of Culture & Tourism 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Ministry of Culture & Tourism 2026 kason kasafin da aka sabunta da aka kashe: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-04 (followup) ok (4.7s)

**Q:** How much did it spend in Q4 2026?

```
Not in the documents:
• College of Agriculture Wurno 2026 spent in Q4: the latest implementation report is Q2 2026
• College of Agriculture Wurno 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
```

## not_in_data-05 (hausa) ok (5.4s)

**Q:** Nawa ne Infectious Diseases Hospital Amanawa ta kashe a Q4 2026?

```
Ba a cikin takardun ba:
• Infectious Diseases Hospital Amanawa 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Infectious Diseases Hospital Amanawa 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Infectious Diseases Hospital Amanawa 2026 kason kasafin da aka sabunta da aka kashe: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## rank_lga-01 (code_switched) ok (5.1s)

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

## lookup_lga-01 (followup) ok (5.0s)

**Q:** How many IDPs are in it?

```
IOM DTM counts *3,386* IDPs in Silame (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (template) ok (4.6s)

**Q:** How many IDPs are there in Shagari LGA?

```
IOM DTM counts *14,850* IDPs in Shagari (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-03 (typo) ok (5.6s)

**Q:** How mnay IDPs are thre in Bodinga LGA?

```
IOM DTM counts *1,990* IDPs in Bodinga (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-04 (hausa) ok (7.0s)

**Q:** Adadin IDPs a Tureta LGA nawa ne?

```
IOM DTM ta ƙidaya *15,068* 'yan gudun hijira a Tureta (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-05 (code_switched) ok (6.3s)

**Q:** Nawa IDPs ne a Goronyo LGA?

```
IOM DTM ta ƙidaya *1,926* 'yan gudun hijira a Goronyo (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## trend-01 (code_switched) ok (15.0s)

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

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```
