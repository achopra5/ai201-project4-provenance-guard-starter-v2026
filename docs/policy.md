# Approved scoring policy — recorded before implementation

The owner approved this policy on October 31, 2026, after supplying the five
criteria and before new evaluation.

`scoring.py::combine_signals` will compute
`0.5 * model_score + 0.5 * style_score`. Both inputs must be finite and in
[0, 1]. No learned weights or extra disagreement penalty will be applied.
A 0.9/0.1 split yields 0.5, which is unsure. The two measurements differ in
method but are not assumed statistically independent or equally accurate.

- `0 <= score <= 0.20`: human.
- `0.20 < score < 0.85`: unsure.
- `0.85 <= score <= 1`: AI.

This wide unsure band prioritizes avoiding accusations over catching all AI
writing. No automatic publishing penalty or removal is performed. The 5%
false-positive criterion is a test-sample target, not a measured guarantee.

Exact approved labels:

- Human: “This writing appears likely to be human-written. This is an automated estimate, not proof of authorship. The writer can request a review.”
- Unsure: “We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.”
- AI: “This writing shows patterns associated with AI-generated text. This is an automated estimate, not proof of AI use. The writer can request a review.”

## Stylometry normalization planned before calibration

Measure sentence lengths in Unicode word tokens. Sentence spread is population
standard deviation divided by mean sentence length (zero when fewer than two
nonempty sentences). Type-token ratio is distinct lowercase tokens divided by
total tokens (zero for no tokens). Punctuation density is the number of Unicode
punctuation characters divided by total characters (zero for empty text).

Convert to AI-oriented components: `1 - min(spread, 1)`, `1 - TTR`, and
`1 - min(punctuation_density / 0.10, 1)`. Average the three equally. These are
explicit heuristic normalization scales, not learned statistical evidence.
Low variability, repetition, and sparse punctuation push upward. Abundant
punctuation, rare vocabulary, sentence restructuring, and text length can all
move the result without changing authorship. On fewer than 20 word tokens or
fewer than two nonempty sentences, return a neutral style score of 0.5 because
there is too little evidence to infer regularity. Raw measures remain available.

Both signals' blind spots and this short-text behavior must be documented. The
normalization will not be adjusted to chase calibration or hidden attack scores.
