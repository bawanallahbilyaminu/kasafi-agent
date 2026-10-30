# Open-question run: mid_tier.json

39 questions: answered 20, partial 17, unverified 1, not found 1 | wrong 1 of 11 checked (m37) | median 14.1s

```
plan          n=39 median   3.6s    26% of all time
line_search   n=33 median   2.2s    15% of all time
read          n=30 median   6.6s    39% of all time
read1         n=30 median   3.7s    24% of all time
read2         n=30 median   3.8s    22% of all time
reread        n= 5 median   5.4s     5% of all time
page_search   n=34 median   2.2s    13% of all time
compose       n=31 median   3.3s    19% of all time
answer        n=37 median   6.2s    46% of all time
row readings: 69 model calls for 30 questions (2 = no retry)
```

## m01: answered (lines:list, 18.3s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
I, akwai kudaden tallafin karatu da aka ware wa dalibai a kasafin 2026. An ware ₦1.60 biliyan ga Domestic Scholarship da ₦1.50 biliyan ga FOREIGN SCHOLARSHIP SCHEME a matsayin kasafin da aka amince da shi (approved).

• Domestic Scholarship (code 22021025), 2026 Approved Budget: ₦1.60 biliyan
• FOREIGN SCHOLARSHIP SCHEME (code 22021020), 2026 Approved Budget: ₦1.50 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m02: partial (lines:compare, 22.2s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
SUBEB's renovation of public schools was allocated ₦205.00 million for 2025 (Revised Budget) and ₦205.00 million for 2026 (Approved Budget). No SUBEB classroom construction line is shown in the lines provided.

• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million
• Not found: SUBEB primary school classroom construction

📄 *Sources:* Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: answered (lines:list, 13.9s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
The 2026 approved budget shows a Girls Education Project line at 0.00, a School feeding programme at ₦2.03 billion, a Meal Subsidy to Government Schools at ₦2.00 billion, and an access, retention and completion objective at ₦11.26 billion. These are allocated (budgeted) amounts, not spent amounts.

• Girls Education Project (11) with State to State (Ministry for Basic Education), 2026 Approved Budget: 0.00
• School feeding (programme inside a sector, all spending (total), code 050203), 2026 Approved Budget: ₦2.03 billion
• Increase in access, retention, and completion rate at all levels (objective inside a sector, all spending (total), code 0502), 2026 Approved Budget: ₦11.26 billion
• MEAL SUBSIDY TO GOVERNMENT SCHOOLS (code 22050102), 2026 Approved Budget: ₦2.00 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40, 41, 65, 149
_Reply *show working* to see the rows and arithmetic._
```

## m04: partial (lines:share, 18.8s)

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

## m05: answered (category, 7.7s)

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

## m06: partial (lines:sum, 14.2s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
• Not added up: on a second reading I wasn't sure which lines belong in the total, so a total of these alone could mislead.

• Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health), 2026 Approved Budget: ₦70.00 million
• 04050126007201 - Functional health facilities Basic Health Care Provision Funds (BHCF) 25% Counterpart, 2026 Approved Budget: ₦109.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): BHCF Counterpart Funds for SOCHEMA (Sokoto State contributory health care mgt agency) (2026 Approved Budget); Support for Family Planning Programme (Counterpart) (Primary Health Care Development Agency) (2026 Approved Budget); 04050124000403 - Functional health facilities BHCF Counterpart Funds for SOCHEMA (2026 Approved Budget); 04050124008401 - Functional health facilities Support for Family Planning Programme (Counterpart) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 67, 229
_Reply *show working* to see the rows and arithmetic._
```

## m07: partial (lines:list, 19.7s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Ministry of Health (ministry total including its agencies, all spending (total), code 052100000000), 2026 Performance Year to Date (Q1-Q2): ₦12.36 billion [1]
• REHABILITATION / REPAIRS - HOSPITAL / HEALTH CENTRES (code 23030105), 2026 Performance Year to Date (Q1-Q2): ₦41.81 million [2]
• CONSTRUCTION / PROVISION OF HOSPITALS / HEALTH CENTRES (code 23020106), 2026 Performance Year to Date (Q1-Q2): ₦200.38 million [3]

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18, 33, 53
```

## m08: answered (category, 6.9s)

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

## m09: partial (lines:list, 23.8s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
The budgets show two irrigation-scheme line items and one tube-wells line item. Kware irrigation scheme (SPIN Project) is allocated ₦200.00 million for 2025 and ₦800.00 million for 2026. Irrigation Scheme Youth empowerment (NEMI NA KANKA) is allocated ₦200.00 million for 2025 and ₦200.00 million for 2026. Construction of Tube Wells across the State is allocated ₦531.96 million for 2025 and 0.00 for 2026. No line item for solar-powered tube wells is shown.

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

## m10: answered (lines:list, 16.3s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
I, an ware kudade don gyaran madatsar ruwa da ruwan famfo a kasafin 2026. Gyaran madatsar ruwa ta Rafin Duma na da ₦54.56 miliyan da aka ware, gyaran ayyukan ruwan birnin Sokoto na da ₦25.00 biliyan da aka ware, gyaran manyan tankunan ruwa a cikin birnin Sokoto na da ₦35.00 miliyan da aka ware. Duka kudaden da aka ware ne na 2026, ba kudin da aka kashe ba.

• Rehabilitation and expansion of earth dams at Rafin Duma (Ministry of Water Resources), 2026 Approved Budget: ₦54.56 miliyan
• Rehabilitation of Sokoto Township Water Works (Water Board), 2026 Approved Budget: ₦25.00 biliyan
• Rehabilitation of Overhead Tanks within Sokoto Metropolis (Water Board), 2026 Approved Budget: ₦35.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 58
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 12.4s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
The combined 2026 approved allocation for animal health/livestock diseases and livestock feeds development is ₦13.30 billion (Kasafi's calculation). This covers livestock disease control and veterinary services and grazing reserves under livestock feeds development.

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Livestock feeds development (programme inside a sector, all spending (total), code 010206), 2026 Approved Budget: ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40
_Reply *show working* to see the rows and arithmetic._
```

## m12: partial (lines:list, 18.9s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
No capital lines for flyovers or inner-city dualization under Ministry of Works are shown. For rural feeder roads under the Department for Rural Roads, the 2026 approved capital breakdown shown is: Construction / Provision of Roads, Rehabilitation of existing projects, Rural Roads through RAMP, Marketing Project / SEED Fund for RARA and State Road Fund, and tarring across the state. All figures are approved allocations for 2026, not spending.

• Department for Rural Roads (code 023405700100) – construction / provision of roads, 2026 Approved Budget: ₦2.25 billion
• Rehabilitation of existing projects under rural roads (Department for Rural Roads), 2026 Approved Budget: ₦200.00 million
• 17100125000200 - Road - General Construction of Rural Roads through Rural access and mobility projects (RAMP), 2026 Approved Budget: ₦7.90 billion
• Marketing Project/ SEED Fund for RARA and State Road Fund (SRS) (Department for Rural Roads), 2026 Approved Budget: ₦4.71 billion
• (tarring) across the state (Department for Rural Roads), 2026 Approved Budget: ₦209.11 million
• Not found: flyovers, inner-city dualization

📄 *Sources:* Sokoto State FY 2026 Budget, p. 56, 57, 217
_Reply *show working* to see the rows and arithmetic._
```

## m13: partial (lines:list, 15.7s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Ministry of Justice 032600100100 12020417 CONTRACTOR REGISTRATION FEES, 2025 Revised Budget: ₦550,000.00 [1]
• Supervision and Monitoring of Capital Projects (code 22021024), 2026 Approved Budget: 0.00 [2]

📄 *Sources:* Sokoto State Government 2025 Amended Budget, p. 17; Sokoto State FY 2026 Budget, p. 77
```

## m14: answered (lines:sum, 13.5s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
An ware ₦6.38 biliyan (lissafin Kasafi) a kasafin kudin 2026 da aka amince don gina sabbin gidajen ma’aikata da gidajen matsakaici. Wannan kuɗi ne da aka ware (budgeted), ba wanda aka kashe ba. Ya haɗa da gina rukunin gidaje 500 a Gidan Salanke, da rukunin gidaje 500 a Wajekke, Wamakko, da kammala gidan ma’aikata 53 a Jami’ar Jihar Sakkwato.

• Construction of 500 Housing units at Gidan Salanke (Min of Lands and Housing), 2026 Approved Budget: ₦4.00 biliyan
• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan
• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: answered (search, 14.9s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
Eh, akwai kuɗi da aka ware a kasafin 2026 don saukaka sufurin jama'a. An ware ₦1.50 biliyan don sayen motocin bas na sufuri tsakanin jihohi da cikin jihar a ƙarƙashin Ma'aikatar Sufuri. Jimillar kasafin Ma'aikatar Sufuri da aka amince da ita na 2026 ita ce ₦50.87 biliyan.

• 2026 kasafin da aka amince da shi (jimilla) Ma'aikatar Sufuri: ₦50.87 biliyan
• 2026 kasafin da aka amince da shi (manyan ayyuka) Ma'aikatar Sufuri: ₦47.67 biliyan
• 2026 kasafin da aka amince da shi (manyan ayyuka) sayen motocin bas (INTER AND INTRA STATE TRANSPORTATION SSTA): ₦1.50 biliyan
• 2026 kasafin da aka amince da shi (manyan ayyuka) sayen jiragen ruwa: ₦300.00 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26, 55
```

## m16: answered (search, 10.7s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
The projected Internally Generated Revenue (IGR) for 2025 in the approved budget was ₦47.44 billion. The final budget was ₦47.94 billion and actual collection for the full year (Q1–Q4 2025) was ₦20.58 billion (42.9% of the final budget). The target set for 2026 is ₦74.52 billion.

• 2025 approved budget (total): ₦47.44 billion
• 2025 final budget (total): ₦47.94 billion
• 2025 actual collection Q1–Q4 2025 (total): ₦20.58 billion (42.9% of the final budget)
• 2026 approved budget target (total): ₦74.52 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 7; Budget Implementation Report Q4 2025, p. 9, 13; Sokoto State FY 2026 Budget, p. 11
```

## m17: answered (lines:ratio, 12.1s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
The approved 2026 budget allocates ₦553.34 billion to Capital Expenditure and ₦205.36 billion to Recurrent Expenditure. The ratio of capital to recurrent is 2.69 : 1 (Kasafi's calculation).

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (lines:list, 14.0s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
• DOMESTIC INTEREST / DISCOUNT (code 220602), 2026 Approved Budget: ₦6.00 billion
• DOMESTIC PRINCIPAl (code 220604), 2026 Approved Budget: ₦10.03 billion
• FOREIGN PRINCIPAL (code 220603), 2026 Approved Budget: ₦2.42 billion
• FOREIGN INTEREST / DISCOUNT (code 220601), 2026 Approved Budget: ₦1.31 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29
_Reply *show working* to see the rows and arithmetic._
```

## m19: answered (lines:compare, 11.6s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
• Difference (2026 Approved Budget vs 2025 Approved Budget): -₦489.02 million (-11.6%) (Kasafi's calculation)

• Government House (one agency or unit, overhead (running costs), code 011100100100), 2025 Approved Budget: ₦4.20 billion
• Government House (one agency or unit, overhead (running costs), code 011100100100), 2026 Approved Budget: ₦3.71 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 14; Sokoto State FY 2026 Budget, p. 21
_Reply *show working* to see the rows and arithmetic._
```

## m20: answered (search, 15.0s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa ƙarshen Q1 na 2026, an kashe kashi 3.0% na kasafin babban aiki (capital) na daukacin jihar. Kasafin da aka amince da shi na 2026 (jimilla) shi ne ₦553.34 biliyan, an kashe ₦16.82 biliyan a Q1 kaɗai.

• 2026 kasafin babban aiki da aka amince da shi (jimilla): ₦553.34 biliyan
• Q1 2026 da aka kashe (Janairu–Maris, capital): ₦16.82 biliyan (3.0% na kasafin da aka amince da shi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 5, 27, 33, 43, 50
```

## m21: unverified (search, 10.5s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
I found documents about your question, but couldn't verify the figures. Please check these sources:

[1] Budget Implementation Report Q2 2026, page 27
[2] Budget Implementation Report Q2 2026, page 28
[3] Budget Implementation Report Q2 2026, page 26
```

## m22: answered (search, 4.6s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
*Ministry of Health* (code 052100000000):
• Total: share of the revised budget spent 10.6% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## m23: answered (search, 9.7s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
In the first half of 2026 (Q1–Q2), budgeted personnel expenditure was ₦70.57 billion. Actual payroll outturn through Q1–Q2 was ₦37.30 billion (52.8% of the revised budget). The remaining balance against the revised budget was ₦33.28 billion.

• 2026 revised budget (personnel): ₦70.57 billion
• 2026 Q1–Q2 actual (personnel, January–June only): ₦37.30 billion (52.8% of the revised budget)
• Balance (against revised budget): ₦33.28 billion

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19, 30, 38, 47
```

## m24: partial (lines:list, 16.3s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Babu layin da aka ware daban don horar da matasa sana'o'i da tallafin kudi a Ma'aikatar Matasa da Wasanni a 2026. Abin da aka buga kawai shi ne jimillar Ma'aikatar Matasa da Wasanni baki daya. Jimillar kasafin da aka amince da ita a 2026 na Ma'aikatar Matasa da Wasanni ita ce ₦17.06 biliyan.

• Ministry of Youth and Sports Development (ma'aikata tare da hukumominta, duk kashe kuɗi (jimilla), code 051300000000), 2026 Approved Budget: ₦17.06 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m25: partial (lines:list, 12.5s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
Yes, the 2026 budget shows dedicated lines: ₦50.00 million for therapeutic appliances and equipment, ₦500.00 million for Raji Special School rehabilitation, and ₦150.00 million for rehabilitation of centres of the Agency for Persons Living With Disabilities in Goronyo, Kware and Bodinga. All figures are 2026 approved allocations.

• THERAPEUTIC APPLIANCES AND EQUIPTMENT (code 70713), 2026 Approved Budget: ₦50.00 million
• Raji Special School (Ministry for Basic Education), 2026 Approved Budget: ₦500.00 million
• centres of Goronyo, Kware and Bodinga (Agency for Persons Living With Disabilities), 2026 Approved Budget: ₦150.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): DISABILITY (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 64, 65, 188
_Reply *show working* to see the rows and arithmetic._
```

## m26: partial (lines:list, 17.1s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
• Ministry for Women Affairs (ministry total including its agencies, all spending (total), code 051400000000), 2025 Approved Budget: ₦8.44 billion
• Ministry for Women Affairs (ministry total including its agencies, all spending (total), code 051400000000), 2026 Approved Budget: ₦7.24 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Possibly relevant too, not counted (I wasn't sure on a second reading): Ministry of Humanitarian Affairs & Social Welfare (2025 Approved Budget); Ministry of Humanitarian Affairs & Social Welfare (2026 Original Budget); Ministry of Social Welfare & Community Development (2025 Approved Budget); Ministry of Social Welfare & Community Development (2026 Original Budget)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
_Reply *show working* to see the rows and arithmetic._
```

## m27: partial (lines:sum, 13.2s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
_Ban ga wani bayani ba, don haka na yi amfani da kasafin 2026 da aka amince da shi._

Babu layin da ya ware kudi daban don ayyukan raya yankunan karkara da rage talauci a kananan hukumomin kan iyaka a takardun kasafin 2026. Abin da aka buga kawai shi ne jimillar bangarori: an ware ₦44.37 biliyan ga Water Resources and Rural Development da ₦6.10 biliyan ga Poverty Alleviation a matsayin kasafin 2026 da aka amince da shi, wanda ya kai ₦50.47 biliyan idan an hada su (lissafin Kasafi). Wadannan jimilloli na bangarori ne, ba kason da aka ware wa kananan hukumomin kan iyaka daban ba.

• Water Resources and Rural Development (jimillar ɓangare, duk kashe kuɗi (jimilla), code 10), 2026 Approved Budget: ₦44.37 biliyan
• Poverty Alleviation (jimillar ɓangare, duk kashe kuɗi (jimilla), code 03), 2026 Approved Budget: ₦6.10 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 40, 41
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m28: partial (search, 10.6s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
The approved personnel budget for 2026 is shown in the evidence, but the evidence does not say whether it incorporates the full financial implementation of the national minimum wage across all MDAs.

• 2026 approved budget (personnel): ₦70.57 billion
• 2026 approved budget (personnel): ₦70.57 billion
• 2026 approved budget (personnel): ₦70.57 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1, 19, 27
```

## m29: answered (lines:list, 14.9s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
Gwamnati ta ware ₦9.12 biliyan a kasafin 2025 da aka amince don biyan gratuity, da ₦5.00 biliyan a kasafin 2026 da aka amince don biyan gratuity ga tsofaffin ma’aikata. Wadannan kudaden da aka ware ne (budgeted), ba wanda aka kashe ba.

• GRATUITY (manyan ayyuka, code 21030101), 2025 Approved Budget: ₦9.12 biliyan
• GRATUITY (manyan ayyuka, code 21030101), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 27
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 9.4s)

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

## m31: partial (lines:list, 10.6s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Sokoto Marshal Corps (one agency or unit, overhead (running costs), code 012400700100), 2026 Original Budget: ₦1.13 billion [1]
• SECURITY SERVICES (code 22020601), 2026 Approved Budget: ₦8.62 billion [2]
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion [2]

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 23; Sokoto State FY 2026 Budget, p. 28
```

## m32: partial (lines:list, 24.5s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
• Ministry of Justice (ministry total including its agencies, overhead (running costs), code 032600000000) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2026 Approved Budget: ₦1.52 billion
• Ministry of Justice (ministry total including its agencies, personnel (salaries), code 032600000000) [Personnel Expenditure by Administrative Classification], 2026 Approved Budget: ₦864.15 million
• Renovation of 25No Upper and lower Sharia Courts (Shari’a Court of Appeal), 2026 Approved Budget: ₦102.06 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): Renovation of Hon Grand khadi and khadis Residence Houses (Shari’a Court of Appeal) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 24, 63
_Reply *show working* to see the rows and arithmetic._
```

## m33: partial (lines:sum, 18.1s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
The approved security vote is ₦5.50 billion for 2025 and ₦8.21 billion for 2026. Together this is ₦13.71 billion (Kasafi's calculation) in allocated expenditure. No contingency fund line is shown separately.

• SECURITY VOTE (INCLUDING OPERATIONS) (capital, code 22020604), 2025 Approved Budget: ₦5.50 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion
• Not found: contingency funds

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 17; Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m34: not found (search, 15.3s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Ban sami amsar wannan tambayar a cikin takardun da nake da su ba.
```

## m35: answered (lines:list, 15.0s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
The Sokoto State Independent Electoral Commission's 2026 approved allocation for total spending is ₦460.48 million.

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
• Airways - General (programme inside a sector, capital, code 181001), 2026 Approved Budget: ₦36.00 billion [1]
• PURCHASE OF AEROPLANE (code 23010143), 2026 Approved Budget: ₦36.00 billion [2]

📄 *Sources:* Sokoto State FY 2026 Budget, p. 47, 126
```

## m37: answered WRONG: none of [['3,301,437,040.18']] (search, 14.1s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
Jimillar kuɗin da aka ware wa ɓangaren Information Communication and Technology (ICT and Innovation) a 2025 (kasafin da aka sabunta) ita ce ₦5.29 biliyan, a 2026 (kasafin da aka amince) kuma ₦7.15 biliyan. Wannan bayani ya fito a shafi na 41 na kasafin 2026 inda aka jera jimillar kashe kuɗi ta fanni (Total Expenditure by Programme).

• 2025 (kasafin da aka sabunta, jimilla): ₦5.29 biliyan
• 2026 (kasafin da aka amince, jimilla): ₦7.15 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 41
```

## m38: partial (lines:list, 12.2s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Babu layi a takardun da yake daidai wannan. Layukan da suka fi kusa da shi (masu alaƙa, ba shi kansa ba):
• WAMAKKO (capital, code 33312100, Capital Expenditure by Functional Classification), 2026 Approved Budget: ₦82.18 biliyan [1]
• WAMAKKO (code 33312100, Personnel Expenditure by Location), 2026 Approved Budget: ₦79.98 biliyan [2]
• WAMAKKO (code 33312100, Personnel Expenditure by Location), 2026 Approved Budget: ₦1.60 biliyan [2]

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 38, 39
```

## m39: answered (search, 4.6s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
*Ministry of Environment* (code 053500000000):
• Capital: share of the revised budget spent 48.6% (Kasafi's calculation)
• Total: share of the revised budget spent 47.0% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18, 28
```
