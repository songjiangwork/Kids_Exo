import random

from kids_exo.config import SectionSettings
from kids_exo.models import Question
from kids_exo.plugins.base import allocate_strategies
from kids_exo.plugins.tens_sum_to_ten_same_ones.settings import (
    TensSumToTenSameOnesSettings,
)


ZERO_PADDED = "zero_padded_ones_square"
TWO_DIGIT = "two_digit_ones_square"


class TensSumToTenSameOnesPlugin:
    def __init__(self, settings: TensSumToTenSameOnesSettings) -> None:
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
                    "Multiply the tens digits. Add the shared ones digit.",
                    "Square the shared ones digit. Keep the last part as two digits.",
                    "Example: 43 x 63: 4 x 6 + 3 = 27 and 3 x 3 = 09, so the answer is 2709.",
                ),
            )
        return ("B. Practice", ("Use the tens-sum-to-ten shortcut to calculate.",))

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
        left_tens = rng.randint(1, 9)
        right_tens = 10 - left_tens
        if strategy == ZERO_PADDED:
            ones = rng.randint(1, 3)
        elif strategy == TWO_DIGIT:
            ones = rng.randint(4, 9)
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")
        left = left_tens * 10 + ones
        right = right_tens * 10 + ones
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
                left_tens,
                right_tens,
                ones,
                format_name,
            ),
        )


def _render_question(
    left: int,
    right: int,
    left_tens: int,
    right_tens: int,
    ones: int,
    format_name: str,
) -> str:
    if format_name == "expression_with_answer_blank":
        return f"{left} x {right} = __________"
    if format_name != "guided_front_plus_tail_square":
        raise ValueError(f"Unsupported format: {format_name}")
    tail_hint = " (write two digits)" if ones * ones < 10 else ""
    return (
        f"{left} x {right}: {left_tens} x {right_tens} + {ones} = ___; "
        f"{ones} x {ones} = ___{tail_hint}; answer = ______"
    )
