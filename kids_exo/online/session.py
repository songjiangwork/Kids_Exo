from dataclasses import dataclass
import random
from typing import Any

from kids_exo.config import SectionSettings
from kids_exo.online.catalog import (
    get_online_catalog,
    get_online_plugin,
    load_online_plugin_settings,
)
from kids_exo.online.models import OnlineQuestionSnapshot, PracticeSessionSnapshot
from kids_exo.plugins.registry import get_plugin_definition


@dataclass(frozen=True)
class OnlineSessionRequest:
    plugin: str
    plugin_settings: dict[str, Any]
    question_count: int
    requested_locale: str = "en-CA"
    feedback_mode: str = "immediate"
    show_timer: bool = False
    seed: int | None = None


def create_practice_session(request: OnlineSessionRequest) -> PracticeSessionSnapshot:
    """Create an immutable online-practice snapshot before persistence is introduced."""

    _validate_request(request)
    definition = get_plugin_definition(request.plugin)
    settings = load_online_plugin_settings(request.plugin, request.plugin_settings)
    definition.validate_format("expression_with_answer_blank", "practice")
    section = SectionSettings(
        name="practice",
        plugin=request.plugin,
        count=request.question_count,
        columns=1,
        format="expression_with_answer_blank",
        settings=settings,
    )
    plugin = definition.create(settings)
    printable_questions = plugin.generate(
        "practice",
        section,
        random.Random(request.seed),
        set(),
    )
    presentation = plugin.localized_presentation("practice", request.requested_locale)
    questions = tuple(
        OnlineQuestionSnapshot(
            identifier=f"question-{position}",
            prompt=question.display_text,
            strategy=question.strategy,
            expected_answer=question.left_operand * question.right_operand,
            skill_tags=("mental_multiplication", request.plugin),
        )
        for position, question in enumerate(printable_questions, start=1)
    )
    return PracticeSessionSnapshot(
        plugin=request.plugin,
        plugin_settings=settings,
        requested_locale=request.requested_locale,
        feedback_mode=request.feedback_mode,
        show_timer=request.show_timer,
        seed=request.seed,
        presentation=presentation,
        questions=questions,
    )


def _validate_request(request: OnlineSessionRequest) -> None:
    catalog = get_online_catalog()
    get_online_plugin(request.plugin)
    if request.question_count not in catalog.question_counts:
        raise ValueError("Online MVP question_count must be 10, 20, or 30")
    if request.feedback_mode not in catalog.feedback_modes:
        raise ValueError("feedback_mode must be immediate or deferred")
