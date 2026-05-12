from __future__ import annotations
from app.models.task import AnswerTypeEnum


def normalize_answer(answer: str, answer_type: AnswerTypeEnum) -> str:
    answer = answer.strip()

    if answer_type == AnswerTypeEnum.numeric:
        answer = answer.replace(",", ".").replace(" ", "")
        try:
            return f"{float(answer):g}"
        except ValueError:
            return answer.lower()

    if answer_type == AnswerTypeEnum.multiple_choice:
        return answer.upper().strip()

    return answer.lower().strip()