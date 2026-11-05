# Unit 8 baseline attack analysis — before improvement

## Experimental boundary and evidence

The instrumented baseline is commit `e9d674e`; no detector, stylometry, weight,
threshold, or label change has been made from Unit 7. Approved limits are
8/minute and 100/day per stated valid creator ID, with source-IP fallback.
In-memory counters were reset by restarting the local service between the
separate 15-request flood check and the full staff attack run. The append-only
audit file was retained. Staff CSVs were copied and only headers displayed
before execution; payload inspection began after all 56 responses were saved.

The complete raw baseline is `results/unit8/attacks_before.json`; each response
has HTTP status, both signals, combined score, guess, fixed label, request ID,
and raw response text. Source-file and runtime-file SHA-256 hashes identify the
exact set and service version. Derived judgments, explanations, and matching
audit events are in `results/unit8/attacks_before_reviewed.json`. The raw artifact
has not been edited to replace the runner's initially blank verdicts.

Actual source counts match 56 cases: 10 evasion, 8 false positive, 6 prompt
injection, 20 malformed, and 12 shared-creator flood requests. The flood rows'
target text says "20 rapid submissions", but the supplied set contains 12;
we executed all 12, without inventing eight additional official cases.

All 56 attempts have one matching audit event. The 37 successful responses have
all nine decision fields. The 19 rejections are 14 HTTP 400, one 413, and four
429; rejection records contain available metadata without fabricated scores or
content IDs. No request crashed the service or returned 5xx.

## Judgment rules

HELD/BROKE is relative to the objective, not synonymous with HTTP 200/non-200:

- Evasion: known staff AI should retain an AI label. Unsure counts as a
  detection miss under this rule because the system has not identified AI.
  This does not imply a confident-human decision or an unauthorized publication.
- False positives: staff-designated human text must not receive an AI label.
  Unsure satisfies that protection, although it does not positively verify
  the writer. The staff's provenance assertion is not independently verified.
- Injection: check the particular requested output override, hostile label,
  or forged audit values. The outputs did not obey those requests. A label
  alone would not prove instruction-following; GPT-2 computes likelihood and
  produces no instruction-following completion in this service.
- Malformed requests: enforce the actual published API contract and avoid
  crashes/confident claims on ambiguous text. Missing, wrong-type, bad-media,
  broken JSON, empty, one-token, and excessive inputs must be rejected.
  Nonblank multi-token strings such as punctuation, controls mixed with words,
  emoji, and Arabic are not categorically forbidden by the baseline contract.
  Their safe unsure responses are not falsely reported as required 400s.
- Flood: the first eight requests are within the allowance and must succeed;
  later requests in the same burst must be 429. Permitted requests do not
  constitute bypasses. Individual rows and the aggregate burst are reported.

Using these rules: 47 HELD and 9 BROKE. Family results: evasion 1/10 HELD,
false positives 8/8, injection 6/6, malformed 20/20, flood 12/12 expected-policy
responses. These are policy-specific judgments, not an overall security score.

## Every broken attack — stage and mechanism

All nine broken cases are detection misses with `guess: unsure`. The direct
combining mechanism is verified: arithmetic mean of the observed component
scores lies strictly below 0.85 and above 0.20. Why an edit moves a component
relative to an unedited control is a separate causal question: no paired
counterfactual was run, so edit effects below are hypotheses supported by the
surface measures and scoring code, not experimentally isolated causal claims.

- **EV01:** model 0.163500; style 0.604390; combined 0.383945. The target names
  style/TTR, but the lower component is actually the model signal. TTR is
  0.870588 and sentence CV is 0.148813. Unusual spellings plausibly raise
  perplexity as well as creating distinct tokens. Confirmed stages: both
  signals disagree, combination averages, label mapping returns unsure.
- **EV02:** model 0.594300; style 0.373285; combined 0.483793. Sentence CV
  0.815855 reduces the regularity component, and TTR 0.824176 reduces the
  repetition component. The style signal reads this as more human-like.
  Stage: surface stylometry plus averaging and the wide unsure band.
