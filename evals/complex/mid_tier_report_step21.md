# Open-question run: mid_tier.json

39 questions: answered 23, partial 11, not found 5 | wrong 0 of 11 checked | median 17.3s

```
plan          n=39 median   4.3s    25% of all time
line_search   n=34 median   1.1s     6% of all time
read          n=34 median   9.0s    48% of all time
read1         n=34 median   7.6s    42% of all time
read2         n=34 median   4.1s    22% of all time
reread        n= 8 median   7.8s    10% of all time
page_search   n=35 median   1.1s     5% of all time
compose       n=35 median   8.5s    43% of all time
answer        n=39 median   8.6s    56% of all time
row readings: 78 model calls for 34 questions (2 = no retry)
```

## m01: answered (category, 10.0s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
_Ban ga wata shekara a tambayarka ba, don haka na yi amfani da kasafin 2026._

A kasafin 2026 da aka amince, a duk jihar: Domestic Scholarship (22021025) ₦1.60 biliyan; FOREIGN SCHOLARSHIP SCHEME (22021020) ₦1.50 biliyan, jimilla ₦3.10 biliyan (lissafin Kasafi). Zuwa ƙarshen Yuni 2026, an kashe ₦549.70 miliyan daga ciki a duk jihar (17.7%, Budget Implementation Report Q2 2026).

Mafi girma:
• Umaru Ali Shinkafi Polytechnic Sokoto: ₦3.10 biliyan

