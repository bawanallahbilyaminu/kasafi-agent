# Open-question run: mid_tier.json

39 questions: answered 17, partial 17, not found 5 | wrong 1 of 11 checked (m19) | median 10.8s

```
plan          n=39 median   2.9s    24% of all time
line_search   n=27 median   1.1s     7% of all time
read          n=27 median   5.9s    36% of all time
read1         n=27 median   5.6s    35% of all time
read2         n=27 median   4.8s    27% of all time
reread        n= 8 median   6.8s    12% of all time
page_search   n=12 median   1.0s     2% of all time
compose       n=12 median   4.3s    12% of all time
answer        n=39 median   5.9s    59% of all time
row readings: 64 model calls for 27 questions (2 = no retry)
```

## m01: answered (lines:list, 10.8s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
Eh, akwai tanadi a kasafin 2026. An ware ₦1.60 biliyan don Domestic Scholarship, da kuma ₦1.50 biliyan don FOREIGN SCHOLARSHIP SCHEME. Dukkan adadin kuɗaɗen da aka ware ne (approved budget), ba kuɗaɗen da aka kashe ba.

• Domestic Scholarship (code 22021025), 2026 Approved Budget: ₦1.60 biliyan
• FOREIGN SCHOLARSHIP SCHEME (code 22021020), 2026 Approved Budget: ₦1.50 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m02: partial (lines:list, 23.9s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
For classroom construction (CONSTRUCTION / PROVISION OF PUBLIC SCHOOLS), the 2025 approved allocations shown for SUBEB are ₦4.55 billion and ₦500.00 million. For renovation (REHABILITATION / REPAIRS - PUBLIC SCHOOLS), the lines show ₦205.00 million revised in 2025 and ₦205.00 million approved in 2026. No 2026 approved construction line for SUBEB is shown.

• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦4.55 billion
• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦500.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million
• Not found: 2026 approved allocation for SUBEB classroom construction, and 2025 approved allocation for SUBEB school rehabilitation, are not shown in the lines provided.

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 29; Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: answered (lines:list, 11.1s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
The 2026 approved budget includes ₦1.16 billion for the Female Education Board for girl-child education, ₦2.03 billion for the School feeding programme and ₦2.00 billion for Meal Subsidy to Government Schools for boarding school feeding, and ₦11.26 billion for the Increase in access, retention, and completion rate objective. All figures are allocated (budgeted) amounts, not spent amounts.

• Female Education Board (one agency or unit, all spending (total), code 051705700100), 2026 Approved Budget: ₦1.16 billion
• School feeding (programme inside a sector, all spending (total), code 050203), 2026 Approved Budget: ₦2.03 billion
• MEAL SUBSIDY TO GOVERNMENT SCHOOLS (code 22050102), 2026 Approved Budget: ₦2.00 billion
• Increase in access, retention, and completion rate at all levels (objective inside a sector, all spending (total), code 0502), 2026 Approved Budget: ₦11.26 billion
• Girls Education Project (11) with State to State (Ministry for Basic Education), 2026 Approved Budget: 0.00

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 40, 41, 65, 149
_Reply *show working* to see the rows and arithmetic._
```

## m04: answered (lines:share, 23.2s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
The 2026 approved budget allocates ₦120.13 billion to the health sector, out of Total approved expenditure of ₦758.70 billion. 15.8% of the 2026 approved budget's Total Expenditure goes to health (Kasafi's calculation).

• HEALTH (all spending (total), code 707), 2026 Approved Budget: ₦120.13 billion ↑
• Total Expenditure, 2026 Approved Budget: ₦758.70 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1, 32
_Reply *show working* to see the rows and arithmetic._
```

## m05: answered (category, 4.8s)

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

## m06: partial (lines:list, 15.2s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
• 04050126007201 - Functional health facilities Basic Health Care Provision Funds (BHCF) 25% Counterpart, 2026 Approved Budget: ₦109.00 million
• Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health), 2026 Approved Budget: ₦70.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): 04050124000403 - Functional health facilities BHCF Counterpart Funds for SOCHEMA (2026 Approved Budget); Provision of support for PHC-MOU activities (Primary Health Care Development Agency) (2026 Approved Budget); BHCF Counterpart Funds for SOCHEMA (Sokoto State contributory health care mgt agency) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 67, 229
_Reply *show working* to see the rows and arithmetic._
```

## m07: partial (search, 27.2s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
The papers do not show maternal and child healthcare centers across rural LGAs as a separate line. The Ministry of Health's Q1–Q2 2026 capital spent (total) was ₦3.75 billion (3.9% of the revised budget). The Primary Health Care Development Agency's Q1–Q2 2026 capital spent was ₦729.23 million (12.6% of the revised budget).

📄 *Sources:* Budget Implementation Report Q2 2026, p. 28
```

