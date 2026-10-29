# Open-question run: held_out.json

10 questions: partial 6, answered 3, not found 1 | median 13.2s

## h01: partial (lines:share, 20.9s)

**Q:** Beyond the Ministry of Environment's direct allocation, if you combine all climate-adaptation and flood-control capital projects scattered across Agriculture, Water Resources, and Emergency Management in the 2026 budget, how does that combined total compare to their actual cumulative releases by Q2 2026?

_Cross-MDA thematic aggregation rather than single-ministry lookup._

```
Only broader ministry totals are shown, not separate climate-adaptation/flood-control projects: Agriculture capital ₦15.37 billion [1] and SEMA capital ₦1.20 billion [2], with Q1-Q2 releases of ₦4.83 billion [3] and ₦543.57 million [4], representing  (Kasafi's calculation) spent.

🧮 *Working* (the rows used):
• AGRICULTURE (code 70421), 2026 Approved Budget: ₦15.37 billion [1] ↓
• State Emergency Management Agency (SEMA) (code 011100800100), 2026 Approved Budget: ₦1.20 billion [2] ↓
• AGRICULTURE (code 70421), 2026 Performance Year to Date (Q1-Q2): ₦4.83 billion [3] ↑
• State Emergency Management Agency (SEMA) (code 011100800100), 2026 Performance Year to Date (Q1-Q2): ₦543.57 million [4] ↑
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Share (↑ ÷ ↓): 32.4% (Kasafi's calculation)
• Not found: Specific climate-adaptation and flood-control capital projects for Agriculture, Water Resources and Emergency Management are not shown separately; no Water Resources line is shown at all.

[1] Sokoto State FY 2026 Budget, page 37
[2] Sokoto State FY 2026 Budget, page 25
[3] Budget Implementation Report Q2 2026, page 42
[4] Budget Implementation Report Q2 2026, page 26
```

## h02: answered (search, 6.2s)

**Q:** Since the Ministry of Health already spent 89.4% of its ₦124.41 billion allocation by June 2026, how much supplementary funding was approved for it in the Q2 2026 report?

_False-premise detection: only 10.6% was spent by June; 89.4% is the unspent balance._

```
No supplementary funding was approved for the Ministry of Health; its revised budget is lower than its original budget [4].

• 2026 original budget (total): ₦124.41 billion [4]
• 2026 revised budget (total): ₦116.91 billion [4]
• 2026 Q1-Q2 performance (total): ₦12.36 billion (10.6% of the revised budget) (Q1-Q2 2026 only) [4]

[4] Budget Implementation Report Q2 2026, page 18
```

## h03: not found (search, 6.2s)

**Q:** Looking across both the 2026 approved budget and the Q2 2026 implementation report, which specific ministries had already exhausted more than 50% of their annual overhead allocation by June while recording 0% capital expenditure release, and on which pages do these figures appear?

_Multi-condition filtering across recurrent and capital columns._

```
I couldn't find the answer to that in the documents I have.
```

## h04: partial (lines:share, 11.4s)

**Q:** Idan muka hada duka kudaden da gwamnati ta ware domun farfado da kananan sana'o'in hannu da tallafin kasuwanci a ma'aikatu daban-daban a 2026, shin kudin da aka saki a zahiri zuwa watan Yuni ya kai rabin abin da aka kashe a shekarar 2025?

_Dialectal Hausa, cross-year synthesis, multi-agency summation._

```
Ba a nuna farfado da sana'o'in hannu da tallafin kasuwanci daban-daban ba, sai jimillar Hukumar SME Development Agency aka samu. Abin da aka saki zuwa watan Yuni 2026 ya kai ₦21.57 miliyan [1], abin da aka kashe a 2025 duka ya kai ₦136.56 miliyan [2], rabon ya kai 15.8% (lissafin Kasafi).

🧮 *Yadda aka lissafa* (layukan da aka yi amfani da su):
• Sokoto State SME Development Agency (code 022205100100), 2026 Performance Year to Date (Q1-Q2): ₦21.57 miliyan [1] ↑
• Sokoto State SME Development Agency (code 022205100100), 2025 Performance Year to Date (Q1-Q4): ₦136.56 miliyan [2] ↓
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.
• Kaso (↑ ÷ ↓): 15.8% (lissafin Kasafi)

[1] Budget Implementation Report Q2 2026, shafi 16
[2] Budget Implementation Report Q4 2025, shafi 17
```

## h05: answered (lines:share, 10.3s)

**Q:** If we strip out personnel salaries and routine office overheads across all education-related agencies in the 2026 budget, what exact percentage of the remaining capital development fund is dedicated to Tsangaya and Almajiri school integration versus conventional schooling?

_Sub-sector disaggregation and a percentage after excluding recurrent lines._

