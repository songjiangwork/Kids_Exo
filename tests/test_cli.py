import tempfile
import unittest
from pathlib import Path

from kids_exo.cli import main


class CliTests(unittest.TestCase):
    def test_generate_command_writes_a_pdf_from_a_preset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "printable-worksheet.pdf"

            exit_code = main(
                [
                    "generate",
                    "--preset",
                    "presets/distributive_property_beginner.toml",
                    "--output",
                    str(output_path),
                    "--seed",
                    "20260523",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            self.assertGreater(output_path.stat().st_size, 1000)

    def test_generate_command_supports_the_multiply_by_11_preset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "multiply-by-11.pdf"

            exit_code = main(
                [
                    "generate",
                    "--preset",
                    "presets/multiply_by_11_beginner.toml",
                    "--output",
                    str(output_path),
                    "--seed",
                    "20260524",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_generate_command_supports_the_same_tens_ones_sum_to_ten_preset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "same-tens.pdf"

            exit_code = main(
                [
                    "generate",
                    "--preset",
                    "presets/same_tens_ones_sum_to_ten_beginner.toml",
                    "--output",
                    str(output_path),
                    "--seed",
                    "20260524",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_generate_command_supports_the_square_ending_in_5_preset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "squares-ending-in-5.pdf"

            exit_code = main(
                [
                    "generate",
                    "--preset",
                    "presets/square_ending_in_5_beginner.toml",
                    "--output",
                    str(output_path),
                    "--seed",
                    "20260524",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
