from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
    plugin="near_round_pair_multiplication",
    subject="Math",
    category="Mental Multiplication",
    title="Near Round-Number Pair Multiplication",
    description="Multiply pairs near the same round number from above or below.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice", "warmup")),),
    settings=(
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("both_below_round", "both_above_round"),
            options=(
                SettingOption("both_below_round", "Both factors below the round number"),
                SettingOption("both_above_round", "Both factors above the round number"),
            ),
        ),
    ),
)
