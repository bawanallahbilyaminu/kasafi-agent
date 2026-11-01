# Demo video script (3 minutes)

A screen recording of WhatsApp on a phone (or WhatsApp Web), with captions. Every message below is sent from a
test number that has already accepted the consent notice and chosen Hausa. **Replies marked "verify live" must be
checked on the day:** they come from live data and models, so wording and figures can differ. Re-record any segment
whose reply doesn't match what the caption says. Nothing private appears on screen: no phone number, no real
person's farm.

Before recording:
- Open `/admin/status` and check that the hazard layers are fresh (ages in minutes or hours) and the serving commit
  is the one you mean to show.
- Ask the farm question once on a demo pin off camera, so the recorded answer comes from the cache (a first request
  takes about a minute). Use a pin you choose for the demo, not a real farmer's field.
- For the live fetch, pick a document that is **not** in the library yet (check `/admin/traces` or the
  documents table) and that sits on an allowlisted site.
- Turn on WhatsApp's large text, and mute notifications.

## 0:00–0:15 · What Kasafi is

Caption over the chat list: *"Kasafi answers questions about Sokoto State from public sources, in Hausa or English,
on WhatsApp. Every figure is cited and checked in code."*

## 0:15–0:50 · A Hausa voice note about a budget, with evidence

1. Record and send a voice note: **"Nawa aka ware wa Ma'aikatar Lafiya a kasafin 2026?"** (How much was
   budgeted for the Ministry of Health in 2026?)
2. Expected: "🎧 Ina sauraro…", then the transcript ("Na ji tambayarka: «…»"), then the answer: a short Hausa answer with the
   2026 approved total and the source line (*Madogara: … shafi …*). After it comes the cropped image of the
   printed row. **Verify live:** the figure and page match the 2026 budget.
3. Send: **"nuna lissafi"**.
4. Expected: the rows used and the arithmetic, with the verification state at the end (*Tabbatarwa: …*).
   **Verify live.**

Caption: *"Muse Voice Transcribe and Muse Spark each transcribe; Muse Spark Open reads the budget rows a second
time, independently; SAM 3.1 crops the evidence."*

## 0:50–1:15 · A report Kasafi doesn't have yet

5. Send a question about the document you chose, naming it, for example **"What does the <publisher> <report
   title> say about <topic> in Sokoto?"**
6. Expected: "📥 Ba ni da wannan takardar tukuna. Ina neman takardar …" (I don't have this document yet; looking
   for it on government and partner sites), then the answer citing the newly fetched document and page.
   **Verify live:** the citation names the new document. If the fetch fails, the reply says what it couldn't
   get; use that take only as the limitation segment below.

Caption: *"Allowlisted sites only, robots.txt respected, the document is indexed and then cited."*

## 1:15–1:55 · A farm pin, its satellite record, then the budget

7. Share the demo pin with WhatsApp's location button.
8. Expected: "📍 Na gane wurinka: Ƙaramar Hukumar … (mazaɓar …)".
9. Send: **"Yaya koriyar gonata a 2024?"** (How green was my farm in 2024?)
10. If asked for the farm size, send **"kadada 3"**. Expected: "An gama: da'irar hekta 1.21 …".
11. Expected: the place-history answer, marked *na gwaji* (experimental). It gives this season against the plot's
    own years and the rain, in plain words, and the water and flood sentence. A chart and a map follow, with the
    LGA's NiMet line from the library and the referral to the ADP extension service. **Verify live.**
12. Send: **"Kuma nawa aka ware wa ban ruwa a nan?"** (And how much is budgeted for irrigation here?)
13. Expected: the LGA's 2026 irrigation and agriculture lines, or "no 2026 budget line names <LGA>" with the
    statewide totals that may cover it. **Verify live.**

Caption: *"Sentinel-2, Sentinel-1 radar, JRC water and the UN's flood maps; SAM 3.1 draws the plot. Observation,
not advice."*

## 1:55–2:20 · Nearest hospital, with the route

14. Send: **"Ina asibiti mafi kusa?"** (Where is the nearest hospital?)
15. Expected: the three nearest hospitals with level, ownership and road distance. A map follows, then the nearest
    one's location pin. **Verify live.**
16. Send: **"hanya"** (route).
17. Expected: the route and travel time to the first hospital, with a map. **Verify live.**

## 2:20–2:35 · The emergency fast path

18. Send the test phrase: **"Maciji ya sare ɗana"** (a snake has bitten my child). Say in the caption that this
    is a test.
19. Expected within about a second: "🚨 …", meaning get help now. It lists the verified emergency numbers and the
    nearest suitable facility from the location shared above, with no medical instructions. The road distance
    follows in a second message. **Verify live:** only verified numbers appear.

Caption: *"Runs before anything else, with no model on the phrase path. Only the fact that it fired is logged."*

## 2:35–2:48 · Signing up for an alert

20. Send: **"Ka faɗakar da ni idan za a yi ambaliya a Goronyo"** (Alert me if there will be floods in Goronyo).
21. Expected: a confirmation naming floods in Goronyo LGA, with buttons. Tap **Eh**. Expected: the sign-up is
    confirmed, and DAINA stops it. **Verify live.** Caption: *"Alerts are in dry run for this demo: the decisions
    go to the admin page."*

## 2:48–3:00 · An honest limitation

22. Send: **"Nawa aka kashe a Orthopedic Hospital Wamakko a Q1 2027?"** (How much was spent at Orthopedic
    Hospital Wamakko in Q1 2027?)
23. Expected: "Ba a cikin takardun ba" (not in the documents). There is no 2027 implementation report in the
    library yet, and the reply names the newest one. **Verify live.**

Closing caption: *"When the documents don't say, Kasafi says so."*
