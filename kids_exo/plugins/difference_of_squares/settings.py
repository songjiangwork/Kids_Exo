from dataclasses import dataclass


SUPPORTED_FORMATS = {"guided_difference_of_squares", "expression_with_answer_blank"}
SUPPORTED_STRATEGIES = {"symmetric_around_round"}


@dataclass(frozen=True)
class DifferenceOfSquaresSettings:
    round_numbers: tuple[int, ...]
    near_round_distances: tuple[int, ...]
    strategies: tuple[str, ...]
    allow_duplicates: bool
    strategy_weights: dict[str, float]


def load_settings(data: dict) -> DifferenceOfSquaresSettings:
    strategies = tuple(data.get("strategies", ["symmetric_around_round"]))
    raw_weights = data.get("strategy_weights") or {
        strategy: 1.0 for strategy in strategies
    }
    settings = DifferenceOfSquaresSettings(
        round_numbers=tuple(data.get("round_numbers", range(20, 101, 10))),
        near_round_distances=tuple(data.get("near_round_distances", [1, 2, 3, 4])),
        strategies=strategies,
        allow_duplicates=bool(data.get("allow_duplicates", False)),
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


def _validate_settings(settings: DifferenceOfSquaresSettings) -> None:
    if not settings.round_numbers or any(number < 10 or number % 10 for number in settings.round_numbers):
        raise ValueError("round_numbers must contain positive multiples of ten")
    if not settings.near_round_distances or any(
        distance < 1 or distance > 9 for distance in settings.near_round_distances
    ):
        raise ValueError("Near-round distances must be between 1 and 9")
    if settings.strategies != ("symmetric_around_round",):
        raise ValueError("Difference-of-squares beginner preset supports symmetric factors only")
    if set(settings.strategy_weights) != set(settings.strategies):
        raise ValueError("strategy_weights must define exactly the enabled strategies")
    if any(weight < 0 for weight in settings.strategy_weights.values()):
        raise ValueError("strategy_weights cannot contain negative values")
    if sum(settings.strategy_weights.values()) <= 0:
        raise ValueError("strategy_weights must have a positive total")
