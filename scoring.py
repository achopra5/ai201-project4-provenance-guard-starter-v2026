"""Approved equal-weight AI-likeness score and exhaustive reader labels."""

import math

import config

LABELS = {
    "human": (
        "This writing appears likely to be human-written. This is an automated "
        "estimate, not proof of authorship. The writer can request a review."
    ),
    "unsure": (
        "We cannot reliably determine how this writing was created. "
        "This label is not an accusation. The writer can request a review."
    ),
    "ai": (
        "This writing shows patterns associated with AI-generated text. This is "
        "an automated estimate, not proof of AI use. The writer can request a review."
    ),
}


def _validated_score(score: float) -> float:
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ValueError("Scores must be numbers in [0, 1].")
    if not math.isfinite(score) or not 0 <= score <= 1:
        raise ValueError("Scores must be finite and in [0, 1].")
    return float(score)


def combine_signals(model_score: float, style_score: float) -> float:
    """Return the configured weighted mean; reject invalid signals or weights.

    Approved weights are 0.5/0.5. A 0.9/0.1 split produces 0.5 (unsure).
    No disagreement penalty, calibrated probability, or misconduct inference.
    """
    model_score = _validated_score(model_score)
    style_score = _validated_score(style_score)
    weights = (config.WEIGHT_MODEL_SIGNAL, config.WEIGHT_STYLE_SIGNAL)
    if any(isinstance(w, bool) or not isinstance(w, (int, float))
           or not math.isfinite(w) or w < 0 for w in weights):
        raise ValueError("Signal weights must be finite, nonnegative numbers.")
    if not math.isclose(sum(weights), 1.0, rel_tol=0, abs_tol=1e-12):
        raise ValueError("Signal weights must sum to 1.")
    return min(1.0, max(0.0, weights[0] * model_score + weights[1] * style_score))


def score_to_label(score: float) -> tuple[str, str]:
    """Human through 0.20; unsure strictly between 0.20 and 0.85; AI from 0.85."""
    score = _validated_score(score)
    if not 0 <= config.HUMAN_THRESHOLD < config.AI_THRESHOLD <= 1:
        raise ValueError("Thresholds must satisfy 0 <= human < AI <= 1.")
    if score <= config.HUMAN_THRESHOLD:
        guess = "human"
    elif score >= config.AI_THRESHOLD:
        guess = "ai"
    else:
        guess = "unsure"
    return guess, LABELS[guess]


def label_ranges() -> list[tuple[str, str]]:
    """Explicit interval endpoints, including which boundary owns equality."""
    return [
        ("high-confidence human", f"0 <= score <= {config.HUMAN_THRESHOLD:.2f}"),
        ("unsure", f"{config.HUMAN_THRESHOLD:.2f} < score < {config.AI_THRESHOLD:.2f}"),
        ("high-confidence AI", f"{config.AI_THRESHOLD:.2f} <= score <= 1"),
    ]
