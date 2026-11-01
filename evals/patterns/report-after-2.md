# Pattern eval

| pattern | wrong | of |
|---|---|---|
| p1_revenue | 0 | 7 |
| p2_period | 0 | 4 |
| p3_project | 0 | 3 |
| p4_narrative | 1 | 3 |
| p5_not_published | 0 | 2 |
| p6_multi_part | 0 | 3 |

Output checks on every reply (count of replies failing):

| check | failing |
|---|---|
| p7_letters | 0 |
| p8_labels | 0 |
| p9_cut | 0 |
| p11_bullet_first | 0 |

## p1_revenue-01 ok  (21.9s)

**Q:** How much revenue does the Ministry of Innovation and Digital Economy expect to collect in 2026?

```
The Ministry of Innovation and Digital Economy expects to collect ₦100.00 million in 2026. This is the 2026 approved budget figure for the ministry total.

• Ministry of Innovation and Digital Economy, 2026 Approved Budget: ₦100.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 7
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-02 ok  (17.3s)

**Q:** How much revenue does the Ministry for Basic Education expect to collect in 2026?

```
The Ministry for Basic Education expects to collect ₦15.78 billion in revenue in the 2026 approved budget. This is the ministry's Total Revenue figure, including capital receipts.

• Ministry for Basic Education, 2026 Approved Budget: ₦15.78 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-03 ok  (19.1s)

**Q:** How much revenue does the Sokoto State University expect to collect in 2026?

```
Sokoto State University expects to collect ₦315.00 million in revenue in 2026. This is the 2026 approved budget figure (allocated, not spent).

• Sokoto State University, 2026 Approved Budget: ₦315.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-04 ok  (11.3s)

**Q:** How much revenue had the College of Nursing Sciences collected by the end of Q1 2026?

```
By the end of Q1 2026, the College of Nursing Sciences had collected ₦13.30 million in revenue. This is actual revenue collected, not the budgeted allocation.

• College of Nursing Sciences, 2026 Performance Year to Date (Q1): ₦13.30 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 12
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-05 ok  (17.5s)

**Q:** How much revenue had the Umaru Ali Shinkafi Polytechnic Sokoto collected by the end of Q1 2026?

```
Umaru Ali Shinkafi Polytechnic Sokoto had collected ₦4.82 million in revenue by the end of Q1 2026. This is actual collected revenue (spent/collected), not the approved budget.

• Umaru Ali Shinkafi Polytechnic Sokoto, 2026 Performance Year to Date (Q1): ₦4.82 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-06 ok  (16.3s)

**Q:** How much does the 2026 budget expect to receive for the Nutrition Response (kyautata Rayuwa)- Recurrent?

```
The 2026 approved budget expects to receive ₦500.00 million for Nutrition Response (Kyautata Rayuwa) - Recurrent. This is the budgeted (allocated) revenue expectation.

• NUTRITION RESPONSE (KYAUTATA RAYUWA)- RECURRENT (Ministry of Humanitarian Affairs & Social Welfare), 2026 Approved Budget: ₦500.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-07 ok  (17.2s)

**Q:** How much does the 2026 budget expect to receive for the Federal Government Tetfund Intervention - Capital?

```
The 2026 approved budget expects to receive ₦4.82 billion for Federal Government Tetfund Intervention - Capital. This is the budgeted (expected) amount, not actual spending.

• FEDERAL GOVERNMENT TETFUND INTERVENTION - CAPITAL (Ministry for Higher Education), 2026 Approved Budget: ₦4.82 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p2_period-01 ok  (19.9s)

**Q:** How much had the Ministry for Religious Affairs spent by the end of Q1 2026?

```
By the end of Q1 2026 the Ministry for Religious Affairs had spent ₦1.02 billion (January–March 2026 only). This is 5.7% of its 2026 Original Budget of ₦18.05 billion. The figure is the total expenditure for the ministry including its agencies.

• 2026 Original Budget (total): ₦18.05 billion
• 2026 Q1 Performance (total, January–March 2026 only): ₦1.02 billion (5.7% of the original budget)

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-02 ok  (13.8s)

**Q:** How much had the Ministry Careers & Special Services spent by the end of Q1 2026?

```
By the end of Q1 2026 (January–March) the Ministry Careers & Special Services had spent ₦1.84 billion in total (7.0% of its 2026 Original Budget). This was made up of personnel and overhead spending, with no capital spending recorded in Q1.

• 2026 Q1 total spent (total): ₦1.84 billion (7.0% of the original budget) (January–March 2026 only)
• 2026 Q1 personnel spent (personnel): ₦17.46 million (27.5% of the original budget) (January–March 2026 only)
• 2026 Q1 overhead spent (overhead): ₦1.83 billion (10.1% of the original budget) (January–March 2026 only)
• 2026 Q1 capital spent (capital): - (0.0% of the original budget) (January–March 2026 only)

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17, 20, 24, 27
```

