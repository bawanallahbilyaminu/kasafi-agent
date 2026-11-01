# Pattern eval

| pattern | wrong | of |
|---|---|---|
| p1_revenue | 0 | 7 |
| p2_period | 0 | 4 |
| p3_project | 1 | 3 |
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

## p1_revenue-01 ok  (11.3s)

**Q:** How much revenue does the Ministry of Innovation and Digital Economy expect to collect in 2026?

```
The Ministry of Innovation and Digital Economy expects to collect ₦100.00 million in 2026, as shown in the 2026 Approved Budget.

• Ministry of Innovation and Digital Economy, 2026 Approved Budget: ₦100.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 7
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-02 ok  (8.5s)

**Q:** How much revenue does the Ministry for Basic Education expect to collect in 2026?

```
The Ministry for Basic Education expects to collect ₦15.78 billion in total revenue in the 2026 approved budget. This is the ministry's own agency total, including capital receipts.

• Ministry for Basic Education, 2026 Approved Budget: ₦15.78 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-03 ok  (7.9s)

**Q:** How much revenue does the Sokoto State University expect to collect in 2026?

```
Sokoto State University expects to collect ₦315.00 million in revenue in the 2026 approved budget. This is the budgeted (allocated) amount.

• Sokoto State University, 2026 Approved Budget: ₦315.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-04 ok  (8.4s)

**Q:** How much revenue had the College of Nursing Sciences collected by the end of Q1 2026?

```
By the end of Q1 2026, the College of Nursing Sciences had collected ₦13.30 million in revenue. This is actual collection, not the approved budget.

• College of Nursing Sciences, 2026 Performance Year to Date (Q1): ₦13.30 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 12
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-05 ok  (9.7s)

**Q:** How much revenue had the Umaru Ali Shinkafi Polytechnic Sokoto collected by the end of Q1 2026?

```
By the end of Q1 2026, Umaru Ali Shinkafi Polytechnic Sokoto had collected ₦4.82 million in revenue (actual collection).

• Umaru Ali Shinkafi Polytechnic Sokoto, 2026 Performance Year to Date (Q1): ₦4.82 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-06 ok  (6.5s)

**Q:** How much does the 2026 budget expect to receive for the Nutrition Response (kyautata Rayuwa)- Recurrent?

```
The 2026 approved budget expects to receive ₦500.00 million for Nutrition Response (Kyautata Rayuwa) - Recurrent. This is the budgeted (expected) revenue, not actual spending.

• NUTRITION RESPONSE (KYAUTATA RAYUWA)- RECURRENT (Ministry of Humanitarian Affairs & Social Welfare), 2026 Approved Budget: ₦500.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-07 ok  (7.5s)

**Q:** How much does the 2026 budget expect to receive for the Federal Government Tetfund Intervention - Capital?

```
The 2026 approved budget expects to receive ₦4.82 billion for Federal Government Tetfund Intervention - Capital. This is the budgeted (allocated) amount, not actual spending.

• FEDERAL GOVERNMENT TETFUND INTERVENTION - CAPITAL (Ministry for Higher Education), 2026 Approved Budget: ₦4.82 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p2_period-01 ok  (3.2s)

**Q:** How much had the Ministry for Religious Affairs spent by the end of Q1 2026?

```
For Ministry for Religious Affairs, the spent so far (Q1–Q1) is ₦1.02 billion.

*Ministry for Religious Affairs*:
• Total: spent so far (Q1–Q1) ₦1.02 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-02 ok  (4.3s)

**Q:** How much had the Ministry Careers & Special Services spent by the end of Q1 2026?

```
For Ministry Careers & Special Services, the spent so far (Q1–Q1) is ₦1.84 billion.

*Ministry Careers & Special Services*:
• Total: spent so far (Q1–Q1) ₦1.84 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-03 ok  (4.1s)

**Q:** Nawa Ministry for Women Affairs ta kashe zuwa ƙarshen Q1 2026?

```
Ga Ministry for Women Affairs, abin da aka kashe zuwa yanzu (Q1–Q1) shi ne ₦305.20 miliyan.

