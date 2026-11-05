#!/usr/bin/env python3
"""
Provenance Guard — the web service.

    python app.py

Then, in another terminal:

    curl -X POST http://127.0.0.1:5000/ping \
      -H "Content-Type: application/json" \
      -d '{"message": "hello"}'

That's the example route. It works right now, before you've written anything.
**Leave it alone** — it's your control. When something breaks later, check that
`/ping` still answers: if it does, the problem is in your handler; if it
doesn't, it's the service itself.

Routes:

    POST /ping        the worked example. Already works. Don't edit it
    POST /submit      validate, score with two signals, label, log
    POST /appeal      record a review request, preserving the original decision
    GET  /log         the audit log. Already works
    GET  /health      is the service up, and is the model loaded
"""

import uuid

from werkzeug.exceptions import RequestEntityTooLarge

from flask import Flask, g, jsonify, request

import audit
import config
import detector
import scoring
import stylometry

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = config.MAX_REQUEST_BYTES


def error_response(error, message, status=400):
    return jsonify({"error": error, "message": message}), status


@app.errorhandler(RequestEntityTooLarge)
def request_too_large(exc):
    return error_response("input_too_large", "Request body exceeds 128 KiB.", 413)


def json_object():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, error_response("invalid_json", "Send a JSON object with Content-Type: application/json.")
    return payload, None


def string_field(payload, name, max_chars):
    value = payload.get(name)
    if not isinstance(value, str) or not value.strip():
        return error_response("invalid_" + name, f"{name} must be a nonblank string.")
    if len(value) > max_chars:
        return error_response("input_too_large", f"{name} must be at most {max_chars} characters.", 413)
    return None


# Unit 8 instrumentation adds context without changing validation or scoring.
@app.before_request
def identify_request():
    if request.path in ("/submit", "/appeal"):
        g.audit_request_id = str(uuid.uuid4())


def audit_context():
    return {"request_id": g.audit_request_id, "path": request.path,
            "method": request.method}


@app.after_request
def record_rejected_request(response):
    if request.path not in ("/submit", "/appeal"):
        return response
    response.headers["X-Request-ID"] = g.audit_request_id
    if response.status_code < 400:
        return response
    # Avoid retaining submitted writing or reparsing a rejected oversized body.
    try:
        payload = request.get_json(silent=True)
    except RequestEntityTooLarge:
        payload = None
    creator = payload.get("creator_id") if isinstance(payload, dict) else None
    if not isinstance(creator, str) or not creator.strip() or len(creator) > config.MAX_CREATOR_ID_CHARS:
        creator = "unknown"
    # JSON can contain lone surrogates; metadata must remain writable UTF-8.
    creator = creator.encode("utf-8", errors="replace").decode("utf-8")
    body = response.get_json(silent=True) or {}
    metadata = {**audit_context(), "http_status": response.status_code,
                "source_ip": request.remote_addr}
    if "limit" in body:
        metadata["limit"] = body["limit"]
    try:
        audit.log_rejection(creator_id=creator,
                            reason=body.get("error", "http_error"), **metadata)
    except OSError:
        app.logger.exception("Could not persist rejection audit event")
    return response


# ── Rate limiting — UNIT 8 ────────────────────────────────────────────────────
# Off until you turn it on. In unit 8, Milestone 1:
#
#   1. Set RATE_LIMITING_ENABLED = True in config.py (or AI201_RATE_LIMITS=1)
#   2. Choose your numbers there
#   3. Uncomment the @limiter.limit(...) line on /submit below
#
# The order doesn't matter. While limiting is off, that decorator is a no-op
# that quietly does nothing, so uncommenting it early costs you nothing — but
# it also means no 429 until you've done step 1.
#
# The storage backend is preconfigured, which stops Flask-Limiter printing a
# warning on every start. In-memory is right for one laptop and wrong for
# anything real — a restart forgets every count.

class _LimiterOff:
    """
    Stands in for the real limiter while rate limiting is off.

    It makes @limiter.limit(...) a decorator that returns the route
    untouched, so uncommenting the line before you flip the setting is
    harmless instead of a crash on startup.
    """

    def limit(self, *args, **kwargs):
        return lambda view: view


limiter = _LimiterOff()
if config.RATE_LIMITING_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    def rate_limit_key():
        """
        Who a request counts against.

        Falling back to the caller's address is the easy version. Unit 8's
        stretch asks about per-creator limits instead — and the difference
        matters: one script can look like a thousand callers, and one household
        can look like one.
        """
        payload = request.get_json(silent=True)
        # A body that parses as JSON but isn't an object — a bare list or
        # string — has no .get. Without this guard the key function raises
        # BEFORE the route runs, and a malformed request becomes a 500 that
        # looks like your handler crashed when your handler never ran.
        if not isinstance(payload, dict):
            return get_remote_address()
        creator = payload.get("creator_id")
        return creator if isinstance(creator, str) and creator.strip() else get_remote_address()

    limiter = Limiter(
        key_func=rate_limit_key,
        app=app,
        storage_uri=config.RATE_LIMIT_STORAGE,
        default_limits=[],
    )

    @app.errorhandler(429)
    def rate_limited(exc):
        """
        A rejected request still leaves a trace.

        ⚠️ An attack that shows up only as an absence is one you'll never find.
        """
        return jsonify({
            "error": "rate_limited",
            "message": "Too many submissions. Try again shortly.",
            "limit": str(exc.description),
        }), 429