## p2_period-03 ok  (15.3s)

**Q:** Nawa Ministry for Women Affairs ta kashe zuwa ƙarshen Q1 2026?

```
Ministry for Women Affairs ta kashe jimilla ₦305.20 miliyan zuwa ƙarshen Q1 2026 (Janairu–Maris 2026 kawai). Wannan kashewar ita ce 4.2% na kasafin 2026 da aka amince da shi na ₦7.24 biliyan.

• 2026 kasafin da aka amince da shi (jimilla): ₦7.24 biliyan
• Q1 2026 kashewar albashi (Janairu–Maris 2026 kawai): ₦34.57 miliyan (27.5% na kasafin ƙarshe)
• Q1 2026 kashewar kuɗin gudanarwa (Janairu–Maris 2026 kawai): ₦56.00 miliyan (7.3% na kasafin ƙarshe)

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 19, 22, 25
```

## p2_period-04 ok  (3.8s)

**Q:** How much did the Ministry of Lands and Housing spend from January to September 2025?

```
For Min of Lands and Housing, the spent so far (Q1–Q3) is ₦33.20 billion.

*Min of Lands and Housing*:
• Total: spent so far (Q1–Q3) ₦33.20 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## p6_multi_part-01 ok  (4.8s)

**Q:** How much was allocated to the Ministry of Justice in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Justice, the approved budget is ₦6.09 billion.

*Ministry of Justice*:
• Total: approved budget ₦6.09 billion; spent so far (Q1–Q2) ₦902.45 million; share of the revised budget spent 14.8% (Kasafi's calculation)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18; Budget Implementation Report Q2 2026, p. 17
```

## p6_multi_part-02 ok  (3.8s)

**Q:** How much was allocated to the Ministry of Social Welfare & Community Development in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Social Welfare & Community Development, the approved budget is ₦5.11 billion.

