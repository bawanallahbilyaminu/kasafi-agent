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
| p8_labels | 0 |
| p9_cut | 0 |
| p11_bullet_first | 0 |

## p1_revenue-01 ok  (8.2s)

**Q:** How much revenue does the Ministry of Innovation and Digital Economy expect to collect in 2026?

```
The Ministry of Innovation and Digital Economy expects to collect ₦100.00 million in 2026. This is the 2026 approved budget figure (allocated, not spent).

• Ministry of Innovation and Digital Economy, 2026 Approved Budget: ₦100.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 7
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-02 ok  (8.3s)

**Q:** How much revenue does the Ministry for Basic Education expect to collect in 2026?

```
The Ministry for Basic Education expects to collect ₦15.78 billion in revenue in the 2026 approved budget. This is the total revenue figure, including capital receipts.

• Ministry for Basic Education, 2026 Approved Budget: ₦15.78 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-03 ok  (6.4s)

**Q:** How much revenue does the Sokoto State University expect to collect in 2026?

```
Sokoto State University expects to collect ₦315.00 million in revenue in 2026. This is the 2026 approved budget figure (allocated, not spent).

• Sokoto State University, 2026 Approved Budget: ₦315.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-04 ok  (9.8s)

**Q:** How much revenue had the College of Nursing Sciences collected by the end of Q1 2026?

```
By the end of Q1 2026, the College of Nursing Sciences had collected ₦13.30 million in revenue (actual collection).

• College of Nursing Sciences, 2026 Performance Year to Date (Q1): ₦13.30 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 12
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-05 ok  (8.2s)

**Q:** How much revenue had the Umaru Ali Shinkafi Polytechnic Sokoto collected by the end of Q1 2026?

```
By the end of Q1 2026, Umaru Ali Shinkafi Polytechnic Sokoto had collected ₦4.82 million in revenue. This is actual revenue collected (spent/performance), not the approved budget.

• Umaru Ali Shinkafi Polytechnic Sokoto, 2026 Performance Year to Date (Q1): ₦4.82 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-06 ok  (5.4s)

**Q:** How much does the 2026 budget expect to receive for the Nutrition Response (kyautata Rayuwa)- Recurrent?

```
The 2026 approved budget expects to receive ₦500.00 million for Nutrition Response (Kyautata Rayuwa) - Recurrent. This is the budgeted (allocation) figure.

• NUTRITION RESPONSE (KYAUTATA RAYUWA)- RECURRENT (Ministry of Humanitarian Affairs & Social Welfare), 2026 Approved Budget: ₦500.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-07 ok  (5.9s)

**Q:** How much does the 2026 budget expect to receive for the Federal Government Tetfund Intervention - Capital?

```
The 2026 approved budget expects to receive ₦4.82 billion for Federal Government Tetfund Intervention - Capital.

• FEDERAL GOVERNMENT TETFUND INTERVENTION - CAPITAL (Ministry for Higher Education), 2026 Approved Budget: ₦4.82 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p2_period-01 ok  (3.5s)

**Q:** How much had the Ministry for Religious Affairs spent by the end of Q1 2026?

```
For Ministry for Religious Affairs, the spent so far (Q1–Q1) is ₦1.02 billion.

*Ministry for Religious Affairs*:
• Total: spent so far (Q1–Q1) ₦1.02 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-02 ok  (8.9s)

**Q:** How much had the Ministry Careers & Special Services spent by the end of Q1 2026?

```
The Ministry Careers & Special Services had a 2026 approved budget (total) of ₦26.37 billion. By the end of Q1 2026 it had spent ₦1.84 billion (total, Q1 only), which is 7.0% of the original budget.

• 2026 approved budget (total): ₦26.37 billion
• Q1 2026 spent (total, January–March only): ₦1.84 billion (7.0% of the original budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16; Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-03 ok  (10.3s)

**Q:** Nawa Ministry for Women Affairs ta kashe zuwa ƙarshen Q1 2026?

```
Ministry for Women Affairs ta kashe ₦305.20 miliyan zuwa ƙarshen Q1 2026 (Janairu–Maris 2026 kawai). Wannan kashe kuɗi ne (jimilla), wanda ya yi daidai da 4.2% na kasafin ƙarshe.

