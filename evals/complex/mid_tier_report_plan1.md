# Open-question run: mid_tier.json

39 questions: answered 19, partial 15, not found 4, clarify 1 | wrong 2 of 11 checked (m04, m10) | median 21.0s

```
plan          n=39 median   5.2s    24% of all time
line_search   n=33 median   1.1s     5% of all time
read          n=33 median  11.8s    48% of all time
read1         n=33 median  10.5s    45% of all time
read2         n=33 median   3.6s    16% of all time
reread        n= 7 median  12.2s    10% of all time
page_search   n=34 median   0.8s     4% of all time
compose       n=34 median   8.9s    36% of all time
answer        n=37 median  13.0s    55% of all time
row readings: 77 model calls for 33 questions (2 = no retry)
```

## m01: answered (lines:sum, 20.6s)

**Q:** Shin akwai kudaden alawus ko tallafin karatu (scholarships) da aka ware wa daliban jihar Sokoto a kasafin 2026, kuma nawa ne adadin?

```
_Na yi amfani da kasafin 2026 da aka amince da shi._

Eh, akwai kudaden tallafin karatu da aka ware a kasafin 2026 da aka amince. Tallafin cikin gida (Domestic Scholarship) ₦1.60 biliyan ne, tallafin kasashen waje (FOREIGN SCHOLARSHIP SCHEME) kuma ₦1.50 biliyan ne. Jimillarsu ₦3.10 biliyan (lissafin Kasafi). Dukkanin kudaden da aka ware (budgeted) ne.

• Domestic Scholarship (code 22021025), 2026 Approved Budget: ₦1.60 biliyan
• FOREIGN SCHOLARSHIP SCHEME (code 22021020), 2026 Approved Budget: ₦1.50 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 29
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m02: partial (lines:list, 43.1s)

**Q:** How much was allocated to the Sokoto State Universal Basic Education Board (SUBEB) for primary school classroom construction and renovation in 2025 versus 2026?

```
For SUBEB classroom construction, the 2025 approved budget shows ₦4.55 billion plus ₦500.00 million for CONSTRUCTION / PROVISION OF PUBLIC SCHOOLS. For rehabilitation/renovation of public schools, ₦205.00 million was shown as the 2025 Revised Budget and ₦205.00 million as the 2026 Approved Budget. The 2026 construction allocation for SUBEB is not shown in the lines provided.

• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦4.55 billion
• (SUBEB) – construction / provision of public schools [Basic Education Capital Expenditure by Project], 2025 Approved Budget: ₦500.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2025 Revised Budget: ₦205.00 million
• State Universal Basic Education Board (SUBEB) (code 051700300100) – rehabilitation / repairs - public schools [Capital Expenditure by Project], 2026 Approved Budget: ₦205.00 million
• Not found: 2026 SUBEB allocation for construction / provision of public schools / classrooms

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 29; Sokoto State FY 2026 Budget, p. 66
_Reply *show working* to see the rows and arithmetic._
```

## m03: partial (lines:list, 22.8s)

**Q:** What specific budget lines exist for girl-child education, boarding school feeding, and retention programs in the 2026 budget?

```
The 2026 approved budget shows Female Education Board at ₦1.16 billion for girl-child education. For feeding it shows School feeding programme at ₦2.03 billion and MEAL SUBSIDY TO GOVERNMENT SCHOOLS at ₦2.00 billion. For retention it shows the Increase in access, retention, and completion rate objective at ₦11.26 billion. All figures are approved allocations, not spending.

