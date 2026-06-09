from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
    plugin="multiply_by_5_25_125",
    subject="Math",
    category="Mental Multiplication",
    title="Multiply by 5, 25, and 125",
    description="Use halving and scaling shortcuts to multiply by 5, 25, or 125.",
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
            default=("times_5", "times_25", "times_125"),
            options=(
                SettingOption("times_5", "Multiply by 5"),
                SettingOption("times_25", "Multiply by 25"),
                SettingOption("times_125", "Multiply by 125"),
            ),
        ),
    ),
)
