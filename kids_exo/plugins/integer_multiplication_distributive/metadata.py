from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
    plugin="integer_multiplication_distributive",
    subject="Math",
    category="Mental Multiplication",
    title="Distributive Property Multiplication",
    description="Break apart a two-digit factor to multiply faster with addition or near-round subtraction.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice", "warmup")),),
    settings=(
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("place_value_addition", "near_round_number_subtraction"),
            options=(
                SettingOption("place_value_addition", "Break apart by place value"),
                SettingOption("near_round_number_subtraction", "Use a near-round shortcut"),
            ),
        ),
    ),
)
