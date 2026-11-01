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

## p1_revenue-01 ok  (8.6s)

**Q:** How much revenue does the Ministry of Innovation and Digital Economy expect to collect in 2026?

```
The Ministry of Innovation and Digital Economy expects to collect ₦100.00 million in revenue in the 2026 approved budget. This is the ministry total figure.

• Ministry of Innovation and Digital Economy, 2026 Approved Budget: ₦100.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 7
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-02 ok  (9.1s)

**Q:** How much revenue does the Ministry for Basic Education expect to collect in 2026?

```
The Ministry for Basic Education expects to collect ₦15.78 billion in the 2026 approved budget. This is the ministry unit's Total Revenue figure, budgeted (allocated), not spent.

• Ministry for Basic Education, 2026 Approved Budget: ₦15.78 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-03 ok  (7.4s)

**Q:** How much revenue does the Sokoto State University expect to collect in 2026?

```
Sokoto State University expects to collect ₦315.00 million in approved revenue for 2026.

• Sokoto State University, 2026 Approved Budget: ₦315.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-04 ok  (9.0s)

**Q:** How much revenue had the College of Nursing Sciences collected by the end of Q1 2026?

```
By the end of Q1 2026 the College of Nursing Sciences had collected ₦13.30 million in revenue (27.7% of its budget). This is the actual revenue collected in Q1 2026.

• 2026 Original Budget (total): ₦48.01 million
• 2026 Q1 Performance Year to Date (Q1 only) (total): ₦13.30 million (27.7% of the original budget)

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 12
```

## p1_revenue-05 ok  (8.5s)

**Q:** How much revenue had the Umaru Ali Shinkafi Polytechnic Sokoto collected by the end of Q1 2026?

```
By the end of Q1 2026, Umaru Ali Shinkafi Polytechnic Sokoto had collected ₦4.82 million in revenue (actual collection, not budgeted).

• Umaru Ali Shinkafi Polytechnic Sokoto, 2026 Performance Year to Date (Q1): ₦4.82 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-06 ok  (6.6s)

**Q:** How much does the 2026 budget expect to receive for the Nutrition Response (kyautata Rayuwa)- Recurrent?

```
The 2026 approved budget expects to receive ₦500.00 million for Nutrition Response (Kyautata Rayuwa) - Recurrent. This is budgeted revenue under the Ministry of Humanitarian Affairs & Social Welfare.

• NUTRITION RESPONSE (KYAUTATA RAYUWA)- RECURRENT (Ministry of Humanitarian Affairs & Social Welfare), 2026 Approved Budget: ₦500.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-07 ok  (7.5s)

**Q:** How much does the 2026 budget expect to receive for the Federal Government Tetfund Intervention - Capital?

```
The 2026 approved budget expects to receive ₦4.82 billion for the Federal Government Tetfund Intervention - Capital. This is the budgeted (expected) amount.

• FEDERAL GOVERNMENT TETFUND INTERVENTION - CAPITAL (Ministry for Higher Education), 2026 Approved Budget: ₦4.82 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p2_period-01 ok  (7.9s)

**Q:** How much had the Ministry for Religious Affairs spent by the end of Q1 2026?

```
The Ministry for Religious Affairs had spent ₦1.02 billion by the end of Q1 2026 (January–March 2026 only). This is 5.7% of its 2026 Original Budget of ₦18.05 billion.

• 2026 Original Budget (total): ₦18.05 billion
• 2026 Q1 Performance Year to Date (Q1) (total) (5.7% of the original budget): ₦1.02 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-02 ok  (3.6s)

**Q:** How much had the Ministry Careers & Special Services spent by the end of Q1 2026?

```
For Ministry Careers & Special Services, the spent so far (Q1–Q1) is ₦1.84 billion.

*Ministry Careers & Special Services*:
• Total: spent so far (Q1–Q1) ₦1.84 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-03 ok  (11.5s)

**Q:** Nawa Ministry for Women Affairs ta kashe zuwa ƙarshen Q1 2026?

