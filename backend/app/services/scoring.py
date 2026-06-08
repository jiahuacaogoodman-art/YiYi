from __future__ import annotations

from app.models.question import Question
from app.utils.text import normalize_answer, normalize_multi_answer


def is_answer_correct(question: Question, answer: str) -> bool:
    question_type = question.question_type
    correct_answer = question.correct_answer
    if question_type == "multiple_choice":
        return normalize_multi_answer(answer) == normalize_multi_answer(correct_answer)
    if question_type in {"single_choice", "true_false"}:
        return normalize_answer(answer) == normalize_answer(correct_answer)
    if question_type == "fill_blank":
        return answer.strip() == correct_answer.strip()
    if question_type == "short_answer":
        # 简答题先保留人工判分能力，默认精确匹配为正确。
        return answer.strip() == correct_answer.strip()
    return normalize_answer(answer) == normalize_answer(correct_answer)


def update_question_stats(question: Question, is_correct: bool) -> None:
    question.practice_count += 1
    if is_correct:
        question.correct_count += 1
    else:
        question.wrong_count += 1
    question.correct_rate = (
        round(question.correct_count / question.practice_count * 100, 2)
        if question.practice_count
        else 0
    )

