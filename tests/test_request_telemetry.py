import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import config
from app import app


class RequestTelemetryTests(unittest.TestCase):
    def test_redaction_and_correlation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "requests.jsonl"
            with patch.object(config, "REQUEST_LOG", path), patch.object(config, "AUDIT_LOG", path.with_name("audit.jsonl")):
                client = app.test_client()
                responses = [
                    client.post("/ping?query_secret=1", json={"message": "echo_secret"}),
                    client.post("/submit", json={"creator_id": "creator_secret", "text": ""}),
                    client.options("/appeal"),
                    client.get("/path_secret", headers={"Authorization": "header_secret"}),
                ]
                raw = path.read_text(encoding="utf-8")
        self.assertNotIn("_secret", raw)
        records = [json.loads(line) for line in raw.splitlines()]
        self.assertEqual(len(records), len(responses))
        for record, response in zip(records, responses):
            self.assertEqual(record["request_id"], response.headers["X-Request-ID"])
            self.assertEqual(record["http_status"], response.status_code)
            self.assertGreater(record["duration_ms"], 0)
        self.assertEqual(records[1]["error"], "invalid_text")
        self.assertIsNone(records[3]["route"])
        self.assertEqual(records[3]["error"], "http_404")

    def test_write_failure_preserves_response(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(config, "REQUEST_LOG", Path(directory)), self.assertLogs(app.logger, level="ERROR"):
                self.assertEqual(app.test_client().get("/health").status_code, 200)
