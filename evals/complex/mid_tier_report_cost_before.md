# Open-question run: mid_tier.json

39 questions: partial 21, answered 17, not found 1 | wrong 0 of 11 checked | median 15.8s

```
plan          n=39 median   4.0s    27% of all time
line_search   n=34 median   2.1s    14% of all time
read          n=33 median   6.5s    37% of all time
read1         n=33 median   4.3s    24% of all time
read2         n=33 median   3.8s    23% of all time
reread        n= 7 median   5.4s     6% of all time
page_search   n=35 median   2.1s    11% of all time
compose       n=30 median   6.2s    32% of all time
answer        n=38 median   6.4s    46% of all time
row readings: 76 model calls for 33 questions (2 = no retry)
```

## m01: answered (lines:list, 14.3s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
• FOREIGN SCHOLARSHIP SCHEME (code 22021020), 2026 Approved Budget: ₦1.50 biliyan
• Domestic Scholarship (code 22021025), 2026 Approved Budget: ₦1.60 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m02: partial (lines:list, 20.0s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
SUBEB classroom construction in 2025 was allocated ₦4.55 billion plus ₦500.00 million. For school rehabilitation/repairs, ₦205.00 million was shown for 2025 (revised) and ₦205.00 million for 2026 approved. No 2026 SUBEB classroom construction line is shown in the lines provided.

• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦4.55 billion
• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦500.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million
• Not found: 2026 SUBEB classroom construction provision

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 29; Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: partial (lines:list, 24.3s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
The 2026 approved budget shows a Girls Education Project line at 0.00, a Girls secondary schools line at ₦45.00 million, a School feeding programme at ₦2.03 billion, and an Increase in access, retention, and completion rate objective at ₦11.26 billion. All figures are approved allocations, not spending.

• Girls Education Project (11) with State to State (Ministry for Basic Education), 2026 Approved Budget: 0.00
• Girls secondary schools (Female Education Board) – purchase of industrial equipment, 2026 Approved Budget: ₦45.00 million
• School feeding (programme inside a sector, all spending (total), code 050203), 2026 Approved Budget: ₦2.03 billion
• Increase in access, retention, and completion rate at all levels (objective inside a sector, all spending (total), code 0502), 2026 Approved Budget: ₦11.26 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): Female Education Board (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40, 41, 65, 67
_Reply *show working* to see the rows and arithmetic._
```

## m04: partial (lines:share, 16.7s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
The budget prints two totals for this, in different tables; the share of each:
• Health (sector total, all spending (total), code 04) [Total Expenditure by Programme (Sector, Objective and Programme)]: 15.7% (Kasafi's calculation)
• HEALTH (all spending (total), code 707) [Total Expenditure by Functional Classification]: 15.8% (Kasafi's calculation)

• Health (sector total, all spending (total), code 04), 2026 Approved Budget: ₦118.83 billion ↑
• HEALTH (all spending (total), code 707), 2026 Approved Budget: ₦120.13 billion ↑
• Total Expenditure (all spending (total)), 2026 Original Budget: ₦758.70 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 32, 40; Budget Implementation Report Q2 2026, p. 15
_Reply *show working* to see the rows and arithmetic._
```

## m05: answered (category, 6.3s)

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

## m06: partial (lines:list, 12.9s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
The 2026 approved counterpart funding allocation for routine immunization and primary healthcare (Provision of support for PHC-MOU activities) is ₦100.00 million. This figure is the approved budget allocation.

• Provision of support for PHC-MOU activities (Primary Health Care Development Agency), 2026 Approved Budget: ₦100.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 70
_Reply *show working* to see the rows and arithmetic._
```

## m07: partial (lines:list, 17.6s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
No line in the documents is exactly that (maternal and child healthcare centers across rural local government areas). The nearest lines they print (related, not the item itself):
• Ministry of Health (ministry total including its agencies, all spending (total), code 052100000000, Total Expenditure by Administrative Classification), 2026 Performance Year to Date (Q1-Q2): ₦12.36 billion [1]
• Ministry of Health (one agency or unit, all spending (total), code 052100100100, Total Expenditure by Administrative Classification), 2026 Performance Year to Date (Q1-Q2): ₦5.19 billion [1]
• 04050100000001 Primary Health Care (capital), 2026 Approved Budget: ₦5.89 billion [2]

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18; Sokoto State FY 2026 Budget, p. 48
```

## m08: answered (category, 8.9s)

**Q:** Nawa gwamnatin jihar Sokoto ta ware don sayen takin zamani da tallafin kayan noma a shekarar 2026, kuma nawa aka riga aka kashe?

```
_Na yi amfani da kasafin 2026 da aka amince da shi don warewa, da rahoton aiwatarwa na kwata na 2 na 2026 don abin da aka kashe zuwa yanzu._

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

## m09: partial (lines:list, 21.6s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
The budgets show two irrigation-scheme line items and one tube-wells line item, all capital. Irrigation Scheme Youth empowerment (NEMI NA KANKA) was allocated ₦200.00 million in 2025 and ₦200.00 million in 2026. Kware irrigation scheme (SPIN Project) was allocated ₦200.00 million in 2025 and ₦800.00 million in 2026. Construction of Tube Wells across the State was allocated ₦531.96 million in 2025 and 0.00 in 2026; no line item describes them as solar-powered.

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

## m10: partial (lines:list, 17.5s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
_Ban ga wani kasafin ba, don haka na yi amfani da kasafin 2026 da aka amince._

Akwai kudaden da aka ware don ruwan sha a cikin birnin Sokoto a kasafin 2026, amma ba a nuna gyaran madatsar ruwa a cikin birnin da kanta ba. An ware ₦35.00 miliyan don gyaran manyan tankunan ruwa a cikin Sokoto Metropolis da kuma ₦25.00 biliyan don gyaran Aikin Ruwan Garin Sokoto (Sokoto Township Water Works), duka kudaden da aka amince da su na 2026 ne.

• Rehabilitation of Overhead Tanks within Sokoto Metropolis (Water Board), 2026 Approved Budget: ₦35.00 miliyan
• Rehabilitation of Sokoto Township Water Works (Water Board), 2026 Approved Budget: ₦25.00 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 58
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 11.2s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
The total 2026 approved allocation for animal health/livestock diseases management and livestock feeds development is ₦13.30 billion (Kasafi's calculation). This covers disease control and veterinary services plus grazing reserves/feeds.

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Livestock feeds development (programme inside a sector, all spending (total), code 010206), 2026 Approved Budget: ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40
_Reply *show working* to see the rows and arithmetic._
```

## m12: partial (lines:list, 20.1s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
The 2026 approved capital budget shows ₦2.25 billion for construction/provision of roads under the Department for Rural Roads and ₦200.00 million for rehabilitation/repairs of roads for existing rural roads projects. No separate lines for flyovers or inner-city dualization are shown.

• Department for Rural Roads (code 023405700100) – construction / provision of roads, 2026 Approved Budget: ₦2.25 billion
• Rehabilitation of existing projects under rural roads (Department for Rural Roads), 2026 Approved Budget: ₦200.00 million
• Not found: flyovers, inner-city dualization

📄 *Sources:* Sokoto State FY 2026 Budget, p. 56
_Reply *show working* to see the rows and arithmetic._
```

## m13: not found (search, 14.1s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m14: partial (lines:sum, 16.6s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
• Ba a haɗa su ba: a karatu na biyu ban tabbata waɗanne layuka ne ke cikin jimillar ba, don haka jimillar waɗannan kaɗai za ta iya ɓatarwa.

• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan
• Construction of 500 Housing units at Gidan Salanke (Min of Lands and Housing), 2026 Approved Budget: ₦4.00 biliyan
• Construction of 6 no Houses for 6 New Hon. Khadis in the State (Shari’a Court of Appeal), 2026 Approved Budget: ₦51.00 miliyan
• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): Arkilla Federal Low cost Housing (Ministry for Basic Education) (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 63, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: partial (lines:list, 17.4s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
Eh, akwai kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a. An ware ₦1.50 biliyan don sufurin jihohi na SSTA, da ₦2.40 biliyan don siyan motocin bas 20 na SSTA, da ₦140.00 miliyan don siyan babura masu kafa uku 300 ga nakasassu don saukaka sufuri. Wadannan kudaden da aka ware (budgeted) ne, ba kashewa ba.

• INTER AND INTRA STATE TRANSPORTATION (SSTA) (Ministry of Transport), 2026 Approved Budget: ₦1.50 biliyan
• PURCHASE OF 20 NO TOYOTA 18-SEATER BUSES for SSTA (Ministry of Transport), 2026 Approved Budget: ₦2.40 biliyan
• Purchase of 300 Trycle bicycle for disable for ease transportation (Agency for Persons Living With Disabilities), 2026 Approved Budget: ₦140.00 miliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): PURCHASE OF BUSES (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 55, 64
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m16: answered (search, 15.8s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
The State Government projected ₦47.44 billion as 2025 IGR, later revised to ₦47.94 billion, collected ₦20.58 billion in Q1–Q4 2025 (42.9% of the final budget), and set ₦74.52 billion as the 2026 IGR target.

📄 *Sources:* Budget Implementation Report Q4 2025, p. 9; Sokoto State Government 2025 Approved Budget, p. 1; Sokoto State FY 2026 Budget, p. 1
```

## m17: answered (lines:ratio, 13.6s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
The approved 2026 budget provides ₦553.34 billion for Capital Expenditure and ₦205.36 billion for Recurrent Expenditure. The exact ratio of Capital to Recurrent is 2.69 : 1 (Kasafi's calculation).

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (lines:list, 14.1s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
Sokoto State earmarked ₦10.03 billion for domestic principal plus ₦6.00 billion for domestic interest in the 2026 Approved Budget. For external debt it earmarked ₦2.42 billion for foreign principal plus ₦1.31 billion for foreign interest. All figures are budgeted allocations, not spent amounts.

• DOMESTIC PRINCIPAl (code 220604), 2026 Approved Budget: ₦10.03 billion
• DOMESTIC INTEREST / DISCOUNT (code 220602), 2026 Approved Budget: ₦6.00 billion
• FOREIGN PRINCIPAL (code 220603), 2026 Approved Budget: ₦2.42 billion
• FOREIGN INTEREST / DISCOUNT (code 220601), 2026 Approved Budget: ₦1.31 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29
_Reply *show working* to see the rows and arithmetic._
```

## m19: answered (lines:compare, 16.4s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
_Assumption: used approved budgets for 2025 and 2026._

• Difference (2026 Approved Budget vs 2025 Approved Budget): -₦489.02 million (-11.6%) (Kasafi's calculation)

• Government House (one agency or unit, overhead (running costs), code 011100100100), 2025 Approved Budget: ₦4.20 billion
• Government House (one agency or unit, overhead (running costs), code 011100100100), 2026 Approved Budget: ₦3.71 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 14; Sokoto State FY 2026 Budget, p. 21
_Reply *show working* to see the rows and arithmetic._
```

## m20: answered (search, 20.1s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa karshen Q1 na 2026, 3.0% na kasafin manyan ayyuka na daukacin jihar aka riga aka kashe. Kasafin da aka amince da shi (manyan ayyuka) ₦553.34 biliyan ne. Abin da aka kashe a Q1 2026 kaɗai (manyan ayyuka) ₦16.82 biliyan ne.

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 5, 27
```

## m21: answered (query_budget:rank, 11.3s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
Ten MDAs are tied for the lowest capital absorption at 0.0% in Q1–Q2 2026, so no distinct three ministries can be named.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 26, 27, 28
_Reply *show working* to see the rows and arithmetic._
```

## m22: answered (search, 21.8s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
The actual release rate for the Ministry of Health at the end of Q2 2026 was 10.6% of the revised budget. This is confirmed in the Budget Implementation Report Q2 2026 on page 18.

• 2026 revised budget (total): ₦116.91 billion
• Q1-Q2 2026 spent (total, January-June 2026 only): ₦12.36 billion (10.6% of the revised budget)
• Q2 2026 spent (total): ₦5.67 billion

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## m23: answered (search, 14.9s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
The 2026 personnel budget was ₦70.57 billion. Actual payroll for Q1–Q2 2026 was ₦37.30 billion (52.8% of the revised budget). The variance (balance against revised budget) was ₦33.28 billion.

• 2026 revised budget (personnel): ₦70.57 billion
• Q1–Q2 2026 actual (personnel): ₦37.30 billion (52.8% of the revised budget)
• Variance / balance (personnel): ₦33.28 billion

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19
```

## m24: partial (lines:list, 15.1s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Babu layin kasafin kudi da aka ware daban don horar da matasa sana'o'i da tallafin kudi a karkashin Ma'aikatar Matasa da Wasanni a cikin takardun da aka bayar. Jimillar kasafin Ma'aikatar Matasa da Wasanni (da hukumominta) da aka amince da ita a 2026 ita ce ₦17.06 biliyan (jimilla da aka ware, ba na aikin horarwa kadai ba).

• Ministry of Youth and Sports Development (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 051300000000), 2026 Approved Budget: ₦17.06 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m25: partial (lines:list, 22.0s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
• THERAPEUTIC APPLIANCES AND EQUIPTMENT (code 70713), 2026 Approved Budget: ₦50.00 million
• Raji Special School (Ministry for Basic Education), 2026 Approved Budget: ₦500.00 million
• DISABILITY (all spending (total), code 71012), 2026 Approved Budget: ₦3.07 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): DISABILITY (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 33, 65, 188
_Reply *show working* to see the rows and arithmetic._
```

## m26: partial (lines:list, 16.5s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
The Women's Economic Empowerment programme was provided ₦4.94 billion for 2025 (revised) and ₦3.15 billion for 2026 (approved). No separate lines for orphanages and destitute homes are shown in the documents.

• Women's Economic Empowerment (programme inside a sector, all spending (total), code 230301) [Total Expenditure by Programme (Sector, Objective and Programme)], 2025 Revised Budget: ₦4.94 billion
• Women's Economic Empowerment (programme inside a sector, all spending (total), code 230301) [Total Expenditure by Programme (Sector, Objective and Programme)], 2026 Approved Budget: ₦3.15 billion
• Not found: orphanages, destitute homes

📄 *Sources:* Sokoto State FY 2026 Budget, p. 42
_Reply *show working* to see the rows and arithmetic._
```

## m27: partial (lines:list, 20.9s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• Water Resources and Rural Development (sector total, all spending (total), code 10), 2026 Approved Budget: ₦44.37 biliyan [1]
• Poverty Alleviation (sector total, all spending (total), code 03), 2026 Approved Budget: ₦6.10 biliyan [2]
• Integrated rural development (agricultural land development, farm mechanization, & rural infrastructures (programme inside a sector, all spending (total), code 010701), 2026 Approved Budget: 0.00 [2]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 40, 41
```

## m28: partial (search, 12.4s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
The 2026 approved personnel budget is ₦70.57 billion (allocated). Spending in Q1–Q2 2026 was ₦37.30 billion (52.8% of the revised budget) (January–June 2026 only). The evidence does not state whether this incorporates full minimum wage implementation across MDAs.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 19; Budget Implementation Report Q2 2026, p. 30
```

## m29: answered (lines:list, 10.7s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
A kasafin 2025 da aka amince da shi, an ware ₦5.67 biliyan don fansho (pension) da ₦9.12 biliyan don garatuti (gratuity). A kasafin 2026 da aka amince da shi, an ware ₦5.27 biliyan don fansho da ₦5.00 biliyan don garatuti. Wadannan alkaluma kudin da aka ware ne (budgeted), ba kudin da aka kashe ba.

• PENSION (manyan ayyuka, code 21030102), 2025 Approved Budget: ₦5.67 biliyan
• GRATUITY (code 21030101), 2025 Original Budget: ₦9.12 biliyan
• PENSION (code 21030102), 2026 Original Budget: ₦5.27 biliyan
• Gratuity (shiri cikin ɓangare, duk kashe kuɗi (jimilla), code 230502), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Budget Implementation Report Q4 2025, shafi 32; Budget Implementation Report Q2 2026, shafi 30; Sokoto State FY 2026 Budget, shafi 42
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 9.5s)

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

## m31: partial (lines:list, 12.8s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
No separate approved 2026 budget line for the Sokoto State Community Guard Corps or internal security logistics support is shown separately. The closest budgets printed are the Department for Security Matters capital budget of ₦8.30 billion and the SECURITY SERVICES economic classification budget of ₦8.62 billion, both of which are broader totals that would include internal security spending.

• Department for Security Matters (one agency or unit, capital, code 017000100200), 2026 Approved Budget: ₦8.30 billion
• SECURITY SERVICES (code 22020601), 2026 Approved Budget: ₦8.62 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 25, 28
_Reply *show working* to see the rows and arithmetic._
```

## m32: partial (lines:list, 22.6s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
No line in the documents is exactly that (administration of justice, renovation of Shari'ah courts). The nearest lines they print (related, not the item itself):
• Law and Justice (ministry total including its agencies, capital, code 030000000000, Capital Expenditure by Administrative Classification), 2026 Approved Budget: ₦7.10 billion [1]
• Law and Justice (ministry total including its agencies, personnel (salaries), code 030000000000, Personnel Expenditure by Administrative Classification), 2026 Approved Budget: ₦2.46 billion [2]
• Law and Justice (ministry total including its agencies, overhead (running costs), code 030000000000, Other Non-Debt Recurrent Expenditure by Administrative Classification), 2026 Approved Budget: ₦4.70 billion [3]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## m33: partial (lines:sum, 18.2s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
The allocated Security Vote is ₦5.50 billion for 2025 and ₦8.21 billion for 2026, for a combined ₦13.71 billion (Kasafi's calculation). No separate line for contingency funds is shown, so it is not included.

• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2025 Original Budget: ₦5.50 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion
• Not found: contingency funds

📄 *Sources:* Budget Implementation Report Q4 2025, p. 33; Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m34: partial (lines:list, 12.1s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• RECREATION, CULTURE AND RELIGION (all spending (total), code 708), 2026 Approved Budget: ₦34.81 biliyan [1]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 32
```

## m35: answered (lines:list, 12.6s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: partial (lines:list, 12.9s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Airways (sector total, capital, code 18), 2026 Approved Budget: ₦36.00 billion [1]
• PURCHASE OF AEROPLANE (code 23010143), 2026 Approved Budget: ₦36.00 billion [2]
• Airways - General (programme inside a sector, capital, code 181001), 2026 Approved Budget: ₦36.00 billion [1]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 47, 126
```

## m37: answered (lines:list, 18.9s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
Jimillar kudin da aka ware wa bangaren Information Communication and Technology a kasafin 2025 da aka amince da shi shi ne ₦3.30 biliyan. A kasafin 2026 da aka amince da shi kuma jimillar bangaren ta kai ₦7.15 biliyan. Wadannan alkaluma duka kudaden da aka ware ne, ba kashewa ba.

• Information Communication and Technology (jimillar ɓangare, duk kashe kuɗi (jimilla), code 11), 2025 Approved Budget: ₦3.30 biliyan
• Information Communication and Technology (jimillar ɓangare, duk kashe kuɗi (jimilla), code 11), 2026 Approved Budget: ₦7.15 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 24; Sokoto State FY 2026 Budget, shafi 41
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m38: partial (lines:list, 18.1s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• Kasarawa Wamakko Local Government (Ministry of Health), 2026 Approved Budget: ₦10.00 biliyan [1]
• Total Expenditure (all spending (total)), 2026 Approved Budget: ₦758.70 biliyan [2]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 67
```

## m39: answered (search, 4.3s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
*Ministry of Environment* (code 053500000000):
• Capital: share of the revised budget spent 48.6% (Kasafi's calculation)
• Total: share of the revised budget spent 47.0% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18, 28
```
