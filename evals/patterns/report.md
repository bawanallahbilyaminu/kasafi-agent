# Pattern eval

| pattern | wrong | of |
|---|---|---|
| p1_revenue | 0 | 7 |
| p2_period | 0 | 4 |
| p3_project | 0 | 3 |
| p4_narrative | 0 | 2 |
| p5_not_published | 0 | 2 |
| p6_multi_part | 0 | 3 |

Output checks on every reply (count of replies failing):

| check | failing |
|---|---|
| p7_letters | 0 |
| p8_labels | 0 |
| p9_cut | 0 |
| p11_bullet_first | 0 |

## p1_revenue-01 ok  (24.3s)

**Q:** How much revenue does the Ministry of Innovation and Digital Economy expect to collect in 2026?

```
The Ministry of Innovation and Digital Economy expects to collect ₦100.00 million in 2026. This is the ministry total approved revenue for 2026 (budgeted, not spent).

• Ministry of Innovation and Digital Economy, 2026 Approved Budget: ₦100.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 7
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-02 ok  (25.1s)

**Q:** How much revenue does the Ministry for Basic Education expect to collect in 2026?

```
The Ministry for Basic Education expects to collect ₦15.78 billion in 2026. This is the 2026 approved budget figure for Total Revenue (including Capital Receipts) for the Ministry as one agency.

• Ministry for Basic Education, 2026 Approved Budget: ₦15.78 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-03 ok  (17.8s)

**Q:** How much revenue does the Sokoto State University expect to collect in 2026?

```
Sokoto State University expects to collect ₦315.00 million in revenue in the 2026 approved budget (budgeted allocation).

• Sokoto State University, 2026 Approved Budget: ₦315.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-04 ok  (17.8s)

**Q:** How much revenue had the College of Nursing Sciences collected by the end of Q1 2026?

```
The College of Nursing Sciences had collected ₦13.30 million in revenue by the end of Q1 2026. This is actual revenue collected (performance), not the approved budget.

• College of Nursing Sciences, 2026 Performance Year to Date (Q1): ₦13.30 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 12
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-05 ok  (21.8s)

**Q:** How much revenue had the Umaru Ali Shinkafi Polytechnic Sokoto collected by the end of Q1 2026?

```
By the end of Q1 2026, Umaru Ali Shinkafi Polytechnic Sokoto had collected ₦4.82 million. This is the actual revenue collected (spent/performance), not the approved budget.

• Umaru Ali Shinkafi Polytechnic Sokoto, 2026 Performance Year to Date (Q1): ₦4.82 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-06 ok  (16.9s)

**Q:** How much does the 2026 budget expect to receive for the Nutrition Response (kyautata Rayuwa)- Recurrent?

```
The 2026 approved budget expects to receive ₦500.00 million for Nutrition Response (kyautata Rayuwa)- Recurrent. This is the budgeted (expected) revenue amount, not actual spending.

• NUTRITION RESPONSE (KYAUTATA RAYUWA)- RECURRENT (Ministry of Humanitarian Affairs & Social Welfare), 2026 Approved Budget: ₦500.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-07 ok  (22.7s)

**Q:** How much does the 2026 budget expect to receive for the Federal Government Tetfund Intervention - Capital?

```
The 2026 approved budget expects to receive ₦4.82 billion for Federal Government Tetfund Intervention - Capital (Ministry for Higher Education). This is an allocated (budgeted) amount, not actual spending.

• FEDERAL GOVERNMENT TETFUND INTERVENTION - CAPITAL (Ministry for Higher Education), 2026 Approved Budget: ₦4.82 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p2_period-01 ok  (21.3s)

**Q:** How much had the Ministry for Religious Affairs spent by the end of Q1 2026?

```
By the end of Q1 2026 the Ministry for Religious Affairs had spent ₦1.02 billion. This is the total (Q1 performance) from the Total Expenditure by Administrative Classification report, which is 5.7% of its 2026 Original Budget.

• 2026 Q1 spent (total, January-March only): ₦1.02 billion (5.7% of the original budget)

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-02 ok  (17.0s)

**Q:** How much had the Ministry Careers & Special Services spent by the end of Q1 2026?

```
For Ministry Careers & Special Services, the spent so far (Q1–Q1) is ₦1.84 billion.

*Ministry Careers & Special Services*:
• Total: spent so far (Q1–Q1) ₦1.84 billion; spent in Q1 ₦1.84 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-03 ok  (26.4s)

**Q:** Nawa Ministry for Women Affairs ta kashe zuwa ƙarshen Q1 2026?

```
Ministry for Women Affairs ta kashe ₦305.20 miliyan a ƙarshen Q1 2026 (Janairu–Maris 2026 kawai). Wannan kashe kuɗi jimilla ne, ya kai 4.2% na kasafin 2026 na asali.

• 2026 kasafin da aka amince (jimilla): ₦7.24 biliyan
• Q1 2026 da aka kashe (jimilla, 4.2% na kasafin na asali): ₦305.20 miliyan
• albashi Q1 2026 (27.5% na kasafin na asali): ₦34.57 miliyan
• kuɗin gudanarwa Q1 2026 (7.3% na kasafin na asali): ₦56.00 miliyan

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 19, 22, 25
```

## p2_period-04 ok  (6.3s)

**Q:** How much did the Ministry of Lands and Housing spend from January to September 2025?

```
For Min of Lands and Housing, the spent so far (Q1–Q3) is ₦33.20 billion.

