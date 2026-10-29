# Open-question run: held_out.json

10 questions: partial 4, answered 4, not found 2 | median 11.7s

## h01: partial (search, 24.4s)

**Q:** Beyond the Ministry of Environment's direct allocation, if you combine all climate-adaptation and flood-control capital projects scattered across Agriculture, Water Resources, and Emergency Management in the 2026 budget, how does that combined total compare to their actual cumulative releases by Q2 2026?

_Cross-MDA thematic aggregation rather than single-ministry lookup._

```
The evidence shows only whole-ministry capital totals, not climate-adaptation/flood-control projects separately [1][3].

• Ministry of Agriculture & Natural Resource 2026 original budget (capital): ₦14.93 billion [1]
• Ministry of Agriculture & Natural Resource Q1-Q2 2026 actual (capital): ₦4.52 billion (30.3% of the revised budget) [1]
• Ministry of Water Resources 2026 original budget (capital): ₦40.86 billion [3]
• Ministry of Water Resources Q1-Q2 2026 actual (capital): ₦3.46 billion (8.5% of the revised budget) [3]
• State Emergency Management Agency (SEMA) 2026 original budget (capital): ₦1.20 billion [1]
• State Emergency Management Agency (SEMA) Q1-Q2 2026 actual (capital): ₦543.57 million (45.3% of the revised budget) [1]

[1] Budget Implementation Report Q2 2026, page 26
[3] Budget Implementation Report Q2 2026, page 27
```

## h02: answered (search, 7.9s)

**Q:** Since the Ministry of Health already spent 89.4% of its ₦124.41 billion allocation by June 2026, how much supplementary funding was approved for it in the Q2 2026 report?

_False-premise detection: only 10.6% was spent by June; 89.4% is the unspent balance._

```
No supplementary funding was approved for the Ministry of Health in Q2 2026 [3].

• 2026 original budget (total): ₦124.41 billion [3]
• 2026 revised budget (total): ₦116.91 billion [3]
• 2026 year-to-date Q1-Q2 performance (total): ₦12.36 billion (10.6% of the revised budget) [3]

[3] Budget Implementation Report Q2 2026, page 18
```

## h03: not found (search, 7.8s)

**Q:** Looking across both the 2026 approved budget and the Q2 2026 implementation report, which specific ministries had already exhausted more than 50% of their annual overhead allocation by June while recording 0% capital expenditure release, and on which pages do these figures appear?

_Multi-condition filtering across recurrent and capital columns._

```
I couldn't find the answer to that in the documents I have.
```

## h04: answered (lines:share, 10.3s)

**Q:** Idan muka hada duka kudaden da gwamnati ta ware domun farfado da kananan sana'o'in hannu da tallafin kasuwanci a ma'aikatu daban-daban a 2026, shin kudin da aka saki a zahiri zuwa watan Yuni ya kai rabin abin da aka kashe a shekarar 2025?

_Dialectal Hausa, cross-year synthesis, multi-agency summation._

```
Kudin da aka saki ga Hukumar SME Development Agency har zuwa Yuni 2026 ya kai ₦21.57 miliyan [1], yayin da jimillar da aka kashe a 2025 ta kai ₦136.56 miliyan [2], ma'ana rabon ya kai 15.8% (lissafin Kasafi).

🧮 *Yadda aka lissafa* (layukan da aka yi amfani da su):
• Sokoto State SME Development Agency (code 022205100100), 2026 Performance Year to Date (Q1-Q2): ₦21.57 miliyan [1] ↑
• Sokoto State SME Development Agency (code 022205100100), 2025 Performance Year to Date (Q1-Q4): ₦136.56 miliyan [2] ↓
• Kaso (↑ ÷ ↓): 15.8% (lissafin Kasafi)

[1] Budget Implementation Report Q2 2026, shafi 16
[2] Budget Implementation Report Q4 2025, shafi 17
```

## h05: answered (lines:share, 12.3s)

**Q:** If we strip out personnel salaries and routine office overheads across all education-related agencies in the 2026 budget, what exact percentage of the remaining capital development fund is dedicated to Tsangaya and Almajiri school integration versus conventional schooling?

_Sub-sector disaggregation and a percentage after excluding recurrent lines._

```
Excluding personnel and overheads, the 2026 capital development fund is ₦370.00 million for the Agency for Almajiri Matters [1] and ₦34.19 billion for the Ministry for Basic Education [2]; the Tsangaya/Almajiri integration share is 1.1% (Kasafi's calculation), with the remainder for conventional schooling.

🧮 *Working* (the rows used):
• Agency for Almajiri Matters (code 017200700300), 2026 Approved Budget: ₦370.00 million [1] ↑↓
• Ministry for Basic Education (code 051700100100), 2026 Approved Budget: ₦34.19 billion [2] ↓
• Share (↑ ÷ ↓): 1.1% (Kasafi's calculation)

[1] Sokoto State FY 2026 Budget, page 25
[2] Sokoto State FY 2026 Budget, page 27
```

## h06: partial (search, 11.1s)

**Q:** Given that the Ministry of Health spent 10.6% of its ₦124.41 billion allocation by the end of Q2 2026, if the ministry continues at that exact six-month burn rate for the remainder of the year, what will its unspent naira balance be on December 31, 2026, and how does that compare to its 2025 full-year unspent balance?

