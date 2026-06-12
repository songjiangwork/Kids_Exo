import random

from kids_exo.localization import LocalizedPresentation, LocalizedText
from kids_exo.online.catalog import get_online_plugin
from kids_exo.online.models import OnlineQuestionSnapshot, PracticeSessionSnapshot
from kids_exo.plugins.integer_signed_addition_subtraction.settings import load_settings


OPERATION_LABELS = {
    "addition": "addition",
    "subtraction": "subtraction",
}


def create_signed_integer_session(request) -> PracticeSessionSnapshot:
    descriptor = get_online_plugin(request.plugin)
    settings = load_settings(request.plugin_settings)
    rng = random.Random(request.seed)
    operation_plan = [
        settings.operations[index % len(settings.operations)]
        for index in range(request.question_count)
    ]
    rng.shuffle(operation_plan)
    questions = tuple(
        _question_for_operation(operation, position, settings.absolute_limit, rng)
        for position, operation in enumerate(operation_plan, start=1)
    )
    return PracticeSessionSnapshot(
        plugin=request.plugin,
        subject=descriptor.subject,
        category=descriptor.category,
        skill=descriptor.title,
        plugin_settings={
            "number_range": [settings.number_range],
            "operations": list(settings.operations),
        },
        requested_locale=request.requested_locale,
        feedback_mode=request.feedback_mode,
        show_timer=request.show_timer,
        seed=request.seed,
        presentation=LocalizedPresentation(
            heading=LocalizedText("Signed Integer Addition and Subtraction", "en-CA", False),
            instructions=(
                LocalizedText("Add or subtract positive and negative integers.", "en-CA", False),
                LocalizedText("Use parentheses to notice negative numbers in the expression.", "en-CA", False),
            ),
        ),
        questions=questions,
    )


def _question_for_operation(
    operation: str,
    position: int,
    absolute_limit: int,
    rng: random.Random,
) -> OnlineQuestionSnapshot:
    left = _random_non_zero_integer(absolute_limit, rng)
    right = _random_non_zero_integer(absolute_limit, rng)
    if operation == "addition":
        expected_answer = left + right
        prompt = f"{left} + {_format_operand(right)} = __________"
    else:
        expected_answer = left - right
        prompt = f"{left} - {_format_operand(right)} = __________"
    return OnlineQuestionSnapshot(
        identifier=f"question-{position}",
        prompt=prompt,
        strategy=OPERATION_LABELS[operation],
        skill_tags=("integer_arithmetic", "signed_integers", operation),
        expected_answer=expected_answer,
        renderer_type="numeric_answer",
        answer_type="signed_integer_exact",
        evaluation_payload={"expected_value": expected_answer},
        prompt_payload={"display_text": prompt},
        public_payload={"tools": {"scratch_pad": True, "audio": False}},
    )


def _random_non_zero_integer(absolute_limit: int, rng: random.Random) -> int:
    value = 0
    while value == 0:
        value = rng.randint(-absolute_limit, absolute_limit)
    return value


def _format_operand(value: int) -> str:
    if value < 0:
        return f"({value})"
    return str(value)
