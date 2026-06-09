from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
    plugin="difference_of_squares",
    subject="Math",
    category="Mental Multiplication",
    title="Difference of Squares",
    description="Use symmetric factors around a round number to multiply quickly.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice", "warmup")),),
    settings=(
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("symmetric_around_round",),
            options=(SettingOption("symmetric_around_round", "Symmetric factors around a round number"),),
        ),
    ),
)
