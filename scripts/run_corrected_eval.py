#!/usr/bin/env python3
"""Rerun only criteria 1–2 on the corrected private cohort and historical service.

Exports byte-identical runtime files from Git to ignored .private/, launches its
own local server with fresh counters, then saves metadata and results only.
Historical attack/acceptance files are never overwritten or rerun.
"""

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import config
import corrected_corpus
import run_eval
import scenarios

VERSIONS = {"before": "8524fa8", "after": "ea0dbd4"}
RUNTIME_FILES = ("app.py", "config.py", "audit.py", "detector.py", "stylometry.py", "scoring.py")


def hashes(paths):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def ensure_public(value, private_texts):
    serialized = json.dumps(value, ensure_ascii=False)
    for text in private_texts:
        if text in serialized:
            raise ValueError("Refusing to persist private excerpt text in public evidence.")


def prepare_runtime(phase):
    version = VERSIONS[phase]
    directory = ROOT / ".private/unit8" / f"corrected-runtime-{phase}"
    directory.mkdir(parents=True, exist_ok=True)
    expected = json.loads((ROOT / f"results/unit8/attacks_{phase}.json").read_text())["runtime_sha256"]
    for name in RUNTIME_FILES:
        blob = subprocess.check_output(["git", "show", f"{version}:{name}"], cwd=ROOT)
        if hashlib.sha256(blob).hexdigest() != expected[name]:
            raise ValueError("Historical service does not match its recorded attack runtime.")
        path = directory / name
        if path.exists() and path.read_bytes() != blob:
            raise ValueError("Existing historical runtime export differs; refuse replacement.")
        path.write_bytes(blob)
    if (directory / "logs/audit.jsonl").exists():
        raise ValueError("Runtime already has request history; do not reuse its counters/log as fresh.")
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", choices=("before", "after"), required=True)
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    out = ROOT / "results/unit8/corrected"
    out.mkdir(exist_ok=True)
    path = out / f"eval_{args.label}.json"
    if path.exists():
        parser.error("Corrected run already exists; never overwrite recorded trials.")
    cohorts = corrected_corpus.load()
    snapshot = scenarios.snapshot(cohorts)
    fingerprint = scenarios.fingerprint(snapshot)
    if args.label == "after":
        before = json.loads((out / "eval_before.json").read_text())
        if not before.get("complete") or before["cohort_sha256"] != fingerprint:
            parser.error("Completed corrected before run and identical frozen cohort required.")
    private_texts = [sample["text"] for sample in cohorts["human"]["samples"]]
    directory = prepare_runtime(args.label)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", args.port))
    env = {**os.environ, "HOST": "127.0.0.1", "PORT": str(args.port), "AI201_DEBUG": "0",
           "AI201_RATE_LIMITS": "1", "HF_HUB_OFFLINE": "1", "AI201_DETECTOR_MODEL": "gpt2"}
    command = [sys.executable, str(directory / "app.py")]
    console = directory / "console.log"
    client = run_eval.Client(f"http://127.0.0.1:{args.port}")
    with console.open("x") as stream:
        proc = subprocess.Popen(command, cwd=directory, env=env, stdout=stream, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 30
            health = None
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    raise RuntimeError("Historical local server exited; inspect the ignored console log.")
                health = client.request("/health")
                if health.get("status") == 200:
                    break
                time.sleep(.1)
            body = health.get("response", {}) if health else {}
            if (not body.get("rate_limiting") or body.get("detector_loaded")
                    or body.get("log_entries") != 0 or body.get("detector_model") != "gpt2"):
                raise RuntimeError("Expected fresh historical runtime, enabled limiter, and cached GPT-2 configuration.")
            rid = str(uuid.uuid4())
            result = {"produced_by": "scripts/run_corrected_eval.py using unchanged run_eval.py::run_trial",
                      "phase": args.label, "run_id": rid, "corpus_id": snapshot["human_manifest"]["corpus_id"],
                      "service_commit": VERSIONS[args.label],
                      "service_runtime_sha256": hashes([directory / n for n in RUNTIME_FILES]),
                      "harness_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                      "cohort_sha256": fingerprint, "public_snapshot": snapshot,
                      "started_at": datetime.now(timezone.utc).isoformat(), "health_before": health,
                      "scope": "Corrected criteria 1 and 2 only; historical criteria 3–5 are carried forward explicitly.",
                      "privacy": "Human text remains local; public evidence contains sample IDs/hashes, responses, and audit metadata only.",
                      "criteria": []}
            ensure_public(result, private_texts)
            with path.open("x") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                f.write("\n")
            for criterion in (1, 2):
                definition = next(s for s in scenarios.SCENARIOS if s["criterion"] == criterion)
                row = {**definition, "trials": [], "verdict": "INCOMPLETE"}
                result["criteria"].append(row)
                for trial in (1, 2, 3):
                    observed = run_eval.run_trial(criterion, client, cohorts, f"corrected-{rid}-c{criterion}-t{trial}")
                    row["trials"].append(observed)
                    ensure_public(result, private_texts)
                    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
                    print(f"{args.label}: criterion {criterion}, trial {trial}: {observed['value']}", flush=True)
                row["verdict"] = "MET" if all(t["passed"] for t in row["trials"]) else "MISSED"
            events = client.log()
            ensure_public(events, private_texts)
            if len(events) != 120:
                raise RuntimeError(f"Expected 120 request events, recorded {len(events)}")
            result["audit_event_count"] = len(events)
            result["complete"] = True
            result["finished_at"] = datetime.now(timezone.utc).isoformat()
            ensure_public(result, private_texts)
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
            audit_path = out / f"audit_{args.label}.jsonl"
            with audit_path.open("x") as f:
                for event in events:
                    f.write(json.dumps(event, ensure_ascii=False) + "\n")
            print(f"Saved {len(result['criteria']) * 3} corrected trials and 120 correlated events; private text excluded.")
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=10)


if __name__ == "__main__":
    main()
