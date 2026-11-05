#!/usr/bin/env python3
"""Evaluate all five original criteria, three real trials per before/after run.

    .venv/bin/python run_eval.py --label before
    .venv/bin/python run_eval.py --label after

Requires the frozen owner/AI cohorts and the corresponding full staff attack
run. Direct boundary checks are identified as function calls, not HTTP traffic.
The detector is deterministic; identical trials are expected and all are saved.
"""

import argparse
import hashlib
import json
import math
import statistics
import subprocess
import time
import uuid
from datetime import datetime, timezone

import requests

import config
import scenarios
import scoring


class Client:
    def __init__(self, url, timeout=90):
        self.url = url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def request(self, path, body=None, raw=None):
        started = time.perf_counter()
        kwargs = {"timeout": self.timeout}
        method = "GET" if body is None and raw is None else "POST"
        if raw is not None:
            kwargs.update(data=raw, headers={"Content-Type": "application/json"})
        elif body is not None:
            kwargs["json"] = body
        try:
            response = self.session.request(method, self.url + path, **kwargs)
            result = {"status": response.status_code,
                      "request_id": response.headers.get("X-Request-ID"),
                      "elapsed_seconds": time.perf_counter() - started}
            try:
                result["response"] = response.json()
            except ValueError:
                result.update(response_text=response.text, error="Non-JSON response")
            return result
        except requests.RequestException as exc:
            return {"status": None, "error": f"{type(exc).__name__}: {exc}"}

    def log(self):
        reply = self.request("/log")
        if reply.get("status") != 200 or not isinstance(reply.get("response"), dict):
            raise RuntimeError(f"Could not read audit evidence: {reply}")
        entries = reply["response"].get("entries")
        if not isinstance(entries, list):
            raise RuntimeError("/log did not return an entries list")
        return entries


def usable(reply):
    body = reply.get("response")
    if reply.get("status") != 200 or not isinstance(body, dict) or body.get("guess") not in ("human", "unsure", "ai"):
        return False
    return all(isinstance(body.get(k), (int, float)) and not isinstance(body[k], bool)
               and math.isfinite(body[k]) and 0 <= body[k] <= 1
               for k in ("confidence", "model_score", "style_score"))


def submit_samples(client, samples, prefix):
    rows = []
    for index, sample in enumerate(samples):
        reply = client.request("/submit", body={"text": sample["text"], "creator_id": f"{prefix}-{index}"})
        rows.append({"sample_id": sample["id"], "text_sha256": hashlib.sha256(sample["text"].encode()).hexdigest(), **reply})
    return rows


def evaluate_false_positives(client, cohorts, prefix):
    rows = submit_samples(client, cohorts["human"]["samples"], prefix)
    valid = sum(usable(r) for r in rows)
    false_positives = sum(r.get("response", {}).get("guess") == "ai" for r in rows if isinstance(r.get("response"), dict))
    return {"passed": valid == 20 and false_positives <= 1,
            "value": f"{false_positives}/20 AI labels; {valid}/20 usable", "false_positives": false_positives,
            "usable": valid, "denominator": 20, "cases": rows}


def evaluate_separation(client, cohorts, prefix):
    human = submit_samples(client, cohorts["human"]["samples"][:10], prefix + "-human")
    ai = submit_samples(client, cohorts["ai"]["samples"], prefix + "-ai")
    complete = len(human) == 10 and len(ai) == 10 and all(usable(r) for r in human + ai)
    human_mean = statistics.mean(r["response"]["confidence"] for r in human) if complete else None
    ai_mean = statistics.mean(r["response"]["confidence"] for r in ai) if complete else None
    difference = ai_mean - human_mean if complete else None
    return {"passed": complete and difference >= .20,
            "value": f"AI mean - human mean = {difference:.6f}" if complete else "Incomplete 10/10 groups (errors remain in denominator)",
            "human_mean": human_mean, "ai_mean": ai_mean, "difference": difference,
            "human_cases": human, "ai_cases": ai}


