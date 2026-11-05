# Unit 8 final report — Provenance Guard

Completed locally November 4, 2026. The human corpus was created from the owner's
supplied PDFs and feedback and approved before scoring. Both complete staff runs
and all 30 criterion trials actually executed. The result is an honest evaluation
with one remaining missed target, not an accuracy or production-readiness claim.

## Implementation and approved policy

`app.py` and `audit.py` add request correlation and rejection auditing while
retaining all nine successful-decision fields and append-only appeal history.
400/404/413/429/503 responses on submission/appeal paths are observable without
logging full submitted writing or fabricating absent content IDs or scores.

The owner approved 8 submissions/minute and 100/day on `/submit`: a valid,
nonblank creator ID up to 200 characters, otherwise source IP. Separate key
namespaces prevent a creator string from colliding with an IP fallback. IDs are
unauthenticated and can be rotated; the cap does not cover global coordinated
abuse. In-memory counters reset on service restart; the audit log is retained.

The real 15-request flood returned:

```text
200 200 200 200 200 200 200 200 429 429 429 429 429 429 429
```

The enabled policy was reported by `/health`. The day window and scope/fallback
behavior are also tested using a controlled clock and small test-only limits;
we did not send 101 expensive real-model requests under one identity just to
exhaust the day limit. This distinguishes actual flood evidence from unit tests.

## Staff attacks

The owner identified `/Users/adi/Downloads/attack_set`. Only CSV headers were
displayed before the full baseline. The two copied source files are frozen with
SHA-256 hashes. Actual counts are 10 evasion, 8 false positive, 6 injection,
20 malformed, and 12 shared-creator flood: 56 total. The flood rows describe
20 submissions but contain 12; all actual rows ran, and none were invented.

All 56 ran before and after. Fresh processes established the same counter
conditions before each complete phase, without clearing audit history. There
were no 5xx responses or service crashes. Every attempt in both runs has exactly
one matching request-ID audit event.

| Family | Before HELD / BROKE | After HELD / BROKE |
|---|---|---|
| Evasion | 1 / 9 | 1 / 9 |
| False positive | 8 / 0 | 8 / 0 |
| Prompt injection | 6 / 0 | 6 / 0 |
| Malformed | 20 / 0 | 20 / 0 |
| Shared-creator flood | 12 / 0 | 12 / 0 |
| Total | 47 / 9 | 47 / 9 |

Judgments are explicitly objective-specific. Unsure on known staff AI counts as
an evasion miss, but unsure on human text is not an accusation or a confident
human certification. The first eight permitted flood requests are expected 200s;
the four above the cap are 429. Text-level edge cases are judged against the
published contract and safe uncertain handling; Arabic/emoji are not forbidden
merely by category. Injection verdicts concern requested output/audit overrides,
not proof that any score movement was caused by following instructions.

All nine broken IDs are EV01–EV09. Their exact scores, stage/mechanism mappings,
and causal limits are in `docs/unit8/baseline-analysis.md`. Key mechanisms include
model sensitivity to wording, surface variability, and the explicit neutral
style fallback for one sentence or fewer than 20 words. No paired ablation was
performed where needed to prove an edit's causal effect; those remain hypotheses.

For a legitimate writer, FP05 is the least comfortable staff outcome: human
technical documentation gets combined 0.721738, still unsure. No staff human
sample was called AI, and no automatic penalty occurred. Uncertainty and the
review burden remain real limitations rather than invented false accusations.

The README includes all 56 before and after rows and ten actual before audit
entries, including a 400 and a 429. Full raw replies, reviewed events, source
hashes, and the comparison are retained under `results/unit8/`.

## The original criteria — three trials per phase

The owner supplied and committed the criteria as `26e6ce2` before Unit 7's new
results; the earlier supplied transcript's default detector demo is disclosed.
`criteria.md` is byte-for-byte unchanged in Unit 8. The fixed owner-approved
cohort was committed as `f787792` before acceptance scoring.

