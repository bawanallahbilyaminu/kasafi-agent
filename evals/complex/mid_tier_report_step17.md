# Open-question run: mid_tier.json

39 questions: answered 20, partial 14, not found 5 | wrong 4 of 11 checked (m10, m14, m19, m35) | median 11.9s

```
plan          n=39 median   3.0s    22% of all time
line_search   n=28 median   2.3s    12% of all time
read          n=28 median   5.7s    34% of all time
read1         n=28 median   5.0s    31% of all time
read2         n=28 median   4.4s    25% of all time
reread        n= 8 median   8.9s    12% of all time
page_search   n=13 median   1.3s     3% of all time
compose       n=13 median   4.0s    12% of all time
answer        n=39 median   5.1s    51% of all time
row readings: 63 model calls for 28 questions (2 = no retry)
```

## m01: answered (lines:sum, 12.2s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
I, akwai tanadi na tallafin karatu ga daliban jihar Sokoto a kasafin 2026 da aka amince da shi. Tallafin cikin gida (Domestic Scholarship) ₦1.60 biliyan ne, tallafin kasashen waje (Foreign Scholarship Scheme) kuma ₦1.50 biliyan ne. Jimillarsu ₦3.10 biliyan (lissafin Kasafi). Wadannan kudade ne da aka ware (budgeted), ba wanda aka kashe ba.

