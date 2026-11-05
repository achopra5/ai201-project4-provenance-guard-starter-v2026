# Provenance Guard

A local Flask backend that estimates AI-like writing patterns, explains uncertainty,
and lets a writer request review. It does not establish authorship or make
publishing/removal decisions. Unit 7 is implemented. Current Unit 8 progress is recorded below.

Run with the existing environment:

```bash
.venv/bin/python test.py
HF_HUB_OFFLINE=1 AI201_DEBUG=0 .venv/bin/python app.py
```

The default address is `http://127.0.0.1:5000`. To use the sample-run port,
add `PORT=5057` before the Python command. `HF_HUB_OFFLINE=1` uses the already
cached GPT-2 weights; if starting on a new machine, follow [RUNNING.md](RUNNING.md)
to install dependencies and download the model first. No hosted API key is needed.

## What This Does

1. `POST /submit` accepts a JSON object containing writing in `text` and its
   `creator_id`. Validate both before inference, rejecting invalid or excessive input.
2. The cached local GPT-2 detector measures next-token predictability.
3. Independent stylometry measures sentence-length spread, word variety, and
   punctuation density without language-model probabilities.
4. `scoring.py::combine_signals` averages their AI-likeness scores equally.
5. `scoring.py::score_to_label` chooses human, unsure, or AI using the approved
   thresholds and returns the full reader-facing label.
6. Assign a unique UUID and write both signals, the combined score, label, and
   `decided` status through `audit.log_decision` before returning a success.
7. A writer can `POST /appeal` with that ID and reasoning. Append an appeal with
   `under_review`; preserve the original estimate. `GET /log` reconstructs the
   history and latest status after a restart. No automatic reclassification occurs.

The expensive error is a real writer receiving an AI label. Both signals can
produce that error. The wide unsure band, cautious labels, and durable appeal
path are the chosen response; they do not guarantee a low false-positive rate.

**Endpoint contracts:**

- `POST /submit`: `{"text": "A piece of writing", "creator_id": "writer-123"}`.
  HTTP 200 returns `content_id`, `guess` (`human`, `ai`, `unsure`), `confidence`,
  `label`, `model_score`, `style_score`, and `status: "decided"`.
- `POST /appeal`: `{"content_id": "existing-id", "reasoning": "Please review."}`.
  HTTP 200 returns the ID, `status: "under_review"`, and a confirmation message.
  Repeated appeals append new events. The original creator ID comes from the
  stored decision; no creator supplied by the appeal caller overrides it.
- `/submit` and `/appeal` require nonblank string fields in a JSON object;
  additional fields are ignored. Limits: 20,000 text characters, 200 creator-ID
  characters, 36 content-ID characters, 4,000 reasoning characters, and 128 KiB
  for the entire request body. The detector requires at least three GPT-2 tokens.
- Invalid/missing fields, malformed JSON, non-object bodies, incorrect media
  type, and unscorably short text return JSON HTTP 400. Excessive input returns
  413, an unknown submission ID returns 404, and unavailable inference/scoring
  or decision/appeal storage returns 503. Errors contain `error` and `message`.
  Rejected requests create no completed decision; Unit 8 rejection telemetry is
  still future work.
- `POST /ping` is the untouched starter control. `GET /health` reports model
  state, log count, and rate-limiting state. `GET /log?limit=2` returns the newest
  two events in chronological order. The last event for an ID gives its status.

## Signals and Scoring

### Signal one — the model signal

**What it measures:** GPT-2 mean next-token negative log likelihood, converted
to perplexity on at most the first 400 GPT-2 tokens. `detector.model_signal`
returns `1 / (1 + (perplexity / 45) ** 1.6)`, rounded to four decimals.
Lower perplexity gives a higher AI-likeness score. The model is cached and
loaded under a lock so simultaneous first requests do not duplicate the load.

**Why it might correlate:** Generated continuations can use predictable language.
This measures predictability, not semantic understanding or verified provenance.

**What it cannot see:** Familiar human phrasing, plain prose, and formulaic
language can look predictable too. Novel words or edits can make AI output look
human. Material beyond 400 tokens is truncated for this signal. Domain, language,
and length affect results. Submitted instructions are scored as text, never
executed; this detector produces probabilities of tokens rather than responses
following a submitted prompt.

### Signal two — the style signal

**What it measures:** `stylometry.py` computes three surface measures:

- `sentence_length_spread`: population standard deviation of sentence word
  counts divided by their mean. Fewer than two nonempty sentences returns zero.
- `type_token_ratio`: distinct case-folded Unicode word tokens / total word
  tokens. Internal apostrophes are kept. No words returns zero.
- `punctuation_density`: Unicode punctuation characters / all characters,
  including spaces. Empty text returns zero.

The AI-oriented components are `1 - min(spread, 1)`, `1 - type_token_ratio`,
and `1 - min(punctuation_density / 0.10, 1)`. `style_signal` averages those
three equally. Fewer than 20 words or two nonempty sentences returns neutral
`0.5` because regularity cannot be estimated well. Raw measures remain available.
This fallback limits the combined score to 0.25–0.75, so these inputs receive
unsure if the detector can score them. This is explicit uncertainty handling,
not evidence about their author.

**Why it might correlate:** Even sentence lengths, repeated vocabulary, and
sparse punctuation can resemble formulaic generated prose. The normalization
scales are fixed heuristics, chosen before calibration; they were not learned
from an authorship dataset.

**What it cannot see:** Meaning, intent, author identity, or writing history.
TTR depends on length; abbreviations, poetry, unusual punctuation, language,
quotations, and typos can distort all three measures. Splitting on punctuation
followed by whitespace is only an approximation of sentences. Low punctuation
is not evidence of cheating. The full accepted text is used here, whereas the
model sees only its prefix. Different methods can still have correlated errors.

### The combining rule

**The rule and numbers:** `confidence = 0.5 * model_score + 0.5 * style_score`.
Inputs must be finite and between 0 and 1; weights must be nonnegative and sum
to one. Both signals point toward AI as the value increases. No extra
penalty is applied when they disagree: 0.9 and 0.1 average to 0.5 (unsure).

**Where it lives:** `scoring.py::combine_signals`, with weights and thresholds
in `config.py`. The owner approved the policy in [docs/policy.md](docs/policy.md)
before implementation. Equal weights do not claim equal scientific validity.

**Score meaning:** The API's required `confidence` field is a combined
AI-likeness index, not a probability of AI use and not confidence in whichever
`guess` was returned. Low scores favor human-like patterns. The chosen wide
unsure band favors avoiding false accusations and accepts more missed AI text.
No automatic penalty, removal, or publishing restriction is applied.

### Four fixed calibration inputs

Run `HF_HUB_OFFLINE=1 .venv/bin/python scripts/calibrate.py`.
Actual outputs and complete input text are in [results/calibration.json](results/calibration.json).
These are diagnostics, not a representative accuracy test:

