import argparse
from collections.abc import Sequence
from datetime import datetime
import getpass
import os
from pathlib import Path
import sys
from typing import TextIO

from kids_exo.catalog import get_preset_entry, list_preset_entries
from kids_exo.config import load_preset
from kids_exo.generator import generate_worksheet
from kids_exo.persistence.database import build_engine, build_session_factory
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.renderers.pdf import write_pdf


DEFAULT_PRESET_PATH = "presets/distributive_property_beginner.toml"
DEFAULT_OUTPUT_PATH = "output/distributive-practice.pdf"


def main(
    arguments: Sequence[str] | None = None,
    *,
    input_stream: TextIO | None = None,
    output_stream: TextIO | None = None,
    default_output_dir: str | Path = "output",
) -> int:
    input_stream = input_stream or sys.stdin
    output_stream = output_stream or sys.stdout
    parsed_arguments = list(arguments) if arguments is not None else sys.argv[1:]
    if not parsed_arguments:
        parsed_arguments = ["interactive", "--output-dir", str(default_output_dir)]
    parser = argparse.ArgumentParser(description="Generate printable children's exercise worksheets.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate_parser = subparsers.add_parser("generate", help="Generate a PDF worksheet.")
    preset_group = generate_parser.add_mutually_exclusive_group()
    preset_group.add_argument("--preset")
    preset_group.add_argument("--preset-id")
    generate_parser.add_argument("--output")
    generate_parser.add_argument("--output-dir", default="output")
    generate_parser.add_argument("--seed", type=int)
    subparsers.add_parser("list", help="List available worksheet presets.")
    interactive_parser = subparsers.add_parser(
        "interactive",
        help="Choose a worksheet preset interactively and generate its PDF.",
    )
    interactive_parser.add_argument("--output-dir", default="output")
    interactive_parser.add_argument("--seed", type=int)
    parent_parser = subparsers.add_parser(
        "create-parent",
        help="Create a local parent login account.",
    )
    parent_parser.add_argument("--email", required=True)
    parent_parser.add_argument("--display-name", required=True)
    parent_parser.add_argument("--household-name", required=True)
    parent_parser.add_argument("--password")
    parent_parser.add_argument(
        "--database-url",
        default=os.environ.get("KIDS_EXO_DATABASE_URL", "sqlite+pysqlite:///kids-exo.db"),
    )
    options = parser.parse_args(parsed_arguments)

    if options.command == "generate":
        preset_path, output_path = _resolve_generate_paths(options)
        _generate_pdf(preset_path, output_path, options.seed)
        return 0
    if options.command == "list":
        _write_catalog(output_stream, numbered=False)
        return 0
    if options.command == "interactive":
        entries = list_preset_entries()
        output_stream.write("Choose a worksheet to generate:\n")
        _write_catalog(output_stream, numbered=True)
        output_stream.write("Enter a number: ")
        output_stream.flush()
        selection = input_stream.readline().strip()
        try:
            selection_number = int(selection)
            if selection_number < 1 or selection_number > len(entries):
                raise ValueError
            entry = entries[selection_number - 1]
        except ValueError as exc:
            raise ValueError(f"Invalid worksheet selection: {selection}") from exc
        output_path = _automatic_output_path(
            Path(options.output_dir) / entry.default_output_filename,
            options.seed,
        )
        _generate_pdf(entry.preset_path, output_path, options.seed)
        output_stream.write(f"Generated: {output_path}\n")
        return 0
    if options.command == "create-parent":
        password = options.password or getpass.getpass("Password: ")
        repository = PracticeRepository(
            build_session_factory(build_engine(options.database_url))
        )
        try:
            account = repository.create_parent_account(
                email=options.email,
                display_name=options.display_name,
                password=password,
                household_name=options.household_name,
            )
        except ValueError as exc:
            raise ValueError(str(exc)) from exc
        output_stream.write(f"Created parent account: {account.email}\n")
        return 0
    return 1


def _resolve_generate_paths(options: argparse.Namespace) -> tuple[str, Path]:
    if options.preset_id:
        entry = get_preset_entry(options.preset_id)
        output_path = (
            Path(options.output)
            if options.output
            else _automatic_output_path(
                Path(options.output_dir) / entry.default_output_filename,
                options.seed,
            )
        )
        return entry.preset_path, output_path
    if options.output:
        return options.preset or DEFAULT_PRESET_PATH, Path(options.output)
    return (
        options.preset or DEFAULT_PRESET_PATH,
        _automatic_output_path(Path(DEFAULT_OUTPUT_PATH), options.seed),
    )


def _automatic_output_path(base_path: Path, seed: int | None) -> Path:
    marker = f"seed-{seed}" if seed is not None else datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = base_path.with_name(f"{base_path.stem}-{marker}{base_path.suffix}")
    if not candidate.exists():
        return candidate
    counter = 2
    while True:
        numbered_candidate = candidate.with_name(
            f"{candidate.stem}-{counter}{candidate.suffix}"
        )
        if not numbered_candidate.exists():
            return numbered_candidate
        counter += 1


def _generate_pdf(preset_path: str, output_path: str | Path, seed: int | None) -> None:
    preset = load_preset(preset_path)
    worksheet = generate_worksheet(preset, seed=seed)
    if preset.output.renderer != "pdf":
        raise ValueError(f"Unsupported output renderer: {preset.output.renderer}")
    write_pdf(worksheet, preset.output.options, output_path)


def _write_catalog(output_stream: TextIO, numbered: bool) -> None:
    entries = list_preset_entries()
    current_group: tuple[str, str] | None = None
    for index, entry in enumerate(entries, start=1):
        group = (entry.subject, entry.category)
        if group != current_group:
            output_stream.write(f"{entry.subject}\n  {entry.category}\n")
            current_group = group
        prefix = f"{index}. " if numbered else "- "
        output_stream.write(f"    {prefix}{entry.title} [{entry.identifier}]\n")
