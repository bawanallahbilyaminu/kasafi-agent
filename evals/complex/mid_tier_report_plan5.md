# Open-question run: mid_tier.json

39 questions: answered 23, partial 12, not found 3, unverified 1 | wrong 1 of 11 checked (m37) | median 11.9s

```
plan          n=39 median   3.6s    30% of all time
line_search   n=33 median   1.1s     8% of all time
read          n=33 median   5.0s    38% of all time
read1         n=33 median   3.8s    29% of all time
read2         n=33 median   3.6s    26% of all time
reread        n= 5 median   4.6s     5% of all time
page_search   n=34 median   0.9s     7% of all time
compose       n=25 median   5.7s    33% of all time
answer        n=37 median   5.6s    53% of all time
row readings: 75 model calls for 33 questions (2 = no retry)
```

## m01: answered (lines:sum, 9.7s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
I, akwai kudaden tallafin karatu da aka ware wa dalibai a kasafin 2026. Tallafin karatu na cikin gida (Domestic Scholarship) ₦1.60 biliyan aka ware, tallafin karatu na kasashen waje (FOREIGN SCHOLARSHIP SCHEME) kuma ₦1.50 biliyan aka ware. Jimillarsu ₦3.10 biliyan (lissafin Kasafi). Dukkan kudaden da aka ware ne (budgeted), ba wanda aka kashe ba.

