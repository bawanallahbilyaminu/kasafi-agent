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
| p8_labels | 1 |
| p9_cut | 0 |
| p11_bullet_first | 0 |

## p1_revenue-01 ok p8_labels (10.8s)

**Q:** How much revenue does the Ministry of Innovation and Digital Economy expect to collect in 2026?

```
The Ministry of Innovation and Digital Economy expects to collect ₦100.00 million in 2026 approved revenue. This is the ministry total including its agencies.

• Ministry of Innovation and Digital Economy, 2026 Approved Budget: ₦100.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 7
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-02 ok  (8.3s)

**Q:** How much revenue does the Ministry for Basic Education expect to collect in 2026?

```
The Ministry for Basic Education expects to collect ₦15.78 billion in revenue in 2026. This is the 2026 approved budget figure for total revenue including capital receipts.

• Ministry for Basic Education, 2026 Approved Budget: ₦15.78 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-03 ok  (7.9s)

**Q:** How much revenue does the Sokoto State University expect to collect in 2026?

```
Sokoto State University expects to collect ₦315.00 million in 2026. This is the 2026 approved budget figure (allocated revenue, not actual collection).

• Sokoto State University, 2026 Approved Budget: ₦315.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-04 ok  (9.3s)

**Q:** How much revenue had the College of Nursing Sciences collected by the end of Q1 2026?

```
By the end of Q1 2026, the College of Nursing Sciences had collected ₦13.30 million in revenue. This is actual revenue collected (spent/performance), not the approved budget.

• College of Nursing Sciences, 2026 Performance Year to Date (Q1): ₦13.30 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 12
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-05 ok  (8.7s)

**Q:** How much revenue had the Umaru Ali Shinkafi Polytechnic Sokoto collected by the end of Q1 2026?

```
By the end of Q1 2026, Umaru Ali Shinkafi Polytechnic Sokoto had collected ₦4.82 million in revenue. This is actual revenue collected (spent/performance), not the approved budget.

• Umaru Ali Shinkafi Polytechnic Sokoto, 2026 Performance Year to Date (Q1): ₦4.82 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-06 ok  (7.3s)

**Q:** How much does the 2026 budget expect to receive for the Nutrition Response (kyautata Rayuwa)- Recurrent?

```
The 2026 budget expects to receive ₦500.00 million for Nutrition Response (Kyautata Rayuwa) - Recurrent. This is the 2026 Approved Budget allocation (budgeted, not spent).

• NUTRITION RESPONSE (KYAUTATA RAYUWA)- RECURRENT (Ministry of Humanitarian Affairs & Social Welfare), 2026 Approved Budget: ₦500.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-07 ok  (10.1s)

**Q:** How much does the 2026 budget expect to receive for the Federal Government Tetfund Intervention - Capital?

```
The 2026 approved budget expects to receive ₦4.82 billion for the Federal Government Tetfund Intervention - Capital. This is the budgeted (expected) amount, not actual receipts.

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

## p2_period-02 ok  (3.6s)

**Q:** How much had the Ministry Careers & Special Services spent by the end of Q1 2026?

```
For Ministry Careers & Special Services, the spent so far (Q1–Q1) is ₦1.84 billion.

*Ministry Careers & Special Services*:
• Total: spent so far (Q1–Q1) ₦1.84 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-03 ok  (12.2s)

**Q:** Nawa Ministry for Women Affairs ta kashe zuwa ƙarshen Q1 2026?

```
Ministry for Women Affairs ta kashe jimilla ₦305.20 miliyan zuwa ƙarshen Q1 2026 (Janairu–Maris 2026 kawai). Wannan kashewar ita ce ainihin abin da aka kashe (actual expenditure), wanda ya yi daidai da 4.2% na kasafin 2026 na asali.

• 2026 Q1 jimilla da aka kashe (Janairu–Maris 2026 kawai, 4.2% na kasafin asali): ₦305.20 miliyan

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 19
```

## p2_period-04 ok  (3.8s)

