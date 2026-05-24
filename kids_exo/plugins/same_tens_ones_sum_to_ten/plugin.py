import random

from kids_exo.config import SectionSettings
from kids_exo.models import Question
from kids_exo.plugins.base import allocate_strategies
from kids_exo.plugins.same_tens_ones_sum_to_ten.settings import (
    SameTensOnesSumToTenSettings,
)


ZERO_PADDED = "zero_padded_ones_product"
TWO_DIGIT = "two_digit_ones_product"


class SameTensOnesSumToTenPlugin:
    def __init__(self, settings: SameTensOnesSumToTenSettings) -> None:
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
                    "Multiply the tens digit by the next number.",
                    "Multiply the ones digits. Keep the last part as two digits.",
                    "Example: 43 x 47: 4 x 5 = 20 and 3 x 7 = 21, so the answer is 2021.",
                ),
            )
        return ("B. Practice", ("Use the same-tens shortcut to calculate.",))

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
        tens = rng.randint(1, 9)
        if strategy == ZERO_PADDED:
            left_ones = rng.choice((1, 9))
        elif strategy == TWO_DIGIT:
            left_ones = rng.randint(2, 8)
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")
        right_ones = 10 - left_ones
        left = tens * 10 + left_ones
        right = tens * 10 + right_ones
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
                tens,
                left_ones,
                right_ones,
                format_name,
            ),
        )


def _render_question(
    left: int,
    right: int,
    tens: int,
    left_ones: int,
    right_ones: int,
    format_name: str,
) -> str:
    if format_name == "expression_with_answer_blank":
        return f"{left} x {right} = __________"
    if format_name != "guided_two_part_product":
        raise ValueError(f"Unsupported format: {format_name}")
    tail_hint = " (write two digits)" if left_ones * right_ones < 10 else ""
    return (
        f"{left} x {right}: {tens} x ({tens} + 1) = ___; "
        f"{left_ones} x {right_ones} = ___{tail_hint}; answer = ______"
    )