| Criterion | Original target | Before trials 1 / 2 / 3 | After trials 1 / 2 / 3 | Verdict both phases |
|---|---|---|---|---|
| Human false positives | At most 1/20 AI labels | 0/20 / 0/20 / 0/20 | 0/20 / 0/20 / 0/20 | MET |
| Score separation | AI mean - human mean >= 0.20 on 10+10 | -0.056844 / -0.056844 / -0.056844 | -0.056844 / -0.056844 / -0.056844 | MISSED |
| Numerical label coverage | All 7 correct, all 3 labels | 7/7 / 7/7 / 7/7 | 7/7 / 7/7 / 7/7 | MET |
| Appeals | All 5 reasoning/status/history checks | 5/5 / 5/5 / 5/5 | 5/5 / 5/5 / 5/5 | MET |
| Invalid inputs | All 6 specified cases: 400, no decision | 6/6 / 6/6 / 6/6 | 6/6 / 6/6 / 6/6 | MET |

`run_eval.py` actually executes all five criteria three times per phase. Boundary
checks are direct `scoring.py::score_to_label` calls, clearly distinguished from
HTTP requests. Appeals use distinct real submission IDs and exact reasoning,
compare original decisions, and inspect latest persisted status. Invalid-input
checks correlate real rejection events and verify no successful decision. Errors
or 429s are never silently dropped from the fixed denominators. Preparation unit
tests were not substituted for these experiments.

Model/combined scores are deterministic; identical three-trial results are
expected and all are saved. Raw evidence is in `eval_before.json` and
`eval_after.json`, with generated `.md` tables and actual first-trial JSON.
The combined cohort/criteria/boundary fingerprint matches in both:
`689e45fb7ebd3004835e13f5625998543c105ca2b9ae2de28d59316f0c52447f`.

### Why separation was missed

All 20 separation requests in every trial returned usable decisions. Human
combined mean is 0.5757811029891394; AI mean is 0.5189370898250648. The model means
are human 0.562880 and AI 0.509640; style means are human 0.5886822059782788 and
AI 0.5282341796501296. Both component mean differences are negative, and averaging
preserves that reversed group ordering. This is a signal/combination limitation,
not a transport failure, missing-data problem, or threshold issue. Convex
reweighting alone cannot yield the required positive 0.20 difference.

The AI cohort includes creative prose and poetry, while human excerpts include
formal narratives and feedback. Genre, repeated source works, and extraction
may contribute; a controlled causal test would be needed to isolate them. No
sample was removed, replaced, or reordered after observing scores.

### Human-source qualification

The owner provided five PDFs and instructor feedback, stated all were human
written, and explicitly approved the proposed mixed-author corpus and committing
its excerpts. The file has 20 distinct source-linked excerpts, not 20 independent
works/authors. Some passages are example essays or instructor comments, so they
are not all attributed to Aditya Chopra. Human origin is user-attested rather
than independently verified. This differs from the course suggestion to use
one's own writing and limits what the results establish.

Samples 1–10 are the fixed separation subset. PDF ligatures and whitespace were
normalized; prompts/page furniture and incomplete fragments were excluded.
Original words/grammar were not rewritten. Source hashes, page references, and
exact excerpt boundaries are in `data/unit8/human_samples.json`. Only the approved
excerpts, not full personal PDFs, are committed. Ten AI pieces were generated
and fixed before scoring. All these qualifications remain visible in the record.

## Exactly one measured improvement

Dedicated commit `ea0dbd4` adds one pre-inference rule: reject C0 control
characters except tab/newline/carriage return, plus DEL, with HTTP 400 and a
useful `unsupported_control_characters` error. No signal, weight, threshold,
label, rate policy, original target, or cohort was changed.

The observed MF03 route weakness was a control-bearing string accepted for
inference and an authorship estimate. It was HELD under the permissive baseline
contract, not a crash or forced label; the narrower handling opportunity and
scope cost were documented before implementing it. This change responds to
that observation and makes no promise to solve detector accuracy.

After measurement, MF03 alone changes from HTTP 200/decided with scores to
HTTP 400/rejected without content ID or scores. The guard is before the model
call, verified by a test that the model is not invoked. All other 55 attack
cases retain status, guess, label, and scores. Total HTTP 200s change 37→36 and
400s 14→15, with one 413 and four 429s in each phase.

The change helps input handling and avoids one completed inference/decision on
this set. It does not improve attack verdict totals, false positives, score
separation, or criterion verdicts. No detection regressions were measured;
intentional use of the rejected controls now requires cleanup. Ordinary tabs,
line breaks, Unicode, emoji, and Arabic remain allowed. Cold/warm elapsed times
are not used to invent a latency or cost reduction. No second substantive fix
was added.

