# Open-question run: mid_tier.json

39 questions: answered 23, partial 13, not found 3 | wrong 2 of 11 checked (m10, m37) | median 13.9s

```
plan          n=39 median   3.7s    27% of all time
line_search   n=31 median   1.2s     7% of all time
read          n=31 median   7.2s    46% of all time
read1         n=31 median   6.1s    40% of all time
read2         n=31 median   3.5s    22% of all time
reread        n= 7 median   7.6s    10% of all time
page_search   n=32 median   0.9s     6% of all time
compose       n=32 median   6.1s    36% of all time
answer        n=37 median   7.3s    56% of all time
row readings: 72 model calls for 31 questions (2 = no retry)
```

## m01: answered (lines:sum, 19.8s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
_Ban ga wani bayani ba, don haka na yi amfani da kasafin 2026 da aka amince._

I, akwai kudaden tallafin karatu a kasafin 2026 na daliban jihar Sokoto. An ware ₦1.50 biliyan ga FOREIGN SCHOLARSHIP SCHEME da ₦1.60 biliyan ga Domestic Scholarship. Jimillarsu ₦3.10 biliyan (lissafin Kasafi), dukkansu kudaden da aka ware ne.

• FOREIGN SCHOLARSHIP SCHEME (code 22021020), 2026 Approved Budget: ₦1.50 biliyan
• Domestic Scholarship (code 22021025), 2026 Approved Budget: ₦1.60 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m02: partial (lines:compare, 16.5s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
For rehabilitation/repairs of public schools by SUBEB, ₦205.00 million was allocated in the 2025 revised budget and ₦205.00 million was allocated in the 2026 approved budget, so 0.0% (Kasafi's calculation). No separate SUBEB line for classroom construction is shown.

• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million
• Not found: SUBEB classroom construction allocation

📄 *Sources:* Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: answered (lines:list, 17.1s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
The 2026 approved budget provides ₦1.16 billion for the Female Education Board, including ₦45.00 million for Girls secondary schools. For feeding it provides ₦2.03 billion under the School feeding programme, including ₦2.00 billion as MEAL SUBSIDY TO GOVERNMENT SCHOOLS. For retention it provides ₦11.26 billion under Increase in access, retention, and completion rate at all levels. The Girls Education Project monitoring line is shown with 0.00 for 2026. All figures are approved allocations, not spending.

• Female Education Board (one agency or unit, all spending (total), code 051705700100), 2026 Approved Budget: ₦1.16 billion
• Girls secondary schools (Female Education Board) – purchase of industrial equipment, 2026 Approved Budget: ₦45.00 million
• Girls Education Project (11) with State to State (Ministry for Basic Education), 2026 Approved Budget: 0.00
• School feeding (programme inside a sector, all spending (total), code 050203), 2026 Approved Budget: ₦2.03 billion
• MEAL SUBSIDY TO GOVERNMENT SCHOOLS (code 22050102), 2026 Approved Budget: ₦2.00 billion
• … +1

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 40, 41, 65, 67, 149
_Reply *show working* to see the rows and arithmetic._
```

## m04: answered (lines:share, 25.5s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
The health sector is allocated ₦120.13 billion in the 2026 approved budget, out of Total Expenditure of ₦758.70 billion. 15.8% of the 2026 approved budget's Total Expenditure goes to health (Kasafi's calculation). Both figures are budgeted allocations, not actual spending. This can be compared with the Abuja Declaration benchmark.

• HEALTH (all spending (total), code 707), 2026 Approved Budget: ₦120.13 billion ↑
• Total Expenditure, 2026 Approved Budget: ₦758.70 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1, 32
_Reply *show working* to see the rows and arithmetic._
```

## m05: answered (category, 5.3s)

**Q:** Nawa aka ware wa sayen magunguna da kayan aiki na asibitoci a karkashin Ma'aikatar Lafiya a kasafin 2026?

```
_Ban ga wani bayani ba, don haka na yi amfani da kasafin 2026 da aka amince._

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

## m06: partial (lines:sum, 13.5s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
The 2026 Approved Budget provides counterpart funding for primary healthcare of ₦70.00 million for Basic Health Care Provision Fund (BHCPF) and ₦100.00 million for PHC-MOU activities (support for routine immunization/primary healthcare). Together this is ₦170.00 million (Kasafi's calculation) allocated for these primary healthcare counterpart funds.

• Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health), 2026 Approved Budget: ₦70.00 million
• Provision of support for PHC-MOU activities (Primary Health Care Development Agency), 2026 Approved Budget: ₦100.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 67, 70
_Reply *show working* to see the rows and arithmetic._
```

## m07: partial (lines:list, 28.5s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
No separate line for maternal and child healthcare centers in rural LGAs is shown by Q2 2026, so only the broader Ministry of Health total can be reported. The Ministry of Health had a 2026 Original Budget of ₦124.41 billion allocated. It had spent ₦12.36 billion year-to-date by Q2 2026.

• Ministry of Health (ministry total including its agencies, all spending (total), code 052100000000) [Total Expenditure by Administrative Classification], 2026 Original Budget: ₦124.41 billion
• Ministry of Health (ministry total including its agencies, all spending (total), code 052100000000) [Total Expenditure by Administrative Classification], 2026 Performance Year to Date (Q1-Q2): ₦12.36 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Not found: maternal and child healthcare centers across rural local government areas

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
_Reply *show working* to see the rows and arithmetic._
```

## m08: answered (category, 5.7s)

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

## m09: partial (lines:list, 16.3s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
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

## m10: partial WRONG: none of [['25,000,000,000.00']] (lines:list, 17.2s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
_Ban ga wata shekara daban ba, don haka na yi amfani da kasafin 2026._

Ee, akwai kudaden da aka ware a kasafin 2026. Gyaran madatsar ƙasa a Rafin Duma na ₦54.56 miliyan. Samar da rijiyoyin burtsatse mai amfani da hasken rana na ₦2.20 biliyan da ayyukan rijiyoyi da bututun ruwa a fadin Jihar na ₦226.01 miliyan. Gyaran tankunan ruwa a cikin Sokoto Metropolis na ₦35.00 miliyan. Dukkan su kudaden 2026 Approved Budget ne da aka ware, ba kudin da aka kashe ba.

• Rehabilitation and expansion of earth dams at Rafin Duma (Ministry of Water Resources), 2026 Approved Budget: ₦54.56 miliyan
• through Construction Solar powered boreholes (Department for Rural Water), 2026 Approved Budget: ₦2.20 biliyan
• boreholes, distribution pipes network across the State (Ministry of Water Resources), 2026 Approved Budget: ₦226.01 miliyan
• Rehabilitation of Overhead Tanks within Sokoto Metropolis (Water Board), 2026 Approved Budget: ₦35.00 miliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): Renovation of Boreholes across 40 wards in the State (Department for Special Projects) (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 58, 59
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 11.9s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
The total 2026 approved allocation for the two livestock programmes is ₦13.30 billion (Kasafi's calculation). This is ₦12.93 billion for Animal health and livestock diseases management and ₦368.05 million for Livestock feeds development, which covers grazing reserves. All figures are approved allocations, not actual spending.

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Livestock feeds development (programme inside a sector, all spending (total), code 010206), 2026 Approved Budget: ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40
_Reply *show working* to see the rows and arithmetic._
```

## m12: answered (analysis:mda_profile, 3.8s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
In 2026, Ministry of Works (code 023400000000) and its agencies is allocated ₦59.17 billion: ₦698.42 million for salaries, ₦337.90 million for running costs and ₦58.13 billion for capital projects. In 2025 it was allocated ₦29.22 billion (final budget) and spent ₦12.61 billion over the year (43.2%). By the end of June 2026 it had spent ₦9.63 billion (16.6% of its budget). It has 44 capital projects; the largest are below.

Largest:
• Construction of Rural Roads through Rural access and mobility projects (RAMP), State Wide: ₦7.90 billion
• REHABILATATION AND ASPHALTING OVERLAY OF ILLELA -GADA ROAD, State Wide: ₦5.00 billion
• CONSTRUCTION OF ROAD MANDERA DARIN GURU JABO (13)km) ROAD, State Wide: ₦4.80 billion
• Construction of Rural Roads under Rural Access and Agricultural Marketing Project/ SEED Fund for RARA and Stat, State Wide: ₦4.71 billion
• CONSTRUCTION OF AND ASPHALT OVERLAY.OF KAJIJI TO ZAMFARA STATE BOADER (25.650km) ROAD, State Wide: ₦4.50 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 20, 23, 26, 56, 57; Budget Implementation Report Q4 2025, p. 17; Budget Implementation Report Q2 2026, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m13: not found (search, 11.3s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m14: answered (lines:sum, 13.6s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
An ware ₦6.38 biliyan (lissafin Kasafi) don gina sabbin gidajen ma’aikata da gidaje masu araha a kasafin 2026 da aka amince. Wannan adadin da aka ware ne, ba kuɗin da aka kashe ba. Ya haɗa da ₦4.00 biliyan na rukunin gidaje 500, da ₦2.00 biliyan na rukunin gidaje 500, da ₦382.98 miliyan na kammala gidan ma’aikata.

• Construction of 500 Housing units at Gidan Salanke (Min of Lands and Housing), 2026 Approved Budget: ₦4.00 biliyan
• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan
• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: answered (category, 6.3s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
A kasafin 2026 da aka amince, a duk jihar: PURCHASE OF BUSES (23010108) ₦5.45 biliyan. Zuwa ƙarshen Yuni 2026, an kashe ₦481.04 miliyan daga ciki a duk jihar (8.8%, Budget Implementation Report Q2 2026).

Mafi girma:
• Ministry of Transport: ₦3.90 biliyan
• Ministry of Health: ₦615.00 miliyan
• Pilgrims Welfare Agency: ₦575.00 miliyan
• Sokoto State House of Assembly: ₦300.00 miliyan
• Orthopedic Hospital Wamakko: ₦60.00 miliyan

✓ Layukan hukumomi sun yi daidai da jimillar jihar da aka buga.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29, 86, 93, 126, 162; Budget Implementation Report Q2 2026, shafi 32
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m16: answered (search, 10.1s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
The State Government projected ₦47.44 billion as 2025 original IGR budget, later revised to ₦47.94 billion final budget. Actual IGR collections for full-year Q1–Q4 2025 were ₦20.58 billion, which was 42.9% of the final budget. The 2026 IGR target is set at ₦74.52 billion.

• 2025 original budget (allocated): ₦47.44 billion
• 2025 final budget (allocated): ₦47.94 billion
• 2025 actual collections (Q1–Q4 2025 only) (42.9% of the final budget): ₦20.58 billion
• 2026 approved budget target (allocated): ₦74.52 billion

📄 *Sources:* Budget Implementation Report Q4 2025, p. 9; Sokoto State FY 2026 Budget, p. 1, 11
```

## m17: answered (lines:ratio, 17.2s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
Capital Expenditure allocated in the 2026 approved budget is ₦553.34 billion. Recurrent Expenditure allocated is ₦205.36 billion. The exact ratio of Capital to Recurrent is 2.69 : 1 (Kasafi's calculation).

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (lines:list, 10.3s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
• DOMESTIC PRINCIPAl (code 220604), 2026 Approved Budget: ₦10.03 billion
• DOMESTIC INTEREST / DISCOUNT (code 220602), 2026 Approved Budget: ₦6.00 billion
• FOREIGN PRINCIPAL (code 220603), 2026 Approved Budget: ₦2.42 billion
• FOREIGN INTEREST / DISCOUNT (code 220601), 2026 Approved Budget: ₦1.31 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29
_Reply *show working* to see the rows and arithmetic._
```

## m19: answered (lines:compare, 21.7s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
_Assumption: used approved budgets for 2025 and 2026._

The Office of the Executive Governor's overhead allocation was ₦4.20 billion in the 2025 approved budget versus ₦3.71 billion in the 2026 approved budget. Both figures are allocated (budgeted) overhead and running costs.

• Government House (one agency or unit, overhead (running costs), code 011100100100), 2025 Approved Budget: ₦4.20 billion
• Government House (one agency or unit, overhead (running costs), code 011100100100), 2026 Approved Budget: ₦3.71 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 14; Sokoto State FY 2026 Budget, p. 21
_Reply *show working* to see the rows and arithmetic._
```

## m20: answered (search, 15.6s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa ƙarshen zangon farko (Q1) na 2026, an kashe 3.0% na kasafin manyan ayyuka na daukacin jihar. Wannan 3.0% shi ne yadda ake aiki zuwa yau a Q1 (Q1 2026 kawai).

• 2026 kasafin da aka amince (manyan ayyuka): ₦553.34 biliyan
• Q1 2026 da aka kashe (manyan ayyuka, Q1 2026 kawai) (3.0% na kasafin da aka amince): ₦16.82 biliyan

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 5, 27
```

## m21: answered (query_budget:rank, 11.9s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
Ten MDAs are tied for the lowest capital absorption rate at 0.0% in Q1–Q2 2026 (Kasafi's calculation). They are the Fiscal Responsibility Commission, Ministry for Skills Acquisition and Entrepreneurship Development, Ministry of Commerce and Industry, Ministry of Culture & Tourism, Ministry of Justice, Ministry of Solid Minerals and Natural Resources, Ministry for Local Government and Chieftancy, Ministry for Special Duties, Sokoto State House of Assembly and Sokoto State Independent Electoral Commission.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 26, 27, 28
_Reply *show working* to see the rows and arithmetic._
```

## m22: answered (search, 3.8s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
*Ministry of Health* (code 052100000000):
• Total: spent so far (Q1–Q2) ₦12.36 billion; share of the revised budget spent 10.6% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## m23: answered (lines:compare, 12.5s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
Budgeted personnel expenditure for 2026 was ₦70.57 billion (allocated). Actual payroll outturn through the first half (Q1-Q2) was ₦37.30 billion (spent). The variance is -₦33.28 billion (Kasafi's calculation), which is 52.8% spent (Kasafi's calculation).

• PERSONNEL COST (code 21) [Total Expenditure by Economic Classification], 2026 Original Budget: ₦70.57 billion
• PERSONNEL COST (code 21) [Total Expenditure by Economic Classification], 2026 Performance Year to Date (Q1-Q2): ₦37.30 billion

📄 *Sources:* Budget Implementation Report Q2 2026, p. 30
_Reply *show working* to see the rows and arithmetic._
```

## m24: partial (lines:list, 16.4s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Ba a ware horar da matasa sana'o'i da tallafin kudi daban a cikin kasafin 2026 ba. Abin da aka buga kawai shi ne jimillar Ma'aikatar Matasa da Wasanni ta ₦17.06 biliyan a matsayin kasafin da aka amince. An kashe ₦1.11 biliyan har zuwa kwata na biyu a matsayin abin da aka kashe.

• Ministry of Youth and Sports Development (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 051300000000), 2026 Original Budget: ₦17.06 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): Ministry of Youth and Sports Development (2026 Performance Year to Date (Q1-Q2))

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 17
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m25: partial (lines:list, 17.8s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
The 2026 approved budget includes ₦1.99 billion allocated to Disability and Survival Support and ₦50.00 million allocated to Therapeutic Appliances and Equipment. These are budgeted allocations, not spending. No dedicated line for special schools is shown in the provided lines.

• Disability and Survival Support (objective inside a sector, all spending (total), code 2306), 2026 Approved Budget: ₦1.99 billion
• THERAPEUTIC APPLIANCES AND EQUIPTMENT (code 70713), 2026 Approved Budget: ₦50.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): DISABILITY (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 42, 188
_Reply *show working* to see the rows and arithmetic._
```

## m26: partial (lines:list, 13.9s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
• Ministry for Women Affairs (ministry total including its agencies, all spending (total), code 051400000000) [Total Expenditure by Administrative Classification], 2025 Revised Budget: ₦6.43 billion
• Ministry for Women Affairs (ministry total including its agencies, all spending (total), code 051400000000) [Total Expenditure by Administrative Classification], 2026 Approved Budget: ₦7.24 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Possibly relevant too, not counted (I wasn't sure on a second reading): tabs for Youth and Women Empowerment (POVERTY REDUCTION PROGRAMME) (2025 Revised Budget); tabs for Youth and Women Empowerment (POVERTY REDUCTION PROGRAMME) (2026 Approved Budget); Ministry for Women Affairs (2025 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18
_Reply *show working* to see the rows and arithmetic._
```

## m27: partial (lines:list, 15.3s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
Kasafin 2026 bai ware layi na daban ga kananan hukumomin kan iyaka ba. Abin da aka buga shi ne jimillar sassa masu kula da aikin: ₦44.37 biliyan aka ware wa bangaren Albarkatun Ruwa da Raya Karkara da ₦6.10 biliyan aka ware wa bangaren Rage Talauci a matsayin kasafin da aka amince (allocated), ba kudin da aka kashe ba.

• Water Resources and Rural Development (jimillar ɓangare, duk kashe kuɗi (jimilla), code 10), 2026 Approved Budget: ₦44.37 biliyan
• Poverty Alleviation (jimillar ɓangare, duk kashe kuɗi (jimilla), code 03), 2026 Approved Budget: ₦6.10 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 40, 41
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m28: partial (search, 11.4s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
The 2026 approved personnel total is ₦70.57 billion. The evidence does not state whether this includes full implementation of the national minimum wage across all MDAs.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19
```

## m29: answered (lines:list, 13.4s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
Gwamnati ta ware ₦9.12 biliyan a kasafin 2025 da aka amince da shi don biyan gratuity. Ta ware ₦5.00 biliyan a kasafin 2026 da aka amince da shi don biyan gratuity. Dukkan kudaden da aka ware ne a kasafin kudi, ba abin da aka kashe ba.

• GRATUITY (manyan ayyuka, code 21030101), 2025 Approved Budget: ₦9.12 biliyan
• GRATUITY (manyan ayyuka, code 21030101), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 27
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 8.3s)

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

## m31: partial (search, 14.9s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
The excerpts do not show a separate 2026 approved line named Sokoto State Community Guard Corps and internal security logistics support. The Department for Security Matters has 2026 approved capital of ₦8.30 billion, which is allocated (budgeted), not spent.

• 2026 approved budget (capital) Department for Security Matters: ₦8.30 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 25, 28
```

## m32: answered (lines:list, 12.6s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
The 2026 approved capital allocation for renovation of 25 Upper and lower Sharia Courts is ₦102.06 million. For the State Judiciary, which administers justice, the 2026 approved allocations are ₦1.60 billion for personnel, ₦3.18 billion for overhead, and ₦3.39 billion for capital. All figures are budgeted allocations, not spending.

• Renovation of 25No Upper and lower Sharia Courts (Shari’a Court of Appeal), 2026 Approved Budget: ₦102.06 million
• State Judiciary (ministry total including its agencies, personnel (salaries), code 031800000000) [Personnel Expenditure by Administrative Classification], 2026 Approved Budget: ₦1.60 billion
• State Judiciary (ministry total including its agencies, overhead (running costs), code 031800000000) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2026 Approved Budget: ₦3.18 billion
• State Judiciary (ministry total including its agencies, capital, code 031800000000) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦3.39 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26, 63
_Reply *show working* to see the rows and arithmetic._
```

## m33: partial (lines:sum, 20.6s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
The approved allocation for Security Vote (including operations) is ₦5.50 billion in 2025 and ₦8.21 billion in 2026. Together they total ₦13.71 billion (Kasafi's calculation). No separate line for contingency funds is shown, so only security votes could be added.

• SECURITY VOTE (INCLUDING OPERATIONS) (capital, code 22020604), 2025 Approved Budget: ₦5.50 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion
• Not found: contingency funds

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 17; Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m34: not found (search, 16.2s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Ban sami amsar wannan tambayar a cikin takardun da nake da su ba.
```

## m35: answered (lines:list, 19.7s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
The Sokoto State Independent Electoral Commission (SIEC) as one agency or unit has administrative code 014800100100. Its 2026 Approved Budget allocation is ₦460.48 million. The page number is that of the selected line shown below.

• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: partial (search, 27.2s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
The budget does not show the asked airport project separately. The Airways sector total in the 2026 approved budget is ₦36.00 billion.

• 2026 approved budget (capital): ₦553.34 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 25, 47, 55, 58
```

## m37: answered WRONG: none of [['3,301,437,040.18']] (lines:compare, 17.0s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
Jimillar kudin da aka ware wa shirin ICT equipment, software and expertise a 2025 shi ne ₦3.56 biliyan, kuma a 2026 shi ne ₦7.45 biliyan. Dukkanin lambobin kasafin kudi ne da aka ware, ba kudin da aka kashe ba. Bambancin shi ne ₦3.89 biliyan (lissafin Kasafi), wanda yake 109.4% (lissafin Kasafi) daga 2025 zuwa 2026.

• ICT equipment, software and expertise (shiri cikin ɓangare, duk kashe kuɗi (jimilla), code 050601) [Total Expenditure by Programme (Sector, Objective and Programme)], 2025 Revised Budget: ₦3.56 biliyan
• ICT equipment, software and expertise (shiri cikin ɓangare, duk kashe kuɗi (jimilla), code 050601) [Total Expenditure by Programme (Sector, Objective and Programme)], 2026 Approved Budget: ₦7.45 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 41
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m38: not found (search, 12.9s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Kasafin jihar bai nuna kuɗin da aka ware kai tsaye ga Ƙaramar Hukumar Wamakko ba. Layukan kasafin jiha na cibiyoyin da ke Wamakko (misali asibiti ko makaranta) kuɗin jiha ne, ba na ƙaramar hukumar ba. Ƙananan hukumomi suna samun kasonsu na doka daga asusun tarayya daban, kuma takardun da nake da su ba su nuna na Wamakko ba.
```

## m39: answered (search, 4.1s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
*Ministry of Environment* (code 053500000000):
• Capital: share of the revised budget spent 48.6% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 28
```