_Multi-step arithmetic projection with historical retrieval._

```
The 2026 year-end unspent balance is not published in the evidence, while the 2025 full-year unspent balance is published [4].

• 2026 approved budget (total): ₦124.41 billion [1]
• 2025 full-year unspent balance (Q1-Q4 2025): ₦24.36 billion [4]

🧮 Projected Ministry of Health unspent naira balance on December 31, 2026 at double the six-month burn rate isn't published, but I can calculate it from the official figures: 2026 approved budget × (1 − 2 × 10.6%). Reply *Eh* (yes) to calculate.

[1] Sokoto State FY 2026 Budget, page 18
[4] Budget Implementation Report Q4 2025, page 19
```

## h07: partial (search, 27.6s)

**Q:** Idan muka kwatanta actual debt servicing expenditure a Q2 2026 report da kuma combined capital releases na Ministry of Water Resources da Primary Healthcare a wannan lokacin, wanne ya fi yawa kuma da nawa suka bambanta?

_Hausa-English code-switching; debt service vs social-sector comparison._

```
Ba a samo adadin biyan bashin a hujjojin ba, don haka ba a iya kwatantawa ba.

• Ma'aikatar Ruwa Q2 2026 (manyan ayyuka): ₦1.72 biliyan [2]
• Primary Healthcare Q2 2026 (manyan ayyuka): ₦121.81 miliyan [3]
• Ma'aikatar Ruwa Q1-Q2 2026 (manyan ayyuka): ₦3.46 biliyan [2]
• Primary Healthcare Q1-Q2 2026 (manyan ayyuka): ₦729.23 miliyan [3]

🧮 Ba a wallafa Jimillar sakin kuɗin manyan ayyuka na Ma'aikatar Ruwa da Primary Healthcare, Q1-Q2 2026 ba, amma zan iya lissafa shi daga alƙalumman hukuma: (kashe manyan ayyukan Ruwa na Q1-Q2 + kashe manyan ayyukan Primary Healthcare na Q1-Q2). Amsa *Eh* domin in lissafa.

[2] Budget Implementation Report Q2 2026, shafi 27
[3] Budget Implementation Report Q2 2026, shafi 53
```

## h08: answered (lines:list, 17.2s)

**Q:** Rural feeder road construction and rehabilitation often appear under both the Ministry of Works and the Ministry of Rural Development; can you identify any potentially overlapping or similarly named road projects between these two ministries in the 2026 budget and cite their exact budget codes and page numbers?

_Similarity search across separate administrative sections._

```
Rural Roads has allocations of ₦2.25 billion [1] and ₦7.90 billion [1] for CONSTRUCTION / PROVISION OF ROADS and ₦200.00 million [1] for REHABILITATION / REPAIRS - ROADS, while Works has ₦3.00 billion [2] and ₦81.80 million [1] for CONSTRUCTION / PROVISION OF ROADS.

🧮 *Working* (the rows used):
• Department for Rural Roads (code 023405700100) – construction / provision of roads, 2026 Approved Budget: ₦2.25 billion [1]
• (RAMP) (Department for Rural Roads) – construction / provision of roads, 2026 Approved Budget: ₦7.90 billion [1]
• Rehabilitation of existing projects under rural roads (Department for Rural Roads), 2026 Approved Budget: ₦200.00 million [1]
• Ministry of Works (code 023400100100) – construction / provision of roads, 2026 Approved Budget: ₦3.00 billion [2]
• ROAD (30km) (Ministry of Works) – construction / provision of roads, 2026 Approved Budget: ₦81.80 million [1]

[1] Sokoto State FY 2026 Budget, page 56
[2] Sokoto State FY 2026 Budget, page 55
```

## h09: partial (search, 13.7s)

**Q:** What proportion of the 2026 capital budget is scheduled to be financed through domestic and external loans versus recurrent revenue surplus, and according to the Q2 2026 report, which expected capital receipts failed to record any inflows during the first half of the year?

_Deficit-financing structure rather than expenditure lines._

```
The loan-versus-surplus split was not found, but Q1-Q2 2026 shows zero inflows for expected capital grants and capital foreign aid [4].

• 2026 approved budget (capital) for capital expenditure: ₦553.34 billion [1][5].
• 2026 approved budget (total) for CDF receipts: ₦154.89 billion [1].
• Capital grants from FGN 2026 original budget (total): ₦13.42 billion with Q1-Q2 2026 performance zero (0.0% of the revised budget) [4].
• Capital grants from other sources 2026 original budget (total): ₦25.21 billion with Q1-Q2 2026 performance zero (0.0% of the revised budget) [4].
• Capital foreign aid 2026 original budget (total): ₦2.50 billion with Q1-Q2 2026 performance zero (0.0% of the revised budget) [4].

[1] Sokoto State FY 2026 Budget, page 1
[4] Budget Implementation Report Q2 2026, page 14
[5] Sokoto State FY 2026 Budget, page 25
```

## h10: not found (search, 7.8s)

**Q:** Between the 2025 and 2026 budgets, which ministry received the highest percentage increase in its nominal capital allocation, yet recorded one of the lowest percentage rates of actual funds released by the end of Q2 2026?

_Cross-year growth paired with inverse ranking on implementation._

```
I couldn't find the answer to that in the documents I have.
```
