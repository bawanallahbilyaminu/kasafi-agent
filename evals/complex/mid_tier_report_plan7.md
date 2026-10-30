# Open-question run: mid_tier.json

39 questions: answered 20, partial 17, not found 2 | wrong 2 of 11 checked (m04, m10) | median 13.4s

```
plan          n=39 median   3.7s    28% of all time
line_search   n=32 median   1.6s    11% of all time
read          n=31 median   6.4s    39% of all time
read1         n=31 median   4.0s    27% of all time
read2         n=31 median   3.8s    26% of all time
reread        n= 5 median   4.7s     4% of all time
page_search   n=33 median   1.7s    10% of all time
compose       n=27 median   5.9s    32% of all time
answer        n=37 median   6.3s    46% of all time
row readings: 72 model calls for 31 questions (2 = no retry)
```

## m01: answered (search, 18.5s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
Ee, an ware ₦1.60 biliyan na Domestic Scholarship a kasafin 2026. Wannan kuɗi ne da aka ware (ba kuɗin da aka kashe ba). A Q1–Q2 2026 kaɗai, an kashe ₦494.70 miliyan (30.9% na kasafin da aka sabunta).

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29, 160; Budget Implementation Report Q2 2026, shafi 31
```

## m02: partial (lines:list, 15.9s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
SUBEB's 2025 approved allocation for construction/provision of public schools was ₦4.55 billion plus ₦500.00 million. For rehabilitation/repairs of public schools, the 2025 revised figure was ₦205.00 million and the 2026 approved allocation was ₦205.00 million. No 2026 approved construction line for SUBEB is shown separately.

• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦4.55 billion
• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦500.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools, 2026 Approved Budget: ₦205.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): State Universal Basic Education Board (SUBEB) (2025 Revised Budget)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 29; Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: answered (lines:list, 10.2s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
The 2026 approved budget shows specific lines for all three areas. For girl-child education: Female Education Board and Girls Education Project monitoring. For feeding: Meal Subsidy to Government Schools and the School feeding programme. For retention: the Increase in access, retention, and completion rate objective. All figures are approved allocations for 2026.

• Female Education Board (one agency or unit, all spending (total), code 051705700100), 2026 Approved Budget: ₦1.16 billion
• Girls Education Project (11) with State to State (Ministry for Basic Education), 2026 Approved Budget: 0.00
• MEAL SUBSIDY TO GOVERNMENT SCHOOLS (code 22050102), 2026 Approved Budget: ₦2.00 billion
• School feeding (programme inside a sector, all spending (total), code 050203), 2026 Approved Budget: ₦2.03 billion
• Increase in access, retention, and completion rate at all levels (objective inside a sector, all spending (total), code 0502), 2026 Approved Budget: ₦11.26 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 40, 41, 65, 149
_Reply *show working* to see the rows and arithmetic._
```

## m04: partial WRONG: none of [['15.8']] (lines:list, 23.7s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
The health sector allocation is ₦120.13 billion in 2026 approved (original) budget. The overall 2026 Total Expenditure line needed to calculate the share is not among the lines shown, so the percentage cannot be calculated here.

• HEALTH (all spending (total), code 707), 2026 Original Budget: ₦120.13 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): Total Expenditure (2026 Approved Budget)

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 36
_Reply *show working* to see the rows and arithmetic._
```

## m05: answered (category, 6.6s)

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

## m06: partial (lines:list, 13.0s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
• 04050126007201 - Functional health facilities Basic Health Care Provision Funds (BHCF) 25% Counterpart, 2026 Approved Budget: ₦109.00 million
• Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health), 2026 Approved Budget: ₦70.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): Provision of support for PHC-MOU activities (Primary Health Care Development Agency) (2026 Approved Budget); BHCF Counterpart Funds for SOCHEMA (Sokoto State contributory health care mgt agency) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 67, 229
_Reply *show working* to see the rows and arithmetic._
```

