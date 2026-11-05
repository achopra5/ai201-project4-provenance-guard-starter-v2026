# Unit 8 experiment plan and readiness

Recorded November 4, 2026, before staff attack execution or criterion evaluation.

## Baseline

Unit 7 ends at `522dfca` on `main`. The working tree was clean. Environment
checks passed 9/9 and the original deterministic suite passed 30/30. Keep the
five criteria in `criteria.md` byte-for-byte unchanged. The before detector is
0.5 model + 0.5 style, human through 0.20, AI from 0.85, unsure between, with
unchanged labels. Instrumentation may add audit metadata and limits, not retune
scores, validation decisions, or labels before the baseline.

The project brief and lecture require instrumentation, the full external attack
set, all five criteria across three trials, diagnoses of every miss, exactly
one measured improvement, and remaining-failure analysis. Repeated identical
scores are expected: the cached GPT-2 model is in eval mode and surface measures
are deterministic. The starter's suggestion that scores are inherently random
is inaccurate; record all three real trials anyway.

The lecture mentions 56 attacks across five families (10 evasion, 8 false
positive, 6 prompt injection, 20 malformed, 12 shared-creator flood). These are
expected counts, not observed results. Actual archive contents must establish
counts. A later slide mentions six false positives, so do not infer outcomes or
cardinality from that example. No staff payloads have been read or executed.

## Pending owner inputs

- Approve limits and caller identity. Recommended: 8/minute and 100/day per
  nonblank creator ID, source-IP fallback. This caps repeated work by one stated
  identity but does not authenticate it. Changing IDs can evade the cap. An
  IP-only policy would share the cap across users behind one address.
- Staff-provided archive with `attacks.csv` and
  `attacks_malformed_requests.csv`. No such files are in this repo, and no
  matching named archive was found in Downloads. Do not locate leaked copies,
  synthesize an official set, or inspect payloads before baseline execution.
- Twenty nonsensitive, owner-authored writing samples with explicit permission
  for coursework publication. Use the first ten in the frozen declared order
  for separation. Do not classify AI-authored material as verified human.

## Sequence

1. Complete rejection logging and the owner-approved limiter. Decisions retain
   all nine fields. Rejections retain available metadata only, with no invented
   content IDs or signal scores. Request IDs link HTTP evidence to audit events.
2. Test the actual limit with `run_attacks.py --flood 15`; save real statuses and
   append events to the existing audit log. Do not clear Unit 7 audit evidence.
3. Freeze human/AI sample manifests before obtaining any acceptance scores.
4. Obtain the staff archive, place it in the repo, read headers only, and run
   `run_attacks.py --set <folder> --label before` without modifying the detector.
   Preserve every outcome, source-file hashes, and raw response evidence. Mark
   HELD/BROKE against the actual stated objective after the complete run.
5. Run `run_eval.py --label before`: five criteria, three trials each, with no
   implementation changes between trials. Use unique request identities for
   independent valid submissions; use fresh, documented limiter windows for
   shared-IP invalid requests. Never disable production limits to make results
   pass. Boundary checks call the actual scoring function and are identified
   as direct checks rather than invented HTTP requests.
6. Commit attack and acceptance baselines before selecting an improvement.
   Map every failure to a pipeline stage and mechanism; distinguish hypotheses
   from conclusions supported by both scores, response, and audit events.
7. Propose exactly one improvement supported by those diagnoses. Obtain owner
   approval for changes to weights, thresholds, labels, or the safety tradeoff.
   Commit that change separately. No opportunistic unrelated fixes.
8. Restart the service with the same limiter policy and document the reset of
   in-memory counters. Run the same complete set and fixed samples as `after`,
   preserving separate raw artifacts. Compare regressions as well as gains.
9. Finish the five Unit 8 README sections, at least ten real audit entries
   including a rejection, all failure mappings, and the production tradeoff.
   Preserve Unit 7 history and collect four or more meaningful Unit 8 commits.
   Push and portal submission require final owner authorization.

## Verdict rules and remaining harness work

