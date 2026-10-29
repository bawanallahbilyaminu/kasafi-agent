# Kasafi architecture and build plan

## Users and the core experience

- **Citizens** (often low-literacy Hausa speakers), **civil servants** (e.g. Sokoto Ministry of Budget and Economic Planning), and **development partners**.
- A user sends a WhatsApp **voice note or text in Hausa** (or English). Kasafi replies in the same language with:
  1. a short, plain answer
  2. citations, e.g. `[1] Kasafin Jihar Sokoto 2025, shafi 34`
  3. an **evidence image**: the exact table or row cropped from the source page (SAM 3.1)
  4. optionally a **voice note** reply (depends on text-to-speech availability)

## Agent flow

> **Status (Oct 27):** single-document answers are live (`app/agent/answer.py`: plan → find → answer → number
> check), on typed questions, clearly heard voice notes and confirmed or corrected read-backs. Multi-document
> evidence lists, the calculator, the verify pass, live fetching and SAM 3.1 crops are next.

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

## Decisions (confirmed with Bilyaminu, Oct 26)

- **Backend:** Python + FastAPI.
- ~~**Storage**~~ **Decided (Oct 26):** PostgreSQL + pgvector, one database for documents, chunks, tables, provenance and the review queue.
  - **Dev:** local Docker Postgres 17 + pgvector.
  - **Deploy (changed Oct 27, Bilyaminu chose option A):** a **Postgres 17 + pgvector container on the VPS**, in the `kasafi-agent` compose project.
    - It has no published port; only the API container reaches it, on the private network.
    - Its password is generated on the server in `deploy/db.env`.
    - Nightly `pg_dump` backups are kept for 7 days in `deploy/backups/`. An off-server copy is still to do.
    - The index is copied from the dev DB with `deploy/deploy.sh --sync-index`.
    - The Azure option below is kept for later. The same migrations work there.
  - **Deploy (original plan, deferred):** Azure Database for PostgreSQL Flexible Server (Burstable B1ms, free tier), pgvector enabled via `azure.extensions=VECTOR`, SSL required, firewall limited to the VPS IP.
  - Same schema and Alembic migrations for both; switch with `DATABASE_URL` in `.env`.
  - The app (VPS) and DB (Azure) are on different networks, so **keep round-trips per answer minimal**: batch queries, fetch what a step needs in one query, avoid N+1 patterns.
  - Click-by-click Azure setup steps to be written at deployment time.
- **Embeddings:** the Meta Model API has no embeddings endpoint, so we run an open embedding model locally on CPU (in Docker on the VPS) and combine it with Postgres full-text search (hybrid retrieval).
  - **Built (Oct 29):** **BAAI/bge-small-en-v1.5** (ONNX via `fastembed`, 384 dimensions, ~200 MB RAM, baked into the image) embeds every budget line's name plus its codes' standard descriptions (`app/retrieval/line_meaning.py`, migration 0006). Line search fuses the keyword and meaning rankings (`line_search.fuse`). BGE-M3 was the first plan; the small English model was chosen because the documents and search queries are English and it fits the API container. Page chunks are still keyword-only.
  - The documents are in English, so the **agent translates the Hausa question into English search queries** before retrieval rather than embedding the Hausa directly. Answers are still written in the user's language.
- **Speech-to-text:** `muse-voice-transcribe-1.0` does **not** list Hausa (25 languages) and accepts WAV only (mono 16-bit PCM, 16/24 kHz, at most 10 min, at most 32 MB), so WhatsApp OGG/Opus voice notes need ffmpeg conversion. `muse-spark-1.3` accepts audio input directly.
  - **Decided (Oct 27), after testing 16 of our own voice notes** (`evals/stt-hausa-2026-10-26.md`): no single model is reliable on Hausa, so we use a **combined pipeline**. Voice Transcribe and `muse-spark-1.2` audio run in parallel, then one Spark text call reconciles the two into a Hausa transcript, an English version and a confidence level.
  - When confidence is low, or the two disagree on a year, number or place, Kasafi **reads back** its understanding ("Kana nufin …?") before doing any retrieval.
  - Unclear audio never gets an answer: the guardrails can't rely on the transcript alone.
  - **Guardrails must also check the raw hypotheses** (`SpeechResult.hypotheses`). The merge dropped "'yan bindiga" with high confidence in 3 of 4 tries (`evals/stt-hausa-2026-10-26.md`).
  - **Read-back and correction:**
    - The read-back quotes what was said, in the language it was spoken; the English translation is only for search.
    - The pending question is kept for at most 15 minutes, and deleted with the user's data.
    - Eh/Yes confirms and A'a/No cancels. A short correction ("2025") is merged into the pending question by Muse Spark; a clearly different question is treated as new.
    - A "🎧 Ina sauraro…" ack goes out as soon as a voice note passes the consent and limit checks.
  - Muse Spark Open on Baseten (`audio_url`) was tested too: 7/17, and it often ignores the audio at random, so it stays out of the speech path. It is used for text tasks instead.
