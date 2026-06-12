from dataclasses import dataclass


SUPPORTED_RANGES = {
    "within_20": 20,
    "within_50": 50,
    "within_100": 100,
}
SUPPORTED_OPERATIONS = {"addition", "subtraction"}


@dataclass(frozen=True)
class SignedIntegerSettings:
    number_range: str
    operations: tuple[str, ...]

    @property
    def absolute_limit(self) -> int:
        return SUPPORTED_RANGES[self.number_range]


def load_settings(data: dict) -> SignedIntegerSettings:
    unexpected_keys = set(data) - {"number_range", "operations"}
    if unexpected_keys:
        names = ", ".join(sorted(unexpected_keys))
        raise ValueError(f"Plugin settings are not configurable online: {names}")
    number_ranges = tuple(data.get("number_range", ("within_20",)))
    settings = SignedIntegerSettings(
        number_range=str(number_ranges[0]) if number_ranges else "within_20",
        operations=tuple(data.get("operations", ("addition", "subtraction"))),
    )
    _validate_settings(settings, number_range_count=len(number_ranges))
    return settings


def _validate_settings(settings: SignedIntegerSettings, *, number_range_count: int) -> None:
    if number_range_count != 1 or settings.number_range not in SUPPORTED_RANGES:
        raise ValueError("Unsupported signed integer number range")
    if not settings.operations or set(settings.operations) - SUPPORTED_OPERATIONS:
        raise ValueError("Unsupported signed integer operation")
