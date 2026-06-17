from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
    plugin="french_meat_word_sounds",
    subject="French",
    category="Pronunciation",
    title="French Meat Word Sounds",
    description="Listen to French meat words, then choose the matching word and meaning.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice",)),),
    settings=(
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("meat_words",),
            options=(SettingOption("meat_words", "Meat words"),),
        ),
    ),
    supported_delivery_modes=("web_practice",),
    answer_types=("multiple_choice_index",),
    release_stage="experimental",
)
