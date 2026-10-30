# Open-question run: mid_tier.json

39 questions: answered 21, partial 13, not found 4, clarify 1 | wrong 0 of 11 checked | median 12.4s

```
plan          n=39 median   3.8s    30% of all time
line_search   n=33 median   1.1s     8% of all time
read          n=33 median   5.6s    40% of all time
read1         n=33 median   3.6s    27% of all time
read2         n=33 median   3.8s    28% of all time
reread        n= 7 median   5.1s     6% of all time
page_search   n=34 median   1.1s     7% of all time
compose       n=26 median   5.8s    33% of all time
answer        n=38 median   6.4s    54% of all time
row readings: 77 model calls for 33 questions (2 = no retry)
```

## m01: answered (lines:sum, 10.3s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
I, akwai kudin tallafin karatu da aka ware wa dalibai a kasafin 2026. Tallafin karatu na cikin gida ₦1.60 biliyan, tallafin karatu na kasashen waje kuma ₦1.50 biliyan. Jimillarsu ₦3.10 biliyan (lissafin Kasafi). Dukkan kudaden da aka ware (budgeted) ne na 2026.

• Domestic Scholarship (code 22021025), 2026 Approved Budget: ₦1.60 biliyan
• FOREIGN SCHOLARSHIP SCHEME (code 22021020), 2026 Approved Budget: ₦1.50 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m02: partial (lines:list, 20.5s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
SUBEB classroom construction had two allocated lines in the 2025 approved budget: ₦4.55 billion and ₦500.00 million. For renovation/rehabilitation of public schools, ₦205.00 million was allocated in 2025 (revised) and ₦205.00 million in the 2026 approved budget. No separate 2026 SUBEB classroom construction line is shown.

• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦4.55 billion
• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦500.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million
• Not found: 2026 SUBEB classroom construction allocation

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 29; Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: partial (lines:list, 10.4s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
The 2026 approved budget shows a Girls/Boys child education programme of ₦200.00 million, a School feeding programme of ₦2.03 billion including a MEAL SUBSIDY TO GOVERNMENT SCHOOLS project of ₦2.00 billion, and an Increase in access, retention, and completion rate objective of ₦11.26 billion.

• Girls/Boys child education (programme inside a sector, all spending (total), code 050305), 2026 Approved Budget: ₦200.00 million
• School feeding (programme inside a sector, all spending (total), code 050203), 2026 Approved Budget: ₦2.03 billion
• MEAL SUBSIDY TO GOVERNMENT SCHOOLS (code 22050102), 2026 Approved Budget: ₦2.00 billion
• Increase in access, retention, and completion rate at all levels (objective inside a sector, all spending (total), code 0502), 2026 Approved Budget: ₦11.26 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): Female Education Board (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40, 41, 149
_Reply *show working* to see the rows and arithmetic._
```

## m04: answered (lines:share, 16.8s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
• Share (↑ ÷ ↓): 15.8% (Kasafi's calculation)

• HEALTH (all spending (total), code 707), 2026 Approved Budget: ₦120.13 billion ↑
• Total Expenditure, 2026 Approved Budget: ₦758.70 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1, 32
_Reply *show working* to see the rows and arithmetic._
```

## m05: answered (category, 5.8s)

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

## m06: partial (lines:list, 11.0s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
The 2026 approved counterpart for Basic Health Care Provision Funds (BHCF) for primary healthcare is ₦109.00 million. No separate counterpart line for routine immunization is shown.

• 04050126007201 - Functional health facilities Basic Health Care Provision Funds (BHCF) 25% Counterpart, 2026 Approved Budget: ₦109.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): 04050124000403 - Functional health facilities BHCF Counterpart Funds for SOCHEMA (2026 Approved Budget); Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health) (2026 Approved Budget); 04050124008401 - Functional health facilities Support for Family Planning Programme (Counterpart) (2026 Approved Budget); 04050124008201 - Functional health facilities Provision of support for PHC-MOU activities (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 229
_Reply *show working* to see the rows and arithmetic._
```

## m07: partial (search, 20.7s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
The Q2 2026 reports do not show releases or spending separately for maternal and child healthcare centers across rural LGAs. A state facility located in an LGA is not an allocation to that LGA, as LGAs receive statutory allocations separately. The specific Q2 2026 released and spent figure was not found, only broader health lines.

• Reproductive, maternal and neonatal health, 2026 approved budget (capital): ₦170.00 million
• Primary Healthcare Expenditure, Q1-Q2 2026 spent (total): ₦1.22 billion (16.9% of the revised budget)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 28, 43, 52; Sokoto State FY 2026 Budget, p. 45
```

## m08: answered (category, 8.0s)

**Q:** Nawa gwamnatin jihar Sokoto ta ware don sayen takin zamani da tallafin kayan noma a shekarar 2026, kuma nawa aka riga aka kashe?

```
_Ban ga lokacin kashe kudin ba, don haka na yi amfani da rahoton aiwatarwa na Q2 2026 mafi sabo._

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

## m09: partial (lines:list, 14.5s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
Specific capital project lines are shown for irrigation schemes and for tube wells. Irrigation Scheme Youth empowerment (NEMI NA KANKA) was ₦200.00 million in 2025 Revised and ₦200.00 million in 2026 Approved. Kware irrigation scheme (SPIN Project) was ₦200.00 million in 2025 Revised and ₦800.00 million in 2026 Approved. Construction of Tube Wells across the State (Nigeria CARES-Fadama) was ₦531.96 million in 2025 Revised and 0.00 in 2026 Approved. No line combining solar-powered with tube wells is shown separately.

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

## m10: partial (lines:list, 13.5s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
Eh, akwai kudade don ruwan famfo a birnin Sokoto a kasafin 2026 da aka amince da shi. An ware ₦25.00 biliyan don gyaran ayyukan ruwan garin Sokoto, da ₦35.00 miliyan don gyaran manyan tankunan ruwa a cikin birnin Sokoto. Ba a nuna wani layi daban don gyaran madatsun ruwa ba.

• Rehabilitation of Sokoto Township Water Works (Water Board), 2026 Approved Budget: ₦25.00 biliyan
• Rehabilitation of Overhead Tanks within Sokoto Metropolis (Water Board), 2026 Approved Budget: ₦35.00 miliyan
• Ba a samu ba: gyaran madatsun ruwa

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 58
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 8.7s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
The combined 2026 approved allocation for animal health/livestock diseases management and livestock feeds development, which covers grazing reserves, is ₦13.30 billion (Kasafi's calculation). These are allocated (budgeted) amounts, not spent amounts.

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Livestock feeds development (programme inside a sector, all spending (total), code 010206), 2026 Approved Budget: ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40
_Reply *show working* to see the rows and arithmetic._
```

## m12: clarify (search, 12.2s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
I can read your question two ways. Which do you mean?
```

## m13: not found (search, 10.3s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m14: answered (lines:sum, 10.9s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
An ware ₦6.43 biliyan (lissafin Kasafi) a kasafin 2026 don gina sabbin gidaje: ₦4.00 biliyan na rukunin gidaje 500 a Gidan Salanke, da ₦2.00 biliyan na rukunin gidaje 500 a Wajekke, da ₦382.98 miliyan na kammala gidan ma’aikata 53 a jami’a, da ₦51.00 miliyan na gina gidaje 6 na sabbin Khadis. Dukkan kudaden da aka ware ne (approved budget).

• Construction of 500 Housing units at Gidan Salanke (Min of Lands and Housing), 2026 Approved Budget: ₦4.00 biliyan
• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan
• Construction of 6 no Houses for 6 New Hon. Khadis in the State (Shari’a Court of Appeal), 2026 Approved Budget: ₦51.00 miliyan
• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 63, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: answered (lines:list, 10.0s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
Eh, akwai kudi a kasafin 2026 don saukaka sufurin jama'a. An ware ₦1.50 biliyan don sufuri a ciki da wajen jihar (SSTA), da ₦2.40 biliyan don sayen bas 20 na SSTA, da ₦140.00 miliyan don sayen keke uku 300 ga nakasassu don saukaka sufuri. Dukkan su kudin kasafi ne da aka amince (approved), ba kudin da aka kashe ba.

• INTER AND INTRA STATE TRANSPORTATION (SSTA) (Ministry of Transport), 2026 Approved Budget: ₦1.50 biliyan
• PURCHASE OF 20 NO TOYOTA 18-SEATER BUSES for SSTA (Ministry of Transport), 2026 Approved Budget: ₦2.40 biliyan
• Purchase of 300 Trycle bicycle for disable for ease transportation (Agency for Persons Living With Disabilities), 2026 Approved Budget: ₦140.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 55, 64
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m16: answered (search, 11.8s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
The State Government originally projected 2025 IGR at ₦47.44 billion, later revised to ₦47.94 billion. Actual full-year collections (Q1–Q4 2025) were ₦20.58 billion (42.9% of the final budget). The approved 2026 IGR target is ₦74.52 billion.

• 2025 January–September actual (total): ₦14.62 billion

📄 *Sources:* Budget Implementation Report Q4 2025, p. 9; Sokoto State FY 2026 Budget, p. 1, 11; Sokoto State Government 2025 Approved Budget, p. 1
```

## m17: answered (lines:ratio, 8.4s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
The approved 2026 budget allocates ₦553.34 billion to Capital Expenditure and ₦205.36 billion to Recurrent Expenditure. The ratio of Capital to Recurrent is 2.69 : 1 (Kasafi's calculation).

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (lines:list, 12.1s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
For 2026, domestic debt is budgeted at ₦10.03 billion for principal plus ₦6.00 billion for interest/discount, all allocated (budgeted). External debt deductions are budgeted at ₦2.42 billion for principal plus ₦1.31 billion for interest/discount, all allocated (budgeted).

• DOMESTIC PRINCIPAl (code 220604), 2026 Approved Budget: ₦10.03 billion
• DOMESTIC INTEREST / DISCOUNT (code 220602), 2026 Approved Budget: ₦6.00 billion
• FOREIGN PRINCIPAL (code 220603), 2026 Approved Budget: ₦2.42 billion
• FOREIGN INTEREST / DISCOUNT (code 220601), 2026 Approved Budget: ₦1.31 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29
_Reply *show working* to see the rows and arithmetic._
```

## m19: answered (lines:list, 14.0s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
The Office of the Executive Governor (Government House's overhead) was allocated ₦4.20 billion in the 2025 approved budget and ₦3.71 billion in the 2026 approved budget. Both figures are budgeted allocations.

• Government House (one agency or unit, overhead (running costs), code 011100100100), 2025 Approved Budget: ₦4.20 billion
• Government House (one agency or unit, overhead (running costs), code 011100100100), 2026 Approved Budget: ₦3.71 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 14; Sokoto State FY 2026 Budget, p. 21
_Reply *show working* to see the rows and arithmetic._
```

## m20: answered (search, 12.7s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa ƙarshen zangon farko (Q1) na 2026, an kashe 3.0% na kasafin manyan ayyuka na daukacin jihar. Wannan kaso na Q1 2026 kaɗai ne.

• 2026 kasafin da aka amince (manyan ayyuka): ₦553.34 biliyan
• Q1 2026 da aka kashe (Q1 2026 kaɗai): ₦16.82 biliyan

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 27
```

## m21: answered (query_budget:rank, 17.0s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
The lowest capital absorption rate in Q1–Q2 2026 is 0.0%, shared by the Ministry for Skills Acquisition and Entrepreneurship Development, Ministry of Commerce and Industry, Ministry of Culture & Tourism, Ministry of Justice, Ministry of Solid Minerals and Natural Resources, Ministry for Local Government and Chieftancy and Ministry for Special Duties, with the Fiscal Responsibility Commission, Sokoto State House of Assembly and Sokoto State Independent Electoral Commission also at 0.0%.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 26, 27, 28
_Reply *show working* to see the rows and arithmetic._
```

## m22: answered (lines:share, 18.1s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
• Share (↑ ÷ ↓): 10.6% (Kasafi's calculation)

• Ministry of Health (ministry total including its agencies, all spending (total), code 052100000000) [Total Expenditure by Administrative Classification], 2026 Performance Year to Date (Q1-Q2): ₦12.36 billion ↑
• Ministry of Health (ministry total including its agencies, all spending (total), code 052100000000) [Total Expenditure by Administrative Classification], 2026 Revised Budget: ₦116.91 billion ↓

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
_Reply *show working* to see the rows and arithmetic._
```

## m23: answered (search, 9.2s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
The 2026 personnel budget (allocated) was ₦70.57 billion. Through the first half of 2026 (Q1–Q2 2026 only), actual payroll outturn was ₦37.30 billion (52.8% of the revised budget), leaving a balance of ₦33.28 billion.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19
```

## m24: partial (lines:list, 15.2s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Ba a nuna layin daban don horar da matasa sana'o'i da tallafin kudi a karkashin Ma'aikatar Matasa da Wasanni a 2026 a cikin layukan da aka bayar. Jimillar kasafin Ma'aikatar Matasa da Wasanni da aka ware a 2026 ita ce ₦17.06 biliyan (kasafin da aka amince da shi), wannan jimillar ma'aikatar baki daya ce ba lambar aikin horon sana'a kadai ba.

• Ministry of Youth and Sports Development (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 051300000000), 2026 Original Budget: ₦17.06 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 17
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m25: partial (lines:list, 17.1s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
Yes, the 2026 approved budget shows dedicated lines for all three. Assistive devices are budgeted as Therapeutic Appliances and Equipment at ₦50.00 million, Raji Special School rehabilitation is budgeted at ₦500.00 million, and welfare support is budgeted under Disability at ₦3.07 billion including Disability and Survival Support at ₦1.99 billion. All figures are allocations (budgeted), not spent amounts.

• THERAPEUTIC APPLIANCES AND EQUIPTMENT (code 70713), 2026 Approved Budget: ₦50.00 million
• Raji Special School (Ministry for Basic Education), 2026 Approved Budget: ₦500.00 million
• DISABILITY (all spending (total), code 71012), 2026 Approved Budget: ₦3.07 billion
• Disability and Survival Support (objective inside a sector, all spending (total), code 2306), 2026 Approved Budget: ₦1.99 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): centres of Goronyo, Kware and Bodinga (Agency for Persons Living With Disabilities) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 33, 42, 65, 188
_Reply *show working* to see the rows and arithmetic._
```

## m26: partial (lines:list, 12.7s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
_Assumption: used approved budgets for 2025 and 2026._

The Women's Economic Empowerment programme is provided ₦3.15 billion in the 2026 Approved Budget and ₦4.94 billion in the 2025 Revised Budget. No separate lines for orphanages or destitute homes are shown in the lines provided.

• Women's Economic Empowerment (programme inside a sector, all spending (total), code 230301) [Total Expenditure by Programme (Sector, Objective and Programme)], 2025 Revised Budget: ₦4.94 billion
• Women's Economic Empowerment (programme inside a sector, all spending (total), code 230301) [Total Expenditure by Programme (Sector, Objective and Programme)], 2026 Approved Budget: ₦3.15 billion
• Not found: orphanages, destitute homes

📄 *Sources:* Sokoto State FY 2026 Budget, p. 42
_Reply *show working* to see the rows and arithmetic._
```

## m27: partial (lines:list, 17.3s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
Babu layin kasafin 2026 da ya ware kudi daban domin raya karkara da rage talauci a kananan hukumomin kan iyaka. Abin da aka buga kawai shi ne jimillar sassan gaba daya: ₦44.37 biliyan ga Ruwa da Raya Karkara da ₦6.10 biliyan ga Rage Talauci, duka kasafin da aka amince da su (allocated).

• Water Resources and Rural Development (jimillar ɓangare, duk kashe kuɗi (jimilla), code 10), 2026 Approved Budget: ₦44.37 biliyan
• Poverty Alleviation (jimillar ɓangare, duk kashe kuɗi (jimilla), code 03), 2026 Approved Budget: ₦6.10 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 40, 41
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m28: not found (search, 10.8s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
I couldn't find the answer to that in the documents I have.
```

## m29: answered (lines:list, 13.2s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
Gwamnati ta ware ₦9.12 biliyan a kasafin 2025 da aka amince don biyan Gratuity. A kasafin 2026 da aka amince ta ware ₦5.00 biliyan don Gratuity.

• GRATUITY (manyan ayyuka, code 21030101), 2025 Approved Budget: ₦9.12 biliyan
• GRATUITY (manyan ayyuka, code 21030101), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 27
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 8.6s)

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

## m31: partial (lines:list, 14.1s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
No budget line explicitly titled 'Sokoto State Community Guard Corps' is shown in the provided 2026 approved budget lines. The internal security logistics support line that is shown is Purchase of Motor Vehicles for Guards (Department for Security Matters) with an approved 2026 allocation of ₦3.00 billion (allocated, not spent).

• Guards (Department for Security Matters) – purchase of motor vehicles, 2026 Approved Budget: ₦3.00 billion
• Not found: Sokoto State Community Guard Corps as a separately labelled line

📄 *Sources:* Sokoto State FY 2026 Budget, p. 52
_Reply *show working* to see the rows and arithmetic._
```

## m32: partial (lines:list, 14.4s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
• Renovation of 25No Upper and lower Sharia Courts (Shari’a Court of Appeal), 2026 Approved Budget: ₦102.06 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): Law and Justice (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 63
_Reply *show working* to see the rows and arithmetic._
```

## m33: answered (category, 5.9s)

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

## m34: not found (search, 10.8s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Ban sami amsar wannan tambayar a cikin takardun da nake da su ba.
```

## m35: answered (lines:list, 12.4s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
The 2026 Approved Budget allocation for SIEC is ₦460.48 million.

• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: partial (search, 18.7s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
The excerpts do not show the line item asked about. The closest published totals are listed below, with approved amounts as allocated and January-to-September amounts as spent.

• 2026 approved budget (capital) for Airways [sector total]: ₦36.00 billion
• 2025 performance January to September only (capital) for Airways: ₦12.34 billion
• 2026 approved budget (capital) for Ministry of Works [ministry total]: ₦58.13 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 26, 47
```

## m37: answered (search, 14.2s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
An ware jimillar ₦3.30 biliyan ga ɓangaren ICT a kasafin 2025 da aka amince da shi, kamar yadda shafi na 24 ya nuna. An ware jimillar ₦7.15 biliyan ga ɓangaren a kasafin 2026 da aka amince da shi, kamar yadda shafi na 41 ya nuna. Waɗannan ƙididdiga kuɗin da aka ware ne, ba kuɗin da aka kashe ba.

• 2025 (Janairu–Satumba kaɗai, aka kashe, jimilla): ₦2.71 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 41; Sokoto State Government 2025 Approved Budget, shafi 24
```

## m38: not found (search, 15.4s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Kasafin jihar bai nuna kuɗin da aka ware kai tsaye ga Ƙaramar Hukumar Wamakko ba. Layukan kasafin jiha na cibiyoyin da ke Wamakko (misali asibiti ko makaranta) kuɗin jiha ne, ba na ƙaramar hukumar ba. Ƙananan hukumomi suna samun kasonsu na doka daga asusun tarayya daban, kuma takardun da nake da su ba su nuna na Wamakko ba.
```

## m39: answered (search, 2.9s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
*Ministry of Environment* (code 053500000000):
• Capital: share of the revised budget spent 48.6% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 28
```