- **Text-to-speech:** the Meta Model API has none, so we use Meta's open-weight **MMS-TTS Hausa** (`facebook/mms-tts-hau`, VITS, 36M params, CPU). Its license is **CC-BY-NC 4.0**: fine for the hackathon, but commercial use later needs another provider.
  - Voice replies are **short**: a 1–2 sentence spoken summary. The full answer, citations and evidence image are sent as text.
  - A **Hausa number normaliser** runs before TTS, e.g. "₦2.4bn" becomes "Naira biliyan biyu da miliyan ɗari huɗu" and "2025" becomes "dubu biyu da ashirin da biyar". It gets its own unit tests.
- **Access and consent (decided Oct 27).** Kasafi is open to everyone (`KASAFI_OPEN_ACCESS`; the pilot allowlist is the fallback), but consent comes first:
  - **First contact:** a bilingual notice with [OK / Na yarda] [Hausa] [English] buttons. Nothing reaches a model until the user agrees.
  - **Reply language:** detected locally from the first message and switchable at any time.
  - **Limits:** per-number daily limits (20 voice notes, 50 questions) and a global daily spend cap.
  - **Storage:** state is kept in SQLite on a Docker volume and keyed by HMAC(number). It moves to Postgres later.
  - **Spoken replies:** Hausa voice replies only go to users in Hausa mode.
- **Scope guardrails (built Oct 27, `app/guardrails/scope.py`).** They run after the emergency referral, on typed text, voice notes (the merged transcript plus both raw hypotheses) and corrected questions.
  - **Keyword tier (no model):** catches clear cases, i.e. eval 13 (electoral), 14 (verdict), 16 (security) and medical advice.
  - **Muse Spark tier:** runs only when a borderline word appears (gwamna, zaɓe, tsaro, magani, …).
  - **Replies:** a polite refusal in the user's language. A verdict question is redirected to "facts side by side".
  - **Security budgets:** in scope when `KASAFI_ALLOW_SECURITY_BUDGET=true`. Bilyaminu chose true (Oct 27); the code default is the strict reading of rule 5.
  - **Election budgets:** budget lines for the state electoral commission are in scope.
- **Data retention, confirmed with Bilyaminu (Oct 27).** The published privacy policy (halalnumeriq.com.ng/kasafi; source in `docs/site/`) promises the following, so the code must enforce it:
  - **Voice notes:** audio is held in memory only, plus a temporary file for ffmpeg that is deleted straight away. It is never stored, and it is discarded as soon as it has been transcribed.
  - **Conversations** (messages and replies): deleted after **90 days**.
  - **Logs:** kept **30 days**. They never contain message text or full phone numbers.
  - **Deletion requests** (GOGE BAYANAI NA / DELETE MY DATA, or email): completed within **7 days**.
  - **AI providers** receive question content only, never the phone number or WhatsApp name.
- **Admin / review queue:** a minimal FastAPI + HTML admin page behind HTTP basic auth (`ADMIN_USER` / `ADMIN_PASSWORD` from `.env`, with a strong password). It moves to Clerk later, when the React app is built.
  - **Review queue:** logged gaps and `auto-indexed` documents waiting for `human-verified` status.
  - **Agent trace view** (used in the demo video): for each question it shows the plan, the documents found and fetched, the evidence list and the verification result. The agent therefore saves one trace record per question, written in a single insert at the end so the database round-trips stay low.
  - **Built Oct 29** (`app/admin`, `app/agent/trace.py`, table `traces`):
    - `/admin/traces`: every answer, with outcome, path, time, flags and readers; `?flagged=1` shows only flagged ones.
    - `/admin/traces/{id}`: the plan, the two readings side by side (Muse Spark and Muse Spark Open, rows both chose marked ✓), what code verified and computed, citations, timings and the reply sent.
    - `/admin/review`: open gaps, plus answers flagged partial, not found, unverified, readings disagreed, or Open fell back. Each has a close or mark button.
    - A trace stores the English wording only, with no user key, and is purged after 30 days.
    - Pages return 404 unless both `ADMIN_USER` and `ADMIN_PASSWORD` are set. Form posts must come from the same site.
- **Seed documents:** about 20 core public Sokoto documents, a mix of URLs and local PDFs that Bilyaminu provides. The files go in the gitignored `data/`. Only `data/manifest.json` is committed, with the source URL, SHA-256 hash, title, year and publisher of each document.

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
