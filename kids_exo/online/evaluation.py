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
    checks = _structured_diagnostic_checks(
        normalized_values,
        expected_values,
        evaluation_payload.get("diagnostic_checks"),
    )
    return EvaluationResult(
        normalized_answer={"values": normalized_values, "work": work},
        is_correct=all_correct,
        detail={
            "answer_type": "structured_word_problem",
            "field_results": field_results,
            "checks": checks,
            "feedback_code": _structured_feedback_code(all_correct, field_results, checks),
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


def _structured_diagnostic_checks(
    normalized_values: dict[str, Any],
    expected_values: dict[str, Any],
    diagnostic_checks: Any,
) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "values_swapped": _values_are_swapped(normalized_values, expected_values),
    }
    if not isinstance(diagnostic_checks, dict):
        return checks

    if "total_count" in diagnostic_checks:
        submitted_total_count = sum(
            value for value in normalized_values.values()
            if isinstance(value, int) and not isinstance(value, bool)
        )
        expected_total_count = diagnostic_checks["total_count"]
        checks.update(
            {
                "submitted_total_count": submitted_total_count,
                "expected_total_count": expected_total_count,
                "total_count_matches": submitted_total_count == expected_total_count,
            }
        )

    unit_values = diagnostic_checks.get("unit_values")
    if isinstance(unit_values, dict) and "total_units" in diagnostic_checks:
        submitted_total_units = sum(
            normalized_values[key] * unit_value
            for key, unit_value in unit_values.items()
            if key in normalized_values
            and isinstance(normalized_values[key], int)
            and not isinstance(normalized_values[key], bool)
            and isinstance(unit_value, int)
            and not isinstance(unit_value, bool)
        )
        expected_total_units = diagnostic_checks["total_units"]
        checks.update(
            {
                "submitted_total_units": submitted_total_units,
                "expected_total_units": expected_total_units,
                "total_units_matches": submitted_total_units == expected_total_units,
                "unit_label": diagnostic_checks.get("unit_label"),
            }
        )
    return checks


def _values_are_swapped(
    normalized_values: dict[str, Any],
    expected_values: dict[str, Any],
) -> bool:
    keys = list(expected_values.keys())
    if len(keys) != 2:
        return False
    first, second = keys
    return (
        normalized_values.get(first) == expected_values.get(second)
        and normalized_values.get(second) == expected_values.get(first)
        and expected_values.get(first) != expected_values.get(second)
    )


def _structured_feedback_code(
    is_correct: bool,
    field_results: dict[str, dict[str, Any]],
    checks: dict[str, Any],
) -> str:
    if is_correct:
        return "correct"
    if checks.get("values_swapped") is True:
        return "values_swapped"
    if checks.get("total_count_matches") is False:
        return "total_count_mismatch"
    if checks.get("total_units_matches") is False:
        return "total_units_mismatch"
    if any(not result.get("is_correct") for result in field_results.values()):
        return "field_value_mismatch"
    return "field_value_mismatch"
