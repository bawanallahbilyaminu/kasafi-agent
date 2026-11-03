# Conversation understanding eval (open)

94 cases: **94 right**, 0 wrong. Latency median 2.22 s, p90 3.12 s; cost $0.0038 ($0.0019 per message; 2 re-read with --only, the rest kept from the last run).

| Id | Message | Capability / level / time / kind | Restatement | Wrong |
|---|---|---|---|---|
| u01 | But Uduth is closer to me | facility / facility / none / correction | Is Usmanu Danfodiyo University Teaching Hospital (UDUTH) the nearest hospital to my farm (the pin)? | ✅ |
| u02 | Has this area ever flooded | place_history / ward / past / follow_up | Has my ward ever flooded in the past? | ✅ |
| u03 | Has this land ever flooded? | place_history / pin / past / follow_up | Has my farm (the pin) ever flooded? | ✅ |
| u04 | What about the rain this season, will it flood? | hazard / pin / forecast / follow_up | Will my farm (the pin) flood this rainy season and what is the rain forecast for it? | ✅ |
| u05 | How much of that has actually been spent? | place_budget / lga / year / follow_up | How much of the 2026 budgeted amount for my LGA has actually been spent? | ✅ |
| u06 | And the past three years? | place_budget / lga / span / follow_up | What did the government budget for my LGA in the past three years (2023-2025)? | ✅ |
| u07 | How do I get to the second one? | facility / facility / none / follow_up | How do I get to Gidan Bubu Health Post from my farm (the pin)? | ✅ |
| u08 | Does Kalambaina PHC have enough nurses? | statistics / facility / now / follow_up | Does Kalambaina PHC have enough nurses to meet staffing standards? | ✅ |
| u09 | Amma UDUTH ya fi kusa da ni | facility / facility / now / correction | UDUTH is closer to my farm (the pin) than the previously listed nearest facilities | ✅ |
| u10 | Shin wannan gonar ta taba cika da ruwa? | place_history / pin / past / follow_up | Has my farm (the pin) ever been flooded? | ✅ |
| u11 | Za a yi ambaliya a nan bana? | hazard / pin / forecast / follow_up | Will my farm (the pin) be flooded this year? | ✅ |
| u12 | Nawa aka kashe daga ciki? | place_budget / lga / year / follow_up | How much of the 2026 budget allocated to my LGA has been spent? | ✅ |
| u13 | And how much of it was spent by June? | budget / sector / span / follow_up | How much of Sokoto State's 2026 health budget was spent by June 2026? | ✅ |
| u14 | That's not right, the health budget is much smaller | budget / sector / year / correction | What is the correct amount budgeted for health in Sokoto State in 2026? | ✅ |
| u15 | What about in the DHS? | statistics / document / none / follow_up | What share of children age 12-23 months in Sokoto State are fully vaccinated according to the DHS (NDHS)? | ✅ |
| u16 | What about the dust? | hazard / pin / forecast / follow_up | What will the dust/air quality be like tomorrow at my farm (the pin)? | ✅ |
| u17 | Which hospital near me can I go to if my child has trouble breathing? | facility / pin / none / new | Which hospital nearest to my farm (the pin) can I go to if my child has trouble breathing? | ✅ |
| u18 | How much did the government budget for Specialist Hospital this year? | budget / facility / year / follow_up | How much did the Sokoto State government budget for Specialist Hospital Sokoto in 2026? | ✅ |
| u19 | And is it getting greener over the years? | place_history / pin / past / follow_up | Is my farm (the pin) getting greener over the years? | ✅ |
| u20 | What about the whole of Wamakko? | place_history / lga / past / follow_up | Has my LGA ever flooded? | ✅ |
| u21 | Is there any budget for irrigation there? | place_budget / lga / none / follow_up | Is there any budget for irrigation allocated to my LGA (Wamakko)? | ✅ |
| u22 | What is the state doing about it in the 2026 budget? | budget / state / year / follow_up | What is Sokoto State doing about out-of-school children in the 2026 budget? | ✅ |
| u23 | Send me the full brief | deep / state / none / follow_up | Send me the full brief on the state of PHCs in Sokoto State | ✅ |
| u24 | Thanks | conversation / none / none / chitchat | Thanks for the previous answer about the nearest PHC to my farm (the pin) in my ward, Wamakko LGA – no new request | ✅ |
| u25 | Is Arkilla open at night? | facility / facility / none / follow_up | Is Arkilla PHC near my farm (the pin) open at night? | ✅ |
| u26 | Last year was there flooding in my LGA? | place_history / lga / past / follow_up | Was there flooding in my LGA last year (2025)? | ✅ |
| u27 | Na farko, yaya zan je can? | facility / facility / none / follow_up | How do I get to the first one, Specialist Hospital Sokoto, from my farm (the pin)? | ✅ |
| u28 | Nawa ne a karamar hukumata? | place_budget / lga / year / follow_up | How much of the 2026 education budget is allocated to my LGA? | ✅ |
| u29 | Is there anything for farmers? | place_budget / lga / year / follow_up | Is there anything budgeted for farmers in my LGA in the 2026 budget? | ✅ |
| u30 | My neighbour says it flooded in 2020, are you sure? | place_history / pin / past / correction | Did my farm (the pin) ever flood, and specifically did it flood in 2020 as my neighbour claims? | ✅ |
| f01 | How many medical officers do PHCs need in Sokoto? | statistics / state / none / new | How many medical officers do PHCs need in Sokoto State? | ✅ |
| f02 | What's the state of PHCs in Sokoto? | deep / state / none / new | What is the state of Primary Health Centres (PHCs) in Sokoto State? | ✅ |
| f03 | tell me about health in Sokoto | deep / state / none / new | Tell me about the state of health in Sokoto State | ✅ |
| f04 | what's happening in my area? | deep / ward / now / new | Give a broad overview of what is happening in my ward | ✅ |
| f05 | How many PHCs are in Tureta? | facility / lga / none / new | How many PHCs are in Tureta LGA? | ✅ |
| f06 | How much did Sokoto spend on education last year? | budget / sector / year / new | How much did Sokoto State spend on education in 2025? | ✅ |
| f07 | Is it safe to plant this week, will it rain? | hazard / pin / forecast / new | Will it rain at my farm (the pin) in Kalambaina ward, Wamakko LGA this week and is it safe to plant? | ✅ |
| f08 | Nawa aka ware wa ma'aikatar lafiya a 2026? | budget / agency / year / new | How much was allocated to the Ministry of Health in Sokoto State in 2026? | ✅ |
| f09 | Ina asibiti mafi kusa da ni? | facility / pin / now / new | Where is the nearest health facility to my farm (the pin)? | ✅ |
| f10 | Gonata ta taba yin ambaliya? | place_history / pin / past / new | Has my farm (the pin) ever been flooded? | ✅ |
| f11 | What does the MICS say about birth registration in Sokoto? | statistics / document / none / new | What does the MICS report say about birth registration coverage in Sokoto State? | ✅ |
| f12 | Alert me when there will be floods in Goronyo | alerts / lga / forecast / new | Sign me up to be alerted when floods are forecast for Goronyo LGA | ✅ |
| f13 | What projects is the government doing in Tambuwal? | place_budget / lga / span / new | What projects and budget allocations is the Sokoto State government doing in Tambuwal LGA? | ✅ |
| f14 | Sannu | conversation / none / none / chitchat | User greets Kasafi | ✅ |
| f15 | Yaya yanayin ilimi a Sokoto? | deep / state / now / new | What is the state of education in Sokoto State? | ✅ |
| c01 | Who are you? | conversation / none / none / chitchat | Who or what is Kasafi? | ✅ |
| c02 | Kai wanene? | conversation / none / none / chitchat | Who are you? | ✅ |
| c03 | Me za ka iya yi? | conversation / none / none / chitchat | What can you (Kasafi) do to help me? | ✅ |
| c04 | What can you do? | conversation / none / none / chitchat | What can Kasafi do? | ✅ |
| c05 | How does this work? | conversation / none / none / chitchat | How does Kasafi work? | ✅ |
| c06 | Who made you? | conversation / none / none / chitchat | Who made Kasafi? | ✅ |
| c07 | Is this a bot? | conversation / none / none / chitchat | Ask who or what Kasafi is and if it is a bot | ✅ |
| c08 | Can you speak Hausa? | conversation / none / none / chitchat | Can Kasafi speak Hausa? | ✅ |
| c09 | Na gode | conversation / none / none / chitchat | User is saying thank you and not asking a new question | ✅ |
| c10 | Assalamu alaikum | conversation / none / none / chitchat | Greeting: says Assalamu alaikum | ✅ |
| c11 | Hello | conversation / none / none / chitchat | User says hello | ✅ |
| c12 | Sai anjima | conversation / none / none / chitchat | Goodbye for now | ✅ |
| c13 | Thank you, bye | conversation / none / none / chitchat | The user says thank you and goodbye | ✅ |
| c14 | help | conversation / none / none / chitchat | What can Kasafi do and what help is available | ✅ |
| c15 | Ina kwana | conversation / none / none / chitchat | The user greets Kasafi (Ina kwana) | ✅ |
| c16 | Wa ya yi ka? | conversation / none / none / chitchat | Who made you? | ✅ |
| c17 | Kana jin Hausa? | conversation / none / none / chitchat | Can you understand and speak Hausa? | ✅ |
| c18 | Mutum ne kai ko na'ura? | conversation / none / none / chitchat | Are you a human or a machine? | ✅ |
| c19 | Yaya kake aiki? | conversation / none / none / chitchat | How does Kasafi work? | ✅ |
| c20 | But uduth is closer to me | facility / facility / none / correction | UDUTH (Usmanu Danfodiyo University Teaching Hospital) is closer to my LGA than the facility previously suggested | ✅ |
| m01 | Where can my wife deliver a baby? | facility / none / none / new | Where can my wife deliver a baby near my farm (the pin) in my ward in my LGA? | ✅ |
| m02 | Matata na naƙuda, ina zan kai ta? | facility / pin / now / new | Where should I take my wife who is in labour from my farm (the pin) in my ward, Wamakko LGA? | ✅ |
| m03 | Nearest place for antenatal care | facility / pin / none / new | What is the nearest health facility to my farm (the pin) for antenatal care? | ✅ |
| m04 | A ina matata za ta haihu? | facility / none / none / new | Where can my wife give birth near my farm (the pin) in my ward in Wamakko LGA, Sokoto State? | ✅ |
| m05 | Is there anywhere I can deliver a baby around here? | facility / pin / none / new | Where can I deliver a baby near my farm (the pin) in Kalambaina ward, Wamakko LGA? | ✅ |
| m06 | Where can I take my sick child? | facility / pin / now / new | Where can I take my sick child from my farm (the pin) in my ward in my LGA? | ✅ |
| m07 | Ina asibitin gwamnati mafi kusa? | facility / pin / none / new | Where is the nearest public hospital to my farm (the pin)? | ✅ |
| m08 | Is there a private clinic near me? | facility / pin / none / new | Is there a private clinic near my farm (the pin)? | ✅ |
| m09 | Only government ones | facility / none / none / follow_up | What are the nearest government health facilities where my wife can deliver near my farm (the pin) in my ward? | ✅ |
| m10 | Anything for schools? | place_budget / lga / year / follow_up | What does the 2026 budget allocate for schools in my LGA? | ✅ |
| k01 | menu | conversation / none / none / menu | The user wants to see the menu of available options | ✅ |
| k02 | zaɓi | conversation / none / none / menu | Show the menu of options | ✅ |
| k03 | Nuna min zaɓuɓɓuka | conversation / none / none / menu | Show me the menu/options | ✅ |
| n01 | How many people were affected by floods in Sokoto State in October 2024? | statistics / state / past / new | How many people were affected by floods in Sokoto State in October 2024? | ✅ |
| n02 | How many people were displaced by the 2024 floods in Sokoto? | statistics / state / year / new | How many people were displaced by the 2024 floods in Sokoto State? | ✅ |
| n03 | How many houses were destroyed by flooding in Sokoto in 2025? | statistics / state / year / new | How many houses were destroyed by flooding in Sokoto State in 2025? | ✅ |
| n04 | Was Wamakko LGA affected by floods in 2025, according to NEMA? | statistics / lga / year / new | Was Wamakko LGA affected by floods in 2025 according to NEMA reports? | ✅ |
| n05 | Which LGAs in Sokoto State were affected by floods in 2025, according to NEMA? | statistics / state / past / new | Which LGAs in Sokoto State were affected by floods in 2025 according to NEMA? | ✅ |
| n06 | Mutane nawa ambaliyar ruwa ta shafa a Jihar Sokoto a 2025, a cewar NEMA? | statistics / state / year / new | How many people were affected by floods in Sokoto State in 2025 according to NEMA? | ✅ |
| n07 | Mutane nawa suka rasa matsugunansu saboda ambaliya a Sokoto a 2024? | statistics / state / year / new | How many people lost their homes due to floods in Sokoto State in 2024? | ✅ |
| n08 | Gidaje nawa ambaliya ta rushe a Sokoto a 2024? | statistics / state / year / new | How many houses were destroyed by floods in Sokoto State in 2024? | ✅ |
| n09 | How bad were the 2024 floods in Sokoto? | statistics / state / year / new | How bad were the 2024 floods in Sokoto State overall? | ✅ |
| n10 | Yaya girman ambaliyar 2024 a Jihar Sokoto? | statistics / state / year / new | How big were the 2024 floods in Sokoto State? | ✅ |
| n11 | How many people died in floods in Sokoto in 2024? | statistics / state / year / new | How many people died due to floods in Sokoto State in 2024? | ✅ |
| n12 | How much of my ward was under water in 2024? | place_history / ward / past / follow_up | How much of my ward was under water in 2024? | ✅ |
| n13 | Which wards of Wamakko flooded most in 2022? | place_history / lga / past / new | Which wards of Wamakko LGA flooded most in 2022? | ✅ |
| n14 | Ruwa ya taɓa rufe gonata? | place_history / pin / past / follow_up | Has flood water ever covered my farm (the pin)? | ✅ |
| n15 | What does the MICS report say about birth registration in Sokoto? | statistics / document / none / new | What does the MICS report say about birth registration in Sokoto State? | ✅ |
| n16 | According to NiMet, when will the rains end in my LGA this year? | hazard / lga / forecast / new | According to NiMet, when will the rains end in my LGA (Wamakko LGA) this year? | ✅ |
