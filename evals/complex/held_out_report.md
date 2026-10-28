# Open-question run: held_out.json

10 questions: partial 6, answered 2, not found 2 | median 11.6s

## h01: partial (lines:compare, 14.4s)

**Q:** Beyond the Ministry of Environment's direct allocation, if you combine all climate-adaptation and flood-control capital projects scattered across Agriculture, Water Resources, and Emergency Management in the 2026 budget, how does that combined total compare to their actual cumulative releases by Q2 2026?

_Cross-MDA thematic aggregation rather than single-ministry lookup._

```
The only sector-specific total shown is State Emergency Management Agency (SEMA) capital of ₦1.20 billion [1] with Q1-Q2 releases of ₦543.57 million [2], a change of ₦656.43 million 120.8% (Kasafi's calculation); no separate climate-adaptation and flood-control project lines for Agriculture, Water Resources or Emergency Management are shown.

🧮 *Working* (the rows used):
• State Emergency Management Agency (SEMA) (code 011100800100), 2026 Approved Budget: ₦1.20 billion [1]
• State Emergency Management Agency (SEMA) (code 011100800100), 2026 Performance Year to Date (Q1-Q2): ₦543.57 million [2]
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Difference (2026 Approved Budget vs 2026 Performance Year to Date (Q1-Q2)): +₦656.43 million (+120.8%) (Kasafi's calculation)
• Not found: Agriculture and Water Resources climate-adaptation and flood-control capital projects; specific flood-control project breakdown within SEMA capital

[1] Sokoto State FY 2026 Budget, page 25
[2] Budget Implementation Report Q2 2026, page 26
```

## h02: answered (search, 7.4s)

**Q:** Since the Ministry of Health already spent 89.4% of its ₦124.41 billion allocation by June 2026, how much supplementary funding was approved for it in the Q2 2026 report?

_False-premise detection: only 10.6% was spent by June; 89.4% is the unspent balance._

```
No supplementary funding was approved; the Q2 2026 report shows a lower revised budget and 10.6% spending [4].

• 2026 original budget (total): ₦124.41 billion [1][4]
• 2026 revised budget (total): ₦116.91 billion [4]
• 2026 Q1-Q2 performance (total): ₦12.36 billion (10.6% of the revised budget) [4]

[1] Sokoto State FY 2026 Budget, page 18
[4] Budget Implementation Report Q2 2026, page 18
```

## h03: not found (search, 6.5s)

**Q:** Looking across both the 2026 approved budget and the Q2 2026 implementation report, which specific ministries had already exhausted more than 50% of their annual overhead allocation by June while recording 0% capital expenditure release, and on which pages do these figures appear?

_Multi-condition filtering across recurrent and capital columns._

```
I couldn't find the answer to that in the documents I have.
```

## h04: answered (lines:share, 11.6s)

**Q:** Idan muka hada duka kudaden da gwamnati ta ware domun farfado da kananan sana'o'in hannu da tallafin kasuwanci a ma'aikatu daban-daban a 2026, shin kudin da aka saki a zahiri zuwa watan Yuni ya kai rabin abin da aka kashe a shekarar 2025?

_Dialectal Hausa, cross-year synthesis, multi-agency summation._

```
Kudin da aka saki ga Hukumar SME zuwa watan Yuni 2026 ya kai ₦21.57 miliyan [1], yayin da aka kashe ₦136.56 miliyan [2] a 2025, don haka bai kai rabi ba domin ya kai 15.8% (Kasafi's calculation).

🧮 *Yadda aka lissafa* (layukan da aka yi amfani da su):
• Sokoto State SME Development Agency (code 022205100100), 2026 Performance Year to Date (Q1-Q2): ₦21.57 miliyan [1] ↑
• Sokoto State SME Development Agency (code 022205100100), 2025 Performance Year to Date (Q1-Q4): ₦136.56 miliyan [2] ↓
• Kaso: 15.8% (lissafin Kasafi)

[1] Budget Implementation Report Q2 2026, shafi 16
[2] Budget Implementation Report Q4 2025, shafi 17
```

## h05: partial (lines:list, 11.5s)

**Q:** If we strip out personnel salaries and routine office overheads across all education-related agencies in the 2026 budget, what exact percentage of the remaining capital development fund is dedicated to Tsangaya and Almajiri school integration versus conventional schooling?

_Sub-sector disaggregation and a percentage after excluding recurrent lines._

```
The lines show ₦370.00 million capital for Agency for Almajiri Matters [1] and ₦840.00 million capital for Arabic and Islamic Education Board [2], after stripping personnel and overheads, but the full education capital total and the Tsangaya/Almajiri vs conventional split is not shown, so  (Kasafi's calculation) cannot be determined.

🧮 *Working* (the rows used):
• Agency for Almajiri Matters (code 017200700300), 2026 Approved Budget: ₦370.00 million [1]
• Arabic and Islamic Education Board (code 051705800100), 2026 Approved Budget: ₦840.00 million [2]
• Not found: capital development fund for all other education-related agencies (e.g. SUBEB, Ministry of Education and other education MDAs) and project titles distinguishing Tsangaya/Almajiri integration versus conventional schooling

[1] Sokoto State FY 2026 Budget, page 25
[2] Sokoto State FY 2026 Budget, page 27
```

