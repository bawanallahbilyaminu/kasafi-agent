# Conversation understanding eval (open)

135 cases: **135 right**, 0 wrong. Latency median 6.86 s, p90 13.60 s; cost $0.0107 ($0.0054 per message; 2 re-read with --only, the rest kept from the last run).

| Id | Message | Capability / level / time / kind | Restatement | Wrong |
|---|---|---|---|---|
| u01 | But Uduth is closer to me | facility / facility / none / correction | Is Usmanu Danfodiyo University Teaching Hospital (UDUTH) closer to my ward than the hospitals previously listed? | ✅ |
| u02 | Has this area ever flooded | place_history / ward / past / follow_up | Has my ward ever been flooded? | ✅ |
| u03 | Has this land ever flooded? | place_history / pin / past / follow_up | Has my farm (the pin) ever flooded? | ✅ |
| u04 | What about the rain this season, will it flood? | hazard / pin / forecast / follow_up | Will my farm (the pin) flood this rainy season based on the rain forecast? | ✅ |
| u05 | How much of that has actually been spent? | place_budget / lga / year / follow_up | How much of the 2026 budget allocated to my LGA (Wamakko LGA) has actually been spent? | ✅ |
| u06 | And the past three years? | place_budget / lga / span / follow_up | What did the government budget for my LGA in the past three years (2023-2025)? | ✅ |
| u07 | How do I get to the second one? | facility / facility / none / follow_up | How do I get to Gidan Bubu Health Post from my location? | ✅ |
| u08 | Does Kalambaina PHC have enough nurses? | statistics / facility / now / follow_up | Does Kalambaina PHC have enough nurses? | ✅ |
| u09 | Amma UDUTH ya fi kusa da ni | facility / facility / none / correction | Is UDUTH the nearest health facility to my ward? | ✅ |
| u10 | Shin wannan gonar ta taba cika da ruwa? | place_history / pin / past / follow_up | Has my farm (the pin) ever been flooded? | ✅ |
| u11 | Za a yi ambaliya a nan bana? | hazard / ward / forecast / follow_up | Will my ward be flooded this year? | ✅ |
| u12 | Nawa aka kashe daga ciki? | place_budget / ward / year / follow_up | How much of the 2026 budget allocated to my ward has been spent? | ✅ |
| u13 | And how much of it was spent by June? | budget / sector / year / follow_up | How much of the 2026 health budget for Sokoto State was spent by June 2026? | ✅ |
| u14 | That's not right, the health budget is much smaller | budget / sector / year / correction | How much was budgeted for health in Sokoto State in 2026? | ✅ |
| u15 | What about in the DHS? | statistics / document / none / follow_up | What share of children are fully vaccinated in Sokoto State according to the DHS? | ✅ |
| u16 | What about the dust? | hazard / ward / forecast / follow_up | What is the dust forecast for tomorrow in my ward? | ✅ |
| u17 | Which hospital near me can I go to if my child has trouble breathing? | facility / ward / none / new | Which hospital near my ward can I go to if my child has trouble breathing? | ✅ |
| u18 | How much did the government budget for Specialist Hospital this year? | budget / facility / year / follow_up | How much did Sokoto State government budget for Specialist Hospital Sokoto in 2026? | ✅ |
| u19 | And is it getting greener over the years? | place_history / pin / span / follow_up | Is my farm (the pin) getting greener over the years? | ✅ |
| u20 | What about the whole of Wamakko? | place_history / lga / past / follow_up | Has Wamakko LGA ever been flooded? | ✅ |
| u21 | Is there any budget for irrigation there? | place_budget / lga / none / follow_up | Is there any budget for irrigation in my LGA (Wamakko)? | ✅ |
| u22 | What is the state doing about it in the 2026 budget? | budget / sector / year / follow_up | What is Sokoto State budgeting in 2026 to address out-of-school children in Sokoto State? | ✅ |
| u23 | Send me the full brief | deep / state / none / follow_up | Send the full brief on the state of PHCs in Sokoto State | ✅ |
| u24 | Thanks | conversation / none / none / chitchat | The user says thanks | ✅ |
| u25 | Is Arkilla open at night? | facility / facility / now / follow_up | Is Arkilla PHC open at night? | ✅ |
| u26 | Last year was there flooding in my LGA? | place_history / lga / past / follow_up | Was my LGA (Wamakko LGA) flooded in 2025? | ✅ |
| u27 | Na farko, yaya zan je can? | facility / facility / none / follow_up | How do I get to Specialist Hospital Sokoto from my ward? | ✅ |
| u28 | Nawa ne a karamar hukumata? | place_budget / lga / year / follow_up | How much of the 2026 education budget is allocated to my LGA? | ✅ |
| u29 | Is there anything for farmers? | place_budget / lga / year / follow_up | What projects for farmers/agriculture are budgeted for my LGA in 2026? | ✅ |
| u30 | My neighbour says it flooded in 2020, are you sure? | place_history / pin / past / correction | Has my farm (the pin) ever flooded, specifically in 2020? | ✅ |
| f01 | How many medical officers do PHCs need in Sokoto? | statistics / state / none / new | How many medical officers are needed for PHCs in Sokoto State? | ✅ |
| f02 | What's the state of PHCs in Sokoto? | deep / state / none / new | What is the overall state of PHCs in Sokoto State? | ✅ |
| f03 | tell me about health in Sokoto | deep / state / none / new | Tell me about the state of health in Sokoto State | ✅ |
| f04 | what's happening in my area? | deep / ward / now / new | What is happening in my ward (general overview)? | ✅ |
| f05 | How many PHCs are in Tureta? | facility / lga / none / new | How many PHCs are in Tureta LGA? | ✅ |
| f06 | How much did Sokoto spend on education last year? | budget / state / year / new | How much did Sokoto State spend on education in 2025? | ✅ |
| f07 | Is it safe to plant this week, will it rain? | hazard / pin / forecast / new | Will it rain this week at my farm (the pin) and is it safe to plant there? | ✅ |
| f08 | Nawa aka ware wa ma'aikatar lafiya a 2026? | budget / agency / year / new | What amount was allocated to the Ministry of Health in Sokoto State in 2026? | ✅ |
| f09 | Ina asibiti mafi kusa da ni? | facility / facility / now / new | Where is the nearest hospital to my ward? | ✅ |
| f10 | Gonata ta taba yin ambaliya? | place_history / pin / past / new | Has my farm (the pin) ever been flooded? | ✅ |
| f11 | What does the MICS say about birth registration in Sokoto? | statistics / document / none / new | What does the MICS report say about birth registration in Sokoto State? | ✅ |
| f12 | Alert me when there will be floods in Goronyo | alerts / lga / forecast / new | Alert me when there will be floods in Goronyo LGA | ✅ |
| f13 | What projects is the government doing in Tambuwal? | place_budget / lga / now / new | What projects is the Sokoto State government doing in Tambuwal LGA? | ✅ |
| f14 | Sannu | conversation / none / none / chitchat | The user greets Kasafi with Sannu | ✅ |
| f15 | Yaya yanayin ilimi a Sokoto? | deep / state / none / new | What is the state of education in Sokoto State? | ✅ |
| c01 | Who are you? | conversation / none / none / chitchat | Who are you? | ✅ |
| c02 | Kai wanene? | conversation / none / none / chitchat | Who are you? | ✅ |
| c03 | Me za ka iya yi? | conversation / none / none / chitchat | What can you do? | ✅ |
| c04 | What can you do? | conversation / none / none / chitchat | What can Kasafi do for users in Sokoto State? | ✅ |
| c05 | How does this work? | conversation / none / none / chitchat | How does Kasafi work? | ✅ |
| c06 | Who made you? | conversation / none / none / chitchat | Who made Kasafi? | ✅ |
| c07 | Is this a bot? | conversation / none / none / chitchat | Is Kasafi a bot? | ✅ |
| c08 | Can you speak Hausa? | conversation / none / none / chitchat | Can you speak Hausa? | ✅ |
| c09 | Na gode | conversation / none / none / chitchat | The user says thank you. | ✅ |
| c10 | Assalamu alaikum | conversation / none / none / chitchat | Greeting and introductory question to Kasafi | ✅ |
| c11 | Hello | conversation / none / none / chitchat | The user greets Kasafi. | ✅ |
| c12 | Sai anjima | conversation / none / none / chitchat | The user says goodbye, see you later | ✅ |
| c13 | Thank you, bye | conversation / none / none / chitchat | The user says thank you and goodbye. | ✅ |
| c14 | help | conversation / none / none / chitchat | What can Kasafi help me with? | ✅ |
| c15 | Ina kwana | conversation / none / none / chitchat | greeting in Hausa | ✅ |
| c16 | Wa ya yi ka? | conversation / none / none / chitchat | Who made you (Kasafi)? | ✅ |
| c17 | Kana jin Hausa? | conversation / none / none / chitchat | Can you understand and speak Hausa? | ✅ |
| c18 | Mutum ne kai ko na'ura? | conversation / none / none / chitchat | Are you a human or a machine? | ✅ |
| c19 | Yaya kake aiki? | conversation / none / none / chitchat | How do you work? | ✅ |
| c20 | But uduth is closer to me | facility / facility / none / correction | Is Usmanu Danfodiyo University Teaching Hospital (UDUTH) closer to me in my LGA? | ✅ |
| m01 | Where can my wife deliver a baby? | facility / ward / now / new | Where is the nearest health facility to my ward where my wife can deliver a baby? | ✅ |
| m02 | Matata na naƙuda, ina zan kai ta? | facility / ward / now / new | Where should I take my wife who is in labour now from my ward? | ✅ |
| m03 | Nearest place for antenatal care | facility / ward / none / new | What is the nearest health facility offering antenatal care to my ward? | ✅ |
| m04 | A ina matata za ta haihu? | facility / ward / none / new | Where can my wife give birth near my ward in Wamakko LGA? | ✅ |
| m05 | Is there anywhere I can deliver a baby around here? | facility / ward / now / new | Is there a health facility where I can deliver a baby near my ward? | ✅ |
| m06 | Where can I take my sick child? | facility / ward / now / new | Where is the nearest health facility to my ward where I can take my sick child? | ✅ |
| m07 | Ina asibitin gwamnati mafi kusa? | facility / ward / none / new | Where is the nearest government hospital to my ward? | ✅ |
| m08 | Is there a private clinic near me? | facility / ward / now / new | Is there a private clinic near my ward? | ✅ |
| m09 | Only government ones | facility / ward / now / clarification | Where can my wife deliver a baby at the nearest government facilities to my ward? | ✅ |
| m10 | Anything for schools? | place_budget / lga / year / follow_up | What does the budget allocate for schools in my LGA? | ✅ |
| k01 | menu | conversation / none / none / menu | Show the menu of what Kasafi can do | ✅ |
| k02 | zaɓi | conversation / none / none / menu | Show the menu of available options | ✅ |
| k03 | Nuna min zaɓuɓɓuka | conversation / none / none / menu | Show me the menu of options | ✅ |
| n01 | How many people were affected by floods in Sokoto State in October 2024? | statistics / state / past / new | How many people were affected by floods in Sokoto State in October 2024? | ✅ |
| n02 | How many people were displaced by the 2024 floods in Sokoto? | statistics / state / past / new | How many people were displaced by the 2024 floods in Sokoto State? | ✅ |
| n03 | How many houses were destroyed by flooding in Sokoto in 2025? | statistics / state / year / new | How many houses were destroyed by flooding in Sokoto State in 2025? | ✅ |
| n04 | Was Wamakko LGA affected by floods in 2025, according to NEMA? | statistics / document / year / new | Was Wamakko LGA affected by floods in 2025 according to NEMA? | ✅ |
| n05 | Which LGAs in Sokoto State were affected by floods in 2025, according to NEMA? | statistics / document / year / new | Which LGAs in Sokoto State were affected by floods in 2025 according to NEMA? | ✅ |
| n06 | Mutane nawa ambaliyar ruwa ta shafa a Jihar Sokoto a 2025, a cewar NEMA? | statistics / state / year / new | How many people were affected by floods in Sokoto State in 2025 according to NEMA? | ✅ |
| n07 | Mutane nawa suka rasa matsugunansu saboda ambaliya a Sokoto a 2024? | statistics / state / year / new | How many people were displaced due to floods in Sokoto State in 2024? | ✅ |
| n08 | Gidaje nawa ambaliya ta rushe a Sokoto a 2024? | statistics / state / past / new | How many houses were destroyed by floods in Sokoto State in 2024? | ✅ |
| n09 | How bad were the 2024 floods in Sokoto? | statistics / state / past / new | How bad were the 2024 floods in Sokoto State? | ✅ |
| n10 | Yaya girman ambaliyar 2024 a Jihar Sokoto? | statistics / state / year / new | How severe and extensive were the 2024 floods in Sokoto State? | ✅ |
| n11 | How many people died in floods in Sokoto in 2024? | statistics / state / past / new | How many people died due to floods in Sokoto State in 2024? | ✅ |
| n12 | How much of my ward was under water in 2024? | place_history / ward / past / follow_up | How much of my ward was under water in 2024? | ✅ |
| n13 | Which wards of Wamakko flooded most in 2022? | place_history / lga / past / new | Which wards in Wamakko LGA were the most flooded in 2022? | ✅ |
| n14 | Ruwa ya taɓa rufe gonata? | place_history / pin / past / follow_up | Has water ever covered my farm (the pin)? | ✅ |
| n15 | What does the MICS report say about birth registration in Sokoto? | statistics / document / none / new | What does the MICS report say about birth registration in Sokoto State? | ✅ |
| n16 | According to NiMet, when will the rains end in my LGA this year? | hazard / lga / forecast / new | According to NiMet, when will the rains end in my LGA this year? | ✅ |
| lf15 | Which wards of Kware LGA got the most June–October rain in 2024? | place_history / lga / past / new | Which wards of Kware LGA received the most rainfall during June-October 2024? | ✅ |
| lf16 | Waɗanne gundumomin Ƙaramar Hukumar Kware ne suka fi samun ruwan sama a damina ta 2024? | place_history / lga / past / new | Which wards of Kware LGA received the most rainfall during the 2024 rainy season? | ✅ |
| lf17 | Will it rain in my LGA this week? | hazard / lga / forecast / new | Will it rain in my LGA this week? | ✅ |
| lf11 | According to the Multiple Indicator Cluster Survey (MICS) by NBS and UNICEF, what are the gaps in child healthcare and civil registration for Sokoto State? | statistics / document / year / new | According to the Multiple Indicator Cluster Survey (MICS) by NBS and UNICEF, what are the gaps in child healthcare and civil registration for Sokoto State? | ✅ |
| lf12 | A cewar MICS na NBS da UNICEF, waɗanne gibi ne ke cikin kula da lafiyar yara da rajistar haihuwa a Jihar Sokoto? | statistics / document / none / new | According to the MICS by NBS and UNICEF, what gaps exist in child healthcare and birth registration in Sokoto State? | ✅ |
| lf13 | Birth registration in Sokoto: what did MICS 2021 and NDHS 2024 each find, and can the two be compared? | statistics / state / span / new | What did MICS 2021 and NDHS 2024 each find about birth registration in Sokoto State and can the two be compared? | ✅ |
| lf14 | What's the state of child health in Sokoto? | deep / state / none / new | What is the overall state of child health in Sokoto State? | ✅ |
| lf01 | How many schools are in Dange Shuni | statistics / lga / none / new | How many schools are in Dange Shuni LGA at each level? | ✅ |
| lf02 | I mean all the total schools primary, senior secondary and junior secondary and IQS | statistics / lga / none / clarification | How many schools are in Dange Shuni LGA in total, broken down by primary, junior secondary, senior secondary and IQS levels? | ✅ |
| lf03 | Am talking about schools not budget | statistics / lga / none / correction | How many schools at all levels (primary, junior secondary, senior secondary and IQS) are in Dange Shuni LGA? | ✅ |
| lf04 | Makarantu nawa ne a Dange Shuni? | statistics / lga / none / new | How many schools are in Dange Shuni LGA, with numbers at each level? | ✅ |
| lf05 | Ina nufin duka makarantun: firamare, ƙaramar sakandare, babbar sakandare da IQS | statistics / lga / none / clarification | How many schools are in Dange Shuni LGA at each level: primary, JSS, SSS and IQS? | ✅ |
| lf06 | Makarantu nake magana ba kasafi ba | statistics / lga / none / correction | How many schools are there in Dange Shuni LGA in total, broken down by level? | ✅ |
| lf07 | I asked about people, not hectares of land | statistics / state / year / correction | How many people were affected by floods in Sokoto State in 2024? | ✅ |
| lf08 | I mean the 2025 budget | place_budget / lga / year / clarification | What is the government budgeting for Wamakko LGA in the 2025 budget? | ✅ |
| lf09 | I mean all of them, PHCs and dispensaries too | facility / lga / none / clarification | How many health facilities at all levels (hospitals, PHCs and dispensaries) are in Wamakko LGA? | ✅ |
| lf10 | Ok so which LGAs does it name? | statistics / document / year / follow_up | Which LGAs does NEMA's 26 September 2025 situation report name as affected by floods in Sokoto State? | ✅ |
| a01 | Has it ever flooded here? | place_history / ward / past / follow_up | Has my ward ever been flooded in the past? | ✅ |
| a02 | Has this place ever flooded? | place_history / ward / past / follow_up | Has my ward ever flooded? | ✅ |
| a03 | Any floods around here in past years? | place_history / ward / past / follow_up | Was my ward flooded in past years? | ✅ |
| a04 | Shin wannan wuri ya taɓa ambaliya? | place_history / ward / past / new | Has my ward ever been flooded? | ✅ |
| a05 | An taɓa samun ambaliya a nan? | place_history / ward / past / follow_up | Has my ward ever been flooded? | ✅ |
| a06 | Has my farm ever flooded? | place_history / pin / past / follow_up | Has my farm (the pin) in my ward in Wamakko LGA ever flooded? | ✅ |
| a07 | Has this field been under water before? | place_history / pin / past / follow_up | Has my farm (the pin) been under water before? | ✅ |
| a08 | Gonata ta taɓa ambaliya? | place_history / pin / past / follow_up | Has my farm (the pin) in my ward, Wamakko LGA ever been flooded? | ✅ |
| a09 | I'm thinking of moving my family here. What is the government spending in this area, has it ever flooded, and where's the nearest clinic? | place_budget / ward / none / follow_up | What is the government spending in my ward (Kalambaina, Wamakko LGA), has my ward ever flooded, and where is the nearest clinic to my ward? | ✅ |
| a10 | Has this area flooded before, and what is the state spending on erosion here? | place_history / ward / past / follow_up | Has my ward flooded before and what is the state spending on erosion control in my LGA? | ✅ |
| p01 | my name is musa | conversation / none / none / chitchat | My name is Musa | ✅ |
| p02 | Ni ne Musa | conversation / none / none / chitchat | My name is Musa | ✅ |
| p03 | Call me Musa | conversation / none / none / chitchat | User asks to be called Musa | ✅ |
| p04 | Musa ne sunana | conversation / none / none / chitchat | My name is Musa. | ✅ |
| p05 | Sunana Aisha Umar, ina so in san kasafin lafiya na 2026 | budget / sector / year / new | What is the health budget for Sokoto State in 2026? | ✅ |
| p06 | Hello, I'm Dr. Aisha Umar from the Ministry of Finance. How much is the 2026 health budget? | budget / sector / year / new | What is the 2026 health budget for Sokoto State? | ✅ |
| p07 | ku kira ni malam sani | conversation / none / none / chitchat | Please call me Malam Sani. | ✅ |
| p08 | good morning, hauwa here. where is the nearest hospital? | facility / ward / none / follow_up | Where is the nearest hospital to my ward? | ✅ |
| p09 | I am a farmer in Wamakko. Has my farm ever flooded? | place_history / pin / past / follow_up | Has my farm (the pin) in Wamakko LGA ever been flooded? | ✅ |
| p10 | Ni manomi ne daga Wurno, nawa aka ware wa noma a kasafin 2026? | budget / sector / year / new | How much was allocated to agriculture in the Sokoto State 2026 budget? | ✅ |
| p11 | I want to take my son Musa for immunisation, where is the nearest clinic? | facility / ward / none / new | Where is the nearest clinic for my son's immunisation to my ward? | ✅ |
| p12 | Thank you | conversation / none / none / chitchat | User says thank you. | ✅ |
| p13 | I am the Director of Budget. Tell me about the Ministry of Innovation and Digital Economy | deep / agency / none / new | Tell me about the Ministry of Innovation and Digital Economy in Sokoto State | ✅ |
| p14 | Is this Kasafi? | conversation / none / none / chitchat | Is this Kasafi? | ✅ |
