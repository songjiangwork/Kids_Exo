import unittest

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet
from kids_exo.plugins.same_tens_ones_sum_to_ten.plugin import (
    SameTensOnesSumToTenPlugin,
)
from kids_exo.plugins.square_ending_in_5.plugin import SquareEndingIn5Plugin


class SquareEndingIn5GenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preset = load_preset("presets/square_ending_in_5_beginner.toml")

    def test_plugin_is_a_specialized_same_tens_ones_sum_to_ten_plugin(self) -> None:
        self.assertTrue(issubclass(SquareEndingIn5Plugin, SameTensOnesSumToTenPlugin))

    def test_preset_allows_repetition_for_thirty_two_digit_practice_questions(self) -> None:
        self.assertEqual(self.preset.sections[0].plugin, "square_ending_in_5")
        self.assertEqual(self.preset.sections[1].count, 30)
        self.assertTrue(self.preset.sections[1].settings.allow_duplicates)

    def test_warmup_explains_the_ending_in_5_square_shortcut(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=625)
        introduction = " ".join(worksheet.section_intros["warmup"])

        self.assertIn("Write 25 at the end.", introduction)
        self.assertIn("Example: 35 x 35", introduction)
        self.assertTrue(
            all("write 25" in question.display_text for question in worksheet.sections["warmup"])
        )

    def test_all_questions_are_two_digit_squares_ending_in_five(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=525)

        self.assertEqual(len(worksheet.sections["practice"]), 30)
        for question in worksheet.all_questions:
            self.assertEqual(question.left_operand, question.right_operand)
            self.assertEqual(question.left_operand % 10, 5)
            self.assertGreaterEqual(question.left_operand, 15)
            self.assertLessEqual(question.left_operand, 95)


if __name__ == "__main__":
    unittest.main()
