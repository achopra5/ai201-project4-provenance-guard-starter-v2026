"""Surface-form heuristics, independent of GPT-2 probabilities.

Higher style scores mean more AI-like patterns, never proof of authorship.
The fixed normalization and limitations are recorded in docs/policy.md.
"""

import re
import statistics
import unicodedata


def sentences(text: str) -> list[str]:
    """Rough sentence split; abbreviations, poetry, and missing spaces can mislead it."""
    return [part for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]


def words(text: str) -> list[str]:
    """Unicode alphanumeric tokens; retain internal apostrophes, case insensitive."""
    return re.findall(r"[^\W_]+(?:['’][^\W_]+)*", text.casefold())


def sentence_length_spread(text: str) -> float:
    """Population coefficient of variation; zero when fewer than two lengths exist."""
    lengths = [len(words(sentence)) for sentence in sentences(text)]
    lengths = [length for length in lengths if length]
    if len(lengths) < 2:
        return 0.0
    return statistics.pstdev(lengths) / statistics.mean(lengths)


def type_token_ratio(text: str) -> float:
    """Distinct lowercase word tokens / total tokens; zero for no words.

    This ratio is length dependent: repeated common words lower it in long text.
    """
    tokens = words(text)
    return len(set(tokens)) / len(tokens) if tokens else 0.0


def punctuation_density(text: str) -> float:
    """Unicode punctuation characters / all characters, including whitespace."""
    return sum(unicodedata.category(char).startswith("P") for char in text) / len(text) if text else 0.0


def style_signal(text: str) -> float:
    """Average of three bounded, AI-oriented measures with fixed normalization.

    Low spread, low word variety, and sparse punctuation increase the score.
    Fewer than 20 words or two nonempty sentences gives neutral 0.5 because
    little evidence is available. This is not a statistical confidence estimate.
    """
    if len(words(text)) < 20 or sum(bool(words(s)) for s in sentences(text)) < 2:
        return 0.5
    regularity = 1.0 - min(sentence_length_spread(text), 1.0)
    repetition = 1.0 - type_token_ratio(text)
    sparse_punctuation = 1.0 - min(punctuation_density(text) / 0.10, 1.0)
    return (regularity + repetition + sparse_punctuation) / 3.0


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )
    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    for measure in (sentence_length_spread, type_token_ratio, punctuation_density, style_signal):
        print(f"{measure.__name__:24} {measure(text):.6f}")
