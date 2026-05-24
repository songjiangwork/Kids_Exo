import unittest

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet


DIVISOR_BY_MULTIPLIER = {5: 2, 25: 4, 125: 8}


class MultiplyByFiveFamilyGenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preset = load_preset("presets/multiply_by_5_25_125_beginner.toml")

    def test_preset_uses_the_plugin_and_balances_thirty_practice_questions(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=125)
        practice = worksheet.sections["practice"]

        self.assertEqual(self.preset.sections[0].plugin, "multiply_by_5_25_125")
        self.assertEqual(len(practice), 30)
        self.assertEqual(
            {
                multiplier: sum(question.right_operand == multiplier for question in practice)
                for multiplier in (5, 25, 125)
            },
            {5: 10, 25: 10, 125: 10},
        )

    def test_warmup_explains_divide_then_multiply_shortcuts(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=25)
        warmup = worksheet.sections["warmup"]

        self.assertIn("Divide first", worksheet.section_intros["warmup"][0])
        self.assertIn("x 125", worksheet.section_intros["warmup"][1])
        self.assertEqual({question.right_operand for question in warmup}, {5, 25, 125})
        self.assertTrue(all(" / " in question.display_text for question in warmup))

    def test_beginner_questions_divide_evenly_before_scaling(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=5)
        expressions = [question.expression for question in worksheet.all_questions]

        self.assertEqual(len(expressions), len(set(expressions)))
        for question in worksheet.all_questions:
            divisor = DIVISOR_BY_MULTIPLIER[question.right_operand]
            self.assertEqual(question.left_operand % divisor, 0)
            self.assertGreaterEqual(question.left_operand, 10)
            self.assertLess(question.left_operand, 100)


if __name__ == "__main__":
    unittest.main()
