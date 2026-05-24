from dataclasses import dataclass


SUPPORTED_FORMATS = {
    "guided_full_expansion",
    "expression_with_answer_blank",
}
SUPPORTED_STRATEGIES = {
    "place_value_addition",
    "near_round_number_subtraction",
}


@dataclass(frozen=True)
class DistributiveSettings:
    left_operand_digits: tuple[int, ...]
    right_operand_digits: tuple[int, ...]
    decomposable_operand: str
    strategies: tuple[str, ...]
    allow_duplicates: bool
    near_round_distances: tuple[int, ...]
    strategy_weights: dict[str, float]

    @property
    def allow_subtraction(self) -> bool:
        return "near_round_number_subtraction" in self.strategies


def load_settings(data: dict) -> DistributiveSettings:
    strategies = tuple(data.get("strategies", ["place_value_addition"]))
    raw_weights = data.get("strategy_weights")
    if raw_weights is None:
        raw_weights = {strategy: 1.0 for strategy in strategies}
    settings = DistributiveSettings(
        left_operand_digits=tuple(data.get("left_operand_digits", [2])),
        right_operand_digits=tuple(data.get("right_operand_digits", [1])),
        decomposable_operand=data.get("decomposable_operand", "left"),
        strategies=strategies,
        allow_duplicates=bool(data.get("allow_duplicates", False)),
        near_round_distances=tuple(data.get("near_round_distances", [1, 2, 3])),
        strategy_weights={
            strategy: float(weight)
            for strategy, weight in raw_weights.items()
        },
    )
    _validate_settings(settings)
    return settings


def validate_format(format_name: str, section_name: str) -> None:
    if format_name not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format for section {section_name}: {format_name}")


def _validate_settings(settings: DistributiveSettings) -> None:
    if settings.left_operand_digits != (2,) or settings.right_operand_digits != (1,):
        raise ValueError("Version 1 supports two-digit x one-digit multiplication only")
    if settings.decomposable_operand != "left":
        raise ValueError("Version 1 decomposes the left operand only")
    if not settings.strategies or set(settings.strategies) - SUPPORTED_STRATEGIES:
        raise ValueError("Unsupported distributive strategy")
    if not settings.near_round_distances or any(distance < 1 or distance > 9 for distance in settings.near_round_distances):
        raise ValueError("Near-round distances must be between 1 and 9")
    if set(settings.strategy_weights) != set(settings.strategies):
        raise ValueError("strategy_weights must define exactly the enabled strategies")
    if any(weight < 0 for weight in settings.strategy_weights.values()):
        raise ValueError("strategy_weights cannot contain negative values")
    if sum(settings.strategy_weights.values()) <= 0:
        raise ValueError("strategy_weights must have a positive total")
