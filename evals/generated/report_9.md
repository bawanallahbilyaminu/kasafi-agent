# Generated coverage run

Cases: cases-379141.json (draw seed 379141), form seed 1

52 cases: wrong 1 (1.9%), of them wrong agency 0 | median 6.8s

| family | wrong | of |
|---|---|---|
| compare | 0 | 6 |
| false_premise | 1 | 6 |
| lookup | 0 | 6 |
| lookup_lga | 0 | 6 |
| not_in_data | 0 | 6 |
| rank_lga | 0 | 3 |
| share | 0 | 6 |
| spend_quarter | 0 | 6 |
| split | 0 | 6 |
| trend | 0 | 1 |

| form | wrong | of |
|---|---|---|
| code_switched | 0 | 11 |
| followup | 0 | 7 |
| hausa | 0 | 12 |
| informal | 0 | 4 |
| template | 0 | 10 |
| typo | 1 | 8 |

```
Cost of this run:
  Baseten: 25 calls, 210,832 prompt tokens (46,976 cached), 10,031 output tokens -> $0.25
  Meta: 120 calls, 354,301 prompt tokens (241,593 cached), 91,014 output tokens -> $0.56
  models together: $0.82 (prices per 1M tokens from settings kasafi_price_*)
  per answer (52 answers): $0.0114, 1.8 model calls
    Meta/plan               1.00 calls  $0.0035  (31%)
    Baseten/compose         0.23 calls  $0.0027  (24%)
    Meta/read1              0.25 calls  $0.0026  (23%)
    Baseten/read2           0.25 calls  $0.0022  (19%)
    Meta/topic              0.06 calls  $0.0003  (3%)
  Serper queries: 0 | documents fetched: 0 (downloads tried: 0) | identical calls answered from the run's cache: 0
peak memory: 261 MB
```

## lookup-01 (code_switched) ok (17.7s)

**Q:** Ministry for Home Affairs ta samu nawa a 2025 budget?

```
Ma'aikatar Harkokin Cikin Gida (Ministry for Home Affairs) ta samu ₦2.11 biliyan a kasafin 2025 da aka amince da shi. Wannan jimilla ce (total) daga teburin Jimillar Kashe Kuɗi ta Rarraba na Gudanarwa.

• 2025 kasafin da aka amince da shi (jimilla): ₦2.11 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-02 (template) ok (15.6s)

**Q:** How much was approved for the Ministry for Higher Education in the 2025 budget?

```
The Ministry for Higher Education was approved to receive ₦19.15 billion in the 2025 approved budget. This figure is the total expenditure for the ministry in that year.

• 2025 approved budget (total): ₦19.15 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12
```

## lookup-03 (followup) ok (11.9s)

**Q:** How much was approved for it in the 2025 budget?

```
The 2025 approved budget allocation for the Local Government Service Commission was ₦555.67 million. This is the ministry total, covering all spending.

• Local Government Service Commission (ministry total including its agencies, all spending (total), code 014900000000), 2025 Approved Budget: ₦555.67 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11
_Reply *show working* to see the rows and arithmetic._
```

## lookup-04 (code_switched) ok (16.8s)

**Q:** Nawa ne approved amount na Ministry of Budget and Economic Planning a 2025 budget?

```
Jimillar kasafin da aka amince da shi ga Ma'aikatar Kasafin Kuɗi da Tsare-Tsaren Tattalin Arziƙi a kasafin 2025 ita ce ₦4.03 biliyan. Wannan adadi daga teburin Total Expenditure by Administrative Classification ne, wanda ya haɗa da ma'aikatar da hukumominta.

• 2025 approved budget (jimilla) na Ministry of Budget and Economic Planning: ₦4.03 biliyan
• 2025 approved budget (jimilla) na hedkwatar ma'aikatar kaɗai (023800100100): ₦2.39 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11
```

## lookup-05 (hausa) ok (16.7s)

**Q:** Nawa aka amince wa Ministry Careers & Special Services a kasafin kudin 2026?

```
An amince wa Ministry Careers & Special Services jimillar ₦26.37 biliyan a kasafin kuɗi na 2026 da aka amince da shi. Wannan adadi jimilla ne (Total Expenditure) daga teburin kashe kuɗi ta ma'aikata.

