"""Run the five capstone criteria over real loopback HTTP with cached GPT-2."""

import argparse
import json
import math
import os
import platform
import socket
import statistics
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from time import perf_counter, sleep
from urllib.error import HTTPError
from urllib.request import Request, urlopen


FIXTURES = (
    "The library opened early. Someone had already left a book by the door.",
    "By dusk, rain had filled the chipped bowl beside the porch. A sparrow dipped its beak into it.",
    "The proposal outlines three steps. First, gather the records. Next, sort them by date. Finally, publish a summary.",
    "I fixed the loose hinge this morning. The pantry door used to click whenever the furnace started.",
    "A bright orange kite rose above the field, stopped, and dipped. Below it, two children ran toward the fence.",
)
PREDICTION = ("guess", "confidence", "label", "model_score", "style_score", "status")
CRITERIA = ("structured_logging", "performance", "deployment", "failure_logging", "submit_and_appeal")
REASON = "Synthetic acceptance case requesting review of the original decision."


def send(base, route, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(base + route, data=data, headers={"Content-Type": "application/json"})
    started = perf_counter()
    try:
        response = urlopen(request, timeout=125)
    except HTTPError as error:
        response = error
    with response:
        raw = response.read()
        client_ms = (perf_counter() - started) * 1000
        try:
            body = json.loads(raw)
        except ValueError:
            body = raw.decode("utf-8", errors="replace")
        return {
            "http_status": response.code, "body": body,
            "request_id": response.headers.get("X-Request-ID"),
            "client_ms": client_ms, "input_bytes": None if data is None else len(data),
        }


@contextmanager
def service(checkout, gunicorn, reference=False):
    with tempfile.TemporaryDirectory(prefix="provenance-capstone-") as directory:
        paths = Path(directory)
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        environment = dict(os.environ, PORT=str(port), HF_HUB_OFFLINE="1", AI201_RATE_LIMITS="1",
                           AI201_DETECTOR_MODEL="gpt2", AI201_AUDIT_LOG=str(paths / "audit.jsonl"),
                           AI201_REQUEST_LOG=str(paths / "requests.jsonl"))
        # The historical app predates the configurable audit path. It runs in
        # a disposable checkout and writes to that checkout's existing audit.
        args = ("--bind", f"127.0.0.1:{port}", "--workers", "1", "--timeout", "120") if reference else (
            "-c", "gunicorn.conf.py")
        with (paths / "gunicorn.log").open("w+", encoding="utf-8") as startup_log:
            started = perf_counter()
            process = subprocess.Popen([str(gunicorn), *args, "app:app"], cwd=checkout,
                                       env=environment, stdout=startup_log, stderr=startup_log)
            try:
                while True:
                    try:
                        with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                            break
                    except OSError:
                        if process.poll() is not None or perf_counter() - started > 10:
                            raise RuntimeError("Gunicorn did not bind within 10 seconds")
                        sleep(0.02)
                health = send(base, "/health")
                yield base, paths, health, (perf_counter() - started) * 1000
            except (OSError, RuntimeError):
                startup_log.seek(0)
                print(startup_log.read(), file=sys.stderr)
                raise
            finally:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


def records(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def matching(events, response):
    matches = [event for event in events if event["request_id"] == response["request_id"]]
    return matches[0] if len(matches) == 1 else {}


def valid_record(event, response):
    timestamp = event.get("timestamp")
    if not isinstance(timestamp, str):
        return False
    try:
        datetime.fromisoformat(timestamp)
    except ValueError:
        return False
    duration = event.get("duration_ms")
    return (event.get("input_bytes") == response["input_bytes"]
            and event.get("http_status") == response["http_status"]
            and isinstance(duration, (int, float)) and math.isfinite(duration))


def prediction(response):
    body = response["body"]
    if response["http_status"] != 200 or not isinstance(body, dict) or not all(k in body for k in PREDICTION):
        return None
    return {key: body[key] for key in PREDICTION}


def revision(checkout):
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout, text=True).strip()


def original_predictions(checkout, gunicorn):
    with service(checkout, gunicorn, reference=True) as (base, _, health, _):
        submissions = [send(base, "/submit", {"text": text, "creator_id": f"capstone-reference-{i}"})
                       for i, text in enumerate(FIXTURES, 1)]
    if any(prediction(response) is None for response in submissions):
        raise RuntimeError(f"Reference inference did not succeed: {submissions}")
    return {"commit": revision(checkout), "health": health, "submissions": submissions}


def trial_case(base, paths, health, ready_ms, text, case_id, expected):
    submit = send(base, "/submit", {"text": text, "creator_id": case_id})
    actual = prediction(submit)
    content_id = submit["body"].get("content_id") if actual else None
    appeal = send(base, "/appeal", {"content_id": content_id, "reasoning": REASON}) if content_id else None
    invalid = send(base, "/submit", {"text": "", "creator_id": case_id})
    events = records(paths / "requests.jsonl")
    submission_log = matching(events, submit)
    invalid_log = matching(events, invalid)
    appeal_events = [event for event in records(paths / "audit.jsonl") if content_id
                     and event.get("content_id") == content_id]
    expected_output = {key: value for key, value in (actual or {}).items() if key != "label"}
    checks = {
        "structured_logging": valid_record(submission_log, submit) and bool(actual)
        and submission_log.get("output") == expected_output,
        "performance": valid_record(submission_log, submit) and bool(actual)
        and 0 < submission_log["duration_ms"] <= submit["client_ms"] + 100,
        "deployment": health["http_status"] == 200 and health["body"].get("ok") is True and bool(actual),
        "failure_logging": valid_record(invalid_log, invalid) and invalid["http_status"] == 400
        and invalid["body"].get("error") == invalid_log.get("error") == "invalid_text",
        "submit_and_appeal": actual == expected and bool(appeal) and appeal["http_status"] == 200
        and appeal["body"].get("status") == "under_review" and appeal["body"].get("content_id") == content_id
        and [event.get("status") for event in appeal_events] == ["decided", "under_review"]
        and appeal_events[0].get("request_id") == submit["request_id"]
        and appeal_events[1].get("request_id") == appeal["request_id"]
        and appeal_events[1].get("reasoning") == REASON,
    }
    return {"case": case_id, "ready_ms": ready_ms, "health": health, "submit": submit,
            "appeal": appeal, "invalid": invalid, "checks": checks, "requests": events,
            "decision_and_appeal": appeal_events}


def measure_warm_cost(base, paths):
    submissions = [send(base, "/submit", {"text": FIXTURES[index % len(FIXTURES)],
                                          "creator_id": f"capstone-cost-{index + 1}"}) for index in range(10)]
    events = records(paths / "requests.jsonl")
    logs = [matching(events, response) for response in submissions]
    if not all(prediction(response) and valid_record(event, response) and event.get("model_loaded_before")
               for response, event in zip(submissions, logs)):
        raise RuntimeError("Warm cost measurement requires ten successful warm requests with telemetry")
    mean_ms = statistics.mean(event["duration_ms"] for event in logs)
    return {"submissions": submissions, "requests": logs, "mean_server_ms": mean_ms,
            "mean_client_ms": statistics.mean(response["client_ms"] for response in submissions),
            "server_seconds_per_100": 100 * mean_ms / 1000}


def evaluate(checkout, gunicorn, reference):
    trials = []
    for trial in range(1, 4):
        cases = []
        for index, text in enumerate(FIXTURES, 1):
            with service(checkout, gunicorn) as (base, paths, health, ready_ms):
                case = trial_case(base, paths, health, ready_ms, text, f"t{trial}-case{index}",
                                  prediction(reference["submissions"][index - 1]))
                cases.append(case)
                print(case["case"], case["checks"], flush=True)
                if (trial, index) == (3, len(FIXTURES)):
                    cost = measure_warm_cost(base, paths)
        trials.append({"trial": trial, "cases": cases,
                       "passes": {name: sum(case["checks"][name] for case in cases) for name in CRITERIA}})
    return {"commit": revision(checkout), "python": platform.python_version(), "platform": platform.platform(),
            "reference_commit": reference["commit"], "trials": trials, "warm_cost": cost,
            "verdicts": {name: "MET" if all(trial["passes"][name] == len(FIXTURES) for trial in trials)
                         else "MISSED" for name in CRITERIA}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True, help="Clean checkout of the code to run")
    parser.add_argument("--gunicorn", type=Path, required=True, help="Gunicorn from the freshly installed venv")
    parser.add_argument("--reference", type=Path, help="Original Unit 8 output from a reference run")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checkout, gunicorn = args.checkout.resolve(), args.gunicorn.resolve()
    if args.reference:
        report = evaluate(checkout, gunicorn, json.loads(args.reference.read_text(encoding="utf-8")))
    else:
        report = original_predictions(checkout, gunicorn)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
