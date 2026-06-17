from typing import Any, Mapping, TypeAlias


AnswerValue: TypeAlias = int | str | dict[str, Any] | None

TEXT_ANSWER_TYPES = {"text_exact", "text_case_insensitive"}


def expected_answer_value(
    answer_type: str | None,
    evaluation_payload: Mapping[str, Any] | None,
    legacy_expected_answer: int | None = None,
) -> AnswerValue:
    payload = evaluation_payload or {}
    if answer_type in {"integer_exact", "signed_integer_exact"} and "expected_value" in payload:
        return payload["expected_value"]
    if answer_type == "multiple_choice_index" and "expected_index" in payload:
        return payload["expected_index"]
    if answer_type in TEXT_ANSWER_TYPES and "expected_text" in payload:
        return str(payload["expected_text"])
    if answer_type == "spelling_text" and "expected_text" in payload:
        return {"text": str(payload["expected_text"])}
    if answer_type == "structured_word_problem" and "expected_values" in payload:
        return {"values": dict(payload["expected_values"])}
    return legacy_expected_answer


def expected_answer_value_for_question(question) -> AnswerValue:
    return expected_answer_value(
        getattr(question, "answer_type", None),
        getattr(question, "evaluation_payload", None),
        getattr(question, "expected_answer", None),
    )


def submitted_answer_value_for_attempt(attempt) -> AnswerValue:
    payload = getattr(attempt, "normalized_payload", None) or {}
    if "value" in payload:
        return payload["value"]
    return getattr(attempt, "normalized_answer", None)


def choice_label(value: AnswerValue, choices: tuple[str, ...]) -> str | None:
    if isinstance(value, int) and 1 <= value <= len(choices):
        return choices[value - 1]
    return None


def answer_display(
    value: AnswerValue,
    *,
    choices: tuple[str, ...] = (),
    answer_type: str | None = None,
) -> str | None:
    if answer_type == "multiple_choice_index":
        selected_choice = choice_label(value, choices)
        if selected_choice is not None:
            return selected_choice
    if value is None:
        return None
    if isinstance(value, dict):
        text = value.get("text")
        if isinstance(text, str):
            return text
        values = value.get("values")
        if isinstance(values, dict):
            return ", ".join(f"{_humanize_key(key)}: {item}" for key, item in values.items())
        return str(value)
    return str(value)


def value_for_legacy_integer_column(value: AnswerValue) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _humanize_key(key: str) -> str:
    return str(key).replace("_count", "").replace("_", " ").title()
