"""Harness mechanics with explicitly synthetic fixtures; not acceptance results."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import app as service
import audit
import config
import detector
import run_attacks
import run_eval
import scenarios


def fixtures():
    return {
        "human": {"author": "UNIT TEST FIXTURE, NOT A VERIFIED COHORT", "public_coursework_use": True,
                  "authorship_attestation": "Synthetic harness fixture only; not evaluated as real human writing.",
                  "samples": [{"id": f"human-{i}", "source": "Unit-test fixture", "text": f"human fixture {i}. Several ordinary words for a mocked model."} for i in range(20)]},
        "ai": {"origin": "Synthetic unit-test fixture only", "samples": [
            {"id": f"ai-{i}", "source": "Unit-test fixture", "text": f"ai fixture {i}. Several ordinary words for a mocked model."} for i in range(10)]},
    }


class LocalClient:
    def __init__(self):
        self.client = service.app.test_client()

    def request(self, path, body=None, raw=None):
        if raw is not None:
            response = self.client.post(path, data=raw, content_type="application/json")
        elif body is not None:
            response = self.client.post(path, json=body)
        else:
            response = self.client.get(path)
        return {"status": response.status_code, "response": response.json,
                "request_id": response.headers.get("X-Request-ID")}

    def log(self):
        return audit.read_entries()


class HarnessTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for name, value in (("LOG_DIR", self.root), ("AUDIT_LOG", self.root / "audit.jsonl")):
            patcher = patch.object(config, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch.object(detector, "model_signal", side_effect=lambda text: .9 if text.startswith("ai fixture") else .1)
        patcher.start()
        self.addCleanup(patcher.stop)
        if hasattr(service.limiter, "enabled"):
            patcher = patch.object(service.limiter, "enabled", False)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.cohorts = fixtures()
        self.client = LocalClient()

    def write_manifests(self, cohorts):
        for name, value in cohorts.items():
            (self.root / f"{name}_samples.json").write_text(json.dumps(value))

    def test_missing_cohort_is_a_blocker_not_an_evaluation(self):
        with self.assertRaisesRegex(ValueError, "Missing"):
            scenarios.load_cohorts(self.root)
        self.assertFalse(config.AUDIT_LOG.exists())

    def test_exact_counts_and_permission_required(self):
        self.write_manifests(self.cohorts)
        self.assertEqual(len(scenarios.load_cohorts(self.root)["human"]["samples"]), 20)
        broken = copy.deepcopy(self.cohorts)
        broken["human"]["public_coursework_use"] = False
        self.write_manifests(broken)
        with self.assertRaisesRegex(ValueError, "permission"):
            scenarios.load_cohorts(self.root)
        broken = copy.deepcopy(self.cohorts)
        broken["human"]["samples"].pop()
        self.write_manifests(broken)
        with self.assertRaisesRegex(ValueError, "exactly 20"):
            scenarios.load_cohorts(self.root)

    def test_duplicate_and_undocumented_samples_rejected(self):
        broken = copy.deepcopy(self.cohorts)
        broken["ai"]["samples"][1]["text"] = broken["ai"]["samples"][0]["text"]
        self.write_manifests(broken)
        with self.assertRaisesRegex(ValueError, "unique"):
            scenarios.load_cohorts(self.root)
        broken = copy.deepcopy(self.cohorts)
        broken["human"]["samples"][0]["source"] = ""
        self.write_manifests(broken)
        with self.assertRaisesRegex(ValueError, "source"):
            scenarios.load_cohorts(self.root)

    def test_fingerprint_detects_data_changes_and_order(self):
        before = scenarios.fingerprint(scenarios.snapshot(self.cohorts))
        changed = copy.deepcopy(self.cohorts)
        changed["human"]["samples"].reverse()
        self.assertNotEqual(before, scenarios.fingerprint(scenarios.snapshot(changed)))

    def test_all_five_harness_paths_and_exact_case_counts(self):
        for criterion, count in ((1, 20), (3, 7), (4, 5), (5, 6)):
            result = run_eval.run_trial(criterion, self.client, self.cohorts, f"fixture-{criterion}")
            self.assertTrue(result["passed"], result)
            self.assertEqual(len(result["cases"]), count)
        result = run_eval.run_trial(2, self.client, self.cohorts, "separation")
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["human_cases"]), 10)
        self.assertEqual(len(result["ai_cases"]), 10)
        self.assertGreaterEqual(result["difference"], .20)

    def test_rate_limited_human_cannot_be_counted_as_a_negative(self):
        original = self.client.request
        first = [True]
        def request(*args, **kwargs):
            if first[0]:
                first[0] = False
                return {"status": 429, "response": {"error": "rate_limited"}}
            return original(*args, **kwargs)
        self.client.request = request
        result = run_eval.evaluate_false_positives(self.client, self.cohorts, "fixture")
        self.assertFalse(result["passed"])
        self.assertEqual(result["usable"], 19)
        self.assertEqual(result["denominator"], 20)

    def test_incomplete_separation_does_not_shrink_denominators(self):
        with patch.object(self.client, "request", return_value={"status": 503, "response": {"error": "unavailable"}}):
            result = run_eval.evaluate_separation(self.client, self.cohorts, "fixture")
        self.assertFalse(result["passed"])
        self.assertIsNone(result["difference"])
        self.assertEqual(len(result["human_cases"]), 10)
        self.assertEqual(len(result["ai_cases"]), 10)

    def test_429_is_not_accepted_as_input_validation(self):
        self.client.request = lambda *args, **kwargs: {"status": 429, "request_id": "none", "response": {"error": "rate_limited"}}
        result = run_eval.evaluate_invalid(self.client, "fixture")
        self.assertFalse(result["passed"])
        self.assertEqual(len(result["cases"]), 6)

    def test_missing_appeal_history_fails(self):
        self.client.log = lambda: []
        result = run_eval.evaluate_appeals(self.client, self.cohorts, "fixture")
        self.assertFalse(result["passed"])
        self.assertEqual(len(result["cases"]), 5)

    def test_attack_runner_records_nonobject_response_instead_of_crashing(self):
        response = Mock(status_code=200, text='[]', headers={"X-Request-ID": "fixture-id"})
        response.json.return_value = []
        evidence = {}
        with patch("requests.post", return_value=response):
            status, body, error = run_attacks.send("http://test.invalid", {"body": {}}, 1, evidence)
        self.assertEqual(status, 200)
        self.assertEqual(body, [])
        self.assertIn("not an object", error)
        self.assertEqual(evidence["request_id"], "fixture-id")
        self.assertEqual(evidence["response_text"], "[]")


if __name__ == "__main__":
    unittest.main()
