"""Unit 8: frozen scenarios for all five original criteria.

Human input is required, not synthesized. The first ten of the declared 20
human pieces form criterion 2's subset. Loading this module never scores text.
"""

import hashlib
import json
from pathlib import Path

import config

DATA_DIR = config.ROOT / "data" / "unit8"
BOUNDARY_CASES = [
    (0.0, "human"), (0.20, "human"), (0.200001, "unsure"),
    (0.50, "unsure"), (0.849999, "unsure"), (0.85, "ai"), (1.0, "ai"),
]
SCENARIOS = [
    {"criterion": 1, "name": "False positives", "target": "At most 1 of 20 human pieces labelled ai", "kind": "false_positives"},
    {"criterion": 2, "name": "Score separation", "target": "AI mean - human mean >= 0.20; 10 samples each", "kind": "separation"},
    {"criterion": 3, "name": "Label coverage", "target": "7/7 specified scores correct; all 3 labels", "kind": "boundaries"},
    {"criterion": 4, "name": "Appeals", "target": "5/5 distinct appeals recorded with reasoning and under_review", "kind": "appeals"},
    {"criterion": 5, "name": "Invalid inputs", "target": "6/6 specified invalid submissions return 400 without decisions", "kind": "invalid"},
]


def load_cohorts(data_dir=DATA_DIR):
    """Validate provenance declarations/counts before permitting any evaluation."""
    # The old mixed corpus remains historical evidence, never the active
    # fallback after the owner corrected authorship and privacy requirements.
    if Path(data_dir).resolve() == DATA_DIR.resolve() and (DATA_DIR / "corrected_human_manifest.json").exists():
        import corrected_corpus
        return corrected_corpus.load()
    manifests = {}
    for key in ("human", "ai"):
        path = Path(data_dir) / f"{key}_samples.json"
        if not path.exists():
            raise ValueError(f"Missing {path}: authentic owner-written human samples and publication permission are required; placeholders cannot be evaluated.")
        manifests[key] = json.loads(path.read_text(encoding="utf-8"))
    human, ai = manifests["human"], manifests["ai"]
    if not isinstance(human, dict) or not isinstance(ai, dict):
        raise ValueError("Both manifests must be JSON objects.")
    if human.get("public_coursework_use") is not True or not human.get("author") or not human.get("authorship_attestation"):
        raise ValueError("Human samples need explicit publication permission, named author, and an accurate authorship attestation.")
    if not ai.get("origin"):
        raise ValueError("AI samples need a documented generation origin.")
    all_ids, all_texts = set(), set()
    for key, expected in (("human", 20), ("ai", 10)):
        records = manifests[key].get("samples")
        if not isinstance(records, list) or len(records) != expected:
            raise ValueError(f"{key} manifest needs exactly {expected} samples, not a changed denominator.")
        for record in records:
            if not isinstance(record, dict) or any(not isinstance(record.get(k), str) or not record[k].strip() for k in ("id", "text", "source")):
                raise ValueError(f"Every {key} sample needs nonblank id, text, and source strings.")
            if record["id"] in all_ids or record["text"] in all_texts:
                raise ValueError("Sample IDs and exact texts must be unique across both cohorts.")
            if len(record["text"]) > config.MAX_TEXT_CHARS:
                raise ValueError(f"{record['id']} exceeds the existing API size limit; discuss the cohort before scoring it.")
            all_ids.add(record["id"])
            all_texts.add(record["text"])
    return manifests


def snapshot(cohorts):
    """Capture exact data, original criteria, and expected boundary answers."""
    if cohorts["human"].get("commit_excerpt_text") is False:
        import corrected_corpus
        return {**corrected_corpus.public_snapshot(), "boundary_cases": BOUNDARY_CASES}
    return {"cohorts": cohorts, "boundary_cases": BOUNDARY_CASES,
            "criteria_sha256": hashlib.sha256((config.ROOT / "criteria.md").read_bytes()).hexdigest()}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def validate():
    try:
        load_cohorts()
    except (ValueError, OSError) as exc:
        return [str(exc)]
    return []
