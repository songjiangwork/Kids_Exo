import unittest

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet


class TensSumToTenSameOnesGenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preset = load_preset("presets/tens_sum_to_ten_same_ones_beginner.toml")

    def test_preset_uses_the_plugin_and_thirty_practice_questions(self) -> None:
        self.assertEqual(self.preset.sections[0].plugin, "tens_sum_to_ten_same_ones")
        self.assertEqual(self.preset.sections[1].count, 30)

    def test_warmup_explains_the_rule_and_balances_zero_padding(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=1010)
        warmup = worksheet.sections["warmup"]
        introduction = " ".join(worksheet.section_intros["warmup"])

        self.assertIn("Add the shared ones digit.", introduction)
        self.assertIn("Keep the last part as two digits.", introduction)
        self.assertIn("Example: 43 x 63", introduction)
        self.assertEqual(
            {
                strategy: sum(question.strategy == strategy for question in warmup)
                for strategy in ("zero_padded_ones_square", "two_digit_ones_square")
            },
            {"zero_padded_ones_square": 2, "two_digit_ones_square": 2},
        )
        self.assertTrue(all("answer" in question.display_text for question in warmup))
        self.assertTrue(
            all(
                "write two digits" in question.display_text
                for question in warmup
                if question.strategy == "zero_padded_ones_square"
            )
        )

    def test_practice_balances_zero_padded_and_two_digit_tail_squares(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=1063)
        practice = worksheet.sections["practice"]

        self.assertEqual(len(practice), 30)
        self.assertEqual(
            {
                strategy: sum(question.strategy == strategy for question in practice)
                for strategy in ("zero_padded_ones_square", "two_digit_ones_square")
            },
            {"zero_padded_ones_square": 15, "two_digit_ones_square": 15},
        )

    def test_generated_operands_have_tens_sum_to_ten_and_matching_ones(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=4363)
        expressions = [question.expression for question in worksheet.all_questions]

        self.assertEqual(len(expressions), len(set(expressions)))
        for question in worksheet.all_questions:
            left_tens, left_ones = divmod(question.left_operand, 10)
            right_tens, right_ones = divmod(question.right_operand, 10)
            self.assertEqual(left_tens + right_tens, 10)
            self.assertEqual(left_ones, right_ones)
            if question.strategy == "zero_padded_ones_square":
                self.assertLess(left_ones * right_ones, 10)
            else:
                self.assertGreaterEqual(left_ones * right_ones, 10)


if __name__ == "__main__":
    unittest.main()
