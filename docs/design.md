# Unit 7 implementation design

## Scope and current state

This document records the design before implementation. Unit 7 builds the
submission, scoring, disclosure, and appeal flow. Unit 8 rate limiting, attack
execution, criterion evaluation, and remediation remain future work.

The initial repository contains working `/ping`, `/health`, `/log`, the local
GPT-2 detector, and append-only audit helpers. `/submit` and `/appeal` return
501; stylometry returns constants; scoring uses placeholder weights and labels.
No evaluation artifacts were present in `logs/` or `results/` at the audit.
The supplied terminal transcript already contains a score for the detector's
default demonstration paragraph. That is prior environment/demo output, not a
criterion evaluation; it cannot honestly be described as unseen.

Baseline on October 31, 2026: `.venv/bin/python test.py` reports 9 passed,
0 failed, 0 warnings. No detector calibration, criterion evaluation, or attack
run has been performed in this work.

## Submission flow

1. A caller sends a JSON object to `POST /submit` with `text` and `creator_id`.
2. The route validates the object, string fields, nonblank values, and resource
   bounds before invoking the model. Invalid input returns a JSON error.
3. `detector.model_signal(text)` measures predictability using the cached local
   GPT-2 model. The route never creates or reloads a model itself.
4. `stylometry.style_signal(text)` independently measures sentence-length
   variability, word variety, and punctuation density.
5. `scoring.combine_signals(model_score, style_score)` applies the agreed
   numerical rule. Higher scores mean more AI-like patterns. This score is
   a heuristic index, not a calibrated probability or proof of authorship.
6. `scoring.score_to_label(score)` maps the score to exactly one of `human`,
   `unsure`, or `ai`, paired with the agreed reader-facing sentence.
7. The service creates a UUID, persists both signals, the combined score,
   label, and `decided` status through `audit.log_decision`, then returns JSON.
   A successful response must follow successful persistence.

## Signals and blind spots

The model uses mean next-token negative log likelihood to compute perplexity
on at most the first 400 GPT-2 tokens. Its existing conversion is
`1 / (1 + (perplexity / 45) ** 1.6)`. Predictable continuations may resemble
generated writing, but familiar phrases, plain human prose, and second-language
writing can also be predictable. Rare vocabulary or edits can raise perplexity.
Text beyond the truncation boundary is not assessed by this signal. GPT-2 is
a language model, not an authorship classifier; it does not establish meaning,
intent, provenance, or misconduct. Submitted instructions are text to score,
never commands to execute.

Stylometry measures surface form without model probabilities: dispersion of
sentence lengths, unique words relative to total words, and punctuation relative
to text length. Regular prose and repetition can resemble generated writing;
varied human prose may differ. Poetry, short writing, length differences,
abbreviations, quotations, language, and typos all undermine these heuristics.
Its normalization must be documented with its implementation, and edge cases
must return finite values. Two different measurements can still share biases;
they are not statistically independent evidence of authorship.

## Proposed HTTP contracts

These are implementation contracts, not acceptance criteria. Numerical policy
and reader-facing wording remain pending the project owner's decisions.

### `POST /submit`

Request: `{"text": "A piece of writing", "creator_id": "writer-123"}`.
Both fields are required nonblank strings. Preserve submitted writing for
scoring rather than rewriting its punctuation or whitespace. Ignore extra
fields. Bound text length and total body size explicitly; document final limits
in the README. Too little text for the detector must produce a clear client
error rather than an invented signal.

Success: HTTP 200, with `content_id` (unique UUID string), `guess` (`human`,
`ai`, or `unsure`), `confidence` (finite combined AI-likeness index in [0, 1]),
`label` (reader-facing text), `model_score` and `style_score` (finite numbers in
[0, 1]). An additional `status: "decided"` is compatible with existing tools.
`confidence` always points toward AI, including when `guess` is `human`;
clients must not interpret it as probability that the returned guess is true.

Errors: HTTP 400 for malformed/non-object JSON, missing/invalid fields, blank
or unscorable text; HTTP 413 for excessive input size; HTTP 503 for unavailable
local detector. Return a JSON object with a machine-readable `error` and a
useful `message`. Do not log an unavailable-model request as a completed decision.

### `POST /appeal`

Request: `{"content_id": "existing-uuid", "reasoning": "I wrote this myself."}`.
Both fields are required nonblank strings; bound reasoning length. An ID must
match an original decision, not merely any unrelated audit event.

Success: HTTP 200, with the original `content_id`, `status: "under_review"`,
and a confirmation `message`. Append `audit.log_appeal` with the original
creator ID and the supplied reasoning. Retain the original decision unchanged.
Repeated appeals append further review requests; they do not reset the score or
claim a review has already occurred. No automatic reclassification is required.

Errors: HTTP 400 for invalid fields/JSON, HTTP 404 for an unknown submission,
HTTP 413 for excessive input size. Restarting the service must preserve the
appeal state because the log, rather than process memory, is the source of truth.

### Existing endpoints and audit compatibility

Leave `/ping` as the starter control. `/health` reports model loading and log
count. `/log` returns append-only events, oldest first; optional `limit` selects
recent events. An item's latest status is the last event for its content ID.

Keep the decision fields `timestamp`, `content_id`, `creator_id`, `guess`,
`model_score`, `style_score`, `combined_score`, `label`, and `status`. Keep
appeal events in the starter format with `event: "appeal"`, reasoning, and
`under_review`. Keep Unit 8 response fields and scripts intact. No authentication
or completed human-review queue is provided by this local coursework service.

## The false-positive path

A real writer may submit plain, repetitive writing. Both signals can read it as
AI-like and cross the AI boundary. The label must communicate an uncertain
automated estimate, never proof of cheating. The writer uses the returned ID
to appeal with reasoning; the service records `under_review` durably and keeps
the original estimate visible in the history. An appeal requests review; it
does not itself prove authorship. The acceptable error rate, tradeoff, thresholds,
and precise labels require the owner's decision before implementation.

## Work and validation sequence

1. Commit this design before implementation.
2. Obtain the owner's five original criteria and reasons. Review testability,
   preserve approved wording, and commit `criteria.md` separately before building
   or running evaluation. Do not manufacture a criteria-before-results history.
3. Record the approved numerical rule, thresholds, and labels before coding them.
4. Build the route incrementally, isolate each signal, then integrate scoring,
   logging, and appeals. Keep meaningful local milestones.
5. Use deterministic detector mocks for application tests and a temporary log
   so automated tests cannot pollute committed evidence. Separately exercise
   the downloaded model and repeated requests to verify model reuse.
6. Calibrate only after the criteria commit, with established-origin human,
   AI, conventional human, and edited-AI examples; report both signals and
   disagreement honestly. Generated prose cannot be called verified human.
7. Capture actual HTTP submission, appeal, and log output for the README and
   commit `logs/audit.jsonl`. Keep the Unit 8 templates and scripts untouched.

Pending owner input: five criteria and reasons, acceptable false-positive rate,
error-cost priority, weights/disagreement policy, thresholds, and exact labels.
Human calibration excerpts and the owner's actual review of AI contributions
will also be needed; do not invent either.
