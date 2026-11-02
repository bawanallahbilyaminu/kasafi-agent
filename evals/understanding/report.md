# Conversation understanding eval (meta)

45 cases: **45 right**, 0 wrong. Latency median 2.70 s, p90 3.66 s; cost $0.0918 ($0.0020 per message).

| Id | Message | Capability / level / time / kind | Restatement | Wrong |
|---|---|---|---|---|
| u01 | But Uduth is closer to me | facility / facility / none / correction | The user says UDUTH is closer to my farm (the pin) than the hospitals previously listed. | ✅ |
| u02 | Has this area ever flooded | place_history / ward / past / follow_up | Has my ward ever flooded in the past? | ✅ |
| u03 | Has this land ever flooded? | place_history / pin / past / follow_up | Has my farm (the pin) ever flooded? | ✅ |
| u04 | What about the rain this season, will it flood? | hazard / pin / forecast / follow_up | Will my farm (the pin) flood this rainy season? | ✅ |
| u05 | How much of that has actually been spent? | place_budget / lga / year / follow_up | How much of the 2026 budgeted amount for my LGA has actually been spent? | ✅ |
| u06 | And the past three years? | place_budget / lga / span / follow_up | What did the government budget for my LGA in 2023 to 2025? | ✅ |
| u07 | How do I get to the second one? | facility / facility / none / follow_up | How do I get from my farm (the pin) to Gidan Bubu Health Post? | ✅ |
| u08 | Does Kalambaina PHC have enough nurses? | statistics / facility / now / follow_up | Does Kalambaina PHC have enough nurses? | ✅ |
| u09 | Amma UDUTH ya fi kusa da ni | facility / facility / none / correction | User says UDUTH is closer to my farm (the pin) than the listed facilities and asks to check the nearest hospital | ✅ |
| u10 | Shin wannan gonar ta taba cika da ruwa? | place_history / pin / past / follow_up | Has my farm (the pin) ever been flooded? | ✅ |
| u11 | Za a yi ambaliya a nan bana? | hazard / pin / forecast / follow_up | Will my farm (the pin) flood this year? | ✅ |
| u12 | Nawa aka kashe daga ciki? | place_budget / lga / year / follow_up | How much was spent out of the 2026 budget allocation for my LGA? | ✅ |
| u13 | And how much of it was spent by June? | budget / sector / year / follow_up | How much of the Sokoto State 2026 health budget was spent by June? | ✅ |
| u14 | That's not right, the health budget is much smaller | budget / sector / year / correction | How much was budgeted for health in Sokoto State in 2026? | ✅ |
| u15 | What about in the DHS? | statistics / document / none / follow_up | What share of children are fully vaccinated in Sokoto State according to the DHS? | ✅ |
| u16 | What about the dust? | hazard / pin / forecast / follow_up | Will there be dust tomorrow at my farm (the pin)? | ✅ |
| u17 | Which hospital near me can I go to if my child has trouble breathing? | facility / pin / none / new | Which hospital nearest to my farm (the pin) can I go to if my child has trouble breathing? | ✅ |
| u18 | How much did the government budget for Specialist Hospital this year? | budget / facility / year / follow_up | How much did the Sokoto State government budget for Specialist Hospital Sokoto in 2026? | ✅ |
| u19 | And is it getting greener over the years? | place_history / pin / span / follow_up | Is my farm (the pin) getting greener over the years? | ✅ |
| u20 | What about the whole of Wamakko? | place_history / lga / past / follow_up | Has Wamakko LGA ever flooded? | ✅ |
| u21 | Is there any budget for irrigation there? | place_budget / lga / none / follow_up | Is there any budget for irrigation in my LGA? | ✅ |
| u22 | What is the state doing about it in the 2026 budget? | budget / sector / year / follow_up | What is Sokoto State budgeting and planning in 2026 to address out-of-school children? | ✅ |
| u23 | Send me the full brief | deep / state / now / follow_up | Send me the full brief on the state of PHCs in Sokoto State | ✅ |
| u24 | Thanks | chitchat / none / none / chitchat | The user says thank you for the nearest PHC information. | ✅ |
| u25 | Is Arkilla open at night? | facility / facility / now / follow_up | Is Arkilla PHC open at night? | ✅ |
| u26 | Last year was there flooding in my LGA? | place_history / lga / past / follow_up | Was there flooding in my LGA in 2025? | ✅ |
| u27 | Na farko, yaya zan je can? | facility / facility / none / follow_up | How do I get to Specialist Hospital Sokoto (the first one) from my farm (the pin)? | ✅ |
| u28 | Nawa ne a karamar hukumata? | place_budget / lga / year / follow_up | How much of the 2026 education budget is for my LGA? | ✅ |
| u29 | Is there anything for farmers? | place_budget / lga / year / follow_up | Is there anything for farmers in the 2026 budget for my LGA? | ✅ |
| u30 | My neighbour says it flooded in 2020, are you sure? | place_history / pin / past / correction | Was my farm (the pin) flooded in 2020 as my neighbour claims? | ✅ |
| f01 | How many medical officers do PHCs need in Sokoto? | statistics / state / none / new | How many medical officers do PHCs in Sokoto State need? | ✅ |
| f02 | What's the state of PHCs in Sokoto? | deep / state / now / new | What is the state of primary health centres in Sokoto State? | ✅ |
| f03 | tell me about health in Sokoto | deep / state / none / new | Tell me about health in Sokoto State. | ✅ |
| f04 | what's happening in my area? | deep / ward / now / new | Give a broad overview of what is happening in my ward. | ✅ |
| f05 | How many PHCs are in Tureta? | facility / lga / none / new | How many PHCs are in Tureta LGA? | ✅ |
| f06 | How much did Sokoto spend on education last year? | budget / sector / year / new | How much did Sokoto State spend on education in 2025? | ✅ |
| f07 | Is it safe to plant this week, will it rain? | hazard / pin / forecast / new | Will it rain on my farm (the pin) this week and is it safe to plant there? | ✅ |
| f08 | Nawa aka ware wa ma'aikatar lafiya a 2026? | budget / agency / year / new | How much was allocated to the Ministry of Health in Sokoto State in 2026? | ✅ |
| f09 | Ina asibiti mafi kusa da ni? | facility / pin / none / new | Where is the nearest hospital to my farm (the pin)? | ✅ |
| f10 | Gonata ta taba yin ambaliya? | place_history / pin / past / new | Has my farm (the pin) ever been flooded? | ✅ |
| f11 | What does the MICS say about birth registration in Sokoto? | statistics / document / none / new | What does the MICS say about birth registration coverage in Sokoto State? | ✅ |
| f12 | Alert me when there will be floods in Goronyo | alerts / lga / forecast / new | Alert me about future floods in Goronyo LGA | ✅ |
| f13 | What projects is the government doing in Tambuwal? | place_budget / lga / none / new | What projects is the government doing in Tambuwal? | ✅ |
| f14 | Sannu | chitchat / none / none / chitchat | The user greets Kasafi with 'Sannu'. | ✅ |
| f15 | Yaya yanayin ilimi a Sokoto? | deep / sector / now / new | What is the state of education in Sokoto State? | ✅ |
