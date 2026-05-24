from dataclasses import dataclass


SUPPORTED_FORMATS = {"guided_digit_sum", "expression_with_answer_blank"}
SUPPORTED_STRATEGIES = {"no_carrying", "with_carrying"}


@dataclass(frozen=True)
class MultiplyBy11Settings:
    multiplicand_digits: tuple[int, ...]
    strategies: tuple[str, ...]
    allow_duplicates: bool
    strategy_weights: dict[str, float]


def load_settings(data: dict) -> MultiplyBy11Settings:
    strategies = tuple(data.get("strategies", ["no_carrying", "with_carrying"]))
    raw_weights = data.get("strategy_weights") or {
        strategy: 1.0 for strategy in strategies
    }
    settings = MultiplyBy11Settings(
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


def _validate_settings(settings: MultiplyBy11Settings) -> None:
    if settings.multiplicand_digits != (2,):
        raise ValueError("Version 1 supports two-digit multiplication by 11 only")
    if not settings.strategies or set(settings.strategies) - SUPPORTED_STRATEGIES:
        raise ValueError("Unsupported multiply-by-11 strategy")
    if set(settings.strategy_weights) != set(settings.strategies):
        raise ValueError("strategy_weights must define exactly the enabled strategies")
    if any(weight < 0 for weight in settings.strategy_weights.values()):
        raise ValueError("strategy_weights cannot contain negative values")
    if sum(settings.strategy_weights.values()) <= 0:
        raise ValueError("strategy_weights must have a positive total")
