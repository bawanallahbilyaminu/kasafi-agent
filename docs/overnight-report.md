# Overnight eval loop, 2026-11-04

Branch `overnight-evals`, from the deployed commit `a7836ff`. Muse Spark Open on Baseten only; the Meta key in the environment was deliberately invalid and every Muse Spark client was served by Muse Spark Open (`evals/overnight/common.py`, `meta_guard`). Caps in code: $20 Baseten, stop 06:30.

**Spend:** $14.36 on Baseten (every model call priced from its token usage, `kasafi_price_baseten_*`). **Meta attempts:** 0 (none: $0 Meta spend).

## Rounds

| Round | Commit tested | Fix half | Held-out half | Notes |
|---|---|---|---|---|
| 1 | `a7836ff (base) -> c57988f (after fixes)` | 38/47 (81%) | 45/48 (94%) | baseline before fixes: fix 38/47 ($2.77), held-out 41/48 ($1.97); causes: single-level count's one figure dropped from the reply (4), check discarded a deep brief (1), one private part added to a public total (1), dated NEMA row not retrieved (3), IQS state figure missing (2), wrong-agency rows (1), MICS Hausa unverified (1); r1-063 invalid (generator) | after the fixes: held-out 45/48 ($1.92), live-failures 13/13, routing 88/88, understanding replay 244/244; 4 better, 0 worse |
| 2 | `c57988f (base) -> 3137cda (after fixes)` | 52/59 (88%) | 34/37 (92%) | baseline: fix 52/59 ($2.30), held-out 34/37 ($1.60); causes: dated NEMA questions answered from the newest card (3), an LGA's wards answered statewide (1), the IQS state figure omitted by the writer (1), MICS wealth/anaemia unverified (2), a budget comparison missing one year (1) | after the fixes: held-out 34/37 (first rerun 33/37: r2-008 passed on rerun, r2-035 failed twice on the writer omitting the IQS state figure; r2-070 fixed), live-failures 12/13 then 13/13 (lfB rerun), routing 88/88, understanding replay unchanged |

### Per feature (all rounds, both halves)

| Feature | Right | Direct | Combine | Multi |
|---|---|---|---|---|
| budget | 41/44 (93%) | 23/24 (96%) | 18/20 (90%) | – |
| budget_lga | 9/9 (100%) | – | 9/9 (100%) | – |
| conversation | 12/12 (100%) | 12/12 (100%) | – | – |
| deep | 5/6 (83%) | – | 5/6 (83%) | – |
| emergency | 16/16 (100%) | 16/16 (100%) | – | – |
| facilities | 16/16 (100%) | 16/16 (100%) | – | – |
| nearest | 8/8 (100%) | – | – | 8/8 (100%) |
| nema | 7/12 (58%) | 7/12 (58%) | – | – |
| place | 15/16 (94%) | – | 15/16 (94%) | – |
| schools | 31/40 (78%) | 18/20 (90%) | 9/10 (90%) | 4/10 (40%) |
| surveys | 9/12 (75%) | 9/12 (75%) | – | – |

### Per difficulty

| Difficulty | Right |
|---|---|
| direct | 101/112 (90%) |
| combine | 56/61 (92%) |
| multi | 12/18 (67%) |

## Fixes

- **Kept** `6ad37a3`: one private part never joins a public total when the census counts per level — held-out 41/48 → 45/48; live-failures 11/13 -> 13/13, routing 88/88, understanding 244/244.
- **Kept** `03ccd89`: a count with one figure shows that figure (single-level school counts had no figure in the reply) — held-out 41/48 → 45/48; live-failures 11/13 -> 13/13, routing 88/88, understanding 244/244.
- **Kept** `23c805d`: a count naming no ownership gives public and private both (writer rule) — held-out 41/48 → 45/48; live-failures 11/13 -> 13/13, routing 88/88, understanding 244/244.
- **Kept** `00d1117`: a date in the question is searched in its printed forms; the writer gives the figure for that date — held-out 41/48 → 45/48; live-failures 11/13 -> 13/13, routing 88/88, understanding 244/244.
- **Kept** `e613a8e`: 'which 3 LGAs' is a kind of place, not a named one (the DTM ranking route kept) — held-out 41/48 → 45/48; live-failures 11/13 -> 13/13, routing 88/88, understanding 244/244.
- **Kept** `df48ceb`: the check judges a deep analysis on its subject only — held-out 41/48 → 45/48; live-failures 11/13 -> 13/13, routing 88/88, understanding 244/244.
- **Kept** `1497bb8`: 'No 2028 budget…' is not a Yes/No verdict — held-out 41/48 → 45/48; live-failures 11/13 -> 13/13, routing 88/88, understanding 244/244.
- **Kept** `28f4a80`: a dash-printed part the draft reports is stated, not missing (check prompt) — held-out 41/48 → 45/48; live-failures 11/13 -> 13/13, routing 88/88, understanding 244/244.
- **Kept** `060614e`: a figure-free statement draft is sent as written — held-out 41/48 → 45/48; live-failures 11/13 -> 13/13, routing 88/88, understanding 244/244.
- **Kept** `79a531d`: drafts kept in the trace (diagnosis, no behaviour change) — held-out 41/48 → 45/48; live-failures 11/13 -> 13/13, routing 88/88, understanding 244/244.
- **Kept** `80440bf`: the reading's LGA beats the words in the area route (Tambuwal's wards, not the state's 244) — held-out 34/37 → 34/37 (33/37 first rerun); live-failures 13/13 -> 12/13, 13/13 on rerun, routing 88/88, understanding unchanged.
- **Kept** `0e34ea1`: a topic figure must carry the day asked (the 17 August 2025 dashboard, not the newest) — held-out 34/37 → 34/37 (33/37 first rerun); live-failures 13/13 -> 12/13, 13/13 on rerun, routing 88/88, understanding unchanged.
- **Kept** `3137cda`: the 'not found' line keeps its spaces when figures are removed (wording only) — held-out 34/37 → 34/37 (33/37 first rerun); live-failures 13/13 -> 12/13, 13/13 on rerun, routing 88/88, understanding unchanged.