• Female Education Board (one agency or unit, all spending (total), code 051705700100), 2026 Approved Budget: ₦1.16 billion
• School feeding (programme inside a sector, all spending (total), code 050203), 2026 Approved Budget: ₦2.03 billion
• MEAL SUBSIDY TO GOVERNMENT SCHOOLS (code 22050102), 2026 Approved Budget: ₦2.00 billion
• Increase in access, retention, and completion rate at all levels (objective inside a sector, all spending (total), code 0502), 2026 Approved Budget: ₦11.26 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): Female Education Board (2026 Approved Budget); Girls Education Project (11) with State to State (Ministry for Basic Education) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 40, 41, 149
_Reply *show working* to see the rows and arithmetic._
```

## m04: partial WRONG: none of [['15.8']] (lines:share, 61.6s)

**Q:** What percentage of the overall 2026 Sokoto State budget is allocated to the health sector, and does it meet the 15% Abuja Declaration benchmark?

```
• Not added up: on a second reading I wasn't sure which lines belong in the total, so a total of these alone could mislead.

• Total Expenditure (capital), 2026 Approved Budget: ₦758.70 billion ↓
• Possibly relevant too, not counted (I wasn't sure on a second reading): Health (2026 Approved Budget); HEALTH (2026 Original Budget); Recurrent Expenditure (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 27
_Reply *show working* to see the rows and arithmetic._
```

## m05: answered (category, 7.9s)

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

## m06: partial (lines:sum, 23.0s)

**Q:** What is the exact counterpart funding allocation provided by Sokoto State for routine immunization and primary healthcare in the 2026 budget?

```
• Not added up: on a second reading I wasn't sure which lines belong in the total, so a total of these alone could mislead.

• Provision of support for PHC-MOU activities (Primary Health Care Development Agency), 2026 Approved Budget: ₦100.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): Counterpart Funds for Basic Health Care Provision Funds (BHCBF)- EMT (Ministry of Health) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 70
_Reply *show working* to see the rows and arithmetic._
```

## m07: not found (search, 37.5s)

**Q:** How much was released and spent for maternal and child healthcare centers across rural local government areas by Q2 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m08: answered (category, 9.0s)

**Q:** Nawa gwamnatin jihar Sokoto ta ware don sayen takin zamani da tallafin kayan noma a shekarar 2026, kuma nawa aka riga aka kashe?

```
_Na yi amfani da rahoton aiwatar da kasafin Q2 na 2026 don adadin da aka kashe, domin shi ne sabo da ake da shi._

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

## m09: partial (lines:list, 20.0s)

**Q:** What are the specific line-item capital allocations for dry-season irrigation schemes and solar-powered tube wells in the 2025 and 2026 budgets?

```
The budgets show separate capital lines for irrigation schemes and for tube wells, but no single line for solar-powered tube wells. Irrigation allocations shown are Kware irrigation scheme (SPIN Project), Irrigation Scheme Youth empowerment (NEMI NA KANKA) and intensive crop and vegetable production including irrigation, and tube wells are Construction of Tube Wells across the State. All figures below are allocated (budgeted), not spent.

• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Irrigation Scheme Youth empowerment,(NEMI NA KANKA) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2025 Revised Budget: ₦200.00 million
• Kware irrigation scheme (SPIN Project) (Ministry of Agriculture & Natural Resource) [Capital Expenditure by Project], 2026 Approved Budget: ₦800.00 million
• Construction of Tube Wells across the State (Nigeria CARES- Fadama Programme) [Capital Expenditure by Project], 2025 Revised Budget: ₦531.96 million
• … +3
• Possibly relevant too, not counted (I wasn't sure on a second reading): through Construction Solar powered boreholes (Department for Rural Water) (2025 Revised Budget); through Construction Solar powered boreholes (Department for Rural Water) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 45, 53
_Reply *show working* to see the rows and arithmetic._
```

## m10: partial WRONG: none of [['25,000,000,000.00']] (lines:list, 22.0s)

**Q:** Shin akwai kudaden da aka ware don gyaran madatsun ruwa da samar da ruwan famfo a cikin birnin Sokoto a kasafin 2026?

