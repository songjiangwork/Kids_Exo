from __future__ import annotations

from dataclasses import dataclass
import random
from typing import TYPE_CHECKING, Any

from kids_exo.localization import LocalizedPresentation, LocalizedText
from kids_exo.online.models import OnlineQuestionSnapshot, PracticeSessionSnapshot
from kids_exo.plugins.chicken_rabbit_word_problems.settings import (
    ChickenRabbitWordProblemSettings,
)

if TYPE_CHECKING:
    from kids_exo.online.session import OnlineSessionRequest


@dataclass(frozen=True)
class WordProblemContext:
    key: str
    group_label: str
    container: str
    item_a: str
    item_a_plural: str
    item_b: str
    item_b_plural: str
    unit_label: str
    unit_a: int
    unit_b: int


INTRO_CONTEXTS = (
    WordProblemContext(
        key="chicken_rabbit",
        group_label="animals",
        container="in a cage",
        item_a="chicken",
        item_a_plural="chickens",
        item_b="rabbit",
        item_b_plural="rabbits",
        unit_label="legs",
        unit_a=2,
        unit_b=4,
    ),
    WordProblemContext(
        key="bicycle_car",
        group_label="vehicles",
        container="in a parking lot",
        item_a="bicycle",
        item_a_plural="bicycles",
        item_b="car",
        item_b_plural="cars",
        unit_label="wheels",
        unit_a=2,
        unit_b=4,
    ),
)

MIXED_CONTEXTS = INTRO_CONTEXTS + (
    WordProblemContext(
        key="bee_spider",
        group_label="creatures",
        container="in a garden",
        item_a="bee",
        item_a_plural="bees",
        item_b="spider",
        item_b_plural="spiders",
        unit_label="legs",
        unit_a=6,
        unit_b=8,
    ),
    WordProblemContext(
        key="pentagon_heptagon",
        group_label="shapes",
        container="on a worksheet",
        item_a="pentagon",
        item_a_plural="pentagons",
        item_b="heptagon",
        item_b_plural="heptagons",
        unit_label="sides",
        unit_a=5,
        unit_b=7,
    ),
    WordProblemContext(
        key="stool_chair",
        group_label="pieces of furniture",
        container="in a classroom",
        item_a="three-legged stool",
        item_a_plural="three-legged stools",
        item_b="four-legged chair",
        item_b_plural="four-legged chairs",
        unit_label="legs",
        unit_a=3,
        unit_b=4,
    ),
)


def create_chicken_rabbit_word_problem_session(
    request: OnlineSessionRequest,
    settings: ChickenRabbitWordProblemSettings,
) -> PracticeSessionSnapshot:
    rng = random.Random(request.seed)
    contexts = INTRO_CONTEXTS if settings.difficulty == "intro" else MIXED_CONTEXTS
    questions = tuple(
        _create_question(position, request.question_count, rng, contexts, settings.difficulty)
        for position in range(1, request.question_count + 1)
    )
    return PracticeSessionSnapshot(
        plugin=request.plugin,
        subject="Math",
        category="Word Problems",
        skill="Chicken and Rabbit Word Problems",
        plugin_settings=settings,
        requested_locale=request.requested_locale,
        feedback_mode=request.feedback_mode,
        show_timer=request.show_timer,
        seed=request.seed,
        presentation=LocalizedPresentation(
            heading=LocalizedText("Chicken and Rabbit Word Problems", "en-CA", False),
            instructions=(
                LocalizedText(
                    "Use total count and total units to find both quantities.",
                    "en-CA",
                    False,
                ),
            ),
        ),
        questions=questions,
    )


def _create_question(
    position: int,
    total_questions: int,
    rng: random.Random,
    contexts: tuple[WordProblemContext, ...],
    difficulty: str,
) -> OnlineQuestionSnapshot:
    context = rng.choice(contexts)
    max_count = 15 if difficulty == "intro" else 30
    item_a_count = rng.randint(2, max_count)
    item_b_count = rng.randint(2, max_count)
    total_count = item_a_count + item_b_count
    total_units = item_a_count * context.unit_a + item_b_count * context.unit_b
    first_key = f"{context.item_a.replace('-', ' ').replace(' ', '_')}_count"
    second_key = f"{context.item_b.replace('-', ' ').replace(' ', '_')}_count"
    problem_text = (
        f"There are {total_count} {context.group_label} {context.container}. Some are "
        f"{context.item_a_plural} and some are {context.item_b_plural}. Altogether they "
        f"have {total_units} {context.unit_label}. How many {context.item_a_plural} "
        f"and {context.item_b_plural} are there?"
    )
    answer_schema = {
        "fields": (
            _answer_field(first_key, context.item_a_plural),
            _answer_field(second_key, context.item_b_plural),
        ),
    }
    expected_values = {
        first_key: item_a_count,
        second_key: item_b_count,
    }
    field_rules = {
        first_key: {"value_type": "integer", "tolerance": 0},
        second_key: {"value_type": "integer", "tolerance": 0},
    }
    diagnostic_checks: dict[str, Any] = {
        "total_count": total_count,
        "unit_label": context.unit_label,
        "total_units": total_units,
        "unit_values": {
            first_key: context.unit_a,
            second_key: context.unit_b,
        },
    }
    return OnlineQuestionSnapshot(
        identifier=f"question-{position}",
        prompt=problem_text,
        strategy=f"{context.key}_{difficulty}",
        skill_tags=("word_problems", "two_quantity_total_unit", context.key),
        renderer_type="word_problem_answer",
        answer_type="structured_word_problem",
        evaluation_payload={
            "expected_values": expected_values,
            "field_rules": field_rules,
            "diagnostic_checks": diagnostic_checks,
        },
        prompt_payload={"problem_text": problem_text},
        public_payload={
            "problem_text": problem_text,
            "answer_schema": answer_schema,
            "work_area": {
                "enabled": True,
                "required": False,
                "label": "Show your work",
            },
            "tools": {"scratch_pad": True, "audio": False},
        },
        question_type="word_problem",
    )


def _answer_field(key: str, label: str) -> dict[str, Any]:
    return {
        "key": key,
        "label": label.title(),
        "value_type": "integer",
        "unit": "items",
        "required": True,
    }
