# The one Unit 8 handling improvement

Baseline attacks and all 15 acceptance trials were committed before this change
(`dcd9c52` and `8524fa8`). The original cohort was frozen in `f787792`.

## Change

In `app.py::submit`, reject C0 control characters other than tab, newline, and
carriage return, plus DEL, with HTTP 400 before either signal is evaluated.
Return `unsupported_control_characters` with an instruction to remove the
controls and resubmit. Existing audit instrumentation records the rejection.

This is one input-validation rule, not multiple signal/weight/threshold changes.
Normal prose, Unicode, emoji, ordinary multiline writing, limits, scoring,
reader labels, appeal behavior, and rate-limit policy otherwise retain baseline
behavior. Submitted writing is rejected rather than silently cleaned/reclassified.

## Evidence and expected effect, recorded before the after run

MF03 contains NUL, control bytes, and terminal escape sequences mixed with
words. Baseline response: HTTP 200, model 0.0, style 0.5, combined 0.25, unsure.
It did not crash and met the permissive baseline contract, so the frozen review
rules correctly called it HELD. The narrower handling weakness is accepting
unsupported control-bearing input for expensive inference and an authorship
estimate. The missing guard is directly visible in the original route.

Expected benefit: this case will produce an explicit 400 rejection with no
completed decision or inference. All ordinary corpus samples and allowed line
formatting should preserve exactly the same numerical scores and behavior.
Expected cost: callers intentionally sending prohibited controls must remove
them; tab/newline/carriage return remain permitted. The rule is not a ban on
non-Latin writing or punctuation, and is not a detector-accuracy claim.

The criteria baseline found the only missed criterion to be score separation:
human mean 0.575781, AI mean 0.518937, difference -0.056844 versus +0.20.
Both component mean differences are negative; reweighting alone cannot fix it.
No detection gain, improved separation, or evasion verdict change is promised
for this handling improvement. Those scientific limitations remain visible.

## Measurement plan

Restart with the same 8/minute and 100/day policy and retain the append-only
log. Execute the same staff set as `after`, followed by the same five criteria
three times with the frozen cohort and unchanged original targets. Save raw
before/after separately and apply the same review rules. Compare every attack,
criterion value, and any regression, plus MF03's status, audit event type, and
presence/absence of completed signal scores. Do not infer wall-clock savings
from an uncontrolled cold/warm timing comparison.

No other substantive fix is authorized as part of this experiment. A broader
classifier improvement needs appropriate validation data and is deferred rather
than tuned on this small mixed-source cohort.

## Actual after results

The complete set and all five criteria ran again, with source/cohort hashes
unchanged and fresh in-memory counters for each phase. MF03 alone changed:
200/decided with scores became 400/rejected without scores. All other 55 attack
responses retain statuses, labels, and scores. The original review rules still
mark the set 47 HELD/9 BROKE. All 56 audit correlations hold in both phases.

All three after trials reproduce each before criterion value: false positives
0/20; separation -0.056844; boundary checks 7/7; appeals 5/5; invalid cases 6/6.
Four criteria are MET, separation MISSED. No detection benefit or controlled
latency saving is claimed. The handling improvement worked for its one targeted
case and leaves the scientific failures visible. Raw and derived comparisons
are in `results/unit8/comparison.json`. No second substantive change was made.
