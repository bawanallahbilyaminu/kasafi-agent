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

## Before the deadline

The day-by-day record of what was built during the hackathon (26 Oct to 4 Nov 2026) is in the README of the
submitted version, under "Built during the hackathon", and in the git history up to `9e3c96e`.