• Domestic Scholarship (code 22021025), 2026 Approved Budget: ₦1.60 biliyan
• FOREIGN SCHOLARSHIP SCHEME (code 22021020), 2026 Approved Budget: ₦1.50 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m02: partial (lines:list, 18.6s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
SUBEB classroom construction had two approved lines in 2025 of ₦4.55 billion and ₦500.00 million, both allocated (budgeted). For renovation (rehabilitation/repairs of public schools), ₦205.00 million was budgeted in 2025 Revised and ₦205.00 million was allocated in 2026 Approved. No 2026 SUBEB classroom construction line is shown.

• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦4.55 billion
• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦500.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million
• Not found: 2026 SUBEB classroom construction (construction/provision of public schools)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 29; Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: answered (lines:list, 9.9s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
Specific lines are shown for all three areas in the 2026 approved budget. Girl-child education is covered by the Female Education Board, plus Girls secondary schools and the Girls Education Project. Boarding / school feeding is covered by Meal Subsidy to Government Schools and the School feeding programme. Retention is covered under Increase in access, retention, and completion rate at all levels. All figures are allocated (budgeted), not spent.

• Female Education Board (one agency or unit, all spending (total), code 051705700100), 2026 Approved Budget: ₦1.16 billion
• Girls secondary schools (Female Education Board) – purchase of industrial equipment, 2026 Approved Budget: ₦45.00 million
• Girls Education Project (11) with State to State (Ministry for Basic Education), 2026 Approved Budget: 0.00
• MEAL SUBSIDY TO GOVERNMENT SCHOOLS (code 22050102), 2026 Approved Budget: ₦2.00 billion
• School feeding (programme inside a sector, all spending (total), code 050203), 2026 Approved Budget: ₦2.03 billion
• … +1

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 40, 41, 65, 67, 149
_Reply *show working* to see the rows and arithmetic._
```

## m04: answered (lines:share, 17.4s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
The 2026 approved health sector allocation is ₦120.13 billion out of Total Expenditure of ₦758.70 billion. 15.8% of the 2026 approved budget's Total Expenditure goes to health (Kasafi's calculation); the Abuja Declaration benchmark is shown alongside.

• HEALTH (all spending (total), code 707), 2026 Approved Budget: ₦120.13 billion ↑
• Total Expenditure, 2026 Approved Budget: ₦758.70 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1, 32
_Reply *show working* to see the rows and arithmetic._
```

## m05: answered (category, 6.8s)

**Q:** Nawa aka ware wa sayen magunguna da kayan aiki na asibitoci a karkashin Ma'aikatar Lafiya a kasafin 2026?

```
A kasafin 2026 da aka amince, a duk jihar: DRUGS/LABORATORY/MEDICAL SUPPLIES (22020307) ₦2.71 biliyan; PURCHASE OF HEALTH / MEDICAL EQUIPMENT (23010122) ₦31.56 biliyan, jimilla ₦34.27 biliyan (lissafin Kasafi). Ministry of Health da hukumominta: ₦32.75 biliyan, 95.6% na jimillar jihar (lissafin Kasafi). Zuwa ƙarshen Yuni 2026, an kashe ₦559.92 miliyan daga ciki a duk jihar (1.6%, Budget Implementation Report Q2 2026).

Mafi girma:
• Ministry of Health: ₦31.52 biliyan
• Primary Health Care Development Agency: ₦590.00 miliyan
• Agency for Malaria Control: ₦404.73 miliyan
• Specialist Hospital: ₦123.06 miliyan
• Orthopedic Hospital Wamakko: ₦94.00 miliyan

✓ Layukan hukumomi sun yi daidai da jimillar jihar da aka buga.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 28, 29, 161, 162, 163, 164, 165, 166, 170; Budget Implementation Report Q2 2026, shafi 30, 32
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m06: partial (lines:list, 10.0s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
• Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health), 2026 Approved Budget: ₦70.00 million
• 04050126007201 - Functional health facilities Basic Health Care Provision Funds (BHCF) 25% Counterpart, 2026 Approved Budget: ₦109.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): 04050124000403 - Functional health facilities BHCF Counterpart Funds for SOCHEMA (2026 Approved Budget); BHCF Counterpart Funds for SOCHEMA (Sokoto State contributory health care mgt agency) (2026 Approved Budget); Support for Family Planning Programme (Counterpart) (Primary Health Care Development Agency) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 67, 229
_Reply *show working* to see the rows and arithmetic._
```

## m07: partial (search, 17.7s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
The budget doesn't show maternal and child healthcare centers across rural LGAs separately; the Ministry of Health's total capital Year to Date (Q1-Q2) is ₦3.75 billion (3.9% of the revised budget), and a state facility located in an LGA is not an allocation to that LGA.

• 2026 capital Year to Date (Q1-Q2) for PUBLIC HEALTH SERVICES (total, not the item): ₦264.26 million (0.4% of the revised budget)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 28, 43; Sokoto State FY 2026 Budget, p. 45
```

## m08: answered (category, 5.4s)

**Q:** Nawa gwamnatin jihar Sokoto ta ware don sayen takin zamani da tallafin kayan noma a shekarar 2026, kuma nawa aka riga aka kashe?

```
A kasafin 2026 da aka amince, a duk jihar: PURCHASE OF AGRICULTURAL INPUTS (23010140) ₦5.65 biliyan. Zuwa ƙarshen Yuni 2026, an kashe ₦2.43 biliyan daga ciki a duk jihar (43.0%, Budget Implementation Report Q2 2026).

Mafi girma:
• Ministry of Agriculture & Natural Resource: ₦2.44 biliyan
• Nigeria CARES- Fadama Programme: ₦2.00 biliyan
• Commodity Board: ₦550.00 miliyan
• Livestock Development Programme: ₦300.00 miliyan
• International Fund for Agriculture: ₦150.00 miliyan

✓ Layukan hukumomi sun yi daidai da jimillar jihar da aka buga.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 30, 108, 110, 116, 138; Budget Implementation Report Q2 2026, shafi 32
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m09: partial (lines:list, 14.8s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
The budgets show separate capital line-items for irrigation schemes and for tube wells, but no line-item described as solar-powered tube wells. Irrigation Scheme Youth empowerment (NEMI NA KANKA) is allocated ₦200.00 million in 2025 Revised and ₦200.00 million in 2026 Approved. Kware irrigation scheme (SPIN Project) is allocated ₦200.00 million in 2025 Revised and ₦800.00 million in 2026 Approved. Construction of Tube Wells across the State is allocated ₦531.96 million in 2025 Revised and 0.00 in 2026 Approved. All figures are budgeted allocations, not spent amounts.

• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦800.00 million
• Construction of Tube Wells across the State (Nigeria CARES- Fadama Programme) [Capital Expenditure by Project], 2025 Revised Budget: ₦531.96 million
• … +1
• Possibly relevant too, not counted (I wasn't sure on a second reading): through Construction Solar powered boreholes (Department for Rural Water) (2025 Revised Budget); through Construction Solar powered boreholes (Department for Rural Water) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 53
_Reply *show working* to see the rows and arithmetic._
```

## m10: answered (lines:list, 10.9s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
I, an ware kuɗaɗe a kasafin 2026. Gyaran madatsun ruwa na Rafin Duma yana da ₦54.56 miliyan da aka ware (budgeted). Gyaran ayyukan ruwan birnin Sokoto (Sokoto Township Water Works) yana da ₦25.00 biliyan da aka ware, da gyaran manyan tankokin ruwa a cikin birnin yana da ₦35.00 miliyan da aka ware.

• Rehabilitation and expansion of earth dams at Rafin Duma (Ministry of Water Resources), 2026 Approved Budget: ₦54.56 miliyan
• Rehabilitation of Sokoto Township Water Works (Water Board), 2026 Approved Budget: ₦25.00 biliyan
• Rehabilitation of Overhead Tanks within Sokoto Metropolis (Water Board), 2026 Approved Budget: ₦35.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 58
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 8.8s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
The combined 2026 approved allocation for animal health and livestock diseases management and livestock feeds development, which covers grazing reserves, is ₦13.30 billion (Kasafi's calculation). These are budgeted allocations, not spent amounts.

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Livestock feeds development (programme inside a sector, all spending (total), code 010206), 2026 Approved Budget: ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40
_Reply *show working* to see the rows and arithmetic._
```

## m12: partial (lines:list, 10.4s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
The 2026 budget does not list flyovers, inner-city dualization and rural feeder roads as separate projects. The broader capital totals that would contain them are ₦42.26 billion for the Ministry of Works unit and ₦15.47 billion for the Department for Rural Roads, both 2026 Approved Budget allocations (budgeted, not spent).

• Ministry of Works (one agency or unit, capital, code 023400100100), 2026 Approved Budget: ₦42.26 billion
• Department for Rural Roads (one agency or unit, capital, code 023405700100), 2026 Approved Budget: ₦15.47 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Possibly relevant too, not counted (I wasn't sure on a second reading): Ministry of Works (2026 Approved Budget); Department for Rural Roads (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 26
_Reply *show working* to see the rows and arithmetic._
```

## m13: not found (search, 10.0s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m14: answered (lines:sum, 10.4s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
An ware jimillar ₦6.38 biliyan (lissafin Kasafi) a kasafin kudin 2026 da aka amince da shi don gina sabbin gidaje. Wannan ya hada da ₦4.00 biliyan don gina rukunin gidaje 500 a Gidan Salanke, da ₦2.00 biliyan don gina rukunin gidaje 500 a Wajekke, Wamakko, da ₦382.98 miliyan don kammala gidan ma’aikata 53 a Jami’ar Jihar Sokoto. Dukkan adadin da aka ware ne (budgeted), ba wanda aka kashe ba.

• Construction of 500 Housing units at Gidan Salanke (Min of Lands and Housing), 2026 Approved Budget: ₦4.00 biliyan
• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan
• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: answered (search, 12.1s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
Ee, kasafin 2026 ya ware ₦1.50 biliyan don siyayyar bas don sufuri a ciki da wajen jihar. Wannan kuɗi ne da aka ware (manyan ayyuka), ba kuɗin da aka kashe ba.

• 2026 approved budget (manyan ayyuka): ₦1.50 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 55
```

## m16: answered (search, 11.1s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
The State Government projected ₦47.94 billion as 2025 IGR in the final budget, and collected ₦20.58 billion in Q1–Q4 2025 (42.9% of the final budget). The 2026 IGR target is ₦74.52 billion.

• 2025 original budget: ₦47.44 billion
• 2025 collection January–September 2025 only: ₦14.62 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1, 11; Budget Implementation Report Q4 2025, p. 9, 13
```

## m17: answered (lines:ratio, 8.7s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
The approved 2026 budget allocates ₦553.34 billion to Capital Expenditure and ₦205.36 billion to Recurrent Expenditure. The exact ratio of Capital to Recurrent is 2.69 : 1 (Kasafi's calculation).

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (search, 11.8s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
Sokoto State's 2026 approved budget (allocated) earmarks ₦10.03 billion for domestic principal and ₦6.00 billion for domestic interest. It earmarks ₦2.42 billion for foreign principal and ₦1.31 billion for foreign interest. Total debt service for 2026 is ₦19.76 billion.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 25, 29
```

## m19: answered (lines:compare, 13.5s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
• Difference (2026 Approved Budget vs 2025 Approved Budget): -₦489.02 million (-11.6%) (Kasafi's calculation)

• Government House (one agency or unit, overhead (running costs), code 011100100100), 2025 Approved Budget: ₦4.20 billion
• Government House (one agency or unit, overhead (running costs), code 011100100100), 2026 Approved Budget: ₦3.71 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 14; Sokoto State FY 2026 Budget, p. 21
_Reply *show working* to see the rows and arithmetic._
```

## m20: answered (search, 11.6s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa ƙarshen zangon farko (Q1) na 2026, an kashe 3.0% na kasafin babban aiki na daukacin jihar. Kasafin da aka amince da shi (manyan ayyuka) shi ne ₦553.34 biliyan, adadin da aka kashe a Q1 shi ne ₦16.82 biliyan.

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 27
```

## m21: answered (query_budget:rank, 15.5s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
The lowest capital absorption rate for Q1–Q2 2026 is 0.0% of the 2026 Revised Budget, shared by the Ministry for Skills Acquisition and Entrepreneurship Development, Ministry of Commerce and Industry, Ministry of Culture & Tourism, Ministry of Justice, Ministry of Solid Minerals and Natural Resources, Ministry for Local Government and Chieftancy, and Ministry for Special Duties, so no single three can be picked out. The same 0.0% is also recorded for the Fiscal Responsibility Commission, Sokoto State House of Assembly and Sokoto State Independent Electoral Commission.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 26, 27, 28
_Reply *show working* to see the rows and arithmetic._
```

## m22: answered (search, 3.8s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
*Ministry of Health* (code 052100000000):
• Total: share of the revised budget spent 10.6% (Kasafi's calculation); approved budget ₦124.41 billion; spent so far (Q1–Q2) ₦12.36 billion

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18; Sokoto State FY 2026 Budget, p. 18
```

## m23: answered (search, 12.4s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
2026 approved personnel budget (personnel) was ₦70.57 billion. Actual payroll outturn through the first half (Q1–Q2 2026) was ₦37.30 billion (52.8% of the revised budget). The balance (budget variance) was ₦33.28 billion.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19
```

## m24: partial (lines:list, 16.7s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Babu layin da aka ware daban don horar da matasa sana'o'i da tallafin kudi a Ma'aikatar Matasa da Wasanni a 2026. Abin da aka buga shi ne jimillar Ma'aikatar Matasa da Wasanni gaba daya, ₦17.06 biliyan a kasafin 2026 da aka amince. Wannan jimilla ce, ba kudin horarwa da tallafi kadai ba.

• Ministry of Youth and Sports Development (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 051300000000), 2026 Approved Budget: ₦17.06 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.
• Ba a samu ba: horar da matasa sana'o'i da tallafin kudi na Ma'aikatar Matasa da Wasanni

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m25: partial (lines:list, 14.7s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
Yes, the 2026 approved budget shows dedicated lines. Welfare support for disability is budgeted as ₦3.07 billion, special school rehabilitation for Raji Special School is ₦500.00 million, and therapeutic appliances and equipment is ₦50.00 million. All figures are approved allocations, not spending.

• THERAPEUTIC APPLIANCES AND EQUIPTMENT (code 70713), 2026 Approved Budget: ₦50.00 million
• Raji Special School (Ministry for Basic Education), 2026 Approved Budget: ₦500.00 million
• DISABILITY (all spending (total), code 71012), 2026 Approved Budget: ₦3.07 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): DISABILITY (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 33, 65, 188
_Reply *show working* to see the rows and arithmetic._
```

## m26: partial (lines:list, 13.1s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
• Ministry for Women Affairs (ministry total including its agencies, all spending (total), code 051400000000), 2025 Approved Budget: ₦8.44 billion
• Ministry for Women Affairs (ministry total including its agencies, all spending (total), code 051400000000), 2026 Approved Budget: ₦7.24 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Possibly relevant too, not counted (I wasn't sure on a second reading): Ministry of Social Welfare & Community Development (2025 Approved Budget); Ministry of Social Welfare & Community Development (2026 Original Budget)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
_Reply *show working* to see the rows and arithmetic._
```

## m27: partial (search, 15.8s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
Kasafin bai nuna kudi daban ga ƙananan hukumomin kan iyaka don raya karkara da rage talauci ba. Layin jiha da ke cikin ƙaramar hukuma ba kudin waccan ƙaramar hukumar ba ne, ƙananan hukumomi suna da rabon kansu daban.

• 2026 kasafin da aka amince (jimilla) — fannin Ruwa da Raya Karkara: ₦44.37 biliyan
• 2026 kasafin da aka amince (manyan ayyuka) — Shirin Rage Talauci: ₦1.70 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 25, 41, 45, 49, 173
```

## m28: partial (lines:list, 9.9s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
The budget tables show the 2026 personnel budget but do not state whether it includes the national minimum wage. The 2026 Approved Budget for PERSONNEL COST is ₦70.57 billion (allocated/budgeted, not spent). No line in the provided tables is labeled as minimum wage implementation across MDAs.

• PERSONNEL COST (code 21), 2026 Approved Budget: ₦70.57 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m29: answered (lines:compare, 11.9s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
• Bambanci (2026 Approved Budget vs 2025 Approved Budget): -₦4.12 biliyan (-45.2%) (lissafin Kasafi)

• GRATUITY (manyan ayyuka, code 21030101), 2025 Approved Budget: ₦9.12 biliyan
• GRATUITY (manyan ayyuka, code 21030101), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 27
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 9.9s)

**Q:** How much was budgeted for staff training, civil service computerization, and promotion arrears in the 2026 budget?

```
Statewide, the 2026 approved budget has LOCAL TRAINING (22020501) ₦6.80 billion; INTERNATIONAL TRAINING (22020502) ₦1.82 billion; COMPUTER SOFTWARE ACQUISITION (23050102) ₦1.41 billion, ₦10.03 billion together (Kasafi's calculation). By the end of June 2026, ₦653.93 million of it had been spent statewide (6.5%, Budget Implementation Report Q2 2026).

Largest:
• Department for Security Matters: ₦1.80 billion
• State Universal Basic Education Board (SUBEB): ₦938.00 million
• Office of Head of Service: ₦663.00 million
• Ministry for Basic Education: ₦550.00 million
• Fertilizer and Agricultral Supplies Company: ₦534.35 million

✓ The agencies' rows add up exactly to the printed statewide totals.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 28, 31, 84, 97, 104, 112, 113, 120, 127, 134, 149, 150, 158; Budget Implementation Report Q2 2026, p. 31, 34
_Reply *show working* to see the rows and arithmetic._
```

## m31: partial (lines:list, 13.1s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
The 2026 Approved Budget does not show a separate line named "Sokoto State Community Guard Corps"; provision for the Corps and internal security logistics is under the Department for Security Matters. The Department's total approved allocation is ₦26.37 billion, made up of ₦18.00 billion overhead, ₦8.30 billion capital and ₦63.37 million personnel. Specific logistics support lines shown include ₦405.00 million for Purchase of 250 Bajaj Motorcycles for Security Guards and ₦550.00 million for motor vehicles as assistance to security agencies. The economic classification also shows ₦8.62 billion for SECURITY SERVICES and ₦8.21 billion for SECURITY VOTE (INCLUDING OPERATIONS) as allocated.

• Department for Security Matters (one agency or unit, all spending (total), code 017000100200) [Total Expenditure by Administrative Classification], 2026 Approved Budget: ₦26.37 billion
• Department for Security Matters (one agency or unit, overhead (running costs), code 017000100200) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2026 Approved Budget: ₦18.00 billion
• Department for Security Matters (one agency or unit, capital, code 017000100200), 2026 Approved Budget: ₦8.30 billion
• Department for Security Matters (one agency or unit, personnel (salaries), code 017000100200), 2026 Approved Budget: ₦63.37 million
• Purchase of 250 No Bajaj Motor cycle for Security Guards (Department for Security Matters), 2026 Approved Budget: ₦405.00 million
• … +3
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 19, 22, 25, 28, 51, 52
_Reply *show working* to see the rows and arithmetic._
```

## m32: answered (lines:list, 12.3s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
The 2026 approved capital for renovation of 25 Upper and lower Sharia Courts is ₦102.06 million. For the State Judiciary (administration of justice), the 2026 approved capital is ₦3.39 billion, personnel is ₦1.60 billion and overhead is ₦3.18 billion. All figures are budgeted allocations.

• Renovation of 25No Upper and lower Sharia Courts (Shari’a Court of Appeal), 2026 Approved Budget: ₦102.06 million
• State Judiciary (ministry total including its agencies, capital, code 031800000000) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦3.39 billion
• State Judiciary (ministry total including its agencies, personnel (salaries), code 031800000000) [Personnel Expenditure by Administrative Classification], 2026 Approved Budget: ₦1.60 billion
• State Judiciary (ministry total including its agencies, overhead (running costs), code 031800000000) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2026 Approved Budget: ₦3.18 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26, 63
_Reply *show working* to see the rows and arithmetic._
```

## m33: partial (lines:sum, 15.7s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
Security vote is allocated ₦5.50 billion in 2025 and ₦8.21 billion in 2026. The combined allocation for security votes across the two years is ₦13.71 billion (Kasafi's calculation). No separate line for contingency funds is shown, so it is not included.

• SECURITY VOTE (INCLUDING OPERATIONS) (capital, code 22020604), 2025 Approved Budget: ₦5.50 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion
• Not found: contingency funds

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 17; Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m34: not found (search, 9.4s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Ban sami amsar wannan tambayar a cikin takardun da nake da su ba.
```

## m35: answered (lines:list, 13.4s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
The Sokoto State Independent Electoral Commission is shown as one agency. Its 2026 Approved Budget is ₦460.48 million.

• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: unverified (search, 16.3s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
I found documents about your question, but couldn't verify the figures. Please check these sources:

[6] Sokoto State FY 2026 Budget, page 26
[7] Sokoto State FY 2026 Budget, page 47
```

## m37: answered WRONG: none of [['3,301,437,040.18']] (lines:compare, 15.5s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
Jimillar kasafin bangaren ICT a 2025 ita ce ₦1.49 biliyan. A 2026 kuma jimillar ta kasance ₦3.70 biliyan. Dukkanin adadin da aka ware ne (approved budget), ba kudin da aka kashe ba.

• Information Communication and Technology (jimillar ɓangare, manyan ayyuka, code 11), 2025 Approved Budget: ₦1.49 biliyan
• Information Communication and Technology (jimillar ɓangare, manyan ayyuka, code 11), 2026 Approved Budget: ₦3.70 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 26; Sokoto State FY 2026 Budget, shafi 46
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m38: not found (search, 14.2s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Kasafin jihar bai nuna kuɗin da aka ware kai tsaye ga Ƙaramar Hukumar Wamakko ba. Layukan kasafin jiha na cibiyoyin da ke Wamakko (misali asibiti ko makaranta) kuɗin jiha ne, ba na ƙaramar hukumar ba. Ƙananan hukumomi suna samun kasonsu na doka daga asusun tarayya daban, kuma takardun da nake da su ba su nuna na Wamakko ba.
```

## m39: answered (search, 3.8s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
*Ministry of Environment* (code 053500000000):
• Capital: share of the revised budget spent 48.6% (Kasafi's calculation)
• Total: share of the revised budget spent 47.0% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18, 28
```