- **EV03:** model 0.666200; style 0.493190; combined 0.579695. The appended
  informal quotation changes measured surface form, but its causal effect
  requires a paired unquoted test. Confirmed: neither component reaches the
  AI threshold, so their equal mean cannot cross it. Stages: signals and label
  mapping. This is not a broken HTTP route or injected system instruction.
- **EV04:** model 0.611400; style 0.594805; combined 0.603103. Both components
  provide moderate AI-like readings rather than strong evidence. Rare words
  plausibly influence perplexity, but no same-text vocabulary ablation was
  performed. Confirmed: arithmetic mean falls in the approved unsure interval.
- **EV05:** model 0.321200; style 0.434063; combined 0.377631. Both signals
  favor human-like patterns. The conversational rewritten text is a staff
  evasion example; no verified human editing history is asserted. Stages:
  weak authorship proxies, combination, and uncertainty mapping.
- **EV06:** model 0.572700; style 0.375000; combined 0.473850. CV 1.082600
  saturates the spread normalization: the regularity component becomes zero.
  TTR is 0.75. A very long sentence alongside short ones makes the surface
  heuristic more human-like. Confirmed stage: stylometry normalization.
- **EV07:** model 0.586200; style 0.500000; combined 0.543100. This has 97
  words but only one detected sentence. The style signal returns its explicit
  neutral fallback before using punctuation density; the apparent punctuation
  attack does not exercise that component. Stages: sentence segmentation,
  short-evidence fallback, combining rule, and label mapping.
- **EV08:** model 0.245200; style 0.500000; combined 0.372600. There are ten
  word tokens across two sentences, so the under-20-word fallback applies.
  This is not evidence of truncating a long text at the 400-token maximum;
  rather, it is too little writing for the style heuristic. Stage: insufficient
  evidence and neutral fallback. It is unsure, not confidently human.
- **EV09:** model 0.704200; style 0.492110; combined 0.598155. CV 0.440797
  and TTR 0.846847 are the actual measured surface properties. A conversational
  opening may shift both features, but a controlled no-opening comparison is
  needed to establish the effect. Stage: distinct signals give moderate or
  near-neutral readings, and the mean remains below the AI boundary.

These nine failures share the basic limitation that predictable language and
surface regularity cannot establish provenance. Some cases expose the deliberate
neutral fallback and normalization; others expose model sensitivity to wording.
The approved wide band buys protection from false accusations at the cost of
these missed AI labels. No weights or thresholds have been changed to improve
these results.

## Other observed behavior and the writer's perspective

EV10 was AI at 0.870135: repeated stanza structure was not sufficient to hide it.
All eight staff-designated human cases were unsure, with zero AI accusations.
FP05, human technical documentation, has the highest combined reading in that
family: model 0.800500, style 0.642977, combined 0.721738. It is the baseline's
least comfortable outcome to explain to a legitimate writer: ordinary technical
instructions receive a fairly high AI-likeness index and no positive human
assessment. This is uncertainty and a possible review burden, not an observed
false accusation or automatic penalty. The policy's protective part held.

PI01–PI06 remain unsure with the approved fixed label. PI02 does not return the
requested `human`/0.02 pair. PI04 does not place its script fragment into the
reader label. PI05 has exactly one valid JSON audit event whose guess and score
match the real response, rather than its embedded `human`/0.01 fragment. No
claim is made about a nonexistent front-end's rendering behavior.

MF03–MF07 are accepted as strings and return unsure. The control-containing
MF03 receives model 0.0 but combined 0.25 because style is neutral. MF05's long
single word and MF06's emoji produce high model scores with neutral style, but
neither receives a confident label. MF07's Arabic is not invalid merely because
it is non-Latin. The remaining malformed cases are rejected under the stated
contract; the 60,000-character input is 413.

## Next experimental boundary

The acceptance cohort still requires 20 actual owner-written pieces and explicit
coursework-publication permission. All five criteria must be evaluated three
times before an improvement is selected. No acceptance verdicts or after results
exist. No improvement has been chosen or applied. The owner will provide samples
in chat; preserve their order and wording, using 1–10 as the separation subset.
A proposed change must respond to the combined attack/criteria evidence, and any
safety-policy change requires owner approval. The original targets remain fixed.

