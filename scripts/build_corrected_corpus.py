#!/usr/bin/env python3
"""Reconstruct the corrected private cohort from exact owner-confirmed PDFs.

Uses pypdf (available in the bundled document runtime). Source-position policy
is public; human excerpt text is written only beneath ignored .private/.
This selector does not import a detector, scoring function, or evaluation result.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical_pages(reader):
    pages, offsets, start = [], [], 0
    for number, page in enumerate(reader.pages, 1):
        text = re.sub(r"\s+", " ", page.extract_text(extraction_mode="layout")).strip()
        pages.append(text)
        offsets.append({"page": number, "start": start, "end": start + len(text)})
        start += len(text) + 1
    return " ".join(pages), offsets


def windows(text, start, end, size=50, minimum=25):
    """Non-overlapping fixed word windows; short final tail joins the prior one."""
    tokens = list(re.finditer(r"\S+", text[start:end]))
    if len(tokens) < minimum:
        return []
    spans = []
    index = 0
    while index < len(tokens):
        stop = min(index + size, len(tokens))
        if 0 < len(tokens) - stop < minimum:
            stop = len(tokens)
        spans.append((start + tokens[index].start(), start + tokens[stop - 1].end()))
        index = stop
    return spans


def select(plan, documents):
    pools = []
    policy = plan["selection_algorithm"]
    for source in plan["sources"]:
        text = documents[source["filename"]]
        pool = []
        for region_index, region in enumerate(source["eligible_regions"]):
            for start, end in windows(text, region["start"], region["end"],
                                      policy["word_window"], policy["minimum_tail_words"]):
                pool.append((source, region_index, start, end, text[start:end]))
        pools.append(pool)
    chosen, seen = [], set()
    for index in range(max(map(len, pools))):
        for pool in pools:
            if index < len(pool):
                item = pool[index]
                digest = sha(item[-1].encode("utf-8"))
                if digest not in seen:
                    chosen.append(item)
                    seen.add(digest)
                if len(chosen) == 20:
                    return chosen
    raise ValueError("Approved source regions cannot provide 20 distinct windows.")


def build(source_dir, plan_path):
    import pypdf
    plan = json.loads(plan_path.read_text())
    documents = {}
    for source in plan["sources"]:
        path = source_dir / source["filename"]
        if sha(path.read_bytes()) != source["pdf_sha256"]:
            raise ValueError(f"Source PDF hash mismatch: {source['filename']}")
        text, offsets = canonical_pages(pypdf.PdfReader(path))
        if sha(text.encode()) != source["canonical_text_sha256"] or offsets != source["pages"]:
            raise ValueError("Extraction differs from the frozen source positions; do not guess new boundaries.")
        documents[source["filename"]] = text
    chosen = select(plan, documents)
    public_samples, private_samples = [], []
    for index, (source, region, start, end, text) in enumerate(chosen, 1):
        if any(q in text for q in ('"', '“', '”')):
            raise ValueError("A selected window includes quotation marks; eligibility must be reviewed before scoring.")
        page_ranges = [{"page": p["page"], "start_in_page": max(start, p["start"]) - p["start"],
                        "end_in_page": min(end, p["end"]) - p["start"]}
                       for p in source["pages"] if start < p["end"] and end > p["start"]]
        public = {"id": f"owner-human-{index:02d}", "source": source["filename"],
                  "source_pdf_sha256": source["pdf_sha256"], "region_index": region,
                  "start_in_document": start, "end_in_document": end,
                  "page_ranges": page_ranges, "word_count": len(text.split()),
                  "character_count": len(text), "text_sha256": sha(text.encode())}
        public_samples.append(public)
        private_samples.append({**public, "text": text})
    manifest = {"corpus_id": plan["corpus_id"], "author": plan["author"],
                "authorship_attestation": plan["authorship_attestation"],
                "local_evaluation_authorized": True, "commit_excerpt_text": False,
                "frozen_on": plan["created_on"], "selection_plan_sha256": sha(plan_path.read_bytes()),
                "extractor": {"package": "pypdf", "version": pypdf.__version__, "mode": "layout; whitespace collapse only"},
                "ai_manifest_sha256": sha((ROOT / "data/unit8/ai_samples.json").read_bytes()),
                "criteria_sha256": sha((ROOT / "docs/unit8/criteria.md").read_bytes()),
                "sampling_unit": "20 excerpts from three owner-authored source documents, not 20 independent works.",
                "separation_subset": [p["id"] for p in public_samples[:10]],
                "prior_exposure": plan["prior_exposure"], "samples": public_samples}
    private = {"corpus_id": plan["corpus_id"], "author": plan["author"],
               "authorship_attestation": plan["authorship_attestation"],
               "local_evaluation_authorized": True, "commit_excerpt_text": False,
               "samples": private_samples}
    return manifest, private


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--plan", type=Path, default=ROOT / "data/unit8/corrected_selection_plan.json")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/unit8/corrected_human_manifest.json")
    parser.add_argument("--private-output", type=Path, default=ROOT / ".private/unit8/corrected_human_samples.json")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    private_path = args.private_output.resolve()
    if not private_path.is_relative_to((ROOT / ".private").resolve()):
        parser.error("Excerpt text must stay beneath ignored .private/.")
    if not args.verify and (args.manifest.exists() or private_path.exists()):
        parser.error("A frozen corpus already exists; refuse to reseat boundaries or overwrite it.")
    manifest, private = build(args.source_dir, args.plan)
    if args.verify:
        assert json.loads(args.manifest.read_text()) == manifest
        assert json.loads(private_path.read_text()) == private
        print("Re-extraction exactly matches all frozen hashes, positions, text, and ordering.")
        return
    private_path.parent.mkdir(parents=True, exist_ok=True)
    with private_path.open("x", encoding="utf-8") as stream:
        json.dump(private, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    with args.manifest.open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print("Frozen 20 private excerpts; public manifest contains metadata/hashes only.")
    print("Source counts:", {name: sum(r['source'] == name for r in manifest['samples']) for name in (s['filename'] for s in json.loads(args.plan.read_text())['sources'])})


if __name__ == "__main__":
    main()