• 2026 kasafin jimilla (total): ₦7.24 biliyan
• Q1 2026 kashe jimilla (4.2% na kasafin ƙarshe, Janairu–Maris kawai): ₦305.20 miliyan
• Q1 2026 albashi (27.5% na kasafin ƙarshe): ₦34.57 miliyan
• Q1 2026 kuɗin gudanarwa (7.3% na kasafin ƙarshe): ₦56.00 miliyan
• Q1 2026 manyan ayyuka (4.1% na kasafin ƙarshe): ₦178.52 miliyan

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 19, 22, 25, 29
```

## p2_period-04 ok  (3.4s)

**Q:** How much did the Ministry of Lands and Housing spend from January to September 2025?

```
For Min of Lands and Housing, the spent so far (Q1–Q3) is ₦33.20 billion.

*Min of Lands and Housing*:
• Total: spent so far (Q1–Q3) ₦33.20 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## p6_multi_part-01 ok  (2.8s)

**Q:** How much was allocated to the Ministry of Justice in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Justice, the approved budget is ₦6.09 billion.

*Ministry of Justice*:
• Total: approved budget ₦6.09 billion; spent so far (Q1–Q2) ₦902.45 million; share of the revised budget spent 14.8% (Kasafi's calculation)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18; Budget Implementation Report Q2 2026, p. 17
```

## p6_multi_part-02 ok  (3.1s)

**Q:** How much was allocated to the Ministry of Social Welfare & Community Development in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Social Welfare & Community Development, the approved budget is ₦5.11 billion.

*Ministry of Social Welfare & Community Development*:
• Total: approved budget ₦5.11 billion; spent so far (Q1–Q2) ₦365.48 million; share of the revised budget spent 7.1% (Kasafi's calculation)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19; Budget Implementation Report Q2 2026, p. 18
```

## p6_multi_part-03 ok  (3.6s)

**Q:** Nawa aka ware wa Civil Service Commission a 2026, kuma nawa ta kashe zuwa ƙarshen Q2 2026?

```
Ga Civil Service Commission, kasafin da aka amince shi ne ₦403.14 miliyan.

*Civil Service Commission*:
• Jimilla: kasafin da aka amince ₦403.14 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦141.42 miliyan; kason kasafin da aka sabunta da aka kashe 35.1% (lissafin Kasafi)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16; Budget Implementation Report Q2 2026, shafi 15
```

## p3_project-01 ok  (7.8s)

**Q:** How much is budgeted for Procurment of 5n0 peugout 406 saloon for members and secretary in 2026?

```
₦10.00 million is budgeted in 2026 for Procurement of 5N0 Peugout 406 Saloon for Members and Secretary. This is the 2026 approved allocation.

• Procurement of 5N0 Peugout 406 Saloon for Members and Secretary (JUDICIAL SERVICE COMMISSION), 2026 Approved Budget: ₦10.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 62
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-02 ok  (8.0s)

**Q:** How much is budgeted for Renovaton of kebbi house and gwandu house at iktc in 2026?

```
₦150.00 million is budgeted for Renovation of Kebbi House and Gwandu House at IKTC in the 2026 approved budget.

• Renovation of Kebbi House and Gwandu House at IKTC (Ministry of Science and Technology), 2026 Approved Budget: ₦150.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 55
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-03 ok  (7.0s)

**Q:** How much is budgeted for Constraction of idp camps at isa, sabon birni and rabah in 2026?

```
₦800.00 million was budgeted for Construction of IDP Camps at Isa, Sabon Birni and Rabah in the 2026 approved budget.

• Construction of IDP Camps at Isa, Sabon Birni and Rabah (Department for IDPs Matters), 2026 Approved Budget: ₦800.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 51
_Reply *show working* to see the rows and arithmetic._
```

## p4_narrative-01 ok  (8.5s)

**Q:** What does the Budget Implementation Report Q4 2025 say about Revenue Performance, and what reasons does it give?

```
The Q4 2025 report says Sokoto budgeted Total Revenue and other receipts of ₦413.07 billion for 2025. It projected Recurrent Revenue of ₦268.95 billion and Capital Receipts of ₦144.13 billion plus an Opening Balance of ₦113.81 billion carried from 2024. Actual Total Revenue in the fourth quarter was ₦95.24 billion with Capital Receipts of ₦33.85 billion. Statutory Allocation performed at 109.0% while Internally Generated Revenue closed at 42.9%. The report gives reasons for non-performance: restructuring of the Sokoto Geographical Information System with the Ministry of Lands and Housing, review of tax and non-tax rates by the State Ministry of Justice, low sales of chemicals and farm produce, and mining affected by insecurity.

• 2025 budgeted Total Revenue and other receipts (total): ₦413.07 billion
• 2025 Q4 actual Total Revenue generated (total): ₦95.24 billion
• Statutory Allocation YTD performance: 109.0%
• Independent Revenue YTD performance: 42.9%
• Total Revenue YTD (Q1-Q4) vs final budget: ₦365.26 billion (88.4% of final budget)

📄 *Sources:* Budget Implementation Report Q4 2025, p. 5, 9, 10
```

## p4_narrative-02 ok  (9.5s)

**Q:** What does the Sokoto State Budget Implementation Report Q3 2025 say about Revenue Performance, and what reasons does it give?

```
The report says the State budgeted total revenue and other receipts of ₦413.07 billion for 2025. As of Q3 2025, actual total revenue was ₦104.32 billion in Q3 and ₦270.02 billion year-to-date (65.4% of the revised budget). Statutory Allocation performed at 90.2% while Internally Generated Revenue was 30.5%. The report says the noticeable zero performance of some revenue items was due to timing (due in Q4) and administrative changes linked to current reforms.

• 2025 budgeted total revenue and other receipts (total): ₦413.07 billion
• 2025 Q3 actual total revenue (total): ₦104.32 billion
• 2025 YTD actual total revenue Jan-Sept (total): ₦270.02 billion (65.4% of the revised budget)
• Government Share of FAAC YTD (total): ₦234.31 billion (90.2% of the revised budget)
• Independent Revenue YTD (total): ₦14.62 billion (30.5% of the revised budget)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 4, 9, 10
```

## p4_narrative-03 ok  (10.3s)

**Q:** What does the Budget Implementation Report Q2 2026 say about Primary Healthcare Budget Performance, and what reasons does it give?

```
The Budget Implementation Report Q2 2026 says Primary Healthcare was allocated ₦7.21 billion in the 2026 Approved Revised Budget and actual expenditure at end of Q2 2026 (Year-to-Date Q1–Q2) was ₦1.22 billion, representing 16.9% of the allocation. The report describes this as low budget performance. Reasons given are: low related capital receipts draw down, procurement process, late commencement of key capital projects under the sector, and that associated expenditure such as personnel cost and other allowances are documented under the local government’s budget.

• 2026 Approved Revised Budget allocation (total): ₦7.21 billion
• 2026 Performance Year to Date (Q1-Q2) actual expenditure (total): ₦1.22 billion (16.9% of the revised budget)
• 2026 Q2 performance (total): ₦370.04 million
• Reasons cited: low capital receipts draw down, procurement process, late commencement of key capital projects, and personnel/allowances recorded under local government budget

📄 *Sources:* Budget Implementation Report Q2 2026, p. 51, 52, 53
```

## p5_not_published-01 ok  (15.4s)

**Q:** How many staff does the Ministry for Special Duties employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The number of staff and their grade levels for the Ministry for Special Duties isn't published in these documents. The budget shows the Ministry's personnel budget instead: 2026 approved budget (personnel) is ₦12.00 million.

• 2026 approved budget (personnel) for Ministry for Special Duties: ₦12.00 million
• 2026 approved budget (total) for Ministry for Special Duties: ₦829.50 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 19
```

## p5_not_published-02 ok  (11.6s)

**Q:** How many staff does the Government House employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The number of staff and their grade levels for the Government House isn't published in these documents. The documents do publish the Government House personnel budget (2026 approved budget, personnel): ₦444.25 million.

• 2026 approved budget (personnel) for Government House: ₦444.25 million
• 2025 approved budget (personnel) for Government House: ₦353.01 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19; Sokoto State Government 2025 Approved Budget, p. 12
```