- `ai`: model `0.757000`, style `0.793099`, combined `0.775050` → `unsure`.
- `human`: model `0.353200`, style `0.403171`, combined `0.378185` → `unsure`.
- `formal_human`: model `0.981000`, style `0.588419`, combined `0.784710` → `unsure`.
- `edited_ai`: model `0.568000`, style `0.625352`, combined `0.596676` → `unsure`.

Human sources are Melville's *Moby-Dick*, Chapter 1 opening, in the
[Project Gutenberg primary text](https://www.gutenberg.org/cache/epub/2701/pg2701-images.html#link2HCH0001),
and conventional legal prose from the Preamble and Article I Section 1 in the
[National Archives Constitution transcription](https://www.archives.gov/founding-docs/constitution-transcript).
Historical authorship establishes human origin; these excerpts are not the
owner's writing or a representative sample of modern submissions. The AI
example was generated by Codex in this session. Codex lightly edited that
example for the fourth case; it was not edited by a verified human writer.
Origins and exact edits are recorded with the samples.

**A case where my signals split:** The Constitution excerpt scores `0.981000`
on the model and `0.588419` on style: the model alone would fall in the AI band,
while style alone falls in unsure. Their average, `0.784710`, remains unsure.
This illustrates predictability without AI authorship. All four diagnostics
receive unsure under the chosen wide band; we did not retune to force separation.

The separate real-model functional check reached human `0.160488`, unsure
`0.516374`, and AI `0.963641`; see [results/integration.json](results/integration.json).
All three demonstration texts were generated by Codex. The irregular text's
human label is a known false negative, not evidence of detector accuracy.
The examples demonstrate reachable labels and show a blind spot.

## Label Variants

The exact approved labels in `scoring.py::score_to_label` are:

- **human** (0 ≤ score ≤ 0.20): “This writing appears likely to be human-written. This is an automated estimate, not proof of authorship. The writer can request a review.”

- **unsure** (0.20 < score < 0.85): “We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.”

- **ai** (0.85 ≤ score ≤ 1): “This writing shows patterns associated with AI-generated text. This is an automated estimate, not proof of AI use. The writer can request a review.”

Every valid score maps to exactly one label; threshold equality belongs to
human at 0.20 and AI at 0.85. Invalid/non-finite scores are rejected.

**Why I approved the unsure wording:** It admits that the system cannot reliably
determine authorship, explicitly avoids an accusation, and gives the writer a
next step. The owner reviewed and approved all three labels unchanged.

## Sample Run

Captured with real `curl` requests by `scripts/capture_sample.py`, against
`HF_HUB_OFFLINE=1 AI201_DEBUG=0 PORT=5057 .venv/bin/python app.py` on October 31,
2026. The demonstration text and appeal reasoning were generated by Codex;
this is not a claim that a real writer contested a decision. The service
returned HTTP 200 for these requests. These IDs and scores are captured output,
not placeholders. [results/sample_run.json](results/sample_run.json) also
contains `/ping` and `/health` before and after model loading.

**A submission**

```bash
$ curl --silent --show-error --fail-with-body --max-time 90 -X POST http://127.0.0.1:5057/submit -H 'Content-Type: application/json' -d '{"text": "A writing platform needs clear rules. Writers should understand how their work will be reviewed and how to ask for help when the automated system makes a mistake.", "creator_id": "sample-writer"}'
```

```json
{
  "confidence": 0.5163738683127572,
  "content_id": "bf425427-67ea-40b0-bbd3-c62d7501fde4",
  "guess": "unsure",
  "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
  "model_score": 0.5739,
  "status": "decided",
  "style_score": 0.45884773662551437
}
```

**An appeal**

```bash
$ curl --silent --show-error --fail-with-body --max-time 90 -X POST http://127.0.0.1:5057/appeal -H 'Content-Type: application/json' -d '{"content_id": "bf425427-67ea-40b0-bbd3-c62d7501fde4", "reasoning": "Please review this demonstration submission and its automated estimate."}'
```

```json
{
  "content_id": "bf425427-67ea-40b0-bbd3-c62d7501fde4",
  "message": "Your review request was recorded. The writing is now under review.",
  "status": "under_review"
}
```

**What the log shows afterwards**

```bash
$ curl --silent --show-error --fail-with-body --max-time 90 -X GET 'http://127.0.0.1:5057/log?limit=2'
```

```json
{
  "count": 2,
  "entries": [
    {
      "combined_score": 0.5163738683127572,
      "content_id": "bf425427-67ea-40b0-bbd3-c62d7501fde4",
      "creator_id": "sample-writer",
      "guess": "unsure",
      "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
      "model_score": 0.5739,
      "status": "decided",
      "style_score": 0.45884773662551437,
      "timestamp": "2026-10-31T15:27:34+00:00"
    },
    {
      "content_id": "bf425427-67ea-40b0-bbd3-c62d7501fde4",
      "creator_id": "sample-writer",
      "event": "appeal",
      "reasoning": "Please review this demonstration submission and its automated estimate.",
      "status": "under_review",
      "timestamp": "2026-10-31T15:27:34+00:00"
    }
  ]
}
```

The log preserves `decided` followed by `under_review` for the same ID,
with the appeal's reasoning. The committed [logs/audit.jsonl](logs/audit.jsonl)
is the actual append-only evidence. Timestamps are stored in UTC.
To repeat a capture, start the service and run
`.venv/bin/python scripts/capture_sample.py http://127.0.0.1:5057`.
That appends new real events and generates new IDs.

## How I Used AI

These are the owner's two reported decision-making moments. The owner has not
personally reviewed the finished implementation or sample run; code and testing
were performed by Codex. No code authorship or validation by the owner is claimed.

**Moment 1 — Choosing the scoring policy**

- *What I asked for:* Help deciding how to combine the model and stylometry
  signals, set classification thresholds, and handle uncertainty.
- *What came back:* Equal weights and two possible threshold policies. The
  recommended option used a wide unsure band to reduce false accusations.
- *What I decided:* Equal weights (0.5/0.5), human ≤0.20, AI ≥0.85, and unsure
  between them, without an automatic disagreement penalty. I chose this over
  the narrower option because false accusations are more harmful than missed
  AI content. I recognized that the scores are uncalibrated estimates, not
  probabilities. This was a policy choice, not a code change I made.

**Moment 2 — Reviewing the user-facing labels**

- *What I asked for:* Proposed reader-facing human, unsure, and AI labels that
  communicate uncertainty responsibly.
- *What came back:* Three labels describing the automated assessment,
  acknowledging its limitations, and offering writers a review request.
- *What I decided:* I reviewed and approved all three without changing their
  wording. I agreed with the emphasis on uncertainty, avoiding accusations,
  and giving writers an appeal option.

### Unit 7 verification and limits

- Environment: `.venv/bin/python test.py` — 9 passed, 0 failed.
- Fast application/signal suite: `.venv/bin/python -m unittest discover -s tests -v`
  — 30 tests passed, with detector mocks and temporary audit files.
- Actual cached model: `HF_HUB_OFFLINE=1 .venv/bin/python scripts/check_integration.py`
  — 4 integration checks passed, including all three labels, model/tokenizer
  loaded once, a durable appeal, and rejection of a one-token input.
- Calibration: `HF_HUB_OFFLINE=1 .venv/bin/python scripts/calibrate.py` — four
  attributed diagnostics recorded, with no acceptance-accuracy verdict.
- Actual HTTP: `.venv/bin/python scripts/capture_sample.py` — submission,
  appeal, log status transition, ping, and model loading captured through curl.

The owner's five original criteria are in [criteria.md](criteria.md), committed
as `26e6ce2` before implementation and new calibration/test results. Numerical
label coverage, five appeal lifecycles, and the six invalid-input cases are
covered by deterministic tests. The false-positive and mean-separation targets
need the fixed 20-human and 10-AI acceptance sets and three Unit 8 trials;
they have **not been evaluated**, and the four diagnostics cannot establish them.
The earlier supplied transcript already contained the starter detector's default
demo score; no claim is made that it was unseen.

Known limits: neither signal establishes authorship; the index is uncalibrated;
style can be changed cheaply; historical text may be memorized; short input
falls back to neutral style. This is a local coursework service with no
caller authentication, review staff/queue, completed review adjudication, or
multi-process audit-file locking. Appeals are recorded requests for review.
Do not treat an automated label as a finding of misconduct. Unit 8 rate limits,
full rejection instrumentation, attacks, and repeated criterion evaluation are
intentionally deferred. See [docs/verification.md](docs/verification.md) for the
validation record and submission steps.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

**Unit 8 status — corrected evaluation, November 4, 2026:** The active human
corpus now uses only the three documents the owner personally confirmed writing
without generative AI. Twenty source-position-selected excerpts were frozen before
corrected scoring; text stays local and only hashes/offsets/results are committed.
Criteria 1–2 were rerun three times on each exact historical code version.
Criteria 3–5 retain explicitly identified, unchanged historical trial evidence.
The original 56-attack before/after runs and single improvement are unchanged.
Four criteria remain MET; separation remains MISSED. Historical mixed-author
results are retained below as historical evidence, not the active cohort.

## Rate Limiting

**My limits:** 8 per minute and 100 per day on `POST /submit`, enabled by default
in `config.py`. The owner approved these on November 4. The two windows contain
short bursts and sustained use; eight requests allow normal submission/revision
bursts, while 100/day caps repeated model inference by one stated identity.
These are product choices rather than measured usage-derived limits.

**What a caller counts as:** A nonblank string `creator_id` within the existing
200-character bound, otherwise source IP. The `creator:` and `ip:` key namespaces
are distinct. IDs are unauthenticated: rotating them evades a per-ID cap, while
an IP-only policy would share one allowance across households or classmates.
This does not stop coordinated/global abuse. No trust is placed in a forwarded
IP header. The in-memory backend is suitable for this one-process experiment;
a service restart resets counters but retains the audit file.

`/health` reports the enabled flag and exact policy. A 429 returns JSON with a
helpful slow-down message and the triggered limit; it is logged with a request
ID, route, HTTP status, caller metadata, and no invented decision or scores.
Route-level 400/404/413/503 errors are recorded too. Successful decisions retain
all nine required fields and gain correlation metadata. Writing text is not
copied into decision/rejection logs. Appeals retain their required reasoning.

**Actual flood sequence**, generated by
`.venv/bin/python run_attacks.py --flood 15 --url http://127.0.0.1:5058 --creator unit8-flood-baseline`:

```text
200 200 200 200 200 200 200 200 429 429 429 429 429 429 429
```

Eight completed decisions, then seven rejected requests. The report is
[the flood evidence](results/flood_2026-11-04_192145_752179.md).

## Attack Run — Before

The source was the owner's staff folder `/Users/adi/Downloads/attack_set`, copied
to `data/unit8/staff_attack_set`. Only CSV headers were displayed before the
complete execution. The local service was restarted after the separate flood
test to establish fresh in-memory counters; the audit log was retained.
The detector remains exactly the Unit 7 baseline: equal weights, human ≤0.20,
AI ≥0.85, unchanged signals and labels.

```bash
HF_HUB_OFFLINE=1 AI201_DEBUG=0 PORT=5058 .venv/bin/python app.py
.venv/bin/python run_attacks.py --set data/unit8/staff_attack_set --label before --url http://127.0.0.1:5058
.venv/bin/python scripts/review_attack_run.py --label before
```

All **56 cases** executed: 10 evasion, 8 false positive, 6 prompt injection,
20 malformed, and 12 shared-creator flood. The flood rows' target description
says 20 submissions, but the actual staff file contains 12; no extra official
cases were invented. [Raw before responses](results/unit8/attacks_before.json)
include source/runtime hashes and request IDs. The
[reviewed results](results/unit8/attacks_before_reviewed.json) retain every
response and corresponding real audit event. Full diagnoses are in
[the baseline analysis](docs/unit8/baseline-analysis.md).

**Judgment rules:** Evasion is BROKE when known staff AI avoids the AI label,
including unsure; that is a detection miss, not a confident-human classification.
False-positive protection holds when staff-designated human text is not called
AI. Injection checks the requested output/audit override. Malformed cases are
judged against the actual API contract and safe uncertain handling, not an
invented ban on punctuation, emoji, or non-Latin writing. In a flood, the first
eight allowed requests are expected 200s, and later ones must be 429.

**Results:** 47 HELD and 9 BROKE. Evasion: 1 held/9 broke; false positive: 8/0;
injection: 6/0; malformed: 20/0; flood: 12/0 expected-policy responses. There were
37 HTTP 200, 14 HTTP 400, one HTTP 413, four HTTP 429, and zero 5xx/crashes.
These policy-specific judgments are not a universal security or accuracy score.

| ID | Family | Objective | HTTP | Model | Style | Combined | Guess | Verdict |
|---|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | 0.163500 | 0.604390 | 0.383945 | unsure | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | 0.594300 | 0.373285 | 0.483793 | unsure | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | 0.666200 | 0.493190 | 0.579695 | unsure | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | 0.611400 | 0.594805 | 0.603103 | unsure | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | 0.321200 | 0.434063 | 0.377631 | unsure | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | 0.572700 | 0.375000 | 0.473850 | unsure | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | 0.586200 | 0.500000 | 0.543100 | unsure | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | 0.245200 | 0.500000 | 0.372600 | unsure | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | 0.704200 | 0.492110 | 0.598155 | unsure | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | 0.979200 | 0.761069 | 0.870135 | ai | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | 0.617500 | 0.557367 | 0.587434 | unsure | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | 0.738700 | 0.633080 | 0.685890 | unsure | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | 0.805100 | 0.601933 | 0.703517 | unsure | HELD |
| FP04 | false_positive | a student essay written to a rubric | 200 | 0.832900 | 0.548340 | 0.690620 | unsure | HELD |
| FP05 | false_positive | technical documentation written by a person | 200 | 0.800500 | 0.642977 | 0.721738 | unsure | HELD |
| FP06 | false_positive | a person imitating a formal template | 200 | 0.881400 | 0.531132 | 0.706266 | unsure | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | 0.881600 | 0.532341 | 0.706970 | unsure | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | 0.322300 | 0.500000 | 0.411150 | unsure | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | 0.462500 | 0.435166 | 0.448833 | unsure | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | 0.204400 | 0.400319 | 0.302359 | unsure | HELD |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | 0.594300 | 0.536046 | 0.565173 | unsure | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | 0.499800 | 0.464566 | 0.482183 | unsure | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | 0.640100 | 0.253678 | 0.446889 | unsure | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | 0.558300 | 0.562193 | 0.560247 | unsure | HELD |
| MF01 | malformed | text is only whitespace | 400 | — | — | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | — | — | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | 0.000000 | 0.500000 | 0.250000 | unsure | HELD |
| MF04 | malformed | text is only punctuation | 200 | 0.011200 | 0.500000 | 0.255600 | unsure | HELD |
| MF05 | malformed | text is a very long single word | 200 | 0.997600 | 0.500000 | 0.748800 | unsure | HELD |
| MF06 | malformed | text is emoji only | 200 | 0.996900 | 0.500000 | 0.748450 | unsure | HELD |
| MF07 | malformed | text is right-to-left script | 200 | 0.906400 | 0.500000 | 0.703200 | unsure | HELD |
| MF08 | malformed | text is 60,000 characters | 413 | — | — | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | — | — | — | — | HELD |
| RQ02 | malformed | no creator_id | 400 | — | — | — | — | HELD |
| RQ03 | malformed | text is a number | 400 | — | — | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | — | — | — | — | HELD |
| RQ05 | malformed | text is null | 400 | — | — | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | — | — | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | — | — | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | — | — | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | — | — | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | — | — | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD |

**Ten real audit entries from this attack run**, in this order: EV01, EV02,
EV07, EV10, FP05, PI02, PI05, MF03, RQ08, FL01_09. The last two show a 400 and a
429 rejection. Each entry's `request_id` matches the captured HTTP response.
All 56 cases—not only these ten—have exactly one correlated audit event.

```json
[
  {
    "timestamp": "2026-11-05T01:22:23+00:00",
    "content_id": "4ac2f781-0a95-4956-a176-1835ef8e6349",
    "creator_id": "attacker_EV01",
    "guess": "unsure",
    "model_score": 0.1635,
    "style_score": 0.6043903322235802,
    "combined_score": 0.3839451661117901,
    "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
    "status": "decided",
    "http_status": 200,
    "request_id": "47ef2a14-6853-4454-b691-43305bbd3268",
    "path": "/submit",
    "method": "POST"
  },
  {
    "timestamp": "2026-11-05T01:22:24+00:00",
    "content_id": "8502761f-0783-4853-9121-d53b233b378d",
    "creator_id": "attacker_EV02",
    "guess": "unsure",
    "model_score": 0.5943,
    "style_score": 0.3732852481356848,
    "combined_score": 0.4837926240678424,
    "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
    "status": "decided",
    "http_status": 200,
    "request_id": "6e7b33d5-b264-499b-b741-87d726f86476",
    "path": "/submit",
    "method": "POST"
  },
  {
    "timestamp": "2026-11-05T01:22:24+00:00",
    "content_id": "40461566-edfb-4781-8940-c4495d59a46b",
    "creator_id": "attacker_EV07",
    "guess": "unsure",
    "model_score": 0.5862,
    "style_score": 0.5,
    "combined_score": 0.5431,
    "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
    "status": "decided",
    "http_status": 200,
    "request_id": "eca25ff7-6110-45f4-8c3a-58cc5ad1dfe2",
    "path": "/submit",
    "method": "POST"
  },
  {
    "timestamp": "2026-11-05T01:22:24+00:00",
    "content_id": "e275f4cb-5324-4b02-9c7f-d73f1681816f",
    "creator_id": "attacker_EV10",
    "guess": "ai",
    "model_score": 0.9792,
    "style_score": 0.7610694872669427,
    "combined_score": 0.8701347436334713,
    "label": "This writing shows patterns associated with AI-generated text. This is an automated estimate, not proof of AI use. The writer can request a review.",
    "status": "decided",
    "http_status": 200,
    "request_id": "0ea5d8b8-8c26-4997-a93d-f527a7585e39",
    "path": "/submit",
    "method": "POST"
  },
  {
    "timestamp": "2026-11-05T01:22:24+00:00",
    "content_id": "d5afbf7e-f086-46a7-ad09-89113d4c7f3f",
    "creator_id": "attacker_FP05",
    "guess": "unsure",
    "model_score": 0.8005,
    "style_score": 0.6429767009710886,
    "combined_score": 0.7217383504855444,
    "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
    "status": "decided",
    "http_status": 200,
    "request_id": "d5e9ba0b-d67a-40c0-b9b5-f99fdbfb29d9",
    "path": "/submit",
    "method": "POST"
  },
  {
    "timestamp": "2026-11-05T01:22:24+00:00",
    "content_id": "48e8ecd9-8ff1-41f7-8615-00bd8303c8b2",
    "creator_id": "attacker_PI02",
    "guess": "unsure",
    "model_score": 0.2044,
    "style_score": 0.4003186673955981,
    "combined_score": 0.30235933369779905,
    "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
    "status": "decided",
    "http_status": 200,
    "request_id": "69719bd2-9c42-488f-9d91-f1b4c4ae9e89",
    "path": "/submit",
    "method": "POST"
  },
  {
    "timestamp": "2026-11-05T01:22:24+00:00",
    "content_id": "e1611a07-645b-4240-8964-c3dd3c857489",
    "creator_id": "attacker_PI05",
    "guess": "unsure",
    "model_score": 0.6401,
    "style_score": 0.25367762128325516,
    "combined_score": 0.44688881064162755,
    "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
    "status": "decided",
    "http_status": 200,
    "request_id": "e0b8a157-acd8-4a4c-a62e-85bc2acdc426",
    "path": "/submit",
    "method": "POST"
  },
  {
    "timestamp": "2026-11-05T01:22:24+00:00",
    "content_id": "25598b16-4468-4901-bb47-a210420184fb",
    "creator_id": "attacker_MF03",
    "guess": "unsure",
    "model_score": 0.0,
    "style_score": 0.5,
    "combined_score": 0.25,
    "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
    "status": "decided",
    "http_status": 200,
    "request_id": "7774e632-c928-450e-99a3-1b83994f48d8",
    "path": "/submit",
    "method": "POST"
  },
  {
    "timestamp": "2026-11-05T01:22:25+00:00",
    "creator_id": "unknown",
    "event": "rejected",
    "status": "rejected",
    "reason": "invalid_json",
    "request_id": "cf99ce63-9d88-4e5c-952f-ba58ed05dde9",
    "path": "/submit",
    "method": "POST",
    "http_status": 400,
    "source_ip": "127.0.0.1"
  },
  {
    "timestamp": "2026-11-05T01:22:25+00:00",
    "creator_id": "attacker_flood",
    "event": "rejected",
    "status": "rejected",
    "reason": "rate_limited",
    "request_id": "5fd6e344-e2d6-451f-99cf-f4bd476a0e00",
    "path": "/submit",
    "method": "POST",
    "http_status": 429,
    "source_ip": "127.0.0.1",
    "limit": "8 per 1 minute"
  }
]
```

**The single worst outcome for a legitimate writer:** FP05, staff-designated
human technical documentation, has the largest combined reading among the human
cases: model 0.800500, style 0.642977, combined 0.721738. It remains unsure, so
there is no observed false AI accusation or penalty. Still, a writer following
normal documentation conventions gets a fairly high AI-likeness index and may
feel pressure to request review. The uncertainty label and appeal are useful;
they do not amount to verification of the writer.

## Run Log and Verdicts

### Current owner-confirmed correction

The owner confirmed personally writing `THE TRANSITION.pdf`,
`supplemental essays.pdf`, and `UC.pdf` without generative AI. The active cohort
contains only 20 non-overlapping excerpts from these documents. Application
questions, instructor feedback, quoted text, family details, and uncertain
materials were excluded. These are **20 excerpts from three works**, not 20
independent works. Human origin is supported by the owner's explicit authorship
attestation, not a detector's judgment.

The [selection plan](data/unit8/corrected_selection_plan.json) defines score-free
source intervals and a fixed word-window/source-order procedure. The
[public manifest](data/unit8/corrected_human_manifest.json) records source PDF
hashes, page/document offsets, sample hashes, and the fixed first-ten separation
subset. Text remains in ignored `.private/`; no full personal PDFs or corrected
excerpt prose are committed. Some source material appeared in the historical
run, so this is not claimed to be an unseen holdout. The selection was frozen in
`3a8a441` before any corrected scores were obtained. Extraction collapses
whitespace only; it preserves original words, grammar, punctuation, and Unicode.

The dedicated runner executed the affected criteria against the exact recorded
service versions: `8524fa8` before improvement and `ea0dbd4` after. All six
runtime file hashes match their corresponding original staff-run records. Each
version ran with fresh counters, cached GPT-2, identical 8/minute and 100/day
limits, the same corrected human samples, and the unchanged ten AI samples.
Main's production code was not modified or swapped during these experiments.

```bash
.venv/bin/python scripts/run_corrected_eval.py --label before --port 5059
.venv/bin/python scripts/run_corrected_eval.py --label after --port 5060
.venv/bin/python scripts/compare_corrected_eval.py
```

| Criterion | Original target | Current before trials 1 / 2 / 3 | Current after trials 1 / 2 / 3 | Verdict | Evidence scope |
|---|---|---|---|---|---|
| 1. False positives | At most 1 of 20 human pieces labelled ai | 0/20 AI labels; 20/20 usable / 0/20 AI labels; 20/20 usable / 0/20 AI labels; 20/20 usable | 0/20 AI labels; 20/20 usable / 0/20 AI labels; 20/20 usable / 0/20 AI labels; 20/20 usable | MET | corrected rerun |
| 2. Score separation | AI mean - human mean >= 0.20; 10 samples each | AI mean - human mean = -0.012319 / AI mean - human mean = -0.012319 / AI mean - human mean = -0.012319 | AI mean - human mean = -0.012319 / AI mean - human mean = -0.012319 / AI mean - human mean = -0.012319 | MISSED | corrected rerun |
| 3. Label coverage | 7/7 specified scores correct; all 3 labels | 7/7 correct / 7/7 correct / 7/7 correct | 7/7 correct / 7/7 correct / 7/7 correct | MET | unchanged historical trial evidence; not rerun for corpus correction |
| 4. Appeals | 5/5 distinct appeals recorded with reasoning and under_review | 5/5 appeal lifecycles / 5/5 appeal lifecycles / 5/5 appeal lifecycles | 5/5 appeal lifecycles / 5/5 appeal lifecycles / 5/5 appeal lifecycles | MET | unchanged historical trial evidence; not rerun for corpus correction |
| 5. Invalid inputs | 6/6 specified invalid submissions return 400 without decisions | 6/6 invalid cases rejected with no decisions / 6/6 invalid cases rejected with no decisions / 6/6 invalid cases rejected with no decisions | 6/6 invalid cases rejected with no decisions / 6/6 invalid cases rejected with no decisions / 6/6 invalid cases rejected with no decisions | MET | unchanged historical trial evidence; not rerun for corpus correction |

The two corrected JSON artifacts contain all **12 newly executed trials**,
with 120 actual submission events per version. The six original trial records
for each unaffected criterion 3–5 are carried forward, not relabeled as new runs.
The original targets and criteria wording remain unchanged.

- [Corrected before results](results/unit8/corrected/eval_before.json)
- [Corrected after results](results/unit8/corrected/eval_after.json)
- [Corrected comparison](results/unit8/corrected/comparison.json)
- [Corrected before audit](results/unit8/corrected/audit_before.jsonl) and
  [after audit](results/unit8/corrected/audit_after.jsonl), without source text.

**Actual first-trial fields** from `scripts/run_corrected_eval.py` through the
unchanged `run_eval.py::run_trial` functions (full case responses remain in the
linked artifacts; no private text is embedded):

```json
[
  {
    "phase": "before",
    "criterion": 1,
    "trial": 1,
    "verdict": "MET",
    "passed": true,
    "value": "0/20 AI labels; 20/20 usable",
    "false_positives": 0,
    "usable": 20,
    "denominator": 20
  },
  {
    "phase": "before",
    "criterion": 2,
    "trial": 1,
    "verdict": "MISSED",
    "passed": false,
    "value": "AI mean - human mean = -0.012319",
    "human_mean": 0.5312565371862069,
    "ai_mean": 0.5189370898250648,
    "difference": -0.0123194473611421
  },
  {
    "phase": "after",
    "criterion": 1,
    "trial": 1,
    "verdict": "MET",
    "passed": true,
    "value": "0/20 AI labels; 20/20 usable",
    "false_positives": 0,
    "usable": 20,
    "denominator": 20
  },
  {
    "phase": "after",
    "criterion": 2,
    "trial": 1,
    "verdict": "MISSED",
    "passed": false,
    "value": "AI mean - human mean = -0.012319",
    "human_mean": 0.5312565371862069,
    "ai_mean": 0.5189370898250648,
    "difference": -0.0123194473611421
  }
]
```

**Measured correction:** False positives remain 0/20 in every corrected trial.
The corrected human mean is 0.5312565371862069; the unchanged AI mean is
0.5189370898250648. The gap is **−0.0123194473611421**, versus the historical
mixed-corpus **−0.056844013164074614**: a change of +0.044524565802932514 due to
the dataset correction, not a code improvement. Both historical code versions
give identical corrected values. The original +0.20 target is still MISSED.

**Corrected separation diagnosis:** Human/model mean 0.514830 versus AI/model
0.509640; human/style mean 0.5476830743724138 versus AI/style 0.5282341796501296.
Both components still rank this fixed AI group lower on average. Their equal
mean inherits that ordering. A convex reweighting alone cannot reach +0.20;
threshold changes do not change this numerical criterion. Window length,
genre, shared source works, and PDF extraction limit generalization. The change
from the old mean cannot be attributed to authorship correction alone because
the declared excerpt boundaries and normalization differ too.

The nine attack misses and their diagnoses remain unchanged: see
[the historical baseline analysis](docs/unit8/baseline-analysis.md). This corpus
correction is not a second detection improvement and did not rerun or rewrite
any staff attack outcome.

### Historical mixed-author evaluation (superseded for criteria 1–2)

The owner supplied and approved a **mixed-author** human corpus. It contains
20 distinct excerpts from five PDFs and instructor feedback, with source/page
references and hashes. Human origin is user-attested; it is not independently
verified, and these are not 20 independent works or exclusively the owner's
writing. The owner explicitly approved this departure from the suggestion to
use one's own writing and permission to commit the excerpts. Only extraction
whitespace/ligatures and repeated page furniture were cleaned; no prose was
rewritten. These limitations qualify the results without changing any targets.

The [human manifest](data/unit8/human_samples.json) was committed as `f787792`
before scoring. The first ten excerpts form the fixed human separation subset.
The ten [AI samples](data/unit8/ai_samples.json) were generated before evaluation.
The combined manifests, original criteria, and boundary-answer hash is
`689e45fb7ebd3004835e13f5625998543c105ca2b9ae2de28d59316f0c52447f`.

The service was restarted with fresh in-memory counters and unchanged limits
before this run. Valid submissions use unique stated identities; the limiter
remains enabled. No implementation changed between trials.

```bash
.venv/bin/python run_eval.py --label before --url http://127.0.0.1:5058
```

| Criterion | Original target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. False positives | At most 1 of 20 human pieces labelled ai | 0/20 AI labels; 20/20 usable | 0/20 AI labels; 20/20 usable | 0/20 AI labels; 20/20 usable | MET |
| 2. Score separation | AI mean - human mean >= 0.20; 10 samples each | AI mean - human mean = -0.056844 | AI mean - human mean = -0.056844 | AI mean - human mean = -0.056844 | MISSED |
| 3. Label coverage | 7/7 specified scores correct; all 3 labels | 7/7 correct | 7/7 correct | 7/7 correct | MET |
| 4. Appeals | 5/5 distinct appeals recorded with reasoning and under_review | 5/5 appeal lifecycles | 5/5 appeal lifecycles | 5/5 appeal lifecycles | MET |
| 5. Invalid inputs | 6/6 specified invalid submissions return 400 without decisions | 6/6 invalid cases rejected with no decisions | 6/6 invalid cases rejected with no decisions | 6/6 invalid cases rejected with no decisions | MET |

All 15 trial records are saved in [eval_before.json](results/unit8/eval_before.json),
with complete real responses and evidence. [eval_before.md](results/unit8/eval_before.md)
contains the same five-row table and complete first-trial JSON. Identical
results are expected from these deterministic signals; all three were executed.

**Real machine-readable output for every criterion**, produced by
`run_eval.py::run_trial` through its corresponding `evaluate_*` function.
The following exact summary fields are extracted from actual first-trial
results; full cases, histories, and responses remain in the linked JSON.

```json
[
  {
    "criterion": 1,
    "verdict": "MET",
    "trial": 1,
    "passed": true,
    "value": "0/20 AI labels; 20/20 usable",
    "false_positives": 0,
    "usable": 20,
    "denominator": 20
  },
  {
    "criterion": 2,
    "verdict": "MISSED",
    "trial": 1,
    "passed": false,
    "value": "AI mean - human mean = -0.056844",
    "human_mean": 0.5757811029891394,
    "ai_mean": 0.5189370898250648,
    "difference": -0.056844013164074614
  },
  {
    "criterion": 3,
    "verdict": "MET",
    "trial": 1,
    "passed": true,
    "value": "7/7 correct",
    "execution": "Direct scoring.py::score_to_label calls; no HTTP requests"
  },
  {
    "criterion": 4,
    "verdict": "MET",
    "trial": 1,
    "passed": true,
    "value": "5/5 appeal lifecycles"
  },
  {
    "criterion": 5,
    "verdict": "MET",
    "trial": 1,
    "passed": true,
    "value": "6/6 invalid cases rejected with no decisions"
  }
]
```

**How the verdicts were decided:** Criterion 1 has all 20 usable cases and zero
AI labels in every trial. Criterion 2 falls below +0.20 in all trials, so it is
MISSED. All seven fixed mappings pass each time; all five actual appeals retain
reasoning and history; all six actual invalid requests return 400 with no
decision, supported by their request-ID audit events. MET requires all three
trials; preparation tests were not substituted for these results.

**Historical mixed-corpus diagnosis of criterion 2:** The mean model score is 0.562880 for human and
0.509640 for AI; style means are 0.588682 and 0.528234. Both signals order the
groups opposite the desired direction, and averaging preserves that error.
The actual combined difference is −0.056844. A convex reweighting alone cannot
reach +0.20 because both component differences are negative. This is a
signal/combination limitation, not a route failure or a threshold issue.
Genre differences and repeated source works may contribute; no controlled
ablation establishes their causal contributions. No hard samples were excluded.

**Diagnoses of all nine broken attacks:** EV01's lower component is actually
the model (0.163500 versus style 0.604390). EV02 and EV06 have high sentence
spread that lowers surface regularity. EV07's one sentence and EV08's ten
words trigger the neutral style fallback. EV03, EV04, EV05, and EV09 produce
moderate/human-like readings whose mean remains in the wide unsure interval.
[Every broken ID has a stage and mechanism in the baseline analysis](docs/unit8/baseline-analysis.md).
Edit effects relative to an unedited control remain hypotheses where no paired
experiment was performed.

## The Improvement

**The one change:** `app.py::submit` now rejects C0 control characters other
than tab, newline, and carriage return, plus DEL, before invoking either signal.
The response is HTTP 400 with `unsupported_control_characters` and an instruction
to remove the controls and resubmit. Existing audit instrumentation records the
rejection. The dedicated implementation commit is `ea0dbd4`; baseline criteria
were committed earlier in `8524fa8`. See [the pre-measurement improvement record](docs/unit8/improvement.md).

**Which diagnosis pointed at it:** MF03 mixed NUL/control/terminal escape bytes
with words. The baseline route only validated string type, nonblank content,
and length, so it ran GPT-2 and returned model 0.0, style 0.5, combined 0.25,
unsure. That did not violate the original permissive contract or crash, and it
was correctly marked HELD by our frozen review rules. It nevertheless exposed
a missing pre-inference guard and an unnecessary authorship estimate on this
input. The focused improvement addresses that narrower handling weakness.

**Expected benefit and cost:** Avoid the inference and give an actionable error
for unsupported controls. A caller who intentionally uses those controls must
remove them; tabs, newlines, carriage returns, Unicode, Arabic, emoji, and
punctuation remain subject to the same ordinary contract. The code rejects
rather than silently rewriting text. No signals, weights, thresholds, labels,
rate limits, cohort samples, targets, or review rules were changed. This is one
validation rule, not an attempt to repair detector accuracy by tuning the cohort.

### Attack Run — After

The service was restarted with the same policy and fresh in-memory counters,
retaining the append-only log. Both source-file hashes match the before run.

```bash
HF_HUB_OFFLINE=1 AI201_DEBUG=0 PORT=5058 .venv/bin/python app.py
.venv/bin/python run_attacks.py --set data/unit8/staff_attack_set --label after --url http://127.0.0.1:5058
.venv/bin/python scripts/review_attack_run.py --label after
```

All 56 cases executed again. The [raw after artifact](results/unit8/attacks_after.json)
and [reviewed after artifact](results/unit8/attacks_after_reviewed.json) retain
responses and their actual audit events. The same judgment rules apply.

| ID | Family | Objective | HTTP | Model | Style | Combined | Guess | Verdict |
|---|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | 0.163500 | 0.604390 | 0.383945 | unsure | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | 0.594300 | 0.373285 | 0.483793 | unsure | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | 0.666200 | 0.493190 | 0.579695 | unsure | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | 0.611400 | 0.594805 | 0.603103 | unsure | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | 0.321200 | 0.434063 | 0.377631 | unsure | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | 0.572700 | 0.375000 | 0.473850 | unsure | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | 0.586200 | 0.500000 | 0.543100 | unsure | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | 0.245200 | 0.500000 | 0.372600 | unsure | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | 0.704200 | 0.492110 | 0.598155 | unsure | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | 0.979200 | 0.761069 | 0.870135 | ai | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | 0.617500 | 0.557367 | 0.587434 | unsure | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | 0.738700 | 0.633080 | 0.685890 | unsure | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | 0.805100 | 0.601933 | 0.703517 | unsure | HELD |
| FP04 | false_positive | a student essay written to a rubric | 200 | 0.832900 | 0.548340 | 0.690620 | unsure | HELD |
| FP05 | false_positive | technical documentation written by a person | 200 | 0.800500 | 0.642977 | 0.721738 | unsure | HELD |
| FP06 | false_positive | a person imitating a formal template | 200 | 0.881400 | 0.531132 | 0.706266 | unsure | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | 0.881600 | 0.532341 | 0.706970 | unsure | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | 0.322300 | 0.500000 | 0.411150 | unsure | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | 0.462500 | 0.435166 | 0.448833 | unsure | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | 0.204400 | 0.400319 | 0.302359 | unsure | HELD |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | 0.594300 | 0.536046 | 0.565173 | unsure | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | 0.499800 | 0.464566 | 0.482183 | unsure | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | 0.640100 | 0.253678 | 0.446889 | unsure | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | 0.558300 | 0.562193 | 0.560247 | unsure | HELD |
| MF01 | malformed | text is only whitespace | 400 | — | — | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | — | — | — | — | HELD |
| MF03 | malformed | text is control characters | 400 | — | — | — | — | HELD |
| MF04 | malformed | text is only punctuation | 200 | 0.011200 | 0.500000 | 0.255600 | unsure | HELD |
| MF05 | malformed | text is a very long single word | 200 | 0.997600 | 0.500000 | 0.748800 | unsure | HELD |
| MF06 | malformed | text is emoji only | 200 | 0.996900 | 0.500000 | 0.748450 | unsure | HELD |
| MF07 | malformed | text is right-to-left script | 200 | 0.906400 | 0.500000 | 0.703200 | unsure | HELD |
| MF08 | malformed | text is 60,000 characters | 413 | — | — | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | — | — | — | — | HELD |
| RQ02 | malformed | no creator_id | 400 | — | — | — | — | HELD |
| RQ03 | malformed | text is a number | 400 | — | — | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | — | — | — | — | HELD |
| RQ05 | malformed | text is null | 400 | — | — | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | — | — | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | — | — | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | — | — | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | — | — | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | — | — | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.028700 | 0.500000 | 0.264350 | unsure | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD |

### Historical full five-criterion after run (mixed-author corpus)

This original full run is retained as historical evidence. The corrected
criteria 1–2 above supersede its human-dependent metrics; criteria 3–5 remain
valid unaffected evidence. The original service was restarted with fresh
counters and unchanged policy. Historical cohort/criteria fingerprint:
`689e45fb7ebd3004835e13f5625998543c105ca2b9ae2de28d59316f0c52447f`.

```bash
.venv/bin/python run_eval.py --label after --url http://127.0.0.1:5058
```

| Criterion | Original target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. False positives | At most 1 of 20 human pieces labelled ai | 0/20 AI labels; 20/20 usable | 0/20 AI labels; 20/20 usable | 0/20 AI labels; 20/20 usable | MET |
| 2. Score separation | AI mean - human mean >= 0.20; 10 samples each | AI mean - human mean = -0.056844 | AI mean - human mean = -0.056844 | AI mean - human mean = -0.056844 | MISSED |
| 3. Label coverage | 7/7 specified scores correct; all 3 labels | 7/7 correct | 7/7 correct | 7/7 correct | MET |
| 4. Appeals | 5/5 distinct appeals recorded with reasoning and under_review | 5/5 appeal lifecycles | 5/5 appeal lifecycles | 5/5 appeal lifecycles | MET |
| 5. Invalid inputs | 6/6 specified invalid submissions return 400 without decisions | 6/6 invalid cases rejected with no decisions | 6/6 invalid cases rejected with no decisions | 6/6 invalid cases rejected with no decisions | MET |

[eval_after.json](results/unit8/eval_after.json) stores every raw trial and
[eval_after.md](results/unit8/eval_after.md) stores the table with real first-trial
JSON for every criterion. Exactly 15 trials ran in each phase. The score
separation remains −0.056844; no failed target was lowered or reinterpreted.

### Measured comparison

```bash
.venv/bin/python scripts/compare_unit8.py
```

The [comparison artifact](results/unit8/comparison.json) verifies matching staff
and cohort hashes and compares every case, criterion value, and verdict.

| Attack family | Before HELD / BROKE | After HELD / BROKE |
|---|---|---|
| evasion | 1 / 9 | 1 / 9 |
| false_positive | 8 / 0 | 8 / 0 |
| prompt_injection | 6 / 0 | 6 / 0 |
| malformed | 20 / 0 | 20 / 0 |
| flood_same_creator | 12 / 0 | 12 / 0 |

MF03 is the **only changed attack case**. Before: HTTP 200 with a completed
decision and signal scores. After: HTTP 400, `unsupported_control_characters`,
a rejection event, and no content ID or scores. The route checks before the
model call, and the dedicated test verifies that inference is not invoked.
The other 55 cases retain their statuses, guesses, and numerical scores.

HTTP totals changed from 37 successes/14 validation 400s to 36 successes/15
validation 400s; one 413 and four 429s remain in each phase. Audit correlation
is 56/56 in both. No crashes or 5xx responses occurred.

**Actual MF03 before/after events** (exact records extracted from the reviewed
artifacts, not reconstructed):

```json
{
  "before": [
    {
      "timestamp": "2026-11-05T01:22:24+00:00",
      "content_id": "25598b16-4468-4901-bb47-a210420184fb",
      "creator_id": "attacker_MF03",
      "guess": "unsure",
      "model_score": 0.0,
      "style_score": 0.5,
      "combined_score": 0.25,
      "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
      "status": "decided",
      "http_status": 200,
      "request_id": "7774e632-c928-450e-99a3-1b83994f48d8",
      "path": "/submit",
      "method": "POST"
    }
  ],
  "after": [
    {
      "timestamp": "2026-11-05T01:43:57+00:00",
      "creator_id": "attacker_MF03",
      "event": "rejected",
      "status": "rejected",
      "reason": "unsupported_control_characters",
      "request_id": "0288e929-5a6b-4f2e-b916-22b15993c970",
      "path": "/submit",
      "method": "POST",
      "http_status": 400,
      "source_ip": "127.0.0.1"
    }
  ]
}
```

**Did it help?** It improved control-character handling and avoided one
completed inference/decision on the official set. It did **not** improve the
47 HELD/9 BROKE outcome, false positives, separation, or any criterion verdict.
No ordinary corpus response changed and no measured detection regression
occurred. Timing/cost savings were not benchmarked; cold/warm request timings
are not a controlled performance comparison. The scope cost is that intentional
unsupported control characters now require caller cleanup.

## What's Still Broken

All remaining broken attacks are **EV01–EV09**, still unsure after the change.
Their individual scores, stages, and confirmed-versus-hypothesized mechanisms
are preserved in [the baseline analysis](docs/unit8/baseline-analysis.md):

- **EV01, EV04, EV05:** wording/spelling and conversational rewriting can
  produce human-like or moderate model scores. Next investigate matched edits
  and genuine source/provenance evidence; do not assume a low perplexity-based
  index establishes authorship. These were left because the one change was
  deliberately limited to the verified handling gap.
- **EV02, EV03, EV06, EV09:** sentence structure, quotations, and mixed prose
  affect the stylometry proxies and their average. Next use paired ablations
  with both signals recorded to isolate each transformation. Replacing several
  heuristics at once would destroy attribution of the single measured change.
- **EV07 and EV08:** one detected sentence or ten word tokens trigger neutral
  style. More writing or process evidence could make uncertainty more useful;
  assigning confident AI labels from so little evidence would change the
  owner's safety tradeoff. The conservative fallback remains intentional.

**Criterion 2 remains MISSED in all six corrected before/after trials.** Human
mean 0.531257 exceeds AI mean 0.518937. Both signal mean differences are negative,
so convex reweighting cannot reach +0.20. Next collect an independently verified,
more diverse evaluation corpus with document/author-level separation, report
uncertainty, and investigate better provenance evidence. The current frozen
cohort must remain in the record; replacing difficult samples or lowering the
target would not fix this miss. The 20 correlated excerpts from three owner-confirmed source documents and
small sample size limit generalization. Earlier mixed-author results remain historical.

The remaining three text-only edge types (punctuation, a long single word,
emoji) and Arabic still produce safe unsure responses rather than categorical
language bans. Unauthenticated creator IDs can rotate around quotas, and there
is no global inference budget, staffed review queue, or multi-worker audit
database. Those are code/design limitations beyond what the staff set proves.
They were left because each would be another independent substantive change.
This local coursework service is not production-ready.

**The production tradeoff:** I favor fewer false accusations against human
writers and accept more AI text receiving unsure, with missed detection and
review costs borne by the platform. Writers need a practical, staffed appeal
path; this service records review requests and status but does not adjudicate
them or justify punishment from an automated estimate.

**Unit 8 AI-use record:** Codex proposed and implemented the limiter and
instrumentation, built and tested the evaluation harnesses, executed the staff
and criteria runs, and drafted explicit judgments, diagnoses, and comparisons.
The owner approved 8/minute and 100/day with creator-ID/IP fallback, identified
the staff source, supplied the PDF/feedback materials, and explicitly approved
the mixed-author cohort and committing its excerpts. Codex selected source-linked
excerpts before scoring and made the single documented control-character guard
under the authorized engineering scope. No owner code edits, manual tests, or
review of the final results are claimed.

**Corpus-correction decision:** The owner subsequently confirmed personal
non-AI authorship of the three named PDFs, required exclusion of mixed/uncertain
sources, and required private excerpt storage with public metadata/results.
Codex froze the deterministic selection, reran only the affected criteria on
both exact historical code versions, and preserved all earlier evidence. No
new detector/threshold policy was selected and no owner manual testing is claimed.

### Final verification and handoff

The original `criteria.md`, both signals, score combination, thresholds, and
labels remain unchanged. All earlier audit entries are retained. The corrected source/privacy validation, final checks,
and local commit sequence are in [the Unit 8 report](docs/unit8/final-report.md).
The correction passed 9 environment checks and 54 tests; source re-extraction
matched all frozen hashes and boundaries. [Correction verification](results/unit8/corrected/verification.json)
also checks preservation and excludes private text from introduced public files.
No GitHub push or Course Portal submission has been performed.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [x] Rate limiting on /submit, with your numbers justified
       [x] The pasted run of status codes showing 429
       [x] Audit log with all nine fields, recording rejections too
       [x] The attack set run IN FULL, every input with an outcome
       [x] Ten audit log entries pasted as text
       [x] Five criteria across three trials
       [x] A diagnosis for every miss and every broken attack — stage AND mechanism
       [x] One improvement, with Attack Run — After
       [x] What's Still Broken, including the production trade
       [x] At least four new commits
       [x] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
