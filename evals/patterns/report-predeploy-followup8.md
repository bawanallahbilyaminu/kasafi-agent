# Pattern eval

| pattern | wrong | of |
|---|---|---|
| p1_revenue | 0 | 7 |
| p4_narrative | 0 | 1 |

Output checks on every reply (count of replies failing):

| check | failing |
|---|---|
| p7_letters | 0 |
| p8_labels | 0 |
| p9_cut | 0 |
| p11_bullet_first | 0 |

## p1_revenue-01 ok  (9.9s)

**Q:** How much revenue does the Ministry of Innovation and Digital Economy expect to collect in 2026?

```
The Ministry of Innovation and Digital Economy expects to collect ₦100.00 million in revenue in the 2026 approved budget. This is the ministry total figure.

• Ministry of Innovation and Digital Economy, 2026 Approved Budget: ₦100.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 7
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-02 ok  (7.7s)

**Q:** How much revenue does the Ministry for Basic Education expect to collect in 2026?

```
The Ministry for Basic Education expects to collect ₦15.78 billion in 2026 approved revenue (including capital receipts).

• Ministry for Basic Education, 2026 Approved Budget: ₦15.78 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-03 ok  (7.6s)

**Q:** How much revenue does the Sokoto State University expect to collect in 2026?

```
Sokoto State University expects to collect ₦315.00 million in revenue in the 2026 approved budget. This is the budgeted (allocated) amount, not actual collection.

• Sokoto State University, 2026 Approved Budget: ₦315.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 8
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-04 ok  (6.8s)

**Q:** How much revenue had the College of Nursing Sciences collected by the end of Q1 2026?

```
The College of Nursing Sciences had collected ₦13.30 million in revenue by the end of Q1 2026. This is actual collection (spent/performance), not the approved budget.

• College of Nursing Sciences, 2026 Performance Year to Date (Q1): ₦13.30 million

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 12
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-05 ok  (9.6s)

**Q:** How much revenue had the Umaru Ali Shinkafi Polytechnic Sokoto collected by the end of Q1 2026?

```
By the end of Q1 2026 the Umaru Ali Shinkafi Polytechnic Sokoto had collected ₦4.82 million in revenue (Q1 only). Its 2026 original revenue budget was ₦371.00 million.

• 2026 original budget (total revenue): ₦371.00 million
• Q1 2026 collection (January–March 2026 only): ₦4.82 million (1.3% of the original budget)

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 11
```

## p1_revenue-06 ok  (6.8s)

**Q:** How much does the 2026 budget expect to receive for the Nutrition Response (kyautata Rayuwa)- Recurrent?

```
The 2026 approved budget expects to receive ₦500.00 million for Nutrition Response (kyautata Rayuwa)- Recurrent. This is the budgeted (expected) revenue amount, not actual collection.

• NUTRITION RESPONSE (KYAUTATA RAYUWA)- RECURRENT (Ministry of Humanitarian Affairs & Social Welfare), 2026 Approved Budget: ₦500.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p1_revenue-07 ok  (7.1s)

**Q:** How much does the 2026 budget expect to receive for the Federal Government Tetfund Intervention - Capital?

```
The 2026 approved budget expects to receive ₦4.82 billion for Federal Government Tetfund Intervention - Capital. This is the budgeted (expected) amount, not actual spending.

• FEDERAL GOVERNMENT TETFUND INTERVENTION - CAPITAL (Ministry for Higher Education), 2026 Approved Budget: ₦4.82 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 14
_Reply *show working* to see the rows and arithmetic._
```

## p4_narrative-03 ok  (14.8s)

**Q:** What does the Budget Implementation Report Q2 2026 say about Primary Healthcare Budget Performance, and what reasons does it give?

```
The Primary Healthcare subsector was allocated ₦7.21 billion in the 2026 Approved Revised Budget. As at the end of Q2 2026, actual expenditure was ₦1.22 billion, which is 16.9% of the approved revised budget. The report calls this low budget performance.

• 2026 Approved Revised Budget (total) for Primary Healthcare: ₦7.21 billion
• 2026 Performance Year to Date (Q1-Q2) actual expenditure (total): ₦1.22 billion (16.9% of the revised budget)
• Reasons given for low performance: low related capital receipts draw down, procurement process, late commencement of key capital projects under the sector, and associated expenditure are documented under the local government's budget; such as personnel cost and other allowances

📄 *Sources:* Budget Implementation Report Q2 2026, p. 51, 52
```

