# Unit 8 final report — corrected owner-authored corpus

Updated November 4, 2026. This report supersedes the mixed-author human-dependent
metrics. The [previous report](historical-final-report-mixed.md), every original
raw result, the 56-attack baseline/after artifacts, original criteria, and the
single improvement remain preserved. No history was rewritten or pushed.

## Correction and privacy

The owner explicitly confirmed personally writing `THE TRANSITION.pdf`,
`supplemental essays.pdf`, and `UC.pdf` without generative AI, authorized their
non-sensitive coursework excerpts, and required local-only corpus text. Only
these three documents supply the active human cohort. Application questions,
instructor feedback, example essays, quoted material, family details, and other
uncertain text are excluded from the fixed eligible source positions.

The score-independent selection was frozen in `3a8a441` before corrected scoring.
The public selection plan records source PDF hashes and reviewed character
intervals. The builder takes consecutive 50-word windows within those intervals,
merges a final tail shorter than 25 words into the preceding window, and cycles
through document candidate lists in fixed order until 20 distinct excerpts are
selected. No scores are imported or consulted by the builder. It preserves all
non-whitespace Unicode, spelling, grammar, and punctuation; only extraction
whitespace is collapsed. Word windows may cut sentences, a disclosed limitation.

There are 7 excerpts from THE TRANSITION, 6 from supplemental essays, and 7 from
UC: **20 excerpts from three source documents, not 20 independent works**.
All 20 test false positives. The fixed first ten IDs test separation against the
same original ten AI samples. Some passages overlap material exposed in the
historical evaluation; this is a corrected deterministic dataset, not a newly
blind holdout. Selection did not depend on historical or corrected scores.

Public reproducibility inputs are `data/unit8/corrected_selection_plan.json` and
`data/unit8/corrected_human_manifest.json`: source/page/document positions,
word/character counts, source and sample SHA-256 hashes, and the frozen subset.
The actual excerpt text and extracted sources remain under ignored `.private/`.
No full personal PDFs or newly selected excerpt prose are committed. Authorized
access to the original PDFs is required to reproduce private text from metadata.
Earlier approved mixed-author excerpts/snapshots remain unchanged historical
records as requested; no new corrected text is added to them.

## Exact code versions and experimental conditions

`scripts/run_corrected_eval.py` exported the six exact runtime files from
`8524fa8` (before) and `ea0dbd4` (after) to ignored local directories. Their file
hashes match the corresponding original attack-run runtime hashes. Each run
started its own fresh local server using the existing environment, cached GPT-2,
loopback networking, debug off, and the same enabled 8/minute and 100/day policy.
Creator IDs were unique per legitimate request and no rate limit was disabled.
The processes shut down after each experiment; main's production files were not
swapped, changed, or used as a substitute for the historical versions.

The two corrected runs have the identical manifest/criteria/boundary fingerprint:
`49f5da7d11a651df575bc570f908b33b059559661baf01590605e8572e8ba8bb`.
Each version executed criterion 1 three times and criterion 2 three times:
**12 new real trials, 240 actual submissions total**. Only these two criteria
are human-corpus dependent. Criteria 3–5 retain their explicitly identified
original three-trial-per-version evidence; they were not claimed as newly rerun.

## Current criterion values and verdicts

The original `criteria.md` is unchanged. Each target must hold in all three
trials; missing responses cannot shrink denominators or be counted as passes.

| Criterion | Original target | Before trials 1 / 2 / 3 | After trials 1 / 2 / 3 | Verdict | Evidence |
|---|---|---|---|---|---|
| 1. False positives | At most 1 of 20 human excerpts labelled AI | 0/20 / 0/20 / 0/20 | 0/20 / 0/20 / 0/20 | MET | Corrected reruns |
| 2. Separation | AI mean - human mean >= 0.20 on 10+10 | -0.012319 / -0.012319 / -0.012319 | -0.012319 / -0.012319 / -0.012319 | MISSED | Corrected reruns |
| 3. Labels | 7/7 fixed numerical mappings; all 3 labels | 7/7 / 7/7 / 7/7 | 7/7 / 7/7 / 7/7 | MET | Original unaffected trials |
| 4. Appeals | 5/5 reasoning, status, and history checks | 5/5 / 5/5 / 5/5 | 5/5 / 5/5 / 5/5 | MET | Original unaffected trials |
| 5. Invalid input | 6/6 specified inputs return 400, no decision | 6/6 / 6/6 / 6/6 | 6/6 / 6/6 / 6/6 | MET | Original unaffected trials |

Corrected human mean is **0.5312565371862069**. The unchanged AI mean is
**0.5189370898250648**. Their difference is **-0.0123194473611421**, identical
before and after. The historical mixed-corpus gap was -0.056844013164074614;
the new gap differs by +0.044524565802932514. This numerical change comes from
the dataset correction, not a code improvement, and the +0.20 target remains
MISSED. Boundary, appeal, invalid-input, and false-positive verdicts do not change.