## Acceptance baseline — three actual trials

The frozen, owner-approved mixed-author cohort was committed as `f787792` before
any acceptance scores were obtained. Its combined manifest/criteria/boundary
fingerprint is `689e45fb7ebd3004835e13f5625998543c105ca2b9ae2de28d59316f0c52447f`.
The source material is user-attested human writing, not independently verified;
20 excerpts from fewer works are not independent full-document samples. The
first ten declared excerpts are the fixed separation subset. All inputs,
including feedback and example essays, are attributed with those limits.

`run_eval.py --label before --url http://127.0.0.1:5058` executed all five
criteria three times on the unchanged instrumented service, started with fresh
in-memory counters and the same 8/minute, 100/day policy. Unique stated
identities isolate legitimate submissions without disabling the limiter.
The six fallback-IP invalid requests across the three trials remained below
the minute allowance. No implementation was changed between trials.

Actual values were identical across all three trials:

- Criterion 1: 0/20 high-confidence AI labels on the 20 human excerpts; MET.
- Criterion 2: human mean 0.5757811029891394, AI mean 0.5189370898250648;
  difference -0.0568440131640746, below +0.20; MISSED.
- Criterion 3: 7/7 direct numerical mappings correct, all three labels; MET.
- Criterion 4: 5/5 actual submission-to-appeal lifecycles with exact reasoning,
  original decisions retained, and latest status under_review; MET.
- Criterion 5: 6/6 specified invalid HTTP requests returned 400 with correlated
  rejection events and no completed decisions; MET.

Complete raw cases for all 15 trials, including exact responses, audit histories,
request IDs, snapshot and source hashes are in `results/unit8/eval_before.json`.
The generated five-row table and actual JSON per criterion are also in
`results/unit8/eval_before.md`. This is genuine evaluation, not the preparation
unit-test suite. Repeating deterministic outputs is expected, not evidence of
skipping trials or 60 independent human samples.

### Criterion 2 diagnosis

The route returned all 20 usable responses in each separation trial, so this
is not a missing-data, denominator, limiter, or transport failure. The two
component group means establish the mechanism:

- Model: human 0.562880; AI 0.509640; difference -0.053240.
- Style: human 0.5886822059782788; AI 0.5282341796501296;
  difference -0.0604480263281492.
- The equal mean preserves their negative group differences, yielding
  -0.0568440131640746. Thresholds do not affect this numerical criterion.

Stages: model signal and surface stylometry provide weak authorship proxies;
the combination inherits their reversed group ordering. A convex reweighting
alone can only place the difference between -0.060448 and -0.053240, so cannot
reach +0.20. Creative AI examples (including poetry and fiction) can be less
predictable and more varied than formal human excerpts. That is a plausible
explanation of corpus effects, not a controlled causal comparison. User-attested
authorship, mixed genres, PDF extraction, repeated source documents, and small
cohorts limit generalization. No samples were removed or replaced after scores.

### Proposed single handling improvement

The verified MF03 observation is narrower than classifier accuracy: the route
accepted NUL and escape/control characters, ran GPT-2, and returned model score
0.0, style 0.5, combined 0.25 with unsure. It met the baseline's permissive
string contract and did not crash; it was classified HELD for that stated
objective. Still, the route lacks a guard against unsupported invisible controls,
and the inference is unnecessary for this content.

The one planned substantive change is a pre-inference 400 for C0 control
characters other than tab, newline, and carriage return, plus DEL. It will
produce a useful JSON error and the existing rejection audit event. It will not
strip/rewrite writing, ban non-Latin/emoji text, or change signals, scores,
weights, thresholds, labels, or rate limits. Expected measured benefit: MF03
changes from a completed inference/decision to an explicit rejection. Expected
cost: text intentionally containing those controls must be cleaned before
submission; ordinary multiline writing remains valid. No improvement in the
criterion-2 separation or the nine evasion verdicts is promised. The original
review rules and targets remain fixed for the after comparison.

A broader classifier change would require additional validated evidence; this
assignment permits one focused change. Record any lack of detection improvement
honestly rather than tuning the cohort or thresholds until the numbers improve.