## m08: answered (category, 6.9s)

**Q:** Nawa gwamnatin jihar Sokoto ta ware don sayen takin zamani da tallafin kayan noma a shekarar 2026, kuma nawa aka riga aka kashe?

```
_Na dauka kashe kudaden da aka riga aka kashe su ne har zuwa rahoton Q2 2026 mafi sabo._

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

## m09: partial (lines:list, 11.4s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
The budget lists two specific irrigation-scheme capital line items: Irrigation Scheme Youth empowerment (NEMI NA KANKA) with ₦200.00 million for 2025 and ₦200.00 million for 2026, and Kware irrigation scheme (SPIN Project) with ₦200.00 million for 2025 and ₦800.00 million for 2026. For tube wells, Construction of Tube Wells across the State (Nigeria CARES-Fadama Programme) shows ₦531.96 million for 2025 and 0.00 for 2026, all allocated (budgeted) amounts. No line item explicitly labelled solar-powered tube wells is shown.

• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦800.00 million
• Construction of Tube Wells across the State (Nigeria CARES- Fadama Programme) [Capital Expenditure by Project], 2025 Revised Budget: ₦531.96 million
• … +1
• Possibly relevant too, not counted (I wasn't sure on a second reading): Intensive crop and vegetable production (irrigation, crop diversification etc.) (2025 Revised Budget); Intensive crop and vegetable production (irrigation, crop diversification etc.) (2026 Approved Budget); through Construction Solar powered boreholes (Department for Rural Water) (2025 Revised Budget); through Construction Solar powered boreholes (Department for Rural Water) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 53
_Reply *show working* to see the rows and arithmetic._
```

## m10: partial (lines:list, 11.3s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
I, an ware kudade a kasafin 2026. Aikin gyaran ruwan birnin Sokoto ya samu ₦25.00 biliyan da aka ware. Gyaran manyan tankunan ruwa a cikin birnin ya samu ₦35.00 miliyan da aka ware. Gyara da fadaɗa madatsun ƙasa a Rafin Duma ya samu ₦54.56 miliyan da aka ware. Dukkan su kudaden da aka ware ne na 2026, ba kudaden da aka kashe ba.