*Ministry for Women Affairs*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q1) ₦305.20 miliyan

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 19
```

## p2_period-04 ok  (3.9s)

**Q:** How much did the Ministry of Lands and Housing spend from January to September 2025?

```
For Min of Lands and Housing, the spent so far (Q1–Q3) is ₦33.20 billion.

*Min of Lands and Housing*:
• Total: spent so far (Q1–Q3) ₦33.20 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## p6_multi_part-01 ok  (4.6s)

**Q:** How much was allocated to the Ministry of Justice in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Justice, the approved budget is ₦6.09 billion.

*Ministry of Justice*:
• Total: approved budget ₦6.09 billion; spent so far (Q1–Q2) ₦902.45 million; share of the revised budget spent 14.8% (Kasafi's calculation)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18; Budget Implementation Report Q2 2026, p. 17
```

## p6_multi_part-02 ok  (3.5s)

**Q:** How much was allocated to the Ministry of Social Welfare & Community Development in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Social Welfare & Community Development, the approved budget is ₦5.11 billion.

*Ministry of Social Welfare & Community Development*:
• Total: approved budget ₦5.11 billion; spent so far (Q1–Q2) ₦365.48 million; share of the revised budget spent 7.1% (Kasafi's calculation)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19; Budget Implementation Report Q2 2026, p. 18
```

## p6_multi_part-03 ok  (4.7s)

**Q:** Nawa aka ware wa Civil Service Commission a 2026, kuma nawa ta kashe zuwa ƙarshen Q2 2026?

```
Ga Civil Service Commission, kasafin da aka amince shi ne ₦403.14 miliyan.

*Civil Service Commission*:
• Jimilla: kasafin da aka amince ₦403.14 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦141.42 miliyan; kason kasafin da aka sabunta da aka kashe 35.1% (lissafin Kasafi)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16; Budget Implementation Report Q2 2026, shafi 15
```

## p3_project-01 WRONG: missing 10,000,000.00  (5.1s)

**Q:** How much is budgeted for Procurment of 5n0 peugout 406 saloon for members and secretary in 2026?

```
Statewide, the 2026 approved budget has PURCHASE OF MOTOR VEHICLES (23010105) ₦25.98 billion. By the end of June 2026, ₦6.29 billion of it had been spent statewide (24.2%, Budget Implementation Report Q2 2026).

Largest:
• SSG'S Office: ₦6.10 billion
• Department for Security Matters: ₦5.50 billion
• Ministry of Agriculture & Natural Resource: ₦4.50 billion
• Ministry for Home Affairs: ₦1.71 billion
• Office of Head of Service: ₦1.50 billion

✓ The agencies' rows add up exactly to the printed statewide totals.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29, 89, 101, 104, 108; Budget Implementation Report Q2 2026, p. 32
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-02 ok  (10.6s)

**Q:** How much is budgeted for Renovaton of kebbi house and gwandu house at iktc in 2026?

```
₦150.00 million was budgeted in 2026 for Renovation of Kebbi House and Gwandu House at IKTC. This is the approved allocation.

• Renovation of Kebbi House and Gwandu House at IKTC (Ministry of Science and Technology), 2026 Approved Budget: ₦150.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 55
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-03 ok  (8.6s)

**Q:** How much is budgeted for Constraction of idp camps at isa, sabon birni and rabah in 2026?

```
₦800.00 million is budgeted for Construction of IDP Camps at Isa, Sabon Birni and Rabah in the 2026 approved budget. This is the allocated (budgeted) amount.

• Construction of IDP Camps at Isa, Sabon Birni and Rabah (Department for IDPs Matters), 2026 Approved Budget: ₦800.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 51
_Reply *show working* to see the rows and arithmetic._
```

## p4_narrative-01 ok  (9.3s)

**Q:** What does the Budget Implementation Report Q4 2025 say about Revenue Performance, and what reasons does it give?

```
The report says Sokoto budgeted Total Revenue of ₦413.07 billion for 2025. In Q4 it generated ₦95.24 billion, and year-to-date (Q1-Q4) ₦365.26 billion which is 88.4% of the Final Budget. Recurrent Revenue year-to-date was ₦310.32 billion (98.9% of final budget), with Government Share of FAAC at 109.0% and Independent Revenue at 42.9%. For the low performance of some revenue items the report gives restructuring of Sokoto Geographical Information System, review of tax and non-tax rates, low sales of chemicals and farm produce, and insecurity affecting mining.

• 2025 budgeted Total Revenue: ₦413.07 billion
• 2025 budgeted Recurrent Revenue: ₦268.95 billion, Capital Receipts: ₦144.13 billion, Opening Balance: ₦113.81 billion
• 2025 Q4 actual Total Revenue: ₦95.24 billion, Capital Receipts: ₦33.85 billion
• YTD (Q1-Q4) Total Revenue: ₦365.26 billion (88.4% of final budget)
• YTD FAAC performance: 109.0%, IGR performance: 42.9%

📄 *Sources:* Budget Implementation Report Q4 2025, p. 5, 9, 10
```

## p4_narrative-02 WRONG: missing 526,882,142,484.39  (10.0s)

**Q:** What does the Sokoto State Budget Implementation Report Q3 2025 say about Revenue Performance, and what reasons does it give?

```
The Sokoto State Budget Implementation Report Q3 2025 says the State budgeted Total Revenue and other receipts of ₦413.07 billion for 2025. It says actual Total Revenue in Q3 was ₦104.32 billion and year-to-date performance was 65.4% of the Revised Budget. For reasons it says Statutory Allocation had 90.2% performance while Internally Generated Revenue had 30.5%, and zero performance for some revenue items was due to timing (due from Q4) and administrative changes linked to current reforms.

• 2025 Total Revenue budgeted (total): ₦413.07 billion
• Recurrent Revenue projected (total): ₦268.95 billion
• Capital Receipts expected (total): ₦144.13 billion
• Opening Balance from 2024 (total): ₦113.81 billion
• Q3 2025 actual Total Revenue (July-September 2025 only) (total): ₦104.32 billion (65.4% of the revised budget year-to-date)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 4, 10
```

## p4_narrative-03 ok  (10.4s)

**Q:** What does the Budget Implementation Report Q2 2026 say about Primary Healthcare Budget Performance, and what reasons does it give?

```
The Primary Healthcare subsector was allocated ₦7.21 billion in the 2026 Approved Revised Budget. As at end Q2 2026 (Q1-Q2), actual spending was ₦1.22 billion, which is 16.9% of the revised budget. The Report calls this low performance and gives reasons: low capital receipts draw down, procurement process, late start of key capital projects, and that some spending like personnel costs is recorded in the local governments' budget.

• 2026 Approved Revised Budget (total): ₦7.21 billion
• Q1-Q2 2026 actual spending (total): ₦1.22 billion (16.9% of revised budget)
• Q2 2026 only actual spending (total): ₦370.04 million

📄 *Sources:* Budget Implementation Report Q2 2026, p. 51, 52
```

## p5_not_published-01 ok  (10.7s)

**Q:** How many staff does the Ministry for Special Duties employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The budget documents do not publish how many staff the Ministry for Special Duties employs or their grade levels. The closest figures they publish are the ministry's personnel budgets and spending.

• 2025 approved budget (personnel): ₦8.00 million
• 2026 approved budget (personnel): ₦12.00 million
• 2025 approved budget (total): ₦423.00 million
• 2026 approved budget (total): ₦829.50 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 12; Sokoto State FY 2026 Budget, p. 16, 19
```

## p5_not_published-02 ok  (9.2s)

**Q:** How many staff does the Government House employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The number of staff and their grade levels for the Government House isn't published in these documents. The documents show the Government House personnel budget instead.

• 2026 approved budget (personnel): ₦444.25 million
• 2025 revised budget (personnel): ₦353.01 million (₦303.44 million spent January–September 2025)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19
```