✓ Layukan hukumomi sun yi daidai da jimillar jihar da aka buga.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29, 160; Budget Implementation Report Q2 2026, shafi 31
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m02: partial (lines:list, 34.4s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
For construction, the 2025 approved budget shows ₦4.55 billion and ₦500.00 million for SUBEB CONSTRUCTION / PROVISION OF PUBLIC SCHOOLS. For renovation, SUBEB REHABILITATION / REPAIRS - PUBLIC SCHOOLS shows ₦205.00 million revised for 2025 and ₦205.00 million approved for 2026. No 2026 approved construction line for SUBEB is shown in these lines.

• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦4.55 billion
• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦500.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million
• Not found: 2026 approved allocation for SUBEB classroom construction (CONSTRUCTION / PROVISION OF PUBLIC SCHOOLS).

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 29; Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: answered (lines:list, 17.6s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
The 2026 approved budget shows a Girls Education Project line with 0.00 allocated, a School feeding programme with ₦2.03 billion allocated, a Meal Subsidy to Government Schools line with ₦2.00 billion allocated, and an Increase in access, retention, and completion rate objective with ₦11.26 billion allocated. All figures are budgeted allocations, not spent amounts.

• Girls Education Project (11) with State to State (Ministry for Basic Education), 2026 Approved Budget: 0.00
• School feeding (programme inside a sector, all spending (total), code 050203), 2026 Approved Budget: ₦2.03 billion
• MEAL SUBSIDY TO GOVERNMENT SCHOOLS (code 22050102), 2026 Approved Budget: ₦2.00 billion
• Increase in access, retention, and completion rate at all levels (objective inside a sector, all spending (total), code 0502), 2026 Approved Budget: ₦11.26 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40, 41, 65, 149
_Reply *show working* to see the rows and arithmetic._
```

## m04: answered (lines:share, 29.2s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
15.8% (Kasafi's calculation) of the 2026 approved budget's Total Expenditure goes to the health sector. The health sector allocation is ₦120.13 billion out of Total Expenditure of ₦758.70 billion, both 2026 Approved Budget figures.

• HEALTH (all spending (total), code 707), 2026 Approved Budget: ₦120.13 billion ↑
• Total Expenditure, 2026 Approved Budget: ₦758.70 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1, 32
_Reply *show working* to see the rows and arithmetic._
```

## m05: answered (category, 6.7s)

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

## m06: answered (lines:list, 12.9s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
The 2026 approved budget allocates ₦100.00 million as counterpart funding for Provision of support for PHC-MOU activities under the Primary Health Care Development Agency. This is the budgeted allocation, not actual spending.

• Provision of support for PHC-MOU activities (Primary Health Care Development Agency), 2026 Approved Budget: ₦100.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 70
_Reply *show working* to see the rows and arithmetic._
```

## m07: partial (search, 25.7s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
The evidence does not show maternal and child healthcare centers separately. A state facility located in an LGA is not an allocation to that LGA. Primary healthcare's total spent in Q1–Q2 2026 was ₦1.22 billion (16.9% of the revised budget).

📄 *Sources:* Budget Implementation Report Q2 2026, p. 52
```

## m08: answered (category, 8.3s)

**Q:** Nawa gwamnatin jihar Sokoto ta ware don sayen takin zamani da tallafin kayan noma a shekarar 2026, kuma nawa aka riga aka kashe?

```
A kasafin 2026 da aka amince, a duk jihar: PURCHASE OF AGRICULTURAL INPUTS (23010140) ₦5.65 biliyan. Ministry of Agriculture & Natural Resource da hukumominta: ₦4.64 biliyan, 82.1% na jimillar jihar (lissafin Kasafi). Zuwa ƙarshen Yuni 2026, an kashe ₦2.43 biliyan daga ciki a duk jihar (43.0%, Budget Implementation Report Q2 2026).

Mafi girma:
• Ministry of Agriculture & Natural Resource: ₦2.44 biliyan
• Nigeria CARES- Fadama Programme: ₦2.00 biliyan
• International Fund for Agriculture: ₦150.00 miliyan
• State Agricultural Development Project: ₦50.00 miliyan

✓ Layukan hukumomi sun yi daidai da jimillar jihar da aka buga.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 30, 108, 109, 110; Budget Implementation Report Q2 2026, shafi 32
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m09: partial (lines:list, 16.1s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
The 2026 approved budget shows specific capital lines for two irrigation schemes and for tube wells. Their 2025 revised and 2026 approved allocations are listed below, with 2025 shown as revised, not approved. No line in the data is labelled as solar-powered tube wells.

• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦800.00 million
• Construction of Tube Wells across the State (Nigeria CARES- Fadama Programme) [Capital Expenditure by Project], 2025 Revised Budget: ₦531.96 million
• … +1
• Possibly relevant too, not counted (I wasn't sure on a second reading): Intensive crop and vegetable production (irrigation, crop diversification etc.) (2025 Revised Budget); Intensive crop and vegetable production (irrigation, crop diversification etc.) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 53
_Reply *show working* to see the rows and arithmetic._
```

## m10: answered (lines:list, 18.4s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
I, an aka ware kudade don duka biyun a kasafin 2026. An ware ₦25.00 biliyan don gyaran ayyukan ruwan birnin Sokoto (Sokoto Township Water Works). An kuma ware ₦54.56 miliyan don gyara da fadaɗa madatsun ruwa na Rafin Duma. Dukkan kudaden da aka ware su ne na kasafin 2026 da aka amince da su, ba kashewa ba.

• Rehabilitation and expansion of earth dams at Rafin Duma (Ministry of Water Resources), 2026 Approved Budget: ₦54.56 miliyan
• Rehabilitation of Sokoto Township Water Works (Water Board), 2026 Approved Budget: ₦25.00 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 58
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 14.5s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
The total 2026 approved allocation is ₦13.30 billion (Kasafi's calculation). It combines ₦12.93 billion for animal health and livestock diseases management and ₦368.05 million for livestock feeds development. Both figures are approved budget allocations, not actual spending.

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Livestock feeds development (programme inside a sector, all spending (total), code 010206), 2026 Approved Budget: ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40
_Reply *show working* to see the rows and arithmetic._
```

## m12: partial (lines:list, 16.9s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
No separate 2026 capital lines for flyovers, inner-city dualization, or rural feeder roads are shown. The closest broader totals are the Ministry of Works main unit's 2026 approved capital budget of ₦42.26 billion and the Department for Rural Roads' 2026 approved capital budget of ₦15.47 billion. All figures are allocated (budgeted), not spent.

• Ministry of Works (one agency or unit, capital, code 023400100100), 2026 Approved Budget: ₦42.26 billion
• Department for Rural Roads (one agency or unit, capital, code 023405700100), 2026 Approved Budget: ₦15.47 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Possibly relevant too, not counted (I wasn't sure on a second reading): Ministry of Works (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 26
_Reply *show working* to see the rows and arithmetic._
```

## m13: not found (search, 20.1s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m14: answered (lines:sum, 15.4s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
An ware ₦6.38 biliyan (lissafin Kasafi) a kasafin 2026 da aka amince da shi don gina sabbin gidajen ma’aikata da gidaje. Wannan ya haɗa da ₦4.00 biliyan na gina rukunin gidaje 500 a Gidan Salanke, da ₦2.00 biliyan na gina rukunin gidaje 500 a Wajekke, da ₦382.98 miliyan na kammala gidan ma’aikata 53 a Jami’ar Jihar Sokoto. Dukkan waɗannan kuɗaɗen da aka ware ne (budgeted), ba kuɗaɗen da aka kashe ba.

• Construction of 500 Housing units at Gidan Salanke (Min of Lands and Housing), 2026 Approved Budget: ₦4.00 biliyan
• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan
• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: partial (lines:list, 17.3s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
Ee, akwai kudi da aka ware a kasafin 2026 don sufurin jama'a. An ware ₦1.50 biliyan don sufuri na ciki da wajen jihar (SSTA), da ₦2.40 biliyan don siyan motocin bas 20 na SSTA. Haka kuma an ware ₦140.00 miliyan don siyan kekuna masu kafa uku 300 ga nakasassu don saukaka sufuri. Dukkanninsu kudin da aka ware ne a kasafin 2026 da aka amince, ba kudin da aka kashe ba.

• INTER AND INTRA STATE TRANSPORTATION (SSTA) (Ministry of Transport), 2026 Approved Budget: ₦1.50 biliyan
• PURCHASE OF 20 NO TOYOTA 18-SEATER BUSES for SSTA (Ministry of Transport), 2026 Approved Budget: ₦2.40 biliyan
• Purchase of 300 Trycle bicycle for disable for ease transportation (Agency for Persons Living With Disabilities), 2026 Approved Budget: ₦140.00 miliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): PURCHASE OF BUSES (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 55, 64
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m16: answered (search, 13.8s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
2025 IGR was projected at ₦47.44 billion (original budget) and ₦47.94 billion (final budget), while actual collection for Q1–Q4 2025 was ₦20.58 billion (42.9% of the final budget). The 2026 IGR target is set at ₦74.52 billion.

📄 *Sources:* Budget Implementation Report Q4 2025, p. 9, 13; Sokoto State FY 2026 Budget, p. 1, 11
```

## m17: answered (lines:ratio, 19.4s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
The approved 2026 budget allocates ₦553.34 billion for Capital Expenditure and ₦205.36 billion for Recurrent Expenditure. The exact ratio of Capital to Recurrent Expenditure is 2.69 : 1 (Kasafi's calculation). Both figures are approved allocations.

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (lines:list, 12.5s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
For 2026, Sokoto State earmarked ₦10.03 billion for domestic principal and ₦6.00 billion for domestic interest/discount. For external debt, it earmarked ₦2.42 billion for foreign principal and ₦1.31 billion for foreign interest/discount. All four figures are 2026 Approved Budget allocations.

• DOMESTIC PRINCIPAl (code 220604), 2026 Approved Budget: ₦10.03 billion
• DOMESTIC INTEREST / DISCOUNT (code 220602), 2026 Approved Budget: ₦6.00 billion
• FOREIGN PRINCIPAL (code 220603), 2026 Approved Budget: ₦2.42 billion
• FOREIGN INTEREST / DISCOUNT (code 220601), 2026 Approved Budget: ₦1.31 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29
_Reply *show working* to see the rows and arithmetic._
```

## m19: answered (lines:compare, 22.2s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
• Difference (2026 Approved Budget vs 2025 Approved Budget): -₦489.02 million (-11.6%) (Kasafi's calculation)

• Government House (one agency or unit, overhead (running costs), code 011100100100), 2025 Approved Budget: ₦4.20 billion
• Government House (one agency or unit, overhead (running costs), code 011100100100), 2026 Approved Budget: ₦3.71 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 14; Sokoto State FY 2026 Budget, p. 21
_Reply *show working* to see the rows and arithmetic._
```

## m20: answered (search, 18.4s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa ƙarshen Q1 na 2026, an riga an kashe 3.0% na kasafin manyan ayyuka na daukacin jihar. Wannan 3.0% shi ne kaso na kasafin asali da aka kashe a Q1, ba jimillar shekara ba.

• 2026 kasafin asali (manyan ayyuka): ₦553.34 biliyan
• Q1 2026 da aka kashe (manyan ayyuka): ₦16.82 biliyan (3.0% na kasafin asali)

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 9, 27
```

## m21: answered (query_budget:rank, 11.9s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
Ten MDAs are tied for the lowest capital budget absorption rate at 0.0% for Q1–Q2 2026, so there is no distinct set of three lowest ministries.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 26, 27, 28
_Reply *show working* to see the rows and arithmetic._
```

## m22: answered (search, 17.1s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
At the end of Q2 2026 the Ministry of Health release rate was 10.6% of the revised budget (Q1–Q2 spent). This is shown in the Budget Implementation Report Q2 2026, page 18, Total Expenditure by Administrative Classification table.

• 2026 revised budget (total): ₦116.91 billion
• Q1-Q2 2026 spent (total): ₦12.36 billion (10.6% of the revised budget)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## m23: answered (search, 12.7s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
_Assumption: used first half of 2026 as Q1-Q2 cumulative in the Q2 2026 implementation report._

Allocated personnel budget for 2026 was ₦70.57 billion, with ₦37.30 billion spent in Q1-Q2 2026 only (52.8% of the revised budget). The leftover variance was ₦33.28 billion.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19
```

## m24: partial (lines:list, 17.5s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Babu layin horar da matasa sana’o’i da tallafin kudi daban a karkashin Ma’aikatar Matasa da Wasanni da aka nuna. Jimillar kasafin Ma’aikatar (ministry total including its agencies) da aka amince da shi a 2026 shi ne ₦17.06 biliyan (kudin da aka ware, ba wanda aka kashe ba).

• Ministry of Youth and Sports Development (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 051300000000), 2026 Original Budget: ₦17.06 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 17
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m25: answered (search, 20.6s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
Yes, the 2026 budget has dedicated lines for disability support, a special school, and therapeutic appliances. All figures below are allocated (2026 Approved Budget), not spent.

• 2026 approved budget (total): Agency for Persons Living With Disabilities: ₦3.07 billion
• 2026 approved budget (capital): Rehabilitation of 6 Blocks of 3 Classrooms and 5 Students Hostels at AA Raji Special School: ₦500.00 million
• 2026 approved budget (capital): THERAPEUTIC APPLIANCES AND EQUIPTMENT: ₦50.00 million
• 2026 approved budget (total): Inclusive Education: ₦102.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 65, 77, 188
```

## m26: partial (lines:list, 17.3s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
• Ministry for Women Affairs (ministry total including its agencies, all spending (total), code 051400000000), 2026 Approved Budget: ₦7.24 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Possibly relevant too, not counted (I wasn't sure on a second reading): Ministry for Women Affairs (2025 Approved Budget); Ministry for Women Affairs (2025 Revised Budget); tabs for Youth and Women Empowerment (POVERTY REDUCTION PROGRAMME) (2025 Revised Budget); tabs for Youth and Women Empowerment (POVERTY REDUCTION PROGRAMME) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18
_Reply *show working* to see the rows and arithmetic._
```

## m27: partial (search, 19.8s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
Shadun kasafi ba su nuna kuɗi daban don raya karkara da rage talauci a ƙananan hukumomin kan iyaka ba. Ƙaramar hukuma ba ma'aikatar jiha ba ce, kuma ƙananan hukumomi suna da kaso na doka daban. Abin da shaidu suka nuna shi ne jimillar fanni da shirin rage talauci, ba na kan iyaka ba.

• 2026 (kasafin da aka amince da shi, jimilla) fannin Rage Talauci: ₦6.10 biliyan
• 2026 (kasafin da aka amince da shi, jimilla) fannin Ruwa da Raya Karkara: ₦44.37 biliyan
• 2026 (kasafin da aka amince da shi, jimilla) Shirin Rage Talauci: ₦2.24 biliyan
• 2026 (kasafin da aka amince da shi, jimilla) tallafi ga ƙananan hukumomi: ₦10.50 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 40, 41, 173
```

## m28: not found (search, 14.2s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
I couldn't find the answer to that in the documents I have.
```

## m29: answered (lines:list, 18.2s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
Gwamnati ta ware ₦9.12 biliyan a kasafin 2025 don biyan gratuity. Ta ware ₦5.00 biliyan a kasafin 2026 don biyan gratuity. Wadannan kudaden da aka ware (budgeted) ne, ba kudaden da aka kashe ba.

• GRATUITY (manyan ayyuka, code 21030101), 2025 Approved Budget: ₦9.12 biliyan
• GRATUITY (manyan ayyuka, code 21030101), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 27
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 13.2s)

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

## m31: partial (lines:list, 29.6s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
The 2026 approved budget for purchase of motor vehicles for Guards (Department for Security Matters) is ₦3.00 billion. This is the internal security logistics support line shown. No separate line named Sokoto State Community Guard Corps is shown.

• Guards (Department for Security Matters) – purchase of motor vehicles, 2026 Approved Budget: ₦3.00 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): Sokoto Marshal Corps (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 52
_Reply *show working* to see the rows and arithmetic._
```

## m32: partial (lines:list, 18.6s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
For 2026, the State Judiciary's recurrent allocation is personnel of ₦1.60 billion and overhead of ₦3.18 billion, both allocated (budgeted). Its capital allocation is ₦3.39 billion, allocated (budgeted). The specific capital allocation for Renovation of 25No Upper and lower Sharia Courts is ₦102.06 million, allocated (budgeted).

• State Judiciary (ministry total including its agencies, personnel (salaries), code 031800000000) [Personnel Expenditure by Administrative Classification], 2026 Approved Budget: ₦1.60 billion
• State Judiciary (ministry total including its agencies, overhead (running costs), code 031800000000) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2026 Approved Budget: ₦3.18 billion
• State Judiciary (ministry total including its agencies, capital, code 031800000000) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦3.39 billion
• Renovation of 25No Upper and lower Sharia Courts (Shari’a Court of Appeal), 2026 Approved Budget: ₦102.06 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): Shari’a Court of Appeal (2026 Approved Budget); Renovation of Hon Grand khadi and khadis Residence Houses (Shari’a Court of Appeal) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26, 63
_Reply *show working* to see the rows and arithmetic._
```

## m33: partial (lines:sum, 16.7s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
The budgeted security vote is ₦5.50 billion for 2025 and ₦8.21 billion for 2026, totaling ₦13.71 billion (Kasafi's calculation). No line for contingency funds is shown separately in the lines provided.

• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604) [Expenditure by Economic Classification], 2025 Revised Budget: ₦5.50 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604) [Expenditure by Economic Classification], 2026 Approved Budget: ₦8.21 billion
• Not found: contingency funds

📄 *Sources:* Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m34: not found (search, 17.2s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Ban sami amsar wannan tambayar a cikin takardun da nake da su ba.
```

## m35: answered (lines:list, 21.1s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
The Sokoto State Independent Electoral Commission is shown as one agency or unit in the 2026 approved budget. Its 2026 Approved Budget amount is ₦460.48 million. The exact administrative code and page number are shown with the selected row below.

• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: not found (search, 16.8s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
I couldn't find the answer to that in the documents I have.
```

## m37: answered (search, 21.1s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
Daga teburin Jimillar Kashe Kuɗi ta Shiri, bangaren ICT ya samu ₦3.30 biliyan a kasafin 2025 a shafi 24. A kasafin 2026 ya samu ₦7.15 biliyan a shafi 41. Dukkan su kuɗaɗen da aka ware ne, ba kuɗaɗen da aka kashe ba.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 24; Sokoto State FY 2026 Budget, shafi 41
```

## m38: not found (search, 19.4s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Kasafin jihar bai nuna kuɗin da aka ware kai tsaye ga Ƙaramar Hukumar Wamakko ba. Layukan kasafin jiha na cibiyoyin da ke Wamakko (misali asibiti ko makaranta) kuɗin jiha ne, ba na ƙaramar hukumar ba. Ƙananan hukumomi suna samun kasonsu na doka daga asusun tarayya daban, kuma takardun da nake da su ba su nuna na Wamakko ba.
```

## m39: answered (lines:share, 14.1s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
• Share (↑ ÷ ↓): 48.6% (Kasafi's calculation)

• Ministry of Environment (ministry total including its agencies, capital, code 053500000000) [Capital Expenditure by Administrative Classification], 2026 Performance Year to Date (Q1-Q2): ₦7.86 billion ↑
• Ministry of Environment (ministry total including its agencies, capital, code 053500000000) [Capital Expenditure by Administrative Classification], 2026 Revised Budget: ₦16.17 billion ↓

📄 *Sources:* Budget Implementation Report Q2 2026, p. 28
_Reply *show working* to see the rows and arithmetic._
```