```
Excluding personnel and overheads, the capital development fund for Basic Education is ₦10.16 billion [2], of which the Agency for Almajiri Matters capital is ₦370.00 million [1], representing 3.6% (Kasafi's calculation) for Tsangaya/Almajiri versus conventional schooling.

🧮 *Working* (the rows used):
• Agency for Almajiri Matters (code 017200700300), 2026 Approved Budget: ₦370.00 million [1] ↑
• CAPITAL EXPENDITURE (code 23), 2026 Approved Budget: ₦10.16 billion [2] ↓
• Share (↑ ÷ ↓): 3.6% (Kasafi's calculation)

[1] Sokoto State FY 2026 Budget, page 25
[2] Sokoto State FY 2026 Budget, page 77
```

## h06: partial (search, 19.0s)

**Q:** Given that the Ministry of Health spent 10.6% of its ₦124.41 billion allocation by the end of Q2 2026, if the ministry continues at that exact six-month burn rate for the remainder of the year, what will its unspent naira balance be on December 31, 2026, and how does that compare to its 2025 full-year unspent balance?

_Multi-step arithmetic projection with historical retrieval._

```
The projected year-end unspent balance is not published; the 2025 full-year unspent balance (total) was ₦24.36 billion [1].

• Total Expenditure by Administrative Classification 2026 original budget (total): ₦124.41 billion [3]
• 2026 revised budget (total): ₦116.91 billion [3]
• 2026 spend (total) (Q1-Q2 2026 only) (10.6% of the revised budget): ₦12.36 billion [3]
• Total Expenditure by Administrative Classification 2025 full-year unspent balance (total) (Q1-Q4 2025): ₦24.36 billion [1]

🧮 Ministry of Health projected year-end unspent balance if second-half spend equals first-half spend isn't published, but I can calculate it from the official figures: (2026 original budget minus 2 times Q1-Q2 spend). Reply *Eh* (yes) to calculate.

[1] Budget Implementation Report Q4 2025, page 19
[3] Budget Implementation Report Q2 2026, page 18
```

## h07: partial (search, 9.7s)

**Q:** Idan muka kwatanta actual debt servicing expenditure a Q2 2026 report da kuma combined capital releases na Ministry of Water Resources da Primary Healthcare a wannan lokacin, wanne ya fi yawa kuma da nawa suka bambanta?

_Hausa-English code-switching; debt service vs social-sector comparison._

```
Ba a samu adadin biyan bashi ba don kwatance, an samu sakin manyan ayyuka biyu kaɗai [2][3].

• 2026 Q1–Q2 kaɗai, manyan ayyuka na Ministry of Water Resources: ₦3.46 biliyan [2]
• 2026 Q1–Q2 kaɗai, manyan ayyuka na Primary Healthcare: ₦729.23 miliyan [3]

🧮 Ba a wallafa combined capital releases, Ministry of Water Resources + Primary Healthcare, Q1-Q2 2026 ba, amma zan iya lissafa shi daga alƙalumman hukuma: (sakin Ministry of Water Resources + sakin Primary Healthcare). Amsa *Eh* domin in lissafa.

[2] Budget Implementation Report Q2 2026, shafi 27
[3] Budget Implementation Report Q2 2026, shafi 53
```

## h08: partial (lines:list, 21.9s)

**Q:** Rural feeder road construction and rehabilitation often appear under both the Ministry of Works and the Ministry of Rural Development; can you identify any potentially overlapping or similarly named road projects between these two ministries in the 2026 budget and cite their exact budget codes and page numbers?

_Similarity search across separate administrative sections._

```
Ministry of Works lists CONSTRUCTION OF SABON BIRNI GATAWA TO ISA ROAD PROJECT of ₦300.00 million [1] and REHABILITATION OF MARNONA ISA ROAD PROJECT of ₦300.00 million [1], while Department for Rural Roads lists (RAMP) construction of ₦7.90 billion [1] and Rehabilitation of existing projects under rural roads of ₦200.00 million [1].

🧮 *Working* (the rows used):
• CONSTRUCTION OF SABON BIRNI GATAWA TO ISA ROAD PROJECT (Ministry of Works), 2026 Approved Budget: ₦300.00 million [1]
• REHABILITATION OF MARNONA ISA ROAD PROJECT (Ministry of Works), 2026 Approved Budget: ₦300.00 million [1]
• (RAMP) (Department for Rural Roads) – construction / provision of roads, 2026 Approved Budget: ₦7.90 billion [1]
• Rehabilitation of existing projects under rural roads (Department for Rural Roads), 2026 Approved Budget: ₦200.00 million [1]
• Not found: No line labelled Ministry of Rural Development is shown; rural road projects appear under Department for Rural Roads.

[1] Sokoto State FY 2026 Budget, page 56
```