• Domestic Scholarship (code 22021025), 2026 Approved Budget: ₦1.60 biliyan
• FOREIGN SCHOLARSHIP SCHEME (code 22021020), 2026 Approved Budget: ₦1.50 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m02: answered (lines:list, 11.2s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
For construction/provision of public schools, SUBEB was allocated 0.00 in the 2025 revised budget and ₦150.00 million in the 2026 approved budget. For rehabilitation/repairs of public schools, SUBEB was allocated ₦205.00 million in the 2025 revised budget and ₦205.00 million in the 2026 approved budget. These are allocated (budgeted) amounts, not spending.

• education level in the State (State Universal Basic Education Board (SUBEB)) [Capital Expenditure by Project], 2025 Revised Budget: 0.00
• education level in the State (State Universal Basic Education Board (SUBEB)) [Capital Expenditure by Project], 2026 Approved Budget: ₦150.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: answered (lines:list, 10.1s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
The 2026 approved budget shows specific lines for all three areas. Girls Education Project monitoring is budgeted at 0.00, School feeding at ₦2.03 billion, Meal Subsidy to Government Schools at ₦2.00 billion, and access, retention and completion at ₦11.26 billion. All figures are approved allocations, not spending.

• Girls Education Project (11) with State to State (Ministry for Basic Education), 2026 Approved Budget: 0.00
• School feeding (code 050203), 2026 Approved Budget: ₦2.03 billion
• MEAL SUBSIDY TO GOVERNMENT SCHOOLS (code 22050102), 2026 Approved Budget: ₦2.00 billion
• Increase in access, retention, and completion rate at all levels (code 0502), 2026 Approved Budget: ₦11.26 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40, 41, 65, 149
_Reply *show working* to see the rows and arithmetic._
```

## m04: answered (lines:share, 26.3s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
15.8% (Kasafi's calculation) of the 2026 approved budget's Total Expenditure goes to health; the Abuja Declaration target is given in the question. Health is allocated ₦120.13 billion out of Total Expenditure of ₦758.70 billion. Both figures are 2026 Approved Budget allocations (budgeted).

• HEALTH (code 707), 2026 Approved Budget: ₦120.13 billion ↑
• Total Expenditure, 2026 Approved Budget: ₦758.70 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1, 32
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

## m06: partial (lines:list, 16.3s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
• Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health), 2026 Approved Budget: ₦70.00 million
• 04050126007201 - Functional health facilities Basic Health Care Provision Funds (BHCF) 25% Counterpart, 2026 Approved Budget: ₦109.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): BHCF Counterpart Funds for SOCHEMA (Sokoto State contributory health care mgt agency) (2026 Approved Budget); Support for Family Planning Programme (Counterpart) (Primary Health Care Development Agency) (2026 Approved Budget); 04050124000403 - Functional health facilities BHCF Counterpart Funds for SOCHEMA (2026 Approved Budget); Provision of support for PHC-MOU activities (Primary Health Care Development Agency) (2026 Approved Budget); 04050124008401 - Functional health facilities Support for Family Planning Programme (Counterpart) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 67, 229
_Reply *show working* to see the rows and arithmetic._
```

## m07: partial (search, 32.3s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
The evidence does not show releases or spending for maternal and child healthcare centers across rural local government areas separately by Q2 2026. The 2026 approved budget (capital) for Reproductive, maternal and neonatal health is ₦170.00 million, and for Medical and Maternity Centre Services is 0.00.

• 2026 approved budget (capital) for Reproductive, maternal and neonatal health: ₦170.00 million
• 2026 approved budget (capital) for Medical and Maternity Centre Services: 0.00

📄 *Sources:* Sokoto State FY 2026 Budget, p. 45, 188; Budget Implementation Report Q2 2026, p. 49
```

## m08: answered (category, 5.2s)

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

## m09: partial (lines:list, 22.4s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
The budgets show two specific irrigation-scheme lines and one tube-well line. Irrigation Scheme Youth empowerment (NEMI NA KANKA) was allocated ₦200.00 million for 2025 and ₦200.00 million for 2026, and Kware irrigation scheme (SPIN Project) was allocated ₦200.00 million for 2025 and ₦800.00 million for 2026. Construction of Tube Wells across the State was allocated ₦531.96 million for 2025 and 0.00 for 2026. All figures are budgeted allocations, not spending.

• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦800.00 million
• Construction of Tube Wells across the State (Nigeria CARES- Fadama Programme) [Capital Expenditure by Project], 2025 Revised Budget: ₦531.96 million
• … +1
• Not found: solar-powered tube wells

📄 *Sources:* Sokoto State FY 2026 Budget, p. 53
_Reply *show working* to see the rows and arithmetic._
```

## m10: answered WRONG: none of [['25,000,000,000.00']] (lines:list, 10.5s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
Ee, akwai kudin da aka ware a kasafin 2026. An ware ₦54.56 miliyan don gyara da fadada madatsun ruwa na Rafin Duma, da ₦5.00 biliyan don hukumar tashoshin famfon ruwa. Dukkan su kudadene da aka ware (approved budget), ba kudin da aka kashe ba.

• Rehabilitation and expansion of earth dams at Rafin Duma (Ministry of Water Resources), 2026 Approved Budget: ₦54.56 miliyan
• Board for water pumping Stations. (Ministry of Water Resources), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 58
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 12.0s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
• Not added up: these lines are printed in different tables of one budget, which can show the same money twice.

• Animal health and livestock diseases management (code 010205), 2026 Approved Budget: ₦12.93 billion
• Development of Grazing Reserve for posture production (Livestock Development Programme), 2026 Approved Budget: ₦50.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40, 61
_Reply *show working* to see the rows and arithmetic._
```

## m12: partial (lines:list, 19.1s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
The 2026 approved budget does not show flyovers, inner-city dualization and rural feeder roads as separate lines. The broader road construction lines are ₦3.00 billion for the Ministry of Works and ₦2.25 billion for the Department for Rural Roads, both allocated (budgeted).

• Ministry of Works (code 023400100100) – construction / provision of roads, 2026 Approved Budget: ₦3.00 billion
• Department for Rural Roads (code 023405700100) – construction / provision of roads, 2026 Approved Budget: ₦2.25 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Not found: flyovers, inner-city dualization, rural feeder roads

📄 *Sources:* Sokoto State FY 2026 Budget, p. 55, 56
_Reply *show working* to see the rows and arithmetic._
```

## m13: not found (search, 19.6s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m14: partial WRONG: none of [['2,000,000,000.00']] (lines:list, 22.5s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
An ware ₦382.98 miliyan a kasafin 2026 don kammala gina sabbin gidajen ma’aikata (staff quarters 53) a Jami’ar Jihar Sokoto. Wannan kuɗi ne da aka ware (approved budget), ba wanda aka kashe ba. Ba a ga wani layi daban don gina sabbin gidajen masu karamin karfi ko matsakaita ba.

• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): CONSTRUCTION / PROVISION OF RESIDENTIAL BUILDINGS (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: partial (lines:list, 10.3s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
_Ban ga wata shekara ba a tambayarka, don haka na yi amfani da kasafin 2026 mafi sabo._

• INTER AND INTRA STATE TRANSPORTATION (SSTA) (Ministry of Transport), 2026 Approved Budget: ₦1.50 biliyan
• PURCHASE OF 20 NO TOYOTA 18-SEATER BUSES for SSTA (Ministry of Transport), 2026 Approved Budget: ₦2.40 biliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): Purchase of 300 Trycle bicycle for disable for ease transportation (Agency for Persons Living With Disabilities) (2026 Approved Budget); PURCHASE OF BUSES (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 55
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m16: partial (lines:list, 8.7s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
The 2025 projected Independent Revenue (IGR) was ₦47.44 billion allocated (budgeted), later revised to ₦47.94 billion. Actual full-year collections in 2025 were ₦20.58 billion spent. The 2026 target is set at ₦74.52 billion allocated (budgeted).

• INDEPENDENT REVENUE (code 12) [Total Revenue by Economic Classification], 2025 Original Budget: ₦47.44 billion
• INDEPENDENT REVENUE (code 12) [Total Revenue by Economic Classification], 2025 Performance Year to Date (Q1-Q4): ₦20.58 billion
• INDEPENDENT REVENUE (code 12), 2026 Approved Budget: ₦74.52 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): INDEPENDENT REVENUE (2025 Final Budget)

📄 *Sources:* Budget Implementation Report Q4 2025, p. 13; Sokoto State FY 2026 Budget, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## m17: answered (lines:ratio, 7.4s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
Approved Capital Expenditure for 2026 is ₦553.34 billion and approved Recurrent Expenditure is ₦205.36 billion. The exact ratio of Capital to Recurrent Expenditure is 2.69 : 1 (Kasafi's calculation). Both figures are budgeted allocations.

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (lines:list, 11.2s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
• DOMESTIC PRINCIPAl (code 220604), 2026 Approved Budget: ₦10.03 billion
• DOMESTIC INTEREST / DISCOUNT (code 220602), 2026 Approved Budget: ₦6.00 billion
• FOREIGN PRINCIPAL (code 220603), 2026 Approved Budget: ₦2.42 billion
• FOREIGN INTEREST / DISCOUNT (code 220601), 2026 Approved Budget: ₦1.31 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29
_Reply *show working* to see the rows and arithmetic._
```

## m19: not found WRONG: none of [['4,201,809,645.00', '3,712,790,422.00'], ['9,681,659,645.00', '11,441,290,422.00']] (search, 8.2s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m20: answered (search, 10.2s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa karshen Q1 na 2026, an kashe 3.0% na kasafin manyan ayyuka na daukacin jihar. Wannan kashewar ta Q1 2026 ne kawai.

• 2026 kasafin da aka amince (manyan ayyuka): ₦553.34 biliyan
• Q1 2026 da aka kashe (manyan ayyuka) (Q1 2026 kawai): ₦16.82 biliyan

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 9, 27
```

## m21: answered (query_budget:rank, 6.9s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
Ten MDAs are tied for the lowest capital budget absorption rate at 0.0% for Q1–Q2 2026, so there is no distinct three lowest ministries.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 26, 27, 28
_Reply *show working* to see the rows and arithmetic._
```

## m22: answered (search, 8.6s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
At end of Q2 2026 (Q1–Q2 only) the Ministry of Health total spending was ₦12.36 billion, which was 10.6% of the revised budget, confirmed in the Budget Implementation Report Q2 2026 on page 18.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## m23: answered (lines:compare, 10.3s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
The budgeted personnel expenditure for 2026 was ₦70.57 billion (allocated). Actual payroll outturn through the first half (Q1-Q2) was ₦37.30 billion (spent). The variance is -₦33.28 billion (Kasafi's calculation), which is 52.8% spent (Kasafi's calculation).

• Total Personnel Expenditure [Personnel Expenditure by Administrative Classification], 2026 Original Budget: ₦70.57 billion
• Total Personnel Expenditure [Personnel Expenditure by Administrative Classification], 2026 Performance Year to Date (Q1-Q2): ₦37.30 billion

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19
_Reply *show working* to see the rows and arithmetic._
```

## m24: partial (lines:list, 11.2s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Babu layin ware-ware na horar da matasa sana'o'i da tallafin kudi a karkashin Ma'aikatar Matasa da Wasanni da aka nuna daban a 2026. Abin da aka nuna kawai shi ne jimillar kasafin Ma'aikatar Matasa da Wasanni ta 2026 da aka amince da ita na ₦13.99 biliyan, wanda ya kunshi komai na ma'aikatar. Wannan adadin da aka ware ne (budgeted), ba wanda aka kashe ba.

• Ministry of Youth and Sports Development (code 051300100100), 2026 Approved Budget: ₦13.99 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m25: partial (lines:list, 15.5s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
Yes for assistive devices: ₦140.00 million is allocated (budgeted) in 2026 for purchase of 300 tricycle bicycles for disables for ease of transportation. No specific, dedicated lines for special schools or for welfare support for persons with disabilities are shown in the lines provided.

• Purchase of 300 Trycle bicycle for disable for ease transportation (Agency for Persons Living With Disabilities), 2026 Approved Budget: ₦140.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): DISABILITY (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 64
_Reply *show working* to see the rows and arithmetic._
```

## m26: partial (lines:list, 16.5s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
The budget shows ₦400.00 million for 2025 (Revised Budget) and ₦350.00 million for 2026 (Approved Budget) for purchase of industrial equipment under Youth and Women Empowerment. No separate lines are shown for orphanages and destitute homes. The lines show 0.00 performance/spending for this equipment purchase.

• tabs for Youth and Women Empowerment (POVERTY REDUCTION PROGRAMME) [Capital Expenditure by Project], 2025 Revised Budget: ₦400.00 million
• tabs for Youth and Women Empowerment (POVERTY REDUCTION PROGRAMME) [Capital Expenditure by Project], 2026 Approved Budget: ₦350.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): Ministry of Humanitarian Affairs & Social Welfare (2025 Approved Budget); Ministry of Humanitarian Affairs & Social Welfare (2025 Revised Budget); Ministry of Humanitarian Affairs & Social Welfare (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 49
_Reply *show working* to see the rows and arithmetic._
```

## m27: partial (lines:sum, 17.4s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
• Ba a haɗa su ba: a karatu na biyu ban tabbata waɗanne layuka ne ke cikin jimillar ba, don haka jimillar waɗannan kaɗai za ta iya ɓatarwa.

• Poverty Alleviation (code 03), 2026 Approved Budget: ₦6.10 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): Integrated rural development (agricultural land development, farm mechanization, & rural infrastructures (2026 Approved Budget); Water Resources and Rural Development (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 40
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m28: not found (search, 9.6s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
I couldn't find the answer to that in the documents I have.
```

## m29: answered (lines:compare, 15.2s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
Gwamnati ta ware ₦9.12 biliyan a kasafin 2025 da aka amince don biyan gratuity. A kasafin 2026 da aka amince ta ware ₦5.00 biliyan don gratuity. Wadannan kudadeden da aka ware ne, ba kudin da aka kashe ba.

• GRATUITY (code 21030101), 2025 Approved Budget: ₦9.12 biliyan
• GRATUITY (code 21030101), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 27
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 11.9s)

**Q:** How much was budgeted for staff training, civil service computerization, and promotion arrears in the 2026 budget?

```
Statewide, the 2026 approved budget has LOCAL TRAINING (22020501) ₦6.80 billion; INTERNATIONAL TRAINING (22020502) ₦1.82 billion; CAPACITY DEVELOPMENT (23050108) ₦860.00 million; COMPUTER SOFTWARE ACQUISITION (23050102) ₦1.41 billion, ₦10.89 billion together (Kasafi's calculation). By the end of June 2026, ₦991.69 million of it had been spent statewide (9.1%, Budget Implementation Report Q2 2026).

Largest:
• Department for Security Matters: ₦1.80 billion
• State Universal Basic Education Board (SUBEB): ₦1.18 billion
• Office of Head of Service: ₦663.00 million
• Ministry of Budget and Economic Planning: ₦575.00 million
• Ministry for Basic Education: ₦550.00 million

✓ The agencies' rows add up exactly to the printed statewide totals.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 28, 31, 84, 89, 97, 104, 112, 113, 120, 127, 128, 134, 147, 149, 150, 151, 158; Budget Implementation Report Q2 2026, p. 31, 34
_Reply *show working* to see the rows and arithmetic._
```

## m31: not found (search, 14.9s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
I couldn't find the answer to that in the documents I have.
```

## m32: answered (lines:list, 11.6s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
For administration of justice (Law and Justice) in the 2026 approved budget, recurrent allocation is ₦2.46 billion for personnel plus ₦4.70 billion for other non-debt recurrent, and capital allocation is ₦7.10 billion. Within capital, renovation of 25No Upper and lower Sharia Courts is allocated ₦102.06 million and renovation of Hon Grand Khadi and Khadis residence houses is allocated ₦140.00 million. All figures are budgeted allocations, not spending.

• Law and Justice (code 030000000000) [Personnel Expenditure by Administrative Classification], 2026 Approved Budget: ₦2.46 billion
• Law and Justice (code 030000000000) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2026 Approved Budget: ₦4.70 billion
• Law and Justice (code 030000000000) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦7.10 billion
• Renovation of 25No Upper and lower Sharia Courts (Shari’a Court of Appeal), 2026 Approved Budget: ₦102.06 million
• Renovation of Hon Grand khadi and khadis Residence Houses (Shari’a Court of Appeal), 2026 Approved Budget: ₦140.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26, 63
_Reply *show working* to see the rows and arithmetic._
```

## m33: partial (lines:sum, 15.7s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
Security votes were allocated ₦5.50 billion in the 2025 approved budget and ₦8.21 billion in the 2026 approved budget, for a combined ₦13.71 billion (Kasafi's calculation). No separate line for contingency funds is shown, so they are not included.

• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2025 Approved Budget: ₦5.50 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion
• Not found: contingency funds

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 17; Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m34: not found (search, 9.4s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Ban sami amsar wannan tambayar a cikin takardun da nake da su ba.
```

## m35: answered WRONG: none of [['014800000000', '460,48'], ['014800100100', '460,48']] (lines:list, 14.8s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
The Sokoto State Independent Electoral Commission (SIEC) has a 2026 approved budget allocation of ₦460.48 million. This is the allocated (budgeted) amount for the Commission.

• Sokoto State Independent Electoral Commission (code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: partial (search, 28.8s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
No approved line item for that airport amount was shown in the excerpts; the Airways sector's 2026 approved budget (capital) is ₦36.00 billion.

• 2026 approved budget (total) for Ministry of Transport: ₦50.87 billion
• 2025 performance January to September (capital) for Airways: ₦12.34 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 47, 49, 58
```

## m37: answered (search, 10.2s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
Jimillar kuɗi da aka ware wa bangaren ICT and Innovation a 2025 ita ce ₦3.30 biliyan, daga shafi 24 na kasafin 2025. A 2026 jimillar ta kasance ₦7.15 biliyan, daga shafi 41 na kasafin 2026.

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 24; Sokoto State FY 2026 Budget, shafi 41
```

## m38: partial (search, 15.7s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Kasafin 2026 bai nuna kuɗi kai tsaye da aka ware wa Karamar Hukumar Wamakko a matsayin ƙaramar hukuma ba. Ƙaramar hukuma ba ma'aikatar jiha da ke cikinta ba ce, kuma ƙananan hukumomi suna karɓar rabon doka daban, don haka layin Asibitin Orthopedic Wamakko ba warewa ga ƙaramar hukumar ba ne. Abin da kasafin ya nuna shi ne kuɗin da aka kashe a yankin Wamakko, ba warewa ga majalisar ƙaramar hukumar ba.

• 2026 kasafin da aka amince (manyan ayyuka, yankin WAMAKKO): ₦82.18 biliyan
• 2026 kasafin da aka amince (albashi, yankin WAMAKKO): ₦609.75 miliyan
• 2026 kasafin da aka amince (manyan ayyuka, aikin asibiti Kasarawa Wamakko Local Government): ₦10.00 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 29, 38, 39, 67
```

## m39: answered (search, 25.9s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
The Ministry of Environment's capital execution rate was 48.6% of the revised budget (Q1–Q2 2026 only). The figure is from the Budget Implementation Report Q2 2026.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 28
```