## Remaining failures and why the work stops here

EV01–EV09 remain unsure. Next investigations are paired spelling/vocabulary
ablations (EV01/EV04/EV05), matched sentence/quotation/mixed-text experiments
(EV02/EV03/EV06/EV09), and useful short-text provenance/evidence handling
(EV07/EV08). Each ID remains mapped to its actual stage and evidence in the
baseline analysis. The missed separation target needs better evaluation and
provenance evidence; changing weights cannot repair these group means.

Broader signal replacement, more datasets, authenticated identities, global
inference budgeting, staffed appeals, or a shared audit database would each be
additional independent work. The assignment calls for one measured change, so
these remain documented instead of being bundled into the experiment. IDs can
rotate around quotas; the current log lock coordinates threads only; recording
under_review is not a completed human review. This is a local coursework service.

The production preference remains the owner's: minimize false accusations and
accept more missed AI labels, with the platform bearing missed-detection and
review costs. Automated estimates must not alone justify punishment; practical
appeals need actual staff/process beyond this recording endpoint.

## Reproduction and verification

Commands actually executed, using the existing environment and cached weights:

```bash
.venv/bin/python test.py
.venv/bin/python -m unittest discover -s tests -q
HF_HUB_OFFLINE=1 .venv/bin/python scripts/check_integration.py --output results/unit8/integration_final.json
HF_HUB_OFFLINE=1 AI201_DEBUG=0 PORT=5058 .venv/bin/python app.py
.venv/bin/python run_attacks.py --flood 15 --url http://127.0.0.1:5058 --creator unit8-flood-baseline
.venv/bin/python run_attacks.py --set data/unit8/staff_attack_set --label before --url http://127.0.0.1:5058
.venv/bin/python run_eval.py --label before --url http://127.0.0.1:5058
.venv/bin/python run_attacks.py --set data/unit8/staff_attack_set --label after --url http://127.0.0.1:5058
.venv/bin/python run_eval.py --label after --url http://127.0.0.1:5058
.venv/bin/python scripts/review_attack_run.py --label before
.venv/bin/python scripts/review_attack_run.py --label after
.venv/bin/python scripts/compare_unit8.py
```

The service was restarted between each complete experiment to give fresh
in-memory counters with identical 8/minute and 100/day settings, without clearing
audit history. Review/compare scripts ran after their respective complete raw
runs. Completed artifacts deliberately refuse overwriting; reproduction should
use a separate checkout/output directory while retaining these originals and
the frozen manifests. The integration helper accepts a fresh `--output` path.

Final checks: 9 environment checks passed; 49 deterministic tests passed; four
real-model integration checks passed. The model loaded once across repeated
submissions; all three labels remain reachable; a real appeal persisted; the
new invalid-control rejection and allowed line formatting are covered. No
packages, model downloads, or hosted model keys were needed. The installed
Transformers fallback warning for `loss_type=None` remains harmless to these
successful checks. Individual acceptance failures are scientific findings,
separate from regression-test failures.

## Git history and submission

Unit 7 history and its original audit prefix are preserved. Meaningful Unit 8
milestones, in order:

- `51ef938`: rejection instrumentation and experimental plan.
- `1e663ad`: approved limiter and instrumentation tests.
- `e9d674e`: staff sources, fixed AI cohort, and repeatable evaluation harnesses.
- `dcd9c52`: complete staff baseline, flood, and per-failure diagnoses.
- `f787792`: approved human excerpt cohort frozen before acceptance scores.
- `8524fa8`: all 15 baseline criteria trials and separation diagnosis.
- `ea0dbd4`: the one substantive handling improvement, committed separately.
- `d53dd5f`: both after experiments and measured comparison.
- The subsequent final documentation/verification commit completes this report.

The README records actual owner decisions and Codex work without inventing owner
code edits, manual testing, or review of final outcomes. The working tree and
staged files are checked before handoff; virtual environments, secrets, caches,
and weights are excluded. No history is rewritten, and no new repo is created.

No push or portal submission has been performed. After reviewing the corpus,
results, and limitations, the owner can authorize a push or run:

```bash
git push origin main
```

Then submit the same fork URL to CodePath:
https://github.com/achopra5/ai201-project4-provenance-guard-starter-v2026
