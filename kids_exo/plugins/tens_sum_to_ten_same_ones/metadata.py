from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
    plugin="tens_sum_to_ten_same_ones",
    subject="Math",
    category="Mental Multiplication",
    title="Tens Sum to 10, Same Ones",
    description="Multiply two-digit numbers whose tens add to 10 while the ones digits match.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice", "warmup")),),
    settings=(
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("zero_padded_ones_square", "two_digit_ones_square"),
            options=(
                SettingOption("zero_padded_ones_square", "Endings needing a leading zero"),
                SettingOption("two_digit_ones_square", "Two-digit ending squares"),
            ),
        ),
    ),
)
