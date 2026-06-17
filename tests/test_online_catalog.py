import unittest

from kids_exo.online.catalog import get_online_catalog, get_online_plugin
from kids_exo.online.session import OnlineSessionRequest, create_practice_session


class OnlinePluginCatalogTests(unittest.TestCase):
    def test_catalog_exposes_initial_online_mental_multiplication_plugins(self) -> None:
        catalog = get_online_catalog()

        self.assertEqual(catalog.default_locale, "en-CA")
        self.assertEqual(catalog.question_counts, (10, 20, 30, 40, 50, 100))
        self.assertEqual(catalog.feedback_modes, ("immediate", "deferred"))
        self.assertTrue(catalog.show_timer_configurable)
        self.assertEqual(
            tuple(plugin.plugin for plugin in catalog.plugins),
            (
                "multiply_by_11",
                "integer_multiplication_distributive",
                "same_tens_ones_sum_to_ten",
                "square_ending_in_5",
                "multiply_by_9_99_999",
                "multiply_by_5_25_125",
                "three_digit_same_prefix_ones_sum_to_ten",
                "tens_sum_to_ten_same_ones",
                "near_round_pair_multiplication",
                "difference_of_squares",
                "integer_signed_addition_subtraction",
                "chicken_rabbit_word_problems",
                "french_alphabet_sounds",
                "french_common_word_sounds",
                "french_common_word_spelling",
                "french_school_word_sounds",
                "french_school_word_spelling",
                "french_fruit_word_sounds",
                "french_fruit_word_spelling",
            ),
        )

    def test_multiply_by_11_schema_exposes_only_parent_configurable_settings(self) -> None:
        plugin = get_online_plugin("multiply_by_11")

        self.assertEqual(plugin.title, "Multiply by 11")
        self.assertEqual(plugin.default_locale, "en-CA")
        self.assertEqual(
            {coverage.locale for coverage in plugin.locale_coverage},
            {"en-CA", "zh-CN"},
        )
        self.assertEqual(
            tuple(setting.name for setting in plugin.settings),
            ("multiplicand_digits", "strategies"),
        )
        digits = plugin.settings[0]
        self.assertEqual(digits.control, "single_choice")
        self.assertEqual(tuple(option.value for option in digits.options), (2, 3))
        self.assertEqual(digits.default, (2,))

    def test_session_accepts_public_settings_and_applies_safe_internal_defaults(self) -> None:
        session = create_practice_session(
            OnlineSessionRequest(
                plugin="multiply_by_11",
                plugin_settings={
                    "multiplicand_digits": [3],
                    "strategies": ["with_carrying"],
                },
                question_count=10,
                seed=88,
            )
        )

        self.assertEqual(session.plugin_settings.multiplicand_digits, (3,))
        self.assertFalse(session.plugin_settings.allow_duplicates)
        self.assertEqual(
            session.plugin_settings.strategy_weights,
            {"with_carrying": 1.0},
        )
        self.assertTrue(all(question.strategy == "with_carrying" for question in session.questions))

    def test_session_rejects_internal_plugin_settings_from_a_web_request(self) -> None:
        with self.assertRaisesRegex(ValueError, "not configurable online"):
            create_practice_session(
                OnlineSessionRequest(
                    plugin="multiply_by_11",
                    plugin_settings={
                        "multiplicand_digits": [2],
                        "strategies": ["no_carrying"],
                        "allow_duplicates": True,
                    },
                    question_count=10,
                )
            )
        with self.assertRaisesRegex(ValueError, "not configurable online"):
            create_practice_session(
                OnlineSessionRequest(
                    plugin="integer_signed_addition_subtraction",
                    plugin_settings={
                        "number_range": ["within_20"],
                        "operations": ["addition"],
                        "absolute_limit": 999,
                    },
                    question_count=10,
                )
            )

    def test_new_online_plugins_expose_only_their_meaningful_settings(self) -> None:
        distributive = get_online_plugin("integer_multiplication_distributive")
        same_tens = get_online_plugin("same_tens_ones_sum_to_ten")
        squares = get_online_plugin("square_ending_in_5")
        nines = get_online_plugin("multiply_by_9_99_999")
        five_family = get_online_plugin("multiply_by_5_25_125")
        three_digit_prefix = get_online_plugin("three_digit_same_prefix_ones_sum_to_ten")
        tens_same_ones = get_online_plugin("tens_sum_to_ten_same_ones")
        near_round = get_online_plugin("near_round_pair_multiplication")
        difference = get_online_plugin("difference_of_squares")
        signed_integers = get_online_plugin("integer_signed_addition_subtraction")
        word_problems = get_online_plugin("chicken_rabbit_word_problems")
        french_alphabet = get_online_plugin("french_alphabet_sounds")
        french_common_words = get_online_plugin("french_common_word_sounds")
        french_spelling = get_online_plugin("french_common_word_spelling")
        french_school_words = get_online_plugin("french_school_word_sounds")
        french_school_spelling = get_online_plugin("french_school_word_spelling")
        french_fruit_words = get_online_plugin("french_fruit_word_sounds")
        french_fruit_spelling = get_online_plugin("french_fruit_word_spelling")

        self.assertEqual(distributive.title, "Distributive Property Multiplication")
        self.assertEqual(tuple(setting.name for setting in distributive.settings), ("strategies",))
        self.assertEqual(same_tens.title, "Same Tens, Ones Sum to 10")
        self.assertEqual(tuple(setting.name for setting in same_tens.settings), ("strategies",))
        self.assertEqual(squares.title, "Squares Ending in 5")
        self.assertEqual(tuple(setting.name for setting in squares.settings), ("strategies",))
        self.assertEqual(
            tuple(setting.name for setting in nines.settings),
            ("multiplicand_digits", "strategies"),
        )
        self.assertEqual(
            tuple(setting.name for setting in five_family.settings),
            ("multiplicand_digits", "strategies"),
        )
        self.assertEqual(
            tuple(setting.name for setting in three_digit_prefix.settings),
            ("strategies",),
        )
        self.assertEqual(
            tuple(setting.name for setting in tens_same_ones.settings),
            ("strategies",),
        )
        self.assertEqual(
            tuple(setting.name for setting in near_round.settings),
            ("strategies",),
        )
        self.assertEqual(
            tuple(setting.name for setting in difference.settings),
            ("strategies",),
        )
        self.assertEqual(signed_integers.subject, "Math")
        self.assertEqual(signed_integers.category, "Integer Arithmetic")
        self.assertEqual(signed_integers.answer_types, ("signed_integer_exact",))
        self.assertEqual(
            tuple(setting.name for setting in signed_integers.settings),
            ("number_range", "operations"),
        )
        self.assertEqual(word_problems.subject, "Math")
        self.assertEqual(word_problems.category, "Word Problems")
        self.assertEqual(word_problems.title, "Chicken and Rabbit Word Problems")
        self.assertEqual(word_problems.supported_delivery_modes, ("web_practice",))
        self.assertEqual(word_problems.answer_types, ("structured_word_problem",))
        self.assertEqual(tuple(setting.name for setting in word_problems.settings), ("difficulty",))
        self.assertEqual(french_alphabet.subject, "French")
        self.assertEqual(french_alphabet.category, "Pronunciation")
        self.assertEqual(
            tuple(setting.name for setting in french_alphabet.settings),
            ("strategies",),
        )
        self.assertEqual(
            tuple(option.value for option in french_alphabet.settings[0].options),
            ("letter_name_to_letter",),
        )
        self.assertEqual(french_alphabet.answer_types, ("multiple_choice_index",))
        self.assertEqual(french_common_words.subject, "French")
        self.assertEqual(french_common_words.category, "Pronunciation")
        self.assertEqual(french_common_words.title, "French Family Word Sounds")
        self.assertEqual(
            tuple(option.value for option in french_common_words.settings[0].options),
            ("family_words",),
        )
        self.assertEqual(french_common_words.answer_types, ("multiple_choice_index",))
        self.assertEqual(french_spelling.subject, "French")
        self.assertEqual(french_spelling.category, "Spelling")
        self.assertEqual(french_spelling.title, "French Family Word Spelling")
        self.assertEqual(french_spelling.answer_types, ("spelling_text",))
        self.assertEqual(french_spelling.supported_delivery_modes, ("web_practice",))
        self.assertEqual(tuple(setting.name for setting in french_spelling.settings), ("strategy",))
        self.assertEqual(
            tuple(option.value for option in french_spelling.settings[0].options),
            ("dictation", "translation", "combined"),
        )
        self.assertEqual(french_school_words.subject, "French")
        self.assertEqual(french_school_words.category, "Pronunciation")
        self.assertEqual(french_school_words.title, "French School Word Sounds")
        self.assertEqual(
            tuple(option.value for option in french_school_words.settings[0].options),
            ("school_words",),
        )
        self.assertEqual(french_school_words.answer_types, ("multiple_choice_index",))
        self.assertEqual(french_school_spelling.subject, "French")
        self.assertEqual(french_school_spelling.category, "Spelling")
        self.assertEqual(french_school_spelling.title, "French School Word Spelling")
        self.assertEqual(french_school_spelling.answer_types, ("spelling_text",))
        self.assertEqual(french_fruit_words.subject, "French")
        self.assertEqual(french_fruit_words.category, "Pronunciation")
        self.assertEqual(french_fruit_words.title, "French Fruit Word Sounds")
        self.assertEqual(
            tuple(option.value for option in french_fruit_words.settings[0].options),
            ("fruit_words",),
        )
        self.assertEqual(french_fruit_words.answer_types, ("multiple_choice_index",))
        self.assertEqual(french_fruit_spelling.subject, "French")
        self.assertEqual(french_fruit_spelling.category, "Spelling")
        self.assertEqual(french_fruit_spelling.title, "French Fruit Word Spelling")
        self.assertEqual(french_fruit_spelling.answer_types, ("spelling_text",))


if __name__ == "__main__":
    unittest.main()
