from dataclasses import dataclass
from pathlib import Path
from typing import Any
import tomllib


SUPPORTED_PLUGINS = {"integer_multiplication_distributive"}


@dataclass(frozen=True)
class WorksheetSettings:
    title: str
    locale: str
    student_fields: tuple[str, ...]


@dataclass(frozen=True)
class OutputSettings:
    renderer: str
    theme: str
    options: Any


@dataclass(frozen=True)
class SectionSettings:
    name: str
    plugin: str
    count: int
    columns: int
    format: str
    settings: Any


@dataclass(frozen=True)
class Preset:
    version: int
    worksheet: WorksheetSettings
    output: OutputSettings
    sections: tuple[SectionSettings, ...]


def load_preset(path: str | Path) -> Preset:
    with Path(path).open("rb") as config_file:
        data = tomllib.load(config_file)

    version = int(data.get("version", 1))
    if version != 1:
        raise ValueError(f"Unsupported preset version: {version}")

    worksheet_data = data["worksheet"]
    worksheet = WorksheetSettings(
        title=worksheet_data["title"],
        locale=worksheet_data.get("locale", "en-CA"),
        student_fields=tuple(worksheet_data.get("student_fields", ("name", "date", "time"))),
    )
    output = _load_output(data["output"])
    sections = tuple(_load_section(section) for section in data["sections"])
    if not sections:
        raise ValueError("A preset must contain at least one section")
    return Preset(version=version, worksheet=worksheet, output=output, sections=sections)


def _load_output(data: dict) -> OutputSettings:
    renderer = data["renderer"]
    if renderer != "pdf":
        raise ValueError(f"Unsupported output renderer: {renderer}")
    from kids_exo.renderers.pdf.settings import load_options

    options = load_options(data.get("options", {}))
    return OutputSettings(
        renderer=renderer,
        theme=data.get("theme", "classic_a4"),
        options=options,
    )


def _load_section(data: dict) -> SectionSettings:
    plugin = data["plugin"]
    if plugin not in SUPPORTED_PLUGINS:
        raise ValueError(f"Unsupported question type plugin: {plugin}")
    format_name = data["format"]
    from kids_exo.plugins.integer_multiplication_distributive.settings import (
        load_settings,
        validate_format,
    )

    validate_format(format_name, data["name"])
    count = int(data["count"])
    columns = int(data["columns"])
    if count < 0 or columns < 1:
        raise ValueError(f"Invalid layout values for section {data['name']}")
    return SectionSettings(
        name=data["name"],
        plugin=plugin,
        count=count,
        columns=columns,
        format=format_name,
        settings=load_settings(data.get("settings", {})),
    )
