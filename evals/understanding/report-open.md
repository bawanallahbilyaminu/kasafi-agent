# Conversation understanding eval (open)

108 cases: **108 right**, 0 wrong. Latency median 2.24 s, p90 3.72 s; cost $0.0032 ($0.0032 per message; 1 re-read with --only, the rest kept from the last run).

| Id | Message | Capability / level / time / kind | Restatement | Wrong |
|---|---|---|---|---|
| u01 | But Uduth is closer to me | facility / facility / none / correction | Is Usmanu Danfodiyo University Teaching Hospital (UDUTH) closer to my farm (the pin) in Kalambaina ward, Wamakko LGA than Specialist Hospital Sokoto and what is its road distance and time? | ✅ |
| u02 | Has this area ever flooded | place_history / ward / past / follow_up | Has my ward ever been flooded in the past? | ✅ |
| u03 | Has this land ever flooded? | place_history / pin / past / follow_up | Has my farm (the pin) ever been flooded? | ✅ |
| u04 | What about the rain this season, will it flood? | hazard / pin / forecast / follow_up | Will my farm (the pin) flood from rain this season? | ✅ |
| u05 | How much of that has actually been spent? | place_budget / lga / year / follow_up | How much of the 2026 budget for my LGA (Wamakko LGA) has actually been spent? | ✅ |
| u06 | And the past three years? | place_budget / lga / span / follow_up | What was the government budget for capital projects in my LGA in the past three years (2023-2025)? | ✅ |
| u07 | How do I get to the second one? | facility / facility / none / follow_up | How do I get from my farm (the pin) to Gidan Bubu Health Post (the second nearest clinic)? | ✅ |
| u08 | Does Kalambaina PHC have enough nurses? | statistics / facility / now / follow_up | Does Kalambaina PHC in Wamakko LGA have enough nurses? | ✅ |
| u09 | Amma UDUTH ya fi kusa da ni | facility / facility / none / correction | Is UDUTH the nearest hospital to my farm (the pin) in my ward in Wamakko LGA? | ✅ |
| u10 | Shin wannan gonar ta taba cika da ruwa? | place_history / pin / past / follow_up | Has my farm (the pin) ever been flooded? | ✅ |
| u11 | Za a yi ambaliya a nan bana? | hazard / pin / forecast / follow_up | Will my farm (the pin) be flooded this year? | ✅ |
| u12 | Nawa aka kashe daga ciki? | place_budget / lga / year / follow_up | How much of the budget allocated to my LGA in 2026 has been spent? | ✅ |
| u13 | And how much of it was spent by June? | budget / sector / year / follow_up | How much of the 2026 health budget for Sokoto State was spent by June 2026? | ✅ |
| u14 | That's not right, the health budget is much smaller | budget / sector / year / correction | What was budgeted for health in Sokoto State in 2026? | ✅ |
| u15 | What about in the DHS? | statistics / document / none / follow_up | What share of children are fully vaccinated in Sokoto State according to the DHS? | ✅ |
| u16 | What about the dust? | hazard / pin / forecast / follow_up | Will there be dust/dust haze at my farm (the pin) in Kalambaina ward tomorrow? | ✅ |
| u17 | Which hospital near me can I go to if my child has trouble breathing? | facility / pin / none / new | Which hospital near my farm (the pin) can I go to if my child has trouble breathing? | ✅ |
| u18 | How much did the government budget for Specialist Hospital this year? | budget / facility / year / follow_up | How much did Sokoto State government budget for Specialist Hospital Sokoto in 2026? | ✅ |
| u19 | And is it getting greener over the years? | place_history / pin / past / follow_up | Is my farm (the pin) getting greener over the years? | ✅ |
| u20 | What about the whole of Wamakko? | place_history / lga / past / follow_up | Has my LGA ever flooded? | ✅ |
| u21 | Is there any budget for irrigation there? | place_budget / lga / none / follow_up | Is there any budget for irrigation in my LGA? | ✅ |
| u22 | What is the state doing about it in the 2026 budget? | budget / sector / year / follow_up | What is Sokoto State doing about out-of-school children in the 2026 budget? | ✅ |
| u23 | Send me the full brief | deep / state / none / follow_up | Send the full brief on the state of primary health care (PHC) facilities in Sokoto State | ✅ |
| u24 | Thanks | conversation / none / none / chitchat | Thanks for the nearest PHC information | ✅ |
| u25 | Is Arkilla open at night? | facility / facility / now / follow_up | Is Arkilla PHC near my farm (the pin) in Kalambaina ward, Wamakko LGA open at night? | ✅ |
| u26 | Last year was there flooding in my LGA? | place_history / lga / past / follow_up | Was my LGA (Wamakko LGA) flooded last year (2025)? | ✅ |
| u27 | Na farko, yaya zan je can? | facility / facility / none / follow_up | How do I get to Specialist Hospital Sokoto from my farm (the pin) in my ward, Wamakko LGA? | ✅ |
| u28 | Nawa ne a karamar hukumata? | place_budget / lga / year / follow_up | How much of the 2026 education budget is allocated to my LGA? | ✅ |
| u29 | Is there anything for farmers? | place_budget / lga / year / follow_up | What is the 2026 budget allocating for farmers in my LGA? | ✅ |
| u30 | My neighbour says it flooded in 2020, are you sure? | place_history / pin / past / correction | Did my farm (the pin) ever flood, specifically did it flood in 2020 as my neighbour says? | ✅ |
| f01 | How many medical officers do PHCs need in Sokoto? | statistics / state / none / new | How many medical officers do PHCs need in Sokoto State? | ✅ |
| f02 | What's the state of PHCs in Sokoto? | deep / state / none / new | What is the state of PHCs in Sokoto State? | ✅ |
| f03 | tell me about health in Sokoto | deep / state / none / new | Tell me about the state of health in Sokoto State | ✅ |
| f04 | what's happening in my area? | deep / ward / now / new | Give a broad overview of what is happening in my ward (Kalambaina ward in Wamakko LGA, Sokoto State) | ✅ |
| f05 | How many PHCs are in Tureta? | facility / lga / none / new | How many PHCs are there in Tureta LGA? | ✅ |
| f06 | How much did Sokoto spend on education last year? | budget / sector / year / new | How much did Sokoto State spend on education in 2025? | ✅ |
| f07 | Is it safe to plant this week, will it rain? | hazard / pin / forecast / new | Will it rain this week at my farm (the pin) in my ward in my LGA and is it safe to plant? | ✅ |
| f08 | Nawa aka ware wa ma'aikatar lafiya a 2026? | budget / agency / year / new | How much was allocated to the Ministry of Health in Sokoto State in the 2026 budget? | ✅ |
| f09 | Ina asibiti mafi kusa da ni? | facility / pin / none / new | Where is the nearest health facility to my farm (the pin)? | ✅ |
| f10 | Gonata ta taba yin ambaliya? | place_history / pin / past / new | Has my farm (the pin) ever been flooded? | ✅ |
| f11 | What does the MICS say about birth registration in Sokoto? | statistics / document / none / new | What does the MICS report say about birth registration in Sokoto State? | ✅ |
| f12 | Alert me when there will be floods in Goronyo | alerts / lga / forecast / new | Subscribe me to flood alerts for Goronyo LGA in Sokoto State | ✅ |
| f13 | What projects is the government doing in Tambuwal? | place_budget / lga / none / new | What projects is Sokoto State government doing/budgeting in Tambuwal LGA? | ✅ |
| f14 | Sannu | conversation / none / none / chitchat | User says hello (Sannu) | ✅ |
| f15 | Yaya yanayin ilimi a Sokoto? | deep / state / none / new | What is the state of education in Sokoto State? | ✅ |
| c01 | Who are you? | conversation / none / none / chitchat | Who are you? | ✅ |
| c02 | Kai wanene? | conversation / none / none / chitchat | Who are you? | ✅ |
| c03 | Me za ka iya yi? | conversation / none / none / chitchat | What can you (Kasafi) do? | ✅ |
| c04 | What can you do? | conversation / none / none / chitchat | What can Kasafi do? | ✅ |
| c05 | How does this work? | conversation / none / none / chitchat | How does Kasafi work and what can it do? | ✅ |
| c06 | Who made you? | conversation / none / none / chitchat | Who made Kasafi? | ✅ |
| c07 | Is this a bot? | conversation / none / none / chitchat | Is Kasafi a bot? | ✅ |
| c08 | Can you speak Hausa? | conversation / none / none / chitchat | Can Kasafi speak Hausa? | ✅ |
| c09 | Na gode | conversation / none / none / chitchat | User is saying thank you | ✅ |
| c10 | Assalamu alaikum | conversation / none / none / chitchat | Greeting exchanged | ✅ |
| c11 | Hello | conversation / none / none / chitchat | User says hello | ✅ |
| c12 | Sai anjima | conversation / none / none / chitchat | See you later - goodbye for now | ✅ |
| c13 | Thank you, bye | conversation / none / none / chitchat | Thank you and goodbye | ✅ |
| c14 | help | conversation / none / none / chitchat | User asks for help / what Kasafi can do. | ✅ |
| c15 | Ina kwana | conversation / none / none / chitchat | Greeting in Hausa | ✅ |
| c16 | Wa ya yi ka? | conversation / none / none / chitchat | Who made you (Kasafi)? | ✅ |
| c17 | Kana jin Hausa? | conversation / none / none / chitchat | The user asks if Kasafi can understand and speak Hausa | ✅ |
| c18 | Mutum ne kai ko na'ura? | conversation / none / none / chitchat | Is Kasafi a human or a machine/bot? | ✅ |
| c19 | Yaya kake aiki? | conversation / none / none / chitchat | How do you (Kasafi) work? | ✅ |
| c20 | But uduth is closer to me | facility / facility / none / correction | Isn't Usmanu Danfodiyo University Teaching Hospital (UDUTH) the closest hospital to me in my LGA? | ✅ |
| m01 | Where can my wife deliver a baby? | facility / pin / none / new | Where can my wife deliver a baby near my farm (the pin)? | ✅ |
| m02 | Matata na naƙuda, ina zan kai ta? | facility / facility / now / new | Where should I take my wife who is in labour from my farm (the pin) in my ward, my LGA? | ✅ |
| m03 | Nearest place for antenatal care | facility / pin / none / new | Where is the nearest health facility to my farm (the pin) for antenatal care? | ✅ |
| m04 | A ina matata za ta haihu? | facility / pin / now / new | Where can my wife give birth/deliver nearest to my farm (the pin) in my ward, my LGA? | ✅ |
| m05 | Is there anywhere I can deliver a baby around here? | facility / pin / none / new | Where is the nearest health facility to my farm (the pin) in my ward where a baby can be delivered? | ✅ |
| m06 | Where can I take my sick child? | facility / facility / now / new | Where is the nearest health facility where I can take my sick child from my farm (the pin) in my ward, Wamakko LGA? | ✅ |
| m07 | Ina asibitin gwamnati mafi kusa? | facility / pin / none / new | What is the nearest government hospital to my farm (the pin) in my ward in Wamakko LGA? | ✅ |
| m08 | Is there a private clinic near me? | facility / pin / none / new | What is the nearest private clinic to my farm (the pin)? | ✅ |
| m09 | Only government ones | facility / pin / none / correction | Where can my wife deliver a baby near my farm (the pin) at government-owned facilities? | ✅ |
| m10 | Anything for schools? | place_budget / lga / year / follow_up | What is the government budgeting for schools in my LGA in the 2026 budget? | ✅ |
| k01 | menu | conversation / none / none / menu | user asks to see the menu of options | ✅ |
| k02 | zaɓi | conversation / none / none / menu | Show me the menu of what Kasafi can do | ✅ |
| k03 | Nuna min zaɓuɓɓuka | conversation / none / none / menu | Show me the menu options. | ✅ |
| n01 | How many people were affected by floods in Sokoto State in October 2024? | statistics / state / past / new | How many people were affected by floods in Sokoto State in October 2024? | ✅ |
| n02 | How many people were displaced by the 2024 floods in Sokoto? | statistics / state / year / new | How many people were displaced by the 2024 floods in Sokoto State? | ✅ |
| n03 | How many houses were destroyed by flooding in Sokoto in 2025? | statistics / state / year / new | How many houses were destroyed by flooding in Sokoto State in 2025? | ✅ |
| n04 | Was Wamakko LGA affected by floods in 2025, according to NEMA? | statistics / lga / year / new | Was Wamakko LGA affected by floods in 2025 according to NEMA? | ✅ |
| n05 | Which LGAs in Sokoto State were affected by floods in 2025, according to NEMA? | statistics / document / year / new | Which LGAs in Sokoto State were affected by floods in 2025 according to NEMA? | ✅ |
| n06 | Mutane nawa ambaliyar ruwa ta shafa a Jihar Sokoto a 2025, a cewar NEMA? | statistics / state / year / new | How many people were affected by floods in Sokoto State in 2025 according to NEMA? | ✅ |
| n07 | Mutane nawa suka rasa matsugunansu saboda ambaliya a Sokoto a 2024? | statistics / state / year / new | How many people were displaced due to floods in Sokoto State in 2024? | ✅ |
| n08 | Gidaje nawa ambaliya ta rushe a Sokoto a 2024? | statistics / state / year / new | How many houses were destroyed by floods in Sokoto State in 2024? | ✅ |
| n09 | How bad were the 2024 floods in Sokoto? | statistics / state / past / new | What was the impact of the 2024 floods in Sokoto State? | ✅ |
| n10 | Yaya girman ambaliyar 2024 a Jihar Sokoto? | statistics / state / year / new | How severe and extensive were the 2024 floods in Sokoto State? | ✅ |
| n11 | How many people died in floods in Sokoto in 2024? | statistics / state / year / new | How many people died due to floods in Sokoto State in 2024? | ✅ |
| n12 | How much of my ward was under water in 2024? | place_history / ward / past / follow_up | How much of my ward was flooded / under water in 2024? | ✅ |
| n13 | Which wards of Wamakko flooded most in 2022? | place_history / lga / past / new | Which wards of Wamakko LGA were most flooded in 2022? | ✅ |
| n14 | Ruwa ya taɓa rufe gonata? | place_history / pin / past / follow_up | Has flood water ever covered my farm (the pin) in Kalambaina ward, Wamakko LGA? | ✅ |
| n15 | What does the MICS report say about birth registration in Sokoto? | statistics / document / none / new | What does the MICS report say about birth registration in Sokoto State? | ✅ |
| n16 | According to NiMet, when will the rains end in my LGA this year? | hazard / lga / forecast / new | According to NiMet, when will the rains end in my LGA (Wamakko LGA) this year (2026)? | ✅ |
| lf11 | According to the Multiple Indicator Cluster Survey (MICS) by NBS and UNICEF, what are the gaps in child healthcare and civil registration for Sokoto State? | statistics / document / none / new | What are the gaps in child healthcare and civil registration for Sokoto State according to the Multiple Indicator Cluster Survey (MICS) by NBS and UNICEF? | ✅ |
| lf12 | A cewar MICS na NBS da UNICEF, waɗanne gibi ne ke cikin kula da lafiyar yara da rajistar haihuwa a Jihar Sokoto? | statistics / document / year / new | According to the NBS and UNICEF MICS, what gaps exist in child healthcare and birth registration in Sokoto State? | ✅ |
| lf13 | Birth registration in Sokoto: what did MICS 2021 and NDHS 2024 each find, and can the two be compared? | statistics / document / span / new | What did MICS 2021 and NDHS 2024 each find about birth registration in Sokoto State and can the two surveys be directly compared? | ✅ |
| lf14 | What's the state of child health in Sokoto? | deep / state / none / new | What is the state of child health in Sokoto State? | ✅ |
| lf01 | How many schools are in Dange Shuni | statistics / lga / none / new | How many schools are in Dange Shuni LGA, at each level (primary, JSS, SSS, IQS) and in total? | ✅ |
| lf02 | I mean all the total schools primary, senior secondary and junior secondary and IQS | statistics / lga / none / clarification | How many schools are there in total in Dange Shuni LGA, including public and private primary, junior secondary, senior secondary and IQS, with the number at each level? | ✅ |
| lf03 | Am talking about schools not budget | statistics / lga / none / correction | What is the total number of schools in my LGA (Dange Shuni LGA) broken down by primary, junior secondary, senior secondary and IQS? | ✅ |
| lf04 | Makarantu nawa ne a Dange Shuni? | statistics / lga / none / new | How many schools are there in total in Dange Shuni LGA, with breakdown by level? | ✅ |
| lf05 | Ina nufin duka makarantun: firamare, ƙaramar sakandare, babbar sakandare da IQS | statistics / lga / none / clarification | How many schools are in Dange Shuni LGA in total, including primary, JSS, SSS and IQS, with the number at each level? | ✅ |
| lf06 | Makarantu nake magana ba kasafi ba | statistics / lga / none / correction | How many schools in total at all levels (primary, JSS, SSS and IQS) are there in my LGA Dange Shuni? | ✅ |
| lf07 | I asked about people, not hectares of land | statistics / state / year / correction | How many people were affected by floods in Sokoto State in 2024? | ✅ |
| lf08 | I mean the 2025 budget | place_budget / lga / year / correction | What does the 2025 budget allocate to my LGA? | ✅ |
| lf09 | I mean all of them, PHCs and dispensaries too | facility / lga / none / clarification | How many health facilities at all levels (hospitals, PHCs, dispensaries, etc.) are in Wamakko LGA? | ✅ |
| lf10 | Ok so which LGAs does it name? | statistics / document / year / follow_up | Which LGAs in Sokoto State does the NEMA situation report of 26 September 2025 name as affected by floods? | ✅ |
