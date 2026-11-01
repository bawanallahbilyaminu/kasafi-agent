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

## p1_revenue-01 ok  (9.5s)

**Q:** How much revenue does the Ministry of Innovation and Digital Economy expect to collect in 2026?

```
The Ministry of Innovation and Digital Economy expects to collect ₦100.00 million in 2026. This is the 2026 approved budgeted revenue for the Ministry.

• Ministry of Innovation and Digital Economy, 2026 Approved Budget: ₦100.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 7
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-02 ok  (9.9s)

**Q:** How much revenue does the Ministry for Basic Education expect to collect in 2026?

```
The Ministry for Basic Education expects to collect ₦15.78 billion in total revenue in the 2026 approved budget.

• Ministry for Basic Education, 2026 Approved Budget: ₦15.78 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-03 ok  (7.8s)

**Q:** How much revenue does the Sokoto State University expect to collect in 2026?

```
Sokoto State University expects to collect ₦315.00 million in revenue in the 2026 approved budget. This is the budgeted (allocated) expectation, not actual collection.

• Sokoto State University, 2026 Approved Budget: ₦315.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-04 ok  (9.0s)

**Q:** How much revenue had the College of Nursing Sciences collected by the end of Q1 2026?

```
The College of Nursing Sciences had collected ₦13.30 million in revenue by the end of Q1 2026. This is actual collection (spent/collected), not the approved budget.

• College of Nursing Sciences, 2026 Performance Year to Date (Q1): ₦13.30 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 12
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-05 ok  (8.4s)

**Q:** How much revenue had the Umaru Ali Shinkafi Polytechnic Sokoto collected by the end of Q1 2026?

```
By the end of Q1 2026, Umaru Ali Shinkafi Polytechnic Sokoto had collected ₦4.82 million in revenue (actual collection).

• Umaru Ali Shinkafi Polytechnic Sokoto, 2026 Performance Year to Date (Q1): ₦4.82 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-06 ok  (5.6s)

**Q:** How much does the 2026 budget expect to receive for the Nutrition Response (kyautata Rayuwa)- Recurrent?

```
The 2026 approved budget expects to receive ₦500.00 million for Nutrition Response (Kyautata Rayuwa) - Recurrent. This is the budgeted (allocated) revenue expectation.

• NUTRITION RESPONSE (KYAUTATA RAYUWA)- RECURRENT (Ministry of Humanitarian Affairs & Social Welfare), 2026 Approved Budget: ₦500.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-07 ok  (7.9s)

**Q:** How much does the 2026 budget expect to receive for the Federal Government Tetfund Intervention - Capital?

```
The 2026 approved budget expects to receive ₦4.82 billion for Federal Government Tetfund Intervention - Capital. This is the budgeted (expected) receipt, not actual spending.

• FEDERAL GOVERNMENT TETFUND INTERVENTION - CAPITAL (Ministry for Higher Education), 2026 Approved Budget: ₦4.82 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p2_period-01 ok  (3.9s)

**Q:** How much had the Ministry for Religious Affairs spent by the end of Q1 2026?

```
For Ministry for Religious Affairs, the spent so far (Q1–Q1) is ₦1.02 billion.

*Ministry for Religious Affairs*:
• Total: spent so far (Q1–Q1) ₦1.02 billion; spent in Q1 ₦1.02 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-02 ok  (3.9s)

**Q:** How much had the Ministry Careers & Special Services spent by the end of Q1 2026?

```
For Ministry Careers & Special Services, the spent so far (Q1–Q1) is ₦1.84 billion.

*Ministry Careers & Special Services*:
• Total: spent so far (Q1–Q1) ₦1.84 billion; spent in Q1 ₦1.84 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 17
```

## p2_period-03 ok  (4.3s)

**Q:** Nawa Ministry for Women Affairs ta kashe zuwa ƙarshen Q1 2026?

```
Ga Ministry for Women Affairs, abin da aka kashe zuwa yanzu (Q1–Q1) shi ne ₦305.20 miliyan.

*Ministry for Women Affairs*:
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q1) ₦305.20 miliyan

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 19
```

## p2_period-04 ok  (4.3s)

**Q:** How much did the Ministry of Lands and Housing spend from January to September 2025?

```
For Min of Lands and Housing, the spent so far (Q1–Q3) is ₦33.20 billion.

*Min of Lands and Housing*:
• Total: spent so far (Q1–Q3) ₦33.20 billion

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 18
```

## p6_multi_part-01 ok  (5.5s)

**Q:** How much was allocated to the Ministry of Justice in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Justice, the approved budget is ₦6.09 billion.

*Ministry of Justice*:
• Total: approved budget ₦6.09 billion; spent so far (Q1–Q2) ₦902.45 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18; Budget Implementation Report Q2 2026, p. 17
```

## p6_multi_part-02 ok  (3.5s)

**Q:** How much was allocated to the Ministry of Social Welfare & Community Development in 2026, and how much had it spent by the end of Q2 2026?

```
For Ministry of Social Welfare & Community Development, the approved budget is ₦5.11 billion.

*Ministry of Social Welfare & Community Development*:
• Total: approved budget ₦5.11 billion; spent so far (Q1–Q2) ₦365.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19; Budget Implementation Report Q2 2026, p. 18
```

## p6_multi_part-03 ok  (3.3s)

**Q:** Nawa aka ware wa Civil Service Commission a 2026, kuma nawa ta kashe zuwa ƙarshen Q2 2026?

```
Ga Civil Service Commission, kasafin da aka amince shi ne ₦403.14 miliyan.

