from dataclasses import dataclass


SUPPORTED_FORMATS = {"guided_front_plus_tail_square", "expression_with_answer_blank"}
SUPPORTED_STRATEGIES = {"zero_padded_ones_square", "two_digit_ones_square"}


@dataclass(frozen=True)
class TensSumToTenSameOnesSettings:
    strategies: tuple[str, ...]
    allow_duplicates: bool
    strategy_weights: dict[str, float]


def load_settings(data: dict) -> TensSumToTenSameOnesSettings:
    strategies = tuple(
        data.get(
            "strategies",
            ["zero_padded_ones_square", "two_digit_ones_square"],
        )
    )
    raw_weights = data.get("strategy_weights") or {
        strategy: 1.0 for strategy in strategies
    }
    settings = TensSumToTenSameOnesSettings(
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


def _validate_settings(settings: TensSumToTenSameOnesSettings) -> None:
    if not settings.strategies or set(settings.strategies) - SUPPORTED_STRATEGIES:
        raise ValueError("Unsupported tens-sum-to-ten-same-ones strategy")
    if set(settings.strategy_weights) != set(settings.strategies):
        raise ValueError("strategy_weights must define exactly the enabled strategies")
    if any(weight < 0 for weight in settings.strategy_weights.values()):
        raise ValueError("strategy_weights cannot contain negative values")
    if sum(settings.strategy_weights.values()) <= 0:
        raise ValueError("strategy_weights must have a positive total")
