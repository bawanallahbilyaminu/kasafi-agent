# Multi-source topic questions

Twelve hand-written questions that need more than one publisher's figures, for the rules in
`app/agent/topics.py`:

- **Measure identity.** Every fact card carries its kind of number: an index value (0–1), a headcount %, an
  intensity %, a rate, a count or an amount. It also carries whose figure it is (the whole population or a group,
  such as children for a Child MPI) and its area (the state or a district). A change or comparison is computed only
  between the same measure, population and area. Anything else is shown side by side and said to be a different
  measure.
- **Primary vs secondary.** When a document quotes another publisher's figure ("according to the 2022 Nigeria
  MPI"), the card is labelled "NBS …, as cited in …", and that publisher's own document is sought.
- **Named publishers are required.** "According to NBS" means NBS's own document: from the registry's URLs, then its
  listing, then a search. If it can't be obtained, the reply says so, and never gives another publisher's figure as
  NBS's.
- **Change questions.** Code computes the change from a same-measure pair and gives its direction and size, with a
  note when the two come from different surveys.
- **Follow-ups that name a source.** "There's an NBS MPI report from 2022" answers the earlier question again, with
  that source required.

Run this set **before deploys only**:

    uv run python evals/complex/run_open.py --file evals/topics/multi_source.json --out evals/topics/report.md

The checks are in `multi_source_checks.json`. Some of the documents these questions need were fetched on Oct 30
(NBS MPI 2022). On the server they are fetched the first time they are asked for, or copied with `--sync-index`.

## Drafted expected answers (Oct 30 2026, for Bilyaminu to check)

Page numbers are PDF pages (the printed page is in brackets where it differs).

| id | expected | pages |
|---|---|---|
| t01, t02 | **NBS 2022:** Sokoto MPI 0.409, incidence 90.5%, intensity 45.2%. **SBS 2025:** MPI 0.239, headcount 59.1%, intensity 40.3%. **Change** in the MPI value: 0.409 → 0.239, down 0.17 (41.6%). The headcount change and the intensity change are given only as their own pairs. The note says these are different surveys: SBS (p31) warns about direct comparison, and covers 18 accessible LGAs. | nbs-mpi-2022 p123 (101), Appendix D; mpi-2025-sokoto p13, p33, p34 |
| t03 | As t01, with NBS's own report cited (not only SBS's quote of it). | as t01 |
| t04 | 91% is **NBS's** 2022 figure, as quoted by SBS (MPI 2025 p17, "the 2022 National MPI") and by the SBS/JIPS/DRC report (p12). NBS's own report: 91% (summary, p16) and 90.5% (table, p123). SBS's own figure is 59.1% (2025). | nbs-mpi-2022 p16, p48, p123; mpi-2025-sokoto p17; durable-solutions-2026-sokoto p12 |
| t05 | No. 91% is a headcount (NBS 2022) and 0.239 is an MPI value (SBS 2025), which are different measures. Like for like: MPI 0.409 → 0.239; headcount 90.5% → 59.1%. | as t01 |
| t06 | **IOM DTM:** 181,526 (Round 18, 31 Oct 2025). **UNHCR:** 176,099 (dashboard, 1 Oct 2026). **SBS/JIPS/DRC:** "over 181,500" (early 2026), from its footnote 1, so another publisher's count as cited; its survey covers Sokoto town only. | DTM API; unhcr-fdp-2026-10 p1; durable-solutions-2026-sokoto p6, p12 |
| t07 | Round 16 (30 Nov 2024): 99,729 → Round 17 (31 May 2025): 88,562 → Round 18 (31 Oct 2025): 181,526. | DTM API pull |
| t08 | **NBS NLFS 2023:** Sokoto unemployment rate 1.2% (male 1.3%, female 1.1%), with NBS's definition note. **SBS/JIPS/DRC, Sokoto town:** IDPs 14% unemployed, non-displaced 5%. These are different populations and areas, so no change is computed. | nbs-nlfs-2023 p45 (31), Table 11; durable-solutions-2026-sokoto p68 (57), Annex I |
| t09 | 3.8% of employed people are employees. That's NBS NLFS 2023's figure, as cited in the SBS/JIPS/DRC report (p40), not the report's own (NLFS Table 8: employees 3.8%, self-employed 96.2%). The report also quotes the 82.1% employment-to-population ratio as "Sokoto town", but NLFS reports by state. | durable-solutions-2026-sokoto p39–40; nbs-nlfs-2023 p34–35 (20–21), Table 8 |
| t10 | September 2026: Sokoto headline inflation 8.0% year on year and 3.01% month on month (3.0 in the appendix); food 6.1% year on year, −1.6% month on month. | nbs-cpi-2026-09 p16–17, p19 |
| t11 | NDHS 2024: 42.8% of children under 5 are stunted (below −2 SD height-for-age; 14.8% severely). No change can be computed, because the library has no earlier comparable figure (MICS 2021 has no anthropometry). | ndhs-2024 p366 (322), Table 11.1 |
| t12 | 90.5% (NBS 2022) → 59.1% (SBS 2025): down 31.4 percentage points. With NBS's summary figure of 91%, it's down 31.9 points. Different surveys, so the change is indicative. | nbs-mpi-2022 p123; mpi-2025-sokoto p33 |
