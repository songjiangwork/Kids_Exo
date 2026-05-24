import unittest

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet


class MultiplyByNinesGenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preset = load_preset("presets/multiply_by_9_99_999_beginner.toml")

    def test_preset_uses_the_plugin_and_balances_thirty_practice_questions(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=999)
        practice = worksheet.sections["practice"]

        self.assertEqual(self.preset.sections[0].plugin, "multiply_by_9_99_999")
        self.assertEqual(len(practice), 30)
        self.assertEqual(
            {
                multiplier: sum(question.right_operand == multiplier for question in practice)
                for multiplier in (9, 99, 999)
            },
            {9: 10, 99: 10, 999: 10},
        )

    def test_warmup_explains_one_less_than_a_power_of_ten(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=99)
        warmup = worksheet.sections["warmup"]

        self.assertIn("one less than 10, 100, or 1000", worksheet.section_intros["warmup"][0])
        self.assertEqual({question.right_operand for question in warmup}, {9, 99, 999})
        self.assertTrue(all(" - 1)" in question.display_text for question in warmup))

    def test_generated_questions_use_supported_nines_without_duplicates(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=9)
        expressions = [question.expression for question in worksheet.all_questions]

        self.assertEqual(len(expressions), len(set(expressions)))
        for question in worksheet.all_questions:
            self.assertIn(question.right_operand, (9, 99, 999))
            self.assertGreaterEqual(question.left_operand, 10)
            self.assertLess(question.left_operand, 100)


if __name__ == "__main__":
    unittest.main()
