from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
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
