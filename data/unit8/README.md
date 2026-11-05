# Active corrected Unit 8 cohort

The active cohort is `corrected_human_manifest.json` plus local-only text in
`.private/unit8/corrected_human_samples.json`. The owner explicitly confirmed
personal authorship without generative AI of only `THE TRANSITION.pdf`,
`supplemental essays.pdf`, and `UC.pdf` and authorized non-sensitive excerpts for
coursework. Instructor feedback, example essays, application questions, quoted
material, family details, and uncertain authorship are excluded from the active
selection. The historical mixed-author files remain unchanged evidence.

## Deterministic selection, frozen before corrected scoring

`corrected_selection_plan.json` records exact source PDF hashes, canonical page
positions, and reviewed eligible intervals. Within each eligible interval,
`scripts/build_corrected_corpus.py` takes consecutive 50-word windows, appending
a final tail shorter than 25 words to its preceding window. Regions shorter
than 25 words are unused. It then cycles through the three document candidate
lists in source order until 20 distinct excerpts are selected. Duplicate exact
texts are skipped without consulting any scores. No words are added, reordered,
corrected, or paraphrased. Whitespace is collapsed after pypdf layout extraction;
all non-whitespace Unicode and punctuation are retained. Windows may begin/end
inside sentences, so segmentation effects limit generalization.

The result is 7 excerpts from THE TRANSITION, 6 from supplemental essays, and
7 from UC. These are **20 excerpts from three documents, not 20 independent
works or authors**. All 20 serve criterion 1; the immutable first ten IDs in the
manifest serve criterion 2. Prior mixed-author runs exposed some overlapping
source material, so this is not claimed to be an unseen holdout. The corrected
selection uses only frozen source positions and fixed window rules, never scores.

Every sample has document/page character offsets, length, and text SHA-256 in
the public manifest. Full text, extracted source text, and historical runtime
exports stay in ignored `.private/`. No full personal PDFs or new excerpt prose
are committed. Reproduction of the text requires authorized access to the three
original PDFs; public hashes/results alone do not reveal the source passages.

Use Python with pypdf (the bundled document runtime was used):

```bash
python scripts/build_corrected_corpus.py --source-dir /path/to/original/pdfs
python scripts/build_corrected_corpus.py --source-dir /path/to/original/pdfs --verify
```

The builder refuses to overwrite frozen inputs; verify re-extracts them in memory
and checks exact text, positions, hashes, and ordering. Default scenario loading
uses the corrected private corpus and fails clearly when local text is absent;
it never silently falls back to mixed-author history. Snapshots of this cohort
contain metadata/hashes only.

The original ten `ai_samples.json` records and original `criteria.md` are unchanged.

## Corrected runs and historical evidence

`scripts/run_corrected_eval.py` exports the exact runtime files from `8524fa8`
(before) or `ea0dbd4` (after), verifies their hashes against the original staff
runs, and starts its own local service with fresh 8/minute and 100/day counters.
Only affected criteria 1 and 2 are rerun: three trials each per version. Public
results and text-free request audit records live under `results/unit8/corrected/`.
The three unaffected criteria retain their explicitly identified historical
three-trial evidence rather than being represented as newly executed.

`human_samples.json`, the original `eval_before.json`/`eval_after.json` snapshots,
and the original attack/comparison artifacts are **historical, not active**.
They retain previously approved mixed-author excerpts exactly as the owner asked;
this correction adds no new excerpt text to tracked files and does not rewrite
Git history. The original attacks and single improvement remain unchanged.
