# Open-question run: multi_source.json

4 questions: answered 2, not found 1, partial 1 | wrong 4 of 4 checked (t01, t08, t11, t12) | median 16.0s

```
plan          n= 4 median   3.7s    22% of all time
page_search   n= 2 median   1.6s     5% of all time
compose       n= 2 median   3.0s     9% of all time
answer        n= 2 median   3.0s     9% of all time
```

## t01: answered WRONG: says '0.5 (NBS Nigeria Multidimensional Poverty Index, 2022) → 59.1%' (topic:poverty_welfare, 24.0s)

**Q:** According to NBS what is Sokoto's MPI, and according to SBS how much has it improved?

_Bilyaminu's phone test, Oct 30 2026: NBS's own 2022 report and SBS's own 2025 report; the change only between the same measure_

```
📊 Newest figure: *0.23853* – Multidimensional Poverty Index (MPI) (index value, 0–1), Sokoto State (Sokoto State Bureau of Statistics, 2025).

By source:
• Sokoto State Bureau of Statistics: 0.23853 – Multidimensional Poverty Index (MPI) (index value, 0–1), Sokoto State; 2025 (Sokoto State Multi-dimensional Poverty Index (MPI) Report 2025, p. 61)
• Sokoto State Bureau of Statistics: 59.1% – Headcount Ratio (H), Sokoto State; 2025 (Sokoto State Multi-dimensional Poverty Index (MPI) Report 2025, p. 33)
• Sokoto State Bureau of Statistics: 40.3% – Intensity of Poverty (A), Sokoto State; 2025 (Sokoto State Multi-dimensional Poverty Index (MPI) Report 2025, p. 33)
• NBS Nigeria Multidimensional Poverty Index: 0.409 – Multidimensional Poverty Index (MPI) - The share of possible deprivations that multidimensionally poor people experience. It is computed by multiplying 'Inciden (index value, 0–1), Sokoto State; 2022 (Nigeria Multidimensional Poverty Index (2022), p. 123)
• NBS Nigeria Multidimensional Poverty Index: 90.5% – Incidence (H, %) - The percentage of the population who are multidimensionally poor (headcount, % of people), Sokoto State; 2022 (Nigeria Multidimensional Poverty Index (2022), p. 123)
• NBS Nigeria Multidimensional Poverty Index: 45.2% – Intensity (A, %) - The average percentage of weighted deprivations which poor people are experiencing, Sokoto State; 2022 (Nigeria Multidimensional Poverty Index (2022), p. 123)

↔️ Why they differ: they refer to different dates (NBS Nigeria Multidimensional Poverty Index 2022, Sokoto State Bureau of Statistics 2025); they count different things (NBS Nigeria Multidimensional Poverty Index: Multidimensional Poverty Index (MPI) - The share of possible deprivations that multidimensionally poor people experience. It is computed by multiplying 'Inciden; Sokoto State Bureau of Statistics: Multidimensional Poverty Index (MPI)). These are separate counts; Kasafi doesn't average them or pick one.

ℹ️ These are different measures (index value, 0–1; headcount, % of people; intensity, %); a change or comparison is made only between the same measure.

📈 Change in the index value, 0–1: 0.409 (NBS Nigeria Multidimensional Poverty Index, 2022) → 0.23853 (Sokoto State Bureau of Statistics, 2025): down by 0.17047 (41.7% of the earlier value) (Kasafi's calculation).
⚠️ NBS Nigeria Multidimensional Poverty Index, 2022 and Sokoto State Bureau of Statistics, 2025 are different surveys (their indicators, samples and methods differ), so this change is indicative, not a like-for-like trend.
📈 Change in the headcount, % of people: 90.5 (NBS Nigeria Multidimensional Poverty Index, 2022) → 59.1% (Sokoto State Bureau of Statistics, 2025): down by 31.4 percentage points (Kasafi's calculation).
⚠️ NBS Nigeria Multidimensional Poverty Index, 2022 and Sokoto State Bureau of Statistics, 2025 are different surveys (their indicators, samples and methods differ), so this change is indicative, not a like-for-like trend.
📈 Change in the intensity, %: 45.2 (NBS Nigeria Multidimensional Poverty Index, 2022) → 40.3% (Sokoto State Bureau of Statistics, 2025): down by 4.9 percentage points (Kasafi's calculation).
⚠️ NBS Nigeria Multidimensional Poverty Index, 2022 and Sokoto State Bureau of Statistics, 2025 are different surveys (their indicators, samples and methods differ), so this change is indicative, not a like-for-like trend.

📄 *Sources:* Sokoto State Multi-dimensional Poverty Index (MPI) Report 2025, p. 33, 61; Nigeria Multidimensional Poverty Index (2022), p. 123
```

