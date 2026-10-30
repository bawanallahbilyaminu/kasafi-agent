# Open-question run: mid_tier.json

39 questions: answered 21, partial 13, not found 5 | wrong 0 of 11 checked | median 12.8s

```
plan          n=39 median   3.7s    31% of all time
line_search   n=32 median   1.1s     9% of all time
read          n=31 median   5.6s    37% of all time
read1         n=31 median   3.8s    26% of all time
read2         n=31 median   3.7s    26% of all time
reread        n= 5 median   4.6s     4% of all time
page_search   n=33 median   1.1s     7% of all time
compose       n=26 median   5.5s    35% of all time
answer        n=37 median   5.6s    49% of all time
row readings: 68 model calls for 31 questions (2 = no retry)
```

## m01: answered (lines:sum, 10.7s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
I, an ware kudaden tallafin karatu ga dalibai a kasafin 2026. Tallafin cikin gida (Domestic Scholarship) ₦1.60 biliyan ne, tallafin kasashen waje (Foreign Scholarship Scheme) kuma ₦1.50 biliyan ne. Jimillarsu ₦3.10 biliyan (lissafin Kasafi). Dukkaninsu kudaden da aka ware (kasafin kudi) ne.

• Domestic Scholarship (code 22021025), 2026 Approved Budget: ₦1.60 biliyan
• FOREIGN SCHOLARSHIP SCHEME (code 22021020), 2026 Approved Budget: ₦1.50 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m02: partial (lines:list, 15.3s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
• (SUBEB) – construction / provision of public schools, 2025 Approved Budget: ₦4.55 billion
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): (SUBEB) (2025 Approved Budget)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 29; Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: answered (lines:list, 8.9s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
The 2026 approved budget shows specific lines for all three areas. For girl-child education there is the Girls Education Project monitoring line and the Female Education Board total allocation. For school feeding there is the School feeding programme and the Meal Subsidy to Government Schools project. For retention there is the access, retention and completion objective.

• Girls Education Project (11) with State to State (Ministry for Basic Education), 2026 Approved Budget: 0.00
• Female Education Board (one agency or unit, all spending (total), code 051705700100), 2026 Approved Budget: ₦1.16 billion
• MEAL SUBSIDY TO GOVERNMENT SCHOOLS (code 22050102), 2026 Approved Budget: ₦2.00 billion
• School feeding (programme inside a sector, all spending (total), code 050203), 2026 Approved Budget: ₦2.03 billion
• Increase in access, retention, and completion rate at all levels (objective inside a sector, all spending (total), code 0502), 2026 Approved Budget: ₦11.26 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 40, 41, 65, 149
_Reply *show working* to see the rows and arithmetic._
```

## m04: answered (lines:share, 18.0s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
The 2026 approved allocation to the health sector (HEALTH function) is ₦120.13 billion, of the 2026 approved budget's Total Expenditure of ₦758.70 billion. This is 15.8% (Kasafi's calculation) of the overall 2026 approved budget, compared with the Abuja Declaration benchmark.

• HEALTH (all spending (total), code 707), 2026 Approved Budget: ₦120.13 billion ↑
• Total Expenditure (all spending (total)), 2026 Approved Budget: ₦758.70 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 32
_Reply *show working* to see the rows and arithmetic._
```

## m05: answered (category, 6.0s)

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

## m06: partial (lines:list, 10.7s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
The 2026 approved budget provides ₦100.00 million as counterpart support for PHC-MOU activities for routine immunization and primary healthcare. This is the allocated (budgeted) amount.

• Provision of support for PHC-MOU activities (Primary Health Care Development Agency), 2026 Approved Budget: ₦100.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): 04050126007201 - Functional health facilities Basic Health Care Provision Funds (BHCF) 25% Counterpart (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 70
_Reply *show working* to see the rows and arithmetic._
```

## m07: not found (search, 13.1s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m08: answered (category, 5.9s)

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

## m09: partial (lines:list, 17.3s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
The budget shows two irrigation-scheme capital line items and one tube-wells capital line item. Kware irrigation scheme (SPIN Project) is ₦800.00 million in 2026 approved and Irrigation Scheme Youth empowerment (NEMI NA KANKA) is ₦200.00 million in 2026 approved. Construction of Tube Wells across the State had ₦531.96 million in 2025 revised and 0.00 in 2026 approved. No line item specifically named solar-powered tube wells is shown.

• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦800.00 million
• Construction of Tube Wells across the State (Nigeria CARES- Fadama Programme) [Capital Expenditure by Project], 2025 Revised Budget: ₦531.96 million
• … +1
• Not found: solar-powered tube wells as a named line item

📄 *Sources:* Sokoto State FY 2026 Budget, p. 53
_Reply *show working* to see the rows and arithmetic._
```

## m10: partial (lines:list, 16.7s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
Eh, akwai kuɗaɗen da aka ware a kasafin 2026. Don gyaran madatsun ruwa akwai ₦54.56 miliyan, don gyaran tangunan ruwa a cikin birnin Sokoto akwai ₦35.00 miliyan, kuma don gyaran aikin ruwan famfo na birnin Sokoto (Sokoto Township Water Works) akwai ₦25.00 biliyan. Dukkaninsu kuɗaɗen da aka amince da su ne a kasafin 2026, ba kashewa ba.

• Rehabilitation and expansion of earth dams at Rafin Duma (Ministry of Water Resources), 2026 Approved Budget: ₦54.56 miliyan
• Rehabilitation of Overhead Tanks within Sokoto Metropolis (Water Board), 2026 Approved Budget: ₦35.00 miliyan
• Rehabilitation of Sokoto Township Water Works (Water Board), 2026 Approved Budget: ₦25.00 biliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): Construction of Small Earth Dams at Kagara Isa LGA (Ministry of Water Resources) (2026 Approved Budget); Construction of Small Earth Dams at Kamarawa Isa LGA (Ministry of Water Resources) (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 58
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 11.6s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
• Not added up: these lines are printed in different tables of one budget, which can show the same money twice.

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Development of Grazing Reserve for posture production (Livestock Development Programme), 2026 Approved Budget: ₦50.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40, 61
_Reply *show working* to see the rows and arithmetic._
```

## m12: partial (lines:list, 11.1s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
No separate capital lines for flyovers or inner-city dualization under the Ministry of Works are shown in the 2026 Approved Budget. For rural roads under the Department for Rural Roads (the unit handling rural feeder roads) the 2026 capital allocations are: Construction/Provision of Roads ₦2.25 billion, Rehabilitation of existing rural roads projects ₦200.00 million, tarring across the state ₦209.11 million and Rural Access and Mobility Project (RAMP) ₦7.90 billion, all figures are approved budgets not actual spending.

• Department for Rural Roads (code 023405700100) – construction / provision of roads, 2026 Approved Budget: ₦2.25 billion
• Rehabilitation of existing projects under rural roads (Department for Rural Roads), 2026 Approved Budget: ₦200.00 million
• (tarring) across the state (Department for Rural Roads), 2026 Approved Budget: ₦209.11 million
• (RAMP) (Department for Rural Roads) – construction / provision of roads, 2026 Approved Budget: ₦7.90 billion
• Not found: Flyovers, inner-city dualization

📄 *Sources:* Sokoto State FY 2026 Budget, p. 56
_Reply *show working* to see the rows and arithmetic._
```

## m13: not found (search, 9.9s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m14: answered (lines:sum, 10.8s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
An ware ₦2.38 biliyan (lissafin Kasafi) a kasafin 2026 don gina sabbin gidaje: ₦382.98 miliyan don kammala gidan ma'aikata 53 da ₦2.00 biliyan don gina rukunin gidaje 500 a Wajekke. Dukansu kudaden da aka amince (allocation) ne, ba wanda aka kashe ba.

• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan
• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: partial (lines:list, 20.5s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
I, an aka ware kudi a kasafin 2026 don saukaka sufurin jama'a. An ware ₦1.50 biliyan don sufuri a ciki da wajen jihar (SSTA) da ₦2.40 biliyan don siyan bas 20 na SSTA, da kuma ₦140.00 miliyan don siyan babura masu kafa uku 300 ga nakasassu don saukaka sufuri. Dukkan su kudadene da aka tsara (approved), ba kudin da aka kashe ba.

• INTER AND INTRA STATE TRANSPORTATION (SSTA) (Ministry of Transport), 2026 Approved Budget: ₦1.50 biliyan
• PURCHASE OF 20 NO TOYOTA 18-SEATER BUSES for SSTA (Ministry of Transport), 2026 Approved Budget: ₦2.40 biliyan
• Purchase of 300 Trycle bicycle for disable for ease transportation (Agency for Persons Living With Disabilities), 2026 Approved Budget: ₦140.00 miliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): PURCHASE OF BUSES (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 55, 64
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m16: answered (search, 12.8s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
The State Government set 2025 IGR at ₦47.44 billion, later revised to ₦47.94 billion, and collected ₦20.58 billion in Q1–Q4 2025 (42.9% of the final budget). The 2026 IGR target is ₦74.52 billion.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1, 11; Budget Implementation Report Q4 2025, p. 9, 13; Sokoto State Government 2025 Approved Budget, p. 1
```

## m17: answered (lines:ratio, 10.3s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
Capital Expenditure approved for 2026 is ₦553.34 billion. Recurrent Expenditure approved for 2026 is ₦205.36 billion. The exact ratio of Capital to Recurrent is 2.69 : 1 (Kasafi's calculation).

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (lines:list, 9.8s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
For the 2026 approved budget, domestic debt servicing is budgeted as principal of ₦10.03 billion plus interest of ₦6.00 billion. External debt deductions are budgeted as principal of ₦2.42 billion plus interest of ₦1.31 billion. All figures are allocated (budgeted), not spent.

• DOMESTIC PRINCIPAl (code 220604), 2026 Approved Budget: ₦10.03 billion
• DOMESTIC INTEREST / DISCOUNT (code 220602), 2026 Approved Budget: ₦6.00 billion
• FOREIGN PRINCIPAL (code 220603), 2026 Approved Budget: ₦2.42 billion
• FOREIGN INTEREST / DISCOUNT (code 220601), 2026 Approved Budget: ₦1.31 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29
_Reply *show working* to see the rows and arithmetic._
```

## m19: answered (lines:compare, 13.0s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
The approved overhead allocation for the Government House unit was ₦4.20 billion in 2025. The approved overhead allocation for the same unit was ₦3.71 billion in 2026.

• Government House (one agency or unit, overhead (running costs), code 011100100100), 2025 Approved Budget: ₦4.20 billion
• Government House (one agency or unit, overhead (running costs), code 011100100100), 2026 Approved Budget: ₦3.71 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 14; Sokoto State FY 2026 Budget, p. 21
_Reply *show working* to see the rows and arithmetic._
```

## m20: answered (search, 12.2s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa karshen zangon farko (Q1) na 2026, an kashe 3.0% na kasafin manyan ayyuka na daukacin jihar. Kasafin da aka amince da shi (total) ₦553.34 biliyan ne, kuma abin da aka kashe a Q1 2026 kawai ₦16.82 biliyan ne.

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 27
```

## m21: answered (query_budget:rank, 12.9s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
There are no distinct three lowest because several ministries and agencies each recorded 0.0% for Q1–Q2 2026, including the Fiscal Responsibility Commission, Ministry for Skills Acquisition and Entrepreneurship Development, Ministry of Commerce and Industry, Ministry of Culture & Tourism, Ministry of Justice and Ministry of Solid Minerals and Natural Resources, Ministry for Local Government and Chieftancy, and Ministry for Special Duties, Sokoto State House of Assembly and Sokoto State Independent Electoral Commission.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 26, 27, 28
_Reply *show working* to see the rows and arithmetic._
```

## m22: answered (search, 3.6s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
*Ministry of Health* (code 052100000000):
• Total: spent so far (Q1–Q2) ₦12.36 billion; share of the revised budget spent 10.6% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## m23: answered (search, 9.8s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
The 2026 revised budgeted personnel total was ₦70.57 billion (allocated). Actual personnel spending in January–June 2026 (Q1–Q2 only) was ₦37.30 billion, which is 52.8% of the revised budget (spent). The balance (variance) against the revised budget was ₦33.28 billion.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19
```

## m24: partial (lines:list, 14.9s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Babu layin horar da matasa sana'o'i da tallafin kudi na Ma'aikatar Matasa da Wasanni da aka nuna daban a 2026. Abin da aka nuna kawai shi ne jimillar Ma'aikatar Matasa da Wasanni gaba daya na ₦17.06 biliyan a kasafin 2026 da aka amince da shi.

• Ministry of Youth and Sports Development (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 051300000000), 2026 Approved Budget: ₦17.06 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.
• Ba a samu ba: horar da matasa sana'o'i da tallafin kudi na Ma'aikatar Matasa da Wasanni

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m25: partial (lines:list, 15.4s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
Yes, the 2026 approved budget shows dedicated lines for all three. Assistive devices appear as Therapeutic Appliances and Equipment at ₦50.00 million, special schools appear as Raji Special School rehabilitation at ₦500.00 million, and welfare support appears as Disability and Survival Support at ₦1.99 billion. All figures are approved allocations, not spending.

• THERAPEUTIC APPLIANCES AND EQUIPTMENT (code 70713), 2026 Approved Budget: ₦50.00 million
• Raji Special School (Ministry for Basic Education), 2026 Approved Budget: ₦500.00 million
• Disability and Survival Support (objective inside a sector, all spending (total), code 2306), 2026 Approved Budget: ₦1.99 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): DISABILITY (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 42, 65, 188
_Reply *show working* to see the rows and arithmetic._
```

## m26: partial (lines:list, 16.3s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
• Ministry for Women Affairs (ministry total including its agencies, all spending (total), code 051400000000), 2025 Approved Budget: ₦8.44 billion
• Ministry for Women Affairs (ministry total including its agencies, all spending (total), code 051400000000), 2026 Approved Budget: ₦7.24 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Possibly relevant too, not counted (I wasn't sure on a second reading): tabs for Youth and Women Empowerment (POVERTY REDUCTION PROGRAMME) (2025 Revised Budget); tabs for Youth and Women Empowerment (POVERTY REDUCTION PROGRAMME) (2026 Approved Budget); Conduct of Ramadan Lectures for Women (Ministry for Women Affairs) (2025 Revised Budget); Conduct of Ramadan Lectures for Women (Ministry for Women Affairs) (2026 Approved Budget)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
_Reply *show working* to see the rows and arithmetic._
```

## m27: partial (lines:list, 12.6s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
Kasafin 2026 bai ware kudi daban ba musamman don ayyukan raya karkara da rage talauci a kananan hukumomin kan iyaka. Abin da aka buga shi ne jimillar babban bangaren: ₦3.19 biliyan na Poverty Alleviation, ₦1.70 biliyan na POVERTY REDUCTION PROGRAMME, da ₦41.38 biliyan na Water Resources and Rural Development a matsayin jimillar bangare na babban kashe kudi. Dukkan wadannan kudin da aka ware ne (approved budget), ba kudin da aka kashe ba.

• Poverty Alleviation (code 03), 2026 Approved Budget: ₦3.19 biliyan
• POVERTY REDUCTION PROGRAMME (hukuma ɗaya, manyan ayyuka, code 011102000100), 2026 Approved Budget: ₦1.70 biliyan
• Water Resources and Rural Development (jimillar ɓangare, manyan ayyuka, code 10), 2026 Approved Budget: ₦41.38 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 25, 45, 46
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m28: not found (search, 10.0s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
I couldn't find the answer to that in the documents I have.
```

## m29: answered (lines:list, 17.3s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
Gwamnati ta ware ₦9.12 biliyan a kasafin 2025 da ₦5.00 biliyan a kasafin 2026 don biyan gratuity ga tsofaffin ma’aikata. Wadannan kudaden da aka ware (budgeted) ne, ba abin da aka kashe ba.

• GRATUITY (manyan ayyuka, code 21030101), 2025 Approved Budget: ₦9.12 biliyan
• Gratuity (shiri cikin ɓangare, duk kashe kuɗi (jimilla), code 230502), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 42
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 10.0s)

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

## m31: partial (lines:list, 14.5s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
No separate line named 'Sokoto State Community Guard Corps' is printed in the 2026 approved budget. The broader aggregate that covers internal security is the Department for Security Matters with an approved 2026 total of ₦26.37 billion (overhead ₦18.00 billion and personnel ₦63.37 million). Within the economic classification, SECURITY SERVICES is budgeted at ₦8.62 billion and SECURITY VOTE (INCLUDING OPERATIONS) at ₦8.21 billion. A specific logistics project for security guards - Purchase of 250 Bajaj Motorcycles for Security Guards - is budgeted at ₦405.00 million. All figures are 2026 Approved Budget allocations.

• Department for Security Matters (one agency or unit, all spending (total), code 017000100200) [Total Expenditure by Administrative Classification], 2026 Approved Budget: ₦26.37 billion
• Department for Security Matters (one agency or unit, overhead (running costs), code 017000100200) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2026 Approved Budget: ₦18.00 billion
• Department for Security Matters (one agency or unit, personnel (salaries), code 017000100200), 2026 Approved Budget: ₦63.37 million
• SECURITY SERVICES (code 22020601), 2026 Approved Budget: ₦8.62 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion
• … +1
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 19, 22, 28, 52
_Reply *show working* to see the rows and arithmetic._
```

## m32: partial (lines:list, 14.0s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
The 2026 approved capital allocation for renovation of 25 Upper and lower Sharia Courts is ₦102.06 million. The broader State Judiciary, which administers justice, has ₦3.39 billion approved as capital, ₦1.60 billion as personnel and ₦3.18 billion as overhead. Recurrent for the Sharia courts renovation itself is not shown separately.

• Renovation of 25No Upper and lower Sharia Courts (Shari’a Court of Appeal), 2026 Approved Budget: ₦102.06 million
• State Judiciary (ministry total including its agencies, capital, code 031800000000) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦3.39 billion
• State Judiciary (ministry total including its agencies, personnel (salaries), code 031800000000) [Personnel Expenditure by Administrative Classification], 2026 Approved Budget: ₦1.60 billion
• State Judiciary (ministry total including its agencies, overhead (running costs), code 031800000000) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2026 Approved Budget: ₦3.18 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26, 63
_Reply *show working* to see the rows and arithmetic._
```

## m33: answered (category, 7.9s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
Statewide, the 2026 approved budget has SECURITY VOTE (INCLUDING OPERATIONS) (22020604) ₦8.21 billion. By the end of June 2026, ₦3.66 billion of it had been spent statewide (44.5%, Budget Implementation Report Q2 2026).

Largest:
• Department for Security Matters: ₦8.00 billion
• SSG'S Office: ₦210.00 million

✓ The agencies' rows add up exactly to the printed statewide totals.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 28, 88, 104; Budget Implementation Report Q2 2026, p. 31
_Reply *show working* to see the rows and arithmetic._
```

## m34: not found (search, 13.4s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Ban sami amsar wannan tambayar a cikin takardun da nake da su ba.
```

## m35: answered (lines:list, 13.9s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
The Sokoto State Independent Electoral Commission's total allocation is ₦460.48 million in the 2026 Approved Budget. The selected line below shows its exact administrative code and page number.

• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: partial (search, 16.4s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
The budget does not show the asked airport construction separately. The wider Airways sector 2026 approved budget (capital only, not total) is ₦36.00 billion.

• 2026 approved budget (capital): ₦36.00 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 47
```

## m37: answered (search, 15.1s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
Jimillar kasafin fannin Information Communication and Technology (jimilla) da aka amince da shi a 2025 shi ne ₦3.30 biliyan daga shafi 24 na kasafin 2025, yayin da na 2026 shi ne ₦7.15 biliyan daga shafi 41 na kasafin 2026. Duk waɗannan kuɗaɗen da aka ware ne a teburin Total Expenditure by Programme, ba kuɗin da aka kashe ba.

• 2025 kasafin da aka sabunta na ma'aikata (jimilla): ₦1.66 biliyan
• 2026 kasafin da aka amince na ma'aikata (jimilla): ₦3.59 biliyan
• 2025 kashe na fanni Janairu-Satumba kaɗai (jimilla): ₦2.71 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 41; Sokoto State Government 2025 Approved Budget, shafi 24
```

## m38: not found (search, 13.4s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Kasafin jihar bai nuna kuɗin da aka ware kai tsaye ga Ƙaramar Hukumar Wamakko ba. Layukan kasafin jiha na cibiyoyin da ke Wamakko (misali asibiti ko makaranta) kuɗin jiha ne, ba na ƙaramar hukumar ba. Ƙananan hukumomi suna samun kasonsu na doka daga asusun tarayya daban, kuma takardun da nake da su ba su nuna na Wamakko ba.
```

## m39: answered (search, 4.2s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
*Ministry of Environment* (code 053500000000):
• Capital: share of the revised budget spent 48.6% (Kasafi's calculation)
• Total: share of the revised budget spent 47.0% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18, 28
```
