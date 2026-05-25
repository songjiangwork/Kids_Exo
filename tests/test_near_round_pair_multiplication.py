import unittest

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet


class NearRoundPairMultiplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preset = load_preset("presets/near_round_pair_multiplication_beginner.toml")

    def test_preset_uses_the_plugin_and_balances_thirty_practice_questions(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=5047)
        practice = worksheet.sections["practice"]

        self.assertEqual(self.preset.sections[0].plugin, "near_round_pair_multiplication")
        self.assertEqual(len(practice), 30)
        self.assertEqual(
            {
                strategy: sum(question.strategy == strategy for question in practice)
                for strategy in ("both_below_round", "both_above_round")
            },
            {"both_below_round": 15, "both_above_round": 15},
        )

    def test_warmup_explains_the_same_side_round_number_shortcut(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=4852)
        introduction = " ".join(worksheet.section_intros["warmup"])

        self.assertIn("close to the same round number", introduction)
        self.assertIn("Example: 48 x 47", introduction)
        self.assertTrue(
            all("base" in question.display_text for question in worksheet.sections["warmup"])
        )

    def test_questions_have_two_distinct_offsets_on_the_same_side_of_a_round_number(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=5053)
        settings = self.preset.sections[0].settings
        expressions = [question.expression for question in worksheet.all_questions]

        self.assertEqual(len(expressions), len(set(expressions)))
        for question in worksheet.all_questions:
            matches = []
            for base in settings.round_numbers:
                offsets = (
                    question.left_operand - base,
                    question.right_operand - base,
                )
                if all(abs(offset) in settings.near_round_distances for offset in offsets):
                    matches.append(offsets)
            self.assertTrue(matches)
            offsets = matches[0]
            self.assertNotEqual(offsets[0], offsets[1])
            if question.strategy == "both_below_round":
                self.assertTrue(all(offset < 0 for offset in offsets))
            else:
                self.assertTrue(all(offset > 0 for offset in offsets))


if __name__ == "__main__":
    unittest.main()
