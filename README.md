# Provenance Guard

A local Flask backend that estimates AI-like writing patterns, explains uncertainty,
and lets a writer request review. It does not establish authorship or make
publishing/removal decisions. Unit 7 is implemented; Unit 8 remains a template.

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

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



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

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