def evaluate_boundaries():
    cases = []
    for score, expected in scenarios.BOUNDARY_CASES:
        try:
            guess, label = scoring.score_to_label(score)
            cases.append({"score": score, "expected": expected, "guess": guess,
                          "label": label, "passed": guess == expected})
        except Exception as exc:
            cases.append({"score": score, "expected": expected, "passed": False,
                          "error": f"{type(exc).__name__}: {exc}"})
    count = sum(r["passed"] for r in cases)
    return {"passed": count == 7 and {r.get("guess") for r in cases} == {"human", "unsure", "ai"},
            "value": f"{count}/7 correct", "execution": "Direct scoring.py::score_to_label calls; no HTTP requests", "cases": cases}


def evaluate_appeals(client, cohorts, prefix):
    rows = []
    for i, sample in enumerate(cohorts["ai"]["samples"][:5]):
        submission = client.request("/submit", body={"text": sample["text"], "creator_id": f"{prefix}-{i}"})
        row = {"sample_id": sample["id"], "submission": submission, "passed": False}
        if usable(submission):
            content_id = submission["response"].get("content_id")
            original = [e for e in client.log() if e.get("content_id") == content_id]
            reasoning = f"Please review criterion 4 piece {i + 1}. This is a functional appeal test."
            appeal = client.request("/appeal", body={"content_id": content_id, "reasoning": reasoning})
            history = [e for e in client.log() if e.get("content_id") == content_id]
            passed = (isinstance(content_id, str) and len(original) == 1
                      and original[0].get("status") == "decided" and appeal.get("status") == 200
                      and appeal.get("response", {}).get("status") == "under_review"
                      and len(history) == 2 and history[0] == original[0]
                      and history[-1].get("status") == "under_review"
                      and history[-1].get("reasoning") == reasoning)
            row.update(appeal=appeal, reasoning=reasoning, history=history, passed=passed)
        rows.append(row)
    count = sum(r["passed"] for r in rows)
    return {"passed": count == 5, "value": f"{count}/5 appeal lifecycles", "cases": rows}


def evaluate_invalid(client, prefix):
    cases = [
        ("missing_text", {"creator_id": prefix + "-1"}, None),
        ("empty_text", {"text": "", "creator_id": prefix + "-2"}, None),
        ("whitespace_only", {"text": " \n\t", "creator_id": prefix + "-3"}, None),
        ("nonstring_text", {"text": 123, "creator_id": prefix + "-4"}, None),
        ("missing_creator_id", {"text": "An ordinary submission paragraph."}, None),
        ("malformed_json", None, '{"text":'),
    ]
    rows = [{"name": name, **client.request("/submit", body=body, raw=raw)} for name, body, raw in cases]
    events = client.log()
    for row in rows:
        matches = [e for e in events if row.get("request_id") and e.get("request_id") == row["request_id"]]
        row["audit_events"] = matches
        row["passed"] = (row.get("status") == 400 and bool(matches)
                         and not any(e.get("status") == "decided" for e in matches)
                         and all(e.get("status") == "rejected" for e in matches))
    count = sum(r["passed"] for r in rows)
    return {"passed": count == 6, "value": f"{count}/6 invalid cases rejected with no decisions", "cases": rows}


