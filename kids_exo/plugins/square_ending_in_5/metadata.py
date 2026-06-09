from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
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
