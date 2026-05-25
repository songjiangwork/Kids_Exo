import unittest

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet


class MixedPracticeWorksheetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preset = load_preset("presets/mental_multiplication_mixed_practice.toml")

    def test_preset_contains_sources_without_a_warmup_section(self) -> None:
        self.assertNotIn("warmup", {section.name for section in self.preset.sections})
        self.assertEqual(
            {section.combine_into for section in self.preset.sections},
            {"mixed_practice"},
        )
        self.assertEqual(sum(section.count for section in self.preset.sections), 30)

    def test_generated_questions_are_combined_and_shuffled_into_one_practice_area(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=20260524)
        questions = worksheet.sections["mixed_practice"]

        self.assertEqual(worksheet.section_order, ("mixed_practice",))
        self.assertNotIn("warmup", worksheet.sections)
        self.assertEqual(len(questions), 30)
        self.assertEqual(
            {
                section.name: sum(question.section == section.name for question in questions)
                for section in self.preset.sections
            },
            {section.name: 5 for section in self.preset.sections},
        )
        unshuffled_sources = [
            section.name
            for section in self.preset.sections
            for _ in range(section.count)
        ]
        self.assertNotEqual([question.section for question in questions], unshuffled_sources)

    def test_mixed_practice_uses_preset_owned_heading_and_instruction(self) -> None:
        worksheet = generate_worksheet(self.preset, seed=13)

        self.assertEqual(worksheet.section_headings["mixed_practice"], "A. Mixed Practice")
        self.assertEqual(
            worksheet.section_intros["mixed_practice"],
            ("Choose a helpful shortcut for each problem.",),
        )

    def test_hundred_question_preset_is_mixed_and_has_no_warmup(self) -> None:
        preset = load_preset("presets/mental_multiplication_mixed_100.toml")
        worksheet = generate_worksheet(preset, seed=100)
        questions = worksheet.sections["mixed_practice"]

        self.assertNotIn("warmup", worksheet.sections)
        self.assertEqual(len(questions), 100)
        self.assertEqual(sum(section.count for section in preset.sections), 100)
        self.assertGreaterEqual(len({question.section for question in questions}), 6)


if __name__ == "__main__":
    unittest.main()