*Ministry of Social Welfare & Community Development*:
• Total: approved budget ₦5.11 billion; spent so far (Q1–Q2) ₦365.48 million; share of the revised budget spent 7.1% (Kasafi's calculation)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19; Budget Implementation Report Q2 2026, p. 18
```

## p6_multi_part-03 ok  (4.5s)

**Q:** Nawa aka ware wa Civil Service Commission a 2026, kuma nawa ta kashe zuwa ƙarshen Q2 2026?

```
Ga Civil Service Commission, kasafin da aka amince shi ne ₦403.14 miliyan.

*Civil Service Commission*:
• Jimilla: kasafin da aka amince ₦403.14 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦141.42 miliyan; kason kasafin da aka sabunta da aka kashe 35.1% (lissafin Kasafi)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16; Budget Implementation Report Q2 2026, shafi 15
```

## p3_project-01 ok  (9.3s)

**Q:** How much is budgeted for Procurment of 5n0 peugout 406 saloon for members and secretary in 2026?

```
₦10.00 million was budgeted in 2026 for Procurement of 5N0 Peugout 406 Saloon for Members and Secretary (Judicial Service Commission). This is the approved allocation figure.

• Procurement of 5N0 Peugout 406 Saloon for Members and Secretary (JUDICIAL SERVICE COMMISSION), 2026 Approved Budget: ₦10.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 62
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-02 ok  (11.0s)

**Q:** How much is budgeted for Renovaton of kebbi house and gwandu house at iktc in 2026?

```
₦150.00 million is budgeted for Renovation of Kebbi House and Gwandu House at IKTC in the 2026 approved budget.

• Renovation of Kebbi House and Gwandu House at IKTC (Ministry of Science and Technology), 2026 Approved Budget: ₦150.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 55
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-03 ok  (12.1s)

**Q:** How much is budgeted for Constraction of idp camps at isa, sabon birni and rabah in 2026?

```
₦800.00 million is budgeted for Construction of IDP Camps at Isa, Sabon Birni and Rabah in the 2026 approved budget. This is the allocated (budgeted) amount, not spending.

• Construction of IDP Camps at Isa, Sabon Birni and Rabah (Department for IDPs Matters), 2026 Approved Budget: ₦800.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 51
_Reply *show working* to see the rows and arithmetic._
```

## p4_narrative-01 ok  (11.8s)

**Q:** What does the Budget Implementation Report Q4 2025 say about Revenue Performance, and what reasons does it give?

```
The Budget Implementation Report Q4 2025 says the State Government budgeted total revenue and other receipts of ₦413.07 billion for 2025. This was made up of recurrent revenue of ₦268.95 billion and capital receipts of ₦144.13 billion, with an opening balance of ₦113.81 billion carried forward from 2024. For the full year to Q4, total revenue collected was ₦365.26 billion, which is 88.4% of the final budget, and total revenue including opening balance was ₦449.84 billion, which is 85.4% of the final budget. The report says statutory allocation performed at 109.0% and internally generated revenue at 42.9%. For reasons for non-performance, the report says restructuring of the Sokoto Geographical Information System in alignment with the Ministry of Lands and Housing dwindled 2025 collections, other MDAs were affected by a review of tax and non-tax rates with the State Ministry of Justice, there were not much sales of chemicals and farm produce, and mining activities were grossly affected by insecurity.

• 2025 total revenue budgeted (total): ₦413.07 billion
• 2025 Q4 performance (total): ₦95.24 billion
• 2025 year-to-date total revenue (total): ₦365.26 billion (88.4% of the final budget)
• Statutory allocation performance: 109.0%
• Internally Generated Revenue performance: 42.9%

📄 *Sources:* Budget Implementation Report Q4 2025, p. 5, 9, 10
```

## p4_narrative-02 WRONG: didn't cite bir-2025-q3 p4  (12.3s)

**Q:** What does the Sokoto State Budget Implementation Report Q3 2025 say about Revenue Performance, and what reasons does it give?

```
The report's tables show Total Revenue for 2025 of ₦413.07 billion, with Year to Date (Q1-Q3) performance of ₦270.02 billion (65.4% of the revised budget), and Total Revenue including opening balance of ₦526.88 billion, with Year to Date performance of ₦354.61 billion (67.3% of the revised budget). The running-text paragraphs in the evidence do not explain reasons for Revenue Performance; they only explain budget revisions and low spending in the Primary Healthcare and Basic Education sub-sectors.

• 2025 approved budget (total) Total Revenue: ₦413.07 billion
• 2025 performance Year to Date (Q1-Q3) (January–September 2025 only) Total Revenue: ₦270.02 billion (65.4% of the revised budget)
• 2025 approved budget (total) Total Revenue (including OB): ₦526.88 billion
• 2025 performance Year to Date (Q1-Q3) (January–September 2025 only) Total Revenue (including OB): ₦354.61 billion (67.3% of the revised budget)
• 2025 performance Year to Date (Q1-Q3) (January–September 2025 only) Independent Revenue: ₦14.62 billion (30.5% of the revised budget)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 9, 10, 78, 82
```

## p4_narrative-03 ok  (12.6s)

**Q:** What does the Budget Implementation Report Q2 2026 say about Primary Healthcare Budget Performance, and what reasons does it give?

```
The Primary Healthcare subsector was allocated ₦7.21 billion in the 2026 Approved Revised Budget. As at the end of Q2 2026, total actual expenditure was ₦1.22 billion, which is 16.9% of the allocation. The report describes this as low budget performance. It gives these reasons: low related capital receipts draw down, procurement process, late commencement of key capital projects, and that associated expenditure such as personnel cost and other allowances are documented under the local government's budget.

• 2026 Approved Revised Budget (total): ₦7.21 billion
• Q2 2026 performance (total, April-June 2026 only): ₦370.04 million
• Year to Date Q1-Q2 2026 (total): ₦1.22 billion (16.9% of the revised budget)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 51, 52
```

## p5_not_published-01 ok  (9.4s)

**Q:** How many staff does the Ministry for Special Duties employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The number of staff and their grade levels for the Ministry for Special Duties isn't published in these documents. The documents only publish its budget for staff pay. In the 2026 approved budget (total) the Ministry for Special Duties was allocated ₦829.50 million, of which ₦12.00 million was for personnel (staff pay). Its 2025 performance January to September (spent) for personnel was ₦7.98 million.

• 2026 approved budget (total): ₦829.50 million
• 2026 approved budget (personnel): ₦12.00 million
• 2025 approved budget (personnel): ₦8.00 million
• 2025 performance January to September (personnel, spent): ₦7.98 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 16, 19
```

## p5_not_published-02 ok  (9.0s)

**Q:** How many staff does the Government House employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The latest budget (2026) doesn't publish staff numbers or grade levels for the Government House. What it does publish is the Government House's budget: its 2026 approved budget (total) is ₦18.53 billion and its 2026 personnel budget is ₦444.25 million.

• 2026 approved budget (total) for Government House: ₦18.53 billion
• 2026 personnel Original Budget for Government House: ₦444.25 million
• 2026 Q1-Q2 personnel spending for Government House: ₦239.19 million (53.8% of the revised budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16; Budget Implementation Report Q2 2026, p. 19
```

