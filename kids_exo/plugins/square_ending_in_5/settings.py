from dataclasses import dataclass

from kids_exo.plugins.same_tens_ones_sum_to_ten.settings import (
    SameTensOnesSumToTenSettings,
)


SUPPORTED_FORMATS = {"guided_ending_in_5_square", "expression_with_answer_blank"}
SUPPORTED_STRATEGIES = {"ending_in_5_square"}


@dataclass(frozen=True)
class SquareEndingIn5Settings(SameTensOnesSumToTenSettings):
    """A restricted same-tens configuration with both ones digits fixed at five."""


def load_settings(data: dict) -> SquareEndingIn5Settings:
    strategies = tuple(data.get("strategies", ["ending_in_5_square"]))
    raw_weights = data.get("strategy_weights") or {
        strategy: 1.0 for strategy in strategies
    }
    settings = SquareEndingIn5Settings(
        strategies=strategies,
        allow_duplicates=bool(data.get("allow_duplicates", True)),
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


def _validate_settings(settings: SquareEndingIn5Settings) -> None:
    if not settings.strategies or set(settings.strategies) - SUPPORTED_STRATEGIES:
        raise ValueError("Unsupported square-ending-in-5 strategy")
    if set(settings.strategy_weights) != set(settings.strategies):
        raise ValueError("strategy_weights must define exactly the enabled strategies")
    if any(weight < 0 for weight in settings.strategy_weights.values()):
        raise ValueError("strategy_weights cannot contain negative values")
    if sum(settings.strategy_weights.values()) <= 0:
        raise ValueError("strategy_weights must have a positive total")