*Min of Lands and Housing*:
• Total: spent so far (Q1–Q3) ₦33.20 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## p6_multi_part-01 ok  (6.3s)

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

## p6_multi_part-03 ok  (7.2s)

**Q:** Nawa aka ware wa Civil Service Commission a 2026, kuma nawa ta kashe zuwa ƙarshen Q2 2026?

```
Ga Civil Service Commission, kasafin da aka amince shi ne ₦403.14 miliyan.

*Civil Service Commission*:
• Jimilla: kasafin da aka amince ₦403.14 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦141.42 miliyan; kason kasafin da aka sabunta da aka kashe 35.1% (lissafin Kasafi)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16; Budget Implementation Report Q2 2026, shafi 15
```

## p3_project-01 ok  (28.7s)

**Q:** How much is budgeted for Procurment of 5n0 peugout 406 saloon for members and secretary in 2026?

```
The 2026 approved budget for Procurement of 5 No Peugeot 406 Saloon for Members and Secretary (Judicial Service Commission) is ₦10.00 million (allocated/budgeted).

• Procurement of 5N0 Peugout 406 Saloon for Members and Secretary (JUDICIAL SERVICE COMMISSION), 2026 Approved Budget: ₦10.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 62
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-02 ok  (25.2s)

**Q:** How much is budgeted for Renovaton of kebbi house and gwandu house at iktc in 2026?

```
₦150.00 million is budgeted for Renovation of Kebbi House and Gwandu House at IKTC in the 2026 approved budget.

• Renovation of Kebbi House and Gwandu House at IKTC (Ministry of Science and Technology), 2026 Approved Budget: ₦150.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 55
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-03 ok  (34.4s)

**Q:** How much is budgeted for Constraction of idp camps at isa, sabon birni and rabah in 2026?

```
₦800.00 million was budgeted for Construction of IDP Camps at Isa, Sabon Birni and Rabah in the 2026 approved budget. This is the allocated (budgeted) amount, not spending.

• Construction of IDP Camps at Isa, Sabon Birni and Rabah (Department for IDPs Matters), 2026 Approved Budget: ₦800.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 51
_Reply *show working* to see the rows and arithmetic._
```

## p4_narrative-01 ok  (34.3s)

**Q:** What does the Sokoto State Budget Implementation Report Q3 2025 say about education expenditure economic classification? What reasons does it give?

```
The report lists Table 29: Basic Education Expenditure by Economic Classification as part of its contents, and publishes the figures for Basic Education by economic classification. The published tables do not include any written reasons or explanation for the performance.

• 2025 original budget (total): ₦9.61 billion
• 2025 revised budget (total): ₦6.61 billion
• Q1-Q3 2025 spending (total): ₦1.08 billion (16.3% of the revised budget)
• 2025 revised budget (personnel): ₦463.91 million
• 2025 revised budget (capital): ₦5.64 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 3, 84
```

## p4_narrative-02 ok  (24.9s)

**Q:** What does the Budget Implementation Report Q4 2025 say about education performance overview reports? What reasons does it give?

```
The excerpts show the tables for education performance but do not include the written overview text or the reasons it gives. 2025 Education (sector total, programme classification) Year to Date (Q1-Q4): ₦55.32 billion (62.8% of the final budget). 2025 Education (functional classification 709 EDUCATION) Year to Date (Q1-Q4): ₦54.71 billion (63.4% of the final budget).

• 2025 Education sector total (programme) approved: Original Budget ₦90.00 billion, Final Budget ₦88.09 billion, Year to Date (Q1-Q4) ₦55.32 billion (62.8% of the final budget)
• 2025 Education 709 EDUCATION (functional) approved: Original Budget ₦88.59 billion, Final Budget ₦86.35 billion, Year to Date (Q1-Q4) ₦54.71 billion (63.4% of the final budget)
• 2025 Basic Education (Ministry of Education) Year to Date (Q1-Q4): ₦4.94 billion (48.9% of the final budget)

📄 *Sources:* Budget Implementation Report Q4 2025, p. 2, 38, 47, 57
```

## p5_not_published-01 ok  (25.0s)

**Q:** How many staff does the Ministry for Higher Education employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The number of staff and their grade levels isn’t published in these documents. The budget gives money for staff instead. The Ministry for Higher Education’s 2026 approved personnel budget is ₦6.72 billion, and its 2026 total approved budget is ₦33.99 billion.

• 2026 approved budget (personnel): ₦6.72 billion
• 2026 approved budget (total): ₦33.99 billion
• 2026 personnel spending Q1-Q2 (January-June only): ₦4.25 billion (63.3% of the revised budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 21; Budget Implementation Report Q2 2026, p. 21
```

## p5_not_published-02 ok  (13.5s)

**Q:** How many staff does the Ministry of Water Resources employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The number of staff and grade levels for the Ministry of Water Resources isn't published in these documents. The closest figure printed is its personnel budget (albashi). In the 2026 approved budget the Ministry of Water Resources has a personnel allocation of ₦1.03 billion.

• 2026 approved budget (personnel): ₦1.03 billion
• 2025 performance January to September (personnel): ₦732.77 million
• 2026 approved budget (total): ₦44.99 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 20
```

