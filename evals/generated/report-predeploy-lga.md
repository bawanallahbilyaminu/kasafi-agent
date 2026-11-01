# Generated coverage run

Cases: cases-891743.json (draw seed 891743), form seed 1032

2 cases: wrong 0 (0.0%), of them wrong agency 0 | median 6.3s

| family | wrong | of |
|---|---|---|
| lookup_lga | 0 | 1 |
| rank_lga | 0 | 1 |

| form | wrong | of |
|---|---|---|
| hausa | 0 | 2 |

```
Cost of this run:
  Meta: 12 calls, 13,168 prompt tokens (11,852 cached), 11,987 output tokens -> $0.05
  models together: $0.05 (prices per 1M tokens from settings kasafi_price_*)
  per answer (2 answers): $0.0040, 1.0 model calls
    Meta/plan               1.00 calls  $0.0040  (100%)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0) | identical calls answered from the run's cache: 0
peak memory: 262 MB
```

## rank_lga-01 (hausa) ok (6.6s)

**Q:** Wadanne LGAs 3 ne a Sokoto da suka fi yawan IDPs?

```
Ta ƙaramar hukuma (22), mafi yawa:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-01 (hausa) ok (5.9s)

**Q:** IDPs guda nawa ne a Sokoto South LGA?

```
IOM DTM ta ƙidaya *4,486* 'yan gudun hijira a Sokoto South (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```
