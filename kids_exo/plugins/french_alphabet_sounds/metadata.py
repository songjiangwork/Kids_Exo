from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
    plugin="french_alphabet_sounds",
    subject="French",
    category="Pronunciation",
    title="French Alphabet Sounds",
    description="Listen to French letter names, then choose the matching letter.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice",)),),
    settings=(
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("letter_name_to_letter",),
            options=(
                SettingOption("letter_name_to_letter", "French letter names"),
            ),
        ),
    ),
    supported_delivery_modes=("web_practice",),
    answer_types=("multiple_choice_index",),
)
