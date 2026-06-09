from kids_exo.plugins.metadata import (
    LocaleCoverage,
    PluginMetadata,
    PluginSettingSchema,
    SettingOption,
)
from kids_exo.plugins.french_alphabet_sounds.metadata import (
    PLUGIN_METADATA as FRENCH_ALPHABET_SOUNDS,
)
from kids_exo.plugins.multiply_by_11.metadata import PLUGIN_METADATA as MULTIPLY_BY_11

DISTRIBUTIVE_PROPERTY = PluginMetadata(
    plugin="integer_multiplication_distributive",
    subject="Math",
    category="Mental Multiplication",
    title="Distributive Property Multiplication",
    description="Break apart a two-digit factor to multiply faster with addition or near-round subtraction.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice", "warmup")),),
    settings=(
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("place_value_addition", "near_round_number_subtraction"),
            options=(
                SettingOption("place_value_addition", "Break apart by place value"),
                SettingOption("near_round_number_subtraction", "Use a near-round shortcut"),
            ),
        ),
    ),
)

SAME_TENS_ONES_SUM_TO_TEN = PluginMetadata(
    plugin="same_tens_ones_sum_to_ten",
    subject="Math",
    category="Mental Multiplication",
    title="Same Tens, Ones Sum to 10",
    description="Multiply two two-digit numbers with matching tens and ones that total 10.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice", "warmup")),),
    settings=(
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("zero_padded_ones_product", "two_digit_ones_product"),
            options=(
                SettingOption("zero_padded_ones_product", "Products needing a leading zero"),
                SettingOption("two_digit_ones_product", "Two-digit ending products"),
            ),
        ),
    ),
)

SQUARE_ENDING_IN_5 = PluginMetadata(
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

MULTIPLY_BY_NINES = PluginMetadata(
    plugin="multiply_by_9_99_999",
    subject="Math",
    category="Mental Multiplication",
    title="Multiply by 9, 99, and 999",
    description="Use a round-number subtraction shortcut to multiply by strings of nines.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice", "warmup")),),
    settings=(
        PluginSettingSchema(
            name="multiplicand_digits",
            label="Number of digits",
            control="single_choice",
            default=(2,),
            options=(SettingOption(2, "Two digits"),),
        ),
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("times_9", "times_99", "times_999"),
            options=(
                SettingOption("times_9", "Multiply by 9"),
                SettingOption("times_99", "Multiply by 99"),
                SettingOption("times_999", "Multiply by 999"),
            ),
        ),
    ),
)

MULTIPLY_BY_FIVE_FAMILY = PluginMetadata(
    plugin="multiply_by_5_25_125",
    subject="Math",
    category="Mental Multiplication",
    title="Multiply by 5, 25, and 125",
    description="Use halving and scaling shortcuts to multiply by 5, 25, or 125.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice", "warmup")),),
    settings=(
        PluginSettingSchema(
            name="multiplicand_digits",
            label="Number of digits",
            control="single_choice",
            default=(2,),
            options=(SettingOption(2, "Two digits"),),
        ),
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("times_5", "times_25", "times_125"),
            options=(
                SettingOption("times_5", "Multiply by 5"),
                SettingOption("times_25", "Multiply by 25"),
                SettingOption("times_125", "Multiply by 125"),
            ),
        ),
    ),
)

THREE_DIGIT_SAME_PREFIX = PluginMetadata(
    plugin="three_digit_same_prefix_ones_sum_to_ten",
    subject="Math",
    category="Mental Multiplication",
    title="Three-Digit Same Prefix, Ones Sum to 10",
    description="Multiply three-digit numbers with the same front part and ones that add to 10.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice", "warmup")),),
    settings=(
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("zero_padded_ones_product", "two_digit_ones_product"),
            options=(
                SettingOption("zero_padded_ones_product", "Products needing a leading zero"),
                SettingOption("two_digit_ones_product", "Two-digit ending products"),
            ),
        ),
    ),
)

TENS_SUM_TO_TEN_SAME_ONES = PluginMetadata(
    plugin="tens_sum_to_ten_same_ones",
    subject="Math",
    category="Mental Multiplication",
    title="Tens Sum to 10, Same Ones",
    description="Multiply two-digit numbers whose tens add to 10 while the ones digits match.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice", "warmup")),),
    settings=(
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("zero_padded_ones_square", "two_digit_ones_square"),
            options=(
                SettingOption("zero_padded_ones_square", "Endings needing a leading zero"),
                SettingOption("two_digit_ones_square", "Two-digit ending squares"),
            ),
        ),
    ),
)

NEAR_ROUND_PAIR = PluginMetadata(
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

DIFFERENCE_OF_SQUARES = PluginMetadata(
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

FRENCH_COMMON_WORD_SOUNDS = PluginMetadata(
    plugin="french_common_word_sounds",
    subject="French",
    category="Pronunciation",
    title="French Common Word Sounds",
    description="Listen to French family words, then choose the matching word and meaning.",
    default_locale="en-CA",
    locale_coverage=(LocaleCoverage("en-CA", ("practice",)),),
    settings=(
        PluginSettingSchema(
            name="strategies",
            label="Question types",
            control="multiple_choice",
            default=("family_words",),
            options=(SettingOption("family_words", "Family words"),),
        ),
    ),
    supported_delivery_modes=("web_practice",),
    answer_types=("multiple_choice_index",),
)

ENABLED_ONLINE_PLUGIN_METADATA: tuple[PluginMetadata, ...] = (
    MULTIPLY_BY_11,
    DISTRIBUTIVE_PROPERTY,
    SAME_TENS_ONES_SUM_TO_TEN,
    SQUARE_ENDING_IN_5,
    MULTIPLY_BY_NINES,
    MULTIPLY_BY_FIVE_FAMILY,
    THREE_DIGIT_SAME_PREFIX,
    TENS_SUM_TO_TEN_SAME_ONES,
    NEAR_ROUND_PAIR,
    DIFFERENCE_OF_SQUARES,
    FRENCH_ALPHABET_SOUNDS,
    FRENCH_COMMON_WORD_SOUNDS,
)
