# Kasafi architecture and build plan

## Users and the core experience

- **Citizens** (often low-literacy Hausa speakers), **civil servants** (e.g. Sokoto Ministry of Budget and Economic Planning), and **development partners**.
- A user sends a WhatsApp **voice note or text in Hausa** (or English). Kasafi replies in the same language with:
  1. a short, plain answer
  2. citations, e.g. `[1] Kasafin Jihar Sokoto 2025, shafi 34`
  3. an **evidence image**: the exact table or row cropped from the source page (SAM 3.1)
  4. optionally a **voice note** reply (depends on text-to-speech availability)

## Agent flow

```
WhatsApp webhook (FastAPI on VPS)
 ├─ voice note → Muse Voice Transcribe → text   (verify Hausa support)
 ├─ guardrails: political / war / medical-advice → polite refusal
 ├─ quick ack if slow: "Ina duba takardu 3…" (two-step reply)
 └─ Agent (Muse Spark via Meta Model API; Muse Spark Open via Baseten when available)
      1. PLAN       break question into sub-questions; list documents needed (max 3–4)
      2. FIND       for each doc: local index → partner APIs → web search (allowlist)
      3. ACQUIRE    if not indexed: download → sandbox parse → read relevant pages (vision) → index
      4. EVIDENCE   extract facts into an evidence list: {doc_id, page, quote/value, unit, year}
      5. ANSWER     write ONLY from the evidence list; every sentence cites [n]
      6. VERIFY     second pass checks each claim against its quote; drop/flag anything unsupported
      7. EVIDENCE IMG  SAM 3.1 crops the source table from the page image
      8. GAPS       anything not found → honest message + human review queue
```

### Agent tools

| Tool | Purpose |
|---|---|
| `search_index(query, filters)` | Search indexed documents (chunks with page numbers). |
| `find_document(description)` | Local index → ReliefWeb API / World Bank Documents API (partner reports) → Serper web search limited to allowlisted domains (`site:` + `filetype:pdf`, `gl=ng`). Returns candidates with URLs. |
| `fetch_and_index(url)` | Allowlist check → download (size limit) → sandboxed parse → page text (vision OCR for scanned pages) → index with provenance. |
| `query_table(doc_id, filters)` | Structured budget lines extracted from tables (sector, MDA, LGA, year, approved/revised/released/spent, unit). |
| `calculate(expression, inputs)` | Exact arithmetic (percentages, changes). Never do maths "in the head". |
| `crop_evidence(doc_id, page, target)` | SAM 3.1 crops the table/row as an image. |
| `log_gap(question, missing_doc)` | Adds to the human review queue. |

### Self-growing document library

- Answers are not limited to pre-indexed documents. When a needed document is missing, the agent finds, fetches and indexes it, so the next user benefits.
- **Allowlist only** (to be built from real search tests): Sokoto State government domains, federal sites such as budgetoffice.gov.ng, worldbank.org, unicef.org, undp.org, reliefweb.int, etc.
- **Provenance** for every document: source URL, date fetched, SHA-256 hash, title, year, publisher, status `auto-indexed` | `human-verified`.
- **Versions:** prefer the latest or revised version, and say which version is cited.
- **Index relevant pages first**, the rest in the background.

### Multi-document answers: important rules

- **Disagreeing figures** (approved vs revised vs released vs actual): show them side by side with sources and explain the difference. Never average them or silently pick one.
- **Normalize units and years** at the evidence step (₦, ₦'000, ₦ million; fiscal vs calendar year).
- **Partial answers** are fine. Say what was found and what wasn't, and log the gap.
- **Neutral tone.** Put facts side by side and draw no conclusions about government performance.

### Showcase demo questions (TO FILL IN with Bilyaminu)

1. Across years (e.g. one sector across three budgets): _TBD_
2. Policy, budget and partner report: _TBD_
3. Across partners (who works on X, where): _TBD_
4. The self-growing moment: a question about a document that isn't indexed yet, which Kasafi then finds live: _TBD_

## Open decisions (confirm with Bilyaminu before scaffolding)

- **Backend language:** proposed Python + FastAPI (best fit for the AI/PDF tooling). Bilyaminu also knows the MERN stack.
- ~~**Storage**~~ **Decided (Oct 26):** PostgreSQL + pgvector, one database for documents, chunks, tables, provenance and the review queue.
  - **Dev:** local Docker Postgres 17 + pgvector.
  - **Deploy:** Azure Database for PostgreSQL Flexible Server (Burstable B1ms, free tier), pgvector enabled via `azure.extensions=VECTOR`, SSL required, firewall limited to the VPS IP.
  - Same schema and Alembic migrations for both; switch with `DATABASE_URL` in `.env`.
  - The app (VPS) and DB (Azure) are on different networks, so **keep round-trips per answer minimal**: batch queries, fetch what a step needs in one query, avoid N+1 patterns.
  - Click-by-click Azure setup steps to be written at deployment time.
- **Embeddings model:** check whether Meta Model API offers embeddings; otherwise pick an open model.
- **Text-to-speech for Hausa replies:** depends on what Meta offers.
- **Review queue UI:** a minimal admin web page vs. a Notion database.
- **Seed documents:** about 20 core public Sokoto documents. Bilyaminu provides the list or files (stored outside git or in a gitignored `data/`; commit only a manifest of URLs).

## Proposed repo layout

```
kasafi-agent/
  CLAUDE.md
  README.md            # includes "Built during the hackathon" + "Pre-existing assets"
  .env.example
  app/
    main.py            # FastAPI: WhatsApp webhook, health check
    whatsapp/          # send/receive, media download, signature check
    agent/             # planner, tools, evidence list, verifier, prompts (Hausa)
    retrieval/         # indexing, search, table extraction
    acquisition/       # search providers, allowlist, fetch, sandboxed parse
    evidence/          # SAM 3.1 crops
    guardrails/        # political / war / medical refusal
    providers/         # Meta Model API, Baseten, Serper, ReliefWeb, World Bank (swappable)
  data/                # gitignored; manifest.json committed
  evals/               # ~15 questions with expected answers + runner
  deploy/              # Dockerfile, docker-compose, nginx/HTTPS notes
```

## Build plan (Lagos dates)

| Day | Goal |
|---|---|
| Tue Oct 27 | Repo, skeleton, Meta API "hello", WhatsApp webhook echo on VPS, **test Muse Voice Transcribe on Hausa**. Watch Agents 101. |
| Wed Oct 28 | Index seed docs with page numbers; single-document answers with citations. Watch Agents 102. |
| Thu Oct 29 | Agent loop + tools; evidence list; multi-document answers (2–3 docs). |
| Fri Oct 30 | Self-growing library: find_document (Serper + ReliefWeb + World Bank), allowlist. Fireworks session. |
| Sat–Sun Oct 31 – Nov 1 | fetch_and_index in sandbox, table extraction, verify pass, review queue, guardrails. |
| Mon Nov 2 | SAM 3.1 evidence crops; voice replies; Hausa polish. |
| Tue Nov 3 | Evals, bug fixes, deploy hardening (last help day). |
| Wed Nov 4 | Demo video (3 min), README, X post; **submit by the evening** (hard deadline 3 AM Nov 5). |

Stretch goals (only if ahead of schedule): Fireworks LoRA fine-tune for natural Hausa; web UI.
