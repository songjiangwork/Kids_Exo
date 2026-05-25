import random

from kids_exo.config import SectionSettings
from kids_exo.models import Question
from kids_exo.plugins.base import allocate_strategies
from kids_exo.plugins.difference_of_squares.settings import DifferenceOfSquaresSettings


SYMMETRIC = "symmetric_around_round"


class DifferenceOfSquaresPlugin:
    def __init__(self, settings: DifferenceOfSquaresSettings) -> None:
        self.settings = settings

    def generate(
        self,
        section_name: str,
        section: SectionSettings,
        rng: random.Random,
        used_expressions: set[str],
    ) -> tuple[Question, ...]:
        strategies = allocate_strategies(
            self.settings.strategies,
            self.settings.strategy_weights,
            section.count,
            rng,
        )
        return tuple(
            self._unique_question(section_name, section.format, strategy, rng, used_expressions)
            for strategy in strategies
        )

    def presentation(self, section_name: str, locale: str) -> tuple[str, tuple[str, ...]]:
        if locale != "en-CA":
            raise ValueError(f"Unsupported plugin locale: {locale}")
        if section_name == "warmup":
            return (
                "A. Warm-up",
                (
                    "If two numbers are the same distance below and above a round number, subtract squares.",
                    "Example: 47 x 53 = (50 - 3) x (50 + 3) = 50 x 50 - 3 x 3 = 2491.",
                ),
            )
        return ("B. Practice", ("Use the difference of squares shortcut.",))

    def _unique_question(
        self,
        section_name: str,
        format_name: str,
        strategy: str,
        rng: random.Random,
        used_expressions: set[str],
    ) -> Question:
        for _ in range(500):
            question = self._question(section_name, format_name, strategy, rng)
            if self.settings.allow_duplicates or question.expression not in used_expressions:
                used_expressions.add(question.expression)
                return question
        raise ValueError("Unable to generate enough unique questions with the selected settings")

    def _question(
        self,
        section_name: str,
        format_name: str,
        strategy: str,
        rng: random.Random,
    ) -> Question:
        if strategy != SYMMETRIC:
            raise ValueError(f"Unsupported strategy: {strategy}")
        base = rng.choice(self.settings.round_numbers)
        distance = rng.choice(self.settings.near_round_distances)
        left = base - distance
        right = base + distance
        return Question(
            section=section_name,
            format=format_name,
            left_operand=left,
            right_operand=right,
            strategy=strategy,
            decomposition=None,
            display_text=_render_question(left, right, base, distance, format_name),
        )


def _render_question(
    left: int,
    right: int,
    base: int,
    distance: int,
    format_name: str,
) -> str:
    if format_name == "expression_with_answer_blank":
        return f"{left} x {right} = __________"
    if format_name != "guided_difference_of_squares":
        raise ValueError(f"Unsupported format: {format_name}")
    return (
        f"{left} x {right} = ({base} - {distance}) x ({base} + {distance}) "
        f"= ___ x ___ - ___ x ___ = ______"
    )
