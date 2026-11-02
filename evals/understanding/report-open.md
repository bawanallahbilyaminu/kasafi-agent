# Conversation understanding eval (open)

45 cases: **45 right**, 0 wrong. Latency median 1.98 s, p90 4.23 s; cost $0.0934 ($0.0021 per message).

| Id | Message | Capability / level / time / kind | Restatement | Wrong |
|---|---|---|---|---|
| u01 | But Uduth is closer to me | facility / facility / none / correction | UDUTH is closer to my farm (the pin) than Specialist Hospital Sokoto and is the nearest hospital | ✅ |
| u02 | Has this area ever flooded | place_history / ward / past / follow_up | Has my ward (Kalambaina ward, Wamakko LGA) ever been flooded in the past | ✅ |
| u03 | Has this land ever flooded? | place_history / pin / past / follow_up | Has my farm (the pin) in Kalambaina ward, Wamakko LGA ever been flooded? | ✅ |
| u04 | What about the rain this season, will it flood? | hazard / pin / forecast / follow_up | Will my farm (the pin) in ward Kalambaina, Wamakko LGA flood this rain season? | ✅ |
| u05 | How much of that has actually been spent? | place_budget / lga / year / follow_up | How much of the 2026 budget allocated to my LGA Wamakko has actually been spent? | ✅ |
| u06 | And the past three years? | place_budget / lga / span / follow_up | What did the government budget for my LGA (Wamakko LGA) in the past three years (2023-2025)? | ✅ |
| u07 | How do I get to the second one? | facility / facility / none / follow_up | How do I get from my farm (the pin) in Kalambaina ward, Wamakko LGA to Gidan Bubu Health Post (the second nearest clinic)? | ✅ |
| u08 | Does Kalambaina PHC have enough nurses? | statistics / facility / now / follow_up | Does Kalambaina PHC have enough nurses to meet staffing needs/standards? | ✅ |
| u09 | Amma UDUTH ya fi kusa da ni | facility / facility / now / correction | The user corrects the previous answer and claims that Usmanu Danfodiyo University Teaching Hospital (UDUTH) is closer to my farm (the pin) in Kalambaina ward, Wamakko LGA than Specialist Hospital Sokoto | ✅ |
| u10 | Shin wannan gonar ta taba cika da ruwa? | place_history / pin / past / follow_up | Has my farm (the pin) in Kalambaina ward, Wamakko LGA ever been flooded? | ✅ |
| u11 | Za a yi ambaliya a nan bana? | hazard / pin / forecast / follow_up | Will my farm (the pin) in Kalambaina ward, Wamakko LGA be flooded this year? | ✅ |
| u12 | Nawa aka kashe daga ciki? | place_budget / lga / year / follow_up | How much of the N79.98 billion allocated to my LGA (Wamakko LGA) in the 2026 budget has been spent? | ✅ |
| u13 | And how much of it was spent by June? | budget / sector / year / follow_up | How much of Sokoto State's 2026 health budget was spent by June 2026? | ✅ |
| u14 | That's not right, the health budget is much smaller | budget / sector / year / correction | What is the correct amount budgeted for health in Sokoto State in 2026? | ✅ |
| u15 | What about in the DHS? | statistics / document / none / follow_up | What share of children are fully vaccinated in Sokoto State according to the DHS? | ✅ |
| u16 | What about the dust? | hazard / pin / forecast / follow_up | What will the dust conditions be tomorrow at my farm (the pin) in Kalambaina ward, Wamakko LGA? | ✅ |
| u17 | Which hospital near me can I go to if my child has trouble breathing? | facility / pin / now / new | Which hospital near my farm (the pin) in Kalambaina ward, Wamakko LGA can I go to if my child has trouble breathing? | ✅ |
| u18 | How much did the government budget for Specialist Hospital this year? | budget / facility / year / follow_up | How much did Sokoto State budget for Specialist Hospital Sokoto in 2026? | ✅ |
| u19 | And is it getting greener over the years? | place_history / pin / span / follow_up | Is my farm (the pin) getting greener over the years? | ✅ |
| u20 | What about the whole of Wamakko? | place_history / lga / past / follow_up | Has Wamakko LGA ever been flooded? | ✅ |
| u21 | Is there any budget for irrigation there? | place_budget / lga / none / follow_up | Is there any budget for irrigation in my LGA (Wamakko LGA)? | ✅ |
| u22 | What is the state doing about it in the 2026 budget? | budget / sector / year / follow_up | What is Sokoto State budgeting in 2026 to address out-of-school children in Sokoto State? | ✅ |
| u23 | Send me the full brief | deep / state / now / follow_up | Send me the full brief on the state of PHCs in Sokoto State | ✅ |
| u24 | Thanks | chitchat / none / none / chitchat | No question asked, user is thanking for previous nearest PHC information | ✅ |
| u25 | Is Arkilla open at night? | facility / facility / now / follow_up | Is Arkilla PHC open at night? | ✅ |
| u26 | Last year was there flooding in my LGA? | place_history / lga / past / follow_up | Was Wamakko LGA flooded last year (2025)? | ✅ |
| u27 | Na farko, yaya zan je can? | facility / facility / none / follow_up | How do I get to Specialist Hospital Sokoto (the first nearest facility) from my farm (the pin) in Kalambaina ward, Wamakko LGA? | ✅ |
| u28 | Nawa ne a karamar hukumata? | place_budget / lga / year / follow_up | How much of the 2026 education budget is allocated to my LGA (Wamakko LGA)? | ✅ |
| u29 | Is there anything for farmers? | place_budget / lga / year / follow_up | What has Sokoto State budgeted for farmers/agriculture in my LGA (Wamakko LGA) in the 2026 budget? | ✅ |
| u30 | My neighbour says it flooded in 2020, are you sure? | place_history / pin / past / correction | Was my farm (the pin) flooded in 2020 as my neighbour claims? | ✅ |
| f01 | How many medical officers do PHCs need in Sokoto? | statistics / state / none / new | How many medical officers do PHCs need in Sokoto State? | ✅ |
| f02 | What's the state of PHCs in Sokoto? | deep / state / now / new | What is the overall state of Primary Health Centres (PHCs) in Sokoto State? | ✅ |
| f03 | tell me about health in Sokoto | deep / state / none / new | Give an overview of health in Sokoto State | ✅ |
| f04 | what's happening in my area? | deep / ward / none / new | Give a broad overview of what is happening in my area around my farm (the pin) in Kalambaina ward, Wamakko LGA | ✅ |
| f05 | How many PHCs are in Tureta? | facility / lga / now / new | How many PHCs are in Tureta LGA, Sokoto State? | ✅ |
| f06 | How much did Sokoto spend on education last year? | budget / sector / year / new | How much did Sokoto State spend on education in 2025? | ✅ |
| f07 | Is it safe to plant this week, will it rain? | hazard / pin / forecast / new | Will it rain this week at my farm (the pin) in Kalambaina ward, Wamakko LGA and is it safe to plant? | ✅ |
| f08 | Nawa aka ware wa ma'aikatar lafiya a 2026? | budget / agency / year / new | How much was allocated to the Ministry of Health in Sokoto State in 2026? | ✅ |
| f09 | Ina asibiti mafi kusa da ni? | facility / pin / none / new | Where is the nearest health facility to my farm (the pin) in Kalambaina ward, Wamakko LGA? | ✅ |
| f10 | Gonata ta taba yin ambaliya? | place_history / pin / past / new | Has my farm (the pin) in Kalambaina ward, Wamakko LGA ever been flooded in the past? | ✅ |
| f11 | What does the MICS say about birth registration in Sokoto? | statistics / document / none / new | What does the MICS report say about birth registration coverage in Sokoto State? | ✅ |
| f12 | Alert me when there will be floods in Goronyo | alerts / lga / forecast / new | Sign me up for flood alerts for Goronyo LGA | ✅ |
| f13 | What projects is the government doing in Tambuwal? | place_budget / lga / now / new | What projects is the government doing in Tambuwal LGA? | ✅ |
| f14 | Sannu | chitchat / none / none / chitchat | User greets Kasafi in Hausa | ✅ |
| f15 | Yaya yanayin ilimi a Sokoto? | deep / state / now / new | What is the state of education in Sokoto State? | ✅ |
