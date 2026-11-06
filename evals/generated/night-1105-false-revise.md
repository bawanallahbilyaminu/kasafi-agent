# Night run of 5 Nov 2026: false-revise measurement

**Not measured.** The run was stopped 41 s after it started and finished no case. The fresh set is still at 4 of 52,
and those 4 ran on older code. So there is no false-revise rate for the fixed code, and no
`report-fresh-1105.md`: the runner writes that file only when a run ends (`evals/generated/run.py`).

## What happened

| Time (Lagos, 5 Nov) | Event |
|---|---|
| About 16:07 to 16:13 | First attempt: 4 cases finished, then stopped by the system for low memory |
| 22:03:12 | Night run started, database up, resuming from the 4 finished cases |
| 22:03:24 | All 52 paraphrases already present, so no paraphrase call was made |
| 22:03:53 | Stopped by Claude Code because the laptop was critically low on memory |

It was not restarted, as instructed. The stop was a memory decision by the tool, not an error in the run. What was
using the memory at 22:03 was not recorded. At 11:10 on 6 Nov the laptop had 0.8 GB free of 15.7 GB.

## False revises in what did finish

A false revise is a first verdict of revise on a draft whose figures were already right. The runner's score is the
check on the figures.

| Old override would have covered it | Answers | Checked | First-verdict revise | False revise | Draft differs from sent answer | Runner: ok / wrong |
|---|---|---|---:|---:|---:|---|
| Yes | 1 | 1 | 0 | 0 | 0 | 1 / 0 |
| No | 3 | 2 | 0 | 0 | 0 | 2 / 1 |
| **All** | **4** | **3** | **0** | **0** | **0** | **3 / 1** |

0 of 3 is too few to be a rate, and it does not describe the fixed code. These cases ran before `7e41450` (18:01),
which added `not_asked`, and before `71ff91c` and `49624f6`.

The one uncovered answer with no check is lookup-01: the check was skipped with "too little time left".

## Slowest answers

| Case | Form | First verdict | Time | Runner |
|---|---|---|---:|---|
| lookup-01 | code-switched | skipped | 165.0 s | wrong: not found, though the data has it |
| lookup-03 | follow-up | pass | 58.5 s | ok |
| lookup-04 | code-switched | pass | 36.3 s | ok |
| lookup-02 | template | pass | 30.6 s | ok |

Every model step here ran on Fireworks. Live, compose runs on Muse Spark, so these times are not live times.

## Against earlier fresh reports

| Run | Cases | Wrong | Median | Lookup family |
|---|---:|---:|---:|---|
| `report-predeploy-followup2.md` (1 Nov) | 52 | 1 | 6.2 s | 6 of 6 ok, 8.5 to 15.4 s |
| This one (5 Nov) | 4 of 52 | 1 | 47.4 s | 3 of 4 ok, 30.6 to 165.0 s |

Both numbers look worse, but this is not a like-for-like comparison. The 1 Nov run used another draw of questions,
ran mostly on Muse Spark and had no answer check. The times do fit the 41 to 49 s measured for one question on
Fireworks on 4 Nov.

lookup-01 is the one result worth following up: a plain budget lookup used its whole 165 s limit and ended in "please
ask again". The case records three finished model calls and one reading that fell back after 20 s, so where the rest of
the time went is unknown. One case can't show a regression, and it has not been rerun.

## Cases and spend

| Item | Result |
|---|---|
| Cases finished | 4 of 52 (0 by the night run) |
| Night run spend recorded | $0.00 (daily ledger unchanged at $1.49; no `model_spend` row after the 15:00 UTC hour) |
| Fresh set spend so far | $0.42, of which about $0.22 is Meta and $0.20 is Fireworks |
| All eval spend on 5 Nov | $1.49 of the $3 cap |

Calls still in flight at the stop are not recorded. The kill came 29 s after start-up, so that should be a few cents at
most. Only the Fireworks dashboard can confirm it.

## Correction

The 5 Nov measurement note said every step ran on Fireworks. That was wrong: `evals/generated/paraphrase.py` always uses
Meta, and the first attempt made 52 paraphrase calls there (about $0.22 at the settings price). That goes against the
default of no Meta calls in eval runs. The night run made none, because the paraphrases already existed. The script is
not changed.

## To finish the measurement

The 48 remaining cases would cost about $2.30, going by Fireworks spend of about $0.05 a case over 4 cases. That is more
than the $1.63 the night run allowed, so it would have stopped at about 33 more cases even with enough memory. The 4
finished cases should be reported apart from the rest, because they ran on older code.
