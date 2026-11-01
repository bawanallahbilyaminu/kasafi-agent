# Pattern eval

| pattern | wrong | of |
|---|---|---|
| p1_revenue | 0 | 7 |
| p2_period | 1 | 4 |
| p3_project | 0 | 3 |
| p4_narrative | 2 | 3 |
| p5_not_published | 0 | 2 |
| p6_multi_part | 0 | 3 |

Output checks on every reply (count of replies failing):

| check | failing |
|---|---|
| p7_letters | 0 |
| p8_labels | 0 |
| p9_cut | 0 |
| p11_bullet_first | 0 |

## p1_revenue-01 ok  (25.2s)

**Q:** How much revenue does the Ministry of Innovation and Digital Economy expect to collect in 2026?

```
The Ministry of Innovation and Digital Economy expects to collect ₦100.00 million in revenue in the 2026 approved budget.

• Ministry of Innovation and Digital Economy, 2026 Approved Budget: ₦100.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 7
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-02 ok  (18.7s)

**Q:** How much revenue does the Ministry for Basic Education expect to collect in 2026?

```
The Ministry for Basic Education expects to collect ₦15.78 billion in revenue in the 2026 approved budget. This is the budgeted (allocated) amount, not actual collection.

• Ministry for Basic Education, 2026 Approved Budget: ₦15.78 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-03 ok  (12.5s)

**Q:** How much revenue does the Sokoto State University expect to collect in 2026?

```
Sokoto State University expects to collect ₦315.00 million in revenue in the 2026 approved budget. This is the budgeted (allocated) amount, not actual collection.

• Sokoto State University, 2026 Approved Budget: ₦315.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-04 ok  (16.9s)

**Q:** How much revenue had the College of Nursing Sciences collected by the end of Q1 2026?

```
By the end of Q1 2026, the College of Nursing Sciences had collected ₦13.30 million in revenue. This is the actual amount collected (spent/collected), not the approved budget.

• College of Nursing Sciences, 2026 Performance Year to Date (Q1): ₦13.30 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 12
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-05 ok  (23.9s)

**Q:** How much revenue had the Umaru Ali Shinkafi Polytechnic Sokoto collected by the end of Q1 2026?

```
Umaru Ali Shinkafi Polytechnic Sokoto had collected ₦4.82 million in revenue by the end of Q1 2026. This is actual revenue collected (spent/collected), not the budgeted allocation.

• Umaru Ali Shinkafi Polytechnic Sokoto, 2026 Performance Year to Date (Q1): ₦4.82 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-06 ok  (19.7s)

**Q:** How much does the 2026 budget expect to receive for the Nutrition Response (kyautata Rayuwa)- Recurrent?

```
The 2026 approved budget expects to receive ₦500.00 million for Nutrition Response (kyautata Rayuwa)- Recurrent. This is budgeted revenue (allocation), not actual collection.

• NUTRITION RESPONSE (KYAUTATA RAYUWA)- RECURRENT (Ministry of Humanitarian Affairs & Social Welfare), 2026 Approved Budget: ₦500.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-07 ok  (11.2s)

**Q:** How much does the 2026 budget expect to receive for the Federal Government Tetfund Intervention - Capital?

```
The 2026 approved budget expects to receive ₦4.82 billion for the Federal Government Tetfund Intervention - Capital. This is the budgeted (expected) receipt, not actual spending.

• FEDERAL GOVERNMENT TETFUND INTERVENTION - CAPITAL (Ministry for Higher Education), 2026 Approved Budget: ₦4.82 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p2_period-01 ok  (22.1s)

**Q:** How much had the Ministry for Religious Affairs spent by the end of Q1 2026?

```
By the end of Q1 2026 the Ministry for Religious Affairs had spent ₦1.02 billion. This was total expenditure for January to March 2026 only (5.7% of the 2026 Original Budget). The ministry's 2026 Original Budget (total) was ₦18.05 billion.

