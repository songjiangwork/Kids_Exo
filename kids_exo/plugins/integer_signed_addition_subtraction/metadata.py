from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
    plugin="integer_signed_addition_subtraction",
    subject="Math",
    category="Integer Arithmetic",
    title="Signed Integer Addition and Subtraction",
    description="Practise adding and subtracting positive and negative integers.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice",)),),
    settings=(
        PluginSettingSchema(
            name="number_range",
            label="Number range",
            control="single_choice",
            default=("within_20",),
            options=(
                SettingOption("within_20", "-20 to 20"),
                SettingOption("within_50", "-50 to 50"),
                SettingOption("within_100", "-100 to 100"),
            ),
        ),
        PluginSettingSchema(
            name="operations",
            label="Operations",
            control="multiple_choice",
            default=("addition", "subtraction"),
            options=(
                SettingOption("addition", "Addition"),
                SettingOption("subtraction", "Subtraction"),
            ),
        ),
    ),
    supported_delivery_modes=("web_practice",),
    answer_types=("signed_integer_exact",),
)
