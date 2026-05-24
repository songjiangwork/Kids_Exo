from dataclasses import dataclass


SUPPORTED_FORMATS = {"guided_divide_then_scale", "expression_with_answer_blank"}
SUPPORTED_STRATEGIES = {"times_5", "times_25", "times_125"}


@dataclass(frozen=True)
class MultiplyByFiveFamilySettings:
    multiplicand_digits: tuple[int, ...]
    strategies: tuple[str, ...]
    allow_duplicates: bool
    strategy_weights: dict[str, float]


def load_settings(data: dict) -> MultiplyByFiveFamilySettings:
    strategies = tuple(data.get("strategies", ["times_5", "times_25", "times_125"]))
    raw_weights = data.get("strategy_weights") or {
        strategy: 1.0 for strategy in strategies
    }
    settings = MultiplyByFiveFamilySettings(
        multiplicand_digits=tuple(data.get("multiplicand_digits", [2])),
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


def _validate_settings(settings: MultiplyByFiveFamilySettings) -> None:
    if settings.multiplicand_digits != (2,):
        raise ValueError("The beginner 5/25/125 preset supports two-digit multiplicands only")
    if not settings.strategies or set(settings.strategies) - SUPPORTED_STRATEGIES:
        raise ValueError("Unsupported multiply-by-5-25-125 strategy")
    if set(settings.strategy_weights) != set(settings.strategies):
        raise ValueError("strategy_weights must define exactly the enabled strategies")
    if any(weight < 0 for weight in settings.strategy_weights.values()):
        raise ValueError("strategy_weights cannot contain negative values")
    if sum(settings.strategy_weights.values()) <= 0:
        raise ValueError("strategy_weights must have a positive total")
