# Generated coverage run

Cases: cases-389326.json (draw seed 389326), form seed 1

6 cases: wrong 1 (16.7%), of them wrong agency 0 | median 9.4s

| family | wrong | of |
|---|---|---|
| not_in_data | 1 | 6 |

| form | wrong | of |
|---|---|---|
| code_switched | 1 | 3 |
| followup | 0 | 3 |

```
Cost of this run:
  Baseten: 9 calls, 73,796 prompt tokens (36,096 cached), 6,761 output tokens -> $0.08
  Meta: 12 calls, 80,931 prompt tokens (56,697 cached), 9,054 output tokens -> $0.08
  models together: $0.16 (prices per 1M tokens from settings kasafi_price_*)
  per answer (6 answers): $0.0264, 3.5 model calls
    Meta/read1              1.00 calls  $0.0088  (33%)
    Baseten/read2           1.00 calls  $0.0082  (31%)
    Baseten/compose         0.50 calls  $0.0054  (20%)
    Meta/plan               1.00 calls  $0.0040  (15%)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0) | identical calls answered from the run's cache: 0
peak memory: 380 MB
```

## not_in_data-01 (code_switched) WRONG: no mention of what exists (2024–2026) (15.4s)

**Q:** How much ne approved budget na Orthopedic Hospital Wamakko for 2028?

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• Orthopedic Hospital Wamakko, 2026 Approved Budget: ₦1.27 biliyan [1]
• Orthopedic Hospital Wamakko (manyan ayyuka), 2026 Approved Budget: ₦590.00 miliyan [2]
• Orthopedic Hospital Wamakko (albashi), 2026 Approved Budget: ₦630.72 miliyan [3]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 21, 27
```

## not_in_data-02 (code_switched) ok (3.7s)

**Q:** Nawa Department for Rural Roads ta spend a Q4 2026?

```
Ba a cikin takardun ba:
• Department for Rural Roads 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-03 (followup) ok (4.7s)

**Q:** How much did it spend there in Q4 2026?

```
Not in the documents:
• Ministry for Local Government and Chieftancy 2026 spent in Q4: the latest implementation report is Q2 2026
• Ministry for Local Government and Chieftancy 2026 spent so far (Q1–Q4): the latest implementation report is Q2 2026
```

## not_in_data-04 (code_switched) ok (14.0s)

**Q:** Nawa ne approved budget na Rural Water and Sanitation Agency for 2028?

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• Rural Water and Sanitation Agency, 2026 Approved Budget: ₦803.00 miliyan [1]
• Rural Water and Sanitation Agency (kuɗin gudanarwa), 2028 Out-Year Estimate: ₦62.00 miliyan [2]
• Rural Water and Sanitation Agency (manyan ayyuka), 2028 Out-Year Estimate: 0.00 [3]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 23, 26
```

## not_in_data-05 (followup) ok (4.8s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• State Library Board 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
• State Library Board 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-06 (followup) ok (16.7s)

**Q:** How much is its approved budget for 2028?

```
⚠️ I couldn't get the document that fits best (Sokoto State Government 2028 Approved Budget). The answer below is from other documents I have, not from that one. The budgets I have cover 2024–2026; the newest is the 2026 approved budget.

The approved budget for 2028 for the Agency for Industrial Development is not published in these documents. The 2026 Approved Budget only prints a 2028 Out-Year Estimate for the agency of ₦179.34 million, which is an estimate, not an approved budget.

• 2028 Out-Year Estimate (total) for Agency for Industrial Development: ₦179.34 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17
```
