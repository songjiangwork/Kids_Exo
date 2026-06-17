from dataclasses import dataclass


SUPPORTED_STRATEGIES = {"dictation", "translation", "combined"}


@dataclass(frozen=True)
class FrenchCommonWordSpellingSettings:
    strategy: str = "combined"


def load_settings(data: dict) -> FrenchCommonWordSpellingSettings:
    unexpected_keys = set(data) - {"strategy"}
    if unexpected_keys:
        names = ", ".join(sorted(unexpected_keys))
        raise ValueError(f"Plugin settings are not configurable online: {names}")
    strategies = tuple(data.get("strategy", ("combined",)))
    strategy = str(strategies[0]) if strategies else "combined"
    if len(strategies) != 1 or strategy not in SUPPORTED_STRATEGIES:
        raise ValueError("Unsupported French spelling strategy")
    return FrenchCommonWordSpellingSettings(strategy=strategy)
