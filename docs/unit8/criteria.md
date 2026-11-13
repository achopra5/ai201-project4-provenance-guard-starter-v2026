# Acceptance criteria — Provenance Guard

These five criteria and their reasons were provided by the project owner on
October 31, 2026, before implementation and new evaluation results. Their wording
is preserved below. The earlier environment transcript included the starter
model's default demonstration score; it was not an evaluation of these criteria.

## 1. False positives — Protect human writers

My suggested target: Out of 20 pieces of writing known to be human-written, no more than 1 should receive a high-confidence AI label.

**Why this target:** Wrongly accusing a real writer is more harmful than failing to identify some AI-generated content. This gives us a strict but measurable target of 5% on our test sample.

## 2. Score separation — Can the detector distinguish the groups?

My suggested target: Test 10 known-human and 10 known-AI samples. The average AI-likelihood score for AI writing should be at least 0.20 higher than the human-writing average.

**Why this target:** If both groups receive similar scores, combining two signals isn't accomplishing much. We should expect some measurable distinction, even if individual predictions are imperfect.

## 3. Label coverage — Do all three outcomes work?

My suggested target: Test 7 numerical scores, including 0, 1, values near both thresholds, and values inside each classification region. All 7 must map to the expected label, and all three labels must appear.

**Why this target:** The system must reliably distinguish between AI, human, and unsure. Every valid score needs exactly one outcome.

## 4. Appeals — Can writers challenge a decision?

My suggested target: Submit 5 valid appeals for existing content IDs. All 5 must be recorded with their reasoning, change to under_review, and appear in the audit log.

**Why this target:** Since the detector can be wrong, the appeal mechanism needs to work every time. We shouldn't make someone depend on an unreliable process to challenge an accusation.

## 5. Invalid inputs — Does the API reject bad requests?

My suggested target: Test 6 invalid submissions: missing text, empty text, whitespace-only text, non-string text, missing creator ID, and malformed JSON. All 6 should return a suitable 4xx error without creating a successful submission record.

**Why this target:** Invalid inputs should not silently produce misleading classifications or crash the backend.

---

## Reproduction notes (clarifications, not revised targets)

- The approved score means the combined AI-likeness index returned as
  `confidence`, not a calibrated probability. `ai` is the high-confidence AI label.
- Criterion 3's seven scores are `0`, `0.20`, `0.200001`, `0.50`, `0.849999`,
  `0.85`, and `1`; expected guesses are `human`, `human`, `unsure`, `unsure`,
  `unsure`, `ai`, and `ai`. Additional boundary tests may supplement these.
- Use five distinct existing submissions for criterion 4, preserve each appeal's
  exact reasoning, and verify both the original decision and latest status.
- For criterion 5, use `123` as the non-string text and a truncated JSON body
  for malformed JSON. A suitable error is HTTP 400; no `status: decided` event
  may be written for these requests.
- Freeze and identify sample origins before evaluating criteria 1 and 2. The
  10 human pieces for criterion 2 may be a declared subset of the 20 for
  criterion 1. A result on this sample is not a population error-rate estimate.
- Unit 8 evaluates the fixed criteria across three trials. Report any missed
  target honestly. Do not lower it after seeing results; retain original wording
  and append a reasoned revision only if a criterion itself is untestable.
- Unit 7 calibration examples are a small diagnostic set, not the 20/10/10
  acceptance evaluation. The Unit 8 attack and criterion runners stay unused.