## Final comparison: deployed vs branch

Not run (the night ended first).

## Top remaining failures

### wrong figure (6)
- `r1-049-schools` (en): How mnay schools are in Binji? → I mean all of them: primary, JSS, SSS and IQS
  - expected: {'figures': ['77', '123'], 'lead_figure': '77', 'must_any': ['IQS', 'Islamiyya'], 'must_not_figures': ['79'], 'docs': ['asc-sokoto-2023-2024']}
  - got: Binji LGA had *77* public primary, junior secondary and senior secondary schools in 2023/24. /  / • public primary schools in Binji LGA: 70 (page 31) / • public junior secondary schools in Binji LGA: 5 (page 44) / • public senio
  - fails: missing figure 123; none of the names ['IQS', 'Islamiyya']
- `r1-074-schools` (en): How many junioor secondary scools does Yabo have?
  - expected: {'figures': ['14'], 'docs': ['asc-sokoto-2023-2024']}
  - got: The census table prints '-' for private junior secondary schools in Yabo, meaning no figure is given for private JSS. /  / 📄 *Sources:* Sokoto State Annual School Census 23-24 Report, p. 44, 48 /  / Want the figure for another L
  - fails: missing figure 14
- `r1-083-nema` (en): According to NEMA, how many people were affected by floods in Sokoto State as of 12/09/25?
  - expected: {'figures': ['4,278'], 'docs': ['nema-flood-dashboard-2025-09-12'], 'pages': [2]}
  - got: The nearest dated figure printed is 15,675 affected persons in Sokoto State as of 24 September 2025. /  / • Sokoto State affected persons as of 24/09/25: 15,675 (printed on the page) / • Sokoto State affected persons as of 02/
  - fails: missing figure 4,278

### check sent a right answer back (5)
- `r1-024-deep` (ha): Me ke faruwa game da ilimi a Sokoto?
  - expected: {'found': True, 'min_sources': 2, 'route': 'deep'}
  - got: 🧭 Tambaya mai fadi: ina tsara binciken… / --- / 📚 Ina karanta takardu 14: surveys and statistics, plans, budgets, partner reports, policies… (har zuwa minti 3) / --- / ✍️ Ina rubuta taƙaitawa daga alƙaluma 20 da aka tabbatar… / --
  - fails: not found
- `r1-088-schools` (en): How many public primary schools are in Silame?
  - expected: {'figures': ['62'], 'docs': ['asc-sokoto-2023-2024']}
  - got: I couldn't give a checked answer to that: what you asked. The documents I read were Sokoto State Annual School Census 23-24 Report. / [buttons: Show working, Send location]
  - fails: not found; missing figure 62
- `r1-059-surveys` (ha): A cewar MICS 2021, kashi nawa cikin 100 na yara masu watanni 12-23 a Sokoto ne suka samu dukkan rigakafin asali, kuma kashi nawa ne ba su samu ko ɗaya ba?
  - expected: {'any': [['7.2', '50.7']], 'docs': ['mics-2021']}
  - got: Ban iya ba da amsar da aka tabbatar ba: abin da ka tambaya. Takardun da na karanta: Nigeria 2021 Multiple Indicator Cluster Survey (MICS) and National Immunization Coverage Survey (NICS). / [buttons: Nuna lissafi]
  - fails: not found; none of [['7.2', '50.7']]

### wrong figure (check passed it) (5)
- `r1-026-budget` (en): Why Ministry for Special Duties budget drop from 2025 to 2026?
  - expected: {'figures': [], 'any': [['423,000,138.00', '829,500,000.00'], ['423,000,138.00', '829,500,000.00']], 'docs': []}
  - got: The budget documents do not publish reasons for changes and do not show a drop for the Ministry for Special Duties. The approved capital budget was ₦260.00 million in 2025 and ₦622.00 million in 2026, which is an increas
  - fails: none of [['423,000,138.00', '829,500,000.00'], ['423,000,138.00', '829,500,000.00']]
