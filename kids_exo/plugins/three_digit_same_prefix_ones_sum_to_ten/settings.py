from dataclasses import dataclass

from kids_exo.plugins.same_tens_ones_sum_to_ten.settings import (
    SameTensOnesSumToTenSettings,
)


SUPPORTED_FORMATS = {"guided_prefix_product", "expression_with_answer_blank"}
SUPPORTED_STRATEGIES = {"zero_padded_ones_product", "two_digit_ones_product"}


@dataclass(frozen=True)
class ThreeDigitSamePrefixSettings(SameTensOnesSumToTenSettings):
    """Extend the same-prefix rule to prefixes between 10 and 99."""


def load_settings(data: dict) -> ThreeDigitSamePrefixSettings:
    strategies = tuple(
        data.get(
            "strategies",
            ["zero_padded_ones_product", "two_digit_ones_product"],
        )
    )
    raw_weights = data.get("strategy_weights") or {
        strategy: 1.0 for strategy in strategies
    }
    settings = ThreeDigitSamePrefixSettings(
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


def _validate_settings(settings: ThreeDigitSamePrefixSettings) -> None:
    if not settings.strategies or set(settings.strategies) - SUPPORTED_STRATEGIES:
        raise ValueError("Unsupported three-digit same-prefix strategy")
    if set(settings.strategy_weights) != set(settings.strategies):
        raise ValueError("strategy_weights must define exactly the enabled strategies")
    if any(weight < 0 for weight in settings.strategy_weights.values()):
        raise ValueError("strategy_weights cannot contain negative values")
    if sum(settings.strategy_weights.values()) <= 0:
        raise ValueError("strategy_weights must have a positive total")
