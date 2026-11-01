# Pattern eval

| pattern | wrong | of |
|---|---|---|
| p1_revenue | 0 | 7 |
| p2_period | 0 | 4 |
| p3_project | 0 | 3 |
| p4_narrative | 0 | 3 |
| p5_not_published | 0 | 2 |
| p6_multi_part | 0 | 3 |

Output checks on every reply (count of replies failing):

| check | failing |
|---|---|
| p7_letters | 0 |
| p8_labels | 1 |
| p9_cut | 0 |
| p11_bullet_first | 0 |

## p1_revenue-01 ok  (16.0s)

**Q:** How much revenue does the Ministry of Innovation and Digital Economy expect to collect in 2026?

```
The Ministry of Innovation and Digital Economy expects to collect ₦100.00 million in 2026. This is the ministry's total, its agencies included in the 2026 approved budget.

• Ministry of Innovation and Digital Economy, 2026 Approved Budget: ₦100.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 7
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-02 ok  (12.6s)

**Q:** How much revenue does the Ministry for Basic Education expect to collect in 2026?

```
The Ministry for Basic Education expects to collect ₦15.78 billion in revenue in the 2026 approved budget. This is the allocated (budgeted) total revenue figure, including capital receipts.

• Ministry for Basic Education, 2026 Approved Budget: ₦15.78 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-03 ok  (16.4s)

**Q:** How much revenue does the Sokoto State University expect to collect in 2026?

```
Sokoto State University expects to collect ₦315.00 million in revenue in 2026, as approved in the 2026 budget. This is budgeted (allocated) revenue, not actual collection.

• Sokoto State University, 2026 Approved Budget: ₦315.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-04 ok  (11.3s)

**Q:** How much revenue had the College of Nursing Sciences collected by the end of Q1 2026?

```
By the end of Q1 2026, the College of Nursing Sciences had collected ₦13.30 million in revenue. This is actual collection (spent/collected), not the approved budget.

• College of Nursing Sciences, 2026 Performance Year to Date (Q1): ₦13.30 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 12
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-05 ok  (21.3s)

**Q:** How much revenue had the Umaru Ali Shinkafi Polytechnic Sokoto collected by the end of Q1 2026?

```
By the end of Q1 2026, Umaru Ali Shinkafi Polytechnic Sokoto had collected ₦4.82 million in revenue (actual collection).

• Umaru Ali Shinkafi Polytechnic Sokoto, 2026 Performance Year to Date (Q1): ₦4.82 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-06 ok  (12.6s)

**Q:** How much does the 2026 budget expect to receive for the Nutrition Response (kyautata Rayuwa)- Recurrent?

```
The 2026 approved budget expects to receive ₦500.00 million for Nutrition Response (kyautata Rayuwa) - Recurrent. This is the budgeted (expected) revenue figure.

• NUTRITION RESPONSE (KYAUTATA RAYUWA)- RECURRENT (Ministry of Humanitarian Affairs & Social Welfare), 2026 Approved Budget: ₦500.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-07 ok  (18.9s)

**Q:** How much does the 2026 budget expect to receive for the Federal Government Tetfund Intervention - Capital?

```
The 2026 approved budget expects to receive ₦4.82 billion for Federal Government Tetfund Intervention - Capital. This is the budgeted (allocated) amount.

• FEDERAL GOVERNMENT TETFUND INTERVENTION - CAPITAL (Ministry for Higher Education), 2026 Approved Budget: ₦4.82 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p2_period-01 ok  (6.0s)

**Q:** How much had the Ministry for Religious Affairs spent by the end of Q1 2026?

```
For Ministry for Religious Affairs, the spent so far (Q1–Q1) is ₦1.02 billion.

*Ministry for Religious Affairs*:
• Total: spent so far (Q1–Q1) ₦1.02 billion; spent in Q1 ₦1.02 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-02 ok  (5.1s)

**Q:** How much had the Ministry Careers & Special Services spent by the end of Q1 2026?