The corrected component means are:

- Model: human 0.514830, AI 0.509640; gap -0.005190.
- Style: human 0.5476830743724138, AI 0.5282341796501296;
  gap -0.0194488947222842.

Both components still rank the AI group lower on average; their equal average
inherits that ordering. Convex reweighting alone cannot produce a +0.20 gap,
and thresholds do not affect this numerical criterion. Genre, fixed window
length, shared documents, extraction, and small sample size limit generalization.
The numerical change cannot be attributed to author confirmation alone because
the declared excerpt boundaries/normalization also changed. No sample was
removed, reordered, rewritten, or replaced after corrected scores were observed.

Raw cases and exact responses are in `results/unit8/corrected/eval_before.json`
and `eval_after.json`. Each phase has 120 matching text-free audit events in its
own `.jsonl` file, leaving the original global audit log untouched. The corrected
comparison identifies historical versus rerun evidence for every criterion.
Public results store only metadata/hashes, scores, replies, IDs, and audit fields;
they do not embed the private human corpus.

## Unchanged attacks, limiter, and single improvement

The original staff files and both complete 56-case attack runs are unchanged and
were not rerun for this correction. Each still records 47 HELD and 9 BROKE:
9 unsure evasion outcomes (EV01–EV09), no staff-human AI accusations, and the
same injection/malformed/flood judgments. The original complete baseline and
failure diagnoses remain in `docs/unit8/baseline-analysis.md` and the README.

The only substantive improvement is still `ea0dbd4`: reject unsupported C0
controls (except tab/newline/carriage return) and DEL before inference. The
original after run changed only MF03 from 200/decided with scores to a useful
400/rejected event, without improving detection verdict totals. There is no
second signal/weight/threshold/label/handling change in this correction.
Both historical versions give the same corrected human-dependent results.

The original approved policy remains 8/minute and 100/day per valid stated
creator ID, source-IP fallback, with unauthenticated-ID limitations. The original
real flood remains eight 200s followed by seven 429s. Its records, original
465-event global audit log, and all previous evidence are preserved byte for byte.

## Reproduction, checks, and limitations

Selection used pypdf from the existing bundled document runtime; the exact
version is recorded in the public manifest. No package/model downloads or hosted
API calls were needed. Reproduction commands (use a Python with pypdf for the
first two) are:

```bash
python scripts/build_corrected_corpus.py --source-dir /path/to/original/pdfs
python scripts/build_corrected_corpus.py --source-dir /path/to/original/pdfs --verify
.venv/bin/python scripts/run_corrected_eval.py --label before --port 5059
.venv/bin/python scripts/run_corrected_eval.py --label after --port 5060
.venv/bin/python scripts/compare_corrected_eval.py
.venv/bin/python test.py
.venv/bin/python -m unittest discover -s tests -q
```

Builders and runners refuse to overwrite frozen inputs or completed trials.
Use a separate checkout/output location for a repeat while retaining committed
metadata/results and owner-private sources. Default scenario loading selects
only the corrected private corpus; a checkout without private text fails clearly
rather than silently reverting to mixed-author history. Public snapshots redact
private text. New tests cover deterministic disjoint selection, hash/order
validation, local-only snapshots, publication guards, and missing-private-input
behavior. Final validation passed 9 environment checks and 54 tests, and exact
PDF re-extraction reproduced every frozen boundary, hash, and private excerpt.
`results/unit8/corrected/verification.json` records the actual outputs, 240 audit
correlations, preservation checks, and a scan for private excerpt/15-word-fragment
leaks in introduced public files.

The detector remains a heuristic pattern service, not proof of authorship.
EV01–EV09 and criterion 2 remain unresolved for the same documented reasons.
Further classifier changes would be additional improvements and were not made.
The owner's preference remains avoiding false accusations, accepting more unsure
AI outcomes with costs borne by the platform. Appeals still require a staffed
process beyond recording under_review; creator IDs can rotate around quotas;
thread locks are not a multi-worker database. These limitations are not hidden
by the corrected cohort or unchanged MET verdicts.

## Local history and handoff

Original Unit 7/8 history is intact. Correction milestones include:

- `3a8a441`: deterministic corrected metadata/private-text controls frozen before scoring.
- `cd7ffd6`: historical-version correction harness and privacy/selection tests.
- `5d48ff8`: all six corrected before trials and audit events.
- `0c54540`: all six corrected after trials and honest dataset comparison.
- The final correction documentation/validation commit completes this report.

The owner supplied the authorship and privacy correction; Codex extracted and
froze the source-position cohort, ran the historical services, and updated reports.
No owner code edits, manual tests, or final review are invented. No push or portal
submission was performed. Review the corrected metadata/results before authorizing
any later push; the same repository URL remains the eventual CodePath submission.
