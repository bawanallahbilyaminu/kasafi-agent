# Open-question run: mid_tier.json

39 questions: answered 19, partial 14, not found 4, clarify 1, unverified 1 | wrong 1 of 11 checked (m37) | median 11.6s

```
plan          n=39 median   3.3s    25% of all time
line_search   n=31 median   1.2s     7% of all time
read          n=31 median   6.1s    39% of all time
read1         n=31 median   5.9s    38% of all time
read2         n=31 median   4.2s    26% of all time
reread        n= 7 median   4.1s     6% of all time
page_search   n=11 median   1.3s     3% of all time
compose       n=11 median   4.3s    11% of all time
answer        n=39 median   6.5s    50% of all time
row readings: 68 model calls for 31 questions (2 = no retry)
```

## m01: answered (lines:sum, 10.1s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
I, akwai kudaden tallafin karatu da aka ware wa dalibai a kasafin 2026. An ware ₦1.60 biliyan na Domestic Scholarship da ₦1.50 biliyan na Foreign Scholarship Scheme, dukkansu kudaden da aka amince (approved). Jimillarsu ₦3.10 biliyan (lissafin Kasafi).

• Domestic Scholarship (code 22021025), 2026 Approved Budget: ₦1.60 biliyan
• FOREIGN SCHOLARSHIP SCHEME (code 22021020), 2026 Approved Budget: ₦1.50 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m02: partial (lines:list, 15.1s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): (SUBEB) (2025 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: answered (lines:list, 9.6s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
The 2026 approved budget lists ₦2.03 billion for the School feeding programme and ₦2.00 billion for MEAL SUBSIDY TO GOVERNMENT SCHOOLS. It lists ₦11.26 billion for Increase in access, retention, and completion rate at all levels. The Girls Education Project monitoring and evaluation line is shown with 0.00 for 2026.

• Girls Education Project (11) with State to State (Ministry for Basic Education), 2026 Approved Budget: 0.00
• School feeding (programme inside a sector, all spending (total), code 050203), 2026 Approved Budget: ₦2.03 billion
• MEAL SUBSIDY TO GOVERNMENT SCHOOLS (code 22050102), 2026 Approved Budget: ₦2.00 billion
• Increase in access, retention, and completion rate at all levels (objective inside a sector, all spending (total), code 0502), 2026 Approved Budget: ₦11.26 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40, 41, 65, 149
_Reply *show working* to see the rows and arithmetic._
```

## m04: answered (lines:share, 19.4s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
The 2026 approved Total Expenditure is ₦758.70 billion. Health is allocated ₦120.13 billion. 15.8% (Kasafi's calculation) of the 2026 approved budget's Total Expenditure goes to health, compared with the Abuja Declaration benchmark.

• HEALTH (all spending (total), code 707), 2026 Approved Budget: ₦120.13 billion ↑
• Total Expenditure, 2026 Approved Budget: ₦758.70 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1, 32
_Reply *show working* to see the rows and arithmetic._
```

## m05: answered (category, 4.7s)

**Q:** Nawa aka ware wa sayen magunguna da kayan aiki na asibitoci a karkashin Ma'aikatar Lafiya a kasafin 2026?

```
_Ban ga wata shekara daban ba, don haka na yi amfani da kasafin 2026 mafi sabo._

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

## m06: partial (lines:list, 9.2s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
The 2026 approved budget provides ₦100.00 million as counterpart funding for PHC-MOU activities under the Primary Health Care Development Agency. This is the State's budgeted allocation for routine immunization and primary healthcare counterpart funding.

• Provision of support for PHC-MOU activities (Primary Health Care Development Agency), 2026 Approved Budget: ₦100.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health) (2026 Approved Budget); BHCF Counterpart Funds for SOCHEMA (Sokoto State contributory health care mgt agency) (2026 Approved Budget); Support for Family Planning Programme (Counterpart) (Primary Health Care Development Agency) (2026 Approved Budget); 04050126007201 - Functional health facilities Basic Health Care Provision Funds (BHCF) 25% Counterpart (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 70
_Reply *show working* to see the rows and arithmetic._
```

## m07: not found (search, 23.1s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m08: answered (category, 5.6s)

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

## m09: partial (lines:list, 14.8s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
The budget prints three specific capital project lines for irrigation schemes and tube wells. Kware irrigation scheme (SPIN Project) was ₦200.00 million in the 2025 Revised Budget and ₦800.00 million in the 2026 Approved Budget. Irrigation Scheme Youth empowerment (NEMI NA KANKA) was ₦200.00 million in the 2025 Revised Budget and ₦200.00 million in the 2026 Approved Budget. Construction of Tube Wells across the State was ₦531.96 million in the 2025 Revised Budget and 0.00 in the 2026 Approved Budget. No line is explicitly labelled as dry-season or as solar-powered tube wells.

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

## m10: partial (lines:list, 15.1s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
Eh, akwai kuɗaɗen da aka ware a kasafin 2026. An ware ₦54.56 miliyan don gyara da faɗaɗa madatsun ƙasa a Rafin Duma, da ₦226.01 miliyan don rijiyoyin famfo da bututun rarrabawa a faɗin Jihar, da ₦25.00 biliyan don gyaran ayyukan ruwan sha na birnin Sokoto. Dukkan waɗannan alkaluma kuɗaɗen da aka amince da su ne (approved), ba kuɗaɗen da aka kashe ba.

• Rehabilitation and expansion of earth dams at Rafin Duma (Ministry of Water Resources), 2026 Approved Budget: ₦54.56 miliyan
• boreholes, distribution pipes network across the State (Ministry of Water Resources), 2026 Approved Budget: ₦226.01 miliyan
• Rehabilitation of Sokoto Township Water Works (Water Board), 2026 Approved Budget: ₦25.00 biliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): Construction of Small Earth Dams at Kagara Isa LGA (Ministry of Water Resources) (2026 Approved Budget); Construction of Small Earth Dams at Kamarawa Isa LGA (Ministry of Water Resources) (2026 Approved Budget); Construction of Small Earth Dam at Chakai TBW LGA (Ministry of Water Resources) (2026 Approved Budget); through Construction Solar powered boreholes (Department for Rural Water) (2026 Approved Budget); Renovation of Boreholes across 40 wards in the State (Department for Special Projects) (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 58
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 7.1s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
The total 2026 approved allocation for livestock disease control, grazing reserves and veterinary services is ₦13.30 billion (Kasafi's calculation). It combines Animal health and livestock diseases management of ₦12.93 billion and Livestock feeds development of ₦368.05 million. Both figures are 2026 Approved Budget allocations for all spending.

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Livestock feeds development (programme inside a sector, all spending (total), code 010206), 2026 Approved Budget: ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40
_Reply *show working* to see the rows and arithmetic._
```

## m12: clarify (search, 13.2s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
I can read your question two ways. Which do you mean?
```

## m13: not found (search, 18.5s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m14: partial (lines:sum, 11.6s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
• Ba a haɗa su ba: a karatu na biyu ban tabbata waɗanne layuka ne ke cikin jimillar ba, don haka jimillar waɗannan kaɗai za ta iya ɓatarwa.

• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan
• Construction of 500 Housing units at Gidan Salanke (Min of Lands and Housing), 2026 Approved Budget: ₦4.00 biliyan
• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): Construction of 6 no Houses for 6 New Hon. Khadis in the State (Shari’a Court of Appeal) (2026 Approved Budget); Purchase of 500 units houses at Sokoto New City (Min of Lands and Housing) (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: partial (lines:list, 11.9s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
• INTER AND INTRA STATE TRANSPORTATION (SSTA) (Ministry of Transport), 2026 Approved Budget: ₦1.50 biliyan
• PURCHASE OF 20 NO TOYOTA 18-SEATER BUSES for SSTA (Ministry of Transport), 2026 Approved Budget: ₦2.40 biliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): Purchase of 300 Trycle bicycle for disable for ease transportation (Agency for Persons Living With Disabilities) (2026 Approved Budget); PURCHASE OF BUSES (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 55
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m16: partial (lines:list, 13.4s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
• INDEPENDENT REVENUE (code 12), 2025 Performance Year to Date (Q1-Q4): ₦20.58 billion
• INDEPENDENT REVENUE (code 12), 2026 Approved Budget: ₦74.52 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): INDEPENDENT REVENUE (2025 Final Budget); INDEPENDENT REVENUE (2025 Original Budget)

📄 *Sources:* Budget Implementation Report Q4 2025, p. 13; Sokoto State FY 2026 Budget, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## m17: answered (lines:ratio, 7.9s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
Capital Expenditure approved for 2026 is ₦553.34 billion and Recurrent Expenditure approved for 2026 is ₦205.36 billion. The exact ratio of Capital to Recurrent is 2.69 : 1 (Kasafi's calculation). Both figures are approved allocations, not spent amounts.

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (lines:list, 11.0s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
For 2026, Sokoto State budgeted ₦10.03 billion for domestic principal and ₦6.00 billion for domestic interest as domestic debt servicing. For external debt it budgeted ₦2.42 billion for foreign principal and ₦1.31 billion for foreign interest. All figures are 2026 Approved Budget allocations.

• DOMESTIC PRINCIPAl (code 220604), 2026 Approved Budget: ₦10.03 billion
• DOMESTIC INTEREST / DISCOUNT (code 220602), 2026 Approved Budget: ₦6.00 billion
• FOREIGN PRINCIPAL (code 220603), 2026 Approved Budget: ₦2.42 billion
• FOREIGN INTEREST / DISCOUNT (code 220601), 2026 Approved Budget: ₦1.31 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29
_Reply *show working* to see the rows and arithmetic._
```

## m19: answered (lines:compare, 9.0s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
The Office of the Executive Governor (Government House unit) was allocated ₦4.20 billion as overhead/running costs in the 2025 Approved Budget. It was allocated ₦3.71 billion as overhead/running costs in the 2026 Approved Budget. These are budgeted allocations for Government House's overhead, not spending.

• Government House (one agency or unit, overhead (running costs), code 011100100100), 2025 Approved Budget: ₦4.20 billion
• Government House (one agency or unit, overhead (running costs), code 011100100100), 2026 Approved Budget: ₦3.71 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 14; Sokoto State FY 2026 Budget, p. 21
_Reply *show working* to see the rows and arithmetic._
```

## m20: answered (search, 8.4s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa ƙarshen zangon farko (Q1) na 2026, an kashe 3.0% na kasafin babban aiki na daukacin jihar. Kasafin da aka amince da shi (manyan ayyuka) ₦553.34 biliyan ne, kuma abin da aka kashe a Q1 kawai ₦16.82 biliyan ne.

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 27
```

## m21: answered (query_budget:rank, 7.9s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
Ten administrative lines are tied for the lowest capital absorption at 0.0% of the 2026 revised budget in Q1–Q2 2026. The tied lines are Fiscal Responsibility Commission, Ministry for Skills Acquisition and Entrepreneurship Development, Ministry of Commerce and Industry, Ministry of Culture & Tourism, Ministry of Justice and Ministry of Solid Minerals and Natural Resources, Ministry for Local Government and Chieftancy, and Ministry for Special Duties, Sokoto State House of Assembly and Sokoto State Independent Electoral Commission.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 26, 27, 28
_Reply *show working* to see the rows and arithmetic._
```

## m22: answered (search, 9.7s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
The Ministry of Health's total release rate at end of Q2 2026 (Q1–Q2 only) was 10.6% of the revised budget. Its revised budget (allocated) was ₦116.91 billion and year-to-date spending (spent) was ₦12.36 billion. This is confirmed in the Total Expenditure by Administrative Classification table in the Budget Implementation Report Q2 2026, page 18.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## m23: answered (search, 8.1s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
2026 revised budget (personnel): ₦70.57 billion. January–June 2026 actual (personnel): ₦37.30 billion (52.8% of the revised budget), leaving a balance of ₦33.28 billion.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19
```

## m24: answered (category, 12.9s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
A kasafin 2026 da aka amince, a duk jihar: LOCAL TRAINING (22020501) ₦6.80 biliyan; GRANTS TO COMMUNITIES/NGOs (22040109) ₦7.03 biliyan; HUMANITARIAN AND SKILLS ACQUISITION CONSULTING (22020709) ₦70.00 miliyan, jimilla ₦13.90 biliyan (lissafin Kasafi). Ministry of Youth and Sports Development da hukumominta: ₦20.00 miliyan, 0.1% na jimillar jihar (lissafin Kasafi). Zuwa ƙarshen Yuni 2026, an kashe ₦2.12 biliyan daga ciki a duk jihar (15.3%, Budget Implementation Report Q2 2026).

Mafi girma:
• Ministry of Youth and Sports Development: ₦20.00 miliyan

✓ Layukan hukumomi sun yi daidai da jimillar jihar da aka buga.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 28, 29, 145; Budget Implementation Report Q2 2026, shafi 31, 32
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m25: partial (lines:list, 17.7s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
The 2026 approved budget includes ₦150.00 million for centres of Goronyo, Kware and Bodinga under the Agency for Persons Living With Disabilities, and ₦50.00 million  for therapeutic appliances and equipment. Both figures are allocated (budgeted), not spent. No separate, dedicated line for special schools is shown in the lines provided.

• centres of Goronyo, Kware and Bodinga (Agency for Persons Living With Disabilities), 2026 Approved Budget: ₦150.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): THERAPEUTIC APPLIANCES AND EQUIPTMENT (2026 Approved Budget); DISABILITY (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 64
_Reply *show working* to see the rows and arithmetic._
```

## m26: partial (lines:compare, 10.5s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
The budgeted provision for Women's Economic Empowerment was ₦4.94 billion in the 2025 Revised Budget and ₦3.15 billion in the 2026 Approved Budget. These are allocated (budgeted) amounts for the programme. No separate lines for orphanages and destitute homes were shown.

• Women's Economic Empowerment (programme inside a sector, all spending (total), code 230301) [Total Expenditure by Programme (Sector, Objective and Programme)], 2025 Revised Budget: ₦4.94 billion
• Women's Economic Empowerment (programme inside a sector, all spending (total), code 230301) [Total Expenditure by Programme (Sector, Objective and Programme)], 2026 Approved Budget: ₦3.15 billion
• Not found: orphanages, destitute homes

📄 *Sources:* Sokoto State FY 2026 Budget, p. 42
_Reply *show working* to see the rows and arithmetic._
```

## m27: partial (lines:list, 14.1s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
Babu layin da ya ware kudi daban don kananan hukumomin kan iyaka a kasafin 2026. Abin da aka nuna daban shi ne shirin raya karkara  da Shirin Rage Talauci. Kudaden da aka ware musu a 2026 su ne ₦0.00  da ₦2.24 biliyan (kasafin da aka amince).

• POVERTY REDUCTION PROGRAMME (hukuma ɗaya, duk kashe kuɗi (jimilla), code 011102000100), 2026 Approved Budget: ₦2.24 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): Integrated rural development (agricultural land development, farm mechanization, & rural infrastructures (2026 Approved Budget); Water Resources and Rural Development (2026 Approved Budget); Poverty Alleviation (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m28: partial (lines:list, 18.1s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
The 2026 approved personnel budget for all MDAs together is ₦70.57 billion. The lines show only this total personnel figure, with no separate line for the national minimum wage. So the figures alone do not say whether full implementation across all MDAs is included.

• Total Personnel Expenditure, 2026 Approved Budget: ₦70.57 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19
_Reply *show working* to see the rows and arithmetic._
```

## m29: answered (lines:compare, 11.0s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
Gwamnati ta ware ₦9.12 biliyan a kasafin 2025 don biyan gratuity ga tsofaffin ma’aikata. A kasafin 2026 ta ware ₦5.00 biliyan don wannan gratuity. Wadannan kudaden da aka ware (budgeted) ne, ba kudaden da aka kashe ba.

• GRATUITY (manyan ayyuka, code 21030101), 2025 Approved Budget: ₦9.12 biliyan
• GRATUITY (manyan ayyuka, code 21030101), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 27
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 10.3s)

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

## m31: partial (lines:list, 10.3s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
No separate approved 2026 line for the Sokoto State Community Guard Corps is shown. Internal security logistics support is shown as assistance to security agencies of ₦550.00 million and purchase of 250 motorcycles for Security Guards of ₦405.00 million, both allocated (budgeted) amounts.

• as assistance to security agencies in the state (SSG'S Office), 2026 Approved Budget: ₦550.00 million
• Purchase of 250 No Bajaj Motor cycle for Security Guards (Department for Security Matters), 2026 Approved Budget: ₦405.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): Department for Security Matters (2026 Approved Budget); SECURITY SERVICES (2026 Approved Budget); SECURITY VOTE (INCLUDING OPERATIONS) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 51, 52
_Reply *show working* to see the rows and arithmetic._
```

## m32: answered (lines:list, 11.3s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
For Law and Justice in the 2026 approved budget, the capital allocation is ₦7.10 billion. Recurrent allocation is personnel of ₦2.46 billion and overhead of ₦4.70 billion. Renovation of 25No Upper and lower Sharia Courts is allocated ₦102.06 million. All figures are allocated (budgeted), not spent.

• Law and Justice (ministry total including its agencies, capital, code 030000000000) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦7.10 billion
• Law and Justice (ministry total including its agencies, personnel (salaries), code 030000000000) [Personnel Expenditure by Administrative Classification], 2026 Approved Budget: ₦2.46 billion
• Law and Justice (ministry total including its agencies, overhead (running costs), code 030000000000) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2026 Approved Budget: ₦4.70 billion
• Renovation of 25No Upper and lower Sharia Courts (Shari’a Court of Appeal), 2026 Approved Budget: ₦102.06 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26, 63
_Reply *show working* to see the rows and arithmetic._
```

## m33: partial (lines:sum, 15.1s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
Security vote allocation is ₦5.50 billion for 2025 and ₦8.21 billion for 2026. Together this is ₦13.71 billion (Kasafi's calculation) in allocated security votes across the two years. No separate line for contingency funds is shown, so contingency could not be included.

• SECURITY VOTE (INCLUDING OPERATIONS) (capital, code 22020604), 2025 Approved Budget: ₦5.50 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion
• Not found: contingency funds

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 17; Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m34: not found (search, 23.6s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Ban sami amsar wannan tambayar a cikin takardun da nake da su ba.
```

## m35: answered (lines:list, 14.6s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
The Sokoto State Independent Electoral Commission's approved allocation is ₦460.48 million.

• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: unverified (search, 21.7s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
I found documents about your question, but couldn't verify the figures. Please check these sources:

[7] Sokoto State FY 2026 Budget, page 47
```

## m37: partial WRONG: none of [['3,301,437,040.18']] (search, 31.3s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
Jimillar kasafin 2026 da aka amince da shi wa ɓangaren Information Communication and Technology (jimilla) ₦7.15 biliyan ne, a shafi na 41. Takarda daya ta nuna kasafin 2025 da aka sabunta (jimilla) ₦5.29 biliyan ne. Ba a samu jimillar 2025 da aka amince da shi a cikin bayanan ba.

• 2026 kasafin da aka amince da shi (jimilla): ₦7.15 biliyan
• 2025 kasafin da aka sabunta (jimilla): ₦5.29 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 41
```

## m38: not found (search, 16.5s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Kasafin jihar bai nuna kuɗin da aka ware kai tsaye ga Ƙaramar Hukumar Wamakko ba. Layukan kasafin jiha na cibiyoyin da ke Wamakko (misali asibiti ko makaranta) kuɗin jiha ne, ba na ƙaramar hukumar ba. Ƙananan hukumomi suna samun kasonsu na doka daga asusun tarayya daban, kuma takardun da nake da su ba su nuna na Wamakko ba.
```

## m39: answered (lines:share, 10.9s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
• Share (↑ ÷ ↓): 48.6% (Kasafi's calculation)

• Ministry of Environment (ministry total including its agencies, capital, code 053500000000) [Capital Expenditure by Administrative Classification], 2026 Performance Year to Date (Q1-Q2): ₦7.86 billion ↑
• Ministry of Environment (ministry total including its agencies, capital, code 053500000000) [Capital Expenditure by Administrative Classification], 2026 Revised Budget: ₦16.17 billion ↓

📄 *Sources:* Budget Implementation Report Q2 2026, p. 28
_Reply *show working* to see the rows and arithmetic._
```
