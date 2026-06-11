import io
import tempfile
import unittest
from pathlib import Path

from kids_exo.persistence.database import build_engine, build_session_factory
from kids_exo.persistence.models import Base
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.cli import main


class CliTests(unittest.TestCase):
    def test_create_parent_command_creates_a_login_account(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "kids-exo.db"
            database_url = f"sqlite+pysqlite:///{database_path}"
            engine = build_engine(database_url)
            Base.metadata.create_all(engine)
            output = io.StringIO()

            exit_code = main(
                [
                    "create-parent",
                    "--email",
                    "Parent@Example.COM",
                    "--display-name",
                    "Parent",
                    "--household-name",
                    "Song Family",
                    "--password",
                    "secret password",
                    "--database-url",
                    database_url,
                ],
                output_stream=output,
            )

            repository = PracticeRepository(build_session_factory(engine))
            account = repository.verify_account_password(
                "parent@example.com",
                "secret password",
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(account.display_name, "Parent")
            self.assertIn("Created parent account: parent@example.com", output.getvalue())

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

    def test_generate_command_supports_the_three_digit_multiply_by_11_preset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "multiply-by-11-three-digit.pdf"

            exit_code = main(
                [
                    "generate",
                    "--preset",
                    "presets/multiply_by_11_three_digit_beginner.toml",
                    "--output",
                    str(output_path),
                    "--seed",
                    "20260524",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_generate_command_supports_the_multiply_by_9_99_999_preset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "multiply-by-nines.pdf"

            exit_code = main(
                [
                    "generate",
                    "--preset",
                    "presets/multiply_by_9_99_999_beginner.toml",
                    "--output",
                    str(output_path),
                    "--seed",
                    "20260524",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_generate_command_supports_the_multiply_by_5_25_125_preset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "multiply-by-five-family.pdf"

            exit_code = main(
                [
                    "generate",
                    "--preset",
                    "presets/multiply_by_5_25_125_beginner.toml",
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

    def test_generate_command_supports_the_tens_sum_to_ten_same_ones_preset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "tens-sum-to-ten-same-ones.pdf"

            exit_code = main(
                [
                    "generate",
                    "--preset",
                    "presets/tens_sum_to_ten_same_ones_beginner.toml",
                    "--output",
                    str(output_path),
                    "--seed",
                    "20260524",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_generate_command_supports_the_near_round_pair_preset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "near-round-pair.pdf"

            exit_code = main(
                [
                    "generate",
                    "--preset",
                    "presets/near_round_pair_multiplication_beginner.toml",
                    "--output",
                    str(output_path),
                    "--seed",
                    "20260524",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_generate_command_supports_the_difference_of_squares_preset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "difference-of-squares.pdf"

            exit_code = main(
                [
                    "generate",
                    "--preset",
                    "presets/difference_of_squares_beginner.toml",
                    "--output",
                    str(output_path),
                    "--seed",
                    "20260524",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_generate_command_supports_the_mixed_practice_preset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "mixed-practice.pdf"

            exit_code = main(
                [
                    "generate",
                    "--preset",
                    "presets/mental_multiplication_mixed_practice.toml",
                    "--output",
                    str(output_path),
                    "--seed",
                    "20260524",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_generate_command_supports_hundred_question_mixed_practice(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)

            exit_code = main(
                [
                    "generate",
                    "--preset-id",
                    "math.mental_multiplication.mixed_practice_100",
                    "--output-dir",
                    str(output_dir),
                    "--seed",
                    "20260524",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(
                (output_dir / "mental-multiplication-mixed-100-seed-20260524.pdf").exists()
            )

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

    def test_generate_command_supports_three_digit_same_prefix_preset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "three-digit-same-prefix.pdf"

            exit_code = main(
                [
                    "generate",
                    "--preset",
                    "presets/three_digit_same_prefix_ones_sum_to_ten_beginner.toml",
                    "--output",
                    str(output_path),
                    "--seed",
                    "20260524",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_list_command_shows_catalog_hierarchy_and_preset_ids(self) -> None:
        output = io.StringIO()

        exit_code = main(["list"], output_stream=output)

        self.assertEqual(exit_code, 0)
        menu = output.getvalue()
        self.assertIn("Math", menu)
        self.assertIn("Mental Multiplication", menu)
        self.assertIn("Multiply by 11 - Two Digits", menu)
        self.assertIn(
            "math.mental_multiplication.multiply_by_11.two_digit_beginner",
            menu,
        )

    def test_generate_command_accepts_preset_id_and_derives_default_output_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)

            exit_code = main(
                [
                    "generate",
                    "--preset-id",
                    "math.mental_multiplication.difference_of_squares.beginner",
                    "--output-dir",
                    str(output_dir),
                    "--seed",
                    "20260524",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(
                (output_dir / "difference-of-squares-seed-20260524.pdf").exists()
            )

    def test_automatic_seed_filename_does_not_overwrite_an_existing_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            arguments = [
                "generate",
                "--preset-id",
                "math.mental_multiplication.difference_of_squares.beginner",
                "--output-dir",
                str(output_dir),
                "--seed",
                "20260524",
            ]

            main(arguments)
            main(arguments)

            self.assertTrue(
                (output_dir / "difference-of-squares-seed-20260524.pdf").exists()
            )
            self.assertTrue(
                (output_dir / "difference-of-squares-seed-20260524-2.pdf").exists()
            )

    def test_interactive_command_generates_selected_preset_with_default_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            user_input = io.StringIO("2\n")
            output = io.StringIO()

            exit_code = main(
                [
                    "interactive",
                    "--output-dir",
                    str(output_dir),
                    "--seed",
                    "20260524",
                ],
                input_stream=user_input,
                output_stream=output,
            )

            self.assertEqual(exit_code, 0)
            self.assertIn("Choose a worksheet", output.getvalue())
            self.assertIn("Generated:", output.getvalue())
            self.assertTrue(
                (output_dir / "multiply-by-11-practice-seed-20260524.pdf").exists()
            )

    def test_interactive_command_without_a_seed_does_not_overwrite_a_previous_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)

            first_exit_code = main(
                ["interactive", "--output-dir", str(output_dir)],
                input_stream=io.StringIO("11\n"),
                output_stream=io.StringIO(),
            )
            second_exit_code = main(
                ["interactive", "--output-dir", str(output_dir)],
                input_stream=io.StringIO("11\n"),
                output_stream=io.StringIO(),
            )

            self.assertEqual(first_exit_code, 0)
            self.assertEqual(second_exit_code, 0)
            self.assertEqual(
                len(list(output_dir.glob("difference-of-squares-*.pdf"))),
                2,
            )

    def test_no_command_defaults_to_interactive_selection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            output = io.StringIO()

            exit_code = main(
                [],
                input_stream=io.StringIO("11\n"),
                output_stream=output,
                default_output_dir=output_dir,
            )

            self.assertEqual(exit_code, 0)
            self.assertIn("Choose a worksheet", output.getvalue())
            self.assertEqual(len(list(output_dir.glob("difference-of-squares-*.pdf"))), 1)

    def test_interactive_command_rejects_zero_instead_of_selecting_the_last_entry(self) -> None:
        with self.assertRaisesRegex(ValueError, "Invalid worksheet selection"):
            main(
                ["interactive"],
                input_stream=io.StringIO("0\n"),
                output_stream=io.StringIO(),
            )


if __name__ == "__main__":
    unittest.main()
