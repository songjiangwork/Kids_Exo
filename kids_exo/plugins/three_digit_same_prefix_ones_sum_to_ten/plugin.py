import random

from kids_exo.models import Question
from kids_exo.plugins.same_tens_ones_sum_to_ten.plugin import (
    SameTensOnesSumToTenPlugin,
    TWO_DIGIT,
    ZERO_PADDED,
)
from kids_exo.plugins.three_digit_same_prefix_ones_sum_to_ten.settings import (
    ThreeDigitSamePrefixSettings,
)


class ThreeDigitSamePrefixOnesSumToTenPlugin(SameTensOnesSumToTenPlugin):
    """Specialize the same-prefix shortcut for three-digit operands."""

    def __init__(self, settings: ThreeDigitSamePrefixSettings) -> None:
        super().__init__(settings)

    def presentation(self, section_name: str, locale: str) -> tuple[str, tuple[str, ...]]:
        if locale != "en-CA":
            raise ValueError(f"Unsupported plugin locale: {locale}")
        if section_name == "warmup":
            return (
                "A. Warm-up",
                (
                    "Use the matching first two digits. Multiply that number by the next number.",
                    "Multiply the ones digits. Keep the last part as two digits.",
                    "Example: 123 x 127: 12 x 13 = 156 and 3 x 7 = 21, so the answer is 15621.",
                ),
            )
        return ("B. Practice", ("Use the matching-prefix shortcut to calculate.",))

    def _question(
        self,
        section_name: str,
        format_name: str,
        strategy: str,
        rng: random.Random,
    ) -> Question:
        prefix = rng.randint(10, 99)
        if strategy == ZERO_PADDED:
            left_ones = rng.choice((1, 9))
        elif strategy == TWO_DIGIT:
            left_ones = rng.randint(2, 8)
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")
        return self._build_question(
            section_name,
            format_name,
            strategy,
            prefix,
            left_ones,
            10 - left_ones,
        )

    def _render_question(
        self,
        left: int,
        right: int,
        prefix: int,
        left_ones: int,
        right_ones: int,
        format_name: str,
    ) -> str:
        if format_name == "expression_with_answer_blank":
            return f"{left} x {right} = __________"
        if format_name != "guided_prefix_product":
            raise ValueError(f"Unsupported format: {format_name}")
        tail_hint = " (write two digits)" if left_ones * right_ones < 10 else ""
        return (
            f"{left} x {right}: {prefix} x ({prefix} + 1) = ___; "
            f"{left_ones} x {right_ones} = ___{tail_hint}; answer = ______"
        )
