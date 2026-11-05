# Changelog

## Which version is which

- **The hackathon submission** is the branch [`hackathon`](../../tree/hackathon) and the tag
  [`hackathon-submission`](../../tree/hackathon-submission): commit `9e3c96e`, made on 4 Nov 2026 at
  23:37 Lagos time (22:37 UTC), the last commit before the deadline (5 Nov 2026, 03:00 Lagos time). That branch is
  the repository's default and is never committed to again. Everything judged is there.
- **`main`** is the development branch. The live service (https://wa.me/2348039539665) is deployed from it, so it
  carries the bug fixes made after the deadline, listed below. Nothing below is part of the submission.

## After the deadline: bug fixes for the live service

Each entry is a fix for a failure a real tester hit on the live service, kept as a case in
[`evals/live_failures/`](evals/live_failures) with its regression tests. No new features.

### 5 Nov 2026

- `9e73700` **A question about local government budgets, when only state documents are held** (live trace 586,
  "How much was released for MNCH from the local government budget?"). The reply now says first that the library
  has no LGA budgets, only the state budget and its reports, and labels what follows as the state's. A list of
  zero-value "nearest lines" is never presented as an answer; the documents the plan named are read instead. An
  answer check that times out on Muse Spark Open is retried once on Muse Spark rather than skipped.
- `08b935b` **A zero spending figure** on the line actually asked about is one plain sentence with its budget
  ("₦0 of ₦X budgeted was released by Q3 2025"), never a bare "0.00".
- `68e4622` **An overview of one ministry** (live trace 590, "Tell me about the Ministry of Innovation and Digital
  Economy"). The code check had counted none of a deep analysis's 17 figures as printed on their cited pages,
  although all were, because it compared "₦100 million" with the page's "100,000,000.00" without the unit; the
  brief was then cut to one sentence. Fixed. An overview of one ministry now starts from the structured budget
  (the newest approved total with personnel, overhead and capital, spending so far, the year before) and adds
  what the documents say on top. A deep analysis the check sends back is rewritten once from its checked claims
  before any fallback. Every deep analysis gets the longer turn limit, so its check is not skipped for lack of
  time.
- `68e4622` **Privacy.** A name a user gives for themselves ("my name is …") is removed before the message is
  saved in the follow-up history or an answer trace; the prompts never repeat it or claim to know who the user
  is. The privacy page source says so.

- `1157c5b` **Figures on the right row** (follow-up to `68e4622`). On a table page a deep-analysis figure must now
  sit on a row that names what the claim is about, or it is dropped (`deep.row_bound`); before, a value printed
  anywhere on the cited page passed. Correction to this entry's first wording: trace 590's "₦42 million for
  computer purchases" was not a wrong pairing. The page prints 42,000,000.00 twice, as the office-repairs row's
  budget and as the actual spending of a computers row (budget 100,000,000.00, variance 58,000,000.00), and the
  draft cited the second. The tests now use every one of the ministry's rows on that page. Amounts with the scale word first, as Hausa writes them ("miliyan 100"), are matched to the
  printed figure like "₦100 million" is; `tests/test_amount_forms.py` pins every written form on every check.

- **The answer check on answers with a part computed in code** (live trace 629). The check had asked for off-subject
  figures to be dropped from a ministry overview and was overridden, because the budget profile above them was
  computed in code. The override now covers only the part code computed. A part written from documents (and a deep
  analysis alone) keeps the verdict, and a revise triggers the rewrite. An overview of one ministry, LGA, facility or
  sector keeps only document figures whose page names that subject, and its page crops come from rows about it.
- **A long analysis timing out.** A question read as a deep analysis but worded without the broad-question words got
  the short time limit and ended in "took too long". The reading now sets the limit.

### A change that is not a bug fix

- **A stated name, for one hour** (5 Nov 2026, asked for by the owner). When a user tells Kasafi their name in a
  message, it is held in the server's memory for an hour after their last message and may be used, sparingly, in
  a greeting or a thank-you. It is never written to disk (the follow-up history, traces and logs hold
  "[name removed]"), the WhatsApp profile name is never used, and DELETE MY DATA clears it. This replaces the
  `68e4622` behaviour above (never kept at all). The privacy page source says so.
- **The name is read by the understanding step, and removed from every store** (follow-up, same day). The first
  version found a name by its wording and only when capitalised. The conversation-understanding reading now
  returns it (`user_name`: "my name is musa", "Ni ne Musa", "Call me Musa", "Musa ne sunana"; eval cases
  p01-p14), and a name it returns must be in the message itself. The reading kept in a trace never carries it.
  The same redaction now also covers the review queue's gaps and sites awaiting approval, and a voice question
  waiting for its read-back, pending choices and clarifications in the user store.
- **Held data is deleted when its time is up.** A sweep every minute deletes names, locations and first messages
  held in memory past their time, including those of users who never come back; before, they became unusable but stayed
  in memory. The privacy page source now lists the providers actually used (Fireworks AI, no Baseten, no Azure) and
  says exactly what happens to a name, including its limits.

## Before the deadline

The day-by-day record of what was built during the hackathon (26 Oct to 4 Nov 2026) is in the README of the
submitted version, under "Built during the hackathon", and in the git history up to `9e3c96e`.
