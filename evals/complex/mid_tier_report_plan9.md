# Open-question run: mid_tier.json

39 questions: answered 21, partial 16, not found 2 | wrong 0 of 11 checked | median 13.6s

```
plan          n=39 median   3.7s    28% of all time
line_search   n=33 median   1.7s    11% of all time
read          n=32 median   6.4s    40% of all time
read1         n=32 median   4.2s    27% of all time
read2         n=32 median   4.0s    26% of all time
reread        n= 5 median   4.6s     4% of all time
page_search   n=34 median   1.6s    10% of all time
compose       n=29 median   5.8s    34% of all time
answer        n=37 median   6.3s    49% of all time
row readings: 75 model calls for 32 questions (2 = no retry)
```

## m01: answered (lines:sum, 12.4s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
Eh, akwai tanadi a kasafin 2026. An ware ₦1.60 biliyan don Domestic Scholarship da kuma ₦1.50 biliyan don FOREIGN SCHOLARSHIP SCHEME. Jimillarsu ₦3.10 biliyan (lissafin Kasafi). Dukansu kudaden da aka amince da su ne (approved), ba kashewa ba.

• Domestic Scholarship (code 22021025), 2026 Approved Budget: ₦1.60 biliyan
• FOREIGN SCHOLARSHIP SCHEME (code 22021020), 2026 Approved Budget: ₦1.50 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m02: partial (lines:list, 25.6s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
For SUBEB classroom work, 2025 approved construction was ₦4.55 billion plus ₦500.00 million. For renovation, the 2025 figure shown is the 2025 revised amount of ₦205.00 million, with ₦205.00 million allocated for 2026. No 2026 approved construction line for SUBEB is shown separately.

• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦4.55 billion
• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦500.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million
• Not found: 2026 approved allocation for SUBEB classroom construction

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 29; Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: answered (lines:list, 12.7s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
Specific 2026 approved allocations exist for all three areas. For girl-child education: the Female Education Board as an agency, Girls secondary schools equipment, and the Girls Education Project monitoring line budgeted at zero. For feeding: the School feeding programme and Meal Subsidy to Government Schools. For retention: the Increase in access, retention, and completion rate objective.

• Girls Education Project (11) with State to State (Ministry for Basic Education), 2026 Approved Budget: 0.00
• Girls secondary schools (Female Education Board) – purchase of industrial equipment, 2026 Approved Budget: ₦45.00 million
• Female Education Board (one agency or unit, all spending (total), code 051705700100), 2026 Approved Budget: ₦1.16 billion
• School feeding (programme inside a sector, all spending (total), code 050203), 2026 Approved Budget: ₦2.03 billion
• MEAL SUBSIDY TO GOVERNMENT SCHOOLS (code 22050102), 2026 Approved Budget: ₦2.00 billion
• … +1

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 40, 41, 65, 67, 149
_Reply *show working* to see the rows and arithmetic._
```

## m04: answered (lines:share, 17.1s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
15.8% (Kasafi's calculation) of the 2026 approved budget's Total Expenditure is allocated to the health sector. The health sector allocation is ₦120.13 billion out of Total Expenditure of ₦758.70 billion.

• HEALTH (all spending (total), code 707), 2026 Original Budget: ₦120.13 billion ↑
• Total Expenditure (all spending (total)), 2026 Original Budget: ₦758.70 billion ↓

📄 *Sources:* Budget Implementation Report Q2 2026, p. 15, 36
_Reply *show working* to see the rows and arithmetic._
```

## m05: answered (category, 7.7s)

**Q:** Nawa aka ware wa sayen magunguna da kayan aiki na asibitoci a karkashin Ma'aikatar Lafiya a kasafin 2026?

```
_Ban ga wani bayani ba, don haka na yi amfani da kasafin 2026 da aka amince da shi._

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

## m06: partial (lines:list, 11.7s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
• Provision of support for PHC-MOU activities (Primary Health Care Development Agency), 2026 Approved Budget: ₦100.00 million
• 04050126007201 - Functional health facilities Basic Health Care Provision Funds (BHCF) 25% Counterpart, 2026 Approved Budget: ₦109.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health) (2026 Approved Budget); BHCF Counterpart Funds for SOCHEMA (Sokoto State contributory health care mgt agency) (2026 Approved Budget); Support for Family Planning Programme (Counterpart) (Primary Health Care Development Agency) (2026 Approved Budget); 04050124000403 - Functional health facilities BHCF Counterpart Funds for SOCHEMA (2026 Approved Budget); 04050124008401 - Functional health facilities Support for Family Planning Programme (Counterpart) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 70, 229
_Reply *show working* to see the rows and arithmetic._
```

## m07: partial (lines:list, 13.9s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Primary Health Care Development Agency (one agency or unit, all spending (total), code 052100300100), 2026 Performance Year to Date (Q1-Q2): ₦1.22 billion [1]
• CONSTRUCTION / PROVISION OF HOSPITALS / HEALTH CENTRES (code 23020106), 2026 Performance Year to Date (Q1-Q2): ₦80.00 million [2]
• REHABILITATION / REPAIRS - HOSPITAL / HEALTH CENTRES (code 23030105), 2026 Performance Year to Date (Q1-Q2): ₦41.81 million [2]

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18, 53
```

## m08: answered (category, 7.0s)

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

## m09: partial (lines:list, 13.9s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦800.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): Construction of Tube Wells across the State (Nigeria CARES- Fadama Programme) (2025 Revised Budget); Construction of Tube Wells across the State (Nigeria CARES- Fadama Programme) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 53
_Reply *show working* to see the rows and arithmetic._
```

## m10: partial (lines:list, 14.9s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
Eh, akwai kudaden ruwa na birnin Sokoto a kasafin 2026: ₦25.00 biliyan don gyaran Sokoto Township Water Works da ₦35.00 miliyan don gyaran Overhead Tanks a cikin Sokoto Metropolis. Dukkan su kudaden da aka ware (approved) ne, ba wanda aka kashe ba. Ba a nuna layi daban na gyaran madatsun ruwa ba.

• Rehabilitation of Sokoto Township Water Works (Water Board), 2026 Approved Budget: ₦25.00 biliyan
• Rehabilitation of Overhead Tanks within Sokoto Metropolis (Water Board), 2026 Approved Budget: ₦35.00 miliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): boreholes, distribution pipes network across the State (Ministry of Water Resources) (2026 Approved Budget); through Construction Solar powered boreholes (Department for Rural Water) (2026 Approved Budget); Renovation of Boreholes across 40 wards in the State (Department for Special Projects) (2026 Approved Budget); 5.5Hp, 3Hp capacity for Maintenance of Boreholes (Water Board) (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 58
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 9.4s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
The 2026 approved allocation for animal health and livestock diseases management is ₦12.93 billion and for livestock feeds development, which covers grazing reserves, is ₦368.05 million. Together this is ₦13.30 billion (Kasafi's calculation).

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Livestock feeds development (programme inside a sector, all spending (total), code 010206), 2026 Approved Budget: ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40
_Reply *show working* to see the rows and arithmetic._
```

## m12: partial (lines:list, 15.0s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
No separate capital lines for flyovers or inner-city dualization under the Ministry of Works are shown for 2026. The rural feeder roads breakdown shown is through the Department for Rural Roads: Construction/Provision of Roads ₦2.25 billion; Rehabilitation of existing projects under rural roads ₦200.00 million; Construction of Rural Roads through RAMP ₦7.90 billion; and (tarring) across the state ₦209.11 million – all are 2026 Approved Budget allocations.

• Department for Rural Roads (code 023405700100) – construction / provision of roads, 2026 Approved Budget: ₦2.25 billion
• Rehabilitation of existing projects under rural roads (Department for Rural Roads), 2026 Approved Budget: ₦200.00 million
• 17100125000200 - Road - General Construction of Rural Roads through Rural access and mobility projects (RAMP), 2026 Approved Budget: ₦7.90 billion
• (tarring) across the state (Department for Rural Roads), 2026 Approved Budget: ₦209.11 million
• Not found: Flyovers and inner-city dualization

📄 *Sources:* Sokoto State FY 2026 Budget, p. 56, 217
_Reply *show working* to see the rows and arithmetic._
```

## m13: not found (search, 15.9s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m14: answered (lines:sum, 14.9s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
An ware kudade don gina sabbin gidaje a kasafin 2026: Gidan Salanke ₦4.00 biliyan, Wajekke ₦2.00 biliyan, gidajen Khadis 6 ₦51.00 miliyan, da kammala staff quarters 53 na jami'a ₦382.98 miliyan. Jimillarsu ₦6.43 biliyan (lissafin Kasafi). Dukkanin kudaden da aka ware ne (approved budget), ba wanda aka kashe ba.

• Construction of 500 Housing units at Gidan Salanke (Min of Lands and Housing), 2026 Approved Budget: ₦4.00 biliyan
• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan
• Construction of 6 no Houses for 6 New Hon. Khadis in the State (Shari’a Court of Appeal), 2026 Approved Budget: ₦51.00 miliyan
• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 63, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: partial (lines:list, 18.6s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
• INTER AND INTRA STATE TRANSPORTATION (SSTA) (Ministry of Transport), 2026 Approved Budget: ₦1.50 biliyan
• PURCHASE OF 20 NO TOYOTA 18-SEATER BUSES for SSTA (Ministry of Transport), 2026 Approved Budget: ₦2.40 biliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): Purchase of 300 Trycle bicycle for disable for ease transportation (Agency for Persons Living With Disabilities) (2026 Approved Budget); PURCHASE OF BUSES (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 55
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m16: answered (search, 12.3s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
The State Government originally budgeted ₦47.44 billion as Independent Revenue (IGR) for 2025, later revised to ₦47.94 billion. It actually collected ₦20.58 billion in the full year (Q1–Q4 2025), which was 42.9% of the final budget. The approved IGR target for 2026 is ₦74.52 billion.

📄 *Sources:* Budget Implementation Report Q4 2025, p. 9; Sokoto State FY 2026 Budget, p. 1, 11; Sokoto State Government 2025 Approved Budget, p. 1
```

## m17: answered (lines:ratio, 9.7s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
Capital Expenditure approved for 2026 is ₦553.34 billion and Recurrent Expenditure approved for 2026 is ₦205.36 billion. The exact ratio of Capital to Recurrent is 2.69 : 1 (Kasafi's calculation).

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (lines:list, 14.1s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
For 2026 approved budget, domestic debt is earmarked as principal of ₦10.03 billion plus interest of ₦6.00 billion. External debt is earmarked as principal of ₦2.42 billion plus interest of ₦1.31 billion. All figures are allocated (budgeted), not spent.

• DOMESTIC PRINCIPAl (code 220604), 2026 Approved Budget: ₦10.03 billion
• DOMESTIC INTEREST / DISCOUNT (code 220602), 2026 Approved Budget: ₦6.00 billion
• FOREIGN PRINCIPAL (code 220603), 2026 Approved Budget: ₦2.42 billion
• FOREIGN INTEREST / DISCOUNT (code 220601), 2026 Approved Budget: ₦1.31 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29
_Reply *show working* to see the rows and arithmetic._
```

## m19: answered (lines:compare, 15.7s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
• Difference (2026 Approved Budget vs 2025 Approved Budget): -₦489.02 million (-11.6%) (Kasafi's calculation)

• Government House (one agency or unit, overhead (running costs), code 011100100100), 2025 Approved Budget: ₦4.20 billion
• Government House (one agency or unit, overhead (running costs), code 011100100100), 2026 Approved Budget: ₦3.71 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 14; Sokoto State FY 2026 Budget, p. 21
_Reply *show working* to see the rows and arithmetic._
```

## m20: answered (search, 14.8s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa ƙarshen zangon farko na 2026, an kashe 3.0% na kasafin manyan ayyuka na daukacin jihar. Kasafin da aka amince da shi (manyan ayyuka) ₦553.34 biliyan ne, kuma abin da aka kashe a Q1 2026 (Q1 2026 kawai) ₦16.82 biliyan ne.

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 27
```

## m21: answered (query_budget:rank, 18.3s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
The lowest Q1–Q2 2026 capital performance is 0.0% of the 2026 Revised Budget, shared by the Ministry for Skills Acquisition and Entrepreneurship Development, the Ministry of Commerce and Industry, the Ministry of Culture & Tourism, the Ministry of Justice, the Ministry of Solid Minerals and Natural Resources, the Ministry for Local Government and Chieftancy, the Ministry for Special Duties, the Fiscal Responsibility Commission, the Sokoto State House of Assembly and the Sokoto State Independent Electoral Commission. They are tied as the lowest, so only some of them cannot be presented as the answer.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 26, 27, 28
_Reply *show working* to see the rows and arithmetic._
```

## m22: answered (search, 4.7s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
*Ministry of Health* (code 052100000000):
• Total: spent so far (Q1–Q2) ₦12.36 billion; share of the revised budget spent 10.6% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## m23: answered (search, 10.3s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
Budgeted personnel expenditure for 2026 was ₦70.57 billion. Actual payroll outturn through Q1-Q2 2026 only was ₦37.30 billion (52.8% of the revised budget). The balance against the revised budget was ₦33.28 billion.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19
```

## m24: partial (lines:list, 13.6s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Takamaiman layin horar da matasa sana'o'i da tallafin kudi a karkashin Ma'aikatar Matasa da Wasanni bai bayyana daban ba a takardun. Jimillar kasafin Ma'aikatar Matasa da Wasanni da hukumominta a 2026 da aka amince da ita ita ce ₦17.06 biliyan. Wannan jimilla ce, ba kudin shirin horo da tallafi kadai ba.

• Ministry of Youth and Sports Development (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 051300000000), 2026 Approved Budget: ₦17.06 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m25: partial (lines:list, 18.8s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
Yes, the 2026 budget shows dedicated functional totals. Therapeutic Appliances and Equipment is budgeted at ₦50.00 million. Disability is budgeted at ₦3.07 billion in total. No separate project lines for special schools or named welfare items are shown, only the broader Disability total.

• THERAPEUTIC APPLIANCES AND EQUIPTMENT (all spending (total), code 70713), 2026 Approved Budget: ₦50.00 million
• DISABILITY (all spending (total), code 71012), 2026 Approved Budget: ₦3.07 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Not found: separate project lines for special schools and named welfare support items

📄 *Sources:* Sokoto State FY 2026 Budget, p. 32, 33
_Reply *show working* to see the rows and arithmetic._
```

## m26: partial (lines:list, 15.1s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
The budget shows a provision for Women's Economic Empowerment of ₦4.94 billion for 2025 (revised) and ₦3.15 billion for 2026 (approved). No separate lines for orphanages or destitute homes are shown.

• Women's Economic Empowerment (programme inside a sector, all spending (total), code 230301) [Total Expenditure by Programme (Sector, Objective and Programme)], 2025 Revised Budget: ₦4.94 billion
• Women's Economic Empowerment (programme inside a sector, all spending (total), code 230301) [Total Expenditure by Programme (Sector, Objective and Programme)], 2026 Approved Budget: ₦3.15 billion
• Not found: orphanages, destitute homes

📄 *Sources:* Sokoto State FY 2026 Budget, p. 42
_Reply *show working* to see the rows and arithmetic._
```

## m27: partial (lines:sum, 17.5s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
_Ban ga wani bayani ba, don haka na yi amfani da kasafin 2026 da aka amince da shi._

Takardun kasafin ba su nuna warewa daban don kananan hukumomin kan iyaka ba. Abin da aka buga shi ne jimillar sassan da suka kula da aikin: bangaren Ruwa da Raya Yankunan Karkara an ware masa ₦44.37 biliyan a kasafin 2026 da aka amince, bangaren Rage Talauci kuma an ware masa ₦6.10 biliyan. Wadannan su ne jimillar da ake da su a takardu, ba adadin kananan hukumomin kan iyaka kadai ba (lissafin Kasafi).

• Water Resources and Rural Development (jimillar ɓangare, duk kashe kuɗi (jimilla), code 10), 2026 Approved Budget: ₦44.37 biliyan
• Poverty Alleviation (jimillar ɓangare, duk kashe kuɗi (jimilla), code 03), 2026 Approved Budget: ₦6.10 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 40, 41
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m28: partial (search, 12.3s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
The 2026 approved personnel budget is ₦70.57 billion (allocated, not spent). By Q2 2026, ₦37.30 billion had been spent (Q1–Q2 only, 52.8% of the revised budget). The evidence does not say whether the budget includes full implementation of the national minimum wage across all MDAs.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1, 19, 27; Budget Implementation Report Q2 2026, p. 19, 30
```

## m29: answered (lines:compare, 13.0s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
• Bambanci (2026 Approved Budget vs 2025 Approved Budget): -₦4.12 biliyan (-45.2%) (lissafin Kasafi)

• GRATUITY (manyan ayyuka, code 21030101), 2025 Approved Budget: ₦9.12 biliyan
• Gratuity (shiri cikin ɓangare, duk kashe kuɗi (jimilla), code 230502), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 42
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 8.0s)

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

## m31: partial (lines:list, 12.1s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• SECURITY SERVICES (code 22020601), 2026 Approved Budget: ₦8.62 billion [1]
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion [1]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 28
```

## m32: answered (lines:list, 12.6s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
The 2026 approved capital allocation for renovation of 25 Upper and lower Sharia Courts is ₦102.06 million. For the State Judiciary, which administers justice, the 2026 approved capital allocation is ₦3.39 billion, with recurrent allocations of ₦1.60 billion for personnel and ₦3.18 billion for overhead. All figures are approved allocations, not spending.

• Renovation of 25No Upper and lower Sharia Courts (Shari’a Court of Appeal), 2026 Approved Budget: ₦102.06 million
• State Judiciary (ministry total including its agencies, capital, code 031800000000) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦3.39 billion
• State Judiciary (ministry total including its agencies, personnel (salaries), code 031800000000) [Personnel Expenditure by Administrative Classification], 2026 Approved Budget: ₦1.60 billion
• State Judiciary (ministry total including its agencies, overhead (running costs), code 031800000000) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2026 Approved Budget: ₦3.18 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26, 63
_Reply *show working* to see the rows and arithmetic._
```

## m33: partial (lines:sum, 18.0s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
The budget shows ₦5.50 billion for Security Vote in 2025 and ₦8.21 billion for Security Vote in 2026, for a combined total of ₦13.71 billion (Kasafi's calculation). No line for contingency funds is shown.

• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604) [Expenditure by Economic Classification], 2025 Revised Budget: ₦5.50 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604) [Expenditure by Economic Classification], 2026 Approved Budget: ₦8.21 billion
• Not found: Contingency funds

📄 *Sources:* Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m34: not found (search, 14.6s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Ban sami amsar wannan tambayar a cikin takardun da nake da su ba.
```

## m35: answered (lines:list, 14.5s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
The Sokoto State Independent Electoral Commission (SIEC) has administrative code 014800100100 with a 2026 Approved Budget allocation of ₦460.48 million. The page number is shown in the line details below.

• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: partial (lines:list, 11.8s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Airways (sector total, capital, code 18), 2026 Approved Budget: ₦36.00 billion [1]
• Airways - General (programme inside a sector, capital, code 181001), 2026 Approved Budget: ₦36.00 billion [1]
• PURCHASE OF AEROPLANE (code 23010143), 2026 Approved Budget: ₦36.00 billion [2]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 47, 126
```

## m37: answered (search, 10.0s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
Jimillar kuɗin da aka ware wa ɓangaren Information Communication and Technology a kasafin 2025 (jimilla) ita ce ₦3.30 biliyan, kamar yadda shafi na 24 ya nuna. Jimillar kuɗin da aka ware wa ɓangaren a kasafin 2026 (jimilla) ita ce ₦7.15 biliyan, kamar yadda shafi na 41 ya nuna.

• 2025 approved budget (jimilla): ₦3.30 biliyan
• 2026 approved budget (jimilla): ₦7.15 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 41; Sokoto State Government 2025 Approved Budget, shafi 24
```

## m38: partial (lines:list, 13.0s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• WAMAKKO (capital, code 33312100, Capital Expenditure by Functional Classification), 2026 Approved Budget: ₦82.18 biliyan [1]
• WAMAKKO (code 33312100, Personnel Expenditure by Location), 2026 Approved Budget: ₦1.60 biliyan [2]
• WAMAKKO (code 33312100, Personnel Expenditure by Location), 2026 Approved Budget: ₦79.98 biliyan [2]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 38, 39
```

## m39: answered (search, 3.8s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
*Ministry of Environment* (code 053500000000):
• Capital: share of the revised budget spent 48.6% (Kasafi's calculation)
• Total: share of the revised budget spent 47.0% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18, 28
```
