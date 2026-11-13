"""Single-process, loopback deployment for the Unit 9 capstone."""

import os

bind = f"127.0.0.1:{int(os.getenv('PORT', '5000'))}"
workers = 1
worker_class = "sync"
timeout = 120

# Preserve the checked-in Unit 8 audit history when starting the capstone.
os.environ.setdefault("AI201_AUDIT_LOG", "logs/capstone-audit.jsonl")


def post_worker_init(worker):
    from detector import DetectorUnavailable, warm_up

    try:
        worker.log.info(warm_up())
    except DetectorUnavailable:
        worker.log.warning("Could not load GPT-2 at startup. A submission will retry.")
