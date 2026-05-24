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


if __name__ == "__main__":
    unittest.main()
