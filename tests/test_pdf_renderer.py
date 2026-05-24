import tempfile
import unittest
from pathlib import Path

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet
from kids_exo.renderers.pdf import write_pdf


class PdfRendererTests(unittest.TestCase):
    def test_writes_an_a4_english_pdf_with_both_section_headings(self) -> None:
        preset = load_preset("presets/distributive_property_beginner.toml")
        worksheet = generate_worksheet(preset, seed=42)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "worksheet.pdf"
            write_pdf(worksheet, preset.output.options, output_path)
            data = output_path.read_bytes()

        self.assertTrue(data.startswith(b"%PDF-1.4"))
        self.assertIn(b"/MediaBox [0 0 595.28 841.89]", data)
        self.assertIn(b"Distributive Property Multiplication Practice", data)
        self.assertIn(b"Warm-up", data)
        self.assertIn(b"Practice", data)

    def test_renders_the_multiply_by_11_english_rule_and_example(self) -> None:
        preset = load_preset("presets/multiply_by_11_beginner.toml")
        worksheet = generate_worksheet(preset, seed=42)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "multiply-by-11.pdf"
            write_pdf(worksheet, preset.output.options, output_path)
            data = output_path.read_bytes()

        self.assertIn(b"Multiplying by 11 Practice", data)
        self.assertIn(b"Add the two digits.", data)
        self.assertIn(b"Example: 68 x 11", data)

    def test_renders_the_same_tens_ones_sum_to_ten_rule_and_example(self) -> None:
        preset = load_preset("presets/same_tens_ones_sum_to_ten_beginner.toml")
        worksheet = generate_worksheet(preset, seed=42)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "same-tens.pdf"
            write_pdf(worksheet, preset.output.options, output_path)
            data = output_path.read_bytes()

        self.assertIn(b"Same Tens, Ones Sum to 10 Practice", data)
        self.assertIn(b"Multiply the tens digit by the next number.", data)
        self.assertIn(b"Example: 43 x 47", data)

    def test_renders_the_square_ending_in_5_rule_and_example(self) -> None:
        preset = load_preset("presets/square_ending_in_5_beginner.toml")
        worksheet = generate_worksheet(preset, seed=42)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "squares-ending-in-5.pdf"
            write_pdf(worksheet, preset.output.options, output_path)
            data = output_path.read_bytes()

        self.assertIn(b"Squares Ending in 5 Practice", data)
        self.assertIn(b"Write 25 at the end.", data)
        self.assertIn(b"Example: 35 x 35", data)

    def test_renders_the_three_digit_same_prefix_rule_and_example(self) -> None:
        preset = load_preset("presets/three_digit_same_prefix_ones_sum_to_ten_beginner.toml")
        worksheet = generate_worksheet(preset, seed=42)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "three-digit-same-prefix.pdf"
            write_pdf(worksheet, preset.output.options, output_path)
            data = output_path.read_bytes()

        self.assertIn(b"Three-Digit Same Prefix, Ones Sum to 10 Practice", data)
        self.assertIn(b"Use the matching first two digits.", data)
        self.assertIn(b"Example: 123 x 127", data)


if __name__ == "__main__":
    unittest.main()
