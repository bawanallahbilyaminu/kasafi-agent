# Generated coverage run

Cases: cases-44377.json (draw seed 44377), form seed 1

6 cases: wrong 0 (0.0%), of them wrong agency 0 | median 3.6s

| family | wrong | of |
|---|---|---|
| false_premise | 0 | 6 |

| form | wrong | of |
|---|---|---|
| followup | 0 | 1 |
| hausa | 0 | 1 |
| informal | 0 | 2 |
| typo | 0 | 2 |

```
Cost of this run:
  Baseten: 2 calls, 20,282 prompt tokens (16,896 cached), 920 output tokens -> $0.01
  Meta: 9 calls, 41,881 prompt tokens (33,702 cached), 5,822 output tokens -> $0.04
  models together: $0.05 (prices per 1M tokens from settings kasafi_price_*)
  per answer (6 answers): $0.0084, 1.8 model calls
    Meta/plan               1.00 calls  $0.0032  (38%)
    Meta/read1              0.17 calls  $0.0017  (21%)
    Meta/completeness       0.33 calls  $0.0017  (20%)
    Baseten/compose         0.17 calls  $0.0013  (16%)
    Baseten/read2           0.17 calls  $0.0004  (5%)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0) | identical calls answered from the run's cache: 0
peak memory: 386 MB
```

## false_premise-01 (informal) ok (3.6s)

**Q:** Why'd the Ministry of Budget and Economic Planning's approved budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Budget and Economic Planning, the 2025 approved budget is ₦4.03 billion.

*Ministry of Budget and Economic Planning*:
• Total: 2025 approved budget ₦4.03 billion; 2026 approved budget ₦5.32 billion; change +₦1.29 billion (+32.0%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```

## false_premise-02 (typo) ok (3.7s)

**Q:** Why did teh Ministry for Special Duties's aproved budget fall form 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry for Special Duties, the 2025 approved budget (salaries) is ₦8.00 million.

*Ministry for Special Duties*:
• Personnel (salaries): 2025 approved budget ₦8.00 million; 2026 approved budget ₦12.00 million; change +₦4.00 million (+50.0%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦155.00 million; 2026 approved budget ₦195.50 million; change +₦40.50 million (+26.1%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦260.00 million; 2026 approved budget ₦622.00 million; change +₦362.00 million (+139.2%) (Kasafi's calculation)
• Total: 2025 approved budget ₦423.00 million; 2026 approved budget ₦829.50 million; change +₦406.50 million (+96.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 12, 14, 15; Sokoto State FY 2026 Budget, p. 16, 19, 22, 25
```

## false_premise-03 (informal) ok (3.0s)

**Q:** Why did Sokoto State Independent Electoral Commission's approved budget go up from 2025 to 2026?

```
It didn't rise: the approved budget fell from 2025 to 2026, so there is no rise to explain.
For Sokoto State Independent Electoral Commission, the 2025 approved budget is ₦529.14 million.

*Sokoto State Independent Electoral Commission*:
• Total: 2025 approved budget ₦529.14 million; 2026 approved budget ₦460.48 million; change -₦68.67 million (-13.0%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## false_premise-04 (hausa) ok (21.6s)

**Q:** Me yasa approved budget na Civil Service Commission ya sauka daga 2025 zuwa 2026?

```
Approved budget na Civil Service Commission bai sauka ba daga 2025 zuwa 2026. A 2025 approved budget ne ₦254.99 miliyan, a 2026 approved budget ne ₦403.14 miliyan. Don haka ya ƙaru, ba raguwa ba (lissafin Kasafi).

• Civil Service Commission, 2025 Approved Budget: ₦254.99 miliyan
• Civil Service Commission, 2026 Approved Budget: ₦403.14 miliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## false_premise-05 (followup) ok (3.5s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Health, the 2025 approved budget is ₦52.18 billion.

*Ministry of Health*:
• Total: 2025 approved budget ₦52.18 billion; 2026 approved budget ₦124.41 billion; change +₦72.23 billion (+138.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## false_premise-06 (typo) ok (3.4s)

**Q:** Why did the Ministry of Innovation and Digital Economy's approved budet fall form 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
For Ministry of Innovation and Digital Economy, the 2025 approved budget is ₦1.35 billion.

*Ministry of Innovation and Digital Economy*:
• Total: 2025 approved budget ₦1.35 billion; 2026 approved budget ₦3.59 billion; change +₦2.24 billion (+166.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 17
```
