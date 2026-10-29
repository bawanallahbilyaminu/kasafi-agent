# Open-question run: held_out.json

10 questions: partial 6, answered 2, not found 2 | median 9.6s

## h01: partial (lines:compare, 9.8s)

**Q:** Beyond the Ministry of Environment's direct allocation, if you combine all climate-adaptation and flood-control capital projects scattered across Agriculture, Water Resources, and Emergency Management in the 2026 budget, how does that combined total compare to their actual cumulative releases by Q2 2026?

_Cross-MDA thematic aggregation rather than single-ministry lookup._

```
For Emergency Management, the broader SEMA capital allocation is ₦1.20 billion [1] compared to cumulative Q1-Q2 releases of ₦543.57 million [2], a difference of ₦656.43 million 120.8% (Kasafi's calculation). No separate climate-adaptation and flood-control project lines for Agriculture, Water Resources and Emergency Management are shown.

🧮 *Working* (the rows used):
• State Emergency Management Agency (SEMA) (code 011100800100), 2026 Approved Budget: ₦1.20 billion [1]
• State Emergency Management Agency (SEMA) (code 011100800100), 2026 Performance Year to Date (Q1-Q2): ₦543.57 million [2]
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Difference (2026 Approved Budget vs 2026 Performance Year to Date (Q1-Q2)): +₦656.43 million (+120.8%) (Kasafi's calculation)
• Not found: Climate-adaptation and flood-control capital projects for Agriculture, Water Resources

[1] Sokoto State FY 2026 Budget, page 25
[2] Budget Implementation Report Q2 2026, page 26
```

## h02: answered (search, 7.7s)

**Q:** Since the Ministry of Health already spent 89.4% of its ₦124.41 billion allocation by June 2026, how much supplementary funding was approved for it in the Q2 2026 report?

_False-premise detection: only 10.6% was spent by June; 89.4% is the unspent balance._

```
No supplementary increase is shown; the 2026 revised budget is ₦116.91 billion, below the original [4].

• 2026 original budget (total): ₦124.41 billion [1][4]
• 2026 revised budget (total): ₦116.91 billion [4]
• 2026 performance year to date (Q1-Q2 2026 only) (total): ₦12.36 billion (10.6% of the revised budget) [4]

[1] Sokoto State FY 2026 Budget, page 18
[4] Budget Implementation Report Q2 2026, page 18
```

## h03: not found (search, 6.7s)

**Q:** Looking across both the 2026 approved budget and the Q2 2026 implementation report, which specific ministries had already exhausted more than 50% of their annual overhead allocation by June while recording 0% capital expenditure release, and on which pages do these figures appear?

_Multi-condition filtering across recurrent and capital columns._

```
I couldn't find the answer to that in the documents I have.
```

## h04: partial (lines:ratio, 14.4s)

**Q:** Idan muka hada duka kudaden da gwamnati ta ware domun farfado da kananan sana'o'in hannu da tallafin kasuwanci a ma'aikatu daban-daban a 2026, shin kudin da aka saki a zahiri zuwa watan Yuni ya kai rabin abin da aka kashe a shekarar 2025?

_Dialectal Hausa, cross-year synthesis, multi-agency summation._

```
Jimillar sakin kuɗi zuwa Yuni 2026 ya haɗa ₦112.82 miliyan [1] na Kasuwanci da Masana'antu da ₦115.78 miliyan [2] na Koyar da Sana'o'i, idan aka raba da ₦1.42 biliyan [3] da aka kashe a 2025, rabon ya kai 0.16 : 1 (lissafin Kasafi).

🧮 *Yadda aka lissafa* (layukan da aka yi amfani da su):
• Ministry of Commerce and Industry (code 022200000000), 2026 Performance Year to Date (Q1-Q2): ₦112.82 miliyan [1] ↑
• Ministry for Skills Acquisition and Entrepreneurship Development (code 028900000000), 2026 Performance Year to Date (Q1-Q2): ₦115.78 miliyan [2] ↑
• Ministry of Commerce and Industry (code 022200000000), 2025 Performance Year to Date (Q1-Q4): ₦1.42 biliyan [3] ↓
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.
• Rabo: 0.16 : 1 (lissafin Kasafi)
• Ba a samu ba: Cikakken kashe na shekarar 2025 na Ma'aikatar Koyar da Sana'o'i da Ci gaban Ɗan Kasuwa

[1] Budget Implementation Report Q2 2026, shafi 16
[2] Budget Implementation Report Q2 2026, shafi 17
[3] Budget Implementation Report Q4 2025, shafi 17
```

## h05: partial (lines:share, 10.0s)

**Q:** If we strip out personnel salaries and routine office overheads across all education-related agencies in the 2026 budget, what exact percentage of the remaining capital development fund is dedicated to Tsangaya and Almajiri school integration versus conventional schooling?

_Sub-sector disaggregation and a percentage after excluding recurrent lines._