```
Ministry for Women Affairs ta kashe jimilla ₦305.20 miliyan zuwa ƙarshen Q1 2026 (Janairu–Maris 2026). Wannan kashewar jimilla ce daga kasafin asali na 2026 na ₦7.24 biliyan, wato 4.2% na kasafin asali.

• 2026 kasafin asali (jimilla): ₦7.24 biliyan
• 2026 kashe zuwa Q1 (jimilla, Janairu–Maris 2026): ₦305.20 miliyan (4.2% na kasafin asali)
• ciki har da albashi: ₦34.57 miliyan (27.5% na kasafin asali)
• ciki har da kuɗin gudanarwa: ₦56.00 miliyan (7.3% na kasafin asali)
• ciki har da manyan ayyuka: ₦178.52 miliyan (4.1% na kasafin asali)

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 19, 22, 25, 29
```

## p2_period-04 ok  (5.2s)

**Q:** How much did the Ministry of Lands and Housing spend from January to September 2025?

```
For Min of Lands and Housing, the spent so far (Q1–Q3) is ₦33.20 billion.

*Min of Lands and Housing*:
• Total: spent so far (Q1–Q3) ₦33.20 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## p6_multi_part-01 ok  (4.4s)

**Q:** How much was allocated to the Ministry of Justice in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Justice, the approved budget is ₦6.09 billion.

*Ministry of Justice*:
• Total: approved budget ₦6.09 billion; spent so far (Q1–Q2) ₦902.45 million; share of the revised budget spent 14.8% (Kasafi's calculation)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18; Budget Implementation Report Q2 2026, p. 17
```

## p6_multi_part-02 ok  (4.4s)

**Q:** How much was allocated to the Ministry of Social Welfare & Community Development in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Social Welfare & Community Development, the approved budget is ₦5.11 billion.