def run_trial(criterion, client, cohorts, prefix):
    if criterion == 1:
        return evaluate_false_positives(client, cohorts, prefix)
    if criterion == 2:
        return evaluate_separation(client, cohorts, prefix)
    if criterion == 3:
        return evaluate_boundaries()
    if criterion == 4:
        return evaluate_appeals(client, cohorts, prefix)
    if criterion == 5:
        return evaluate_invalid(client, prefix)
    raise ValueError("Unknown criterion")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True, choices=("before", "after"))
    parser.add_argument("--trials", type=int, default=3, choices=(3,))
    parser.add_argument("--url", default=f"http://{config.HOST}:{config.PORT}")
    parser.add_argument("--timeout", type=float, default=90)
    args = parser.parse_args()
    output_dir = config.RESULTS_DIR / "unit8"
    path = output_dir / f"eval_{args.label}.json"
    if path.exists():
        parser.error(f"{path} exists; refusing to overwrite or rerun a recorded experiment.")
    try:
        cohorts = scenarios.load_cohorts()
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    snapshot = scenarios.snapshot(cohorts)
    cohort_hash = scenarios.fingerprint(snapshot)
    attacks_path = output_dir / f"attacks_{args.label}.json"
    if not attacks_path.exists():
        parser.error(f"Run the full staff attack set first; missing {attacks_path}")
    attack_evidence = json.loads(attacks_path.read_text())
    if not attack_evidence.get("complete"):
        parser.error("The attack run is incomplete; preserve that evidence and finish investigating it before acceptance evaluation.")
    if args.label == "after":
        before_path = output_dir / "eval_before.json"
        if not before_path.exists():
            parser.error("A recorded before evaluation is required before after.")
        before = json.loads(before_path.read_text())
        if not before.get("complete") or before.get("cohort_sha256") != cohort_hash:
            parser.error("Cohort, criteria, or expected boundary answers differ from the frozen before run.")
    client = Client(args.url, args.timeout)
    health = client.request("/health")
    if health.get("status") != 200 or not health.get("response", {}).get("rate_limiting"):
        parser.error("Start the service with the approved rate limiter enabled and fresh counters before this experiment.")
    run_id = str(uuid.uuid4())
    result = {"produced_by": "run_eval.py::main/run_trial", "label": args.label,
              "run_id": run_id, "started_at": datetime.now(timezone.utc).isoformat(),
              "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=config.ROOT, text=True).strip(),
              "cohort_sha256": cohort_hash, "snapshot": snapshot, "health_before": health,
              "attack_evidence_sha256": hashlib.sha256(attacks_path.read_bytes()).hexdigest(),
              "runtime_sha256": {name: hashlib.sha256((config.ROOT / name).read_bytes()).hexdigest()
                                  for name in ("app.py", "config.py", "scoring.py", "stylometry.py", "detector.py", "audit.py", "run_eval.py", "scenarios.py")},
              "criteria": []}
    output_dir.mkdir(parents=True, exist_ok=True)
    # Reserve an exclusive artifact and checkpoint after each real trial, so an
    # interrupted run remains visible as incomplete instead of disappearing.
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    for scenario in scenarios.SCENARIOS:
        row = {**scenario, "trials": [], "verdict": "INCOMPLETE"}
        result["criteria"].append(row)
        for trial in range(1, 4):
            prefix = f"eval-{run_id}-c{scenario['criterion']}-t{trial}"
            try:
                observed = run_trial(scenario["criterion"], client, cohorts, prefix)
            except Exception as exc:
                observed = {"passed": False, "value": "Execution error", "error": f"{type(exc).__name__}: {exc}"}
            row["trials"].append(observed)
            print(f"Criterion {scenario['criterion']}, trial {trial}: {observed['value']}", flush=True)
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        row["verdict"] = "MET" if all(t["passed"] for t in row["trials"]) else "MISSED"
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    result["finished_at"] = datetime.now(timezone.utc).isoformat()
    result["complete"] = True
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    lines = [f"# Criteria — {args.label}", "", "Produced by `run_eval.py::main/run_trial`.", "",
             "| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |", "|---|---|---|---|---|---|"]
    for row in result["criteria"]:
        values = " | ".join(t["value"] for t in row["trials"])
        lines.append(f"| {row['criterion']}. {row['name']} | {row['target']} | {values} | {row['verdict']} |")
    for row in result["criteria"]:
        lines += ["", f"## Criterion {row['criterion']} — actual trial 1", "", "```json", json.dumps(row["trials"][0], indent=2, ensure_ascii=False), "```"]
    path.with_suffix(".md").write_text("\n".join(lines) + "\n")
    print(f"Saved all 15 real trial records to {path}")


if __name__ == "__main__":
    main()
