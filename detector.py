"""
Signal one: the model signal.

This signal uses a local language model's next-token probabilities, rather than
surface counts, to ask: **how predictable is this text?** It does not establish
meaning or authorship.

The heuristic is that generated writing may be predictable to a language model.
Human writing can be predictable too; unusual AI writing can surprise a model.
This is a rough signal, not a general test of who wrote a passage.

The measure is called **perplexity**. Low perplexity means "I could have
guessed this"; high perplexity means "that surprised me". This module turns
that into a 0–1 score where **higher means more likely AI**.

    from detector import model_signal
    score = model_signal("some text")     # 0.0 human-ish … 1.0 AI-ish

Everything runs locally. No account, no key, no card.

⚠️ **The blind spot, which you have to name in Milestone 1.**

Predictability is not the same thing as authorship. What this signal actually
rewards is **common words in short, ordinary sentences** — and plenty of real
people write that way.

Someone writing in a second language, sticking to vocabulary they're sure of.
A younger writer. Anyone writing plainly on purpose. Measured against gpt2,
writing like that scores about as machine-like as machine writing does.

The reverse trips people up too: dense, ornate prose full of rare words often
scores as *human* on this signal, because rare words are exactly what a
language model fails to predict. Formality on its own doesn't decide it.

So the writers this signal is most likely to accuse are the ones with the
least room to argue back. That is structural rather than a bug you can fix,
and it is the person Milestone 1 asks you to follow through your service.

Don't take that on trust — it's a claim you can check. Milestone 4 has you run
four calibration inputs. Add a plainly-written human paragraph to them and see
for yourself where it lands.
"""

import math
import threading

import config

_model = None
_tokenizer = None
_load_lock = threading.Lock()


class DetectorUnavailable(RuntimeError):
    """The model couldn't be loaded — no download yet, or no disk."""


def _load():
    """Load the model once and keep it. First call downloads ~550 MB."""
    global _model, _tokenizer
    if _model is not None:
        return _model, _tokenizer

    with _load_lock:
        if _model is not None:
            return _model, _tokenizer
        try:
            import torch  # noqa: F401
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise DetectorUnavailable(
                f"transformers or torch isn't installed ({exc}).\n"
                f"Run: pip install -r requirements.txt"
            ) from exc

        try:
            tokenizer = AutoTokenizer.from_pretrained(config.DETECTOR_MODEL)
            model = AutoModelForCausalLM.from_pretrained(config.DETECTOR_MODEL)
            model.eval()
        except Exception as exc:  # noqa: BLE001
            raise DetectorUnavailable(
                f"Couldn't load '{config.DETECTOR_MODEL}': {exc}\n"
                f"The first run downloads about 550 MB — check your connection and "
                f"that you have disk space free."
            ) from exc

        # Publish only a fully loaded pair, so another request cannot observe
        # a half-initialized model or trigger a second simultaneous load.
        _tokenizer, _model = tokenizer, model
        return _model, _tokenizer


def perplexity(text: str) -> float:
    """
    How surprised the model is by this text. Lower means more predictable.

    Returns a positive number. Typical values land roughly between 10 and 200,
    but that range shifts with topic and length, which is one reason the raw
    number isn't what you score on.
    """
    model, tokenizer = _load()

    import torch

    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=config.DETECTOR_MAX_TOKENS,
    )
    input_ids = encoded["input_ids"]

    # Two tokens is not enough to be surprised by anything.
    if input_ids.shape[1] < 3:
        raise ValueError("Text is too short to score — a few sentences at least.")

    with torch.no_grad():
        output = model(input_ids, labels=input_ids)

    # The model's loss here IS mean negative log-likelihood per token.
    loss = output.loss.item()
    if not math.isfinite(loss):
        raise DetectorUnavailable("The local model returned a non-finite loss.")
    try:
        return float(math.exp(loss))
    except OverflowError as exc:
        raise DetectorUnavailable("The local model returned an unscorable loss.") from exc


def model_signal(text: str) -> float:
    """
    The signal, as a 0–1 score. **Higher means more likely AI.**

    Perplexity is unbounded and roughly log-distributed, so it gets squashed
    onto 0–1 rather than clipped. The midpoint below is the perplexity that
    maps to 0.5 on this heuristic scale, not a probability of authorship.

    You may want to move that midpoint once you've run the four calibration
    inputs in Milestone 4 and seen what your own text actually scores. If you
    do, say so in your README: it's a scoring decision, not a detail.
    """
    ppl = perplexity(text)

    midpoint = 45.0    # perplexity that scores 0.5
    steepness = 1.6    # how sharply the score moves either side of it

    # Logistic on log-perplexity. Low perplexity -> high AI score.
    score = 1.0 / (1.0 + (ppl / midpoint) ** steepness)
    return round(min(max(score, 0.0), 1.0), 4)


def warm_up() -> str:
    """Load the model without scoring anything. Run this before class."""
    _load()
    return f"{config.DETECTOR_MODEL} loaded and ready."


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = (
            "The implementation of the proposed framework requires careful "
            "consideration of several key factors. First, it is important to "
            "note that the system must be able to handle a wide variety of "
            "different inputs. Additionally, the overall performance of the "
            "solution depends on a number of important variables."
        )
        print("(no text given — scoring a sample)\n")

    print(f"Loading {config.DETECTOR_MODEL} (first run downloads ~550 MB)…")
    print(f"perplexity     {perplexity(text):.1f}")
    print(f"model_signal   {model_signal(text):.4f}   (higher = more likely AI)")
