# Conversation understanding eval (open)

104 cases: **104 right**, 0 wrong. Latency median 2.30 s, p90 3.65 s; cost $0.0051 ($0.0025 per message; 2 re-read with --only, the rest kept from the last run).

| Id | Message | Capability / level / time / kind | Restatement | Wrong |
|---|---|---|---|---|
| u01 | But Uduth is closer to me | facility / facility / none / correction | Is UDUTH (Usmanu Danfodiyo University Teaching Hospital) closer to my farm (the pin) than the hospitals previously listed? | ✅ |
| u02 | Has this area ever flooded | place_history / ward / past / follow_up | Has my ward ever been flooded in the past? | ✅ |
| u03 | Has this land ever flooded? | place_history / pin / past / follow_up | Has my farm (the pin) ever flooded? | ✅ |
| u04 | What about the rain this season, will it flood? | hazard / pin / forecast / follow_up | Will my farm (the pin) flood this rainy season and what is the rainfall forecast for my area? | ✅ |
| u05 | How much of that has actually been spent? | place_budget / lga / year / follow_up | How much of the 2026 budgeted amount for my LGA has actually been spent? | ✅ |
| u06 | And the past three years? | place_budget / lga / span / follow_up | What did Sokoto State budget for my LGA in each of the past three years (2023, 2024, 2025)? | ✅ |
| u07 | How do I get to the second one? | facility / facility / none / follow_up | How do I get to Gidan Bubu Health Post from my farm (the pin)? | ✅ |
| u08 | Does Kalambaina PHC have enough nurses? | statistics / facility / now / follow_up | Does Kalambaina PHC have enough nurses? | ✅ |
| u09 | Amma UDUTH ya fi kusa da ni | facility / facility / none / correction | Is UDUTH the nearest health facility to my farm (the pin) and how far is it? | ✅ |
| u10 | Shin wannan gonar ta taba cika da ruwa? | place_history / pin / past / follow_up | Has my farm (the pin) ever been flooded? | ✅ |
| u11 | Za a yi ambaliya a nan bana? | hazard / pin / forecast / follow_up | Will my farm (the pin) be flooded this year? | ✅ |
| u12 | Nawa aka kashe daga ciki? | place_budget / lga / year / follow_up | How much of the N79.98 billion allocated to my LGA (Wamakko) in the 2026 budget has been spent? | ✅ |
| u13 | And how much of it was spent by June? | budget / sector / year / follow_up | How much of the 2026 health budget for Sokoto State was spent by June? | ✅ |
| u14 | That's not right, the health budget is much smaller | budget / sector / year / correction | What was budgeted for health in Sokoto State in 2026? | ✅ |
| u15 | What about in the DHS? | statistics / document / none / follow_up | What share of children are fully vaccinated in Sokoto State according to the DHS? | ✅ |
| u16 | What about the dust? | hazard / pin / forecast / follow_up | What will the dust / air quality be like tomorrow at my farm (the pin)? | ✅ |
| u17 | Which hospital near me can I go to if my child has trouble breathing? | facility / facility / none / new | Which hospital near my farm (the pin) can I go to if my child has trouble breathing? | ✅ |
| u18 | How much did the government budget for Specialist Hospital this year? | budget / facility / year / follow_up | How much did Sokoto State Government budget for Specialist Hospital Sokoto in 2026? | ✅ |
| u19 | And is it getting greener over the years? | place_history / pin / span / follow_up | Has my farm (the pin) become greener over the years? | ✅ |
| u20 | What about the whole of Wamakko? | place_history / lga / past / follow_up | Has my LGA (Wamakko LGA) ever been flooded? | ✅ |
| u21 | Is there any budget for irrigation there? | place_budget / lga / none / follow_up | Is there any budget for irrigation in my LGA? | ✅ |
| u22 | What is the state doing about it in the 2026 budget? | budget / state / year / follow_up | What is Sokoto State doing about out-of-school children in the 2026 budget? | ✅ |
| u23 | Send me the full brief | deep / state / none / follow_up | Send the full brief on the state of PHCs in Sokoto State | ✅ |
| u24 | Thanks | conversation / none / none / chitchat | The user says thanks (conversation) | ✅ |
| u25 | Is Arkilla open at night? | facility / facility / now / follow_up | Is Arkilla PHC open at night? | ✅ |
| u26 | Last year was there flooding in my LGA? | place_history / lga / past / follow_up | Was my LGA flooded last year? | ✅ |
| u27 | Na farko, yaya zan je can? | facility / facility / none / follow_up | How do I get to Specialist Hospital Sokoto from my farm (the pin)? | ✅ |
| u28 | Nawa ne a karamar hukumata? | place_budget / lga / year / follow_up | What amount of the 2026 Sokoto State education budget is allocated to my LGA (Wamakko LGA)? | ✅ |
| u29 | Is there anything for farmers? | place_budget / lga / year / follow_up | Is there anything in the 2026 budget for farmers in my LGA (Wamakko LGA)? | ✅ |
| u30 | My neighbour says it flooded in 2020, are you sure? | place_history / pin / past / correction | Has my farm (the pin) flooded in 2020? | ✅ |
| f01 | How many medical officers do PHCs need in Sokoto? | statistics / state / none / new | How many medical officers are needed in PHCs in Sokoto State? | ✅ |
| f02 | What's the state of PHCs in Sokoto? | deep / state / now / new | What is the overall state of PHCs (primary health centres) in Sokoto State? | ✅ |
| f03 | tell me about health in Sokoto | deep / state / none / new | Give me a broad overview of health in Sokoto State | ✅ |
| f04 | what's happening in my area? | deep / ward / none / new | Give me a broad overview of what is happening in my ward | ✅ |
| f05 | How many PHCs are in Tureta? | facility / lga / none / new | How many PHCs are in Tureta LGA? | ✅ |
| f06 | How much did Sokoto spend on education last year? | budget / sector / year / new | How much did Sokoto State spend on education in 2025? | ✅ |
| f07 | Is it safe to plant this week, will it rain? | hazard / pin / forecast / new | Will it rain this week at my farm (the pin) in my ward, Wamakko LGA and is it safe to plant? | ✅ |
| f08 | Nawa aka ware wa ma'aikatar lafiya a 2026? | budget / agency / year / new | How much was allocated to the Ministry of Health in Sokoto State in 2026? | ✅ |
| f09 | Ina asibiti mafi kusa da ni? | facility / pin / none / new | Where is the nearest health facility to my farm (the pin) in Kalambaina ward, Wamakko LGA? | ✅ |
| f10 | Gonata ta taba yin ambaliya? | place_history / pin / past / new | Has my farm (the pin) ever been flooded? | ✅ |
| f11 | What does the MICS say about birth registration in Sokoto? | statistics / document / none / new | What does the MICS report say about birth registration coverage in Sokoto State? | ✅ |
| f12 | Alert me when there will be floods in Goronyo | alerts / lga / forecast / new | Sign me up for alerts when floods are forecast for Goronyo LGA | ✅ |
| f13 | What projects is the government doing in Tambuwal? | place_budget / lga / none / new | What projects is the Sokoto State government doing in Tambuwal LGA? | ✅ |
| f14 | Sannu | conversation / none / none / chitchat | Greeting saying hello | ✅ |
| f15 | Yaya yanayin ilimi a Sokoto? | deep / sector / none / new | What is the state of education in Sokoto State? | ✅ |
| c01 | Who are you? | conversation / none / none / chitchat | who is Kasafi and what can you do | ✅ |
| c02 | Kai wanene? | conversation / none / none / chitchat | Who are you? | ✅ |
| c03 | Me za ka iya yi? | conversation / none / none / chitchat | What can you do as Kasafi? | ✅ |
| c04 | What can you do? | conversation / none / none / chitchat | What can Kasafi do? | ✅ |
| c05 | How does this work? | conversation / none / none / chitchat | Explain how Kasafi works and what help it can provide | ✅ |
| c06 | Who made you? | conversation / none / none / chitchat | Who made Kasafi? | ✅ |
| c07 | Is this a bot? | conversation / none / none / chitchat | Is Kasafi a bot? | ✅ |
| c08 | Can you speak Hausa? | conversation / none / none / chitchat | Can Kasafi speak Hausa? | ✅ |
| c09 | Na gode | conversation / none / none / chitchat | User is thanking Kasafi | ✅ |
| c10 | Assalamu alaikum | conversation / none / none / chitchat | greeting to Kasafi | ✅ |
| c11 | Hello | conversation / none / none / chitchat | user greets Kasafi | ✅ |
| c12 | Sai anjima | conversation / none / none / chitchat | The user is saying goodbye (see you later) and ending the conversation for now | ✅ |
| c13 | Thank you, bye | conversation / none / none / chitchat | User is saying thank you and goodbye | ✅ |
| c14 | help | conversation / none / none / chitchat | What can Kasafi do and how to use it | ✅ |
| c15 | Ina kwana | conversation / none / none / chitchat | Greeting | ✅ |
| c16 | Wa ya yi ka? | conversation / none / none / chitchat | Who made you (Kasafi)? | ✅ |
| c17 | Kana jin Hausa? | conversation / none / none / chitchat | whether the assistant can understand and speak Hausa | ✅ |
| c18 | Mutum ne kai ko na'ura? | conversation / none / none / chitchat | Are you a human or a machine? | ✅ |
| c19 | Yaya kake aiki? | conversation / none / none / chitchat | How does Kasafi work and what can you help me with? | ✅ |
| c20 | But uduth is closer to me | facility / facility / none / correction | UDUTH (Usmanu Danfodiyo University Teaching Hospital) is the nearest health facility to me in my LGA (Wamakko LGA) | ✅ |
| m01 | Where can my wife deliver a baby? | facility / pin / none / new | Where is the nearest health facility to my farm (the pin) in Kalambaina ward, Wamakko LGA where my wife can deliver a baby? | ✅ |
| m02 | Matata na naƙuda, ina zan kai ta? | facility / facility / now / new | Where should I take my wife who is in labour near my farm (the pin) in my ward, Wamakko LGA, Sokoto State? | ✅ |
| m03 | Nearest place for antenatal care | facility / pin / none / new | What is the nearest health facility for antenatal care to my farm (the pin) in my ward, Wamakko LGA? | ✅ |
| m04 | A ina matata za ta haihu? | facility / pin / none / new | Where can my wife give birth near my farm (the pin) in Kalambaina ward, Wamakko LGA? | ✅ |
| m05 | Is there anywhere I can deliver a baby around here? | facility / pin / none / new | Where is the nearest health facility where I can deliver a baby near my farm (the pin) in my ward in Wamakko LGA? | ✅ |
| m06 | Where can I take my sick child? | facility / pin / now / new | Where is the nearest health facility where I can take my sick child near my farm (the pin) in Kalambaina ward, Wamakko LGA? | ✅ |
| m07 | Ina asibitin gwamnati mafi kusa? | facility / pin / none / new | Where is the nearest government hospital to my farm (the pin)? | ✅ |
| m08 | Is there a private clinic near me? | facility / pin / none / new | What is the nearest private clinic to my farm (the pin) in my ward, Wamakko LGA? | ✅ |
| m09 | Only government ones | facility / facility / none / follow_up | Where can my wife deliver a baby at government-owned facilities nearest to my farm (the pin) in my ward, Wamakko LGA? | ✅ |
| m10 | Anything for schools? | place_budget / lga / year / follow_up | Is there anything for schools for my LGA (Wamakko) in the 2026 budget? | ✅ |
| k01 | menu | conversation / none / none / menu | Show the main menu of what Kasafi can do | ✅ |
| k02 | zaɓi | conversation / none / none / menu | User wants to see the menu of options | ✅ |
| k03 | Nuna min zaɓuɓɓuka | conversation / none / none / menu | Show me the menu of options | ✅ |
| n01 | How many people were affected by floods in Sokoto State in October 2024? | statistics / state / past / new | How many people in Sokoto State were affected by floods in October 2024? | ✅ |
| n02 | How many people were displaced by the 2024 floods in Sokoto? | statistics / state / past / new | How many people were displaced by the 2024 floods in Sokoto State? | ✅ |
| n03 | How many houses were destroyed by flooding in Sokoto in 2025? | statistics / state / year / new | How many houses were destroyed by flooding in Sokoto State in 2025? | ✅ |
| n04 | Was Wamakko LGA affected by floods in 2025, according to NEMA? | statistics / lga / year / new | Was Wamakko LGA affected by floods in 2025 according to NEMA? | ✅ |
| n05 | Which LGAs in Sokoto State were affected by floods in 2025, according to NEMA? | statistics / document / year / new | Which LGAs in Sokoto State were affected by floods in 2025 according to NEMA reports? | ✅ |
| n06 | Mutane nawa ambaliyar ruwa ta shafa a Jihar Sokoto a 2025, a cewar NEMA? | statistics / state / year / new | How many people were affected by floods in Sokoto State in 2025 according to NEMA? | ✅ |
| n07 | Mutane nawa suka rasa matsugunansu saboda ambaliya a Sokoto a 2024? | statistics / state / year / new | How many people were displaced due to flooding in Sokoto State in 2024? | ✅ |
| n08 | Gidaje nawa ambaliya ta rushe a Sokoto a 2024? | statistics / state / past / new | How many houses were destroyed by floods in Sokoto State in 2024? | ✅ |
| n09 | How bad were the 2024 floods in Sokoto? | statistics / state / past / new | How bad were the 2024 floods in Sokoto State overall? | ✅ |
| n10 | Yaya girman ambaliyar 2024 a Jihar Sokoto? | statistics / state / past / new | How severe/extensive were the 2024 floods in Sokoto State? | ✅ |
| n11 | How many people died in floods in Sokoto in 2024? | statistics / state / past / new | How many people died in floods in Sokoto State in 2024? | ✅ |
| n12 | How much of my ward was under water in 2024? | place_history / ward / past / follow_up | How much of my ward (Kalambaina) was under water in 2024? | ✅ |
| n13 | Which wards of Wamakko flooded most in 2022? | place_history / lga / year / new | Which wards of Wamakko LGA flooded most in 2022? | ✅ |
| n14 | Ruwa ya taɓa rufe gonata? | place_history / pin / past / new | Has my farm (the pin) ever been flooded? | ✅ |
| n15 | What does the MICS report say about birth registration in Sokoto? | statistics / document / none / new | What does the MICS report say about birth registration in Sokoto State? | ✅ |
| n16 | According to NiMet, when will the rains end in my LGA this year? | hazard / lga / forecast / new | According to NiMet, when will the rains end in my LGA this year? | ✅ |
| lf01 | How many schools are in Dange Shuni | statistics / lga / none / new | How many schools are in Dange Shuni LGA in total, with numbers at each level? | ✅ |
| lf02 | I mean all the total schools primary, senior secondary and junior secondary and IQS | statistics / lga / none / clarification | What is the total number of schools (primary, junior secondary, senior secondary and IQS) in my LGA Dange Shuni, with the number at each level? | ✅ |
| lf03 | Am talking about schools not budget | statistics / lga / none / correction | How many schools (primary, junior secondary, senior secondary and IQS) are in Dange Shuni LGA at each level? | ✅ |
| lf04 | Makarantu nawa ne a Dange Shuni? | statistics / lga / none / new | How many schools are there in Dange Shuni LGA, counting all levels with breakdown by level? | ✅ |
| lf05 | Ina nufin duka makarantun: firamare, ƙaramar sakandare, babbar sakandare da IQS | statistics / lga / none / clarification | How many schools are there in total in Dange Shuni LGA, with the numbers for primary, junior secondary, senior secondary and IQS? | ✅ |
| lf06 | Makarantu nake magana ba kasafi ba | statistics / lga / none / correction | How many schools in total are there in Dange Shuni LGA, with the number at each level (primary, JSS, SSS and IQS)? | ✅ |
| lf07 | I asked about people, not hectares of land | statistics / state / past / correction | How many people were affected by floods in Sokoto State in 2024? | ✅ |
| lf08 | I mean the 2025 budget | place_budget / lga / year / clarification | What is the government budgeting for my LGA (Wamakko LGA) in 2025? | ✅ |
| lf09 | I mean all of them, PHCs and dispensaries too | facility / lga / none / clarification | How many health facilities in total (all levels including hospitals, PHCs and dispensaries) are in Wamakko LGA, with the number at each level? | ✅ |
| lf10 | Ok so which LGAs does it name? | statistics / document / year / follow_up | Which LGAs does NEMA's situation report of 26 September 2025 name as affected by floods in Sokoto State? | ✅ |