```
_Na yi amfani da kasafin 2026 da aka amince da shi._

Ba a nuna layin kasafin kudi dabam na gyaran madatsun ruwa da ruwan famfo a cikin birnin Sokoto a kasafin 2026 ba. Kudin da aka ware daban shi ne jimillar aikin Samar da Ruwa (WATER SUPPLY) gaba daya da aka tsara a kasafin 2026 ₦44.09 biliyan (Kasafin Kudi Amincewa). Wannan jimilla ce ta aikin ruwa baki daya, ba a ware kudaden madatsar ruwa ko ruwan famfo na birnin Sokoto daban ba.

• WATER SUPPLY (duk kashe kuɗi (jimilla), code 7063), 2026 Approved Budget: ₦44.09 biliyan
⚠️ Kasafin bai nuna wannan abu daban ba. Layin da ke sama jimilla ce mai faɗi; takardun ba su faɗi nawa daga cikinta ne, idan akwai, na wannan abu ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 32
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m11: answered (lines:sum, 19.9s)

**Q:** What is the total allocation for livestock disease control, grazing reserves, and veterinary services in the 2026 budget?

```
The 2026 approved allocation is ₦13.30 billion (Kasafi's calculation) for animal health and livestock diseases management plus livestock feeds development, which includes grazing reserves. These are programme totals covering all spending.

• Animal health and livestock diseases management (programme inside a sector, all spending (total), code 010205), 2026 Approved Budget: ₦12.93 billion
• Livestock feeds development (programme inside a sector, all spending (total), code 010206), 2026 Approved Budget: ₦368.05 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 40
_Reply *show working* to see the rows and arithmetic._
```

## m12: partial (lines:list, 23.5s)

**Q:** What is the capital expenditure breakdown for flyovers, inner-city dualization, and rural feeder roads under the Ministry of Works for 2026?

```
The 2026 approved capital budget for the Ministry of Works, as the ministry total including its agencies, is ₦58.13 billion. The budget lines do not show separate capital lines for flyovers, inner-city dualization or rural feeder roads, so a breakdown cannot be given. The figure above is allocated (budgeted), not spent.

• Ministry of Works (ministry total including its agencies, capital, code 023400000000), 2026 Approved Budget: ₦58.13 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.
• Possibly relevant too, not counted (I wasn't sure on a second reading): Ministry of Works (2026 Approved Budget); Department for Rural Roads (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 26
_Reply *show working* to see the rows and arithmetic._
```

## m13: not found (search, 20.4s)

**Q:** How much was budgeted for the payment of ongoing contractor liabilities and retention fees across MDAs in 2025 and 2026?

```
I couldn't find the answer to that in the documents I have.
```

## m14: answered (lines:sum, 17.4s)

**Q:** Nawa aka ware don gina sabbin gidajen ma’aikata ko matsakaitan masu karamin karfi a kasafin kudin 2026?

```
An ware ₦6.38 biliyan (lissafin Kasafi) don gina sabbin gidajen ma’aikata da gidajen masu karamin karfi a kasafin 2026. Dukkanin wa’annan kuɗaɗen da aka ware ne (budgeted) a cikin 2026 Approved Budget, ba kuɗaɗen da aka kashe ba.

• Construction of 500 Housing Estate at Wajekke, Wamakko (Min of Lands and Housing), 2026 Approved Budget: ₦2.00 biliyan
• Construction of 500 Housing units at Gidan Salanke (Min of Lands and Housing), 2026 Approved Budget: ₦4.00 biliyan
• Completion of staff quarters (53nos) Phase 1 (Sokoto State University), 2026 Approved Budget: ₦382.98 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 59, 74
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m15: partial (lines:list, 21.8s)

**Q:** Shin akwai wani shiri ko kudi da aka ware a kasafin 2026 don saukaka sufurin jama'a ko tallafin motocin bas a jihar?

```
• INTER AND INTRA STATE TRANSPORTATION (SSTA) (Ministry of Transport), 2026 Approved Budget: ₦1.50 biliyan
• PURCHASE OF 20 NO TOYOTA 18-SEATER BUSES for SSTA (Ministry of Transport), 2026 Approved Budget: ₦2.40 biliyan
• Watakila suna da alaƙa, ba a ƙidaya su ba (ban tabbata ba a karatu na biyu): Purchase of 300 Trycle bicycle for disable for ease transportation (Agency for Persons Living With Disabilities) (2026 Approved Budget); PURCHASE OF BUSES (2026 Approved Budget)

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 55
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m16: answered (search, 13.7s)

**Q:** What was the projected Internally Generated Revenue (IGR) for 2025 compared to actual collections, and what is the target set for 2026?

```
The 2025 IGR projection was ₦47.44 billion originally and ₦47.94 billion in the final budget. Actual collection for Q1–Q4 2025 was ₦20.58 billion, which is 42.9% of the final budget. The 2026 IGR target is ₦74.52 billion.

📄 *Sources:* Budget Implementation Report Q4 2025, p. 9; Sokoto State FY 2026 Budget, p. 1, 11
```

## m17: answered (lines:ratio, 18.0s)

**Q:** What is the exact ratio of Capital Expenditure to Recurrent Expenditure in Sokoto State’s approved 2026 budget?

```
The approved 2026 budget allocates ₦553.34 billion for Capital Expenditure and ₦205.36 billion for Recurrent Expenditure. These are both approved (budgeted) figures, not spending. The exact ratio of Capital to Recurrent is 2.69 : 1 (Kasafi's calculation).

• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 billion ↑
• Recurrent Expenditure, 2026 Approved Budget: ₦205.36 billion ↓

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m18: answered (lines:list, 20.5s)

**Q:** How much has Sokoto State earmarked for domestic debt servicing versus external debt deductions in the 2026 fiscal year?

```
For 2026, Sokoto State budgeted ₦10.03 billion for domestic principal and ₦6.00 billion for domestic interest / discount. For external deductions it budgeted ₦2.42 billion for foreign principal and ₦1.31 billion for foreign interest / discount. All figures are 2026 Approved Budget allocations, not actual spending.

• DOMESTIC PRINCIPAl (code 220604), 2026 Approved Budget: ₦10.03 billion
• DOMESTIC INTEREST / DISCOUNT (code 220602), 2026 Approved Budget: ₦6.00 billion
• FOREIGN PRINCIPAL (code 220603), 2026 Approved Budget: ₦2.42 billion
• FOREIGN INTEREST / DISCOUNT (code 220601), 2026 Approved Budget: ₦1.31 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 29
_Reply *show working* to see the rows and arithmetic._
```

## m19: answered (lines:compare, 28.9s)

**Q:** What is the total allocation for office running costs and overhead expenditures for the Office of the Executive Governor in 2025 versus 2026?

```
• Difference (2026 Approved Budget vs 2025 Revised Budget): -₦489.02 million (-11.6%) (Kasafi's calculation)

• Government House (one agency or unit, overhead (running costs), code 011100100100), 2025 Revised Budget: ₦4.20 billion
• Government House (one agency or unit, overhead (running costs), code 011100100100), 2026 Approved Budget: ₦3.71 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 21
_Reply *show working* to see the rows and arithmetic._
```

## m20: answered (search, 16.0s)

**Q:** Zuwa karshen zangon farko (Q1) na 2026, kashi nawa na kasafin babban aiki (capital expenditure) aka riga aka kashe a daukacin jihar?

```
Zuwa ƙarshen zangon farko (Q1) na 2026, an kashe 3.0% na kasafin manyan ayyuka na daukacin jihar.

• 2026 approved budget (capital): ₦553.34 biliyan
• Q1 2026 spent (capital) (Q1 2026 kawai): ₦16.82 biliyan

📄 *Madogara:* Sokoto State Budget Implementation Report Q1 2026, shafi 27
```

## m21: answered (query_budget:rank, 11.7s)

**Q:** Which three state ministries had the lowest capital budget absorption rates according to the Q2 2026 Budget Implementation Report?

```
Ten MDAs are tied for the lowest capital absorption rate at 0.0% in Q1–Q2 2026, so there is no unique bottom three. The seven ministries among them are Ministry for Skills Acquisition and Entrepreneurship Development, Ministry of Commerce and Industry, Ministry of Culture & Tourism, Ministry of Justice, Ministry of Solid Minerals and Natural Resources, Ministry for Local Government and Chieftancy, and Ministry for Special Duties, plus the Fiscal Responsibility Commission, Sokoto State House of Assembly and Sokoto State Independent Electoral Commission, all at 0.0%.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 26, 27, 28
_Reply *show working* to see the rows and arithmetic._
```

## m22: answered (search, 4.6s)

**Q:** What was the actual budget release rate for the Ministry of Health at the end of the second quarter of 2026, and what document and page confirms this?

```
*Ministry of Health* (code 052100000000):
• Total: spent so far (Q1–Q2) ₦12.36 billion; share of the revised budget spent 10.6% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 18
```

## m23: answered (search, 15.8s)

**Q:** What was the variance between budgeted personnel expenditure and actual payroll outturn through the first half of 2026?

```
The 2026 revised personnel budget (allocated) was ₦70.57 billion. Actual payroll for January–June 2026 (spent) was ₦37.30 billion (52.8% of the revised budget). The leftover balance (variance) was ₦33.28 billion.

📄 *Sources:* Budget Implementation Report Q2 2026, p. 19
```

## m24: partial (search, 53.4s)

**Q:** Nawa aka ware wa Ma’aikatar Matasa da Wasanni don horar da matasa sana’o’i da tallafin kudi a shekarar 2026?

```
Kasafin 2026 bai nuna kuɗin horar da matasa sana'o'i da tallafin kuɗi daban ba. Jimillar kasafin Ma'aikatar Matasa da Wasanni da aka amince da shi na 2026 (total) shi ne ₦17.06 biliyan. Wannan jimilla ce ta ma'aikata, ba adadin aikin horarwa da tallafi kaɗai ba.

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 26, 41, 63
```

## m25: partial (lines:list, 21.0s)

**Q:** Are there specific, dedicated budget lines for assistive devices, special schools, and welfare support for persons with disabilities in the 2026 budget?

```
The 2026 approved budget shows a total of ₦3.07 billion for the DISABILITY function. Within that, the only specific dedicated line for persons with disabilities shown is ₦150.00 million for rehabilitation of centres of Goronyo, Kware and Bodinga (Agency for Persons Living With Disabilities). No separate dedicated lines for assistive devices or special schools are shown; they would fall inside the broader disability total if budgeted.

• DISABILITY (all spending (total), code 71012), 2026 Approved Budget: ₦3.07 billion
• centres of Goronyo, Kware and Bodinga (Agency for Persons Living With Disabilities), 2026 Approved Budget: ₦150.00 million
• Possibly relevant too, not counted (I wasn't sure on a second reading): THERAPEUTIC APPLIANCES AND EQUIPTMENT (2026 Approved Budget); DISABILITY (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 33, 64
_Reply *show working* to see the rows and arithmetic._
```

## m26: clarify (search, 20.7s)

**Q:** What is the budgetary provision for women empowerment programs, orphanages, and destitute homes in 2025 and 2026?

```
I can read your question two ways. Which do you mean?
```

## m27: partial (search, 21.5s)

**Q:** Nawa aka ware a kasafin 2026 domin ayyukan raya yankunan karkara da rage radadin talauci a kananan hukumomin kan iyaka?

```
Kasafin 2026 bai nuna kuɗin ayyukan karkara da rage talauci na ƙananan hukumomin kan iyaka daban ba; jimillar fannin rage talauci da aka ware ₦6.10 biliyan ce, jimillar fannin ruwa da raya karkara kuma ₦44.37 biliyan ce. Ƙananan hukumomi suna karɓar rabon doka daban, ba a matsayin layin ma'aikata a kasafin jiha ba.

• 2026 kasafin da aka amince (jimilla) na Shirin Rage Talauci: ₦2.24 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 16, 40, 41
```

## m28: partial (lines:list, 15.7s)

**Q:** Does the personnel budget for 2026 incorporate the full financial implementation of the national minimum wage across all state MDAs?

```
The 2026 approved personnel budget is ₦70.57 billion (allocated, not spent). No separate line for national minimum wage implementation across MDAs is shown, so the tables alone do not confirm full implementation.

• PERSONNEL COST (code 21), 2026 Approved Budget: ₦70.57 billion
⚠️ The budget doesn't show this item separately. The line above is a broader total; the documents don't say how much of it, if any, is for this item.

📄 *Sources:* Sokoto State FY 2026 Budget, p. 1
_Reply *show working* to see the rows and arithmetic._
```

## m29: answered (lines:list, 24.3s)

**Q:** Nawa gwamnati ta ware a kasafin 2025 da 2026 don biyan bashin kudin sallama na fansho da garatuti (gratuity) ga tsofaffin ma’aikata?

```
Gwamnati ta ware ₦9.12 biliyan a kasafin 2025 da aka amince da shi don Gratuity, da kuma ₦5.00 biliyan a kasafin 2026 da aka amince da shi don Gratuity. Dukkanin kudaden kasafin da aka amince da su ne, ba kashewa ba.

• GRATUITY (manyan ayyuka, code 21030101), 2025 Approved Budget: ₦9.12 biliyan
• Gratuity (shiri cikin ɓangare, duk kashe kuɗi (jimilla), code 230502), 2026 Approved Budget: ₦5.00 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 17; Sokoto State FY 2026 Budget, shafi 42
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## m30: answered (category, 29.2s)

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

## m31: partial (lines:list, 24.1s)

**Q:** What is the approved 2026 budget line for the Sokoto State Community Guard Corps and internal security logistics support?

```
The approved 2026 budget includes ₦3.00 billion for purchase of motor vehicles for Guards (Department for Security Matters). This is the dedicated internal security logistics support line shown. It is an allocated (budgeted) amount, not spent.

• Guards (Department for Security Matters) – purchase of motor vehicles, 2026 Approved Budget: ₦3.00 billion
• Possibly relevant too, not counted (I wasn't sure on a second reading): SECURITY SERVICES (2026 Approved Budget); SECURITY VOTE (INCLUDING OPERATIONS) (2026 Approved Budget)

📄 *Sources:* Sokoto State FY 2026 Budget, p. 52
_Reply *show working* to see the rows and arithmetic._
```

## m32: answered (lines:list, 23.6s)

**Q:** What is the capital and recurrent allocation for the administration of justice and renovation of Shari’ah courts in 2026?

```
The 2026 approved capital allocation for renovation of 25 Upper and lower Sharia Courts is ₦102.06 million. For Law and Justice, the 2026 approved capital allocation is ₦7.10 billion. Its 2026 recurrent allocations are ₦2.46 billion for personnel and ₦4.70 billion for overhead. All figures are budgeted allocations, not spending.

• Renovation of 25No Upper and lower Sharia Courts (Shari’a Court of Appeal), 2026 Approved Budget: ₦102.06 million
• Law and Justice (ministry total including its agencies, capital, code 030000000000) [Capital Expenditure by Administrative Classification], 2026 Approved Budget: ₦7.10 billion
• Law and Justice (ministry total including its agencies, personnel (salaries), code 030000000000) [Personnel Expenditure by Administrative Classification], 2026 Approved Budget: ₦2.46 billion
• Law and Justice (ministry total including its agencies, overhead (running costs), code 030000000000) [Other Non-Debt Recurrent Expenditure by Administrative Classification], 2026 Approved Budget: ₦4.70 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26, 63
_Reply *show working* to see the rows and arithmetic._
```

## m33: partial (lines:sum, 25.6s)

**Q:** What is the total expenditure allocated to security votes and contingency funds across the 2025 and 2026 fiscal years?

```
The approved allocation for Security Vote is ₦5.50 billion for 2025 and ₦8.21 billion for 2026. Together this is ₦13.71 billion (Kasafi's calculation). No line for contingency funds is shown in the data provided.

• SECURITY VOTE (INCLUDING OPERATIONS) (capital, code 22020604), 2025 Approved Budget: ₦5.50 billion
• SECURITY VOTE (INCLUDING OPERATIONS) (code 22020604), 2026 Approved Budget: ₦8.21 billion
• Not found: contingency funds

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 17; Sokoto State FY 2026 Budget, p. 28
_Reply *show working* to see the rows and arithmetic._
```

## m34: not found (search, 11.3s)

**Q:** Nawa aka ware wa Masarautar Musulmi (Sultanate Council) don gudanar da harkokin gargajiya da adana kayan tarihi a kasafin 2026?

```
Ban sami amsar wannan tambayar a cikin takardun da nake da su ba.
```

## m35: answered (lines:list, 20.6s)

**Q:** Can you state the exact administrative code, budget amount, and page number for the Sokoto State Independent Electoral Commission (SIEC) in the 2026 budget?

```
The approved 2026 budget amount for SIEC is ₦460.48 million. The exact administrative code and page number are shown with the selected line below; this figure is allocated (budgeted), not spent.

• Sokoto State Independent Electoral Commission (one agency or unit, all spending (total), code 014800100100), 2026 Approved Budget: ₦460.48 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## m36: partial (search, 21.4s)

**Q:** Is there an approved line item of ₦50 billion for the construction of an international cargo airport in the 2026 Sokoto budget?

_Hallucination test: no such line should be invented._

```
The budget does not show the asked airport line separately. The wider Airways sector capital for 2026 is ₦36.00 billion.

• 2026 approved budget (capital): ₦36.00 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 47
```

## m37: answered (search, 24.8s)

**Q:** Ina son ganin jimillar kudin da aka ware wa bangaren fasahar sadarwa (ICT and Innovation) a 2025 da 2026, tare da shafin da bayanin ya fito.

```
Jimillar kasafin da aka amince da shi ga ɓangaren fasahar sadarwa (Information Communication and Technology) a 2025 ya kai ₦3.30 biliyan, kamar yadda shafi na 24 ya nuna. Jimillar kasafin da aka amince da shi ga ɓangaren a 2026 ya kai ₦7.15 biliyan, kamar yadda shafi na 41 ya nuna.

• 2025 kasafin da aka amince (jimilla): ₦3.30 biliyan
• 2026 kasafin da aka amince (jimilla): ₦7.15 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 41; Sokoto State Government 2025 Approved Budget, shafi 24
```

## m38: not found (search, 27.0s)

**Q:** Nawa ne ainihin kudin da aka ware wa Karamar Hukumar Wamakko kai tsaye a cikin kasafin jihar na 2026?

_Tests state-level allocations vs local government statutory funds._

```
Kasafin jihar bai nuna kuɗin da aka ware kai tsaye ga Ƙaramar Hukumar Wamakko ba. Layukan kasafin jiha na cibiyoyin da ke Wamakko (misali asibiti ko makaranta) kuɗin jiha ne, ba na ƙaramar hukumar ba. Ƙananan hukumomi suna samun kasonsu na doka daga asusun tarayya daban, kuma takardun da nake da su ba su nuna na Wamakko ba.
```

## m39: answered (search, 4.3s)

**Q:** What was the exact capital budget execution rate for the Ministry of Environment in the Q2 2026 implementation report, and which document is cited?

```
*Ministry of Environment* (code 053500000000):
• Capital: share of the revised budget spent 48.6% (Kasafi's calculation)

📄 *Sources:* Budget Implementation Report Q2 2026, p. 28
```
