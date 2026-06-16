from dataclasses import dataclass
from typing import Any

from kids_exo.online.answer_display import AnswerValue


@dataclass(frozen=True)
class EvaluationResult:
    normalized_answer: AnswerValue
    is_correct: bool
    detail: dict[str, Any]


def evaluate_answer(
    answer_type: str,
    evaluation_payload: dict[str, Any],
    submitted_answer: str | int | dict[str, Any],
) -> EvaluationResult:
    if answer_type in {"integer_exact", "signed_integer_exact"}:
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
    if answer_type == "text_exact":
        expected_text = str(evaluation_payload["expected_text"])
        normalized_answer = submitted_answer.strip()
        return EvaluationResult(
            normalized_answer=normalized_answer,
            is_correct=normalized_answer == expected_text,
            detail={"answer_type": answer_type, "expected_text": expected_text},
        )
    if answer_type == "text_case_insensitive":
        expected_text = str(evaluation_payload["expected_text"])
        normalized_answer = submitted_answer.strip()
        return EvaluationResult(
            normalized_answer=normalized_answer,
            is_correct=normalized_answer.casefold() == expected_text.casefold(),
            detail={
                "answer_type": answer_type,
                "expected_text": expected_text,
                "comparison_text": expected_text.casefold(),
            },
        )
    if answer_type == "structured_word_problem":
        return _evaluate_structured_word_problem(evaluation_payload, submitted_answer)
    raise ValueError(f"Unsupported answer_type: {answer_type}")


def _parse_integer_answer(submitted_answer: str | int) -> int:
    try:
        if isinstance(submitted_answer, bool):
            raise ValueError
        if isinstance(submitted_answer, int):
            return submitted_answer
        return int(submitted_answer.strip())
    except ValueError as exc:
        raise ValueError("Submitted answer must be an integer") from exc


def _evaluate_structured_word_problem(
    evaluation_payload: dict[str, Any],
    submitted_answer: str | int | dict[str, Any],
) -> EvaluationResult:
    if not isinstance(submitted_answer, dict):
        raise ValueError("Submitted answer must be a structured object")
    submitted_values = submitted_answer.get("values")
    if not isinstance(submitted_values, dict):
        raise ValueError("Submitted answer must include values")

    expected_values = evaluation_payload.get("expected_values", {})
    field_rules = evaluation_payload.get("field_rules", {})
    if not isinstance(expected_values, dict):
        raise ValueError("Structured expected_values must be an object")
    if not isinstance(field_rules, dict):
        raise ValueError("Structured field_rules must be an object")

    normalized_values: dict[str, Any] = {}
    field_results: dict[str, dict[str, Any]] = {}
    all_correct = True
    for key, expected in expected_values.items():
        if key not in submitted_values or submitted_values[key] in (None, ""):
            raise ValueError(f"Missing required answer field: {key}")
        rule = field_rules.get(key, {"value_type": "integer"})
        normalized = _normalize_structured_field(key, submitted_values[key], rule)
        normalized_values[key] = normalized
        is_correct = normalized == expected
        all_correct = all_correct and is_correct
        field_results[key] = {
            "submitted": normalized,
            "expected": expected,
            "is_correct": is_correct,
        }

    work = submitted_answer.get("work", "")
    if work is None:
        work = ""
    work = str(work).strip()
    return EvaluationResult(
        normalized_answer={"values": normalized_values, "work": work},
        is_correct=all_correct,
        detail={
            "answer_type": "structured_word_problem",
            "field_results": field_results,
            "work_submitted": bool(work),
        },
    )


def _normalize_structured_field(key: str, value: Any, rule: dict[str, Any]) -> Any:
    value_type = rule.get("value_type", "integer")
    if value_type == "integer":
        try:
            if isinstance(value, bool):
                raise ValueError
            if isinstance(value, int):
                return value
            text = str(value).strip()
            if not text:
                raise ValueError
            return int(text)
        except ValueError as exc:
            raise ValueError(f"Answer field {key} must be an integer") from exc
    raise ValueError(f"Unsupported structured answer field type: {value_type}")
