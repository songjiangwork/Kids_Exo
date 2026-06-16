from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
    plugin="chicken_rabbit_word_problems",
    subject="Math",
    category="Word Problems",
    title="Chicken and Rabbit Word Problems",
    description=(
        "Solve two-quantity word problems using total count and total units "
        "such as legs, wheels, sides, or other repeated units."
    ),
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice",)),),
    settings=(
        PluginSettingSchema(
            name="difficulty",
            label="Difficulty",
            control="single_choice",
            default=("intro",),
            options=(
                SettingOption("intro", "Intro"),
                SettingOption("mixed", "Mixed"),
            ),
        ),
    ),
    supported_delivery_modes=("web_practice",),
    answer_types=("structured_word_problem",),
    release_stage="experimental",
)
