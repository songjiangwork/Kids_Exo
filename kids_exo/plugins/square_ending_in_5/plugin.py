import random

from kids_exo.models import Question
from kids_exo.plugins.same_tens_ones_sum_to_ten.plugin import (
    SameTensOnesSumToTenPlugin,
)
from kids_exo.plugins.square_ending_in_5.settings import SquareEndingIn5Settings


ENDING_IN_5_SQUARE = "ending_in_5_square"


class SquareEndingIn5Plugin(SameTensOnesSumToTenPlugin):
    """Specialize the same-tens rule by fixing both ones digits at five."""

    def __init__(self, settings: SquareEndingIn5Settings) -> None:
        super().__init__(settings)

    def presentation(self, section_name: str, locale: str) -> tuple[str, tuple[str, ...]]:
        if locale != "en-CA":
            raise ValueError(f"Unsupported plugin locale: {locale}")
        if section_name == "warmup":
            return (
                "A. Warm-up",
                (
                    "Multiply the tens digit by the next number. Write 25 at the end.",
                    "Example: 35 x 35: 3 x 4 = 12, so the answer is 1225.",
                ),
            )
        return ("B. Practice", ("Use the ending-in-5 square shortcut to calculate.",))

    def _question(
        self,
        section_name: str,
        format_name: str,
        strategy: str,
        rng: random.Random,
    ) -> Question:
        if strategy != ENDING_IN_5_SQUARE:
            raise ValueError(f"Unsupported strategy: {strategy}")
        return self._build_question(
            section_name,
            format_name,
            strategy,
            rng.randint(1, 9),
            5,
            5,
        )

    def _render_question(
        self,
        left: int,
        right: int,
        tens: int,
        left_ones: int,
        right_ones: int,
        format_name: str,
    ) -> str:
        if format_name == "expression_with_answer_blank":
            return f"{left} x {right} = __________"
        if format_name != "guided_ending_in_5_square":
            raise ValueError(f"Unsupported format: {format_name}")
        return (
            f"{left} x {right}: {tens} x ({tens} + 1) = ___; "
            "write 25; answer = ______"
        )
