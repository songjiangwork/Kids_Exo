from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
    plugin="french_vegetable_word_spelling",
    subject="French",
    category="Spelling",
    title="French Vegetable Word Spelling",
    description="Practice spelling French vegetable words from audio, English meaning, or both.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice",)),),
    settings=(
        PluginSettingSchema(
            name="strategy",
            label="Question type",
            control="single_choice",
            default=("combined",),
            options=(
                SettingOption("dictation", "Dictation: listen and spell"),
                SettingOption("translation", "Translation: see the meaning and spell"),
                SettingOption("combined", "Combined: see the meaning and listen, then spell"),
            ),
        ),
    ),
    supported_delivery_modes=("web_practice",),
    answer_types=("spelling_text",),
    release_stage="experimental",
)
