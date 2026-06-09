from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)


PLUGIN_METADATA = PluginMetadata(
    plugin="multiply_by_11",
    subject="Math",
    category="Mental Multiplication",
    title="Multiply by 11",
    description="Practise multiplying a two- or three-digit number by 11.",
    default_locale="en-CA",
    locale_coverage=(
        LocaleCoverage("en-CA", ("practice", "warmup")),
        LocaleCoverage("zh-CN", (), ("warmup",)),
    ),
    settings=(
        PluginSettingSchema(
            name="multiplicand_digits",
            label="Number of digits",
            control="single_choice",
            default=(2,),
            options=(
                SettingOption(2, "Two digits"),
                SettingOption(3, "Three digits"),
            ),
        ),
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("no_carrying", "with_carrying"),
            options=(
                SettingOption("no_carrying", "Without carrying"),
                SettingOption("with_carrying", "With carrying"),
            ),
        ),
    ),
)