*Ministry of Social Welfare & Community Development*:
• Total: approved budget ₦5.11 billion; spent so far (Q1–Q2) ₦365.48 million; share of the revised budget spent 7.1% (Kasafi's calculation)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19; Budget Implementation Report Q2 2026, p. 18
```

## p6_multi_part-03 ok  (3.0s)

**Q:** Nawa aka ware wa Civil Service Commission a 2026, kuma nawa ta kashe zuwa ƙarshen Q2 2026?

```
Ga Civil Service Commission, kasafin da aka amince shi ne ₦403.14 miliyan.

*Civil Service Commission*:
• Jimilla: kasafin da aka amince ₦403.14 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦141.42 miliyan; kason kasafin da aka sabunta da aka kashe 35.1% (lissafin Kasafi)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16; Budget Implementation Report Q2 2026, shafi 15
```

## p3_project-01 ok  (9.0s)

**Q:** How much is budgeted for Procurment of 5n0 peugout 406 saloon for members and secretary in 2026?

```
The 2026 approved budget for Procurement of 5N0 Peugout 406 Saloon for Members and Secretary (Judicial Service Commission) is ₦10.00 million. This is an allocated (budgeted) amount.

• Procurement of 5N0 Peugout 406 Saloon for Members and Secretary (JUDICIAL SERVICE COMMISSION), 2026 Approved Budget: ₦10.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 62
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-02 ok  (7.4s)

**Q:** How much is budgeted for Renovaton of kebbi house and gwandu house at iktc in 2026?

```
₦150.00 million is budgeted for Renovation of Kebbi House and Gwandu House at IKTC in the 2026 approved budget.

• Renovation of Kebbi House and Gwandu House at IKTC (Ministry of Science and Technology), 2026 Approved Budget: ₦150.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 55
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-03 ok  (9.1s)

**Q:** How much is budgeted for Constraction of idp camps at isa, sabon birni and rabah in 2026?

```
₦800.00 million is budgeted for Construction of IDP Camps at Isa, Sabon Birni and Rabah in the 2026 approved budget. This is the allocated (budgeted) amount.

• Construction of IDP Camps at Isa, Sabon Birni and Rabah (Department for IDPs Matters), 2026 Approved Budget: ₦800.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 51
_Reply *show working* to see the rows and arithmetic._
```

## p4_narrative-01 ok  (11.3s)

**Q:** What does the Budget Implementation Report Q4 2025 say about Revenue Performance, and what reasons does it give?

```
The Budget Implementation Report Q4 2025 says Sokoto State budgeted Total Revenue and other receipts of ₦413.07 billion for 2025, with Recurrent Revenue projected at ₦268.95 billion and Capital Receipts expected at ₦144.13 billion with an Opening Balance of ₦113.81 billion. In Q4 actual Total Revenue was ₦95.24 billion and Capital Receipts ₦33.85 billion, Statutory Allocation performed at 109.0% while Internally Generated Revenue closed at 42.9%. For the full year to date, Total Revenue YTD was ₦365.26 billion (88.4% of the final budget). The report gives these reasons for non-performance: restructuring of Sokoto Geographical Information System in alignment with the Ministry of Lands and Housing, review of tax and non-tax rates by other MDAs (reform with Ministry of Justice), low sales of chemicals and farm produce, and mining affected by insecurity.

• 2025 budgeted Total Revenue (budgeted): ₦413.07 billion
• 2025 Q4 actual Total Revenue (spent/collected): ₦95.24 billion
• 2025 YTD Total Revenue (Q1-Q4 collected) (85.4% with opening balance shown in table): ₦449.84 billion

📄 *Sources:* Budget Implementation Report Q4 2025, p. 5, 9, 10
```

## p4_narrative-02 ok  (10.2s)

**Q:** What does the Sokoto State Budget Implementation Report Q3 2025 say about Revenue Performance, and what reasons does it give?

```
The Sokoto State Q3 2025 Budget Implementation Report says the 2025 budgeted Total Revenue and other receipts was ₦413.07 billion. Actual Total Revenue generated in Q3 was ₦104.32 billion and Capital Receipts reflecting ₦6.04 billion Revenue Performance. Year-to-date (Q1-Q3) Total Revenue was ₦270.02 billion which is 65.4% of the revised budget. The report says Statutory Allocation had a performance of 90.2% while Internally Generated Revenue closed with 30.5% and it gives reasons for zero performance as timing (most due from Q4) and administrative changes linked to reforms.

• 2025 budgeted Total Revenue and other receipts (total): ₦413.07 billion
• 2025 Q3 actual Total Revenue (total): ₦104.32 billion
• 2025 Q3 Capital Receipts: ₦6.04 billion
• 2025 YTD (Q1-Q3) Total Revenue (total): ₦270.02 billion (65.4% of revised budget)
• Government Share of FAAC YTD (total): ₦234.31 billion (90.2% of revised budget)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 4, 10, 13
```

## p4_narrative-03 ok  (10.9s)

**Q:** What does the Budget Implementation Report Q2 2026 say about Primary Healthcare Budget Performance, and what reasons does it give?

```
The Primary Healthcare subsector was allocated ₦7.21 billion in the 2026 Approved Revised Budget. As at end of Q2 2026, actual expenditure was ₦1.22 billion, which is 16.9% of the revised budget. The report says this low performance is due to low capital receipts draw down, procurement process, late commencement of key capital projects, and because related personnel cost and allowances are documented under the local governments’ budget.

• 2026 Revised Budget allocation (total): ₦7.21 billion
• Performance Year to Date Q1-Q2 2026 (total): ₦1.22 billion (16.9% of the revised budget)
• Q2 2026 performance alone (total): ₦370.04 million

📄 *Sources:* Budget Implementation Report Q2 2026, p. 51, 52
```

## p5_not_published-01 ok  (11.8s)

**Q:** How many staff does the Ministry for Special Duties employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The budget does not publish staff numbers or grade levels. The Ministry for Special Duties' personnel budget for 2026 is ₦12.00 million and its total approved budget for 2026 is ₦829.50 million. Grade levels and headcount aren't published in these documents.

• 2026 approved budget (personnel): ₦12.00 million
• 2026 approved budget (total): ₦829.50 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 19
```

## p5_not_published-02 ok  (7.2s)

**Q:** How many staff does the Government House employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The number of staff employed by the Government House and their grade levels isn't published in these documents. The nearest figure the 2026 budget prints is the Government House personnel budget for 2026.

• 2026 approved budget (personnel): ₦444.25 million
• 2026 approved budget (total): ₦18.53 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 19
```

