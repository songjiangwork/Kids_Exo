import unittest

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet


class DifferenceOfSquaresGenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preset = load_preset("presets/difference_of_squares_beginner.toml")

    def test_preset_uses_the_plugin_and_thirty_practice_questions(self) -> None:
        self.assertEqual(self.preset.sections[0].plugin, "difference_of_squares")
        self.assertEqual(self.preset.sections[1].count, 30)

    def test_warmup_explains_symmetric_factors_in_english(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=4753)
        introduction = " ".join(worksheet.section_intros["warmup"])

        self.assertIn("same distance below and above", introduction)
        self.assertIn("Example: 47 x 53", introduction)
        self.assertTrue(
            all(" - ___ x ___" in question.display_text for question in worksheet.sections["warmup"])
        )

    def test_questions_are_symmetric_around_a_configured_round_number(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=501)
        settings = self.preset.sections[0].settings
        expressions = [question.expression for question in worksheet.all_questions]

        self.assertEqual(len(expressions), len(set(expressions)))
        for question in worksheet.all_questions:
            midpoint = (question.left_operand + question.right_operand) // 2
            distance = midpoint - question.left_operand
            self.assertEqual(question.left_operand + question.right_operand, midpoint * 2)
            self.assertIn(midpoint, settings.round_numbers)
            self.assertIn(distance, settings.near_round_distances)
            self.assertEqual(question.strategy, "symmetric_around_round")


if __name__ == "__main__":
    unittest.main()
