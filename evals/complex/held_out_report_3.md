# Open-question run: held_out.json

10 questions: partial 6, not found 2, answered 2 | median 10.6s

## h01: not found (search, 16.2s)

**Q:** Beyond the Ministry of Environment's direct allocation, if you combine all climate-adaptation and flood-control capital projects scattered across Agriculture, Water Resources, and Emergency Management in the 2026 budget, how does that combined total compare to their actual cumulative releases by Q2 2026?

_Cross-MDA thematic aggregation rather than single-ministry lookup._

```
I couldn't find the answer to that in the documents I have.
```

## h02: answered (search, 11.5s)

**Q:** Since the Ministry of Health already spent 89.4% of its ₦124.41 billion allocation by June 2026, how much supplementary funding was approved for it in the Q2 2026 report?

_False-premise detection: only 10.6% was spent by June; 89.4% is the unspent balance._

```
No supplementary funding was approved; the Ministry of Health revised budget is lower than its original budget. [4]

• 2026 original budget (total): ₦124.41 billion [4]
• 2026 revised budget (total): ₦116.91 billion [4]
• 2026 Q1-Q2 performance (total, Q1-Q2 2026 only): ₦12.36 billion (10.6% of the revised budget) [4]

[4] Budget Implementation Report Q2 2026, page 18
```

## h03: partial (search, 10.4s)

**Q:** Looking across both the 2026 approved budget and the Q2 2026 implementation report, which specific ministries had already exhausted more than 50% of their annual overhead allocation by June while recording 0% capital expenditure release, and on which pages do these figures appear?

_Multi-condition filtering across recurrent and capital columns._

```
The excerpts do not show any one ministry meeting both conditions together [1][2][5].

• Government House headquarters Q1-Q2 2026 (overhead): ₦1.81 billion (50.1% of the revised budget) on page 22 [1]
• Ministry for Special Duties Q1-Q2 2026 (capital): - (0.0% of the revised budget) on page 26 [2]
• Ministry of Culture & Tourism Q1-Q2 2026 (capital): - (0.0% of the revised budget) on page 27 [5]
• Ministry of Justice Q1-Q2 2026 (capital): - (0.0% of the revised budget) on page 27 [5]
• Ministry of Commerce and Industry Q1-Q2 2026 (capital): - (0.0% of the revised budget) on page 27 [5]
• Ministry of Solid Minerals and Natural Resources Q1-Q2 2026 (capital): - (0.0% of the revised budget) on page 27 [5]

[1] Budget Implementation Report Q2 2026, page 22
[2] Budget Implementation Report Q2 2026, page 26
[5] Budget Implementation Report Q2 2026, page 27
```

## h04: partial (lines:share, 10.8s)

**Q:** Idan muka hada duka kudaden da gwamnati ta ware domun farfado da kananan sana'o'in hannu da tallafin kasuwanci a ma'aikatu daban-daban a 2026, shin kudin da aka saki a zahiri zuwa watan Yuni ya kai rabin abin da aka kashe a shekarar 2025?

_Dialectal Hausa, cross-year synthesis, multi-agency summation._

```
Hukumar Bunkasa Kananan Sana'o'i ta saki ₦21.57 miliyan [1] har zuwa Yuni 2026, yayin da aka kashe ₦136.56 miliyan [2] a 2025, wanda ya yi 15.8% (lissafin Kasafi), don haka bai kai rabin abin da aka kashe a 2025 ba; ba a nuna layin farfado da sana'o'in hannu daban ba.

🧮 *Yadda aka lissafa* (layukan da aka yi amfani da su):
• Sokoto State SME Development Agency (code 022205100100), 2026 Performance Year to Date (Q1-Q2): ₦21.57 miliyan [1] ↑
• Sokoto State SME Development Agency (code 022205100100), 2025 Performance Year to Date (Q1-Q4): ₦136.56 miliyan [2] ↓
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.
• Kaso (↑ ÷ ↓): 15.8% (lissafin Kasafi)

[1] Budget Implementation Report Q2 2026, shafi 16
[2] Budget Implementation Report Q4 2025, shafi 17
```

## h05: answered (lines:share, 10.1s)

**Q:** If we strip out personnel salaries and routine office overheads across all education-related agencies in the 2026 budget, what exact percentage of the remaining capital development fund is dedicated to Tsangaya and Almajiri school integration versus conventional schooling?

_Sub-sector disaggregation and a percentage after excluding recurrent lines._

```
Excluding personnel and overheads, the capital fund comprises ₦370.00 million [1] for the Agency for Almajiri Matters, ₦9.15 billion [2] for SUBEB and ₦34.19 billion [2] for Ministry for Basic Education, with the Almajiri share at 0.8% (Kasafi's calculation) versus the remainder for conventional schooling.

🧮 *Working* (the rows used):
• Agency for Almajiri Matters (code 017200700300), 2026 Approved Budget: ₦370.00 million [1] ↑↓
• State Universal Basic Education Board (SUBEB) (code 051700300100), 2026 Approved Budget: ₦9.15 billion [2] ↓
• Ministry for Basic Education (code 051700100100), 2026 Approved Budget: ₦34.19 billion [2] ↓
• Share (↑ ÷ ↓): 0.8% (Kasafi's calculation)

[1] Sokoto State FY 2026 Budget, page 25
[2] Sokoto State FY 2026 Budget, page 27
```

## h06: partial (search, 9.7s)

