# Open-question run: mid_tier.json

39 questions: answered 22, partial 13, not found 2, unverified 1, clarify 1 | wrong 1 of 11 checked (m37) | median 11.6s

```
plan          n=39 median   4.1s    35% of all time
line_search   n=32 median   1.0s     8% of all time
read          n=30 median   5.8s    41% of all time
read1         n=30 median   4.2s    30% of all time
read2         n=30 median   3.7s    26% of all time
reread        n= 4 median   4.3s     3% of all time
page_search   n=33 median   1.0s     8% of all time
compose       n=31 median   3.2s    22% of all time
answer        n=37 median   5.7s    49% of all time
row readings: 72 model calls for 30 questions (2 = no retry)
```

## m01: answered (search, 10.8s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
Eh, akwai kuɗin tallafin karatu a kasafin 2026. Gwamnatin Jiha ta ware ₦1.60 biliyan a matsayin Domestic Scholarship a kasafin 2026 da aka amince da shi.

• 2026 kasafin da aka amince da shi (jimilla) - Domestic Scholarship: ₦1.60 biliyan
• 2026 Q1 an kashe (Janairu-Maris 2026 kaɗai): ₦1.70 miliyan (0.1% na kasafin asali)
• 2026 Q1-Q2 an kashe (Janairu-Yuni 2026 kaɗai): ₦494.70 miliyan (30.9% na kasafin da aka sabunta)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29, 160; Budget Implementation Report Q2 2026, shafi 31; Sokoto State Budget Implementation Report Q1 2026, shafi 32
```

## m02: partial (lines:compare, 16.3s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
For SUBEB rehabilitation/repairs of public schools, the 2025 revised figure was ₦205.00 million and the 2026 approved allocation was ₦205.00 million. No separate SUBEB line for construction of primary school classrooms is shown, so the construction part cannot be answered.

• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million
• Not found: construction of primary school classrooms by SUBEB

📄 *Sources:* Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: answered (lines:list, 10.2s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
The 2026 approved budget shows a Girls Education Project line with Monitoring and Evaluation at 0.00, a School feeding programme at ₦2.03 billion including Meal Subsidy to Government Schools at ₦2.00 billion, and an Increase in access, retention, and completion rate objective at ₦11.26 billion. These are allocated (budgeted) amounts, not spent amounts.

• Girls Education Project (11) with State to State (Ministry for Basic Education), 2026 Approved Budget: 0.00
• School feeding (programme inside a sector, all spending (total), code 050203), 2026 Approved Budget: ₦2.03 billion
• MEAL SUBSIDY TO GOVERNMENT SCHOOLS (code 22050102), 2026 Approved Budget: ₦2.00 billion
• Increase in access, retention, and completion rate at all levels (objective inside a sector, all spending (total), code 0502), 2026 Approved Budget: ₦11.26 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40, 41, 65, 149
_Reply *show working* to see the rows and arithmetic._
```