• Rehabilitation and expansion of earth dams at Rafin Duma (Ministry of Water Resources), 2026 Approved Budget: ₦54.56 miliyan
• Rehabilitation of Sokoto Township Water Works (Water Board), 2026 Approved Budget: ₦25.00 biliyan
• Rehabilitation of Overhead Tanks within Sokoto Metropolis (Water Board), 2026 Approved Budget: ₦35.00 miliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): boreholes, distribution pipes network across the State (Ministry of Water Resources) (2026 Approved Budget); through Construction Solar powered boreholes (Department for Rural Water) (2026 Approved Budget); Board for water pumping Stations. (Ministry of Water Resources) (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 58
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 6.7s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
The total budgeted for animal health and livestock diseases management plus livestock feeds development, which covers grazing reserves, is ₦13.30 billion (Kasafi's calculation) in the 2026 approved budget. These are allocated amounts, not spent amounts.

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Livestock feeds development (programme inside a sector, all spending (total), code 010206), 2026 Approved Budget: ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40
_Reply *show working* to see the rows and arithmetic._
```

## m12: partial (lines:list, 13.4s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
The 2026 approved budget shows specific capital allocations for rural feeder roads under the Department for Rural Roads but no separate lines for flyovers or inner-city dualization under the Ministry of Works were found. Rural roads allocations include ₦7.90 billion for Rural Roads through RAMP, ₦2.25 billion for Construction/Provision of Roads, ₦209.11 million for tarring across the state and ₦200.00 million for rehabilitation of existing rural roads projects, all as allocated (budgeted) amounts.

• 17100125000200 - Road - General Construction of Rural Roads through Rural access and mobility projects (RAMP), 2026 Approved Budget: ₦7.90 billion
• (tarring) across the state (Department for Rural Roads), 2026 Approved Budget: ₦209.11 million
• Department for Rural Roads (code 023405700100) – construction / provision of roads, 2026 Approved Budget: ₦2.25 billion
• Rehabilitation of existing projects under rural roads (Department for Rural Roads), 2026 Approved Budget: ₦200.00 million
• Not found: flyovers and inner-city dualization under Ministry of Works

📄 *Sources:* Sokoto State FY 2026 Budget, p. 56, 217
_Reply *show working* to see the rows and arithmetic._
```

## m13: not found (search, 15.7s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m14: partial (lines:sum, 9.3s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
• Ba a haɗa su ba: a karatu na biyu ban tabbata waɗanne layuka ne ke cikin jimillar ba, don haka jimillar waɗannan kaɗai za ta iya ɓatarwa.

• Construction of 500 Housing units at Gidan Salanke (Min of Lands and Housing), 2026 Approved Budget: ₦4.00 biliyan
• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan
• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): Construction of 6 no Houses for 6 New Hon. Khadis in the State (Shari’a Court of Appeal) (2026 Approved Budget); Arkilla Federal Low cost Housing (Ministry for Basic Education) (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: partial (lines:list, 10.5s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
• INTER AND INTRA STATE TRANSPORTATION (SSTA) (Ministry of Transport), 2026 Approved Budget: ₦1.50 biliyan
• PURCHASE OF 20 NO TOYOTA 18-SEATER BUSES for SSTA (Ministry of Transport), 2026 Approved Budget: ₦2.40 biliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): Purchase of 300 Trycle bicycle for disable for ease transportation (Agency for Persons Living With Disabilities) (2026 Approved Budget); PURCHASE OF BUSES (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 55
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m16: partial (lines:list, 9.0s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
• INDEPENDENT REVENUE (code 12), 2025 Original Budget: ₦47.44 billion
• INDEPENDENT REVENUE (code 12), 2025 Performance Year to Date (Q1-Q4): ₦20.58 billion
• INDEPENDENT REVENUE (code 12), 2026 Approved Budget: ₦74.52 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): INDEPENDENT REVENUE (2025 Final Budget)

📄 *Sources:* Budget Implementation Report Q4 2025, p. 9; Sokoto State FY 2026 Budget, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## m17: answered (lines:ratio, 6.5s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
Sokoto State's approved 2026 budget allocates ₦553.34 billion to Capital Expenditure and ₦205.36 billion to Recurrent Expenditure. The exact ratio of Capital to Recurrent Expenditure is 2.69 : 1 (Kasafi's calculation). Both figures are approved allocations, not actual spending.

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (lines:list, 7.6s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
• DOMESTIC PRINCIPAl (code 220604), 2026 Approved Budget: ₦10.03 billion
• DOMESTIC INTEREST / DISCOUNT (code 220602), 2026 Approved Budget: ₦6.00 billion
• FOREIGN PRINCIPAL (code 220603), 2026 Approved Budget: ₦2.42 billion
• FOREIGN INTEREST / DISCOUNT (code 220601), 2026 Approved Budget: ₦1.31 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29
_Reply *show working* to see the rows and arithmetic._
```

## m19: not found WRONG: none of [['4,201,809,645.00', '3,712,790,422.00'], ['9,681,659,645.00', '11,441,290,422.00']] (search, 9.7s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m20: answered (search, 9.9s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa ƙarshen Q1 na 2026, an kashe 3.0% na kasafin manyan ayyuka a ɗaukacin jihar. Kasafin da aka amince da shi (manyan ayyuka) shi ne ₦553.34 biliyan, kuma kuɗin da aka kashe a Q1 kaɗai (Janairu–Maris 2026) shi ne ₦16.82 biliyan.

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 9, 27
```

## m21: answered (query_budget:rank, 16.6s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
There is no distinct bottom three because the lowest capital performance in Q1-Q2 2026 is 0.0% shared by Ministry for Skills Acquisition and Entrepreneurship Development, Ministry of Commerce and Industry, Ministry of Culture & Tourism, Ministry of Justice, Ministry of Solid Minerals and Natural Resources, Fiscal Responsibility Commission, Ministry for Local Government and Chieftancy, Ministry for Special Duties, Sokoto State House of Assembly and Sokoto State Independent Electoral Commission.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 26, 27, 28
_Reply *show working* to see the rows and arithmetic._
```

## m22: answered (search, 8.1s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
The Ministry of Health spent ₦12.36 billion out of its 2026 revised budget by end of Q2 2026 (Q1–Q2 only), a release rate of 10.6% of the revised budget. This is confirmed in the Budget Implementation Report Q2 2026 on page 18 in the Total Expenditure by Administrative Classification table.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## m23: answered (search, 9.0s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
Budgeted personnel for 2026 was ₦70.57 billion. Actual payroll through the first half (Q1–Q2 2026 only) was ₦37.30 billion (52.8% of the revised budget). The variance left as balance was ₦33.28 billion.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19
```

## m24: partial (lines:list, 20.3s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Babu layin horar da matasa sana'o'i da tallafin kudi daban a cikin Ma'aikatar Matasa da Wasanni da aka nuna. Abin da aka nuna shi ne jimillar Ma'aikatar Matasa da Wasanni baki daya, wato ₦17.06 biliyan a matsayin kasafin 2026 da aka amince da shi. Wannan jimilla ce ta ma'aikatar, ba kudin horarwa da tallafi kadai ba.

• Ministry of Youth and Sports Development (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 051300000000), 2026 Original Budget: ₦17.06 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.
• Ba a samu ba: layin horar da matasa sana'o'i da tallafin kudi daban a Ma'aikatar Matasa da Wasanni

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 17
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m25: partial (lines:list, 10.8s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
Yes, the 2026 approved budget has dedicated lines for all three. Special schools are provided for through Raji Special School rehabilitation of ₦500.00 million and Inclusive Education of ₦102.00 million. Assistive devices are provided for as Therapeutic Appliances and Equipment of ₦50.00 million, and welfare support for persons with disabilities is provided for under the Disability function of ₦3.07 billion. All figures are approved allocations, not spending.

• Raji Special School (Ministry for Basic Education), 2026 Approved Budget: ₦500.00 million
• Inclusive Education (code 50301), 2026 Approved Budget: ₦102.00 million
• THERAPEUTIC APPLIANCES AND EQUIPTMENT (code 70713), 2026 Approved Budget: ₦50.00 million
• DISABILITY (all spending (total), code 71012), 2026 Approved Budget: ₦3.07 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): DISABILITY (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 33, 65, 77, 188
_Reply *show working* to see the rows and arithmetic._
```

## m26: partial (lines:list, 9.9s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
The Women's Economic Empowerment programme was budgeted at ₦4.94 billion for 2025 (Revised Budget) and ₦3.15 billion for 2026 (Approved Budget). The figures are allocated (budgeted) amounts. No separate lines for orphanages and destitute homes were shown in the lines provided.

• Women's Economic Empowerment (programme inside a sector, all spending (total), code 230301) [Total Expenditure by Programme (Sector, Objective and Programme)], 2025 Revised Budget: ₦4.94 billion
• Women's Economic Empowerment (programme inside a sector, all spending (total), code 230301) [Total Expenditure by Programme (Sector, Objective and Programme)], 2026 Approved Budget: ₦3.15 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): Ministry for Women Affairs (2025 Revised Budget); Ministry for Women Affairs (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 42
_Reply *show working* to see the rows and arithmetic._
```

## m27: partial (lines:list, 10.7s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
Babu layin da ya ware kudi daban don ayyukan raya karkara da rage talauci a kananan hukumomin kan iyaka a kasafin 2026. Mafi kusa shine jimillar sashen Water Resources and Rural Development na ₦44.37 biliyan da aka ware (budgeted), da jimillar sashen Poverty Alleviation na ₦6.10 biliyan da aka ware (budgeted). Wadannan jimillolin sassan gaba daya ne, ba na kan iyaka kadai ba.

• Water Resources and Rural Development (jimillar ɓangare, duk kashe kuɗi (jimilla), code 10), 2026 Approved Budget: ₦44.37 biliyan
• Poverty Alleviation (jimillar ɓangare, duk kashe kuɗi (jimilla), code 03), 2026 Approved Budget: ₦6.10 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): REHABILITATION/REPAIRS OF BOUNDARIES (2026 Approved Budget); CONSTRUCTION OF BOUNDARY PILLARS/ RIGHT OF WAYS (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 40, 41
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m28: not found (search, 7.3s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
I couldn't find the answer to that in the documents I have.
```

## m29: answered (lines:list, 12.3s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
Gwamnati ta ware ₦9.12 biliyan a kasafin 2025 don biyan gratuity, da ₦5.00 biliyan a kasafin 2026 don biyan gratuity. Dukkan kudaden da aka ware ne (budgeted), ba kudin da aka kashe ba.

• GRATUITY (manyan ayyuka, code 21030101), 2025 Approved Budget: ₦9.12 biliyan
• GRATUITY (manyan ayyuka, code 21030101), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 27
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 10.7s)

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

## m31: partial (lines:list, 16.2s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
No line is printed with the exact name 'Sokoto State Community Guard Corps' in the 2026 approved budget. The guard-related agency shown is the Sokoto Marshal Corps with an approved 2026 total of ₦1.22 billion, made up of ₦1.13 billion for overhead and ₦90.00 million for capital (all amounts are approved/allocated, not spent). Internal security logistics support is shown as Guards (Department for Security Matters) – Purchase of Motor Vehicles ₦3.00 billion and Security Vote (Including Operations) ₦8.21 billion.

• Guards (Department for Security Matters) – purchase of motor vehicles, 2026 Approved Budget: ₦3.00 billion
• Sokoto Marshal Corps (one agency or unit, all spending (total), code 012400700100) [Total Expenditure by Administrative Classification], 2026 Approved Budget: ₦1.22 billion
• Sokoto Marshal Corps (one agency or unit, overhead (running costs), code 012400700100) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2026 Approved Budget: ₦1.13 billion
• Sokoto Marshal Corps (one agency or unit, capital, code 012400700100), 2026 Approved Budget: ₦90.00 million
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion
• Not found: Sokoto State Community Guard Corps – no 2026 approved budget line is printed with that exact name; the closest guard agency shown is Sokoto Marshal Corps

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 22, 25, 28, 52
_Reply *show working* to see the rows and arithmetic._
```

## m32: partial (lines:list, 15.1s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
The 2026 approved capital allocation for the Ministry of Justice is ₦3.71 billion. The 2026 approved capital allocation for Renovation of 25No Upper and lower Sharia Courts is ₦102.06 million. No recurrent allocation line for the administration of justice is shown in the lines provided.

• Ministry of Justice (ministry total including its agencies, capital, code 032600000000), 2026 Approved Budget: ₦3.71 billion
• Renovation of 25No Upper and lower Sharia Courts (Shari’a Court of Appeal), 2026 Approved Budget: ₦102.06 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): Ministry of Justice (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 26, 63
_Reply *show working* to see the rows and arithmetic._
```

## m33: partial (lines:sum, 14.7s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
The allocated security vote is ₦5.50 billion for 2025 and ₦8.21 billion for 2026, for a combined total of ₦13.71 billion (Kasafi's calculation). No separate line for contingency funds is shown in the lines provided, so this total covers security votes only.

• SECURITY VOTE (INCLUDING OPERATIONS) (capital, code 22020604), 2025 Approved Budget: ₦5.50 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion
• Not found: contingency funds

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 17; Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m34: not found (search, 7.1s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Ban sami amsar wannan tambayar a cikin takardun da nake da su ba.
```

## m35: answered (lines:list, 11.6s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: not found (search, 13.7s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
I couldn't find the answer to that in the documents I have.
```

## m37: answered (search, 8.9s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
Jimillar da aka ware wa bangaren Information Communication and Technology a 2025 ita ce ₦3.30 biliyan daga kasafin da aka amince (jimilla) a shafi 24, a 2026 kuma ₦7.15 biliyan daga kasafin da aka amince (jimilla) a shafi 41.

• Ma'aikata 2025 (jimilla): ₦1.35 biliyan (shafi 11)
• Ma'aikata 2026 (jimilla): ₦3.59 biliyan (shafi 17)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11, 24; Sokoto State FY 2026 Budget, shafi 17, 41
```

## m38: partial (search, 13.1s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Kasafin jihar bai nuna ware kuɗi kai tsaye ga gwamnatin Ƙaramar Hukumar Wamakko ba a cikin shaidun. Layukan da ke ɗauke da WAMAKKO, kamar Asibitin Ƙashi na Wamakko da aikin asibiti a Kasarawa, ayyukan gwamnatin jiha ne da ake yi a yankin, ba kuɗin ƙaramar hukuma ba, kuma ƙananan hukumomi suna karɓar rabon asusu daban. Abin da aka buga a matsayin wurin WAMAKKO shi ne kashewar jihar a yankin.

• 2026 kasafin da aka amincewa (manyan ayyuka, wurin WAMAKKO): ₦82.18 biliyan
• 2026 kasafin da aka amincewa (albashi, wurin WAMAKKO): ₦1.60 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 18, 27, 38, 39, 67
```

## m39: answered (lines:share, 11.6s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
• Share (↑ ÷ ↓): 48.6% (Kasafi's calculation)

• Ministry of Environment (ministry total including its agencies, capital, code 053500000000) [Capital Expenditure by Administrative Classification], 2026 Performance Year to Date (Q1-Q2): ₦7.86 billion ↑
• Ministry of Environment (ministry total including its agencies, capital, code 053500000000) [Capital Expenditure by Administrative Classification], 2026 Revised Budget: ₦16.17 billion ↓

📄 *Sources:* Budget Implementation Report Q2 2026, p. 28
_Reply *show working* to see the rows and arithmetic._
```
