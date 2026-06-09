from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
    plugin="three_digit_same_prefix_ones_sum_to_ten",
    subject="Math",
    category="Mental Multiplication",
    title="Three-Digit Same Prefix, Ones Sum to 10",
    description="Multiply three-digit numbers with the same front part and ones that add to 10.",
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
