import random

from kids_exo.config import SectionSettings
from kids_exo.models import Question
from kids_exo.plugins.base import allocate_strategies
from kids_exo.plugins.multiply_by_11.settings import MultiplyBy11Settings


NO_CARRYING = "no_carrying"
WITH_CARRYING = "with_carrying"


class MultiplyBy11Plugin:
    def __init__(self, settings: MultiplyBy11Settings) -> None:
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
        if self.settings.multiplicand_digits == (3,):
            if section_name == "warmup":
                return (
                    "A. Warm-up",
                    (
                        "Add each pair of neighbouring digits. Keep the first and last digits.",
                        "Work from right to left and carry when a sum is 10 or more.",
                        "Example: 386 x 11: 8 + 6 = 14, write 4 carry 1; 3 + 8 + 1 = 12; answer 4246.",
                    ),
                )
            return ("B. Practice", ("Multiply each three-digit number by 11.",))
        if section_name == "warmup":
            return (
                "A. Warm-up",
                (
                    "Add the two digits. Put the ones digit in the middle and carry the tens digit to the left.",
                    "Example: 68 x 11: 6 + 8 = 14, so (6 + 1) | 4 | 8 = 748",
                ),
            )
        return ("B. Practice", ("Multiply each number by 11.",))

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
        while True:
            digits = self._digits(rng)
            carrying = any(
                left + right >= 10 for left, right in zip(digits, digits[1:])
            )
            if strategy == NO_CARRYING and not carrying:
                break
            if strategy == WITH_CARRYING and carrying:
                break
        left = int("".join(str(digit) for digit in digits))
        return Question(
            section=section_name,
            format=format_name,
            left_operand=left,
            right_operand=11,
            strategy=strategy,
            decomposition=None,
            display_text=_render_question(left, digits, strategy, format_name),
        )

    def _digits(self, rng: random.Random) -> tuple[int, ...]:
        if self.settings.multiplicand_digits == (2,):
            return (rng.randint(1, 9), rng.randint(1, 9))
        return (rng.randint(1, 9), rng.randint(0, 9), rng.randint(0, 9))


def _render_question(
    left: int,
    digits: tuple[int, ...],
    strategy: str,
    format_name: str,
) -> str:
    if format_name == "expression_with_answer_blank":
        return f"{left} x 11 = __________"
    if format_name != "guided_digit_sum":
        raise ValueError(f"Unsupported format: {format_name}")
    if len(digits) == 3:
        hundreds, tens, ones = digits
        return (
            f"{left} x 11: {tens} + {ones} = ___; "
            f"{hundreds} + {tens} + carry = ___; answer = ______"
        )
    tens, ones = digits
    if strategy == NO_CARRYING:
        return f"{left} x 11: {tens} + {ones} = ___, so {tens} | ___ | {ones} = ______"
    return (
        f"{left} x 11: {tens} + {ones} = ___, so "
        f"({tens} + ___) | ___ | {ones} = ______"
    )
