#!/usr/bin/env python3
"""Capture actual curl requests/responses for the README; appends real audit events.

Start app.py separately, then run `.venv/bin/python scripts/capture_sample.py`.
Default URL is port 5057; pass a URL as the first argument to override it.
"""

import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5057"
    result = {"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "produced_by": "scripts/capture_sample.py::main", "url": url, "interactions": []}

    def call(method, route, body=None):
        args = ["curl", "--silent", "--show-error", "--fail-with-body", "--max-time", "90", "-X", method, url + route]
        if body is not None:
            args += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
        command = shlex.join(args)
        completed = subprocess.run(args, capture_output=True, text=True, check=True)
        payload = json.loads(completed.stdout)
        result["interactions"].append({"command": command, "method": method, "route": route, "request": body, "response": payload})
        print("$ " + command)
        print(json.dumps(payload, indent=2))
        return payload

    call("GET", "/health")
    call("POST", "/ping", {"message": "hello"})
    submission = call("POST", "/submit", {
        "text": "A writing platform needs clear rules. Writers should understand how their work will be reviewed and how to ask for help when the automated system makes a mistake.",
        "creator_id": "sample-writer"})
    call("POST", "/appeal", {"content_id": submission["content_id"],
                             "reasoning": "Please review this demonstration submission and its automated estimate."})
    entries = call("GET", "/log?limit=2")
    assert [entry["status"] for entry in entries["entries"]] == ["decided", "under_review"]
    assert all(entry["content_id"] == submission["content_id"] for entry in entries["entries"])
    assert call("GET", "/health")["detector_loaded"]
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "sample_run.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
