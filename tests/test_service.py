"""Fast, deterministic Unit 7 tests; never load weights or touch evidence logs."""

import importlib
import math
import tempfile
import threading
import types
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock, patch

import app as service
import audit
import config
import detector
import scoring
import stylometry


class ServiceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        for name, value in (("LOG_DIR", root), ("AUDIT_LOG", root / "audit.jsonl")):
            patcher = patch.object(config, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch.object(detector, "model_signal", return_value=0.7)
        self.model = patcher.start()
        self.addCleanup(patcher.stop)
        self.client = service.app.test_client()

    def submit(self, **changes):
        body = {"text": "A writer submits an ordinary paragraph. This paragraph has enough words to run the real surface measures without a short-text fallback.",
                "creator_id": "writer-123"}
        body.update(changes)
        return self.client.post("/submit", json=body)

    def test_ping_regression(self):
        response = self.client.post("/ping", json={"message": "hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"ok": True, "you_sent": "hello", "service": "provenance-guard"})

    def test_valid_submission_contract_and_persistence(self):
        response = self.submit()
        self.assertEqual(response.status_code, 200)
        body = response.json
        uuid.UUID(body["content_id"])
        self.assertEqual(body["status"], "decided")
        for name in ("confidence", "model_score", "style_score"):
            self.assertTrue(math.isfinite(body[name]))
            self.assertTrue(0 <= body[name] <= 1)
        self.assertAlmostEqual(body["confidence"], (body["model_score"] + body["style_score"]) / 2)
        self.assertEqual((body["guess"], body["label"]), scoring.score_to_label(body["confidence"]))
        self.assertEqual(audit.entries_for(body["content_id"])[0]["combined_score"], body["confidence"])
        self.assertTrue(config.AUDIT_LOG.exists())
        self.assertEqual(self.client.get("/log").json["count"], 1)
        self.assertEqual(self.client.get("/health").json["log_entries"], 1)
        self.model.assert_called_once()

    def test_unique_ids_and_repeated_submissions(self):
        ids = [self.submit().json["content_id"] for _ in range(5)]
        self.assertEqual(len(set(ids)), 5)
        self.assertEqual(self.model.call_count, 5)
        self.assertEqual(len(audit.read_entries()), 5)

    def test_approved_six_invalid_inputs(self):
        invalid = [{"creator_id": "w"}, {"text": "", "creator_id": "w"},
                   {"text": " \n\t", "creator_id": "w"}, {"text": 123, "creator_id": "w"},
                   {"text": "An ordinary paragraph."}]
        for body in invalid:
            with self.subTest(body=body):
                self.assertEqual(self.client.post("/submit", json=body).status_code, 400)
        self.assertEqual(self.client.post("/submit", data='{"text":', content_type="application/json").status_code, 400)
        self.model.assert_not_called()
        self.assertEqual(audit.read_entries(), [])

    def test_missing_nonobject_and_wrong_media_json(self):
        for raw in ("", "null", "[]", '"text"', "123", "false"):
            for route in ("/submit", "/appeal"):
                with self.subTest(raw=raw, route=route):
                    response = self.client.post(route, data=raw, content_type="application/json")
                    self.assertEqual(response.status_code, 400)
                    self.assertTrue(response.is_json)
        self.assertEqual(self.client.post("/submit", data='{"text":"x"}', content_type="text/plain").status_code, 400)
        self.model.assert_not_called()

    def test_invalid_creator_and_text_types(self):
        for creator in (None, "", " \n", 42, [], {}, True):
            with self.subTest(creator=creator):
                self.assertEqual(self.submit(creator_id=creator).status_code, 400)
        for text in (None, False, [], {}):
            with self.subTest(text=text):
                self.assertEqual(self.submit(text=text).status_code, 400)
        self.model.assert_not_called()

    def test_text_and_creator_length_limits(self):
        self.assertEqual(self.submit(text="x" * (config.MAX_TEXT_CHARS + 1)).status_code, 413)
        self.assertEqual(self.submit(creator_id="x" * (config.MAX_CREATOR_ID_CHARS + 1)).status_code, 413)
        self.model.assert_not_called()
        self.assertEqual(audit.read_entries(), [])

    def test_body_limit_is_json_and_precedes_inference(self):
        response = self.client.post("/submit", data="x" * (config.MAX_REQUEST_BYTES + 1), content_type="application/json")
        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json["error"], "input_too_large")
        self.model.assert_not_called()

    def test_exact_text_limit_is_accepted_without_rewriting(self):
        text = "word " * (config.MAX_TEXT_CHARS // 5)
        self.assertEqual(self.submit(text=text).status_code, 200)
        self.model.assert_called_once_with(text)

    def test_detector_short_input_error(self):
        self.model.side_effect = ValueError("Text is too short to score.")
        response = self.submit(text="a")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "unscorable_text")
        self.assertEqual(audit.read_entries(), [])

    def test_detector_unavailable_is_not_a_decision(self):
        self.model.side_effect = detector.DetectorUnavailable("local path should stay private")
        response = self.submit()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("local path", response.get_data(as_text=True))
        self.assertEqual(audit.read_entries(), [])

    def test_invalid_signal_is_not_a_decision(self):
        for score in (math.nan, math.inf, -0.1, 1.1):
            with self.subTest(score=score), patch.object(service.app.logger, "exception"):
                self.model.return_value = score
                self.assertEqual(self.submit().status_code, 503)
        self.assertEqual(audit.read_entries(), [])

    def test_storage_failure_does_not_report_success(self):
        with patch.object(audit, "log_decision", side_effect=OSError("disk full")), patch.object(service.app.logger, "exception"):
            self.assertEqual(self.submit().status_code, 503)

    def test_all_three_labels_through_route_with_controlled_signals(self):
        for score, expected in ((0.1, "human"), (0.5, "unsure"), (0.95, "ai")):
            self.model.return_value = score
            with patch.object(stylometry, "style_signal", return_value=score):
                response = self.submit()
                self.assertEqual(response.json["guess"], expected)
                self.assertEqual(response.json["label"], scoring.LABELS[expected])

    def test_five_appeals_record_exact_reasoning_and_status(self):
        for i in range(5):
            content_id = self.submit(creator_id=f"writer-{i}").json["content_id"]
            before = audit.entries_for(content_id)[0]
            reasoning = f"  I wrote piece {i} myself. Please review it.  "
            response = self.client.post("/appeal", json={"content_id": content_id, "reasoning": reasoning})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["status"], "under_review")
            events = audit.entries_for(content_id)
            self.assertEqual(events[0], before)
            self.assertEqual(events[-1]["status"], "under_review")
            self.assertEqual(events[-1]["reasoning"], reasoning)
            self.assertEqual(events[-1]["creator_id"], f"writer-{i}")
        entries = self.client.get("/log").json["entries"]
        self.assertEqual(len(entries), 10)
        self.assertEqual(sum(e.get("event") == "appeal" for e in entries), 5)

    def test_unknown_id_and_appeal_without_decision(self):
        for content_id in (str(uuid.uuid4()), "not-a-content-id"):
            self.assertEqual(self.client.post("/appeal", json={"content_id": content_id, "reasoning": "Please review."}).status_code, 404)
        audit.log_appeal("orphan", "w", "Not a decision")
        self.assertEqual(self.client.post("/appeal", json={"content_id": "orphan", "reasoning": "Review."}).status_code, 404)

    def test_invalid_appeal_fields(self):
        content_id = self.submit().json["content_id"]
        for body in ({}, {"content_id": content_id}, {"reasoning": "Review"},
                     {"content_id": content_id, "reasoning": " "},
                     {"content_id": content_id, "reasoning": 3},
                     {"content_id": [], "reasoning": "Review"}):
            with self.subTest(body=body):
                self.assertEqual(self.client.post("/appeal", json=body).status_code, 400)
        self.assertEqual(len(audit.read_entries()), 1)

    def test_appeal_reason_length_limit(self):
        content_id = self.submit().json["content_id"]
        response = self.client.post("/appeal", json={"content_id": content_id, "reasoning": "x" * (config.MAX_REASONING_CHARS + 1)})
        self.assertEqual(response.status_code, 413)
        self.assertEqual(len(audit.read_entries()), 1)

    def test_repeated_appeals_append_and_survive_module_reload(self):
        content_id = self.submit().json["content_id"]
        for reason in ("First request", "Additional evidence"):
            self.assertEqual(self.client.post("/appeal", json={"content_id": content_id, "reasoning": reason}).status_code, 200)
        importlib.reload(audit)
        events = audit.entries_for(content_id)
        self.assertEqual(len(events), 3)
        self.assertEqual(events[-1]["status"], "under_review")
        self.assertEqual(self.client.get("/log?limit=1").json["entries"], events[-1:])

    def test_appeal_storage_failure(self):
        content_id = self.submit().json["content_id"]
        with patch.object(audit, "log_appeal", side_effect=OSError("disk full")), patch.object(service.app.logger, "exception"):
            self.assertEqual(self.client.post("/appeal", json={"content_id": content_id, "reasoning": "Review"}).status_code, 503)
        self.assertEqual(len(audit.read_entries()), 1)


class SignalTests(unittest.TestCase):
    def test_known_surface_measures(self):
        self.assertEqual(stylometry.sentence_length_spread("One. Two three four."), 0.5)
        self.assertEqual(stylometry.type_token_ratio("Word word OTHER"), 2 / 3)
        self.assertEqual(stylometry.punctuation_density("a,b!"), 0.5)
        self.assertEqual(stylometry.punctuation_density("a—b…"), 0.5)
        self.assertEqual(stylometry.words("Café café don't DON’T"), ["café", "café", "don't", "don’t"])

    def test_surface_edges_are_finite_and_bounded(self):
        for text in ("", " \n\t", "One.", "word " * 10000, "!!! — …", "猫。", "café! " * 100):
            with self.subTest(text=text[:40]):
                for measure in (stylometry.sentence_length_spread, stylometry.type_token_ratio, stylometry.punctuation_density, stylometry.style_signal):
                    self.assertTrue(math.isfinite(measure(text)))
                for measure in (stylometry.type_token_ratio, stylometry.punctuation_density, stylometry.style_signal):
                    self.assertTrue(0 <= measure(text) <= 1)
        self.assertEqual(stylometry.style_signal("Too short."), 0.5)
        self.assertEqual(stylometry.style_signal("word " * 30), 0.5)

    def test_style_varies(self):
        regular = ("The writing is clear and the writing is simple. " * 10)
        varied = "Wait! Copper, lilac, pomegranate; unfamiliar voices crossed rain-darkened windows—why would anyone wait here, counting broken umbrellas? Go."
        self.assertGreater(stylometry.style_signal(regular), stylometry.style_signal(varied))

    def test_score_combination_extremes_and_disagreement(self):
        self.assertEqual(scoring.combine_signals(0, 0), 0)
        self.assertEqual(scoring.combine_signals(1, 1), 1)
        self.assertEqual(scoring.combine_signals(.9, .1), .5)
        self.assertAlmostEqual(scoring.combine_signals(.2, .6), .4)

    def test_invalid_scores_rejected(self):
        for value in (math.nan, math.inf, -math.inf, -0.1, 1.1, "0.5", None, True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    scoring.combine_signals(value, .5)
                with self.assertRaises(ValueError):
                    scoring.combine_signals(.5, value)
                with self.assertRaises(ValueError):
                    scoring.score_to_label(value)

    def test_bad_weights_and_thresholds_rejected(self):
        for weight in (math.nan, -1, .7, "x"):
            with patch.object(config, "WEIGHT_MODEL_SIGNAL", weight), self.assertRaises(ValueError):
                scoring.combine_signals(.5, .5)
        with patch.object(config, "HUMAN_THRESHOLD", .9), self.assertRaises(ValueError):
            scoring.score_to_label(.5)

    def test_seven_owner_criterion_scores(self):
        values = [0, .20, .200001, .50, .849999, .85, 1]
        expected = ["human", "human", "unsure", "unsure", "unsure", "ai", "ai"]
        for value, guess in zip(values, expected):
            with self.subTest(value=value):
                self.assertEqual(scoring.score_to_label(value), (guess, scoring.LABELS[guess]))
        self.assertEqual(set(expected), {"human", "unsure", "ai"})

    def test_adjacent_float_boundaries_and_every_thousandth(self):
        self.assertEqual(scoring.score_to_label(math.nextafter(.2, 1))[0], "unsure")
        self.assertEqual(scoring.score_to_label(math.nextafter(.2, 0))[0], "human")
        self.assertEqual(scoring.score_to_label(math.nextafter(.85, 0))[0], "unsure")
        self.assertEqual(scoring.score_to_label(math.nextafter(.85, 1))[0], "ai")
        for i in range(1001):
            self.assertIn(scoring.score_to_label(i / 1000)[0], scoring.LABELS)
        self.assertIn("< score <", scoring.label_ranges()[1][1])

    def test_model_load_once_with_concurrent_requests(self):
        fake_model = Mock()
        fake_tokenizer = Mock()
        model_factory = Mock(return_value=fake_model)
        tokenizer_factory = Mock(return_value=fake_tokenizer)
        module = types.SimpleNamespace(
            AutoModelForCausalLM=types.SimpleNamespace(from_pretrained=model_factory),
            AutoTokenizer=types.SimpleNamespace(from_pretrained=tokenizer_factory))
        barrier = threading.Barrier(8)
        def load():
            barrier.wait(timeout=5)
            return detector._load()
        with patch.object(detector, "_model", None), patch.object(detector, "_tokenizer", None), patch.dict("sys.modules", {"transformers": module, "torch": types.ModuleType("torch")}):
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda _: load(), range(8)))
            self.assertTrue(all(pair == (fake_model, fake_tokenizer) for pair in results))
            model_factory.assert_called_once_with(config.DETECTOR_MODEL)
            tokenizer_factory.assert_called_once_with(config.DETECTOR_MODEL)
            fake_model.eval.assert_called_once()

    def test_failed_model_load_does_not_publish_partial_state(self):
        module = types.SimpleNamespace(
            AutoModelForCausalLM=types.SimpleNamespace(from_pretrained=Mock(side_effect=OSError("missing"))),
            AutoTokenizer=types.SimpleNamespace(from_pretrained=Mock(return_value=object())))
        with patch.object(detector, "_model", None), patch.object(detector, "_tokenizer", None), patch.dict("sys.modules", {"transformers": module, "torch": types.ModuleType("torch")}):
            with self.assertRaises(detector.DetectorUnavailable):
                detector._load()
            self.assertIsNone(detector._model)
            self.assertIsNone(detector._tokenizer)


if __name__ == "__main__":
    unittest.main()
