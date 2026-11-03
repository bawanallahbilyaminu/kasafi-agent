# Conversation understanding eval (open)

111 cases: **111 right**, 0 wrong. Latency median 2.18 s, p90 3.45 s; cost $0.0048 ($0.0048 per message; 1 re-read with --only, the rest kept from the last run).

| Id | Message | Capability / level / time / kind | Restatement | Wrong |
|---|---|---|---|---|
| u01 | But Uduth is closer to me | facility / facility / none / correction | Is Usmanu Danfodiyo University Teaching Hospital (UDUTH) closer to my farm (the pin) than the hospitals previously listed and what is the nearest hospital to my farm (the pin)? | ✅ |
| u02 | Has this area ever flooded | place_history / ward / past / follow_up | Has my ward ever been flooded? | ✅ |
| u03 | Has this land ever flooded? | place_history / pin / past / new | Has my farm (the pin) in Kalambaina ward, Wamakko LGA ever been flooded in the past? | ✅ |
| u04 | What about the rain this season, will it flood? | hazard / pin / forecast / follow_up | Will my farm (the pin) flood this season due to rain? | ✅ |
| u05 | How much of that has actually been spent? | place_budget / lga / year / follow_up | How much of the N79.98 billion budgeted for capital projects in my LGA (Wamakko LGA) in 2026 has actually been spent? | ✅ |
| u06 | And the past three years? | place_budget / lga / span / follow_up | What did the government budget for my LGA (Wamakko LGA, the area of the pin) in the past three years (2023-2025)? | ✅ |
| u07 | How do I get to the second one? | facility / facility / none / follow_up | How do I get to Gidan Bubu Health Post from my farm (the pin)? | ✅ |
| u08 | Does Kalambaina PHC have enough nurses? | statistics / facility / now / follow_up | Does Kalambaina PHC have enough nurses? | ✅ |
| u09 | Amma UDUTH ya fi kusa da ni | facility / facility / none / correction | Is UDUTH (Usmanu Danfodiyo University Teaching Hospital) closer to my farm (the pin) than the facilities previously listed? | ✅ |
| u10 | Shin wannan gonar ta taba cika da ruwa? | place_history / pin / past / new | Has my farm (the pin) ever been flooded? | ✅ |
| u11 | Za a yi ambaliya a nan bana? | hazard / pin / forecast / follow_up | Will my farm (the pin) be flooded this year? | ✅ |
| u12 | Nawa aka kashe daga ciki? | place_budget / lga / year / follow_up | How much of the amount allocated to my LGA in the 2026 budget has been spent? | ✅ |
| u13 | And how much of it was spent by June? | budget / state / year / follow_up | How much of the 2026 health budget for Sokoto State was spent by June? | ✅ |
| u14 | That's not right, the health budget is much smaller | budget / sector / year / correction | How much was budgeted for health in Sokoto State in 2026? | ✅ |
| u15 | What about in the DHS? | statistics / document / none / follow_up | What share of children are fully vaccinated in Sokoto State according to the DHS? | ✅ |
| u16 | What about the dust? | hazard / pin / forecast / follow_up | What is the dust forecast for my farm (the pin) tomorrow? | ✅ |
| u17 | Which hospital near me can I go to if my child has trouble breathing? | facility / pin / none / new | Which is the nearest hospital to my farm (the pin) that I can go to if my child has trouble breathing? | ✅ |
| u18 | How much did the government budget for Specialist Hospital this year? | budget / facility / year / follow_up | How much did Sokoto State budget for Specialist Hospital Sokoto in 2026? | ✅ |
| u19 | And is it getting greener over the years? | place_history / pin / span / follow_up | Is my farm (the pin) getting greener over the years? | ✅ |
| u20 | What about the whole of Wamakko? | place_history / lga / past / follow_up | Has Wamakko LGA ever been flooded? | ✅ |
| u21 | Is there any budget for irrigation there? | place_budget / lga / none / follow_up | Is there any budget for irrigation in my LGA? | ✅ |
| u22 | What is the state doing about it in the 2026 budget? | budget / sector / year / follow_up | What is Sokoto State doing about out-of-school children in the 2026 budget? | ✅ |
| u23 | Send me the full brief | deep / state / none / follow_up | Send the full brief on the state of PHCs in Sokoto State | ✅ |
| u24 | Thanks | conversation / none / none / chitchat | The user says thanks | ✅ |
| u25 | Is Arkilla open at night? | facility / facility / now / follow_up | Is Arkilla PHC open at night? | ✅ |
| u26 | Last year was there flooding in my LGA? | place_history / lga / past / follow_up | Was my LGA flooded last year (in 2025)? | ✅ |
| u27 | Na farko, yaya zan je can? | facility / facility / none / follow_up | How do I get to Specialist Hospital Sokoto from my farm (the pin) in my ward, Wamakko LGA? | ✅ |
| u28 | Nawa ne a karamar hukumata? | place_budget / lga / year / follow_up | How much of the Sokoto State 2026 education budget is allocated to my LGA? | ✅ |
| u29 | Is there anything for farmers? | place_budget / lga / year / follow_up | Is there anything in the 2026 budget for farmers in my LGA (Wamakko LGA)? | ✅ |
| u30 | My neighbour says it flooded in 2020, are you sure? | place_history / pin / year / correction | Did my farm (the pin) flood in 2020 as my neighbour claims, or has it ever flooded? | ✅ |
| f01 | How many medical officers do PHCs need in Sokoto? | statistics / state / none / new | How many medical officers are needed for PHCs in Sokoto State? | ✅ |
| f02 | What's the state of PHCs in Sokoto? | deep / state / none / new | What is the current state of primary health centres (PHCs) in Sokoto State? | ✅ |
| f03 | tell me about health in Sokoto | deep / state / none / new | Provide a broad overview of health in Sokoto State | ✅ |
| f04 | what's happening in my area? | deep / ward / none / new | What is happening in my ward? | ✅ |
| f05 | How many PHCs are in Tureta? | facility / lga / none / new | How many PHCs are in Tureta LGA? | ✅ |
| f06 | How much did Sokoto spend on education last year? | budget / sector / year / new | How much did Sokoto State spend on education in 2025? | ✅ |
| f07 | Is it safe to plant this week, will it rain? | hazard / pin / forecast / new | Will it rain this week at my farm (the pin) in my ward in my LGA and is it safe to plant? | ✅ |
| f08 | Nawa aka ware wa ma'aikatar lafiya a 2026? | budget / agency / year / new | How much was allocated to the Ministry of Health in Sokoto State in 2026? | ✅ |
| f09 | Ina asibiti mafi kusa da ni? | facility / facility / none / new | What is the nearest hospital to my farm (the pin)? | ✅ |
| f10 | Gonata ta taba yin ambaliya? | place_history / pin / past / new | Has my farm (the pin) in my ward in Wamakko LGA ever been flooded? | ✅ |
| f11 | What does the MICS say about birth registration in Sokoto? | statistics / document / none / new | What does the MICS report say about birth registration in Sokoto State? | ✅ |
| f12 | Alert me when there will be floods in Goronyo | alerts / lga / forecast / new | Subscribe to flood alerts for Goronyo LGA in Sokoto State | ✅ |
| f13 | What projects is the government doing in Tambuwal? | place_budget / lga / now / new | What projects is the government doing in Tambuwal LGA? | ✅ |
| f14 | Sannu | conversation / none / none / chitchat | Greeting saying hello | ✅ |
| f15 | Yaya yanayin ilimi a Sokoto? | deep / sector / none / new | What is the state of education in Sokoto State? | ✅ |
| c01 | Who are you? | conversation / none / none / chitchat | Who is Kasafi? | ✅ |
| c02 | Kai wanene? | conversation / none / none / chitchat | Who are you? | ✅ |
| c03 | Me za ka iya yi? | conversation / none / none / chitchat | What can you do as Kasafi? | ✅ |
| c04 | What can you do? | conversation / none / none / chitchat | What can you do as Kasafi assistant? | ✅ |
| c05 | How does this work? | conversation / none / none / chitchat | How does Kasafi work and what can it help me with in Sokoto State? | ✅ |
| c06 | Who made you? | conversation / none / none / chitchat | Who made you / who created Kasafi? | ✅ |
| c07 | Is this a bot? | conversation / none / none / chitchat | Is Kasafi a bot? | ✅ |
| c08 | Can you speak Hausa? | conversation / none / none / chitchat | Can Kasafi speak Hausa? | ✅ |
| c09 | Na gode | conversation / none / none / chitchat | Thank you. | ✅ |
| c10 | Assalamu alaikum | conversation / none / none / chitchat | User greets Kasafi with Assalamu alaikum | ✅ |
| c11 | Hello | conversation / none / none / chitchat | User says hello to Kasafi | ✅ |
| c12 | Sai anjima | conversation / none / none / chitchat | Goodbye / See you later (chitchat). | ✅ |
| c13 | Thank you, bye | conversation / none / none / chitchat | thank you and goodbye | ✅ |
| c14 | help | conversation / none / none / chitchat | The user asks what Kasafi can do and how to get help | ✅ |
| c15 | Ina kwana | conversation / none / none / chitchat | The user is greeting Kasafi in Hausa | ✅ |
| c16 | Wa ya yi ka? | conversation / none / none / chitchat | Who made you? | ✅ |
| c17 | Kana jin Hausa? | conversation / none / none / chitchat | Can you understand and speak Hausa? | ✅ |
| c18 | Mutum ne kai ko na'ura? | conversation / none / none / chitchat | Are you a human or a machine? | ✅ |
| c19 | Yaya kake aiki? | conversation / none / none / chitchat | How do you work as Kasafi? | ✅ |
| c20 | But uduth is closer to me | facility / facility / none / correction | Is Usmanu Danfodiyo University Teaching Hospital (UDUTH) the nearest hospital to me in my LGA? | ✅ |
| m01 | Where can my wife deliver a baby? | facility / pin / none / new | Where can my wife deliver a baby near my farm (the pin) in my ward, Wamakko LGA, Sokoto State? | ✅ |
| m02 | Matata na naƙuda, ina zan kai ta? | facility / facility / now / new | Where is the nearest health facility where my wife can give birth from my farm (the pin) in my ward in Wamakko LGA? | ✅ |
| m03 | Nearest place for antenatal care | facility / pin / none / new | Where is the nearest place for antenatal care to my farm (the pin) in Kalambaina ward, Wamakko LGA? | ✅ |
| m04 | A ina matata za ta haihu? | facility / none / now / new | Where can my wife give birth near my farm (the pin) in my ward in Wamakko LGA? | ✅ |
| m05 | Is there anywhere I can deliver a baby around here? | facility / pin / none / new | Where can I deliver a baby near my farm (the pin) in my ward in Wamakko LGA? | ✅ |
| m06 | Where can I take my sick child? | facility / pin / now / new | What are the nearest health facilities to my farm (the pin) in my ward, Wamakko LGA, where I can take my sick child? | ✅ |
| m07 | Ina asibitin gwamnati mafi kusa? | facility / pin / none / new | Where is the nearest government hospital to my farm (the pin) in my ward, Wamakko LGA? | ✅ |
| m08 | Is there a private clinic near me? | facility / pin / none / new | Is there a private clinic near my farm (the pin)? | ✅ |
| m09 | Only government ones | facility / pin / none / clarification | Where can my wife deliver a baby near my farm (the pin) considering only government facilities? | ✅ |
| m10 | Anything for schools? | place_budget / lga / year / follow_up | Are there any school/education projects budgeted for my LGA (Wamakko LGA) in 2026? | ✅ |
| k01 | menu | conversation / none / none / menu | Show the menu of options | ✅ |
| k02 | zaɓi | conversation / none / none / menu | Show the main menu of what Kasafi can do | ✅ |
| k03 | Nuna min zaɓuɓɓuka | conversation / none / none / menu | User wants to see the menu of available options. | ✅ |
| n01 | How many people were affected by floods in Sokoto State in October 2024? | statistics / state / past / new | How many people were affected by floods in Sokoto State in October 2024? | ✅ |
| n02 | How many people were displaced by the 2024 floods in Sokoto? | statistics / state / past / new | How many people were displaced by the 2024 floods in Sokoto State? | ✅ |
| n03 | How many houses were destroyed by flooding in Sokoto in 2025? | statistics / state / year / new | How many houses were destroyed by flooding in Sokoto State in 2025? | ✅ |
| n04 | Was Wamakko LGA affected by floods in 2025, according to NEMA? | statistics / lga / year / new | Was Wamakko LGA affected by floods in 2025 according to NEMA? | ✅ |
| n05 | Which LGAs in Sokoto State were affected by floods in 2025, according to NEMA? | statistics / document / year / new | Which LGAs in Sokoto State were affected by floods in 2025 according to NEMA? | ✅ |
| n06 | Mutane nawa ambaliyar ruwa ta shafa a Jihar Sokoto a 2025, a cewar NEMA? | statistics / state / year / new | How many people were affected by floods in Sokoto State in 2025 according to NEMA? | ✅ |
| n07 | Mutane nawa suka rasa matsugunansu saboda ambaliya a Sokoto a 2024? | statistics / state / year / new | How many people were displaced due to floods in Sokoto State in 2024? | ✅ |
| n08 | Gidaje nawa ambaliya ta rushe a Sokoto a 2024? | statistics / state / year / new | How many houses were destroyed by floods in Sokoto State in 2024? | ✅ |
| n09 | How bad were the 2024 floods in Sokoto? | statistics / state / past / new | How bad were the 2024 floods in Sokoto State in terms of people affected and overall impact? | ✅ |
| n10 | Yaya girman ambaliyar 2024 a Jihar Sokoto? | statistics / state / past / new | How large were the 2024 floods in Sokoto State? | ✅ |
| n11 | How many people died in floods in Sokoto in 2024? | statistics / state / past / new | How many people died due to floods in Sokoto State in 2024? | ✅ |
| n12 | How much of my ward was under water in 2024? | place_history / ward / past / follow_up | How much of my ward was under water in 2024? | ✅ |
| n13 | Which wards of Wamakko flooded most in 2022? | place_history / lga / past / new | Which wards in Wamakko LGA had the largest flooded area in 2022? | ✅ |
| n14 | Ruwa ya taɓa rufe gonata? | place_history / pin / past / new | Has flood water ever covered my farm (the pin) in Kalambaina ward, Wamakko LGA? | ✅ |
| n15 | What does the MICS report say about birth registration in Sokoto? | statistics / document / none / new | What does the MICS report say about birth registration in Sokoto State? | ✅ |
| n16 | According to NiMet, when will the rains end in my LGA this year? | hazard / lga / forecast / new | According to NiMet, when will the rains end in my LGA (Wamakko LGA) this year? | ✅ |
| lf15 | Which wards of Kware LGA got the most June–October rain in 2024? | place_history / lga / past / new | Which wards of Kware LGA received the most rainfall during June-October 2024? | ✅ |
| lf16 | Waɗanne gundumomin Ƙaramar Hukumar Kware ne suka fi samun ruwan sama a damina ta 2024? | place_history / lga / past / new | Which wards of my LGA Kware received the most rainfall during the 2024 rainy season? | ✅ |
| lf17 | Will it rain in my LGA this week? | hazard / lga / forecast / new | Will it rain in my LGA this week? | ✅ |
| lf11 | According to the Multiple Indicator Cluster Survey (MICS) by NBS and UNICEF, what are the gaps in child healthcare and civil registration for Sokoto State? | statistics / document / none / new | What are the gaps in child healthcare and civil registration for Sokoto State according to the Multiple Indicator Cluster Survey (MICS) by NBS and UNICEF? | ✅ |
| lf12 | A cewar MICS na NBS da UNICEF, waɗanne gibi ne ke cikin kula da lafiyar yara da rajistar haihuwa a Jihar Sokoto? | statistics / document / none / new | According to the NBS and UNICEF MICS, what gaps exist in child healthcare and birth registration in Sokoto State? | ✅ |
| lf13 | Birth registration in Sokoto: what did MICS 2021 and NDHS 2024 each find, and can the two be compared? | statistics / document / span / new | What did MICS 2021 and NDHS 2024 each find about birth registration in Sokoto State and can the two be compared? | ✅ |
| lf14 | What's the state of child health in Sokoto? | deep / state / none / new | What is the overall state of child health in Sokoto State? | ✅ |
| lf01 | How many schools are in Dange Shuni | statistics / lga / none / new | How many schools are there in total in Dange Shuni LGA (all levels, with breakdown by primary, JSS, SSS and IQS)? | ✅ |
| lf02 | I mean all the total schools primary, senior secondary and junior secondary and IQS | statistics / lga / none / clarification | What is the total number of schools in Dange Shuni LGA, with the breakdown for primary, junior secondary, senior secondary and IQS? | ✅ |
| lf03 | Am talking about schools not budget | statistics / lga / none / correction | How many schools are there in total in Dange Shuni LGA, counting primary, junior secondary, senior secondary and IQS, with breakdown by level | ✅ |
| lf04 | Makarantu nawa ne a Dange Shuni? | statistics / lga / none / new | How many schools are there in Dange Shuni LGA, with the number at each level? | ✅ |
| lf05 | Ina nufin duka makarantun: firamare, ƙaramar sakandare, babbar sakandare da IQS | statistics / lga / none / clarification | How many schools are there in Dange Shuni LGA in total, broken down by primary, junior secondary, senior secondary and IQS? | ✅ |
| lf06 | Makarantu nake magana ba kasafi ba | statistics / lga / none / correction | How many schools are there in total in Dange Shuni LGA, at all levels? | ✅ |
| lf07 | I asked about people, not hectares of land | statistics / state / past / correction | How many people were affected by floods in Sokoto State in 2024? | ✅ |
| lf08 | I mean the 2025 budget | place_budget / lga / year / correction | What is the government budgeting for my LGA (Wamakko LGA) in the 2025 budget? | ✅ |
| lf09 | I mean all of them, PHCs and dispensaries too | facility / lga / none / clarification | How many health facilities of all levels, including PHCs, dispensaries and hospitals, are in Wamakko LGA? | ✅ |
| lf10 | Ok so which LGAs does it name? | statistics / document / year / follow_up | Which LGAs does the NEMA situation report of 26 September 2025 name as affected by floods in Sokoto State? | ✅ |
