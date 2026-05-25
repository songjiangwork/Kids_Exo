from dataclasses import dataclass
from pathlib import Path
from typing import Any
import tomllib

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
    combine_into: str | None = None
    heading: str | None = None
    instructions: tuple[str, ...] | None = None
    shuffle: bool = False

    @property
    def display_name(self) -> str:
        return self.combine_into or self.name


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
    _validate_sections(sections)
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
    from kids_exo.plugins.registry import get_plugin_definition

    definition = get_plugin_definition(plugin)
    format_name = data["format"]
    definition.validate_format(format_name, data["name"])
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
        settings=definition.load_settings(data.get("settings", {})),
        combine_into=data.get("combine_into"),
        heading=data.get("heading"),
        instructions=(
            tuple(data["instructions"]) if "instructions" in data else None
        ),
        shuffle=bool(data.get("shuffle", False)),
    )


def _validate_sections(sections: tuple[SectionSettings, ...]) -> None:
    names = [section.name for section in sections]
    if len(names) != len(set(names)):
        raise ValueError("Section source names must be unique")

    display_layouts: dict[str, tuple[int, str | None, tuple[str, ...] | None, bool]] = {}
    for section in sections:
        if (section.heading is None) != (section.instructions is None):
            raise ValueError("A custom section heading and instructions must be configured together")
        layout = (section.columns, section.heading, section.instructions, section.shuffle)
        existing = display_layouts.setdefault(section.display_name, layout)
        if existing != layout:
            raise ValueError("Combined sections must use the same presentation settings")
        if section.combine_into and section.heading is None:
            raise ValueError("Combined sections must provide a shared heading and instructions")