## m07: partial (lines:list, 18.2s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
No line in the documents is exactly that (maternal and child healthcare centers across rural local government areas). The nearest lines they print (related, not the item itself):
• Ministry of Health (ministry total including its agencies, all spending (total), code 052100000000, Total Expenditure by Administrative Classification), 2026 Performance Year to Date (Q1-Q2): ₦12.36 billion [1]
• Ministry of Health (ministry total including its agencies, all spending (total), code 052100000000, Primary Healthcare Expenditure by Administrative Classification), 2026 Performance Year to Date (Q1-Q2): ₦1.22 billion [2]

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18, 52
```

## m08: answered (category, 7.2s)

**Q:** Nawa gwamnatin jihar Sokoto ta ware don sayen takin zamani da tallafin kayan noma a shekarar 2026, kuma nawa aka riga aka kashe?

```
_Ban ga rahoton da aka ce ba, don haka na yi amfani da kasafin 2026 da rahoton aiwatarwa na Q2 2026 mafi sabo._

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

## m09: answered (lines:list, 14.0s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
The budgets show separate capital project lines for irrigation schemes and for tube wells / solar-powered boreholes. For 2026 approved vs 2025 revised in the 2026 budget: Kware irrigation scheme (SPIN) is ₦800.00 million vs ₦200.00 million, Irrigation Scheme Youth empowerment (NEMI NA KANKA) is ₦200.00 million in both years, Construction of Tube Wells (Fadama) is 0.00 in 2026 vs ₦531.96 million in 2025 revised, and Construction Solar powered boreholes is ₦2.20 billion in 2026 vs 0.00 in 2025 revised. All figures are allocated (budgeted), not spent.

• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦800.00 million
• Construction of Tube Wells across the State (Nigeria CARES- Fadama Programme) [Capital Expenditure by Project], 2025 Revised Budget: ₦531.96 million
• … +3

📄 *Sources:* Sokoto State FY 2026 Budget, p. 53, 59
_Reply *show working* to see the rows and arithmetic._
```

## m10: partial WRONG: none of [['25,000,000,000.00']] (lines:list, 17.3s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• boreholes, distribution pipes network across the State (Ministry of Water Resources), 2026 Approved Budget: ₦226.01 miliyan [1]
• Renovation of Boreholes across 40 wards in the State (Department for Special Projects), 2026 Approved Budget: ₦50.00 miliyan [2]
• WATER SUPPLY (all spending (total), code 7063), 2026 Approved Budget: ₦44.09 biliyan [3]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 32, 49, 58
```