*Civil Service Commission*:
• Jimilla: kasafin da aka amince ₦403.14 miliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦141.42 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16; Budget Implementation Report Q2 2026, shafi 15
```

## p3_project-01 ok  (10.4s)

**Q:** How much is budgeted for Procurment of 5n0 peugout 406 saloon for members and secretary in 2026?

```
₦10.00 million is budgeted for Procurement of 5N0 Peugout 406 Saloon for Members and Secretary in the 2026 approved budget.

• Procurement of 5N0 Peugout 406 Saloon for Members and Secretary (JUDICIAL SERVICE COMMISSION), 2026 Approved Budget: ₦10.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 62
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-02 ok  (7.3s)

**Q:** How much is budgeted for Renovaton of kebbi house and gwandu house at iktc in 2026?

```
₦150.00 million is budgeted for Renovation of Kebbi House and Gwandu House at IKTC in the 2026 approved budget.

• Renovation of Kebbi House and Gwandu House at IKTC (Ministry of Science and Technology), 2026 Approved Budget: ₦150.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 55
_Reply *show working* to see the rows and arithmetic._
```

## p3_project-03 ok  (9.6s)

**Q:** How much is budgeted for Constraction of idp camps at isa, sabon birni and rabah in 2026?

```
The 2026 approved budget for Construction of IDP Camps at Isa, Sabon Birni and Rabah is ₦800.00 million. This is the allocated (budgeted) amount.

• Construction of IDP Camps at Isa, Sabon Birni and Rabah (Department for IDPs Matters), 2026 Approved Budget: ₦800.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 51
_Reply *show working* to see the rows and arithmetic._
```

## p4_narrative-01 ok  (21.3s)

**Q:** What does the Budget Implementation Report Q4 2025 say about Revenue Performance, and what reasons does it give?

```
The Budget Implementation Report Q4 2025 says Sokoto State budgeted Total Revenue and other receipts of ₦413.07 billion for 2025. It says actual Total Revenue in Q4 2025 was ₦95.24 billion, with Year-to-Date (Q1-Q4) performance of ₦365.26 billion (88.4% of final budget). It says Statutory Allocation (Government Share of FAAC) performed at 109.0% while Independent Revenue (IGR) closed at 42.9%. The report gives reasons for non-performance of some revenue items as restructuring of Sokoto Geographical Information System, review of tax and non-tax rates, low sales of chemicals and farm produce, and insecurity affecting mining.

• 2025 approved Total Revenue (total): ₦413.07 billion
• 2025 Q4 Total Revenue actual: ₦95.24 billion
• 2025 YTD Total Revenue (Q1-Q4): ₦365.26 billion (88.4% of final budget)
• Government Share of FAAC YTD performance: 109.0%
• Independent Revenue YTD performance: 42.9%

📄 *Sources:* Budget Implementation Report Q4 2025, p. 5, 9, 10
```

## p4_narrative-02 ok  (19.0s)

**Q:** What does the Sokoto State Budget Implementation Report Q3 2025 say about Revenue Performance, and what reasons does it give?

```
The Q3 2025 report says Sokoto State budgeted Total Revenue of ₦413.07 billion for 2025. It reports actual Total Revenue of ₦104.32 billion in Q3 and Year to Date (Q1-Q3) of ₦270.02 billion (65.4% of revised budget). Statutory Allocation performance was 90.2% and Internally Generated Revenue was 30.5%. The reasons given for revenue performance, including zero performance on some items, were timing (due from Q4) and administrative changes linked to current reforms.

• 2025 budgeted Total Revenue (total): ₦413.07 billion
• 2025 Q3 actual Total Revenue (total): ₦104.32 billion
• 2025 YTD (Q1-Q3) Total Revenue (total): ₦270.02 billion (65.4% of revised budget)
• Statutory Allocation YTD performance: 90.2%
• IGR YTD performance: 30.5%

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 4, 9, 10
```

## p4_narrative-03 WRONG: none of 7,210,210,444.94, 1,221,243,045.30  (28.3s)

**Q:** What does the Budget Implementation Report Q2 2026 say about Primary Healthcare Budget Performance, and what reasons does it give?

```
I found documents about your question, but couldn't verify the figures. Please check these sources:

[1] Budget Implementation Report Q2 2026, page 51
[4] Budget Implementation Report Q2 2026, page 52

Not found in these documents: Reasons for Primary Healthcare performance in report.
```

## p5_not_published-01 ok  (8.4s)

**Q:** How many staff does the Ministry for Special Duties employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The number of staff and their grade levels for the Ministry for Special Duties isn't published in these documents. The budget does show money for staff: the Ministry's 2026 approved budget for personnel is ₦12.00 million, and its total approved budget is ₦829.50 million.

• 2026 approved budget (personnel): ₦12.00 million
• 2026 approved budget (total): ₦829.50 million
• 2025 revised budget (personnel): ₦8.00 million
• 2025 January–September performance (personnel): ₦7.98 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 4, 16, 19
```

## p5_not_published-02 ok  (7.1s)

**Q:** How many staff does the Government House employ, and on which grade levels?

```
_Assumption: used the latest budget, 2026._

The number of staff employed by the Government House and their grade levels isn't published in these documents. The documents show money budgeted for personnel. For example, the 2026 approved budget for personnel for Government House is ₦444.25 million.

• 2026 approved budget (personnel): ₦444.25 million
• 2025 revised budget (personnel): ₦353.01 million
• 2024 full year actuals (personnel): ₦276.23 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19
```

