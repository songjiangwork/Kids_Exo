from dataclasses import dataclass


SUPPORTED_FORMATS = {"guided_two_part_product", "expression_with_answer_blank"}
SUPPORTED_STRATEGIES = {"zero_padded_ones_product", "two_digit_ones_product"}


@dataclass(frozen=True)
class SameTensOnesSumToTenSettings:
    strategies: tuple[str, ...]
    allow_duplicates: bool
    strategy_weights: dict[str, float]


def load_settings(data: dict) -> SameTensOnesSumToTenSettings:
    strategies = tuple(
        data.get(
            "strategies",
            ["zero_padded_ones_product", "two_digit_ones_product"],
        )
    )
    raw_weights = data.get("strategy_weights") or {
        strategy: 1.0 for strategy in strategies
    }
    settings = SameTensOnesSumToTenSettings(
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


def _validate_settings(settings: SameTensOnesSumToTenSettings) -> None:
    if not settings.strategies or set(settings.strategies) - SUPPORTED_STRATEGIES:
        raise ValueError("Unsupported same-tens-ones-sum-to-ten strategy")
    if set(settings.strategy_weights) != set(settings.strategies):
        raise ValueError("strategy_weights must define exactly the enabled strategies")
    if any(weight < 0 for weight in settings.strategy_weights.values()):
        raise ValueError("strategy_weights cannot contain negative values")
    if sum(settings.strategy_weights.values()) <= 0:
        raise ValueError("strategy_weights must have a positive total")
