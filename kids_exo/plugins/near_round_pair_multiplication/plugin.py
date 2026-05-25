import random

from kids_exo.config import SectionSettings
from kids_exo.models import Question
from kids_exo.plugins.base import allocate_strategies
from kids_exo.plugins.near_round_pair_multiplication.settings import (
    NearRoundPairSettings,
)


BELOW = "both_below_round"
ABOVE = "both_above_round"


class NearRoundPairMultiplicationPlugin:
    def __init__(self, settings: NearRoundPairSettings) -> None:
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
                    "When both numbers are close to the same round number, use their small differences.",
                    "Example: 48 x 47, with base 50: 50 x (50 - 2 - 3) + 2 x 3 = 2256.",
                ),
            )
        return ("B. Practice", ("Use the nearby round-number shortcut to calculate.",))

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
        base = rng.choice(self.settings.round_numbers)
        first_distance, second_distance = sorted(
            rng.sample(self.settings.near_round_distances, 2)
        )
        if strategy == BELOW:
            left = base - first_distance
            right = base - second_distance
            operator = "-"
        elif strategy == ABOVE:
            left = base + first_distance
            right = base + second_distance
            operator = "+"
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")
        return Question(
            section=section_name,
            format=format_name,
            left_operand=left,
            right_operand=right,
            strategy=strategy,
            decomposition=None,
            display_text=_render_question(
                left,
                right,
                base,
                first_distance,
                second_distance,
                operator,
                format_name,
            ),
        )


def _render_question(
    left: int,
    right: int,
    base: int,
    first_distance: int,
    second_distance: int,
    operator: str,
    format_name: str,
) -> str:
    if format_name == "expression_with_answer_blank":
        return f"{left} x {right} = __________"
    if format_name != "guided_same_side_round":
        raise ValueError(f"Unsupported format: {format_name}")
    return (
        f"{left} x {right}: base = {base}; {base} x "
        f"({base} {operator} {first_distance} {operator} {second_distance}) "
        f"+ {first_distance} x {second_distance} = ______"
    )
