# Routing: which path answers a message

Written 1 Nov 2026 after two live misroutes of one class: a question naming a report fired a keyword shortcut.
"What did UNFPA find out about health facilities in Wamakko" got the registry card for "Wamakko Primary Health
Center" (the name lookup matched the LGA and a facility word); "which 10 LGAs get most IDPs" had earlier gone to ward
greenness; "According to the MICS … gaps in child healthcare" was refused by a budget-table rule. The rule, the
switches and the eval set below fix the class.

## 1. The rule

1. **A shortcut fires only on unambiguous intent for its own feature.** A named facility needs *where is / how far /
   directions to / what about X / is X open* (`app/agent/routing.py: facility_intent`); the nearest-facility search
   needs *nearest / closest / around me*; a hazard route needs a hazard word and no money word; a place-history route
   needs a satellite measure word.
2. **A question naming a publisher, survey or report goes to the planner and the document path**, whatever facility,
   place or hazard words it also contains: "according to", "what did X find / say / report", UNFPA, MICS, NDHS, IOM,
   SBS, World Bank, "the … report / survey / assessment", Hausa *a cewar*, *rahoton*, *binciken*, *ya gano*
   (`routing.document_question`; the publisher names come from `data/source_registry.yaml` plus a fixed list). A route
   whose own data source is the one named may still answer (NCDC for the outbreak tables, NiMet and NIHSA for the
   outlooks: `routing.own_source`).
3. **When in doubt the planner decides with the catalogue.** The planner may add facility, hazard or place data as a
   supplement; the report answers the question.
4. **The emergency fast path stays first, unchanged.** The guardrails stay second.

## 2. Every path that answers before or instead of the planner (audit, 1 Nov 2026)

In order of priority. "Pre-planner" paths run in `app/whatsapp/conversation.py: handle` before any model call;
"post-plan" paths run in `app/agent/answer.py: _answer_question` after the planner model, before the document path.

