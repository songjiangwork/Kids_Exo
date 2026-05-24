from typing import Protocol
import random
import math

from kids_exo.config import SectionSettings
from kids_exo.models import Question


class QuestionPlugin(Protocol):
    def generate(
        self,
        section_name: str,
        section: SectionSettings,
        rng: random.Random,
        used_expressions: set[str],
    ) -> tuple[Question, ...]: ...

    def presentation(self, section_name: str, locale: str) -> tuple[str, tuple[str, ...]]: ...


def allocate_strategies(
    strategies: tuple[str, ...],
    weights: dict[str, float],
    count: int,
    rng: random.Random,
) -> list[str]:
    total_weight = sum(weights.values())
    quotas = {
        strategy: count * weights[strategy] / total_weight
        for strategy in strategies
    }
    allocations = {strategy: math.floor(quota) for strategy, quota in quotas.items()}
    remaining = count - sum(allocations.values())
    priority = sorted(
        strategies,
        key=lambda strategy: (
            quotas[strategy] - allocations[strategy],
            -strategies.index(strategy),
        ),
        reverse=True,
    )
    for strategy in priority[:remaining]:
        allocations[strategy] += 1
    result = [
        strategy
        for strategy in strategies
        for _ in range(allocations[strategy])
    ]
    rng.shuffle(result)
    return result