• 2026 Original Budget (total): ₦18.05 billion
• 2026 Q1 spent (total, January–March only): ₦1.02 billion (5.7% of the original budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16; Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-02 ok  (5.8s)

**Q:** How much had the Ministry Careers & Special Services spent by the end of Q1 2026?

```
For Ministry Careers & Special Services, the spent so far (Q1–Q1) is ₦1.84 billion.

*Ministry Careers & Special Services*:
• Total: spent so far (Q1–Q1) ₦1.84 billion; spent in Q1 ₦1.84 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-03 ok  (7.5s)

**Q:** Nawa Ministry for Women Affairs ta kashe zuwa ƙarshen Q1 2026?

```
Ga Ministry for Women Affairs, abin da aka kashe zuwa yanzu (Q1–Q1) shi ne ₦305.20 miliyan.

*Ministry for Women Affairs*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q1) ₦305.20 miliyan

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 19
```

## p2_period-04 WRONG: missing 33,198,501,951.04  (10.2s)

**Q:** How much did the Ministry of Lands and Housing spend from January to September 2025?

```
For Min of Lands and Housing, the spent so far (Q1–Q4) is ₦51.92 billion.

*Min of Lands and Housing*:
• Total: spent so far (Q1–Q4) ₦51.92 billion

📄 *Sources:* Budget Implementation Report Q4 2025, p. 18
```

## p6_multi_part-01 ok  (9.3s)

**Q:** How much was allocated to the Ministry of Justice in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Justice, the approved budget is ₦6.09 billion.

*Ministry of Justice*:
• Total: approved budget ₦6.09 billion; spent so far (Q1–Q2) ₦902.45 million; share of the revised budget spent 14.8% (Kasafi's calculation)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18; Budget Implementation Report Q2 2026, p. 17
```

## p6_multi_part-02 ok  (7.2s)

**Q:** How much was allocated to the Ministry of Social Welfare & Community Development in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Social Welfare & Community Development, the approved budget is ₦5.11 billion.

