import tempfile
import unittest
from pathlib import Path

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet
from kids_exo.renderers.pdf import write_pdf


class PdfRendererTests(unittest.TestCase):
    def test_keeps_current_beginner_worksheets_on_one_page(self) -> None:
        preset_paths = (
            "presets/distributive_property_beginner.toml",
            "presets/multiply_by_11_beginner.toml",
            "presets/multiply_by_11_three_digit_beginner.toml",
            "presets/multiply_by_9_99_999_beginner.toml",
            "presets/multiply_by_5_25_125_beginner.toml",
            "presets/same_tens_ones_sum_to_ten_beginner.toml",
            "presets/square_ending_in_5_beginner.toml",
            "presets/three_digit_same_prefix_ones_sum_to_ten_beginner.toml",
            "presets/tens_sum_to_ten_same_ones_beginner.toml",
            "presets/near_round_pair_multiplication_beginner.toml",
            "presets/difference_of_squares_beginner.toml",
        )

        for preset_path in preset_paths:
            with self.subTest(preset_path=preset_path):
                preset = load_preset(preset_path)
                worksheet = generate_worksheet(preset, seed=42)
                with tempfile.TemporaryDirectory() as directory:
                    output_path = Path(directory) / "worksheet.pdf"
                    write_pdf(worksheet, preset.output.options, output_path)
                    data = output_path.read_bytes()

                self.assertIn(b"/Count 1", data)

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

    def test_renders_the_three_digit_multiply_by_11_rule_and_example(self) -> None:
        preset = load_preset("presets/multiply_by_11_three_digit_beginner.toml")
        worksheet = generate_worksheet(preset, seed=42)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "multiply-by-11-three-digit.pdf"
            write_pdf(worksheet, preset.output.options, output_path)
            data = output_path.read_bytes()

        self.assertIn(b"Three-Digit Multiplying by 11 Practice", data)
        self.assertIn(b"Add each pair of neighbouring digits.", data)
        self.assertIn(b"Example: 386 x 11", data)

    def test_renders_the_multiply_by_9_99_999_rule(self) -> None:
        preset = load_preset("presets/multiply_by_9_99_999_beginner.toml")
        worksheet = generate_worksheet(preset, seed=42)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "multiply-by-nines.pdf"
            write_pdf(worksheet, preset.output.options, output_path)
            data = output_path.read_bytes()

        self.assertIn(b"Multiplying by 9, 99, and 999 Practice", data)
        self.assertIn(b"one less than 10, 100, or 1000", data)

    def test_renders_the_multiply_by_5_25_125_rule(self) -> None:
        preset = load_preset("presets/multiply_by_5_25_125_beginner.toml")
        worksheet = generate_worksheet(preset, seed=42)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "multiply-by-five-family.pdf"
            write_pdf(worksheet, preset.output.options, output_path)
            data = output_path.read_bytes()

        self.assertIn(b"Multiplying by 5, 25, and 125 Practice", data)
        self.assertIn(b"Divide first", data)

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
        self.assertIn(b"/Count 1", data)
        self.assertNotIn(b"Page 2 of", data)

    def test_renders_the_tens_sum_to_ten_same_ones_rule_and_example(self) -> None:
        preset = load_preset("presets/tens_sum_to_ten_same_ones_beginner.toml")
        worksheet = generate_worksheet(preset, seed=42)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "tens-sum-to-ten-same-ones.pdf"
            write_pdf(worksheet, preset.output.options, output_path)
            data = output_path.read_bytes()

        self.assertIn(b"Tens Sum to 10, Same Ones Practice", data)
        self.assertIn(b"Add the shared ones digit.", data)
        self.assertIn(b"Example: 43 x 63", data)

    def test_renders_the_near_round_pair_rule_and_example(self) -> None:
        preset = load_preset("presets/near_round_pair_multiplication_beginner.toml")
        worksheet = generate_worksheet(preset, seed=42)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "near-round-pair.pdf"
            write_pdf(worksheet, preset.output.options, output_path)
            data = output_path.read_bytes()

        self.assertIn(b"Near Round-Number Pair Multiplication Practice", data)
        self.assertIn(b"close to the same round number", data)
        self.assertIn(b"Example: 48 x 47", data)

    def test_renders_the_difference_of_squares_rule_and_example(self) -> None:
        preset = load_preset("presets/difference_of_squares_beginner.toml")
        worksheet = generate_worksheet(preset, seed=42)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "difference-of-squares.pdf"
            write_pdf(worksheet, preset.output.options, output_path)
            data = output_path.read_bytes()

        self.assertIn(b"Difference of Squares Multiplication Practice", data)
        self.assertIn(b"same distance below and above", data)
        self.assertIn(b"Example: 47 x 53", data)

    def test_renders_mixed_practice_without_a_warmup_section(self) -> None:
        preset = load_preset("presets/mental_multiplication_mixed_practice.toml")
        worksheet = generate_worksheet(preset, seed=42)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "mixed-practice.pdf"
            write_pdf(worksheet, preset.output.options, output_path)
            data = output_path.read_bytes()

        self.assertIn(b"Mental Multiplication Mixed Practice", data)
        self.assertIn(b"A. Mixed Practice", data)
        self.assertNotIn(b"Warm-up", data)

    def test_paginates_a_hundred_question_mixed_practice_pdf(self) -> None:
        preset = load_preset("presets/mental_multiplication_mixed_100.toml")
        worksheet = generate_worksheet(preset, seed=42)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "mixed-practice-100.pdf"
            write_pdf(worksheet, preset.output.options, output_path)
            data = output_path.read_bytes()

        self.assertIn(b"/Count 3", data)
        self.assertIn(b"Page 1 of 3", data)
        self.assertIn(b"Page 3 of 3", data)
        self.assertIn(b"A. Mixed Practice \\(continued\\)", data)
        self.assertIn(b"100.", data)

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
