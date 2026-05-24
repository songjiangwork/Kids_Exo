import random

from kids_exo.config import SectionSettings
from kids_exo.models import Question
from kids_exo.plugins.base import allocate_strategies
from kids_exo.plugins.multiply_by_9_99_999.settings import MultiplyByNinesSettings


MULTIPLIER_BY_STRATEGY = {
    "times_9": 9,
    "times_99": 99,
    "times_999": 999,
}


class MultiplyByNinesPlugin:
    def __init__(self, settings: MultiplyByNinesSettings) -> None:
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
                    "Use that 9, 99, and 999 are one less than 10, 100, or 1000.",
                    "Example: 36 x 99 = 36 x (100 - 1) = 3600 - 36 = 3564.",
                ),
            )
        return ("B. Practice", ("Use a round-number subtraction shortcut.",))

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
        multiplier = MULTIPLIER_BY_STRATEGY[strategy]
        left = rng.randint(10, 99)
        return Question(
            section=section_name,
            format=format_name,
            left_operand=left,
            right_operand=multiplier,
            strategy=strategy,
            decomposition=None,
            display_text=_render_question(left, multiplier, format_name),
        )


def _render_question(left: int, multiplier: int, format_name: str) -> str:
    if format_name == "expression_with_answer_blank":
        return f"{left} x {multiplier} = __________"
    if format_name != "guided_round_minus_one":
        raise ValueError(f"Unsupported format: {format_name}")
    round_number = multiplier + 1
    return (
        f"{left} x {multiplier} = {left} x ({round_number} - 1) "
        f"= ___ - ___ = ______"
    )