# ── The worked example. Already works. Don't edit. ────────────────────────────

@app.post("/ping")
def ping():
    """
    Everything a route needs, in six lines.

    JSON arrives as a dict. You pull things out of it. You return a dict and
    the framework turns it into a response. That's the whole idea.
    """
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "you_sent": payload.get("message"),
        "service": "provenance-guard",
    })


@app.get("/health")
def health():
    """Is the service up, and has the model been downloaded yet?"""
    import detector

    loaded = detector._model is not None
    return jsonify({
        "ok": True,
        "detector_model": config.DETECTOR_MODEL,
        "detector_loaded": loaded,
        "rate_limiting": config.RATE_LIMITING_ENABLED,
        "log_entries": len(audit.read_entries()),
    })


# ── Unit 7 submission and appeal pipeline ─────────────────────────────────────

@app.post("/submit")
# @limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit():
    """Validate writing, combine two signals, label, and persist a decision."""
    payload, error = json_object()
    if error is not None:
        return error
    for name, maximum in (("text", config.MAX_TEXT_CHARS),
                          ("creator_id", config.MAX_CREATOR_ID_CHARS)):
        error = string_field(payload, name, maximum)
        if error is not None:
            return error

    try:
        model_score = detector.model_signal(payload["text"])
    except ValueError as exc:
        return error_response("unscorable_text", str(exc))
    except detector.DetectorUnavailable:
        return error_response("detector_unavailable", "The local detector is unavailable. Please try again later.", 503)

    style_score = stylometry.style_signal(payload["text"])
    try:
        confidence = scoring.combine_signals(model_score, style_score)
        guess, label = scoring.score_to_label(confidence)
    except ValueError:
        app.logger.exception("Invalid signal or scoring configuration")
        return error_response("scoring_unavailable", "The writing could not be scored. Please try again later.", 503)

    content_id = str(uuid.uuid4())
    try:
        audit.log_decision(content_id=content_id, creator_id=payload["creator_id"],
                           guess=guess, model_score=model_score,
                           style_score=style_score, combined_score=confidence,
                           label=label, http_status=200, **audit_context())
    except OSError:
        app.logger.exception("Could not persist submission decision")
        return error_response("storage_unavailable", "The decision could not be saved. Please try again later.", 503)
    return jsonify({"content_id": content_id, "guess": guess,
                    "confidence": confidence, "label": label,
                    "model_score": model_score, "style_score": style_score,
                    "status": "decided"})


@app.post("/appeal")
def appeal():
    """Append a writer's review request without overwriting the decision."""
    payload, error = json_object()
    if error is not None:
        return error
    for name, maximum in (("content_id", 36),
                          ("reasoning", config.MAX_REASONING_CHARS)):
        error = string_field(payload, name, maximum)
        if error is not None:
            return error
    try:
        decisions = [entry for entry in audit.entries_for(payload["content_id"])
                     if entry.get("status") == "decided"]
        if not decisions:
            return error_response("content_not_found", "No submission exists for that content_id.", 404)
        audit.log_appeal(content_id=payload["content_id"],
                         creator_id=decisions[0]["creator_id"],
                         reasoning=payload["reasoning"], http_status=200, **audit_context())
    except OSError:
        app.logger.exception("Could not read or persist an appeal")
        return error_response("storage_unavailable", "The review request could not be saved. Please try again later.", 503)
    return jsonify({"content_id": payload["content_id"], "status": "under_review",
                    "message": "Your review request was recorded. The writing is now under review."})


# ── Already works ─────────────────────────────────────────────────────────────

@app.get("/log")
def get_log():
    """
    The audit log, most recent last.

        curl "http://127.0.0.1:5000/log?limit=10"

    You need this in unit 8 to paste entries into your README, and you need it
    now to see whether your logging is actually working.
    """
    limit = request.args.get("limit", type=int)
    entries = audit.read_entries(limit=limit)
    return jsonify({"count": len(entries), "entries": entries})


def main():
    print(f"Provenance Guard on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:  {config.DETECTOR_MODEL}")
    print(f"  rate limiting:   {'ON' if config.RATE_LIMITING_ENABLED else 'off (unit 8)'}")
    print(f"  audit log:       {config.AUDIT_LOG}")
    print()
    print("Check it's alive:")
    print(f'  curl -X POST http://{config.HOST}:{config.PORT}/ping \\')
    print('    -H "Content-Type: application/json" \\')
    print("    -d '{\"message\": \"hello\"}'")
    print()
    # debug=True hands out an interactive debugger, so it's local-only — see config.py
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
