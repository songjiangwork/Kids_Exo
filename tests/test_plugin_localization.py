import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from kids_exo.localization import resolve_presentation
from kids_exo.plugins.multiply_by_11.plugin import MultiplyBy11Plugin
from kids_exo.plugins.multiply_by_11.settings import load_settings


class MultiplyBy11LocalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plugin = MultiplyBy11Plugin(
            load_settings(
                {
                    "multiplicand_digits": [2],
                    "strategies": ["no_carrying", "with_carrying"],
                    "allow_duplicates": False,
                }
            )
        )

    def test_default_presentation_comes_from_english_plugin_resources(self) -> None:
        presentation = self.plugin.localized_presentation("warmup", "en-CA")

        self.assertEqual(presentation.heading.text, "A. Warm-up")
        self.assertEqual(presentation.heading.locale, "en-CA")
        self.assertFalse(presentation.heading.used_fallback)
        self.assertIn("Example: 68 x 11", presentation.instructions[1].text)

    def test_missing_chinese_example_falls_back_to_english_per_key(self) -> None:
        presentation = self.plugin.localized_presentation("warmup", "zh-CN")

        self.assertEqual(presentation.heading.text, "A. 热身")
        self.assertEqual(presentation.heading.locale, "zh-CN")
        self.assertEqual(presentation.instructions[0].locale, "zh-CN")
        self.assertEqual(presentation.instructions[1].locale, "en-CA")
        self.assertTrue(presentation.instructions[1].used_fallback)
        self.assertIn("Example: 68 x 11", presentation.instructions[1].text)
        self.assertEqual(presentation.fallback_keys, ("instruction_2",))

    def test_default_resource_must_contain_required_teaching_text(self) -> None:
        with TemporaryDirectory() as directory:
            Path(directory, "en-CA.toml").write_text(
                '[warmup]\nheading = "Warm-up only"\n',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "incomplete"):
                resolve_presentation(directory, "warmup", "en-CA")


if __name__ == "__main__":
    unittest.main()