## m11: answered (lines:sum, 9.8s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
The combined 2026 approved allocation for animal health and livestock diseases management and livestock feeds development is ₦13.30 billion (Kasafi's calculation). These are programme totals covering all spending, including disease control, veterinary services and grazing reserves.

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Livestock feeds development (programme inside a sector, all spending (total), code 010206), 2026 Approved Budget: ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40
_Reply *show working* to see the rows and arithmetic._
```

## m12: partial (lines:list, 16.6s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
The 2026 approved capital budget shows rural/feeder road items under the Department for Rural Roads, including RAMP, the RARA/State Road Fund item and other road construction items plus rehabilitation. No separate lines for flyovers or inner-city dualization under the Ministry of Works are shown in the lines provided.

• Department for Rural Roads (code 023405700100) – construction / provision of roads, 2026 Approved Budget: ₦2.25 billion
• Rehabilitation of existing projects under rural roads (Department for Rural Roads), 2026 Approved Budget: ₦200.00 million
• (tarring) across the state (Department for Rural Roads), 2026 Approved Budget: ₦209.11 million
• (RAMP) (Department for Rural Roads) – construction / provision of roads, 2026 Approved Budget: ₦7.90 billion
• Marketing Project/ SEED Fund for RARA and State Road Fund (SRS) (Department for Rural Roads), 2026 Approved Budget: ₦4.71 billion
• Not found: flyovers, inner-city dualization

📄 *Sources:* Sokoto State FY 2026 Budget, p. 56, 57
_Reply *show working* to see the rows and arithmetic._
```

## m13: not found (search, 11.6s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m14: answered (lines:sum, 11.8s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
An ware ₦6.38 biliyan (lissafin Kasafi) a kasafin 2026 da aka amince don gina sabbin gidaje, gami da gidajen ma’aikata. Ginin gidaje 500 a Gidan Salanke shi ne mafi girma da ₦4.00 biliyan, sai ginin Housing Estate 500 a Wajekke da ₦2.00 biliyan, da kammala staff quarters 53 a Jami’a da ₦382.98 miliyan. Dukkan adadin da aka ware aka ambata (budgeted), ba kashewa ba.

• Construction of 500 Housing units at Gidan Salanke (Min of Lands and Housing), 2026 Approved Budget: ₦4.00 biliyan
• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan
• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: partial (lines:list, 14.9s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
I, an ware kudi a kasafin 2026 don saukaka sufurin jama'a. Aikin sufuri na tsakanin jiha da cikin jiha (SSTA) na Ma'aikatar Sufuri an ware masa ₦1.50 biliyan, da kuma sayen bas 20 na Toyota 18-seater don SSTA ₦2.40 biliyan. Haka kuma an ware ₦140.00 miliyan don sayen babura masu kafa uku 300 ga nakasassu don saukaka sufuri. Wadannan kudaden da aka ware (budgeted) ne, ba abin da aka kashe ba.

• INTER AND INTRA STATE TRANSPORTATION (SSTA) (Ministry of Transport), 2026 Approved Budget: ₦1.50 biliyan
• PURCHASE OF 20 NO TOYOTA 18-SEATER BUSES for SSTA (Ministry of Transport), 2026 Approved Budget: ₦2.40 biliyan
• Purchase of 300 Trycle bicycle for disable for ease transportation (Agency for Persons Living With Disabilities), 2026 Approved Budget: ₦140.00 miliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): PURCHASE OF BUSES (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 55, 64
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m16: answered (search, 11.5s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
The 2025 approved IGR projection was ₦47.44 billion (revised/final budget ₦47.94 billion). Actual 2025 collection (Q1–Q4 2025) was ₦20.58 billion (42.9% of the final budget). The 2026 IGR target (approved budget) is ₦74.52 billion.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1, 11; Budget Implementation Report Q4 2025, p. 9, 13; Sokoto State Government 2025 Approved Budget, p. 1
```

## m17: answered (lines:ratio, 9.8s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
Capital Expenditure approved for 2026 is ₦553.34 billion and Recurrent Expenditure approved for 2026 is ₦205.36 billion. The exact ratio of Capital to Recurrent is 2.69 : 1 (Kasafi's calculation).

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (category, 8.1s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
Statewide, the 2026 approved budget has FOREIGN INTEREST /DISCOUNT - LONG TERM BORROWINGS (22060102) ₦1.31 billion; FOREIGN PRINCIPAL - LONG TERM BORROWINGS (22060302) ₦2.42 billion; DOMESTIC PRINCIPAL - LONG TERM BORROWINGS (22060402) ₦10.03 billion; DOMESTIC PRINCIPAL - SHORT TERM BORROWINGS (22060401) 0.00, ₦13.76 billion together (Kasafi's calculation).

Largest:
• Fertilizer and Agricultral Supplies Company: ₦13.76 billion

✓ The agencies' rows add up exactly to the printed statewide totals.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29, 112
_Reply *show working* to see the rows and arithmetic._
```

## m19: answered (lines:compare, 16.6s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
• Difference (2026 Approved Budget vs 2025 Approved Budget): -₦489.02 million (-11.6%) (Kasafi's calculation)

• Government House (one agency or unit, overhead (running costs), code 011100100100), 2025 Approved Budget: ₦4.20 billion
• Government House (one agency or unit, overhead (running costs), code 011100100100), 2026 Approved Budget: ₦3.71 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 14; Sokoto State FY 2026 Budget, p. 21
_Reply *show working* to see the rows and arithmetic._
```

## m20: answered (search, 14.1s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa ƙarshen Q1 2026, an kashe 3.0% na kasafin manyan ayyuka na daukacin jihar. Kasafin da aka ware (allocated) shi ne ₦553.34 biliyan, kuma abin da aka kashe (spent) a Q1 2026 kaɗai shi ne ₦16.82 biliyan.

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 27
```

## m21: answered (query_budget:rank, 9.2s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
Ten capital-spending lines are tied at the lowest absorption rate of 0.0% of the 2026 revised budget in Q1–Q2 2026; the seven ministries among them are the Ministry for Local Government and Chieftancy, Ministry for Skills Acquisition and Entrepreneurship Development, Ministry for Special Duties, Ministry of Commerce and Industry, Ministry of Culture & Tourism, Ministry of Justice and Ministry of Solid Minerals and Natural Resources, so there is no distinct bottom three.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 26, 27, 28
_Reply *show working* to see the rows and arithmetic._
```

## m22: answered (search, 4.2s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
*Ministry of Health* (code 052100000000):
• Total: share of the revised budget spent 10.6% (Kasafi's calculation); spent so far (Q1–Q2) ₦12.36 billion

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## m23: answered (search, 11.7s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
2026 budgeted personnel (revised) was ₦70.57 billion. Through Q1–Q2 2026, actual personnel spending was ₦37.30 billion (52.8% of the revised budget). The variance (balance against revised budget) was ₦33.28 billion.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19
```

## m24: partial (lines:list, 16.0s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Babu layin da aka ware daban don horar da matasa sana'o'i da tallafin kudi a Ma'aikatar Matasa da Wasanni a 2026. Abin da takardun suka nuna daban shi ne jimillar Ma'aikatar gaba daya ta ₦17.06 biliyan da aka amince da ita a 2026.

• Ministry of Youth and Sports Development (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 051300000000), 2026 Approved Budget: ₦17.06 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m25: partial (lines:list, 20.6s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
The 2026 approved budget does not show separate, dedicated lines for assistive devices, special schools or welfare support for persons with disabilities. What is shown is the overall DISABILITY function (SICKNESS AND DISABILITY) with a total allocation of ₦3.07 billion - made up of ₦827.90 million for personnel, ₦1.00 billion for overhead and ₦1.24 billion for capital. The only project-level line for disabilities is rehabilitation of centres in Goronyo, Kware and Bodinga for ₦150.00 million.

• DISABILITY (all spending (total), code 71012) [Total Expenditure by Functional Classification], 2026 Approved Budget: ₦3.07 billion
• centres of Goronyo, Kware and Bodinga (Agency for Persons Living With Disabilities), 2026 Approved Budget: ₦150.00 million
• DISABILITY (personnel (salaries), code 71012) [Personnel Expenditure by Functional Classification], 2026 Approved Budget: ₦827.90 million
• DISABILITY (overhead (running costs), code 71012) [Other Non-Debt Recurrent Expenditure by Functional Classification], 2026 Approved Budget: ₦1.00 billion
• DISABILITY (capital, code 71012) [Capital Expenditure by Functional Classification], 2026 Approved Budget: ₦1.24 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Not found: specific dedicated lines for assistive devices, special schools, and itemised welfare support for persons with disabilities

📄 *Sources:* Sokoto State FY 2026 Budget, p. 33, 34, 36, 38, 64
_Reply *show working* to see the rows and arithmetic._
```

## m26: partial (lines:list, 13.8s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
The Women's Economic Empowerment programme is budgeted at ₦4.94 billion for 2025 (revised) and ₦3.15 billion for 2026 (approved). No separate lines for orphanages and destitute homes are shown.

• Women's Economic Empowerment (programme inside a sector, all spending (total), code 230301) [Total Expenditure by Programme (Sector, Objective and Programme)], 2025 Revised Budget: ₦4.94 billion
• Women's Economic Empowerment (programme inside a sector, all spending (total), code 230301) [Total Expenditure by Programme (Sector, Objective and Programme)], 2026 Approved Budget: ₦3.15 billion
• Not found: orphanages, destitute homes

📄 *Sources:* Sokoto State FY 2026 Budget, p. 42
_Reply *show working* to see the rows and arithmetic._
```

## m27: partial (lines:list, 17.4s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• Water Resources and Rural Development (sector total, all spending (total), code 10), 2026 Approved Budget: ₦44.37 biliyan [1]
• Poverty Alleviation (sector total, all spending (total), code 03), 2026 Approved Budget: ₦6.10 biliyan [2]
• Integrated rural development (agricultural land development, farm mechanization, & rural infrastructures (programme inside a sector, all spending (total), code 010701), 2026 Approved Budget: 0.00 [2]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 40, 41
```

## m28: partial (lines:list, 11.6s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• PERSONNEL COST (code 21), 2026 Approved Budget: ₦70.57 billion [1]
• Total Personnel Expenditure (personnel (salaries)), 2026 Original Budget: ₦70.57 billion [2]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1; Budget Implementation Report Q2 2026, p. 19
```

## m29: answered (lines:list, 11.4s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
Gwamnati ta ware ₦9.12 biliyan a kasafin 2025 da aka amince da shi don biyan gratuity, da ₦5.00 biliyan a kasafin 2026 da aka amince da shi don biyan gratuity ga tsofaffin ma’aikata.

• GRATUITY (manyan ayyuka, code 21030101), 2025 Approved Budget: ₦9.12 biliyan
• GRATUITY (manyan ayyuka, code 21030101), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 27
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 10.2s)

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

## m31: partial (lines:list, 13.4s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• SECURITY SERVICES (code 22020601), 2026 Approved Budget: ₦8.62 billion [1]
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion [1]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 28
```

## m32: partial (lines:list, 15.3s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
• Renovation of 25No Upper and lower Sharia Courts (Shari’a Court of Appeal), 2026 Approved Budget: ₦102.06 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): State Judiciary (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 63
_Reply *show working* to see the rows and arithmetic._
```

## m33: partial (lines:sum, 15.8s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
_Assumption: used approved budgets for 2025 and 2026._

The approved allocation for SECURITY VOTE (INCLUDING OPERATIONS) was ₦5.50 billion in 2025 and ₦8.21 billion in 2026, for a combined ₦13.71 billion (Kasafi's calculation). No line for contingency funds is shown, so this covers security votes only.

• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2025 Original Budget: ₦5.50 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion
• Not found: contingency funds

📄 *Sources:* Budget Implementation Report Q4 2025, p. 33; Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m34: not found (search, 12.4s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Ban sami amsar wannan tambayar a cikin takardun da nake da su ba.
```

## m35: answered (lines:list, 12.7s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
The Sokoto State Independent Electoral Commission is shown as one agency with a 2026 Approved Budget of ₦460.48 million.

• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: partial (lines:list, 18.0s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• PURCHASE OF AEROPLANE (code 23010143), 2026 Approved Budget: ₦36.00 billion [1]
• Airways (sector total, capital, code 18), 2026 Approved Budget: ₦36.00 billion [2]
• Airways - General (programme inside a sector, capital, code 181001), 2026 Approved Budget: ₦36.00 billion [2]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 47, 126
```

## m37: answered (lines:compare, 15.0s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
Jimillar kudin da aka ware wa bangaren Information Communication and Technology a 2025 ita ce ₦3.30 biliyan. A 2026 kuma jimillar ta kai ₦7.15 biliyan. Dukkanin kudaden da aka amince da su ne a kasafin kudin, ba kudin da aka kashe ba. 116.5% (lissafin Kasafi).

• Information Communication and Technology (jimillar ɓangare, duk kashe kuɗi (jimilla), code 11), 2025 Approved Budget: ₦3.30 biliyan
• Information Communication and Technology (jimillar ɓangare, duk kashe kuɗi (jimilla), code 11), 2026 Approved Budget: ₦7.15 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 24; Sokoto State FY 2026 Budget, shafi 41
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m38: partial (lines:list, 14.6s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• WAMAKKO (capital, code 33312100, Capital Expenditure by Functional Classification), 2026 Approved Budget: ₦82.18 biliyan [1]
• WAMAKKO (code 33312100, Personnel Expenditure by Location), 2026 Approved Budget: ₦79.98 biliyan [2]
• Kasarawa Wamakko Local Government (Ministry of Health), 2026 Approved Budget: ₦10.00 biliyan [3]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 38, 39, 67
```

## m39: answered (search, 4.1s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
*Ministry of Environment* (code 053500000000):
• Capital: share of the revised budget spent 48.6% (Kasafi's calculation); approved budget ₦18.77 billion; revised budget ₦16.17 billion; spent so far (Q1–Q2) ₦7.86 billion; spent in Q2 ₦7.84 billion
• Total: share of the revised budget spent 47.0% (Kasafi's calculation); approved budget ₦20.77 billion; revised budget ₦18.17 billion; spent so far (Q1–Q2) ₦8.53 billion; spent in Q2 ₦8.21 billion

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18, 28; Sokoto State FY 2026 Budget, p. 18, 27
```