| # | Path | Where | Trigger | Switch (default on) | Yields to a named source? |
|---|---|---|---|---|---|
| 1 | Delete my data | pre-planner | DELETE MY DATA / GOGE BAYANAI NA (exact phrases) | none | n/a |
| 2 | **Emergency fast path** | pre-planner, before consent | the phrase list (bleeding, not breathing, snakebite, labour …) in Hausa or English; health words + the classifier after consent | **none** | no (safety first) |
| 3 | Access, language, consent | pre-planner | pilot numbers; "english" / "hausa"; the consent buttons | none | n/a |
| 4 | Plot shape (size / corner pins / done / skip) | pre-planner | only while a place question is waiting for a size, or "these are the corners" with recent pins | place | n/a (a state, not a keyword) |
| 5 | Location pin / "share my location" | pre-planner | a WhatsApp location message; SHARE phrases | none | n/a |
| 6 | Facility follow-ups (next / route / only government / on foot) | pre-planner | a short message (≤ 7 words, no money word) after a facility list | facilities | n/a (a state) |
| 7 | Facility count | pre-planner | *how many / number of* + a facility kind, no project words | facilities | **yes** |
| 8 | Named facility (card / route) | pre-planner | a facility word or *go to / how far*, **plus intent words**, and a registry name match ≥ 0.9 | facilities | **yes** |
| 9 | Nearest facility | pre-planner | a facility word + *nearest / closest / near me / ina … mafi kusa* | facilities | **yes** |
| 10 | Map only | pre-planner | "show me the map" alone | none | n/a |
| 11 | Images on/off, show working, quotes | pre-planner | exact commands | none | n/a |
| 12 | **Guardrails** (political, electoral, verdict, medical advice, land) | pre-planner, before the model | keyword lists, then the model on borderline wording | **none** | no |
| 13 | Alert sign-up / menu / STOP / MORE | pre-planner | *alert me / faɗakar da ni*, the menu words, STOP / DAINA | alerts (and KASAFI_ALERTS) | n/a |
| 14 | Replace-or-add, clarify buttons, calculation offer, read-back Eh/A'a | pre-planner | a pending state | none | n/a |
| 15 | Voice: transcription and read-back | pre-planner | an audio message | none | n/a |
| 16 | Planner clarify ("which did you mean?") | after the plan | two readings of an entity (never for a place question) | none | n/a |
| 17 | Facility card / count from the registry | post-plan | the planner's facility measures or a facility-kind word, no money word | facilities | **yes** |
| 18 | Place history, area (ward / LGA / state) | post-plan | a satellite measure word + a scope word or the pin's ward | place | **yes** |
| 19 | Place history, the pin's record | post-plan | place words + history words (*my farm*, *gonata*, *how green*) | place | **yes** |
| 20 | Outbreak tables and official outlooks (NCDC, NiMet, NIHSA) | post-plan | disease + cases words; outlook words | hazards | yes, except its own source |
| 21 | Weather and hazard layers | post-plan | a hazard word (heat, dust/*kura*, rain, rivers, fires) and no money word | hazards | yes, except NiMet/NIHSA/NCDC |
| 22 | Structured budget tools (budget_core, dtm_api) | post-plan | every cell of the planner's need fillable by one tool | none (the planner's own) | the budget is the document |
| 23 | Statewide revenue summary | post-plan (analysis tool) | the planner's `revenue` analysis for the statewide picture | revenue (off: the revenue rows are searched instead) | n/a |
| 24 | Multi-source topic path (registry) | post-plan | a statistics question on a registry topic | none (a document path) | it is the document path |
| 25 | Document path (search, fetch, compose, checks) | last | everything else | none | — |

## 3. Feature switches

`.env` (all default true; see `.env.example`):

```
KASAFI_SHORTCUT_FACILITIES=true
KASAFI_SHORTCUT_HAZARDS=true
KASAFI_SHORTCUT_PLACE=true
KASAFI_SHORTCUT_ALERTS=true
KASAFI_SHORTCUT_REVENUE=true
```

Off turns off the shortcut's own trigger (rows 6–9, 13, 17–21, 23) without removing the capability: the planner can
still use the registry, the hazard layers and the place tables from the catalogue. The emergency fast path and the
guardrails have no switch. `tests/test_feature_switches.py` checks that with every switch off a nearest-hospital,
named-facility, count and alert message reaches the planner, the fast path and the guardrails still fire, and the
routing eval set routes every shortcut case to the planner.

## 4. The routing eval set

`evals/routing/cases.json` (56 cases, English and Hausa): questions carrying another feature's words with the route
each must take: a budget question naming a facility, a hazard word in a budget question ("flood control budget"), a
report question about facilities, a place-history question with "health", a facility question naming a ward,
*kura* the village against *kura* dust, the two live misroutes. `uv run python evals/routing/run.py` applies the
predicates in handler order in code (no model, no spend) and writes `evals/routing/report.md`; it is part of the
pre-deploy gate. The named-facility cases need the facility registry (the dev database).

## Conversation understanding before routing (2 Nov 2026)

Three live failures on 2 Nov came from routing each message alone with keyword rules: "But Uduth is closer to me"
after a hospital list (a correction) got the statewide capital budget; "Has this area ever flooded" after a pin (the
past) got the season's forecast; "Has this land ever flooded?" (the pin's land) got a ranking of Wamakko's wards.

Now every text message (after the emergency fast path; not fixed commands, read-backs or pending choices) first goes
through one small Muse Spark call (`app/agent/understand.py`, minimal reasoning) with the last 4 turns (the user's
messages and short summaries of Kasafi's replies with what they listed), the location on file and the keyword rules'
reading as a hint. It returns the kind (new, follow-up, correction, clarification, chit-chat), the capability, the
subject level (pin, ward, LGA, state, facility, document...), the time (past, now, forecast, year, span) and a
standalone restatement in Kasafi's own place words ('my farm (the pin)', 'my ward', 'my LGA').

- The conversation handler and the answer loop route from it: each shortcut (facility, hazard and outlook, place
  history, LGA budget, deep analysis) answers only when the reading names its capability; the planner and the routes
  work from the restatement. Feature switches still apply. When the call fails or runs out of time (20 s), it is tried once on
  Muse Spark Open; when that fails too, the keyword routing decides and a trace row with outcome
  `understanding_fallback` records why (admin traces page). `KASAFI_UNDERSTANDING=false` turns the step off; `KASAFI_UNDERSTAND_PROVIDER=open` uses
  Muse Spark Open on Baseten.
- A correction about the facilities just listed is checked against that list (`_facility_correction`): the named
  facility's road distance from the pin, the list's first, whether the user is right, and why it wasn't listed (the
  search's filter, or the straight-line shortlist before road time). Facility replies are kept as turns, so the next
  message is read with them.
- Every model-written answer and the planner start with the shared core prompt (`app/agent/persona.py`).

Eval: `evals/understanding/` (75 conversations since 2 Nov evening: 45, 10 facility filters and place-budget wordings, plus 20 about Kasafi or the conversation and a cold facility claim; English and Hausa, including the
three failures): 45/45 on Muse Spark, median 2.7 s, p90 3.7 s, $0.0020 per message (`report.md`); 45/45 on Muse
Spark Open, median 2.0 s, p90 4.2 s (`report-open.md`). The deploy gate replays the recorded readings
(`tests/test_understanding.py`) through the conversation handler, without a model call.

Reasoning effort (2 Nov): `minimal` with 900 tokens. `low` with 3000 tokens was measured on the same 45 cases: 44/45, median 4.9 s, p90 8.2 s, $0.0049 per message (`report-low.md`), more precise on two readings and wrong on one, so no more reliable for twice the time and cost. The answer limit went from 120 s to 180 s (the answer loop 165 s, a deep analysis 210 s) so the 2-3 s of understanding never pushes a first-time pin (~95 s) or a deep analysis into the apology. Answers lead with what was asked: a flood question opens with the flood finding (pin and ward answers), a trend follows the year's finding unless the trend was asked, and hazard layers are summarised in the order the question names them.

### The readings obeyed (2 Nov, evening live test)

The live server ran the step on every message, but two readings had no route that honoured them. "Who are you?"
(7:38 and 8:02 PM) was read as chit-chat and still went to the planner and the document search ("I couldn't find
the answer to that in the documents I have"). A cold "But uduth is closer to me" (8:05 PM, trace #123, Wamakko on
file, no list before it) was read as a facility correction, but the correction check needed a list and the facility
shortcut excluded corrections, so it fell to page search in the EmONC assessment. The planner had read it right too
(`verify_claim`, `facility_lookup`, UDUTH). The trace kept no reading, so it looked like the step never ran; the
logs showed it had.

Now:
- **conversation** (greetings, who are you, what can you do, how does it work, who made you, is this a bot, can
  you speak Hausa, thanks, goodbye, help): `app/agent/conversational.py`. One Muse Spark call under the core prompt
  replies in the user's language: who Kasafi is, 3 or 4 example questions that fit the user's place on file ("send
  your location" when there is none), and that answers come from public documents with the page as evidence. There
  is no document search. If the call fails, fixed words in Hausa or English say the same. With no reading, the
  plain self-questions and greetings (`ABOUT_KASAFI`) take the same route.
- **"I couldn't find…" never answers a message that isn't a document question.** A reading of `other` that isn't a
  request (`looks_like_request`) gets the help text directly. A not-found answer to a reading of `other` or
  `conversation`, or to a short non-question when there is no reading, is replaced by the help text: what Kasafi
  can help with, and what the user is looking for.
- **A facility claim** (kind correction, or "closer / nearer / ya fi kusa" with a facility named) goes to
  `_facility_correction` with or without a list. After a list, it is checked against that list as before. With no
  list, the named facility is compared by road with the nearest others of its kind: from the pin, or from the centre
  of the LGA on file (and the reply says so). With neither, the location is asked for, and the check runs when the
  pin or a typed place arrives (`CLAIM_WAIT`). It never goes to the document search.
- **Traces:** every answer's trace starts with the reading (`understanding`). Replies from routes of their own
  (`conversation:model|fixed`, `facility_check`, `help`) get a trace row with the reading. The admin trace page
  shows it as card 0, above the plan.

Capability → route audit:

| Capability | Route that honours the reading | When the keywords miss |
|---|---|---|
| conversation | `conversational.reply` (no search) | — (the reading decides) |
| facility | correction or claim → `_facility_correction`; nearest, route and named → the facility shortcut; counts and named cards → `facility_route` | `_facility_reading`: the facility the reading names (its card), else a nearest search with the reading's filters; the location asked for when there is none. Staff, equipment, services and money at facilities, and a report named, stay with the documents (the registry holds none of them) |
| place_history | `area_route` / `place_route` | the reading's level decides: pin → `place_answer`; ward, LGA or state → `area_route` with the reading's measure |
| hazard | `official.route`, `hazard_route` | `hazard_route` with the reading's measure |
| alerts | `alerts_reply` | `alerts_reply` on the restatement |
| deep | `deep_path` (the reading alone suffices) | — |
| place_budget | `lga_route` | `reading_lga_route`, before the statewide paths: an LGA the message names, else the LGA on file; with neither, the location is asked for and the question resumes with the same reading |
| budget, statistics | the planner, the structured core and the document path | — |
| other | the document path; not found → the help text | a non-request → the help text directly |

Both gaps the first audit left are closed: a `place_budget` reading takes the LGA tool whatever the wording, and a
`facility` reading with no name, count or "nearest" goes to the facilities.

**The reading chooses the facilities** (2 Nov). It carries `facility: {care: maternal|children|general, level:
hospital|primary|any, ownership: public|private|any}`. "Where can my wife deliver a baby", "matata na naƙuda", "a ina
za ta haihu" and "nearest place for antenatal care" are maternal care from the meaning, whatever the words
(`reading_filters`). A follow-up keeps its list's care unless the reading changes it. The keyword filters
(`filters_from`, `MATERNAL`) are only the fallback when the step gave no reading. The same rule applies everywhere: a
missed phrasing is fixed in the reading (prompt, schema, examples) and added as an understanding case, never as a new
keyword. There is no paediatric filter in the registry yet, so `children` searches all facilities.

The dash rule (L36) had refused #123's corrected retry: its second pattern matched "a dash in the table means no"
in "…means no figure is printed", which is the rule followed, not broken. A figure word after "no" now ends the
match.

Live smoke test: `scripts/live_smoke.py` sends conversations through the real webhook reply path in the server
container, with real model calls and nothing sent to WhatsApp. `deploy/deploy.sh` runs the 3-message set after
every deploy ("Who are you?", "Kai wanene?", a cold "But uduth is closer to me" with Wamakko on file), about $0.01.
`deploy/deploy.sh --smoke full` runs the 8 conversations of this fix (about $0.15).

### Emergencies in two layers (2 Nov, night)

"Matata na naƙuda" (my wife is in labour) matched no emergency phrase and no word of the classifier's gate, so it
went to a facility search instead of the maternal fast path.

1. **The fast path's classifier is asked more widely** (`app/guardrails/emergency.py`). After consent, any message
   about a person's body, illness, pregnancy, labour, bleeding, injury or a child's illness (`BODY`, `HEALTH`,
   `MATERNAL`) goes to the classifier when the phrase list misses, unless it is a plain data question. A data
   question naming a person ("my", "she is") is still checked. The gate only decides whether the model is asked;
   the model decides whether it's an emergency. Before consent, only the phrase list runs, because no model may be
   called yet.
2. **The understanding step returns `urgent` and `urgent_reason`.** When it reads an emergency happening now and
   the fast path didn't fire, the handler goes straight to the fast path (`Detection.by = "understanding"`), as the
   maternal path when the reading's care is maternal. This net comes 2–4 s later than a phrase.

Traces: a fired fast path writes an `emergency:<phrase|classifier|understanding>` row with what each layer said,
in the background so the reply never waits. In keeping with the fast path's design, the row never holds the
message, the reason or the place. Every other trace has `safety` (phrase, classifier) and `urgent` in its
understanding reading (card 0 on the admin page).

Eval (`evals/emergency`, live): 64/64 must fire and 64/64 quiet. The off-list set is 20/20 fired with 0/20 false
alarms: 19 caught by the classifier and 1 ("Yarinyata ta sha maganin feshi na gona") only by the understanding step.
The fast reply's median is 0.12 s. `deploy/deploy.sh --smoke emergency` runs the 40 off-list cases on the server.

Place history: a SAM 3.1 outline over 20 ha (`SAM_MAX_HA`) is rarely one farm. The size is asked for instead, and
the reply says why ("about 47 ha, more than one farm usually is"). A size the farmer gives, or their corner pins,
keep the 50 ha limit.
