# Frozen Unit 8 cohort inputs

The human manifest is pending the owner's authentic writing and explicit
coursework-publication permission. No human text is generated or inferred from
its apparent style. Do not run acceptance trials on replacement placeholders.

Provide `human_samples.json` with this structure (the samples array must contain
exactly 20 distinct pieces, in a fixed order):

```json
{
  "author": "Aditya Chopra",
  "public_coursework_use": true,
  "authorship_attestation": "Describe the owner's confirmation of personal authorship and whether generative AI was involved.",
  "samples": [
    {"id": "human-01", "source": "Original work identified by the owner", "text": "Actual owner-provided writing"}
  ]
}
```

The schema example is not a real sample and must not be evaluated. The first ten
pieces, in the declared order, form the human separation subset. Preserve all 20
for false-positive testing. Every record must have a unique ID, nonblank text,
and a source description. Record any AI assistance accurately; it may make an
excerpt unsuitable for the known-human group.

`ai_samples.json` will contain ten newly generated examples with their origin
recorded before evaluation. Those may vary by genre and length; they must not be
selected or discarded based on detector scores. They are not official attacks.

The evaluator fingerprints and snapshots the complete manifests. Before/after
runs must use the same cohort and original targets. Historical-web excerpts from
Unit 7 are not substituted for the owner's required writing.