**Q:** Given that the Ministry of Health spent 10.6% of its ₦124.41 billion allocation by the end of Q2 2026, if the ministry continues at that exact six-month burn rate for the remainder of the year, what will its unspent naira balance be on December 31, 2026, and how does that compare to its 2025 full-year unspent balance?

_Multi-step arithmetic projection with historical retrieval._

```
The 2026 projected unspent balance is not published, while the 2025 full-year unspent balance was ₦24.36 billion [4].

• 2026 approved budget (total): ₦124.41 billion [1][5].
• 2026 revised budget (total): ₦116.91 billion [5].
• 2026 spend Q1-Q2 only (total): ₦12.36 billion (10.6% of the revised budget) [5].
• 2025 full-year unspent (total): ₦24.36 billion [4].

🧮 Projected 2026 unspent balance if H1 burn rate repeats in H2 isn't published, but I can calculate it from the official figures: (2026 approved budget minus twice Q1-Q2 spend). Reply *Eh* (yes) to calculate.

[1] Sokoto State FY 2026 Budget, page 18
[4] Budget Implementation Report Q4 2025, page 19
[5] Budget Implementation Report Q2 2026, page 18
```

## h07: partial (search, 17.0s)

**Q:** Idan muka kwatanta actual debt servicing expenditure a Q2 2026 report da kuma combined capital releases na Ministry of Water Resources da Primary Healthcare a wannan lokacin, wanne ya fi yawa kuma da nawa suka bambanta?

_Hausa-English code-switching; debt service vs social-sector comparison._

```
Adadin biyan bashin bai bayyana a shaidu ba, don haka ba a iya kwatantawa ba [1][5].

• Ma'aikatar Ruwa Q2 2026 kaɗai (manyan ayyuka): ₦1.72 biliyan [2]
• Ma'aikatar Ruwa Q1-Q2 2026 (manyan ayyuka): ₦3.46 biliyan (8.5% na kasafin da aka sabunta) [2]
• Kiwon Lafiya a Matakin Farko Q2 2026 kaɗai (manyan ayyuka): ₦121.81 miliyan [3]
• Kiwon Lafiya a Matakin Farko Q1-Q2 2026 (manyan ayyuka): ₦729.23 miliyan (12.4% na kasafin da aka sabunta) [3]
• Adadin biyan bashin (debt servicing) bai bayyana a cikin shaidu ba, don haka bambancin bai samu ba [1][5]

[1] Budget Implementation Report Q2 2026, shafi 15
[2] Budget Implementation Report Q2 2026, shafi 27
[3] Budget Implementation Report Q2 2026, shafi 53
[5] Budget Implementation Report Q2 2026, shafi 26
```

## h08: partial (search, 16.1s)

**Q:** Rural feeder road construction and rehabilitation often appear under both the Ministry of Works and the Ministry of Rural Development; can you identify any potentially overlapping or similarly named road projects between these two ministries in the 2026 budget and cite their exact budget codes and page numbers?

_Similarity search across separate administrative sections._

```
Only Ministry of Works rural-road projects are shown, so no overlap with Ministry of Rural Development can be identified. [6]

• Construction of State wide 300kms rural feeder roads and 500km road (tarring) across the state (023405700100, page 56) 2026 approved budget (capital): ₦209.11 million [6]
• Construction of Rural Roads through Rural access and mobility projects (RAMP) (023405700100, page 56) 2026 approved budget (capital): ₦7.90 billion [6]
• Rehabilitation of existing projects under rural roads (023405700100, page 56) 2026 approved budget (capital): ₦200.00 million [6]
• The evidence did not show any Ministry of Rural Development road projects to compare for overlap. [6]

[6] Sokoto State FY 2026 Budget, page 56
```

## h09: partial (search, 8.5s)

**Q:** What proportion of the 2026 capital budget is scheduled to be financed through domestic and external loans versus recurrent revenue surplus, and according to the Q2 2026 report, which expected capital receipts failed to record any inflows during the first half of the year?

_Deficit-financing structure rather than expenditure lines._

```
The evidence does not publish the loan versus surplus financing shares, but it shows ₦219.81 billion expected from capital receipts and several capital receipts with zero inflows in H1 [6][3].

• 2026 projected recurrent revenue (total): ₦477.83 billion [6]
• 2026 expected capital receipts (total): ₦219.81 billion 80 [6]
• Capital foreign aid, 2026 revised budget (total): ₦2.50 billion with 0.0% YTD (Q1-Q2 2026 only) [3]
• Domestic grants, 2026 revised budget (total): ₦39.78 billion with 0.0% YTD (Q1-Q2 2026 only) [3]
• Capital grants from FGN, 2026 revised budget (total): ₦13.42 billion with 0.0% YTD (Q1-Q2 2026 only) [3]
• Capital grants from other sources, 2026 revised budget (total): ₦25.21 billion with 0.0% YTD (Q1-Q2 2026 only) [3]

[3] Budget Implementation Report Q2 2026, page 14
[6] Budget Implementation Report Q2 2026, page 4
```

## h10: not found (search, 8.6s)

**Q:** Between the 2025 and 2026 budgets, which ministry received the highest percentage increase in its nominal capital allocation, yet recorded one of the lowest percentage rates of actual funds released by the end of Q2 2026?

_Cross-year growth paired with inverse ranking on implementation._

```
I couldn't find the answer to that in the documents I have.
```
