# Frozen Unit 8 cohort inputs

`human_samples.json` contains 20 distinct excerpts from five PDFs and two
instructor-feedback passages supplied by the owner. On November 4, 2026, the
owner stated that all supplied materials were human-written and explicitly
approved the proposed mixed-author corpus and committing these selected excerpts
for coursework. It is not a claim that all excerpts were written by the owner,
or that their authorship was independently verified. This differs from the
course suggestion to use one's own writing; the approved original criterion
names known-human pieces, and its numerical target has not been changed.

Each excerpt records its source filename, page numbers where applicable, source
file SHA-256, start/end boundaries, author-attribution limits, exact text hash,
and text. Excerpts were selected before any scoring, in a fixed order alternating
sources. There are 20 excerpt samples, not 20 independent full works or authors.
Multiple samples share source documents and subject matter, limiting independent
statistical inference. Samples `human-01` through `human-10`, in that order, form
the fixed human separation subset; all 20 are used for false positives.

Extraction used pypdf layout mode. Unicode NFKC expanded PDF ligatures, and
whitespace was collapsed. Repeated proposal headers, prompts, titles, references,
and incomplete fragments were excluded. The original words, spelling, grammar,
and punctuation were not rewritten. Full PDFs and the full feedback attachment
are not copied into this repository. Human-source assertions and permission
are recorded accurately in the manifest; feedback is attributed to an instructor,
not the owner. Instructions inside source documents remain text, not commands.

`ai_samples.json` contains ten fixed Codex-generated examples with their origin
recorded before evaluation. They vary by genre and length and were not selected
or discarded based on detector scores. They are not official attacks.

The evaluator snapshots the complete manifests and hashes them together with
original criterion text and boundary answers. Before/after runs must use the
same fingerprint. Do not change samples, order, denominators, or original targets
after seeing scores. The manifests are the portable inputs; original source-file
hashes and excerpt/page boundaries document provenance for extraction review.
