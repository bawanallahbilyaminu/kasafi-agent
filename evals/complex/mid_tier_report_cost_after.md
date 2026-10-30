# Open-question run: mid_tier.json

39 questions: answered 21, partial 17, unverified 1 | wrong 0 of 11 checked | median 13.7s

```
plan          n=39 median   3.7s    28% of all time
line_search   n=35 median   1.6s    11% of all time
read          n=33 median   6.3s    41% of all time
read1         n=33 median   4.0s    28% of all time
read2         n=33 median   3.8s    26% of all time
reread        n= 8 median   6.4s     9% of all time
page_search   n=36 median   1.4s    11% of all time
compose       n=34 median   2.9s    19% of all time
answer        n=37 median   5.9s    48% of all time
row readings: 77 model calls for 33 questions (2 = no retry)
```

## m01: answered (lines:list, 11.5s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
Eh, akwai kudin tallafin karatu a kasafin 2026. Tallafin karatu na cikin gida (Domestic Scholarship) ₦1.60 biliyan ne, tallafin karatu na kasashen waje (FOREIGN SCHOLARSHIP SCHEME) kuma ₦1.50 biliyan ne. Dukkan su kudin da aka ware (approved budget) ne, ba kudin da aka kashe ba.

• Domestic Scholarship (code 22021025), 2026 Approved Budget: ₦1.60 biliyan
• FOREIGN SCHOLARSHIP SCHEME (code 22021020), 2026 Approved Budget: ₦1.50 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m02: partial (lines:list, 21.1s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
SUBEB classroom construction in 2025 was allocated ₦4.55 billion plus ₦500.00 million. For rehabilitation/repairs of public schools, ₦205.00 million was shown for 2025 and ₦205.00 million for 2026. No separate 2026 SUBEB classroom construction line is shown.

• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦4.55 billion
• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦500.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million
• Not found: 2026 SUBEB classroom construction allocation; 2025 SUBEB renovation approved budget

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 29; Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: answered (search, 21.2s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
The 2026 approved budget has specific lines for girl-child education and school feeding, and a broader line for retention. Girl-child education is shown as Girls/Boys child education, school feeding is shown as School feeding, and retention is part of Increase in access, retention, and completion rate at all levels. All figures below are allocated (budgeted) amounts for 2026.

• Girls/Boys child education (capital) 2026 approved budget (capital): ₦200.00 million
• Girls/Boys child education (total) 2026 approved budget (total): ₦200.00 million
• School feeding (other non-debt recurrent) 2026 approved budget (overhead): ₦2.03 billion
• School feeding (total) 2026 approved budget (total): ₦2.03 billion
• Increase in access, retention, and completion rate at all levels 2026 approved budget (total): ₦11.26 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40, 41, 44, 46
```

## m04: answered (lines:share, 14.9s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
The 2026 approved allocation to HEALTH (all spending) is ₦120.13 billion out of Total Expenditure of ₦758.70 billion. 15.8% of the 2026 approved budget's Total Expenditure goes to health (Kasafi's calculation), for comparison with the Abuja Declaration benchmark named in the question.

• HEALTH (all spending (total), code 707), 2026 Original Budget: ₦120.13 billion ↑
• Total Expenditure (all spending (total)), 2026 Original Budget: ₦758.70 billion ↓

📄 *Sources:* Budget Implementation Report Q2 2026, p. 15, 36
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

## m06: answered (lines:list, 9.9s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
The 2026 approved counterpart funding for PHC-MOU activities, covering routine immunization and primary healthcare, is ₦100.00 million.

• Provision of support for PHC-MOU activities (Primary Health Care Development Agency), 2026 Approved Budget: ₦100.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 70
_Reply *show working* to see the rows and arithmetic._
```

## m07: partial (lines:list, 14.8s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• CONSTRUCTION / PROVISION OF HOSPITALS / HEALTH CENTRES (code 23020106), 2026 Performance Year to Date (Q1-Q2): ₦80.00 million [1]
• REHABILITATION / REPAIRS - HOSPITAL / HEALTH CENTRES (code 23030105), 2026 Performance Year to Date (Q1-Q2): ₦41.81 million [1]

📄 *Sources:* Budget Implementation Report Q2 2026, p. 53
```

## m08: answered (lines:compare, 13.9s)

**Q:** Nawa gwamnatin jihar Sokoto ta ware don sayen takin zamani da tallafin kayan noma a shekarar 2026, kuma nawa aka riga aka kashe?

```
Gwamnatin Sokoto ta ware ₦5.65 biliyan a 2026 don sayen kayan noma (PURCHASE OF AGRICULTURAL INPUTS). Har zuwa kwata na biyu (Q1-Q2) an kashe ₦2.43 biliyan, wato 43.0% (lissafin Kasafi). Adadin farko kasafin kudi ne, na biyu kuma abin da aka kashe.

• PURCHASE OF AGRICULTURAL INPUTS (code 23010140), 2026 Approved Budget: ₦5.65 biliyan
• PURCHASE OF AGRICULTURAL INPUTS (code 23010140), 2026 Performance Year to Date (Q1-Q2): ₦2.43 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 30; Budget Implementation Report Q2 2026, shafi 32
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m09: partial (lines:list, 14.1s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
The documents show specific capital project lines for irrigation schemes and for tube wells. Irrigation Scheme Youth empowerment (NEMI NA KANKA) was allocated ₦200.00 million in both 2025 Revised and 2026 Approved, and Kware irrigation scheme (SPIN Project) rose from ₦200.00 million in 2025 Revised to ₦800.00 million in 2026 Approved. Construction of Tube Wells (Fadama Programme) was allocated ₦531.96 million in 2025 Revised and 0.00 in 2026 Approved. No line labelled solar-powered tube wells is shown.

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

## m10: partial (lines:list, 20.8s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
Eh, akwai kudaden da aka ware don gyaran ayyukan ruwa a birnin Sokoto a kasafin 2026. Gyaran aikin ruwan garin Sokoto (Sokoto Township Water Works) yana da ₦25.00 biliyan da aka amince da su, gyaran manyan tankokin ruwa a cikin birnin Sokoto yana da ₦35.00 miliyan da aka amince da su. Ba a nuna layin gyaran madatsun ruwa daban ba.

• Rehabilitation of Sokoto Township Water Works (Water Board), 2026 Approved Budget: ₦25.00 biliyan
• Rehabilitation of Overhead Tanks within Sokoto Metropolis (Water Board), 2026 Approved Budget: ₦35.00 miliyan
• Ba a samu ba: gyaran madatsun ruwa

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 58
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 10.4s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
The 2026 approved allocation is ₦13.30 billion (Kasafi's calculation) in total. This is Animal health and livestock diseases management plus Livestock feeds development, which covers grazing reserves. All figures are approved allocations, not spending.

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Livestock feeds development (programme inside a sector, all spending (total), code 010206), 2026 Approved Budget: ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40
_Reply *show working* to see the rows and arithmetic._
```

## m12: partial (lines:list, 18.6s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
The 2026 approved capital figures shown for rural roads are ₦2.25 billion, ₦200.00 million for rehabilitation of existing rural roads projects, and ₦7.90 billion for construction of rural roads through RAMP. No separate lines for flyovers or inner-city dualization under the Ministry of Works are shown in the lines provided.

• Department for Rural Roads (code 023405700100) – construction / provision of roads, 2026 Approved Budget: ₦2.25 billion
• Rehabilitation of existing projects under rural roads (Department for Rural Roads), 2026 Approved Budget: ₦200.00 million
• 17100125000200 - Road - General Construction of Rural Roads through Rural access and mobility projects (RAMP), 2026 Approved Budget: ₦7.90 billion
• Not found: flyovers, inner-city dualization

📄 *Sources:* Sokoto State FY 2026 Budget, p. 56, 217
_Reply *show working* to see the rows and arithmetic._
```

## m13: partial (lines:list, 12.8s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• CONTRACTOR REGISTRATION FEES (code 12020417, Primary Health Capital Expenditure by Project), 2025 Revised Budget: ₦50.00 million [1]
• CONTRACTOR REGISTRATION FEES (code 12020417, Primary Health Capital Expenditure by Project), 2026 Approved Budget: ₦50.00 million [1]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 196
```

## m14: answered (lines:sum, 15.4s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
An ware ₦6.38 biliyan (lissafin Kasafi) a kasafin 2026 don gina sabbin gidaje da gidajen ma’aikata. Wannan ya hada da gidaje 500 a Gidan Salanke, gidaje 500 a Wajekke, Wamakko, da kammala gidajen ma’aikata 53 a Jami’ar Jihar Sakkwato. Duka kudaden da aka ware ne (approved budget), ba wanda aka kashe ba.

• Construction of 500 Housing units at Gidan Salanke (Min of Lands and Housing), 2026 Approved Budget: ₦4.00 biliyan
• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan
• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: answered (search, 13.7s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
Eh, akwai kuɗi a kasafin 2026 don sufurin jama'a. Gwamnatin Jiha ta ware kuɗi don siyan motocin bas a ƙarƙashin Ma'aikatar Sufuri, kuma jimillar kasafin Ma'aikatar Sufuri da fannin sufuri ya nuna an ware babban kuɗi don sufuri. Kuɗi da aka ware (an amince) ne, ba wanda aka kashe ba.

• 2026 kasafin da aka amince (jimilla) - Ma'aikatar Sufuri: ₦50.87 biliyan
• 2026 kasafin da aka amince (manyan ayyuka) - Ma'aikatar Sufuri: ₦47.67 biliyan
• 2026 kasafin da aka amince (manyan ayyuka) - Siyan motocin bas (INTER AND INTRA STATE TRANSPORTATION): ₦1.50 biliyan
• 2026 kasafin da aka amince (manyan ayyuka) - fannin TRANSPORT: ₦105.80 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26, 37, 55
```

## m16: answered (search, 10.5s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
The State Government projected Internally Generated Revenue (IGR) for 2025 was ₦47.44 billion as approved and ₦47.94 billion as final/revised budget. Actual collections for the full year 2025 (Q1–Q4) were ₦20.58 billion which was 42.9% of the final budget. The target set for 2026 is ₦74.52 billion.

• 2025 approved budget (total): ₦47.44 billion
• 2025 final/revised budget (total): ₦47.94 billion
• 2025 actual collections Q1-Q4 (total): ₦20.58 billion (42.9% of the final budget)
• 2026 target (total): ₦74.52 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 11; Budget Implementation Report Q4 2025, p. 9, 13; Sokoto State Government 2025 Approved Budget, p. 1
```

## m17: answered (lines:ratio, 10.4s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
Capital Expenditure approved for 2026 is ₦553.34 billion and Recurrent Expenditure approved for 2026 is ₦205.36 billion. The ratio of Capital to Recurrent is 2.69 : 1 (Kasafi's calculation).

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: partial (lines:list, 18.4s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
For 2026, Sokoto State budgeted ₦10.03 billion for domestic principal and ₦2.42 billion for foreign principal. Both figures are approved allocations (earmarked), not actual spending.

• DOMESTIC PRINCIPAl (code 220604), 2026 Approved Budget: ₦10.03 billion
• FOREIGN PRINCIPAL (code 220603), 2026 Approved Budget: ₦2.42 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): FOREIGN INTEREST / DISCOUNT (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29
_Reply *show working* to see the rows and arithmetic._
```

## m19: answered (lines:compare, 14.8s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
The overhead allocation for Government House (Office of the Executive Governor) was ₦4.20 billion in the 2025 Approved Budget and ₦3.71 billion in the 2026 Approved Budget.

• Government House (one agency or unit, overhead (running costs), code 011100100100), 2025 Approved Budget: ₦4.20 billion
• Government House (one agency or unit, overhead (running costs), code 011100100100), 2026 Approved Budget: ₦3.71 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 14; Sokoto State FY 2026 Budget, p. 21
_Reply *show working* to see the rows and arithmetic._
```

## m20: answered (search, 14.0s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa ƙarshen zangon farko (Q1) na 2026, an kashe kashi 3.0% na kasafin babban aiki na daukacin jihar. Kasafin babban aiki da aka amince da shi na 2026 shi ne ₦553.34 biliyan, kuma abin da aka kashe a Q1 (Janairu-Maris 2026 kawai) shi ne ₦16.82 biliyan. Wannan shi ne kaso da aka buga a rahoton a matsayin 3.0% na kasafin da aka amince da shi.

• 2026 kasafin da aka amince da shi (manyan ayyuka): ₦553.34 biliyan
• Q1 2026 da aka kashe (Janairu-Maris 2026 kawai) (manyan ayyuka): ₦16.82 biliyan (3.0% na kasafin da aka amince da shi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 9, 27
```

## m21: unverified (search, 8.8s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
I found documents about your question, but couldn't verify the figures. Please check these sources:

[1] Budget Implementation Report Q2 2026, page 27
[2] Budget Implementation Report Q2 2026, page 28
[3] Budget Implementation Report Q2 2026, page 26
```

## m22: answered (search, 4.8s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
*Ministry of Health* (code 052100000000):
• Total: share of the revised budget spent 10.6% (Kasafi's calculation); spent so far (Q1–Q2) ₦12.36 billion; approved budget ₦124.41 billion

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18; Sokoto State FY 2026 Budget, p. 18
```

## m23: answered (lines:compare, 10.8s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
Budgeted personnel expenditure for 2026 was ₦70.57 billion, while actual payroll outturn through the first half (Q1-Q2) was ₦37.30 billion. The variance is -₦33.28 billion (Kasafi's calculation), which is 52.8% (Kasafi's calculation) spent.

• Total Personnel Expenditure (personnel (salaries)) [Personnel Expenditure by Administrative Classification], 2026 Original Budget: ₦70.57 billion
• Total Personnel Expenditure (personnel (salaries)) [Personnel Expenditure by Administrative Classification], 2026 Performance Year to Date (Q1-Q2): ₦37.30 billion

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19
_Reply *show working* to see the rows and arithmetic._
```

## m24: partial (lines:list, 11.9s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Babu layin horar da matasa sana'o'i da tallafin kudi na Ma'aikatar Matasa da Wasanni da aka nuna daban a 2026. Abin da aka nuna kawai shi ne jimillar Ma'aikatar Matasa da Wasanni ta ₦17.06 biliyan a kasafin 2026 da aka amince.

• Ministry of Youth and Sports Development (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 051300000000), 2026 Approved Budget: ₦17.06 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m25: answered (search, 15.5s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
Yes. The 2026 approved budget has dedicated lines for persons with disabilities. The Agency for Persons Living With Disabilities has an approved budget of ₦3.07 billion, shown under Capital Expenditure as 71012 DISABILITY. Health provides ₦50.00 million for therapeutic appliances and equipment, which are assistive devices. Basic education provides ₦102.00 million for inclusive education.

• 2026 Approved Budget for Agency for Persons Living With Disabilities (total): ₦3.07 billion
• 2026 Approved Budget for DISABILITY capital (capital): ₦3.07 billion
• 2026 Approved Budget for THERAPEUTIC APPLIANCES AND EQUIPTMENT - assistive devices (capital): ₦50.00 million
• 2026 Approved Budget for Inclusive Education (capital): ₦102.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 37, 77, 188, 189
```

## m26: partial (lines:list, 12.2s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
The budget shows Women's Economic Empowerment separately at ₦4.94 billion for 2025 (revised) and ₦3.15 billion for 2026 (approved). No separate lines for orphanages or destitute homes are shown.

• Women's Economic Empowerment (programme inside a sector, all spending (total), code 230301) [Total Expenditure by Programme (Sector, Objective and Programme)], 2025 Revised Budget: ₦4.94 billion
• Women's Economic Empowerment (programme inside a sector, all spending (total), code 230301) [Total Expenditure by Programme (Sector, Objective and Programme)], 2026 Approved Budget: ₦3.15 billion
• Not found: orphanages, destitute homes

📄 *Sources:* Sokoto State FY 2026 Budget, p. 42
_Reply *show working* to see the rows and arithmetic._
```

## m27: partial (lines:sum, 11.0s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
Kasafin 2026 bai ware kudi daban don raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka ba. Abin da aka buga shi ne jimillar sassan biyu baki daya: ₦44.37 biliyan na Water Resources and Rural Development da kuma ₦6.10 biliyan na Poverty Alleviation a matsayin kasafin da aka amince da shi na 2026 (Kasafi's calculation).

• Water Resources and Rural Development (jimillar ɓangare, duk kashe kuɗi (jimilla), code 10), 2026 Approved Budget: ₦44.37 biliyan
• Poverty Alleviation (jimillar ɓangare, duk kashe kuɗi (jimilla), code 03), 2026 Approved Budget: ₦6.10 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 40, 41
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m28: partial (lines:list, 14.3s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Total Personnel Expenditure, 2026 Approved Budget: ₦70.57 billion [1]
• PERSONNEL COST (capital, code 21), 2026 Approved Budget: ₦70.57 billion [2]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19, 27
```

## m29: answered (lines:compare, 10.7s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
Gwamnati ta ware ₦9.12 biliyan a kasafin 2025 da aka amince da shi don biyan gratuity, da ₦5.00 biliyan a kasafin 2026 da aka amince da shi. Dukkanin adadin da aka ware ne (budgeted), ba abin da aka kashe ba.

• GRATUITY (manyan ayyuka, code 21030101), 2025 Approved Budget: ₦9.12 biliyan
• Gratuity (shiri cikin ɓangare, duk kashe kuɗi (jimilla), code 230502), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 42
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: partial (lines:list, 20.9s)

**Q:** How much was budgeted for staff training, civil service computerization, and promotion arrears in the 2026 budget?

```
The 2026 approved budget for staff training (TRAINING - GENERAL) is ₦8.62 billion. No lines were shown for civil service computerization or promotion arrears, so those amounts could not be listed.

• TRAINING - GENERAL (code 220205), 2026 Approved Budget: ₦8.62 billion
• Not found: civil service computerization and promotion arrears - no lines for these items were shown

📄 *Sources:* Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m31: partial (lines:list, 9.2s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• SECURITY SERVICES (code 22020601), 2026 Approved Budget: ₦8.62 billion [1]
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion [1]
• Sokoto Marshal Corps (one agency or unit, overhead (running costs), code 012400700100), 2026 Original Budget: ₦1.13 billion [2]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 28; Sokoto State Budget Implementation Report Q1 2026, p. 23
```

## m32: answered (search, 12.5s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
In the 2026 approved budget, the Ministry of Justice (administration of justice) has a recurrent allocation of ₦1.52 billion and a capital allocation of ₦3.71 billion. The renovation of 25 Upper and Lower Shari’ah Courts is budgeted separately as a capital project at ₦102.06 million.

• 2026 approved budget (overhead): ₦1.52 billion
• 2026 approved budget (capital): ₦3.71 billion
• Renovation of 25No Upper and lower Sharia Courts 2026 approved budget (capital): ₦102.06 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 24, 26, 63
```

## m33: partial (lines:sum, 17.8s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
The approved allocation for Security Vote (including operations) was ₦5.50 billion in 2025 and ₦8.21 billion in 2026, for a combined ₦13.71 billion (Kasafi's calculation). No line for contingency funds is shown, so it is not included.

• SECURITY VOTE (INCLUDING OPERATIONS) (capital, code 22020604), 2025 Approved Budget: ₦5.50 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion
• Not found: contingency funds

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 17; Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m34: partial (lines:list, 12.4s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• RECREATION, CULTURE AND RELIGION (capital, code 708), 2026 Approved Budget: ₦23.32 biliyan [1]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 37
```

## m35: answered (lines:list, 16.1s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
The 2026 Approved Budget allocation (total expenditure) for the Sokoto State Independent Electoral Commission is ₦460.48 million. The exact administrative code and page number are shown in the line details listed under this summary.

• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: partial (lines:list, 14.4s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Airways (sector total, capital, code 18), 2026 Approved Budget: ₦36.00 billion [1]
• PURCHASE OF AEROPLANE (code 23010143), 2026 Approved Budget: ₦36.00 billion [2]
• Airways - General (programme inside a sector, capital, code 181001), 2026 Approved Budget: ₦36.00 billion [1]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 47, 126
```

## m37: answered (lines:compare, 16.3s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
• Bambanci (2026 Approved Budget vs 2025 Approved Budget): +₦3.85 biliyan (+116.5%) (lissafin Kasafi)

• Information Communication and Technology (jimillar ɓangare, duk kashe kuɗi (jimilla), code 11), 2025 Approved Budget: ₦3.30 biliyan
• Information Communication and Technology (jimillar ɓangare, duk kashe kuɗi (jimilla), code 11), 2026 Approved Budget: ₦7.15 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 24; Sokoto State FY 2026 Budget, shafi 41
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m38: partial (lines:list, 11.6s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• WAMAKKO (capital, code 33312100, Capital Expenditure by Functional Classification), 2026 Approved Budget: ₦82.18 biliyan [1]
• WAMAKKO (code 33312100, Personnel Expenditure by Location), 2026 Approved Budget: ₦1.60 biliyan [2]
• Orthopedic Hospital Wamakko (one agency or unit, all spending (total), code 052104100100), 2026 Approved Budget: ₦1.27 biliyan [3]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 38, 39
```

## m39: answered (search, 5.0s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
*Ministry of Environment* (code 053500000000):
• Capital: share of the revised budget spent 48.6% (Kasafi's calculation)
• Total: share of the revised budget spent 47.0% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18, 28
```