## t08: not found WRONG: none of [['1.2', '14%']] (search, 15.5s)

**Q:** What is the unemployment rate in Sokoto according to NBS, and what did the SBS/JIPS/DRC survey find for IDPs in Sokoto town?

_the state's rate and a town survey's IDP share: different populations and areas, side by side, no change_

```
I couldn't find the answer to that in the documents I have.
```

## t11: partial WRONG: none of [['42.8']] (search, 8.6s)

**Q:** What percentage of children under 5 in Sokoto are stunted, and how has it changed?

_NDHS 2024 only: MICS 2021 has no anthropometry, so no change can be computed (said so)_

```
⚠️ Nigeria Demographic and Health Survey 2024 Final Report isn't a primary source for this figure (those are Cadre Harmonise analysis, FEWS NET Nigeria outlooks, WFP Nigeria, SMART nutrition surveys); treat it as related context.

The evidence does not give a stunting percentage for children under 5 in Sokoto specifically. Nationally, 40% of children under age 5 were stunted in the 2024 NDHS, compared with 37% in the 2018 NDHS.

• 2018 NDHS (national, stunted): 37%
• 2024 NDHS (national, stunted): 40%

📄 *Sources:* Nigeria Demographic and Health Survey 2024 Final Report, p. 347
```

## t12: answered WRONG: none of [['90.5', '59.1'], ['91%', '59.1']] (topic:poverty_welfare, 16.6s)

**Q:** By how many percentage points did the share of multidimensionally poor people in Sokoto change between the NBS 2022 MPI and the SBS 2025 MPI?

_the headcount pair, in percentage points, with a comparability note_

```
📊 Newest figure: *59.2%* – Headcount Ratio (H) - share of people living in multidimensional poverty, non-income, Sokoto State (Sokoto State Bureau of Statistics, 2025).

By source:
• Sokoto State Bureau of Statistics: 59.2% – Headcount Ratio (H) - share of people living in multidimensional poverty, non-income, Sokoto State; 2025 (Sokoto State Multi-dimensional Poverty Index (MPI) Report 2025, p. 68)
• Sokoto State Bureau of Statistics: 91% – 2022 baseline headcount - share of multidimensionally poor people, Sokoto State; 2022 (Sokoto State Multi-dimensional Poverty Index (MPI) Report 2025, p. 36)
• Sokoto State Bureau of Statistics: 32- percentage points – reduction in poverty in three years comparing 2025 state results with 2022 National MPI, Sokoto State; 2022-2025 (Sokoto State Multi-dimensional Poverty Index (MPI) Report 2025, p. 36)
• NBS Nigeria Multidimensional Poverty Index: 90.5% – Incidence (H, %) - percentage of the population who are multidimensionally poor (headcount, % of people), Sokoto State; 2022 (Nigeria Multidimensional Poverty Index (2022), p. 123)

↔️ Why they differ: they refer to different dates (NBS Nigeria Multidimensional Poverty Index 2022, Sokoto State Bureau of Statistics 2025); they count different things (NBS Nigeria Multidimensional Poverty Index: Incidence (H, %) - percentage of the population who are multidimensionally poor; Sokoto State Bureau of Statistics: Headcount Ratio (H) - share of people living in multidimensional poverty, non-income). These are separate counts; Kasafi doesn't average them or pick one.

📈 Change in the headcount, % of people: 90.5 (NBS Nigeria Multidimensional Poverty Index, 2022) → 59.2% (Sokoto State Bureau of Statistics, 2025): down by 31.3 percentage points (Kasafi's calculation).
⚠️ NBS Nigeria Multidimensional Poverty Index, 2022 and Sokoto State Bureau of Statistics, 2025 are different surveys (their indicators, samples and methods differ), so this change is indicative, not a like-for-like trend.

📄 *Sources:* Sokoto State Multi-dimensional Poverty Index (MPI) Report 2025, p. 36, 68; Nigeria Multidimensional Poverty Index (2022), p. 123
```
