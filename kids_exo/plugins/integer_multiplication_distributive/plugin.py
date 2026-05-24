import random
import math

from kids_exo.config import SectionSettings
from kids_exo.models import Decomposition, Question
from kids_exo.plugins.integer_multiplication_distributive.settings import (
    DistributiveSettings,
)


ADDITION = "place_value_addition"
SUBTRACTION = "near_round_number_subtraction"


class IntegerMultiplicationDistributivePlugin:
    def __init__(self, settings: DistributiveSettings) -> None:
        self.settings = settings

    def generate(
        self,
        section_name: str,
        section: SectionSettings,
        rng: random.Random,
        used_expressions: set[str],
    ) -> tuple[Question, ...]:
        strategies = self._section_strategies(section_name, section.count, rng)
        questions = [
            self._unique_question(section_name, section.format, strategy, rng, used_expressions)
            for strategy in strategies
        ]
        return tuple(questions)

    def _section_strategies(self, section_name: str, count: int, rng: random.Random) -> list[str]:
        enabled = list(self.settings.strategies)
        if len(enabled) == 1:
            return enabled * count

        total_weight = sum(self.settings.strategy_weights.values())
        quotas = {
            strategy: count * self.settings.strategy_weights[strategy] / total_weight
            for strategy in enabled
        }
        allocations = {strategy: math.floor(quota) for strategy, quota in quotas.items()}
        remaining = count - sum(allocations.values())
        priority = sorted(
            enabled,
            key=lambda strategy: (quotas[strategy] - allocations[strategy], -enabled.index(strategy)),
            reverse=True,
        )
        for strategy in priority[:remaining]:
            allocations[strategy] += 1

        strategies = [
            strategy
            for strategy in enabled
            for _ in range(allocations[strategy])
        ]
        rng.shuffle(strategies)
        return strategies

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
        right = rng.randint(2, 9)
        if strategy == ADDITION:
            left = rng.randint(12, 98)
            while self._reserved_for_subtraction(left):
                left = rng.randint(12, 98)
            ones = left % 10
            decomposition = Decomposition(
                operator="+",
                first_part=left - ones,
                second_part=ones,
            )
        elif strategy == SUBTRACTION:
            round_number = rng.choice(tuple(range(20, 101, 10)))
            difference = rng.choice(self.settings.near_round_distances)
            left = round_number - difference
            decomposition = Decomposition(
                operator="-",
                first_part=round_number,
                second_part=difference,
                round_number=round_number,
                difference=difference,
            )
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")

        display_text = _render_question(left, right, decomposition, format_name)
        return Question(
            section=section_name,
            format=format_name,
            left_operand=left,
            right_operand=right,
            strategy=strategy,
            decomposition=decomposition,
            display_text=display_text,
        )

    def _reserved_for_subtraction(self, left: int) -> bool:
        if left % 10 == 0:
            return True
        if not self.settings.allow_subtraction:
            return False
        return 10 - (left % 10) in self.settings.near_round_distances


def _render_question(
    left: int,
    right: int,
    decomposition: Decomposition,
    format_name: str,
) -> str:
    if format_name == "expression_with_answer_blank":
        return f"{left} x {right} = __________"
    if format_name == "guided_full_expansion":
        operator = decomposition.operator
        return (
            f"{left} x {right} = ({decomposition.first_part} {operator} "
            f"{decomposition.second_part}) x {right} = ___ x ___ {operator} "
            "___ x ___ = ___"
        )
    raise ValueError(f"Unsupported format: {format_name}")