**Q:** How much did the Ministry of Lands and Housing spend from January to September 2025?

```
For Min of Lands and Housing, the spent so far (Q1–Q3) is ₦33.20 billion.

*Min of Lands and Housing*:
• Total: spent so far (Q1–Q3) ₦33.20 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## p6_multi_part-01 ok  (3.4s)

**Q:** How much was allocated to the Ministry of Justice in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Justice, the approved budget is ₦6.09 billion.

*Ministry of Justice*:
• Total: approved budget ₦6.09 billion; spent so far (Q1–Q2) ₦902.45 million; share of the revised budget spent 14.8% (Kasafi's calculation)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18; Budget Implementation Report Q2 2026, p. 17
```

## p6_multi_part-02 ok  (4.3s)

**Q:** How much was allocated to the Ministry of Social Welfare & Community Development in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Social Welfare & Community Development, the approved budget is ₦5.11 billion.

*Ministry of Social Welfare & Community Development*:
• Total: approved budget ₦5.11 billion; spent so far (Q1–Q2) ₦365.48 million; share of the revised budget spent 7.1% (Kasafi's calculation)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19; Budget Implementation Report Q2 2026, p. 18
```

## p6_multi_part-03 ok  (6.5s)

**Q:** Nawa aka ware wa Civil Service Commission a 2026, kuma nawa ta kashe zuwa ƙarshen Q2 2026?

```
Ga Civil Service Commission, kasafin da aka amince shi ne ₦403.14 miliyan.

*Civil Service Commission*:
• Jimilla: kasafin da aka amince ₦403.14 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦141.42 miliyan; kason kasafin da aka sabunta da aka kashe 35.1% (lissafin Kasafi)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16; Budget Implementation Report Q2 2026, shafi 15
```

## p3_project-01 ok  (14.2s)

**Q:** How much is budgeted for Procurment of 5n0 peugout 406 saloon for members and secretary in 2026?

```
₦10.00 million is budgeted for Procurement of 5N0 Peugout 406 Saloon for Members and Secretary in 2026. This is the 2026 approved allocation.

• Procurement of 5N0 Peugout 406 Saloon for Members and Secretary (JUDICIAL SERVICE COMMISSION), 2026 Approved Budget: ₦10.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 62
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-02 ok  (12.9s)

**Q:** How much is budgeted for Renovaton of kebbi house and gwandu house at iktc in 2026?

```
The 2026 approved budget for Renovation of Kebbi House and Gwandu House at IKTC is ₦150.00 million.

• Renovation of Kebbi House and Gwandu House at IKTC (Ministry of Science and Technology), 2026 Approved Budget: ₦150.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 55
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-03 ok  (11.0s)

**Q:** How much is budgeted for Constraction of idp camps at isa, sabon birni and rabah in 2026?

```
₦800.00 million is budgeted for Construction of IDP Camps at Isa, Sabon Birni and Rabah in the 2026 approved budget. This is the allocated (budgeted) amount.

• Construction of IDP Camps at Isa, Sabon Birni and Rabah (Department for IDPs Matters), 2026 Approved Budget: ₦800.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 51
_Reply *show working* to see the rows and arithmetic._
```

## p4_narrative-01 ok  (12.6s)

**Q:** What does the Budget Implementation Report Q4 2025 say about Revenue Performance, and what reasons does it give?

```
The report says the 2025 budgeted Total Revenue and other receipts was ₦413.07 billion, with Recurrent Revenue projected at ₦268.95 billion and Capital Receipts at ₦144.13 billion plus an Opening Balance of ₦113.81 billion. Actual Total Revenue in Q4 was ₦95.24 billion with Capital Receipts of ₦33.85 billion, and for the year to Q4 (Q1-Q4) total revenue was ₦365.26 billion (88.4% of the final budget). Statutory Allocation performance was 109.0% and Internally Generated Revenue was 42.9%, with independent revenue YTD at ₦20.58 billion (42.9% of the final budget). Reasons given for non-performance were restructuring of the Sokoto Geographical Information System with the Ministry of Lands and Housing, review of tax and non-tax rates by the Ministry of Justice, low sales of chemicals and farm produce, and mining affected by insecurity.

• 2025 budgeted Total Revenue (total): ₦413.07 billion
• Q4 actual Total Revenue (total): ₦95.24 billion
• YTD Total Revenue Q1-Q4 (total): ₦365.26 billion (88.4% of the final budget)
• Independent Revenue YTD (total): ₦20.58 billion (42.9% of the final budget)
• Statutory Allocation performance: 109.0%, IGR performance: 42.9%

📄 *Sources:* Budget Implementation Report Q4 2025, p. 5, 9, 10
```

## p4_narrative-02 WRONG: missing 526,882,142,484.39  (12.0s)

**Q:** What does the Sokoto State Budget Implementation Report Q3 2025 say about Revenue Performance, and what reasons does it give?

```
The Q3 2025 report shows Total Revenue performance Year to Date (Q1-Q3) was ₦270.02 billion, which is 65.4% of the 2025 Revised Budget of ₦413.07 billion. This 65.4% is a Year to Date figure for January–September 2025 only (Q1–Q3), not a full year. The report links fiscal adjustments and downward revisions of sector budgets to shortfalls in revenue performance and reprioritization of government expenditure.

• Total Revenue (total): 2025 Original Budget ₦413.07 billion, 2025 Revised Budget ₦413.07 billion, YTD (Q1-Q3) ₦270.02 billion (65.4% of revised budget)
• Total Revenue (including Opening Balance) (total): YTD (Q1-Q3) ₦354.61 billion (67.3% of revised budget)
• Independent Revenue (total): YTD (Q1-Q3) ₦14.62 billion (30.5% of revised budget)
• Recurrent Revenue (total): YTD (Q1-Q3) ₦248.93 billion (80.9% of revised budget)
• Reasons given: fiscal adjustments necessitated by shortfalls in revenue performance and reprioritization of government expenditure, and fiscal adjustments in line with revenue performance and expenditure prioritization

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 9, 10, 13, 78, 82
```

## p4_narrative-03 ok  (10.5s)

**Q:** What does the Budget Implementation Report Q2 2026 say about Primary Healthcare Budget Performance, and what reasons does it give?

```
The report says Primary Healthcare was allocated ₦7.21 billion in the 2026 Approved Revised Budget. As at end of Q2 2026 (January–June 2026) actual spending was ₦1.22 billion, which is 16.9% of the allocation. The report says this low performance is due to low related capital receipts draw down, procurement process, late commencement of key capital projects, and because some costs like personnel are documented under the local government’s budget.

• 2026 revised budget (total): ₦7.21 billion
• 2026 Performance Year to Date (Q1-Q2) (January–June 2026 only) (total): ₦1.22 billion (16.9% of the revised budget)
• 2026 Q2 Performance (April–June 2026 only) (total): ₦370.04 million

📄 *Sources:* Budget Implementation Report Q2 2026, p. 51, 52
```

## p5_not_published-01 ok  (9.9s)

**Q:** How many staff does the Ministry for Special Duties employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The number of staff and grade levels for the Ministry for Special Duties isn't published in these documents. The documents do show the Ministry's budgets for staff pay (personnel). The 2026 approved budget (personnel) is ₦12.00 million and in 2025 the January to September spending on personnel was ₦7.98 million.

• 2026 approved budget (personnel): ₦12.00 million
• 2025 approved budget (personnel): ₦8.00 million
• 2025 performance January to September (personnel): ₦7.98 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 19
```

## p5_not_published-02 ok  (8.4s)

**Q:** How many staff does the Government House employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The 2026 Sokoto budget documents provided do not publish staff numbers or grade levels for the Government House. They do publish its personnel budget and total spending figures.

• 2026 approved budget (personnel) for Government House: ₦444.25 million
• 2026 approved budget (total) for Government House: ₦18.53 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 19
```