*Ministry of Social Welfare & Community Development*:
• Total: approved budget ₦5.11 billion; spent so far (Q1–Q2) ₦365.48 million; share of the revised budget spent 7.1% (Kasafi's calculation)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19; Budget Implementation Report Q2 2026, p. 18
```

## p6_multi_part-03 ok  (8.6s)

**Q:** Nawa aka ware wa Civil Service Commission a 2026, kuma nawa ta kashe zuwa ƙarshen Q2 2026?

```
Ga Civil Service Commission, kasafin da aka amince shi ne ₦403.14 miliyan.

*Civil Service Commission*:
• Jimilla: kasafin da aka amince ₦403.14 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦141.42 miliyan; kason kasafin da aka sabunta da aka kashe 35.1% (lissafin Kasafi)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16; Budget Implementation Report Q2 2026, shafi 15
```

## p3_project-01 ok  (17.8s)

**Q:** How much is budgeted for Procurment of 5n0 peugout 406 saloon for members and secretary in 2026?

```
₦10.00 million is budgeted in 2026 for Procurement of 5N0 Peugout 406 Saloon for Members and Secretary. This is the 2026 approved allocation.

• Procurement of 5N0 Peugout 406 Saloon for Members and Secretary (JUDICIAL SERVICE COMMISSION), 2026 Approved Budget: ₦10.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 62
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-02 ok  (12.0s)

**Q:** How much is budgeted for Renovaton of kebbi house and gwandu house at iktc in 2026?

```
₦150.00 million is budgeted for Renovation of Kebbi House and Gwandu House at IKTC in the 2026 approved budget.

• Renovation of Kebbi House and Gwandu House at IKTC (Ministry of Science and Technology), 2026 Approved Budget: ₦150.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 55
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-03 ok  (16.0s)

**Q:** How much is budgeted for Constraction of idp camps at isa, sabon birni and rabah in 2026?

```
₦800.00 million is budgeted for Construction of IDP Camps at Isa, Sabon Birni and Rabah in the 2026 approved budget. This is the allocated (budgeted) amount, not spent.

• Construction of IDP Camps at Isa, Sabon Birni and Rabah (Department for IDPs Matters), 2026 Approved Budget: ₦800.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 51
_Reply *show working* to see the rows and arithmetic._
```

## p4_narrative-01 WRONG: missing 413,074,379,419.18  (7.1s)

**Q:** What does the Budget Implementation Report Q4 2025 say about Revenue Performance, and what reasons does it give?

```
The 2025 budget expects ₦144.13 billion from all its main sources (FAAC, independent revenue, aid and grants, and capital receipts including loans). By the end of December 2025, ₦75.52 billion had been received (52.4%). In 2024, ₦211.74 billion was budgeted (revised) and ₦125.97 billion received by September.

Main parts:
• Capital Development Fund (Cdf) Receipts: ₦139.46 billion
• Aid And Grants: ₦4.67 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 8; Budget Implementation Report Q4 2025, p. 13
_Reply *show working* to see the rows and arithmetic._
```

## p4_narrative-02 WRONG: didn't cite bir-2025-q3 p4  (18.9s)

**Q:** What does the Sokoto State Budget Implementation Report Q3 2025 say about Revenue Performance, and what reasons does it give?

```
The report shows total revenue of ₦413.07 billion revised budget with ₦270.02 billion collected January-September 2025 (65.4% of revised budget). Including opening balance, revenue was ₦526.88 billion revised with ₦354.61 billion collected 67.3%. Recurrent revenue performed at 80.9% while independent revenue was 30.5%. The excerpts provided do not contain the report's narrative reasons for revenue performance.

• Total revenue (revised): ₦413.07 billion, YTD Q1-Q3: ₦270.02 billion (65.4% of revised budget) (January-September 2025 only)
• Total revenue including opening balance (revised): ₦526.88 billion, YTD Q1-Q3: ₦354.61 billion (67.3% of revised budget) (January-September 2025 only)
• Recurrent revenue (revised): ₦307.76 billion, YTD Q1-Q3: ₦248.93 billion (80.9% of revised budget) (January-September 2025 only)
• Independent revenue (revised): ₦47.94 billion, YTD Q1-Q3: ₦14.62 billion (30.5% of revised budget) (January-September 2025 only)
• Government share of FAAC (revised): ₦259.82 billion, YTD Q1-Q3: ₦234.31 billion (90.2% of revised budget) (January-September 2025 only)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 9, 10
```

## p4_narrative-03 ok  (21.6s)

**Q:** What does the Budget Implementation Report Q2 2026 say about Primary Healthcare Budget Performance, and what reasons does it give?

```
The 2026 Approved Revised Budget allocated ₦7.21 billion to Primary Healthcare. As at end of Q2 2026 (Q1-Q2), actual spending was ₦1.22 billion, which is 16.9% of the revised budget. The report says this low performance was due to low capital receipts draw down, procurement process, late start of key capital projects, and that personnel costs and allowances are recorded under the local governments’ budget.

• 2026 Revised Budget (total): ₦7.21 billion
• 2026 Performance Year to Date Q1-Q2 (total): ₦1.22 billion (16.9% of the revised budget)
• 2026 Q2 only (total): ₦370.04 million

📄 *Sources:* Budget Implementation Report Q2 2026, p. 51, 52
```

## p5_not_published-01 ok  (16.9s)

**Q:** How many staff does the Ministry for Special Duties employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The number of staff and their grade levels for the Ministry for Special Duties isn't published in these documents. The closest figure printed is the Ministry's personnel budget.

• 2026 approved budget (personnel): ₦12.00 million
• 2026 approved budget (total): ₦829.50 million
• 2025 revised budget (personnel): ₦8.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 19
```

## p5_not_published-02 ok  (10.4s)

**Q:** How many staff does the Government House employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The number of staff the Government House employs and their grade levels isn't published in these documents. The nearest figure the documents do publish is the personnel budget and spending for the Government House.

• 2026 approved budget (personnel): ₦444.25 million
• 2025 approved budget (personnel): ₦353.01 million
• 2025 performance January to September (personnel, part-year only): ₦303.44 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19; Sokoto State Government 2025 Approved Budget, p. 12
```

