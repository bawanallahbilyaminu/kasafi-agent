# Open-question run: mid_tier.json

39 questions: answered 18, partial 18, not found 2, unverified 1 | wrong 1 of 11 checked (m04) | median 14.5s

```
plan          n=39 median   3.8s    26% of all time
line_search   n=34 median   1.8s    11% of all time
read          n=33 median   6.6s    39% of all time
read1         n=33 median   3.7s    24% of all time
read2         n=33 median   4.3s    27% of all time
reread        n= 6 median   5.2s     6% of all time
page_search   n=35 median   1.6s    10% of all time
compose       n=28 median   6.1s    31% of all time
answer        n=38 median   6.7s    50% of all time
row readings: 80 model calls for 33 questions (2 = no retry)
```

## m01: answered (lines:list, 10.6s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
Eh, akwai kudin tallafin karatu a kasafin 2026. An ware ₦1.50 biliyan ga FOREIGN SCHOLARSHIP SCHEME da ₦1.60 biliyan ga Domestic Scholarship. Wadannan kudade da aka ware ne (approved budget).

• FOREIGN SCHOLARSHIP SCHEME (code 22021020), 2026 Approved Budget: ₦1.50 biliyan
• Domestic Scholarship (code 22021025), 2026 Approved Budget: ₦1.60 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m02: partial (lines:list, 20.3s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
For SUBEB classroom work, construction/provision of public schools was allocated ₦4.55 billion in the 2025 approved budget. Rehabilitation/repairs of public schools shows ₦205.00 million as the 2025 revised budget and ₦205.00 million in the 2026 approved budget. The 2026 construction/provision figure for SUBEB is not shown separately in these lines.

• (SUBEB) – construction / provision of public schools, 2025 Approved Budget: ₦4.55 billion
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million
• Not found: 2026 approved allocation for SUBEB construction/provision of public schools; 2025 approved allocation for SUBEB rehabilitation/repairs of public schools

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 29; Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: partial (lines:list, 16.2s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
The 2026 approved budget includes girl-child lines: Female Education Board total  and Girls secondary schools equipment, plus a zero-funded Girls Education Project monitoring line. For feeding it includes Meal Subsidy to Government Schools and the School feeding programme. For retention it includes the Increase in access, retention, and completion rate objective. All figures are approved allocations, not spending.

• Girls secondary schools (Female Education Board) – purchase of industrial equipment, 2026 Approved Budget: ₦45.00 million
• Girls Education Project (11) with State to State (Ministry for Basic Education), 2026 Approved Budget: 0.00
• MEAL SUBSIDY TO GOVERNMENT SCHOOLS (code 22050102), 2026 Approved Budget: ₦2.00 billion
• School feeding (programme inside a sector, all spending (total), code 050203), 2026 Approved Budget: ₦2.03 billion
• Increase in access, retention, and completion rate at all levels (objective inside a sector, all spending (total), code 0502), 2026 Approved Budget: ₦11.26 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): Female Education Board (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40, 41, 65, 67, 149
_Reply *show working* to see the rows and arithmetic._
```

## m04: partial WRONG: none of [['15.8']] (lines:share, 25.4s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
The budget prints two totals for this, in different tables; the share of each:
• Health (sector total, all spending (total), code 04) [Total Expenditure by Programme (Sector, Objective and Programme)]: 1648.0% (Kasafi's calculation)
• HEALTH (all spending (total), code 707) [Total Expenditure by Functional Classification]: 1666.1% (Kasafi's calculation)

• Health (sector total, all spending (total), code 04), 2026 Approved Budget: ₦118.83 billion ↑
• HEALTH (all spending (total), code 707), 2026 Approved Budget: ₦120.13 billion ↑
• Total Expenditure, 2026 Approved Budget: ₦7.21 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 32, 40, 79
_Reply *show working* to see the rows and arithmetic._
```

## m05: answered (category, 6.2s)

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

## m06: partial (lines:list, 12.7s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
The 2026 approved budget shows ₦100.00 million for provision of support for PHC-MOU activities under the Primary Health Care Development Agency. No separate counterpart line for routine immunization is shown in the documents provided.

• Provision of support for PHC-MOU activities (Primary Health Care Development Agency), 2026 Approved Budget: ₦100.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): 04050124000403 - Functional health facilities BHCF Counterpart Funds for SOCHEMA (2026 Approved Budget); 04050126007201 - Functional health facilities Basic Health Care Provision Funds (BHCF) 25% Counterpart (2026 Approved Budget); Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 70
_Reply *show working* to see the rows and arithmetic._
```

## m07: partial (lines:list, 16.7s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• CONSTRUCTION / PROVISION OF HOSPITALS / HEALTH CENTRES (code 23020106), 2026 Performance Year to Date (Q1-Q2): ₦80.00 million [1]
• REHABILITATION / REPAIRS - HOSPITAL / HEALTH CENTRES (code 23030105), 2026 Performance Year to Date (Q1-Q2): ₦41.81 million [1]
• Primary Health Care Development Agency (one agency or unit, all spending (total), code 052100300100), 2026 Performance Year to Date (Q1-Q2): ₦1.22 billion [2]

📄 *Sources:* Budget Implementation Report Q2 2026, p. 52, 53
```

## m08: answered (category, 8.2s)

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

## m09: partial (lines:list, 22.2s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
The budgets show irrigation schemes and tube wells as capital project line-items, but no line-item named solar-powered tube wells. Tube wells construction was allocated ₦531.96 million in 2025 (Revised) and 0.00 in 2026 (Approved). Kware irrigation scheme was allocated ₦200.00 million in 2025 and ₦800.00 million in 2026. Irrigation Scheme Youth empowerment (NEMI NA KANKA) was allocated ₦200.00 million in 2025 and ₦200.00 million in 2026. All figures are budgeted allocations, not spending.

• Construction of Tube Wells across the State (Nigeria CARES- Fadama Programme) [Capital Expenditure by Project], 2025 Revised Budget: ₦531.96 million
• Construction of Tube Wells across the State (Nigeria CARES- Fadama Programme) [Capital Expenditure by Project], 2026 Approved Budget: 0.00
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦800.00 million
• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• … +1
• Not found: solar-powered tube wells – no specific line-item with that name is shown

📄 *Sources:* Sokoto State FY 2026 Budget, p. 53
_Reply *show working* to see the rows and arithmetic._
```

## m10: answered (lines:list, 17.0s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
I, an ware kudade don gyaran madatsun ruwa da ruwan famfo a kasafin 2026. An ware ₦25.00 biliyan don gyaran aikin ruwan birnin Sokoto (Sokoto Township Water Works), da ₦35.00 miliyan don gyaran manyan tankunan ruwa a cikin birnin Sokoto. Haka kuma an ware ₦54.56 miliyan don gyara da fadada madatsun ruwa na Rafin Duma. Wadannan kudaden da aka ware ne (approved), ba kashewa ba.

• Rehabilitation and expansion of earth dams at Rafin Duma (Ministry of Water Resources), 2026 Approved Budget: ₦54.56 miliyan
• Rehabilitation of Sokoto Township Water Works (Water Board), 2026 Approved Budget: ₦25.00 biliyan
• Rehabilitation of Overhead Tanks within Sokoto Metropolis (Water Board), 2026 Approved Budget: ₦35.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 58
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 10.9s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
The 2026 approved allocation for animal health and livestock diseases management is ₦12.93 billion and for livestock feeds development (grazing reserves) is ₦368.05 million, for a combined total of ₦13.30 billion (Kasafi's calculation). These are approved budget allocations.

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Livestock feeds development (programme inside a sector, all spending (total), code 010206), 2026 Approved Budget: ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40
_Reply *show working* to see the rows and arithmetic._
```

## m12: partial (lines:list, 15.3s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
No line in the documents is exactly that (flyovers, inner-city dualization, rural feeder roads). The nearest lines they print (related, not the item itself):
• Ministry of Works (ministry total including its agencies, capital, code 023400000000), 2026 Approved Budget: ₦58.13 billion [1]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 26
```

## m13: not found (search, 11.8s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m14: answered (lines:sum, 11.6s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
An ware ₦6.43 biliyan (lissafin Kasafi) a kasafin 2026 don gina sabbin gidaje, wanda ya haɗa da gidajen ma’aikata da manyan rukunin gidaje. Gida 500 a Gidan Salanke na da ₦4.00 biliyan, gida 500 a Wajekke na da ₦2.00 biliyan, gidajen Khadis 6 na da ₦51.00 miliyan, da kammala dakunan ma’aikata 53 na jami’a na da ₦382.98 miliyan. Dukkanin su kudaden da aka amince da su ne (approved), ba wanda aka kashe ba.

• Construction of 500 Housing units at Gidan Salanke (Min of Lands and Housing), 2026 Approved Budget: ₦4.00 biliyan
• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan
• Construction of 6 no Houses for 6 New Hon. Khadis in the State (Shari’a Court of Appeal), 2026 Approved Budget: ₦51.00 miliyan
• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 63, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: partial (lines:list, 15.3s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
E, akwai kudi a kasafin 2026 don sufurin jama'a ta SSTA. An ware ₦1.50 biliyan don sufuri tsakanin jihohi da cikin jiha (SSTA), da ₦2.40 biliyan don siyan bas 20 na Toyota 18-seater na SSTA. Kudin da aka ware ne (budgeted), ba wanda aka kashe ba.

• INTER AND INTRA STATE TRANSPORTATION (SSTA) (Ministry of Transport), 2026 Approved Budget: ₦1.50 biliyan
• PURCHASE OF 20 NO TOYOTA 18-SEATER BUSES for SSTA (Ministry of Transport), 2026 Approved Budget: ₦2.40 biliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): PURCHASE OF BUSES (2026 Approved Budget); Purchase of 300 Trycle bicycle for disable for ease transportation (Agency for Persons Living With Disabilities) (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 55
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m16: answered (search, 12.5s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
The State Government projected ₦47.94 billion as independent revenue in the 2025 final budget. It collected ₦20.58 billion in Q1–Q4 2025 (42.9% of the final budget). The 2026 approved budget targets ₦74.52 billion for independent revenue.

📄 *Sources:* Budget Implementation Report Q4 2025, p. 9; Sokoto State FY 2026 Budget, p. 11
```

## m17: answered (lines:ratio, 12.2s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
The 2026 approved budget provides ₦553.34 billion for Capital Expenditure and ₦205.36 billion for Recurrent Expenditure. The ratio of Capital to Recurrent is 2.69 : 1 (Kasafi's calculation).

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (lines:list, 10.5s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
Sokoto State earmarked ₦10.03 billion for domestic principal plus ₦6.00 billion for domestic interest, versus ₦2.42 billion for foreign principal plus ₦1.31 billion for foreign interest in the 2026 approved budget. All figures are approved allocations, not actual spending.

• DOMESTIC PRINCIPAl (code 220604), 2026 Approved Budget: ₦10.03 billion
• DOMESTIC INTEREST / DISCOUNT (code 220602), 2026 Approved Budget: ₦6.00 billion
• FOREIGN PRINCIPAL (code 220603), 2026 Approved Budget: ₦2.42 billion
• FOREIGN INTEREST / DISCOUNT (code 220601), 2026 Approved Budget: ₦1.31 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29
_Reply *show working* to see the rows and arithmetic._
```

## m19: answered (lines:compare, 14.0s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
• Difference (2026 Approved Budget vs 2025 Approved Budget): -₦489.02 million (-11.6%) (Kasafi's calculation)

• Government House (one agency or unit, overhead (running costs), code 011100100100), 2025 Approved Budget: ₦4.20 billion
• Government House (one agency or unit, overhead (running costs), code 011100100100), 2026 Approved Budget: ₦3.71 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 14; Sokoto State FY 2026 Budget, p. 21
_Reply *show working* to see the rows and arithmetic._
```

## m20: answered (search, 15.6s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa ƙarshen Q1 na 2026, an kashe 3.0% na kasafin manyan ayyuka na daukacin jihar. Kasafin da aka amince da shi (jimilla) ₦553.34 biliyan ne, kuma an kashe ₦16.82 biliyan a Q1 2026 kaɗai.

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 5, 9, 27
```

## m21: unverified (search, 14.5s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
I found documents about your question, but couldn't verify the figures. Please check these sources:

[1] Budget Implementation Report Q2 2026, page 27
[2] Budget Implementation Report Q2 2026, page 28
[3] Budget Implementation Report Q2 2026, page 26
```

## m22: answered (search, 15.7s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
The Ministry of Health had released 10.6% of its 2026 revised budget by the end of Q2 2026 (Q1–Q2 only). This is confirmed in the Budget Implementation Report Q2 2026 on page 18.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## m23: answered (search, 11.1s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
_Assumption: used Q2 2026 as first half (January-June) year-to-date._

2026 budgeted personnel expenditure was ₦70.57 billion. Actual payroll outturn for Q1–Q2 2026 only was ₦37.30 billion (52.8% of the revised budget). This leaves a balance (variance) of ₦33.28 billion against the revised budget.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19
```

## m24: partial (lines:list, 14.9s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• Youth - General (programme inside a sector, overhead (running costs), code 081001), 2026 Approved Budget: ₦1.46 biliyan [1]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 44
```

## m25: partial (lines:list, 26.7s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
No separate dedicated project lines for assistive devices, special schools or specific welfare support for persons with disabilities are printed in the 2026 budget documents provided. What is printed is the aggregated DISABILITY function total and its breakdowns for capital, overhead and personnel, which is the level where spending for persons with disabilities is shown without further detail.

• DISABILITY (all spending (total), code 71012) [Total Expenditure by Functional Classification], 2026 Approved Budget: ₦3.07 billion
• DISABILITY (capital, code 71012) [Capital Expenditure by Functional Classification], 2026 Approved Budget: ₦1.24 billion
• DISABILITY (overhead (running costs), code 71012) [Other Non-Debt Recurrent Expenditure by Functional Classification], 2026 Approved Budget: ₦1.00 billion
• DISABILITY (personnel (salaries), code 71012) [Personnel Expenditure by Functional Classification], 2026 Approved Budget: ₦827.90 million
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Not found: specific dedicated lines for assistive devices, special schools, and welfare support for persons with disabilities

📄 *Sources:* Sokoto State FY 2026 Budget, p. 33, 34, 36, 38
_Reply *show working* to see the rows and arithmetic._
```

## m26: partial (lines:list, 14.8s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
Shown women empowerment provisions are ₦400.00 million for 2025 and ₦350.00 million approved for 2026, plus ₦250.00 million for 2025. No separate lines for orphanages and destitute homes are shown.

• tabs for Youth and Women Empowerment (POVERTY REDUCTION PROGRAMME) [Capital Expenditure by Project], 2025 Revised Budget: ₦400.00 million
• tabs for Youth and Women Empowerment (POVERTY REDUCTION PROGRAMME) [Capital Expenditure by Project], 2026 Approved Budget: ₦350.00 million
• exercises for self reliance. (Ministry for Women Affairs), 2025 Revised Budget: ₦250.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): exercises for self reliance. (Ministry for Women Affairs) (2026 Approved Budget); Ministry for Women Affairs (2025 Approved Budget); Ministry for Women Affairs (2026 Approved Budget); Ministry of Humanitarian Affairs & Social Welfare (2025 Approved Budget); Ministry of Social Welfare & Community Development (2026 Original Budget); Procurement of delivery kits for pregnant Women across the 23 LGAs. (Ministry for Women Affairs) (2025 Revised Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 49, 64
_Reply *show working* to see the rows and arithmetic._
```

## m27: partial (lines:sum, 14.0s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
Takardun kasafin da aka bayar ba su nuna warewa na musamman ga kananan hukumomin kan iyaka ba. Abin da aka nuna shi ne jimillar sashen: ₦44.37 biliyan aka ware wa Water Resources and Rural Development a kasafin 2026 da aka amince da shi da ₦6.10 biliyan aka ware wa sashen Poverty Alleviation, jimillarsu ₦50.47 biliyan (lissafin Kasafi). Dukansu kudaden da aka ware (budgeted) ne, ba kudaden da aka kashe ba, kuma ba a raba su ta kananan hukumomi ba.

• Water Resources and Rural Development (jimillar ɓangare, duk kashe kuɗi (jimilla), code 10), 2026 Approved Budget: ₦44.37 biliyan
• Poverty Alleviation (jimillar ɓangare, duk kashe kuɗi (jimilla), code 03), 2026 Approved Budget: ₦6.10 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 40, 41
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m28: partial (lines:list, 12.4s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Total Personnel Expenditure (personnel (salaries)), 2026 Original Budget: ₦70.57 billion [1]
• PERSONNEL COST (capital, code 21), 2026 Approved Budget: ₦70.57 billion [2]

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19; Sokoto State FY 2026 Budget, p. 27
```

## m29: partial (lines:list, 18.3s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
Gwamnati ta ware ₦9.12 biliyan a kasafin 2025 da aka amince da ₦5.00 biliyan a kasafin 2026 da aka amince don biyan gratuity ga tsofaffin ma’aikata. Wadannan kudaden da aka ware ne (budgeted), ba abin da aka kashe ba.

• GRATUITY (code 21030101), 2025 Original Budget: ₦9.12 biliyan
• GRATUITY (code 21030101), 2026 Original Budget: ₦5.00 biliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): GRATUITY (2025 Final Budget); Gratuity (2025 Revised Budget)

📄 *Madogara:* Budget Implementation Report Q4 2025, shafi 32; Budget Implementation Report Q2 2026, shafi 30
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 10.0s)

**Q:** How much was budgeted for staff training, civil service computerization, and promotion arrears in the 2026 budget?

```
Statewide, the 2026 approved budget has LOCAL TRAINING (22020501) ₦6.80 billion; INTERNATIONAL TRAINING (22020502) ₦1.82 billion; PURCHASE OF COMPUTERS (23010113) ₦3.08 billion; PURCHASE OF COMPUTER PRINTERS (23010114) ₦240.00 million; COMPUTER SOFTWARE ACQUISITION (23050102) ₦1.41 billion, ₦13.36 billion together (Kasafi's calculation). By the end of June 2026, ₦704.75 million of it had been spent statewide (5.3%, Budget Implementation Report Q2 2026).

Largest:
• Ministry of Innovation and Digital Economy: ₦2.41 billion
• Department for Security Matters: ₦1.80 billion
• State Universal Basic Education Board (SUBEB): ₦1.14 billion
• Fertilizer and Agricultral Supplies Company: ₦684.35 million
• Office of Head of Service: ₦663.00 million

✓ The agencies' rows add up exactly to the printed statewide totals.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 28, 29, 31, 84, 97, 104, 112, 113, 120, 127, 134, 140, 149, 150, 158, 161, 162; Budget Implementation Report Q2 2026, p. 31, 32, 34
_Reply *show working* to see the rows and arithmetic._
```

## m31: partial (search, 14.4s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
The budget does not show a line labelled Sokoto State Community Guard Corps separately. The line named SECURITY VOTE (INCLUDING OPERATIONS) is ₦8.21 billion in the 2026 approved budget (overhead). A line named SECURITY SERVICES is ₦10.00 million in the 2026 approved budget (capital).

• 2026 approved budget (overhead) SECURITY VOTE (INCLUDING OPERATIONS): ₦8.21 billion
• 2026 approved budget (capital) SECURITY SERVICES: ₦10.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 28, 83
```

## m32: answered (lines:list, 13.1s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
The State Judiciary's 2026 approved capital allocation is ₦3.39 billion, with recurrent personnel of ₦1.60 billion and overhead of ₦3.18 billion. The specific renovation of 25 Upper and lower Sharia Courts is allocated ₦102.06 million for 2026. All figures are approved allocations, not spent amounts.

• State Judiciary (ministry total including its agencies, capital, code 031800000000) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦3.39 billion
• State Judiciary (ministry total including its agencies, personnel (salaries), code 031800000000) [Personnel Expenditure by Administrative Classification], 2026 Approved Budget: ₦1.60 billion
• State Judiciary (ministry total including its agencies, overhead (running costs), code 031800000000) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2026 Approved Budget: ₦3.18 billion
• Renovation of 25No Upper and lower Sharia Courts (Shari’a Court of Appeal), 2026 Approved Budget: ₦102.06 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26, 63
_Reply *show working* to see the rows and arithmetic._
```

## m33: partial (lines:sum, 16.0s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
The approved allocation for Security Vote (including operations) was ₦5.50 billion in 2025 and ₦8.21 billion in 2026, for a combined ₦13.71 billion (Kasafi's calculation). No line for contingency funds is shown, so it is not included.

• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2025 Original Budget: ₦5.50 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion
• Not found: contingency funds

📄 *Sources:* Budget Implementation Report Q4 2025, p. 33; Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m34: not found (search, 15.6s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Ban sami amsar wannan tambayar a cikin takardun da nake da su ba.
```

## m35: answered (lines:list, 12.8s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
The Sokoto State Independent Electoral Commission has a 2026 approved budget allocation of ₦460.48 million (allocated/budgeted).

• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: partial (lines:list, 22.1s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Airways (sector total, capital, code 18), 2026 Approved Budget: ₦36.00 billion [1]
• Airways - General (programme inside a sector, capital, code 181001), 2026 Approved Budget: ₦36.00 billion [1]
• PURCHASE OF AEROPLANE (code 23010143), 2026 Approved Budget: ₦36.00 billion [2]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 47, 126
```

## m37: answered (search, 24.4s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
Jimillar da aka ware wa bangaren Information Communication and Technology a kasafin 2025 da aka amince da shi ita ce ₦3.30 biliyan, daga teburin Total Expenditure by Programme a shafi 24. Jimillar da aka ware wa bangaren a kasafin 2026 da aka amince da shi ita ce ₦7.15 biliyan, daga tebur iri daya a shafi 41. Dukkan su kudaden da aka ware ne, ba kudaden da aka kashe ba.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 24; Sokoto State FY 2026 Budget, shafi 41
```

## m38: partial (lines:list, 15.4s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• WAMAKKO (capital, code 33312100, Capital Expenditure by Functional Classification), 2026 Approved Budget: ₦82.18 biliyan [1]
• Ministry for Local Government and Chieftancy23030121 - REHABILITATION / REPAIRS OF OFFICE BUILDINGS 70621 - COMMUNITY DEVELOPMENT (code 055100100100), 2026 Approved Budget: ₦124.94 miliyan [2]
• WAMAKKO (code 33312100, Personnel Expenditure by Location), 2026 Approved Budget: ₦79.98 biliyan [3]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 38, 39, 73
```

## m39: answered (search, 4.9s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
*Ministry of Environment* (code 053500000000):
• Capital: share of the revised budget spent 48.6% (Kasafi's calculation); approved budget ₦18.77 billion; revised budget ₦16.17 billion; spent so far (Q1–Q2) ₦7.86 billion; spent in Q2 ₦7.84 billion
• Total: share of the revised budget spent 47.0% (Kasafi's calculation); approved budget ₦20.77 billion; revised budget ₦18.17 billion; spent so far (Q1–Q2) ₦8.53 billion; spent in Q2 ₦8.21 billion

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18, 28; Sokoto State FY 2026 Budget, p. 18, 27
```
