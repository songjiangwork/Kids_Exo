import random

from kids_exo.config import SectionSettings
from kids_exo.models import Question
from kids_exo.plugins.base import allocate_strategies
from kids_exo.plugins.multiply_by_5_25_125.settings import MultiplyByFiveFamilySettings


SHORTCUT_BY_STRATEGY = {
    "times_5": (5, 2, 10),
    "times_25": (25, 4, 100),
    "times_125": (125, 8, 1000),
}


class MultiplyByFiveFamilyPlugin:
    def __init__(self, settings: MultiplyByFiveFamilySettings) -> None:
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
                    "Divide first, then multiply by a round number.",
                    "x 5 = / 2 x 10; x 25 = / 4 x 100; x 125 = / 8 x 1000.",
                    "Example: 16 x 125 = 2 x 1000 = 2000.",
                ),
            )
        return ("B. Practice", ("Use the divide-then-scale shortcut.",))

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
        multiplier, divisor, scale = SHORTCUT_BY_STRATEGY[strategy]
        factor = rng.randint((10 + divisor - 1) // divisor, 99 // divisor)
        left = factor * divisor
        return Question(
            section=section_name,
            format=format_name,
            left_operand=left,
            right_operand=multiplier,
            strategy=strategy,
            decomposition=None,
            display_text=_render_question(left, multiplier, divisor, scale, format_name),
        )


def _render_question(
    left: int,
    multiplier: int,
    divisor: int,
    scale: int,
    format_name: str,
) -> str:
    if format_name == "expression_with_answer_blank":
        return f"{left} x {multiplier} = __________"
    if format_name != "guided_divide_then_scale":
        raise ValueError(f"Unsupported format: {format_name}")
    return (
        f"{left} x {multiplier} = ({left} / {divisor}) x {scale} "
        f"= ___ x {scale} = ______"
    )
