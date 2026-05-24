import unittest

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet


class SameTensOnesSumToTenGenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preset = load_preset("presets/same_tens_ones_sum_to_ten_beginner.toml")

    def test_preset_uses_the_plugin_and_thirty_practice_questions(self) -> None:
        self.assertEqual(self.preset.sections[0].plugin, "same_tens_ones_sum_to_ten")
        self.assertEqual(self.preset.sections[1].count, 30)

    def test_warmup_explains_the_rule_and_balances_zero_padding(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=311)
        warmup = worksheet.sections["warmup"]
        introduction = " ".join(worksheet.section_intros["warmup"])

        self.assertIn("Multiply the tens digit by the next number.", introduction)
        self.assertIn("Keep the last part as two digits.", introduction)
        self.assertIn("Example: 43 x 47", introduction)
        self.assertEqual(
            {
                strategy: sum(question.strategy == strategy for question in warmup)
                for strategy in ("zero_padded_ones_product", "two_digit_ones_product")
            },
            {"zero_padded_ones_product": 2, "two_digit_ones_product": 2},
        )
        self.assertTrue(all("answer" in question.display_text for question in warmup))
        self.assertTrue(
            all(
                "write two digits" in question.display_text
                for question in warmup
                if question.strategy == "zero_padded_ones_product"
            )
        )

    def test_practice_has_equal_zero_padded_and_two_digit_tail_products(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=912)
        practice = worksheet.sections["practice"]

        self.assertEqual(len(practice), 30)
        self.assertEqual(
            {
                strategy: sum(question.strategy == strategy for question in practice)
                for strategy in ("zero_padded_ones_product", "two_digit_ones_product")
            },
            {"zero_padded_ones_product": 15, "two_digit_ones_product": 15},
        )

    def test_generated_operands_have_same_tens_and_ones_sum_to_ten(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=415)
        expressions = [question.expression for question in worksheet.all_questions]

        self.assertEqual(len(expressions), len(set(expressions)))
        for question in worksheet.all_questions:
            left_tens, left_ones = divmod(question.left_operand, 10)
            right_tens, right_ones = divmod(question.right_operand, 10)
            self.assertEqual(left_tens, right_tens)
            self.assertEqual(left_ones + right_ones, 10)
            if question.strategy == "zero_padded_ones_product":
                self.assertLess(left_ones * right_ones, 10)
            else:
                self.assertGreaterEqual(left_ones * right_ones, 10)


if __name__ == "__main__":
    unittest.main()