- `r1-092-nema` (en): According to NEMA, how many people were displaced by floods in Sokoto State as of 01/10/2024?
  - expected: {'figures': ['56K'], 'docs': ['nema-flood-sitrep-2024-10-02'], 'pages': [2]}
  - got: The nearest NEMA dashboard in the evidence is as of 21/10/2024 and it prints for Sokoto: DISPLACED PERSONS 50K. /  / • Sokoto DISPLACED PERSONS as of 21/10/2024 (dashboard): 50K /  / 📄 *Sources:* 2024 Floods National Emergency O
  - fails: missing figure 56K
- `r1-012-budget` (en): Which 3 LGAs in Sokoto have the most IDPs?
  - expected: {'figures': ['40,729', '19,151', '17,143'], 'any': [], 'docs': []}
  - got: In Sokoto State, Sabon Birni has the most IDPs with 46,759, followed by Isa with 28,494 and Rabah with 16,082. The state total is 176,099 IDPs in Round 19, reporting date 2026-02-28. /  / 📊 Newest figure: *176,099 IDPs* – in
  - fails: missing figure 40,729; missing figure 19,151; missing figure 17,143

### part dropped (state-level part) (3)
- `r1-005-schools` (en): How many schools are in Shagari? → I mean all of them: primary, JSS, SSS and IQS
  - expected: {'figures': ['131', '123'], 'lead_figure': '131', 'must_any': ['IQS', 'Islamiyya'], 'must_not_figures': ['133'], 'docs': ['asc-sokoto-2023-2024']}
  - got: Shagari LGA had *131* public schools in 2023/24. /  / • public Pre-Primary and Primary schools in Shagari LGA: 108 (page 19) / • public Junior Secondary schools in Shagari LGA: 16 (page 44) / • public Senior Secondary schools in
  - fails: missing figure 123
- `r2-058-schools` (en): Good morning sir/ma, please I would like to humbly ask how many schools are in Kebbe? Thank you very much for your assistance. → I mean all of them: primary, JSS, SSS and IQS
  - expected: {'figures': ['78', '123'], 'lead_figure': '78', 'must_any': ['IQS', 'Islamiyya'], 'must_not_figures': [], 'docs': ['asc-sokoto-2023-2024']}
  - got: Kebbe LGA had *78* public schools in 2023/24. /  / • public primary schools (Pre-Primary and Primary): 66 (page 19) / • public junior secondary schools: 8 (page 44) / • public senior secondary schools: 4 (page 53) /  / The tables pr
  - fails: missing figure 123
- `r2-035-schools` (en): How mnay schols are in Shagari? → I mean all of them: primary, JSS, SSS and IQS
  - expected: {'figures': ['131', '123'], 'lead_figure': '131', 'must_any': ['IQS', 'Islamiyya'], 'must_not_figures': ['133'], 'docs': ['asc-sokoto-2023-2024']}
  - got: Shagari LGA had *131* public schools in 2023/24 (Pre-Primary/Primary, JSS and SSS). /  / • public Pre-Primary and Primary schools in Shagari LGA: 108 (page 19) / • public junior secondary schools in Shagari LGA: 16 (page 44) / •
  - fails: missing figure 123

### double count (2)
- `r1-050-schools` (ha): Makarantu nawa ne suke a Tangaza? → I mean all of them: primary, JSS, SSS and IQS
  - expected: {'figures': ['90', '123'], 'lead_figure': '90', 'must_any': ['IQS', 'Islamiyya'], 'must_not_figures': ['93'], 'docs': ['asc-sokoto-2023-2024']}
  - got: Tangaza tana da makarantu *93* da aka buga adadinsu daban-daban a ƙidayar 2023/24. /  / • makarantun gwamnati na pre-primary da firamare (haɗe): 77 (shafi 19) / • makarantun masu zaman kansu na firamare: 3 (shafi 31) / • makaran
  - fails: missing figure 90; total 90 not in the first line; double count 93
- `r1-063-schools` (en): How many schools are in Gudu?
  - expected: {'figures': ['69', '61', '5', '3'], 'lead_figure': '69', 'must_not_figures': ['69'], 'docs': ['asc-sokoto-2023-2024']}
  - got: Gudu LGA had *69* schools in 2023/24. /  / • public Pre-Primary and Primary schools in Gudu LGA (pre-primary counted with pri: 61 (page 31) / • public Junior Secondary schools in Gudu LGA: 5 (page 44) / • public Senior Secondary
  - fails: double count 69

### not found (missing pages) (1)
- `r2-088-nema` (en): Abeg according to NEMA, how many ppl were affected by floods for Sokoto State as of 21/10/24?
  - expected: {'figures': ['102K'], 'docs': ['nema-flood-sitrep-2024-10-22'], 'pages': [2]}
  - got: I couldn't find the answer to that in the documents I have. / [buttons: Menu]
  - fails: not found; missing figure 102K

