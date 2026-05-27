from dataclasses import dataclass
from typing import Any

from kids_exo.plugins.registry import get_plugin_definition


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
class OnlinePluginDescriptor:
    plugin: str
    subject: str
    category: str
    title: str
    description: str
    default_locale: str
    locale_coverage: tuple[LocaleCoverage, ...]
    settings: tuple[PluginSettingSchema, ...]


@dataclass(frozen=True)
class OnlineCatalog:
    default_locale: str
    question_counts: tuple[int, ...]
    feedback_modes: tuple[str, ...]
    show_timer_configurable: bool
    plugins: tuple[OnlinePluginDescriptor, ...]


_MULTIPLY_BY_11 = OnlinePluginDescriptor(
    plugin="multiply_by_11",
    subject="Math",
    category="Mental Multiplication",
    title="Multiply by 11",
    description="Practise multiplying a two- or three-digit number by 11.",
    default_locale="en-CA",
    locale_coverage=(
        LocaleCoverage("en-CA", ("practice", "warmup")),
        LocaleCoverage("zh-CN", (), ("warmup",)),
    ),
    settings=(
        PluginSettingSchema(
            name="multiplicand_digits",
            label="Number of digits",
            control="single_choice",
            default=(2,),
            options=(
                SettingOption(2, "Two digits"),
                SettingOption(3, "Three digits"),
            ),
        ),
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("no_carrying", "with_carrying"),
            options=(
                SettingOption("no_carrying", "Without carrying"),
                SettingOption("with_carrying", "With carrying"),
            ),
        ),
    ),
)

_SAME_TENS_ONES_SUM_TO_TEN = OnlinePluginDescriptor(
    plugin="same_tens_ones_sum_to_ten",
    subject="Math",
    category="Mental Multiplication",
    title="Same Tens, Ones Sum to 10",
    description="Multiply two two-digit numbers with matching tens and ones that total 10.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice", "warmup")),),
    settings=(
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("zero_padded_ones_product", "two_digit_ones_product"),
            options=(
                SettingOption("zero_padded_ones_product", "Products needing a leading zero"),
                SettingOption("two_digit_ones_product", "Two-digit ending products"),
            ),
        ),
    ),
)

_SQUARE_ENDING_IN_5 = OnlinePluginDescriptor(
    plugin="square_ending_in_5",
    subject="Math",
    category="Mental Multiplication",
    title="Squares Ending in 5",
    description="Square two-digit numbers that end in 5 using the ending-in-25 shortcut.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice", "warmup")),),
    settings=(
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("ending_in_5_square",),
            options=(SettingOption("ending_in_5_square", "Squares ending in 5"),),
        ),
    ),
)

_MULTIPLY_BY_NINES = OnlinePluginDescriptor(
    plugin="multiply_by_9_99_999",
    subject="Math",
    category="Mental Multiplication",
    title="Multiply by 9, 99, and 999",
    description="Use a round-number subtraction shortcut to multiply by strings of nines.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice", "warmup")),),
    settings=(
        PluginSettingSchema(
            name="multiplicand_digits",
            label="Number of digits",
            control="single_choice",
            default=(2,),
            options=(SettingOption(2, "Two digits"),),
        ),
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("times_9", "times_99", "times_999"),
            options=(
                SettingOption("times_9", "Multiply by 9"),
                SettingOption("times_99", "Multiply by 99"),
                SettingOption("times_999", "Multiply by 999"),
            ),
        ),
    ),
)

_ONLINE_CATALOG = OnlineCatalog(
    default_locale="en-CA",
    question_counts=(10, 20, 30),
    feedback_modes=("immediate", "deferred"),
    show_timer_configurable=True,
    plugins=(
        _MULTIPLY_BY_11,
        _SAME_TENS_ONES_SUM_TO_TEN,
        _SQUARE_ENDING_IN_5,
        _MULTIPLY_BY_NINES,
    ),
)


def get_online_catalog() -> OnlineCatalog:
    return _ONLINE_CATALOG


def get_online_plugin(plugin_name: str) -> OnlinePluginDescriptor:
    for plugin in _ONLINE_CATALOG.plugins:
        if plugin.plugin == plugin_name:
            return plugin
    raise ValueError(f"Plugin is not enabled for online practice: {plugin_name}")


def load_online_plugin_settings(plugin_name: str, values: dict[str, Any]):
    """Validate public settings before handing them to an existing plugin."""

    descriptor = get_online_plugin(plugin_name)
    schemas = {setting.name: setting for setting in descriptor.settings}
    unexpected_keys = set(values) - set(schemas)
    if unexpected_keys:
        names = ", ".join(sorted(unexpected_keys))
        raise ValueError(f"Plugin settings are not configurable online: {names}")
    merged_values = {
        name: list(schema.default)
        for name, schema in schemas.items()
    }
    merged_values.update(values)
    definition = get_plugin_definition(plugin_name)
    return definition.load_settings(merged_values)
