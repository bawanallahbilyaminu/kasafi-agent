# Conversation understanding eval (meta)

65 cases: **65 right**, 0 wrong. Latency median 2.26 s, p90 3.57 s; cost $0.0459 ($0.0026 per message; 18 re-read with --only after a network drop, the rest kept from the full run at $0.1031).

| Id | Message | Capability / level / time / kind | Restatement | Wrong |
|---|---|---|---|---|
| u01 | But Uduth is closer to me | facility / facility / none / correction | Is UDUTH closer to my farm (the pin) than the hospitals listed as nearest? | ✅ |
| u02 | Has this area ever flooded | place_history / ward / past / follow_up | Has my ward ever flooded? | ✅ |
| u03 | Has this land ever flooded? | place_history / pin / past / follow_up | Has my farm (the pin) ever flooded? | ✅ |
| u04 | What about the rain this season, will it flood? | hazard / pin / forecast / follow_up | Will my farm (the pin) flood this rainy season? | ✅ |
| u05 | How much of that has actually been spent? | place_budget / lga / year / follow_up | How much of the 2026 budget for my LGA has actually been spent? | ✅ |
| u06 | And the past three years? | place_budget / lga / span / follow_up | What did the government budget for my LGA in the past three years (2023-2025)? | ✅ |
| u07 | How do I get to the second one? | facility / facility / none / follow_up | How do I get from my farm (the pin) to Gidan Bubu Health Post? | ✅ |
| u08 | Does Kalambaina PHC have enough nurses? | statistics / facility / now / follow_up | Does Kalambaina PHC have enough nurses? | ✅ |
| u09 | Amma UDUTH ya fi kusa da ni | facility / facility / none / correction | The user says UDUTH is closer to my farm (the pin) than the facilities previously listed | ✅ |
| u10 | Shin wannan gonar ta taba cika da ruwa? | place_history / pin / past / follow_up | Has my farm (the pin) ever been flooded? | ✅ |
| u11 | Za a yi ambaliya a nan bana? | hazard / pin / forecast / follow_up | Will my farm (the pin) be flooded this year? | ✅ |
| u12 | Nawa aka kashe daga ciki? | place_budget / lga / year / follow_up | How much was spent from the 2026 budget allocation for my LGA? | ✅ |
| u13 | And how much of it was spent by June? | budget / sector / year / follow_up | How much of Sokoto State's 2026 health budget was spent by June 2026? | ✅ |
| u14 | That's not right, the health budget is much smaller | budget / sector / year / correction | What was budgeted for health in Sokoto State in 2026? | ✅ |
| u15 | What about in the DHS? | statistics / document / past / follow_up | What share of children are fully vaccinated in Sokoto State according to the DHS? | ✅ |
| u16 | What about the dust? | hazard / pin / forecast / follow_up | Will it be dusty tomorrow at my farm (the pin)? | ✅ |
| u17 | Which hospital near me can I go to if my child has trouble breathing? | facility / pin / now / new | Which nearest hospital to my farm (the pin) can I go to if my child has trouble breathing? | ✅ |
| u18 | How much did the government budget for Specialist Hospital this year? | budget / facility / year / follow_up | How much did Sokoto State budget for Specialist Hospital Sokoto in 2026? | ✅ |
| u19 | And is it getting greener over the years? | place_history / pin / span / follow_up | Is my farm (the pin) getting greener over the years? | ✅ |
| u20 | What about the whole of Wamakko? | place_history / lga / past / follow_up | Has my LGA ever flooded? | ✅ |
| u21 | Is there any budget for irrigation there? | place_budget / lga / none / follow_up | Is there any irrigation budget for my LGA? | ✅ |
| u22 | What is the state doing about it in the 2026 budget? | budget / sector / year / follow_up | What is Sokoto State budgeting and planning in the 2026 budget to address out-of-school children? | ✅ |
| u23 | Send me the full brief | deep / state / none / follow_up | Send me the full brief on the state of PHCs in Sokoto State | ✅ |
| u24 | Thanks | conversation / none / none / chitchat | The user says thank you. | ✅ |
| u25 | Is Arkilla open at night? | facility / facility / now / follow_up | Is Arkilla PHC open at night? | ✅ |
| u26 | Last year was there flooding in my LGA? | place_history / lga / past / follow_up | Was there flooding in my LGA last year (2025)? | ✅ |
| u27 | Na farko, yaya zan je can? | facility / facility / none / follow_up | How do I get to Specialist Hospital Sokoto from my farm (the pin)? | ✅ |
| u28 | Nawa ne a karamar hukumata? | place_budget / lga / year / follow_up | How much of the 2026 education budget is for my LGA? | ✅ |
| u29 | Is there anything for farmers? | place_budget / lga / year / follow_up | Is there anything budgeted for farmers in my LGA in 2026? | ✅ |
| u30 | My neighbour says it flooded in 2020, are you sure? | place_history / pin / past / correction | Did my farm (the pin) flood in 2020 as my neighbour claims? | ✅ |
| f01 | How many medical officers do PHCs need in Sokoto? | statistics / state / none / new | How many medical officers do PHCs need in Sokoto State? | ✅ |
| f02 | What's the state of PHCs in Sokoto? | deep / state / none / new | What is the state of primary health centres in Sokoto State? | ✅ |
| f03 | tell me about health in Sokoto | deep / state / none / new | Tell me about health in Sokoto State. | ✅ |
| f04 | what's happening in my area? | deep / ward / now / new | What is happening in my ward? | ✅ |
| f05 | How many PHCs are in Tureta? | facility / lga / none / new | How many PHCs are in Tureta LGA? | ✅ |
| f06 | How much did Sokoto spend on education last year? | budget / sector / year / new | How much did Sokoto State spend on education in 2025? | ✅ |
| f07 | Is it safe to plant this week, will it rain? | hazard / pin / forecast / new | Will it rain this week at my farm (the pin) and is it safe to plant there? | ✅ |
| f08 | Nawa aka ware wa ma'aikatar lafiya a 2026? | budget / agency / year / new | How much was allocated to the Ministry of Health of Sokoto State in 2026? | ✅ |
| f09 | Ina asibiti mafi kusa da ni? | facility / pin / none / new | Where is the nearest hospital to my farm (the pin)? | ✅ |
| f10 | Gonata ta taba yin ambaliya? | place_history / pin / past / new | Has my farm (the pin) ever been flooded? | ✅ |
| f11 | What does the MICS say about birth registration in Sokoto? | statistics / document / none / new | What does the MICS say about birth registration in Sokoto State? | ✅ |
| f12 | Alert me when there will be floods in Goronyo | alerts / lga / forecast / new | Sign me up for alerts when there will be floods in Goronyo | ✅ |
| f13 | What projects is the government doing in Tambuwal? | place_budget / lga / none / new | What projects is the Sokoto State government doing in Tambuwal LGA? | ✅ |
| f14 | Sannu | conversation / none / none / chitchat | The user greets Kasafi. | ✅ |
| f15 | Yaya yanayin ilimi a Sokoto? | deep / state / now / new | What is the state of education in Sokoto State? | ✅ |
| c01 | Who are you? | conversation / none / none / chitchat | Who are you (what is Kasafi)? | ✅ |
| c02 | Kai wanene? | conversation / none / none / chitchat | Who are you? | ✅ |
| c03 | Me za ka iya yi? | conversation / none / none / chitchat | What can you do? | ✅ |
| c04 | What can you do? | conversation / none / none / chitchat | What can you (Kasafi) do? | ✅ |
| c05 | How does this work? | conversation / none / none / chitchat | How does Kasafi work? | ✅ |
| c06 | Who made you? | conversation / none / none / chitchat | Who made you? | ✅ |
| c07 | Is this a bot? | conversation / none / none / chitchat | Is Kasafi a bot? | ✅ |
| c08 | Can you speak Hausa? | conversation / none / none / chitchat | Can you speak Hausa? | ✅ |
| c09 | Na gode | conversation / none / none / chitchat | The user says thank you. | ✅ |
| c10 | Assalamu alaikum | conversation / none / none / chitchat | The user greets with Assalamu alaikum. | ✅ |
| c11 | Hello | conversation / none / none / chitchat | The user says hello to Kasafi. | ✅ |
| c12 | Sai anjima | conversation / none / none / chitchat | goodbye, see you later | ✅ |
| c13 | Thank you, bye | conversation / none / none / chitchat | The user says thank you and goodbye. | ✅ |
| c14 | help | conversation / none / none / chitchat | The user asks for help about what Kasafi can do. | ✅ |
| c15 | Ina kwana | conversation / none / none / chitchat | The user greets Kasafi. | ✅ |
| c16 | Wa ya yi ka? | conversation / none / none / chitchat | Who made you? | ✅ |
| c17 | Kana jin Hausa? | conversation / none / none / chitchat | Do you understand Hausa? | ✅ |
| c18 | Mutum ne kai ko na'ura? | conversation / none / none / chitchat | Are you a human or a machine? | ✅ |
| c19 | Yaya kake aiki? | conversation / none / none / chitchat | How do you work? | ✅ |
| c20 | But uduth is closer to me | facility / facility / none / correction | Is UDUTH closer to me in my LGA than the previous answer? | ✅ |
