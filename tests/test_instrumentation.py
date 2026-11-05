"""Unit 8 instrumentation checks use temporary logs and controlled local limits."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app as service
import audit
import config
import detector


class AuditInstrumentationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        for name, value in (("LOG_DIR", root), ("AUDIT_LOG", root / "audit.jsonl")):
            p = patch.object(config, name, value)
            p.start()
            self.addCleanup(p.stop)
        p = patch.object(detector, "model_signal", return_value=.6)
        self.model = p.start()
        self.addCleanup(p.stop)
        if hasattr(service.limiter, "enabled"):
            p = patch.object(service.limiter, "enabled", False)
            p.start()
            self.addCleanup(p.stop)
        self.client = service.app.test_client()

    def test_validation_rejection_is_correlated_without_writing_or_fake_scores(self):
        response = self.client.post("/submit", json={"text": "", "creator_id": "writer"})
        self.assertEqual(response.status_code, 400)
        event, = audit.read_entries()
        self.assertEqual(event["request_id"], response.headers["X-Request-ID"])
        self.assertEqual(event["reason"], "invalid_text")
        self.assertEqual(event["status"], "rejected")
        self.assertEqual(event["http_status"], 400)
        self.assertEqual(event["creator_id"], "writer")
        self.assertEqual(event["path"], "/submit")
        for name in ("text", "content_id", "model_score", "style_score", "combined_score"):
            self.assertNotIn(name, event)
        self.model.assert_not_called()

    def test_bad_json_nonobject_and_oversize_are_logged_once_each(self):
        for raw, code in (("{", 400), ("null", 400), ("[]", 400), ("x" * (config.MAX_REQUEST_BYTES + 1), 413)):
            response = self.client.post("/submit", data=raw, content_type="application/json")
            self.assertEqual(response.status_code, code)
        events = audit.read_entries()
        self.assertEqual(len(events), 4)
        self.assertEqual([e["http_status"] for e in events], [400, 400, 400, 413])
        self.assertEqual(len({e["request_id"] for e in events}), 4)

    def test_success_still_contains_nine_required_fields(self):
        text = "An actual paragraph is sent to this controlled test. Its complete text should not be copied into decision metadata."
        response = self.client.post("/submit", json={"text": text, "creator_id": "writer"})
        self.assertEqual(response.status_code, 200)
        event, = audit.read_entries()
        required = {"timestamp", "content_id", "creator_id", "guess", "model_score", "style_score", "combined_score", "label", "status"}
        self.assertTrue(required <= event.keys())
        self.assertEqual(event["request_id"], response.headers["X-Request-ID"])
        self.assertNotIn(text, json.dumps(event))
        self.assertEqual(self.client.get("/log").json["entries"], [event])

    def test_appeals_keep_request_ids_and_rejections(self):
        response = self.client.post("/submit", json={"text": "Enough words for the mocked model.", "creator_id": "writer"})
        content_id = response.json["content_id"]
        response = self.client.post("/appeal", json={"content_id": content_id, "reasoning": "Please review."})
        event = audit.entries_for(content_id)[-1]
        self.assertEqual(event["request_id"], response.headers["X-Request-ID"])
        self.assertEqual(event["status"], "under_review")
        self.client.post("/appeal", json={"content_id": "unknown", "reasoning": "Review"})
        self.assertEqual(audit.read_entries()[-1]["http_status"], 404)

    def test_rejection_storage_error_preserves_client_error(self):
        with patch.object(audit, "log_rejection", side_effect=OSError("disk full")), patch.object(service.app.logger, "exception") as logger:
            self.assertEqual(self.client.post("/submit", json={}).status_code, 400)
            logger.assert_called_once()

    def test_surrogate_creator_metadata_does_not_crash_error_logging(self):
        response = self.client.post("/submit", json={"text": "", "creator_id": "writer\ud800"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(audit.read_entries()[0]["creator_id"], "writer?")

    def test_unsupported_controls_rejected_before_model_with_audit(self):
        for control in ("\x00", "\x01", "\x1b", "\x7f"):
            response = self.client.post("/submit", json={
                "text": "A submitted draft." + control + "More writing follows.",
                "creator_id": "writer"})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json["error"], "unsupported_control_characters")
        self.model.assert_not_called()
        events = audit.read_entries()
        self.assertEqual(len(events), 4)
        self.assertTrue(all(e["event"] == "rejected" for e in events))
        self.assertTrue(all("content_id" not in e and "model_score" not in e for e in events))

    def test_tabs_newlines_and_carriage_returns_preserve_writing(self):
        text = "First\tline.\nSecond line.\rThird line."
        response = self.client.post("/submit", json={"text": text, "creator_id": "writer"})
        self.assertEqual(response.status_code, 200)
        self.model.assert_called_once_with(text)


class IsolatedLimiterTests(unittest.TestCase):
    def test_minute_day_scope_fallback_and_preinference_rejection(self):
        # Test limits 2/minute and 3/day exercise both windows without waiting
        # or loading weights. They are not the owner's production policy.
        code = '''
import tempfile
from pathlib import Path
from unittest.mock import patch
import config
config.RATE_LIMITING_ENABLED = True
config.RATE_LIMIT_PER_MINUTE = 2
config.RATE_LIMIT_PER_DAY = 3
with tempfile.TemporaryDirectory() as tmp:
    config.LOG_DIR = Path(tmp)
    config.AUDIT_LOG = Path(tmp)/"audit.jsonl"
    import app, audit, detector
    clock = [100000.0]
    with patch.object(detector, "model_signal", return_value=.6) as model, patch("time.time", side_effect=lambda: clock[0]):
        c = app.app.test_client()
        assert c.get('/health').json['rate_limiting']
        body = {'text': 'An ordinary test paragraph.', 'creator_id': 'writer'}
        assert [c.post('/submit',json=body).status_code for _ in range(3)] == [200,200,429]
        assert model.call_count == 2
        last = audit.read_entries()[-1]
        assert last['event'] == 'rejected' and last['reason'] == 'rate_limited'
        assert last['http_status'] == 429 and 'limit' in last
        assert 'model_score' not in last and 'content_id' not in last
        assert c.post('/submit',json={**body,'creator_id':'other'}).status_code == 200
        clock[0] += 61
        assert c.post('/submit',json=body).status_code == 200
        assert c.post('/submit',json=body).status_code == 429
        clock[0] += 86401
        assert c.post('/submit',json=body).status_code == 200
        app.limiter.reset()
        assert [c.post('/submit',json={}).status_code for _ in range(3)] == [400,400,429]
        assert c.post('/submit',json={},environ_base={'REMOTE_ADDR':'127.0.0.2'}).status_code == 400
        clock[0] += 61
        assert c.post('/submit',json={}).status_code == 400
        assert c.post('/submit',json={}).status_code == 429
        events = audit.read_entries()
        assert all(e.get('status') in ('decided','rejected') for e in events)
        print('Minute/day limits, creator isolation, IP fallback, 429 audit, and pre-inference blocking passed.')
'''
        completed = subprocess.run([sys.executable, "-c", code], cwd=config.ROOT,
                                   env={**os.environ, "AI201_RATE_LIMITS": "1"},
                                   capture_output=True, text=True, timeout=30)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
