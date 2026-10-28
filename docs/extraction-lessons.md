# Extraction lessons

Every document problem Kasafi has had, why it happened, how it was fixed, and the test that keeps it fixed.
Read this before changing `app/retrieval/indexer.py`, `app/retrieval/quality.py` or the answer rules.

**Ground rules**
- Every fix gets a regression test on the **real page** (`tests/test_extraction_regressions.py`). Those tests
  run the real indexing pipeline on the real PDF pages, and are skipped only when `data/` isn't downloaded.
- New problems get a lesson here and, where a check can catch the whole class, a quality check
  (`app/retrieval/quality.py`). Failing documents go to the review queue (`gaps`, reason `quality`).
- Any indexer change means re-indexing (`scripts/index_docs.py --force`) and `deploy/deploy.sh --sync-index`.

| # | Problem | Cause | Fix | Test |
|---|---|---|---|---|
| L1 | Wrong column: "allocated to education" answered with another year's figure (eval 11). | Budget tables reach us as rows of bare numbers; the header is on an earlier line or page, and the model counted positions. | Rows are labelled in code ("05 Education \| 2026 Approved Budget: …"), only when the value count matches the header exactly. | `test_L1_rows_labelled_with_their_column_2026_p40`, eval 01, 11 |
| L2 | 2024 budget rows stayed unlabelled. | Its header wraps almost one word per line, and splits across a page break. | Headers may run 14 lines and continue onto the next page. | `test_L2_header_wrapped_one_word_per_line_2024_p113` |
| L3 | A row name ("Bureau for Public Procurement …") was swallowed into the last column's label. | Any line after a header was taken as header text. | A header line must look like header text (`_HEADER_WORDS`) and have no amount or row code. | `test_L3_row_name_not_swallowed_into_a_column_2025_p15` |
| L4 | 2025 budget rows labelled with the previous table's title. | PDFium returns text in content order; these PDFs store the title (printed at the top) as the last line. | `titles_first`: a title line near the end but drawn in the top 15% of the page moves to the start. A full visual re-order was rejected (scrambled headers, 20× slower). | `test_L4_title_printed_at_the_top_comes_first_2025_p11`, eval 18 |
| L5 | In the amended budget, plain "Total Expenditure" rows replaced real table titles. | The rule that a Total row starts a new table applied to every Total row. | Only a Total row of a *different kind* (personnel, overhead, capital, debt) switches the title. | `test_L5_plain_total_row_keeps_the_table_title_amended_p7` |
| L6 | Overhead / capital rows filed under the total-expenditure title. | Kind tables follow each other without a printed title. | A "Total Capital Expenditure" row starts "Capital Expenditure (table starting at its Total row)". | `test_L6_kind_total_row_starts_its_own_table_2025_p15` |
| L7 | A ministry's total (12-digit code ending in eight zeros) or a sector total never reached the answer. | Whole-page keyword ranking buried it under tables of contents and long project lists. | Sector, ministry and "Total" rows are also indexed as one-row key chunks with their table title; search tries key rows first. | `test_L7_ministry_total_row_is_its_own_key_row_bir_q4_2025_p17`, eval 17, 18 |
| L8 | The matching row was cut off the evidence (2026 p40 "04 Health"). | Evidence joined a hit with its neighbours in page order, then truncated. | The chunks that matched come first, neighbours after. | eval 01 |
| L9 | Scanned pages had no text (SMART Agenda). | No text layer. | Muse Spark vision OCR (`app/retrieval/ocr.py`, `scripts/ocr_pages.py`; fetched documents in the background). | `test_L9_scanned_page_has_no_text_layer_smart_agenda_p3` |
| L10 | "₦9.08 billion" for the Ministry for Religious Affairs was its headquarters only. | Budget codes are hierarchical: 017200000000 (ministry) vs 017200100100 (headquarters). | Answer rule 3c: use the higher-level code unless the headquarters is asked for. | eval 18 |
| L11 | Bracketed numbers: is "(3.01%)" negative? | Financial statements write negatives as "(56,893,525,653.90)"; prose uses brackets as brackets ("Sokoto (3.01%)" is +3.01%; the same sentence writes "Adamawa (-6.10%)"). | Only accounting-shaped amounts (thousands separators and two decimals) or two-decimal labelled cells become "-…" at indexing; answer rule 6d and the renderer drop brackets around prose figures. | `test_L11_accounting_negative_audited_2024_p46`, `tests/test_negatives.py` |
| L12 | The NBS state CPI table (with Sokoto's published 8.0% y/y) was never read. | The page is an image under a 92-character text title, above the 40-character "has text" threshold, so it wasn't OCR'd. | Pages with under 400 characters of text and an image covering a quarter of the page go to OCR (`image_table_pages`); 111 seed pages were affected. | `test_L12_picture_of_a_table_is_sent_to_ocr_cpi_p19` |
| L13 | OCR'd tables were bare numbers ("Sokoto \| 127.0 \| 125.1 \| …"). | OCR returns pipe tables with two-line headers (blank cells where a heading spans two columns); OCR'd pages were chunked without labelling. | `label_pipe_tables` combines the header lines and labels rows; labelled rows are key rows; OCR'd pages use the same chunking as text pages. | `tests/test_ocr_tables.py` |
| L14 | NBS CPI downloads failed as "not a PDF". | NBS ships each edition as a ZIP (PDF + spreadsheet). | ZIPs are accepted and unpacked in the sandbox, with zip-bomb limits; provenance is the PDF's hash. | `tests/test_editions.py::test_unzip_*` |
| L15 | A budget code and a quantity landed in value cells ("2025 Revised Budget: (25,000) \| Q1 Performance: 23020105", amended p114). | A wrapped line made the value count match by accident. | A bare 5+-digit number (a code) in a value position means the row isn't labelled; the quality check flags codes and bracketed values in cells. | `test_L15_code_and_quantity_never_land_in_value_cells_amended_p114` |
| L16 | **Open.** Citations use the PDF page, but some documents print other numbers (BIRs: printed = PDF − 1; MTEF: − 6). | Cover pages aren't numbered. | The quality check reports the offset (warning). Next: show both in citations ("page 17, printed 16"). | `test_L16_printed_page_offset_is_reported_bir_q4_2025` |
| L17 | A correct answer was replaced by "couldn't verify". | It said "September 2026"; the evidence row only has "Sep-26", so 2026 looked like an unverified figure. | The number check also accepts the cited document's own title and year. | `test_L17_edition_year_from_the_title_is_not_an_unverified_figure` |
| L18 | "Year-on-year" questions didn't find a column headed "YoY". | Keyword search doesn't know abbreviations. | Pipe-table headers are spelled out (YoY → Year-on-Year, MoM → Month-on-Month, Sep-25 → Sep 2025). | `tests/test_ocr_tables.py` |
| L19 | The BIRs' "22 - OTHER RECURRENT COSTS (EXCLUDING 2201)" row was unlabelled in all three reports. | "2201)" (half a bracket) was accepted as a value, so the row seemed to have one value too many. Found by the totals quality check. | Values need balanced brackets. | `test_L19_name_ending_in_a_bracketed_code_is_labelled_bir_q4_2025_p9` |

| L20 | "Tertiary education capital 2026 vs 2025" got "I couldn't find the answer". | The figures are 4-digit function rows (7094) in two documents; page search can't find a row in two documents and compare them. | Structured `budget_rows` from every labelled table cell (`app/retrieval/tables.py`) and `query_budget` computing in code (`app/agent/budget_query.py`). | `tests/test_budget_query.py`, `evals/complex` c01 |
| L21 | Rankings listed "Social Sector"; totals counted a ministry and its own university twice. | Administrative codes are hierarchical: 050000000000 is a sector grouping, 056900400100 sits inside 056900000000. | Ministries are 4 digits + 8 zeros (not 2 + 10); a unit inside a picked parent is folded in and reported as "included". | `test_ranking_lists_ministries_not_sectors`, `test_units_inside_a_picked_ministry_are_not_counted_twice` |
| L22 | "College of Education" found nothing. | The 2026 budget prints "Shehu Shagari **Collage** of Education"; names were matched as whole phrases. | Units match by meaningful words (filler words dropped, plurals and that misprint normalised). | `test_unit_names_match_by_meaningful_words` |
| L23 | "Other Non-Debt Recurrent" tables were typed as debt. | The word "Non-Debt" contains "debt". | Overhead is checked before debt. | `tests/test_budget_tables.py` |
| L24 | "How much for education?" switched from the programme sector (₦128.50 bn) to the function line (₦117.75 bn). | Two classifications total a sector differently. | A whole sector is the programme sector line; a level within it (tertiary) is the function line; one-sector lookups stay on normal search. | eval 01, 11 |

## Quality checks at indexing time

`app/retrieval/quality.py` runs on every document as it's indexed (seed or fetched):

| Check | Fails when | Catches |
|---|---|---|
| `labelled_rows` | a budget or performance document has no labelled rows at all | a new table layout (L1–L3) |
| `code_in_cell` | a labelled cell holds a bare budget code | L15 |
| `bracket_cell` | a labelled cell is still in brackets | L11, L15 |
| `totals` | 2-digit rows don't add up to the Total row of their group (within 0.5%) | a missing or mislabelled row (L19) |
| `units` *(warning)* | tables are in thousands or millions | answers that drop the unit |
| `page_numbers` *(warning)* | printed and PDF page numbers differ by a fixed offset | L16 |
| `image_pages` *(warning)* | pages still wait for OCR | L9, L12 |

Failing documents are listed in the review queue: `SELECT missing_doc, detail FROM gaps WHERE reason = 'quality' AND status = 'open'`.
As of 28 October 2026 only `appropriation-law-2026` fails (its schedules have no labelled rows).
