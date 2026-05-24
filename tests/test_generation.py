import unittest

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet


class WorksheetGenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preset = load_preset("presets/distributive_property_beginner.toml")

    def test_generates_the_configured_sections_without_duplicate_expressions(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=20260523)

        expected_counts = {section.name: section.count for section in self.preset.sections}
        self.assertEqual(len(worksheet.sections["warmup"]), expected_counts["warmup"])
        self.assertEqual(len(worksheet.sections["practice"]), expected_counts["practice"])
        expressions = [q.expression for q in worksheet.all_questions]
        self.assertEqual(len(expressions), len(set(expressions)))

    def test_same_seed_reproduces_the_same_printed_questions(self) -> None:
        first = generate_worksheet(self.preset, seed=1122)
        second = generate_worksheet(self.preset, seed=1122)

        self.assertEqual(
            [question.display_text for question in first.all_questions],
            [question.display_text for question in second.all_questions],
        )

    def test_warmup_includes_both_supported_strategies_and_guided_steps(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=8)
        warmup = worksheet.sections["warmup"]

        self.assertEqual(
            {question.strategy for question in warmup},
            {"place_value_addition", "near_round_number_subtraction"},
        )
        self.assertTrue(all("___" in question.display_text for question in warmup))
        self.assertTrue(any(" - " in question.display_text for question in warmup))
        self.assertTrue(any(" + " in question.display_text for question in warmup))

    def test_subtraction_strategy_uses_a_near_round_number_decomposition(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=19)
        allowed_distances = self.preset.sections[1].settings.near_round_distances
        subtraction_questions = [
            question
            for question in worksheet.all_questions
            if question.strategy == "near_round_number_subtraction"
        ]

        self.assertTrue(subtraction_questions)
        for question in subtraction_questions:
            self.assertIn(question.decomposition.difference, allowed_distances)
            self.assertEqual(
                question.left_operand,
                question.decomposition.round_number - question.decomposition.difference,
            )

    def test_addition_strategy_does_not_use_numbers_reserved_for_subtraction_shortcuts(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=27)
        reserved_distances = self.preset.sections[1].settings.near_round_distances
        addition_questions = [
            question
            for question in worksheet.all_questions
            if question.strategy == "place_value_addition"
        ]

        for question in addition_questions:
            distance_to_next_ten = 10 - (question.left_operand % 10)
            self.assertNotIn(distance_to_next_ten, reserved_distances)

    def test_practice_questions_follow_configured_strategy_weights(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=33)
        practice = worksheet.sections["practice"]
        strategy_counts = {
            strategy: sum(question.strategy == strategy for question in practice)
            for strategy in self.preset.sections[1].settings.strategy_weights
        }

        self.assertEqual(
            strategy_counts,
            {
                "place_value_addition": 18,
                "near_round_number_subtraction": 12,
            },
        )


if __name__ == "__main__":
    unittest.main()