## m04: answered (lines:share, 16.0s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
15.8% (Kasafi's calculation) of the 2026 approved budget's Total Expenditure is allocated to the health sector. Figures used are allocated (budgeted), not spent.

• HEALTH (all spending (total), code 707), 2026 Original Budget: ₦120.13 billion ↑
• Total Expenditure (all spending (total)), 2026 Original Budget: ₦758.70 billion ↓

📄 *Sources:* Budget Implementation Report Q2 2026, p. 15, 36
_Reply *show working* to see the rows and arithmetic._
```

## m05: answered (category, 6.9s)

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

## m06: partial (lines:list, 13.4s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
The 2026 approved counterpart allocation for PHC-MOU activities, which covers routine immunization and primary healthcare support, is ₦100.00 million. This is the budgeted allocation, not spending.

• Provision of support for PHC-MOU activities (Primary Health Care Development Agency), 2026 Approved Budget: ₦100.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health) (2026 Approved Budget); 04050124000403 - Functional health facilities BHCF Counterpart Funds for SOCHEMA (2026 Approved Budget); 04050126007201 - Functional health facilities Basic Health Care Provision Funds (BHCF) 25% Counterpart (2026 Approved Budget); 04050124008401 - Functional health facilities Support for Family Planning Programme (Counterpart) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 70
_Reply *show working* to see the rows and arithmetic._
```

## m07: partial (lines:list, 13.8s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• CAPITAL EXPENDITURE (code 23, Primary Healthcare Expenditure by Economic Classification), 2026 Performance Year to Date (Q1-Q2): ₦729.23 million [1]
• CAPITAL EXPENDITURE (code 23, Primary Healthcare Expenditure by Economic Classification), 2026 Performance Year to Date (Q1): ₦607.41 million [2]
• 04050100000001 Primary Health Care (capital), 2026 Approved Budget: ₦5.89 billion [3]

📄 *Sources:* Budget Implementation Report Q2 2026, p. 53; Sokoto State Budget Implementation Report Q1 2026, p. 55; Sokoto State FY 2026 Budget, p. 48
```

## m08: answered (category, 8.1s)

**Q:** Nawa gwamnatin jihar Sokoto ta ware don sayen takin zamani da tallafin kayan noma a shekarar 2026, kuma nawa aka riga aka kashe?

```
_Na yi amfani da rahoton aiwatar da kasafin Q2 2026 mafi sabo don kashe kudi._

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

## m09: partial (lines:list, 12.7s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
The budgets show separate capital line-items for irrigation schemes and for tube wells / solar-powered boreholes, not one combined dry-season item. Kware irrigation scheme (SPIN Project) was ₦200.00 million revised in 2025 rising to ₦800.00 million approved in 2026, while Irrigation Scheme Youth empowerment (NEMI NA KANKA) was ₦200.00 million in both 2025 revised and 2026 approved. Construction of Tube Wells across the State was ₦531.96 million revised in 2025 and 0.00 approved in 2026, and solar powered boreholes were 0.00 revised in 2025 and ₦2.20 billion approved in 2026. All figures are budgeted allocations, not spent amounts.

• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦800.00 million
• Construction of Tube Wells across the State (Nigeria CARES- Fadama Programme) [Capital Expenditure by Project], 2025 Revised Budget: ₦531.96 million
• … +3

📄 *Sources:* Sokoto State FY 2026 Budget, p. 53, 59
_Reply *show working* to see the rows and arithmetic._
```

## m10: partial (lines:list, 18.5s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
A cikin kasafin 2026 ba a nuna layi na musamman don gyaran madatsun ruwa a Sokoto ba. Sai dai akwai kudaden da aka ware don ruwan sha a cikin birnin Sokoto: ₦25.00 biliyan don gyaran Ayyukan Ruwa na Garin Sokoto (Sokoto Township Water Works) da kuma ₦35.00 miliyan don gyaran manyan tankunan ruwa a cikin birnin Sokoto (Sokoto Metropolis), dukkansu kudadene da aka amince da su a kasafin 2026.

• Rehabilitation of Sokoto Township Water Works (Water Board), 2026 Approved Budget: ₦25.00 biliyan
• Rehabilitation of Overhead Tanks within Sokoto Metropolis (Water Board), 2026 Approved Budget: ₦35.00 miliyan
• Ba a samu ba: gyaran madatsun ruwa, ruwan famfo (borehole) na musamman a cikin birnin Sokoto

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 58
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 9.6s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
The 2026 approved allocation for animal health and livestock diseases management is ₦12.93 billion and for livestock feeds development (including grazing reserves) is ₦368.05 million. Together this is ₦13.30 billion (Kasafi's calculation) in approved 2026 allocations.

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Livestock feeds development (programme inside a sector, all spending (total), code 010206), 2026 Approved Budget: ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40
_Reply *show working* to see the rows and arithmetic._
```

## m12: partial (lines:list, 10.2s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Ministry of Works (ministry total including its agencies, capital, code 023400000000), 2026 Approved Budget: ₦58.13 billion [1]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 26
```

## m13: not found (search, 13.9s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m14: answered (lines:sum, 10.7s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
An ware jimillar ₦6.38 biliyan (lissafin Kasafi) a kasafin 2026 domin gina sabbin gidaje da kammala na ma'aikata. Wannan ya hada da ₦4.00 biliyan na gina rukunin gidaje 500 a Gidan Salanke, da ₦2.00 biliyan na gina rukunin gidaje 500 a Wajekke, Wamakko, da ₦382.98 miliyan na kammala gidan ma'aikata 53 a Jami'ar Jihar Sokoto. Dukkaninsu kudaden da aka amince da su ne a 2026, ba kashewa ba.

• Construction of 500 Housing units at Gidan Salanke (Min of Lands and Housing), 2026 Approved Budget: ₦4.00 biliyan
• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan
• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: answered (category, 9.0s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
_Na yi amfani da kasafin 2026 da aka amince da shi._

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

## m16: answered (search, 9.4s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
The 2025 projected Internally Generated Revenue (IGR) was ₦47.44 billion in the original approved budget and ₦47.94 billion in the final budget. Actual collections for the full year (Q1–Q4 2025) were ₦20.58 billion, which was 42.9% of the final budget. The target set for 2026 is ₦74.52 billion.

• 2025 original approved budget (total): ₦47.44 billion
• 2025 final budget (total): ₦47.94 billion
• 2025 actual collections Q1–Q4 (total, 42.9% of final budget): ₦20.58 billion
• 2026 approved budget target (total): ₦74.52 billion

📄 *Sources:* Budget Implementation Report Q4 2025, p. 9, 13; Sokoto State FY 2026 Budget, p. 1, 11; Sokoto State Government 2025 Approved Budget, p. 1
```

## m17: answered (lines:ratio, 8.2s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
The approved 2026 budget allocates ₦553.34 billion to Capital Expenditure and ₦205.36 billion to Recurrent Expenditure. The exact ratio of Capital to Recurrent is 2.69 : 1 (Kasafi's calculation).

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (lines:list, 11.6s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
For 2026, Sokoto State earmarked ₦10.03 billion for domestic principal plus ₦6.00 billion for domestic interest/discount, versus ₦2.42 billion for foreign principal plus ₦1.31 billion for foreign interest/discount. All figures are 2026 Approved Budget allocations.

• DOMESTIC PRINCIPAl (code 220604), 2026 Approved Budget: ₦10.03 billion
• DOMESTIC INTEREST / DISCOUNT (code 220602), 2026 Approved Budget: ₦6.00 billion
• FOREIGN PRINCIPAL (code 220603), 2026 Approved Budget: ₦2.42 billion
• FOREIGN INTEREST / DISCOUNT (code 220601), 2026 Approved Budget: ₦1.31 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29
_Reply *show working* to see the rows and arithmetic._
```

## m19: answered (lines:compare, 15.3s)

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
Zuwa ƙarshen Q1 na 2026, an kashe 3.0% na kasafin babban aiki na jihar. Jimillar kasafin babban aiki da aka amince da shi na 2026 ita ce ₦553.34 biliyan, kuma abin da aka kashe a Q1 shi ne ₦16.82 biliyan. Wannan adadi na Q1 shi ne na watan Janairu zuwa Maris 2026 kaɗai.

• 2026 kasafin babban aiki da aka amince da shi (jimilla): ₦553.34 biliyan
• Q1 2026 da aka kashe na babban aiki (Janairu–Maris 2026 kaɗai): ₦16.82 biliyan

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 5, 27, 33, 43, 50
```

## m21: unverified (search, 11.9s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
I found documents about your question, but couldn't verify the figures. Please check these sources:

[1] Budget Implementation Report Q2 2026, page 27
[2] Budget Implementation Report Q2 2026, page 28
[3] Budget Implementation Report Q2 2026, page 26
```

## m22: answered (search, 3.9s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
*Ministry of Health* (code 052100000000):
• Total: share of the revised budget spent 10.6% (Kasafi's calculation); approved budget ₦124.41 billion; spent so far (Q1–Q2) ₦12.36 billion

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18; Sokoto State FY 2026 Budget, p. 18
```

## m23: answered (search, 10.2s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
Budgeted personnel expenditure for 2026 was ₦70.57 billion. Actual payroll outturn through the first half of 2026 (Q1–Q2) was ₦37.30 billion (52.8% of the revised budget). The remaining variance/balance against the budget was ₦33.28 billion.

• 2026 approved budget (personnel): ₦70.57 billion
• Q1–Q2 2026 actual outturn (personnel): ₦37.30 billion (52.8% of the revised budget)
• Variance / balance against revised budget: ₦33.28 billion

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19, 30, 38, 47
```

## m24: partial (lines:list, 11.0s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Ba a nuna layi daban don horar da matasa sana'o'i da tallafin kudi a cikin Ma'aikatar Matasa da Wasanni a kasafin 2026 ba. Jimillar kasafin da aka ware wa Ma'aikatar Matasa da Wasanni gaba ɗaya (ciki har da hukumominta) a 2026 ita ce ₦17.06 biliyan (kasafin da aka amince da shi), wanda ya ƙunshi dukkan ayyukan ma'aikatar.

• Ministry of Youth and Sports Development (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 051300000000), 2026 Approved Budget: ₦17.06 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.
• Ba a samu ba: horar da matasa sana'o'i da tallafin kudi - babu layi daban da ke nuna wannan aikin a takardun da aka bayar

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m25: answered (lines:list, 14.7s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
Yes, the 2026 approved budget shows dedicated lines: ₦3.07 billion for Disability, including ₦500.00 million for Raji Special School and ₦50.00 million for Therapeutic Appliances and Equipment. All figures are allocated (budgeted), not spent.

• Raji Special School (Ministry for Basic Education), 2026 Approved Budget: ₦500.00 million
• THERAPEUTIC APPLIANCES AND EQUIPTMENT (code 70713), 2026 Approved Budget: ₦50.00 million
• DISABILITY (all spending (total), code 71012), 2026 Approved Budget: ₦3.07 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 33, 65, 188
_Reply *show working* to see the rows and arithmetic._
```

## m26: clarify (search, 13.1s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
I can read your question two ways. Which do you mean?
```

## m27: partial (lines:list, 10.2s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• Poverty Alleviation (sector total, all spending (total), code 03), 2026 Approved Budget: ₦6.10 biliyan [1]
• Water Resources and Rural Development (sector total, all spending (total), code 10), 2026 Approved Budget: ₦44.37 biliyan [2]
• Integrated rural development (agricultural land development, farm mechanization, & rural infrastructures (programme inside a sector, all spending (total), code 010701), 2026 Approved Budget: 0.00 [1]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 40, 41
```

## m28: partial (search, 10.7s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
The 2026 approved personnel budget is personnel ₦70.57 billion. The evidence does not state whether this incorporates the full financial implementation of the national minimum wage across all MDAs.

• 2026 approved budget (personnel): ₦70.57 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 27
```

## m29: answered (lines:compare, 16.5s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
Gwamnati ta ware ₦9.12 biliyan a kasafin 2025 da aka amince da ₦5.00 biliyan a kasafin 2026 da aka amince don biyan gratuity ga tsofaffin ma’aikata.

• GRATUITY (manyan ayyuka, code 21030101), 2025 Approved Budget: ₦9.12 biliyan
• Gratuity (shiri cikin ɓangare, duk kashe kuɗi (jimilla), code 230502), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 42
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 12.9s)

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

## m31: partial (lines:list, 9.8s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• SECURITY SERVICES (code 22020601), 2026 Approved Budget: ₦8.62 billion [1]
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion [1]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 28
```

## m32: answered (lines:list, 10.6s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
The 2026 approved capital allocation for renovation of 25 Upper and lower Sharia Courts is ₦102.06 million. For the State Judiciary (administration of justice), the 2026 approved capital allocation is ₦3.39 billion, personnel allocation is ₦1.60 billion, and overhead allocation is ₦3.18 billion. All figures are budgeted allocations, not spent amounts.

• Renovation of 25No Upper and lower Sharia Courts (Shari’a Court of Appeal), 2026 Approved Budget: ₦102.06 million
• State Judiciary (ministry total including its agencies, capital, code 031800000000) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦3.39 billion
• State Judiciary (ministry total including its agencies, personnel (salaries), code 031800000000) [Personnel Expenditure by Administrative Classification], 2026 Approved Budget: ₦1.60 billion
• State Judiciary (ministry total including its agencies, overhead (running costs), code 031800000000) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2026 Approved Budget: ₦3.18 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26, 63
_Reply *show working* to see the rows and arithmetic._
```

## m33: partial (lines:sum, 14.8s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
_Assumption: used approved budgets for 2025 and 2026 allocations._

The allocated security vote is ₦5.50 billion for 2025 and ₦8.21 billion for 2026. Together this is ₦13.71 billion (Kasafi's calculation) in approved allocations. No line for contingency funds is shown.

• SECURITY VOTE (INCLUDING OPERATIONS) (capital, code 22020604), 2025 Approved Budget: ₦5.50 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion
• Not found: contingency funds

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 17; Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m34: not found (search, 11.6s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Ban sami amsar wannan tambayar a cikin takardun da nake da su ba.
```

## m35: answered (lines:list, 12.7s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
The Sokoto State Independent Electoral Commission appears in the Sokoto State FY 2026 Budget as one agency or unit. Its 2026 Approved Budget allocation is ₦460.48 million. The exact administrative code and page number are those printed with that row below.

• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: partial (lines:list, 14.7s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Ministry of Works (one agency or unit, capital, code 023400100100, Capital Expenditure by Administrative Classification), 2026 Approved Budget: ₦42.26 billion [1]
• Construction of Water Supply at Old Airport (Water Board), 2026 Approved Budget: 0.00 [2]
• Ministry of Works (code 023400100100, Capital Expenditure by Project), 2026 Approved Budget: ₦3.00 billion [3]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 26, 55, 58
```

## m37: answered WRONG: none of [['3,301,437,040.18']] (lines:list, 20.5s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
Jimillar kasafin bangaren Information Communication and Technology a 2025 ita ce ₦1.49 biliyan. A 2026 kuma jimillar kasafin bangaren ta kasance ₦3.70 biliyan. Dukkanin adadin da aka ware ne (approved budget), ba kudin da aka kashe ba.

• Information Communication and Technology (jimillar ɓangare, manyan ayyuka, code 11), 2025 Approved Budget: ₦1.49 biliyan
• Information Communication and Technology (jimillar ɓangare, manyan ayyuka, code 11), 2026 Approved Budget: ₦3.70 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 26; Sokoto State FY 2026 Budget, shafi 46
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m38: partial (lines:list, 11.6s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• WAMAKKO (capital, code 33312100, Capital Expenditure by Functional Classification), 2026 Approved Budget: ₦82.18 biliyan [1]
• WAMAKKO (code 33312100, Personnel Expenditure by Location), 2026 Approved Budget: ₦1.60 biliyan [2]
• Ministry for Local Government and Chieftancy23030121 - REHABILITATION / REPAIRS OF OFFICE BUILDINGS 70621 - COMMUNITY DEVELOPMENT (code 055100100100), 2026 Approved Budget: ₦124.94 miliyan [3]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 38, 39, 73
```

## m39: answered (search, 4.2s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
*Ministry of Environment* (code 053500000000):
• Capital: share of the revised budget spent 48.6% (Kasafi's calculation)
• Total: share of the revised budget spent 47.0% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18, 28
```
