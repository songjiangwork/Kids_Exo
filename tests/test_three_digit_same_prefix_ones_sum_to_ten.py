import unittest

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet
from kids_exo.plugins.same_tens_ones_sum_to_ten.plugin import (
    SameTensOnesSumToTenPlugin,
)
from kids_exo.plugins.three_digit_same_prefix_ones_sum_to_ten.plugin import (
    ThreeDigitSamePrefixOnesSumToTenPlugin,
)


class ThreeDigitSamePrefixOnesSumToTenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preset = load_preset(
            "presets/three_digit_same_prefix_ones_sum_to_ten_beginner.toml"
        )

    def test_plugin_extends_the_shared_same_prefix_rule(self) -> None:
        self.assertTrue(
            issubclass(ThreeDigitSamePrefixOnesSumToTenPlugin, SameTensOnesSumToTenPlugin)
        )

    def test_preset_has_thirty_balanced_practice_questions(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=127)
        practice = worksheet.sections["practice"]

        self.assertEqual(len(practice), 30)
        self.assertEqual(
            {
                strategy: sum(question.strategy == strategy for question in practice)
                for strategy in ("zero_padded_ones_product", "two_digit_ones_product")
            },
            {"zero_padded_ones_product": 15, "two_digit_ones_product": 15},
        )

    def test_warmup_explains_the_matching_prefix_shortcut(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=123)
        introduction = " ".join(worksheet.section_intros["warmup"])

        self.assertIn("Use the matching first two digits.", introduction)
        self.assertIn("Example: 123 x 127", introduction)
        self.assertTrue(
            all("answer" in question.display_text for question in worksheet.sections["warmup"])
        )

    def test_questions_are_three_digit_products_with_matching_prefixes(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=321)
        expressions = [question.expression for question in worksheet.all_questions]

        self.assertEqual(len(expressions), len(set(expressions)))
        for question in worksheet.all_questions:
            left_prefix, left_ones = divmod(question.left_operand, 10)
            right_prefix, right_ones = divmod(question.right_operand, 10)
            self.assertGreaterEqual(question.left_operand, 100)
            self.assertEqual(left_prefix, right_prefix)
            self.assertEqual(left_ones + right_ones, 10)
            if question.strategy == "zero_padded_ones_product":
                self.assertLess(left_ones * right_ones, 10)
            else:
                self.assertGreaterEqual(left_ones * right_ones, 10)


if __name__ == "__main__":
    unittest.main()