```
For Ministry Careers & Special Services, the spent so far (Q1–Q1) is ₦1.84 billion.

*Ministry Careers & Special Services*:
• Total: spent so far (Q1–Q1) ₦1.84 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-03 ok  (8.4s)

**Q:** Nawa Ministry for Women Affairs ta kashe zuwa ƙarshen Q1 2026?

```
Ga Ministry for Women Affairs, abin da aka kashe zuwa yanzu (Q1–Q1) shi ne ₦305.20 miliyan.

*Ministry for Women Affairs*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q1) ₦305.20 miliyan

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 19
```

## p2_period-04 ok  (8.5s)

**Q:** How much did the Ministry of Lands and Housing spend from January to September 2025?

```
For Min of Lands and Housing, the spent so far (Q1–Q3) is ₦33.20 billion.

*Min of Lands and Housing*:
• Total: spent so far (Q1–Q3) ₦33.20 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## p6_multi_part-01 ok  (8.7s)

**Q:** How much was allocated to the Ministry of Justice in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Justice, the approved budget is ₦6.09 billion.

*Ministry of Justice*:
• Total: approved budget ₦6.09 billion; spent so far (Q1–Q2) ₦902.45 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18; Budget Implementation Report Q2 2026, p. 17
```

## p6_multi_part-02 ok  (5.2s)

**Q:** How much was allocated to the Ministry of Social Welfare & Community Development in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Social Welfare & Community Development, the approved budget is ₦5.11 billion.

*Ministry of Social Welfare & Community Development*:
• Total: approved budget ₦5.11 billion; spent so far (Q1–Q2) ₦365.48 million; share of the revised budget spent 7.1% (Kasafi's calculation)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19; Budget Implementation Report Q2 2026, p. 18
```

## p6_multi_part-03 ok  (7.7s)

**Q:** Nawa aka ware wa Civil Service Commission a 2026, kuma nawa ta kashe zuwa ƙarshen Q2 2026?

```
Ga Civil Service Commission, kasafin da aka amince shi ne ₦403.14 miliyan.

*Civil Service Commission*:
• Jimilla: kasafin da aka amince ₦403.14 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦141.42 miliyan; kason kasafin da aka sabunta da aka kashe 35.1% (lissafin Kasafi)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16; Budget Implementation Report Q2 2026, shafi 15
```

## p3_project-01 ok  (11.7s)

**Q:** How much is budgeted for Procurment of 5n0 peugout 406 saloon for members and secretary in 2026?

```
₦10.00 million was budgeted in the 2026 approved budget for Procurement of 5N0 Peugout 406 Saloon for Members and Secretary.

• Procurement of 5N0 Peugout 406 Saloon for Members and Secretary (JUDICIAL SERVICE COMMISSION), 2026 Approved Budget: ₦10.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 62
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-02 ok  (10.9s)

**Q:** How much is budgeted for Renovaton of kebbi house and gwandu house at iktc in 2026?

```
₦150.00 million was budgeted in the 2026 approved budget for Renovation of Kebbi House and Gwandu House at IKTC. This is the allocated (budgeted) amount, not spending.

• Renovation of Kebbi House and Gwandu House at IKTC (Ministry of Science and Technology), 2026 Approved Budget: ₦150.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 55
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-03 ok  (13.5s)

**Q:** How much is budgeted for Constraction of idp camps at isa, sabon birni and rabah in 2026?

```
₦800.00 million is budgeted for Construction of IDP Camps at Isa, Sabon Birni and Rabah in the 2026 approved budget. This is the allocated (budgeted) amount.

• Construction of IDP Camps at Isa, Sabon Birni and Rabah (Department for IDPs Matters), 2026 Approved Budget: ₦800.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 51
_Reply *show working* to see the rows and arithmetic._
```

## p4_narrative-01 ok  (16.1s)

**Q:** What does the Budget Implementation Report Q4 2025 say about Revenue Performance, and what reasons does it give?

