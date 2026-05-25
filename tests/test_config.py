import tempfile
import unittest
from pathlib import Path

from kids_exo.config import load_preset


CONFIG_TEXT = """
version = 1

[worksheet]
title = "Distributive Property Multiplication Practice"
locale = "en-CA"
student_fields = ["name", "date", "time"]

[output]
renderer = "pdf"
theme = "classic_a4"

[output.options]
paper_size = "A4"
orientation = "portrait"

[[sections]]
name = "warmup"
plugin = "integer_multiplication_distributive"
count = 4
columns = 1
format = "guided_full_expansion"

[sections.settings]
left_operand_digits = [2]
right_operand_digits = [1]
decomposable_operand = "left"
strategies = ["place_value_addition", "near_round_number_subtraction"]
allow_duplicates = false
near_round_distances = [1, 2, 3]

[sections.settings.strategy_weights]
place_value_addition = 0.5
near_round_number_subtraction = 0.5

[[sections]]
name = "practice"
plugin = "integer_multiplication_distributive"
count = 20
columns = 2
format = "expression_with_answer_blank"

[sections.settings]
left_operand_digits = [2]
right_operand_digits = [1]
decomposable_operand = "left"
strategies = ["place_value_addition", "near_round_number_subtraction"]
allow_duplicates = false
near_round_distances = [1, 2, 3]

[sections.settings.strategy_weights]
place_value_addition = 0.6
near_round_number_subtraction = 0.4
"""


class LoadConfigTests(unittest.TestCase):
    def test_loads_output_settings_and_section_owned_plugin_settings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "worksheet.toml"
            path.write_text(CONFIG_TEXT, encoding="utf-8")

            preset = load_preset(path)

        self.assertEqual(preset.version, 1)
        self.assertEqual(preset.worksheet.locale, "en-CA")
        self.assertEqual(preset.output.renderer, "pdf")
        self.assertEqual(preset.output.options.paper_size, "A4")
        self.assertEqual(preset.sections[0].name, "warmup")
        self.assertEqual(preset.sections[0].format, "guided_full_expansion")
        self.assertEqual(preset.sections[0].plugin, "integer_multiplication_distributive")
        self.assertTrue(preset.sections[0].settings.allow_subtraction)
        self.assertEqual(preset.sections[0].settings.near_round_distances, (1, 2, 3))
        self.assertEqual(
            preset.sections[1].settings.strategy_weights,
            {
                "place_value_addition": 0.6,
                "near_round_number_subtraction": 0.4,
            },
        )

    def test_rejects_an_unknown_presentation_format(self) -> None:
        invalid_text = CONFIG_TEXT.replace("guided_full_expansion", "unknown_format")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "worksheet.toml"
            path.write_text(invalid_text, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "format"):
                load_preset(path)

    def test_rejects_strategy_weights_for_a_strategy_not_enabled_in_the_section(self) -> None:
        invalid_text = CONFIG_TEXT.replace(
            'strategies = ["place_value_addition", "near_round_number_subtraction"]',
            'strategies = ["place_value_addition"]',
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "worksheet.toml"
            path.write_text(invalid_text, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "strategy_weights"):
                load_preset(path)

    def test_rejects_duplicate_source_section_names(self) -> None:
        invalid_text = CONFIG_TEXT.replace('name = "practice"', 'name = "warmup"')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate-sections.toml"
            path.write_text(invalid_text, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "unique"):
                load_preset(path)


if __name__ == "__main__":
    unittest.main()
