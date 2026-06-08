from __future__ import annotations

from difflib import SequenceMatcher


def normalize_answer(answer: str) -> str:
    return answer.strip().replace("，", ",").replace("、", ",").upper()


def normalize_multi_answer(answer: str) -> str:
    text = normalize_answer(answer)
    if "," in text:
        parts = [part.strip() for part in text.split(",") if part.strip()]
    else:
        parts = list(text)
    return ",".join(sorted(set(parts)))


def similarity(a: str, b: str) -> float:
    compact_a = "".join(a.split())
    compact_b = "".join(b.split())
    if not compact_a or not compact_b:
        return 0
    return SequenceMatcher(None, compact_a, compact_b).ratio()

