from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
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