```
Excluding personnel and overheads, capital for Agency for Almajiri Matters is ₦370.00 million [1] and capital for Arabic and Islamic Education Board is ₦840.00 million [2]; the Almajiri share of their combined capital fund is 44.0% (Kasafi's calculation).

🧮 *Working* (the rows used):
• Agency for Almajiri Matters (code 017200700300), 2026 Approved Budget: ₦370.00 million [1] ↑
• Arabic and Islamic Education Board (code 051705800100), 2026 Approved Budget: ₦840.00 million [2] ↓
• Share: 44.0% (Kasafi's calculation)
• Not found: Capital expenditure for other conventional schooling agencies such as State Universal Basic Education Board

[1] Sokoto State FY 2026 Budget, page 25
[2] Sokoto State FY 2026 Budget, page 27
```

## h06: partial (search, 9.5s)

**Q:** Given that the Ministry of Health spent 10.6% of its ₦124.41 billion allocation by the end of Q2 2026, if the ministry continues at that exact six-month burn rate for the remainder of the year, what will its unspent naira balance be on December 31, 2026, and how does that compare to its 2025 full-year unspent balance?

_Multi-step arithmetic projection with historical retrieval._

```
The projected 2026 year-end unspent balance is not published in the evidence [5].

• 2026 approved budget (total): ₦124.41 billion [1][5]
• 2026 Q1-Q2 spend, January-June only (total): ₦12.36 billion (10.6% of the revised budget) [5]
• 2025 full-year unspent balance, Q1-Q4 2025 (total): ₦24.36 billion [4]

🧮 Projected 2026 year-end unspent balance if H1 spend repeats in H2 isn't published, but I can calculate it from the official figures: (2026 approved budget minus twice Q1-Q2 spend). Reply *Eh* (yes) to calculate.

[1] Sokoto State FY 2026 Budget, page 18
[4] Budget Implementation Report Q4 2025, page 19
[5] Budget Implementation Report Q2 2026, page 18
```

## h07: partial (search, 10.1s)

**Q:** Idan muka kwatanta actual debt servicing expenditure a Q2 2026 report da kuma combined capital releases na Ministry of Water Resources da Primary Healthcare a wannan lokacin, wanne ya fi yawa kuma da nawa suka bambanta?

_Hausa-English code-switching; debt service vs social-sector comparison._

```
Ba a samu kashe kuɗin biyan bashi ba, sai manyan ayyukan ma'aikatun biyu kawai [2][3].

• Manyan ayyuka na Ministry of Water Resources (Q1–Q2 2026 kawai): ₦3.46 biliyan [2]
• Manyan ayyuka na Primary Healthcare (Q1–Q2 2026 kawai): ₦729.23 miliyan [3]
• Ba a samu adadin kashe kuɗin biyan bashin a cikin shaidun da aka bayar ba, don haka ba a iya kwatanta wanne ya fi yawa ba.

🧮 Ba a wallafa Haɗaɗɗen manyan ayyuka na Ministry of Water Resources da Primary Healthcare, Q1–Q2 2026 ba, amma zan iya lissafa shi daga alƙalumman hukuma: (manyan ayyukan ruwa da manyan ayyukan lafiya) — water + phc. Amsa *Eh* domin in lissafa.

[2] Budget Implementation Report Q2 2026, shafi 27
[3] Budget Implementation Report Q2 2026, shafi 53
```

## h08: not found (search, 13.0s)

**Q:** Rural feeder road construction and rehabilitation often appear under both the Ministry of Works and the Ministry of Rural Development; can you identify any potentially overlapping or similarly named road projects between these two ministries in the 2026 budget and cite their exact budget codes and page numbers?

_Similarity search across separate administrative sections._

```
I couldn't find the answer to that in the documents I have.
```

## h09: partial (search, 8.7s)

**Q:** What proportion of the 2026 capital budget is scheduled to be financed through domestic and external loans versus recurrent revenue surplus, and according to the Q2 2026 report, which expected capital receipts failed to record any inflows during the first half of the year?

_Deficit-financing structure rather than expenditure lines._

```
The loan-versus-surplus financing split was not shown, but several expected capital receipts had zero inflow in H1 2026 [3].

• CAPITAL FOREIGN AID Q1-Q2 2026 only (capital): no inflow against 2026 Revised Budget: ₦2.50 billion [3]
• DOMESTIC GRANTS Q1-Q2 2026 only (capital): no inflow against 2026 Revised Budget: ₦39.78 billion [3]
• CAPITAL GRANTS FROM FGN Q1-Q2 2026 only (capital): no inflow against 2026 Revised Budget: ₦13.42 billion [3]
• CAPITAL GRANTS FROM OTHER SOURCES Q1-Q2 2026 only (capital): no inflow against 2026 Revised Budget: ₦25.21 billion [3]
• The evidence did not include the scheduled domestic loans, external loans or recurrent revenue surplus figures for the 2026 capital budget.

[3] Budget Implementation Report Q2 2026, page 14
```

## h10: answered (query_budget:rank, 7.5s)

**Q:** Between the 2025 and 2026 budgets, which ministry received the highest percentage increase in its nominal capital allocation, yet recorded one of the lowest percentage rates of actual funds released by the end of Q2 2026?

_Cross-year growth paired with inverse ranking on implementation._

```
The evidence shows 0.0% performance in Q1-Q2 2026 for the Ministry of Justice (2026 Revised Budget: ₦3.71 billion), Ministry of Commerce and Industry (2026 Revised Budget: ₦4.11 billion) and eight other entities [1][2][3]. The 2025 capital allocations needed to determine the highest percentage increase were not found, so that part cannot be answered.

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
