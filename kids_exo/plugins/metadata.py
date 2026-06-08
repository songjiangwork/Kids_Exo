from dataclasses import dataclass


@dataclass(frozen=True)
class SettingOption:
    value: int | str
    label: str


@dataclass(frozen=True)
class PluginSettingSchema:
    name: str
    label: str
    control: str
    default: tuple[int | str, ...]
    options: tuple[SettingOption, ...]


@dataclass(frozen=True)
class LocaleCoverage:
    locale: str
    full_sections: tuple[str, ...]
    partial_sections: tuple[str, ...] = ()


@dataclass(frozen=True)
class PluginMetadata:
    plugin: str
    subject: str
    category: str
    title: str
    description: str
    default_locale: str
    locale_coverage: tuple[LocaleCoverage, ...]
    settings: tuple[PluginSettingSchema, ...]
    supported_delivery_modes: tuple[str, ...] = ("web_practice", "pdf_printable")
    answer_types: tuple[str, ...] = ("integer_exact",)
    release_stage: str = "published"


OnlinePluginDescriptor = PluginMetadata


@dataclass(frozen=True)
class OnlineCatalog:
    default_locale: str
    question_counts: tuple[int, ...]
    feedback_modes: tuple[str, ...]
    show_timer_configurable: bool
    plugins: tuple[PluginMetadata, ...]