- Criterion 1: exactly 20 usable human decisions; at most one `ai` per trial.
- Criterion 2: exactly ten usable decisions per group; AI mean minus human
  mean must be at least 0.20 per trial. Errors/429s cannot silently disappear
  from the denominator or be treated as human-like scores.
- Criterion 3: the seven fixed scores and expected guesses in `criteria.md`;
  no threshold changes to the expected answers after observing scores.
- Criterion 4: five distinct actual submissions, five appeals, unchanged
  reasoning, original decisions retained, latest status `under_review`.
- Criterion 5: the six actual specified requests, each 400 and no decision
  logged. New rejection events are expected instrumentation, not decisions.
- Overall MET requires all three trials to satisfy the target. Missing sources
  mean NOT RUN, never MET or an invented failure score.

The starter evaluator only posts writing and cannot implement numeric scoring,
append-only appeal lifecycles, or malformed raw JSON. Extend its harness while
keeping the `--label before/after` interface. Unit tests verify harness mechanics;
they are not acceptance trials. Record cohort hashes, exact case counts, raw
responses, failures, and real audit evidence for independent reproduction.

No before/after outcomes, flood sequence, or chosen improvement exists yet.
This is a preparation record, not a completed Unit 8 submission.

## Owner decisions and source availability — November 4

The owner approved 8 submissions/minute and 100/day, keyed by a valid nonblank
creator ID with source-IP fallback. The implementation uses separate `creator:`
and `ip:` namespaces; IDs longer than the existing 200-character limit fall
back to the IP. No authentication is claimed. Rate limiting is enabled by
default. The owner identified `/Users/adi/Downloads/attack_set` as the staff set.
Both CSV files were copied to `data/unit8/staff_attack_set`; only their header
rows were displayed before execution. Their payloads remain unread by the agent
until the full baseline completes. The owner will supply human samples in chat;
that manifest and explicit publication/authorship confirmation remain pending.

The evaluator now has explicit paths for all five criteria and checks exact
case counts, all three trials, source/criteria fingerprints, failed responses,
appeal histories, and rejected requests' audit events. It refuses to evaluate
placeholder/missing human samples, overwrite an experiment, or run after with
changed cohorts. The attack runner saves raw response evidence and checkpoints
all completed attempts, preserves parse errors as a preflight blocker rather
than silently skipping rows, and requires identical source-file hashes after.

## Completed baseline checkpoint

The actual 15-request flood returned eight 200s followed by seven 429s. The
service was then restarted with the same policy and retained log for the staff
baseline. All 56 staff inputs executed; raw output is
`results/unit8/attacks_before.json`. Its objective-specific review records
47 HELD and 9 BROKE, with 56/56 HTTP-to-audit correlations and no 5xx/crashes.
The nine evasion misses all received unsure. No detection improvement or
acceptance evaluation has occurred. See `docs/unit8/baseline-analysis.md` and
the updated README for every attack and ten real audit entries.

Final preparation verification passed 9 environment checks and 47 deterministic
tests; the earlier four real-model integration checks also passed, with their
new rejection-event expectation. Source comparisons confirm the original
criteria, both signal implementations, scoring/labels, and the Unit 7 audit
prefix remain intact. The local server was stopped after the baseline to avoid
leaving an idle inference process. On receipt of the owner's 20 samples and
publication/authorship confirmation, freeze `human_samples.json`, commit the
cohort, start the same enabled policy with fresh in-memory counters, and run
`run_eval.py --label before --url http://127.0.0.1:5058`. Do not rerun the staff
before set or overwrite the recorded artifacts. Improvement selection follows
that completed criteria baseline.

## Human cohort approved and frozen before acceptance scoring

The owner supplied five PDFs and instructor feedback, stated all were human
written, and explicitly approved the proposed mixed-author corpus and committing
its excerpts. Twenty distinct source-linked excerpts were extracted before
scoring; samples 1–10 are the fixed separation subset. This is user-attested
human origin, not independent verification and not a claim of 20 independent
works or exclusively owner-written text. The manifest and cohort README preserve
these limitations and the explicit permission. No criteria targets are changed.
