from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EvaluationResult:
    normalized_answer: int | str | dict[str, Any]
    is_correct: bool
    detail: dict[str, Any]


def evaluate_answer(
    answer_type: str,
    evaluation_payload: dict[str, Any],
    submitted_answer: str,
) -> EvaluationResult:
    if answer_type == "integer_exact":
        expected_value = int(evaluation_payload["expected_value"])
        normalized_answer = _parse_integer_answer(submitted_answer)
        return EvaluationResult(
            normalized_answer=normalized_answer,
            is_correct=normalized_answer == expected_value,
            detail={"answer_type": answer_type, "expected_value": expected_value},
        )
    if answer_type == "multiple_choice_index":
        expected_index = int(evaluation_payload["expected_index"])
        normalized_answer = _parse_integer_answer(submitted_answer)
        return EvaluationResult(
            normalized_answer=normalized_answer,
            is_correct=normalized_answer == expected_index,
            detail={"answer_type": answer_type, "expected_index": expected_index},
        )
    raise ValueError(f"Unsupported answer_type: {answer_type}")


def _parse_integer_answer(submitted_answer: str) -> int:
    try:
        return int(submitted_answer.strip())
    except ValueError as exc:
        raise ValueError("Submitted answer must be an integer") from exc