• 2026 kasafin da aka amince (jimilla): ₦26.37 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 4, 16
```

## lookup-06 (hausa) ok (15.4s)

**Q:** Nawa aka amince da shi ga Ministry of Social Welfare & Community Development a kasafin kudin 2025?

```
An amince da jimillar ₦7.08 biliyan ga Ministry of Social Welfare & Community Development a kasafin kuɗin 2025 da aka amince da shi. Wannan adadi daga teburin Jimillar Kashe Kuɗi ta Rarraba Gudanarwa ne.

• 2025 kasafin da aka amince da shi (jimilla): ₦7.08 biliyan

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12
```

## split-01 (typo) ok (5.4s)

**Q:** What are the personell, overhead and capial allocations of the Ministry of Transport in 2026?

```
*Ministry of Transport* (code 022900000000):
• Personnel (salaries): approved budget ₦100.00 million
• Overhead (running costs): approved budget ₦3.10 billion
• Capital: approved budget ₦47.67 billion

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-02 (followup) ok (6.8s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
*State Agency for Normadic Education* (code 051701100100):
• Personnel (salaries): approved budget ₦209.00 million
• Overhead (running costs): approved budget ₦64.00 million
• Capital: approved budget ₦228.42 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## split-03 (template) ok (5.0s)

**Q:** What are the personnel, overhead and capital allocations of the Ministry of Solid Minerals and Natural Resources in 2026?

```
*Ministry of Solid Minerals and Natural Resources* (code 023300000000):
• Personnel (salaries): approved budget ₦45.34 million
• Overhead (running costs): approved budget ₦314.50 million
• Capital: approved budget ₦610.10 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 23, 26
```

## split-04 (typo) ok (5.3s)

**Q:** What are teh personnel, overhead adn capital allocations of the Shari’a Court of Appeal in 2026?

```
*Shari’a Court of Appeal* (code 031805500100):
• Personnel (salaries): approved budget ₦682.63 million
• Overhead (running costs): approved budget ₦774.24 million
• Capital: approved budget ₦951.06 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 20, 24, 26
```

## split-05 (hausa) ok (5.5s)

**Q:** Menene personnel, overhead da capital allocations na Ministry of Innovation and Digital Economy a 2026?

```
*Ministry of Innovation and Digital Economy* (code 027900000000):
• Albashi: kasafin da aka amince ₦60.01 miliyan
• Kuɗin gudanarwa: kasafin da aka amince ₦778.47 miliyan
• Manyan ayyuka: kasafin da aka amince ₦2.75 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 20, 23, 26
```

## split-06 (followup) ok (5.8s)

**Q:** What are its personnel, overhead and capital allocations in 2025?

```
*Sokoto Urban & Reg. Planning Department* (code 025300500100):
• Personnel (salaries): approved budget ₦79.94 million
• Overhead (running costs): approved budget ₦49.00 million
• Capital: approved budget ₦914.00 million

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 13, 15, 16
```

## spend_quarter-01 (hausa) ok (6.6s)

**Q:** Nawa UNDP ta kashe har zuwa karshen Q3 2025, akan revised budget dinta?

```
*UNDP* (code 011100900100):
• Jimilla: kasafin da aka sabunta ₦181.00 miliyan; abin da aka kashe zuwa yanzu (Q1–Q3) ₦30.00 miliyan; kason kasafin da aka sabunta da aka kashe 16.6% (lissafin Kasafi)

📄 *Madogara:* Sokoto State Budget Implementation Report Q3 2025, shafi 16
```

## spend_quarter-02 (template) ok (16.5s)

**Q:** How much had the SSG'S Office spent by the end of Q3 2025, against its revised budget?

```
By the end of Q3 2025 the SSG'S Office (code 016100100100) had spent ₦15.08 billion of its 2025 revised budget. That is 73.3% of its revised budget of ₦20.57 billion for the year. Figures are total expenditure for Q1-Q3 2025 only.

• 2025 revised budget (total): ₦20.57 billion
• 2025 spent Q1-Q3 (total): ₦15.08 billion (73.3% of the revised budget)

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 16
```

## spend_quarter-03 (template) ok (16.0s)

**Q:** How much had the Sokoto State House of Assembly spent by the end of Q3 2025, against its revised budget?

```
The Sokoto State House of Assembly had a 2025 revised budget of ₦9.37 billion. By the end of Q3 2025 (January–September) it had spent ₦3.39 billion. That spending was 36.1% of the revised budget.

• 2025 Revised Budget (total): ₦9.37 billion
• 2025 Q1–Q3 spent (total) (January–September 2025 only): ₦3.39 billion (36.1% of the revised budget)
• 2025 Q3 spent (total): ₦741.49 million

📄 *Sources:* Sokoto State Budget Implementation Report Q3 2025, p. 16
```

## spend_quarter-04 (typo) ok (4.9s)

**Q:** How much had teh State High Court spent by the edn of Q4 2024, against its revised budet?

```
*State High Court* (code 031805100100):
• Total: revised budget ₦4.61 billion; spent so far (Q1–Q4) ₦1.17 billion; share of the revised budget spent 25.4% (Kasafi's calculation)

📄 *Sources:* Budget Performance Report Q4 2024, p. 19
```

## spend_quarter-05 (code_switched) ok (4.9s)

**Q:** Ministry of Culture & Tourism ta kashe nawa by end of Q2 2026 against revised budget nata?

```
*Ministry of Culture & Tourism* (code 023600000000):
• Jimilla: kasafin da aka sabunta ₦1.42 biliyan; abin da aka kashe zuwa yanzu (Q1–Q2) ₦183.29 miliyan; kason kasafin da aka sabunta da aka kashe 12.9% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 16
```

## spend_quarter-06 (hausa) ok (4.4s)

**Q:** JUDICIAL SERVICE COMMISSION ta kashe nawa har zuwa karshen Q2 2026, idan aka kwatanta da revised budget dinta?

```
*JUDICIAL SERVICE COMMISSION* (code 031801100100):
• Jimilla: abin da aka kashe zuwa yanzu (Q1–Q2) ₦76.97 miliyan; kasafin da aka sabunta ₦556.51 miliyan; kason kasafin da aka sabunta da aka kashe 13.8% (lissafin Kasafi)

📄 *Madogara:* Budget Implementation Report Q2 2026, shafi 17
```

## compare-01 (code_switched) ok (4.2s)

**Q:** Abeg kwatanta approved budget na Ministry for Women Affairs for 2025 da 2026?

```
*Ministry for Women Affairs* (code 051400000000):
• Jimilla: 2025 kasafin da aka amince ₦8.44 biliyan; 2026 kasafin da aka amince ₦7.24 biliyan; bambanci -₦1.21 biliyan (-14.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-02 (typo) ok (3.8s)

**Q:** Comapre the State Judicary's approved budjet in 2025 and 2026.

```
*State Judiciary* (code 031800000000):
• Total: 2025 approved budget ₦6.28 billion; 2026 approved budget ₦8.17 billion; change +₦1.89 billion (+30.1%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## compare-03 (hausa) ok (4.2s)

**Q:** Kwatanta budget din Local Government Service Commission da aka amince da shi a 2025 da 2026.

```
*Local Government Service Commission* (code 014900000000):
• Jimilla: 2025 kasafin da aka amince ₦555.67 miliyan; 2026 kasafin da aka amince ₦746.52 miliyan; bambanci +₦190.85 miliyan (+34.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## compare-04 (hausa) ok (3.3s)

**Q:** Kwatanta kasafin kuɗin da aka amince da shi na Ministry of Livestocks and Fisheries Development a 2025 da 2026.

```
*Ministry of Livestocks and Fisheries Development* (code 026800000000):
• Jimilla: 2025 kasafin da aka amince ₦7.89 biliyan; 2026 kasafin da aka amince ₦13.60 biliyan; bambanci +₦5.71 biliyan (+72.3%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12; Sokoto State FY 2026 Budget, shafi 18
```

## compare-05 (template) ok (4.6s)

**Q:** Compare the Ministry for Home Affairs's approved budget in 2025 and 2026.

```
*Ministry for Home Affairs* (code 012400000000):
• Total: 2025 approved budget ₦2.11 billion; 2026 approved budget ₦6.11 billion; change +₦4.01 billion (+190.3%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## compare-06 (hausa) ok (5.0s)

**Q:** Kwatanta kasafin kudin Office of the SSG da aka amince da shi na 2025 da na 2026.

```
*Office of the SSG* (code 016100000000):
• Jimilla: 2025 kasafin da aka amince ₦31.36 biliyan; 2026 kasafin da aka amince ₦40.40 biliyan; bambanci +₦9.04 biliyan (+28.8%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 11; Sokoto State FY 2026 Budget, shafi 16
```

## share-01 (code_switched) ok (4.7s)

**Q:** Wannan 2026 approved budget na Arabic and Islamic Education Board, kashi nawa ne capital?

```
*Arabic and Islamic Education Board* (code 051705800100):
• Manyan ayyuka: kasafin da aka amince ₦840.00 miliyan; 26.6% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦3.16 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18, 27
```

## share-02 (hausa) ok (14.3s)

**Q:** Kashi nawa daga kasafin 2026 da aka amince wa Sokoto State Public Service Institute ne na capital?

```
Jimillar kasafin capital na 2026 da aka amince da shi ya kai ₦553.34 biliyan. Daga cikinsa, Sokoto State Public Service Institute na capital ya kai 0.00. Rabon ya zama 0.0% (lissafin Kasafi).

• Sokoto State Public Service Institute (hukuma ɗaya, manyan ayyuka, code 012500100200), 2026 Approved Budget: 0.00 ↑
• CAPITAL EXPENDITURE (Capital Expenditure) (code 23), 2026 Approved Budget: ₦553.34 biliyan ↓

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 1, 25
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## share-03 (typo) ok (4.7s)

**Q:** What shrae of the Primary School Staff Pension Board's 2026 aproved budget is capital?

```
*Primary School Staff Pension Board* (code 011103500200):
• Capital: approved budget ₦0.00; 0.0% of its total (Kasafi's calculation)
• Total: approved budget ₦60.34 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 16, 25
```

## share-04 (informal) ok (4.7s)

**Q:** What's the capital share of Commodity Board's 2026 budget?

```
*Commodity Board* (code 022200200100):
• Capital: approved budget ₦650.00 million; 96.4% of its total (Kasafi's calculation)
• Total: approved budget ₦673.97 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 17, 26
```

## share-05 (template) ok (4.6s)

**Q:** What share of the State Library Board's 2026 approved budget is capital?

```
*State Library Board* (code 051700800100):
• Capital: approved budget ₦300.00 million; 84.5% of its total (Kasafi's calculation)
• Total: approved budget ₦355.00 million

📄 *Sources:* Sokoto State FY 2026 Budget, p. 18, 27
```

## share-06 (code_switched) ok (4.8s)

**Q:** Sokoto State SME Development Agency 2026 approved budget ɗin nan, what share nasa ne capital?

```
*Sokoto State SME Development Agency* (code 022205100100):
• Manyan ayyuka: kasafin da aka amince ₦100.00 miliyan; 6.7% na jimillarsa (lissafin Kasafi)
• Jimilla: kasafin da aka amince ₦1.48 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17, 26
```

## false_premise-01 (informal) ok (5.3s)

**Q:** Why did Ministry of Culture & Tourism's approved budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry of Culture & Tourism* (code 023600000000):
• Personnel (salaries): 2025 approved budget ₦107.91 million; 2026 approved budget ₦103.35 million; change -₦4.56 million (-4.2%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦341.10 million; 2026 approved budget ₦532.80 million; change +₦191.70 million (+56.2%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦761.00 million; 2026 approved budget ₦788.59 million; change +₦27.59 million (+3.6%) (Kasafi's calculation)
• Total: 2025 approved budget ₦1.21 billion; 2026 approved budget ₦1.42 billion; change +₦214.73 million (+17.7%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 13, 14, 16; Sokoto State FY 2026 Budget, p. 17, 20, 23, 26
```

## false_premise-02 (typo) WRONG: didn't correct a premise the figures contradict (19.6s)

**Q:** Why did the Department of Establishment and Pensions's aproved budget rize from 2025 to 2026?

```
• Difference (2026 Approved Budget vs 2025 Approved Budget): -₦4.33 billion (-26.8%) (Kasafi's calculation)

• Department of Establishment and Pensions (ministry total including its agencies, all spending (total), code 017300000000), 2025 Approved Budget: ₦16.17 billion
• Department of Establishment and Pensions (ministry total including its agencies, all spending (total), code 017300000000), 2026 Approved Budget: ₦11.84 billion

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
_Reply *show working* to see the rows and arithmetic._
```

## false_premise-03 (informal) ok (5.6s)

**Q:** why did the Fiscal Responsibility Commission's approved budget drop from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Fiscal Responsibility Commission* (code 025000000000):
• Personnel (salaries): 2025 approved budget ₦9.44 million; 2026 approved budget ₦11.44 million; change +₦2.00 million (+21.2%) (Kasafi's calculation)
• Overhead (running costs): 2025 approved budget ₦35.30 million; 2026 approved budget ₦35.30 million; change ₦0.00 (0.0%) (Kasafi's calculation)
• Capital: 2025 approved budget ₦14.25 million; 2026 approved budget ₦14.25 million; change ₦0.00 (0.0%) (Kasafi's calculation)
• Total: 2025 approved budget ₦58.99 million; 2026 approved budget ₦60.99 million; change +₦2.00 million (+3.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11, 13, 14, 16; Sokoto State FY 2026 Budget, p. 17, 20, 23, 26
```

## false_premise-04 (hausa) ok (7.2s)

**Q:** Me ya sa kasafin kudin Ministry for Local Government and Chieftancy da aka amince da shi ya ragu daga 2025 zuwa 2026?

```
Bai ragu ba: kasafin da aka amince ya karu daga 2025 zuwa 2026, don haka babu raguwa da za a bayyana.
*Ministry for Local Government and Chieftancy* (code 055100000000):
• Albashi: 2025 kasafin da aka amince ₦145.67 miliyan; 2026 kasafin da aka amince ₦190.67 miliyan; bambanci +₦45.00 miliyan (+30.9%) (lissafin Kasafi)
• Kuɗin gudanarwa: 2025 kasafin da aka amince ₦211.97 miliyan; 2026 kasafin da aka amince ₦317.96 miliyan; bambanci +₦105.99 miliyan (+50.0%) (lissafin Kasafi)
• Manyan ayyuka: 2025 kasafin da aka amince ₦213.00 miliyan; 2026 kasafin da aka amince ₦850.44 miliyan; bambanci +₦637.44 miliyan (+299.3%) (lissafin Kasafi)
• Jimilla: 2025 kasafin da aka amince ₦570.64 miliyan; 2026 kasafin da aka amince ₦1.36 biliyan; bambanci +₦788.43 miliyan (+138.2%) (lissafin Kasafi)

📄 *Madogara:* Sokoto State Government 2025 Approved Budget, shafi 12, 14, 15, 17; Sokoto State FY 2026 Budget, shafi 19, 21, 24, 27
```

## false_premise-05 (followup) ok (4.8s)

**Q:** Why did its approved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry Careers & Special Services* (code 017000000000):
• Total: 2025 approved budget ₦10.57 billion; 2026 approved budget ₦26.37 billion; change +₦15.80 billion (+149.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 11; Sokoto State FY 2026 Budget, p. 16
```

## false_premise-06 (typo) ok (4.3s)

**Q:** Why did the Ministry for Higher Educaton's aproved budget fall from 2025 to 2026?

```
It didn't fall: the approved budget rose from 2025 to 2026, so there is no fall to explain.
*Ministry for Higher Education* (code 056900000000):
• Total: 2025 approved budget ₦19.15 billion; 2026 approved budget ₦33.99 billion; change +₦14.83 billion (+77.4%) (Kasafi's calculation)

📄 *Sources:* Sokoto State Government 2025 Approved Budget, p. 12; Sokoto State FY 2026 Budget, p. 18
```

## not_in_data-01 (code_switched) ok (15.3s)

**Q:** Nawa ne Works School Sokoto's approved budget for 2028?

```
Adadin da aka tsara wa Works School Sokoto a 2028 shi ne ₦56.95 miliyan. Wannan adadi hasashen shekara mai zuwa ne a kasafin 2026, ba kasafin 2028 da aka amince da shi ba.

• Works School Sokoto (hukuma ɗaya, duk kashe kuɗi (jimilla), code 023405400100), 2028 Out-Year Estimate: ₦56.95 miliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 17
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## not_in_data-02 (code_switched) ok (20.1s)

**Q:** Nawa ne approved budget na Umaru Ali Shinkafi Polytechnic Sokoto for 2028?

```
Jimillar da aka tanada wa Umaru Ali Shinkafi Polytechnic Sokoto a 2028 ita ce ₦5.19 biliyan. Wannan adadin hasashen shekaru masu zuwa ne (out-year estimate) a cikin kasafin 2026, ba approved budget na 2028 ba, domin babu approved budget na 2028 a takardun.

• Umaru Ali Shinkafi Polytechnic Sokoto (hukuma ɗaya, duk kashe kuɗi (jimilla), code 056901800100), 2028 Out-Year Estimate: ₦5.19 biliyan

📄 *Madogara:* Sokoto State FY 2026 Budget, shafi 18
_Rubuta *nuna lissafi* don ganin layukan da lissafin._
```

## not_in_data-03 (followup) ok (7.6s)

**Q:** How much is its approved budget for 2028?

```
Not in the documents:
• Noma Children Hospital 2028 approved budget: the 2028 budget isn't in the library (approved budgets: 2024–2026)
```

## not_in_data-04 (code_switched) ok (7.9s)

**Q:** Ministry of Justice ta spend nawa in Q4 2026?

```
Ba a cikin takardun ba:
• Ministry of Justice 2026 abin da aka kashe a Q4: rahoton aiwatarwa mafi sabo shi ne Q2 2026
• Ministry of Justice 2026 abin da aka kashe zuwa yanzu (Q1–Q4): rahoton aiwatarwa mafi sabo shi ne Q2 2026
```

## not_in_data-05 (followup) ok (7.0s)

**Q:** How much did it spend in Q1 2027?

```
Not in the documents:
• Min of Lands and Housing 2027 spent so far (Q1–Q1): no implementation report for 2027 in the library yet; the newest is Q2 2026
• Min of Lands and Housing 2027 spent in Q1: no implementation report for 2027 in the library yet; the newest is Q2 2026
```

## not_in_data-06 (followup) ok (17.4s)

**Q:** How much did it spend in Q4 2026?

```
No line in the documents is exactly that. The nearest lines they print (related, not the item itself):
• Rima Radio (one agency or unit, all spending (total), code 012300400100, Total Expenditure by Administrative Classification), 2026 Q1 Performance: ₦39.93 million [1]
• Rima Radio (one agency or unit, capital, code 012300400100, Capital Expenditure by Administrative Classification), 2026 Q2 Performance: 0.00 [2]

📄 *Sources:* Sokoto State Budget Implementation Report Q1 2026, p. 16; Budget Implementation Report Q2 2026, p. 26
```

## rank_lga-01 (code_switched) ok (17.7s)

**Q:** Which LGAs 3 ne a Sokoto with the most IDPs?

```
📊 Alƙaluma mafi sabo: *181,526 IDPs* – internally displaced persons (DTM baseline, all displacement reasons), Sokoto State (IOM Displacement Tracking Matrix, Round 18, reporting date 2025-10-31).

Daga kowace majiya:
• IOM Displacement Tracking Matrix: 181,526 IDPs – internally displaced persons (DTM baseline, all displacement reasons), Sokoto State; Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 40,729 IDPs – in Sabon Birni, the most of its 22 LGAs (then Tangaza 19,151; Tambuwal 17,143; Tureta 15,068; Shagari 14,850); Round 18, reporting date 2025-10-31 (IOM DTM API (Baseline))
• IOM Displacement Tracking Matrix: 88,562 IDPs – the round before, Sokoto State; Round 17, reporting date 2025-05-31 (IOM DTM API (Baseline))

Ban samu ba: Sokoto State Bureau of Statistics, JIPS, DRC, REACH, UNHCR Nigeria Forcibly Displaced Populations Dashboard, UN OCHA Nigeria.

📄 *Madogara:* IOM DTM API (Baseline)
```

## rank_lga-02 (informal) ok (8.7s)

**Q:** Top 5 LGAs with most IDPs in Sokoto?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143
4. Tureta: 15,068
5. Shagari: 14,850

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## rank_lga-03 (template) ok (7.8s)

**Q:** Which 10 LGAs in Sokoto have the most IDPs?

```
By LGA (22 LGAs), the most:
1. Sabon Birni: 40,729
2. Tangaza: 19,151
3. Tambuwal: 17,143
4. Tureta: 15,068
5. Shagari: 14,850
6. Isa: 14,047
7. Illela: 8,953
8. Gwadabawa: 8,406
9. Rabah: 8,277
10. Dange-Shuni: 4,615

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-01 (template) ok (7.6s)

**Q:** How many IDPs are there in Tureta LGA?

```
IOM DTM counts *15,068* IDPs in Tureta (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-02 (template) ok (8.5s)

**Q:** How many IDPs are there in Gada LGA?

```
IOM DTM counts *1,014* IDPs in Gada (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-03 (typo) ok (7.1s)

**Q:** How many ISDP are tehre in Sokoto North LGA?

```
IOM DTM counts *2,274* IDPs in Sokoto North (Round 18, reporting date 2025-10-31).

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-04 (hausa) ok (6.8s)

**Q:** IDPs nawa ne a Sabon Birni LGA?

```
IOM DTM ta ƙidaya *40,729* 'yan gudun hijira a Sabon Birni (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-05 (code_switched) ok (7.6s)

**Q:** IDPs nawa ne there in Tangaza LGA?

```
IOM DTM ta ƙidaya *19,151* 'yan gudun hijira a Tangaza (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## lookup_lga-06 (hausa) ok (6.9s)

**Q:** 'Yan gudun hijira nawa ne a Binji LGA?

```
IOM DTM ta ƙidaya *619* 'yan gudun hijira a Binji (Round 18, reporting date 2025-10-31).

📄 *Madogara:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```

## trend-01 (template) ok (8.4s)

**Q:** How has the number of IDPs in Sokoto State changed over the last DTM rounds?

```
Sokoto State, by round:
• Round 18 (2025-10-31): 181,526
• Round 17 (2025-05-31): 88,562
• Round 16 (2024-11-30): 99,729
• Round 15 (2024-09-30): 96,232
• Round 14 (2024-04-30): 117,568
• Round 13 (2023-12-31): 94,729
• Round 12 (2023-10-31): 67,936
• Round 11 (2022-12-31): 65,393
• Round 10 (2022-10-31): 52,850
• Round 9 (2021-12-31): 72,106
• Round 8 (2021-09-30): 71,289
• Round 7 (2021-07-30): 113,186
• Round 6 (2021-02-01): 45,308
• Round 5 (2020-12-31): 90,804
• Round 4 (2020-08-30): 36,595
• Round 2 (2019-10-30): 43,976
• Round 1 (2019-08-30): 36,153

📄 *Sources:* IOM DTM API (Baseline), Round 18, reporting date 2025-10-31
```
