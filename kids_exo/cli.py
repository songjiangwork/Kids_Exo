import argparse
from collections.abc import Sequence

from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet
from kids_exo.renderers.pdf import write_pdf


def main(arguments: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate printable children's exercise worksheets.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate_parser = subparsers.add_parser("generate", help="Generate a PDF worksheet.")
    generate_parser.add_argument(
        "--preset",
        default="presets/distributive_property_beginner.toml",
    )
    generate_parser.add_argument("--output", default="output/distributive-practice.pdf")
    generate_parser.add_argument("--seed", type=int)
    options = parser.parse_args(arguments)

    if options.command == "generate":
        preset = load_preset(options.preset)
        worksheet = generate_worksheet(preset, seed=options.seed)
        if preset.output.renderer == "pdf":
            write_pdf(worksheet, preset.output.options, options.output)
        else:
            raise ValueError(f"Unsupported output renderer: {preset.output.renderer}")
        return 0
    return 1
