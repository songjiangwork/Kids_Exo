import unittest

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet


class ThreeDigitMultiplyBy11GenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preset = load_preset("presets/multiply_by_11_three_digit_beginner.toml")

    def test_preset_reuses_the_plugin_and_has_thirty_practice_questions(self) -> None:
        self.assertEqual(self.preset.sections[0].plugin, "multiply_by_11")
        self.assertEqual(self.preset.sections[0].settings.multiplicand_digits, (3,))
        self.assertEqual(self.preset.sections[1].count, 30)

    def test_warmup_explains_adjacent_sums_and_carrying_in_english(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=115)
        intro = worksheet.section_intros["warmup"]

        self.assertIn("Add each pair of neighbouring digits.", intro[0])
        self.assertIn("Work from right to left", intro[1])
        self.assertIn("Example: 386 x 11", intro[2])
        self.assertIn("write 4 carry 1", intro[2])
        self.assertTrue(
            all("+ carry" in question.display_text for question in worksheet.sections["warmup"])
        )

    def test_practice_balances_questions_with_and_without_carrying(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=221)
        practice = worksheet.sections["practice"]

        self.assertEqual(len(practice), 30)
        self.assertEqual(
            {
                strategy: sum(question.strategy == strategy for question in practice)
                for strategy in ("no_carrying", "with_carrying")
            },
            {"no_carrying": 15, "with_carrying": 15},
        )

    def test_strategy_matches_adjacent_digit_sums_for_three_digit_numbers(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=19)
        expressions = [question.expression for question in worksheet.all_questions]

        self.assertEqual(len(expressions), len(set(expressions)))
        for question in worksheet.all_questions:
            self.assertGreaterEqual(question.left_operand, 100)
            self.assertLess(question.left_operand, 1000)
            digits = [int(character) for character in str(question.left_operand)]
            adjacent_sums = [digits[index] + digits[index + 1] for index in range(2)]
            if question.strategy == "no_carrying":
                self.assertTrue(all(total < 10 for total in adjacent_sums))
            else:
                self.assertTrue(any(total >= 10 for total in adjacent_sums))
            self.assertEqual(question.right_operand, 11)


if __name__ == "__main__":
    unittest.main()
