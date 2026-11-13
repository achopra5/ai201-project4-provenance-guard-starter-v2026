"""Record one structured event per Flask request without copying user inputs."""

import json
import uuid
from datetime import datetime, timezone
from threading import Lock
from time import perf_counter_ns

from flask import g, request

import config
import detector

_write_lock = Lock()
_submit_fields = ("guess", "confidence", "model_score", "style_score", "status")
_error_codes = frozenset({
    "content_not_found", "detector_unavailable", "input_too_large", "invalid_content_id",
    "invalid_creator_id", "invalid_json", "invalid_reasoning", "invalid_text",
    "rate_limited", "scoring_unavailable", "storage_unavailable",
    "unscorable_text", "unsupported_control_characters",
})


def install(app):
    @app.before_request
    def start_request():
        g.started_ns = perf_counter_ns()
        g.model_loaded_before = detector._model is not None

    @app.after_request
    def finish_request(response):
        duration_ms = (perf_counter_ns() - g.started_ns) / 1_000_000
        request_id = response.headers.get("X-Request-ID") or str(uuid.uuid4())
        response.headers["X-Request-ID"] = request_id
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "request_id": request_id,
            "method": request.method,
            "route": request.url_rule.rule if request.url_rule else None,
            "input_bytes": request.content_length,
            "http_status": response.status_code,
            "duration_ms": duration_ms,
            "model_loaded_before": g.model_loaded_before,
        }
        event.update(outcome(response))
        try:
            with _write_lock:
                config.REQUEST_LOG.parent.mkdir(parents=True, exist_ok=True)
                with config.REQUEST_LOG.open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(event, allow_nan=False) + "\n")
        except OSError:
            app.logger.exception("Could not persist HTTP telemetry")
        return response


def outcome(response):
    """Describe outcomes using service-owned fields only."""
    if response.status_code < 400:
        if request.method == "POST" and request.endpoint == "submit":
            body = response.get_json()
            return {"output": {field: body[field] for field in _submit_fields}}
        if request.method == "POST" and request.endpoint == "appeal":
            return {"output": {"status": response.get_json()["status"]}}
        return {"output": {"status": "ok"}}
    body = response.get_json(silent=True)
    code = body.get("error") if isinstance(body, dict) else None
    if isinstance(code, str) and code in _error_codes:
        return {"error": code}
    return {"error": f"http_{response.status_code}"}