```
The Budget Implementation Report Q4 2025 says Sokoto budgeted Total Revenue of ₦413.07 billion for 2025, with actual Total Revenue in Q4 of ₦95.24 billion and Capital Receipts of ₦33.85 billion. Year-to-date performance was 88.4% for Total Revenue and 42.9% for Independent Revenue, while Statutory Allocation performed at 109.0%. The report gives reasons for non-performance as restructuring of the Sokoto Geographical Information System, review of tax and non-tax rates, low sales of chemicals and farm produce, and insecurity affecting mining.

• 2025 Original Budget Total Revenue: ₦413.07 billion
• 2025 Q4 Performance Total Revenue: ₦95.24 billion
• 2025 Year to Date (Q1-Q4) Total Revenue: ₦365.26 billion (88.4% of final budget)
• Statutory Allocation performance: 109.0%
• Independent Revenue YTD: ₦20.58 billion (42.9% of final budget)

📄 *Sources:* Budget Implementation Report Q4 2025, p. 5, 9, 10
```

## p4_narrative-02 ok  (22.0s)

**Q:** What does the Sokoto State Budget Implementation Report Q3 2025 say about Revenue Performance, and what reasons does it give?

```
The Sokoto State Budget Implementation Report Q3 2025 says the State budgeted a Total Revenue and other receipts to the tune of ₦413.07 billion for 2025. It reports actual Total Revenue in the third quarter was ₦104.32 billion (Q3 only) and Year to Date (Q1-Q3) was 65.4% of the revised budget. For components it reports Statutory Allocation had a performance of 90.2% and Internally Generated Revenue closed with a performance of 30.5%. For reasons, the report says the noticeable zero performance of some revenue items were as a result of timing as most of them will be due from the fourth quarter, as well as administrative changes that are linked to the current reforms.

• 2025 budgeted Total Revenue (total): ₦413.07 billion
• 2025 Q3 actual Total Revenue (Q3 only) (total): ₦104.32 billion
• 2025 YTD Total Revenue (Q1-Q3) (total): ₦270.02 billion (65.4% of the revised budget)
• Statutory Allocation / Government Share of FAAC YTD (Q1-Q3) (total): ₦234.31 billion (90.2% of the revised budget)
• Independent Revenue (IGR) YTD (Q1-Q3) (total): ₦14.62 billion (30.5% of the revised budget)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 4, 9, 10
```

## p4_narrative-03 ok  (16.7s)

**Q:** What does the Budget Implementation Report Q2 2026 say about Primary Healthcare Budget Performance, and what reasons does it give?

```
The Primary Healthcare subsector was allocated ₦7.21 billion in the 2026 Approved Revised Budget. As at end of Q2 2026, actual expenditure was ₦1.22 billion, representing 16.9% of the approved revised budget allocation for the sector. The report says this low performance can be attributed to low related capital receipts draw down, procurement process, late commencement of key capital projects under the sector, and associated expenditure documented under the local government's budget such as personnel cost and other allowances.

• 2026 Approved Revised Budget (total) allocated to PHC: ₦7.21 billion
• 2026 Performance Year to Date (Q1-Q2) actual expenditure (total): ₦1.22 billion, 16.9% of revised budget
• 2026 Q2 Performance (total): ₦370.04 million

📄 *Sources:* Budget Implementation Report Q2 2026, p. 51, 52
```

## p5_not_published-01 ok  (21.3s)

**Q:** How many staff does the Ministry for Special Duties employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The number of staff and their grade levels for the Ministry for Special Duties isn't published in these documents. The documents only show the Ministry's personnel budget and spending. Its 2026 approved budget (total) is ₦829.50 million and its 2026 approved budget for personnel is ₦12.00 million.

• 2026 approved budget (personnel): ₦12.00 million
• 2026 approved budget (total): ₦829.50 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 19
```

## p5_not_published-02 ok p8_labels (32.9s)

**Q:** How many staff does the Government House employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The number of staff the Government House employs and the grade levels they are on isn't published in these documents. The documents do publish its budgets. In the 2026 approved budget the Government House personnel budget is ₦444.25 million (total including its agencies), and its total expenditure budget is ₦18.53 billion.

• 2026 approved budget (personnel) for Government House (ministry total including its agencies): ₦444.25 million
• 2026 approved budget (total) for Government House: ₦18.53 billion
• 2025 performance January to September (personnel) for Government House: ₦303.44 million
• 2026 Q1-Q2 performance year to date (personnel) for Government House (January-June 2026 only): ₦239.19 million (53.8% of the revised budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 19; Budget Implementation Report Q2 2026, p. 19
```

