"""Load the active owner-confirmed cohort without publishing private excerpts."""

import hashlib
import json
from pathlib import Path

import config

MANIFEST = config.ROOT / "data/unit8/corrected_human_manifest.json"
PRIVATE = config.ROOT / ".private/unit8/corrected_human_samples.json"
AI = config.ROOT / "data/unit8/ai_samples.json"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(manifest_path=MANIFEST, private_path=PRIVATE, ai_path=AI):
    manifest_path, private_path, ai_path = map(Path, (manifest_path, private_path, ai_path))
    manifest = json.loads(manifest_path.read_text())
    if not private_path.exists():
        raise ValueError("The active corrected human corpus is local-only. Reconstruct it from the three confirmed PDFs; never fall back to the historical mixed corpus.")
    private = json.loads(private_path.read_text())
    if manifest.get("local_evaluation_authorized") is not True or manifest.get("commit_excerpt_text") is not False:
        raise ValueError("Corrected corpus must authorize local evaluation and forbid excerpt publication.")
    if manifest.get("corpus_id") != private.get("corpus_id"):
        raise ValueError("Private/public cohort identifiers differ.")
    metadata, samples = manifest.get("samples", []), private.get("samples", [])
    if len(metadata) != 20 or len(samples) != 20:
        raise ValueError("The original denominator requires exactly 20 excerpts.")
    texts, ids = set(), set()
    spans = {}
    for expected, actual in zip(metadata, samples):
        if {k: actual.get(k) for k in expected} != expected:
            raise ValueError("Private metadata or ordering differs from the frozen public manifest.")
        text = actual.get("text")
        if not isinstance(text, str) or not text.strip() or hashlib.sha256(text.encode()).hexdigest() != expected["text_sha256"]:
            raise ValueError("Private text is missing or differs from its frozen hash.")
        if text in texts or actual["id"] in ids:
            raise ValueError("Corrected excerpts must be distinct.")
        texts.add(text)
        ids.add(actual["id"])
        spans.setdefault(actual["source"], []).append((actual["start_in_document"], actual["end_in_document"]))
    for ranges in spans.values():
        ranges.sort()
        if any(a[1] > b[0] for a,b in zip(ranges,ranges[1:])):
            raise ValueError("Source excerpt intervals overlap.")
    if manifest["separation_subset"] != [s["id"] for s in samples[:10]]:
        raise ValueError("The fixed separation subset changed.")
    if digest(ai_path) != manifest["ai_manifest_sha256"]:
        raise ValueError("The original AI cohort changed.")
    if digest(config.ROOT / "docs/unit8/criteria.md") != manifest["criteria_sha256"]:
        raise ValueError("The original acceptance criteria changed.")
    ai = json.loads(ai_path.read_text())
    if len(ai.get("samples", [])) != 10:
        raise ValueError("The original AI denominator is 10.")
    return {"human": private, "ai": ai}


def public_snapshot():
    """Only public metadata and hashes may be embedded in committed results."""
    return {"human_manifest": json.loads(MANIFEST.read_text()),
            "human_manifest_sha256": digest(MANIFEST), "ai_manifest_sha256": digest(AI),
            "criteria_sha256": digest(config.ROOT / "docs/unit8/criteria.md")}
