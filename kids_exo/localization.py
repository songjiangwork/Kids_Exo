from dataclasses import dataclass
from pathlib import Path
import tomllib


DEFAULT_LOCALE = "en-CA"


@dataclass(frozen=True)
class LocalizedText:
    text: str
    locale: str
    used_fallback: bool = False


@dataclass(frozen=True)
class LocalizedPresentation:
    heading: LocalizedText
    instructions: tuple[LocalizedText, ...]

    @property
    def fallback_keys(self) -> tuple[str, ...]:
        pairs = (("heading", self.heading),) + tuple(
            (f"instruction_{index}", text)
            for index, text in enumerate(self.instructions, start=1)
        )
        return tuple(key for key, value in pairs if value.used_fallback)

    def plain_text(self) -> tuple[str, tuple[str, ...]]:
        return self.heading.text, tuple(text.text for text in self.instructions)


def resolve_presentation(
    resources_directory: str | Path,
    resource_group: str,
    requested_locale: str,
    default_locale: str = DEFAULT_LOCALE,
) -> LocalizedPresentation:
    """Resolve plugin-owned teaching text while allowing partial translations."""

    directory = Path(resources_directory)
    default_values = _load_group(directory / f"{default_locale}.toml", resource_group)
    requested_values = (
        default_values
        if requested_locale == default_locale
        else _load_optional_group(directory / f"{requested_locale}.toml", resource_group)
    )
    required_instruction_keys = tuple(
        sorted(
            (key for key in default_values if key.startswith("instruction_")),
            key=lambda key: int(key.rsplit("_", 1)[1]),
        )
    )
    if "heading" not in default_values or not required_instruction_keys:
        raise ValueError(
            f"Default locale resource is incomplete for presentation: {resource_group}"
        )

    heading = _resolve_value(
        "heading", requested_values, default_values, requested_locale, default_locale
    )
    instructions = tuple(
        _resolve_value(
            key, requested_values, default_values, requested_locale, default_locale
        )
        for key in required_instruction_keys
    )
    return LocalizedPresentation(heading=heading, instructions=instructions)


def _resolve_value(
    key: str,
    requested_values: dict[str, str],
    default_values: dict[str, str],
    requested_locale: str,
    default_locale: str,
) -> LocalizedText:
    if key in requested_values:
        return LocalizedText(requested_values[key], requested_locale)
    try:
        text = default_values[key]
    except KeyError as exc:
        raise ValueError(f"Missing required localized text key: {key}") from exc
    return LocalizedText(text, default_locale, requested_locale != default_locale)


def _load_group(path: Path, resource_group: str) -> dict[str, str]:
    if not path.exists():
        raise ValueError(f"Missing default locale resource: {path}")
    with path.open("rb") as resource_file:
        data = tomllib.load(resource_file)
    group = _nested_group(data, resource_group)
    if not isinstance(group, dict):
        raise ValueError(f"Invalid localized presentation group: {resource_group}")
    return {str(key): str(value) for key, value in group.items()}


def _load_optional_group(path: Path, resource_group: str) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open("rb") as resource_file:
        data = tomllib.load(resource_file)
    group = _nested_group(data, resource_group)
    if group is None:
        return {}
    if not isinstance(group, dict):
        raise ValueError(f"Invalid localized presentation group: {resource_group}")
    return {str(key): str(value) for key, value in group.items()}


def _nested_group(data: dict, resource_group: str):
    value = data
    for part in resource_group.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value
