import unittest

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet


class MultiplyBy11GenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preset = load_preset("presets/multiply_by_11_beginner.toml")

    def test_preset_uses_the_plugin_and_thirty_practice_questions(self) -> None:
        self.assertEqual(self.preset.sections[0].plugin, "multiply_by_11")
        self.assertEqual(self.preset.sections[1].count, 30)

    def test_warmup_has_an_english_rule_example_and_both_strategies(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=115)
        warmup = worksheet.sections["warmup"]

        self.assertIn("Add the two digits.", worksheet.section_intros["warmup"][0])
        self.assertIn("Example: 68 x 11", worksheet.section_intros["warmup"][1])
        self.assertEqual(
            {
                strategy: sum(question.strategy == strategy for question in warmup)
                for strategy in ("no_carrying", "with_carrying")
            },
            {"no_carrying": 2, "with_carrying": 2},
        )
        self.assertTrue(all("so" in question.display_text for question in warmup))

    def test_practice_has_equal_carrying_and_non_carrying_questions(self) -> None:
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

    def test_each_strategy_generates_the_expected_digit_sum_case(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=19)
        expressions = [question.expression for question in worksheet.all_questions]

        self.assertEqual(len(expressions), len(set(expressions)))

        for question in worksheet.all_questions:
            tens, ones = divmod(question.left_operand, 10)
            if question.strategy == "no_carrying":
                self.assertLess(tens + ones, 10)
            else:
                self.assertGreaterEqual(tens + ones, 10)
            self.assertEqual(question.right_operand, 11)


if __name__ == "__main__":
    unittest.main()
