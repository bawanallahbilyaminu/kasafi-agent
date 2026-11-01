# Generated coverage run

Cases: cases-389326.json (draw seed 389326), form seed 1

6 cases: wrong 0 (0.0%), of them wrong agency 0 | median 7.4s

| family | wrong | of |
|---|---|---|
| not_in_data | 0 | 6 |

| form | wrong | of |
|---|---|---|
| code_switched | 0 | 3 |
| followup | 0 | 3 |

```
Cost of this run:
  Baseten: 9 calls, 74,964 prompt tokens (45,312 cached), 5,260 output tokens -> $0.07
  Meta: 11 calls, 73,415 prompt tokens (35,351 cached), 7,576 output tokens -> $0.09
  models together: $0.15 (prices per 1M tokens from settings kasafi_price_*)
  per answer (6 answers): $0.0252, 3.3 model calls
    Meta/read1              0.83 calls  $0.0105  (42%)
    Baseten/read2           1.00 calls  $0.0076  (30%)
    Meta/plan               1.00 calls  $0.0037  (15%)
    Baseten/compose         0.50 calls  $0.0034  (14%)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0) | identical calls answered from the run's cache: 0
peak memory: 382 MB
```

## not_in_data-01 (code_switched) ok (14.4s)

**Q:** How much ne approved budget na Orthopedic Hospital Wamakko for 2028?

```
Babu kasafin kuɗi na 2028 da aka amince da shi a cikin waɗannan takardun. Abin da aka buga shi ne hasashen 2028 a cikin Kasafin 2026 na Orthopedic Hospital Wamakko, jimilla ₦1.28 biliyan. Wannan hasashe ne (out-year estimate), ba approved budget na 2028 ba.

• Orthopedic Hospital Wamakko, 2028 Out-Year Estimate: ₦1.28 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._

Kasafin da nake da su sun rufe 2024–2026; mafi sabo shi ne kasafin 2026 da aka amince da shi.
```

## not_in_data-02 (code_switched) ok (3.5s)

**Q:** Nawa Department for Rural Roads ta spend a Q4 2026?

```
Ba a cikin takardun ba:
• Department for Rural Roads 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Department for Rural Roads 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Department for Rural Roads 2026 kason kasafin da aka sabunta da aka kashe: rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-03 (followup) ok (4.0s)

**Q:** How much did it spend there in Q4 2026?

```
Not in the documents:
• Ministry for Local Government and Chieftancy 2026 spent in Q4: the latest implementation report is Q2 2026
```

## not_in_data-04 (code_switched) ok (14.7s)

**Q:** Nawa ne approved budget na Rural Water and Sanitation Agency for 2028?

```
Babu approved budget na 2028 a cikin takardun da aka bayar. Abin da ake da shi na Rural Water and Sanitation Agency na 2028 hasashen shekara mai zuwa ne (out-year estimate) na ₦62.00 miliyan, ba approved budget ba.

• Rural Water and Sanitation Agency, 2028 Out-Year Estimate: ₦62.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
_Rubuta *nuna lissafi* don ganin layukan da lissafin._

Kasafin da nake da su sun rufe 2024–2026; mafi sabo shi ne kasafin 2026 da aka amince da shi.
```

## not_in_data-05 (followup) ok (4.0s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• State Library Board 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• State Library Board 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-06 (followup) ok (10.7s)

**Q:** How much is its approved budget for 2028?

```
⚠️ I couldn't get the document that fits best (Sokoto State 2028 Approved Budget). The answer below is from other documents I have, not from that one. The budgets I have cover 2024–2026; the newest is the 2026 approved budget.

The documents do not publish a 2028 approved budget for the Agency for Industrial Development. The latest approved budget in the evidence is the 2026 approved budget, and the document gives a 2028 out-year estimate for the Agency of ₦179.34 million.

• 2026 approved budget (total): ₦129.34 million
• 2028 out-year estimate (total): ₦179.34 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```