## h09: partial (lines:list, 19.5s)

**Q:** What proportion of the 2026 capital budget is scheduled to be financed through domestic and external loans versus recurrent revenue surplus, and according to the Q2 2026 report, which expected capital receipts failed to record any inflows during the first half of the year?

_Deficit-financing structure rather than expenditure lines._

```
The lines do not show the 2026 financing breakdown for domestic and external loans versus recurrent revenue surplus, so that proportion cannot be determined. The Q2 2026 report shows CAPITAL GRANTS FROM FGN expected at ₦13.42 billion [1] with 0.00 recorded YTD [1] and CAPITAL FOREIGN AID expected at ₦2.50 billion [1] with 0.00 recorded YTD [1].

🧮 *Working* (the rows used):
• CAPITAL GRANTS FROM FGN (code 13020102) [Total Revenue by Economic Classification], 2026 Original Budget: ₦13.42 billion [1]
• CAPITAL GRANTS FROM FGN (code 13020102) [Total Revenue by Economic Classification], 2026 Performance Year to Date (Q1-Q2): 0.00 [1]
• CAPITAL FOREIGN AID (code 13010202) [Total Revenue by Economic Classification], 2026 Original Budget: ₦2.50 billion [1]
• CAPITAL FOREIGN AID (code 13010202) [Total Revenue by Economic Classification], 2026 Performance Year to Date (Q1-Q2): 0.00 [1]
• Not found: Domestic loans and external loans financing for 2026 capital budget and recurrent revenue surplus financing for 2026 capital budget

[1] Budget Implementation Report Q2 2026, page 14
```

## h10: answered (query_budget:rank, 15.0s)

**Q:** Between the 2025 and 2026 budgets, which ministry received the highest percentage increase in its nominal capital allocation, yet recorded one of the lowest percentage rates of actual funds released by the end of Q2 2026?

_Cross-year growth paired with inverse ranking on implementation._

```
The evidence does not include 2025 capital allocations, so the ministry with the highest percentage increase between 2025 and 2026 cannot be identified [1][2][3]. The lowest recorded 2026 Q2 capital performance is "% Performance Year to Date against 2026 Revised Budget: 0.0%" for Fiscal Responsibility Commission, Ministry for Skills Acquisition and Entrepreneurship Development, Ministry of Commerce and Industry, Ministry of Culture & Tourism, Ministry of Justice and Ministry of Solid Minerals and Natural Resources [1], Ministry for Local Government and Chieftancy [2], and Ministry for Special Duties, Sokoto State House of Assembly and Sokoto State Independent Electoral Commission [3].

🧮 *Working* (the rows used):
1. Fiscal Responsibility Commission (025000000000): 0.0% (2026 Performance Year to Date (Q1-Q2): 0.00 of 2026 Revised Budget: ₦14.25 million) [1]
1. Ministry for Local Government and Chieftancy (055100000000): 0.0% (2026 Performance Year to Date (Q1-Q2): 0.00 of 2026 Revised Budget: ₦850.44 million) [2]
1. Ministry for Skills Acquisition and Entrepreneurship Development (028900000000): 0.0% (2026 Performance Year to Date (Q1-Q2): 0.00 of 2026 Revised Budget: ₦1.07 billion) [1]
1. Ministry for Special Duties (016700000000): 0.0% (2026 Performance Year to Date (Q1-Q2): 0.00 of 2026 Revised Budget: ₦622.00 million) [3]
1. Ministry of Commerce and Industry (022200000000): 0.0% (2026 Performance Year to Date (Q1-Q2): 0.00 of 2026 Revised Budget: ₦4.11 billion) [1]
1. Ministry of Culture & Tourism (023600000000): 0.0% (2026 Performance Year to Date (Q1-Q2): 0.00 of 2026 Revised Budget: ₦788.59 million) [1]
1. Ministry of Justice (032600000000): 0.0% (2026 Performance Year to Date (Q1-Q2): 0.00 of 2026 Revised Budget: ₦3.71 billion) [1]
1. Ministry of Solid Minerals and Natural Resources (023300000000): 0.0% (2026 Performance Year to Date (Q1-Q2): 0.00 of 2026 Revised Budget: ₦610.10 million) [1]
1. Sokoto State House of Assembly (011200000000): 0.0% (2026 Performance Year to Date (Q1-Q2): 0.00 of 2026 Revised Budget: ₦4.66 billion) [3]
1. Sokoto State Independent Electoral Commission (014800000000): 0.0% (2026 Performance Year to Date (Q1-Q2): 0.00 of 2026 Revised Budget: ₦225.71 million) [3]

[1] Budget Implementation Report Q2 2026, page 27
[2] Budget Implementation Report Q2 2026, page 28
[3] Budget Implementation Report Q2 2026, page 26
```
