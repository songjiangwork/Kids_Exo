from dataclasses import dataclass
from typing import Any
import unicodedata

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
    if answer_type == "spelling_text":
        return _evaluate_spelling_text(evaluation_payload, submitted_answer)
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


def _evaluate_spelling_text(
    evaluation_payload: dict[str, Any],
    submitted_answer: str | int | dict[str, Any],
) -> EvaluationResult:
    submitted_text = _submitted_spelling_text(submitted_answer)
    expected_text = str(evaluation_payload["expected_text"])
    accepted_answers = tuple(
        str(item) for item in evaluation_payload.get("accepted_answers", ())
    ) or (expected_text,)
    case_sensitive = bool(evaluation_payload.get("case_sensitive", False))
    normalize_apostrophe = bool(evaluation_payload.get("normalize_apostrophe", True))

    normalized_submitted = _normalize_spelling_base(
        submitted_text,
        case_sensitive=case_sensitive,
        normalize_apostrophe=normalize_apostrophe,
    )
    normalized_accepted = tuple(
        _normalize_spelling_base(
            answer,
            case_sensitive=case_sensitive,
            normalize_apostrophe=normalize_apostrophe,
        )
        for answer in accepted_answers
    )
    is_correct = normalized_submitted in normalized_accepted
    checks = _spelling_checks(
        submitted_text,
        expected_text,
        case_sensitive=case_sensitive,
        normalize_apostrophe=normalize_apostrophe,
    )
    return EvaluationResult(
        normalized_answer={"text": submitted_text},
        is_correct=is_correct,
        detail={
            "answer_type": "spelling_text",
            "submitted_text": submitted_text,
            "expected_text": expected_text,
            "checks": checks,
            "feedback_code": "correct" if is_correct else _spelling_feedback_code(checks),
        },
    )


def _submitted_spelling_text(submitted_answer: str | int | dict[str, Any]) -> str:
    if isinstance(submitted_answer, dict):
        text = submitted_answer.get("text", "")
    else:
        text = submitted_answer
    return _collapse_internal_whitespace(str(text).strip())


def _normalize_spelling_base(
    value: str,
    *,
    case_sensitive: bool,
    normalize_apostrophe: bool,
) -> str:
    normalized = _collapse_internal_whitespace(value.strip())
    if normalize_apostrophe:
        normalized = normalized.replace("'", "’")
    if not case_sensitive:
        normalized = normalized.casefold()
    return normalized


def _spelling_checks(
    submitted_text: str,
    expected_text: str,
    *,
    case_sensitive: bool,
    normalize_apostrophe: bool,
) -> dict[str, bool]:
    exact_match = submitted_text == expected_text
    normalized_submitted = _normalize_spelling_base(
        submitted_text,
        case_sensitive=case_sensitive,
        normalize_apostrophe=normalize_apostrophe,
    )
    normalized_expected = _normalize_spelling_base(
        expected_text,
        case_sensitive=case_sensitive,
        normalize_apostrophe=normalize_apostrophe,
    )
    case_insensitive_match = _normalize_spelling_base(
        submitted_text,
        case_sensitive=False,
        normalize_apostrophe=normalize_apostrophe,
    ) == _normalize_spelling_base(
        expected_text,
        case_sensitive=False,
        normalize_apostrophe=normalize_apostrophe,
    )
    accent_insensitive_match = _strip_accents(normalized_submitted) == _strip_accents(
        normalized_expected
    )
    hyphen_normalized_match = normalized_submitted.replace("-", " ") == normalized_expected.replace(
        "-",
        " ",
    )
    apostrophe_normalized_match = _normalize_apostrophes(submitted_text).casefold() == (
        _normalize_apostrophes(expected_text).casefold()
    )
    return {
        "exact_match": exact_match,
        "case_insensitive_match": case_insensitive_match,
        "accent_insensitive_match": accent_insensitive_match,
        "hyphen_normalized_match": hyphen_normalized_match,
        "apostrophe_normalized_match": apostrophe_normalized_match,
        "normalized_match": normalized_submitted == normalized_expected,
    }


def _spelling_feedback_code(checks: dict[str, bool]) -> str:
    if checks["case_insensitive_match"]:
        return "case_mismatch"
    if checks["accent_insensitive_match"]:
        return "missing_or_wrong_accents"
    if checks["hyphen_normalized_match"]:
        return "hyphen_mismatch"
    if checks["apostrophe_normalized_match"]:
        return "apostrophe_mismatch"
    return "special_character_mismatch"


def _collapse_internal_whitespace(value: str) -> str:
    return " ".join(value.split())


def _normalize_apostrophes(value: str) -> str:
    return value.replace("'", "’")


def _strip_accents(value: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFD", value)
        if unicodedata.category(char) != "Mn"
    )