## h06: partial (search, 14.8s)

**Q:** Given that the Ministry of Health spent 10.6% of its ₦124.41 billion allocation by the end of Q2 2026, if the ministry continues at that exact six-month burn rate for the remainder of the year, what will its unspent naira balance be on December 31, 2026, and how does that compare to its 2025 full-year unspent balance?

_Multi-step arithmetic projection with historical retrieval._

```
The projected 2026 unspent balance is not published; the evidence gives the allocation, mid-year spending and 2025 balance as inputs [1][3][5].

• 2026 approved budget (total): ₦124.41 billion [1]
• 2026 revised budget (total): ₦116.91 billion [5]
• 2026 performance year to date (total) (Q1-Q2 2026 only) (10.6% of the revised budget): ₦12.36 billion [5]
• 2025 final budget (total) (Q1-Q4 2025): ₦41.87 billion [3]
• 2025 performance year to date (total) (Q1-Q4 2025) (41.8% of the final budget): ₦17.51 billion [3]
• 2025 full-year unspent balance (total): ₦24.36 billion [3]

[1] Sokoto State FY 2026 Budget, page 18
[3] Budget Implementation Report Q4 2025, page 19
[5] Budget Implementation Report Q2 2026, page 18
```

## h07: partial (search, 15.4s)

**Q:** Idan muka kwatanta actual debt servicing expenditure a Q2 2026 report da kuma combined capital releases na Ministry of Water Resources da Primary Healthcare a wannan lokacin, wanne ya fi yawa kuma da nawa suka bambanta?

_Hausa-English code-switching; debt service vs social-sector comparison._

```
Ba a samu adadin biyan bashi a shaidu ba, don haka ba a iya kwatanta ba [2][3].

• Manyan ayyuka na Ma'aikatar Ruwa Q2 2026 kadai: ₦1.72 biliyan [2]
• Manyan ayyuka na Ma'aikatar Ruwa Q1-Q2 2026: ₦3.46 biliyan [2]
• Manyan ayyuka na Primary Healthcare Q2 2026 kadai: ₦121.81 miliyan [3]
• Manyan ayyuka na Primary Healthcare Q1-Q2 2026: ₦729.23 miliyan [3]

[2] Budget Implementation Report Q2 2026, shafi 27
[3] Budget Implementation Report Q2 2026, shafi 53
```

## h08: partial (search, 27.1s)

**Q:** Rural feeder road construction and rehabilitation often appear under both the Ministry of Works and the Ministry of Rural Development; can you identify any potentially overlapping or similarly named road projects between these two ministries in the 2026 budget and cite their exact budget codes and page numbers?

_Similarity search across separate administrative sections._

```
The evidence shows three rural-road projects under Works codes on page 56, with no Ministry of Rural Development road project shown [6].

• Construction of State wide 300kms rural feeder roads and 500km road (tarring) across the state — code 023405700100 - Department for Rural Roads, page 56 — 2026 approved budget (capital): ₦209.11 million [6]
• Construction of Rural Roads through Rural access and mobility projects (RAMP) — code 023405700100 - Department for Rural Roads, page 56 — 2026 approved budget (capital): ₦7.90 billion [6]
• Rehabilitation of existing projects under rural roads — code 023405700100 - Department for Rural Roads, page 56 — 2026 approved budget (capital): ₦200.00 million [6]

[6] Sokoto State FY 2026 Budget, page 56
```

## h09: partial (search, 9.0s)

**Q:** What proportion of the 2026 capital budget is scheduled to be financed through domestic and external loans versus recurrent revenue surplus, and according to the Q2 2026 report, which expected capital receipts failed to record any inflows during the first half of the year?

_Deficit-financing structure rather than expenditure lines._

```
The loan versus surplus financing split was not found, but several expected capital receipts recorded nil inflows in H1 2026 [3].

• 2026 revised budget (total) for CAPITAL GRANTS FROM FGN: ₦13.42 billion with Q1-Q2 2026 performance nil (0.0% of the revised budget) [3].
• 2026 revised budget (total) for CAPITAL GRANTS FROM OTHER SOURCES: ₦25.21 billion with Q1-Q2 2026 performance nil (0.0% of the revised budget) [3].
• 2026 revised budget (total) for CAPITAL FOREIGN AID: ₦2.50 billion with Q1-Q2 2026 performance nil (0.0% of the revised budget) [3].
• 2026 revised budget (total) for DOMESTIC GRANTS: ₦39.78 billion with Q1-Q2 2026 performance nil (0.0% of the revised budget) [3].
• 2026 revised budget (total) for AID: ₦2.50 billion with Q1-Q2 2026 performance nil (0.0% of the revised budget) [3].

[3] Budget Implementation Report Q2 2026, page 14
```

## h10: not found (search, 6.7s)

**Q:** Between the 2025 and 2026 budgets, which ministry received the highest percentage increase in its nominal capital allocation, yet recorded one of the lowest percentage rates of actual funds released by the end of Q2 2026?

_Cross-year growth paired with inverse ranking on implementation._

```
I couldn't find the answer to that in the documents I have.
```
