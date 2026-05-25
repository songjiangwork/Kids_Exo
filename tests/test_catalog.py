import unittest
from pathlib import Path

from kids_exo.catalog import get_preset_entry, list_preset_entries
from kids_exo.config import load_preset


class PresetCatalogTests(unittest.TestCase):
    def test_lists_current_math_mental_multiplication_presets(self) -> None:
        entries = list_preset_entries()

        self.assertGreaterEqual(len(entries), 12)
        self.assertTrue(all(entry.subject == "Math" for entry in entries))
        self.assertTrue(all(entry.category == "Mental Multiplication" for entry in entries))
        self.assertIn(
            "math.mental_multiplication.multiply_by_11.two_digit_beginner",
            {entry.identifier for entry in entries},
        )
        self.assertIn(
            "math.mental_multiplication.mixed_practice",
            {entry.identifier for entry in entries},
        )
        self.assertIn(
            "math.mental_multiplication.mixed_practice_100",
            {entry.identifier for entry in entries},
        )

    def test_entry_resolves_preset_path_and_default_pdf_filename(self) -> None:
        entry = get_preset_entry(
            "math.mental_multiplication.difference_of_squares.beginner"
        )

        self.assertEqual(entry.preset_path, "presets/difference_of_squares_beginner.toml")
        self.assertEqual(entry.default_output_filename, "difference-of-squares.pdf")

    def test_rejects_an_unknown_preset_identifier(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown preset id"):
            get_preset_entry("math.unknown")

    def test_every_catalog_entry_points_to_a_loadable_preset(self) -> None:
        for entry in list_preset_entries():
            with self.subTest(identifier=entry.identifier):
                self.assertTrue(Path(entry.preset_path).exists())
                load_preset(entry.preset_path)


if __name__ == "__main__":
    unittest.main()
