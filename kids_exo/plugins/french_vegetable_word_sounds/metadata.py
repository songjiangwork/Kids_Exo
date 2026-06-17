from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
    plugin="french_vegetable_word_sounds",
    subject="French",
    category="Pronunciation",
    title="French Vegetable Word Sounds",
    description="Listen to French vegetable words, then choose the matching word and meaning.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice",)),),
    settings=(
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("vegetable_words",),
            options=(SettingOption("vegetable_words", "Vegetable words"),),
        ),
    ),
    supported_delivery_modes=("web_practice",),
    answer_types=("multiple_choice_index",),
    release_stage="experimental",
)
