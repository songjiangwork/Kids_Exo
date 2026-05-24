import random

from kids_exo.config import Preset, SectionSettings
from kids_exo.models import Worksheet
from kids_exo.plugins.registry import get_plugin_definition


def generate_worksheet(preset: Preset, seed: int | None = None) -> Worksheet:
    """Generate worksheet content without coupling it to an output renderer."""

    rng = random.Random(seed)
    used_expressions: set[str] = set()
    plugins = {section.name: _create_plugin(section) for section in preset.sections}
    sections = {
        section.name: plugins[section.name].generate(
            section.name,
            section,
            rng,
            used_expressions,
        )
        for section in preset.sections
    }
    worksheet = preset.worksheet
    return Worksheet(
        title=worksheet.title,
        locale=worksheet.locale,
        student_fields=worksheet.student_fields,
        sections=sections,
        section_columns={section.name: section.columns for section in preset.sections},
        section_order=tuple(section.name for section in preset.sections),
        section_headings={
            section.name: plugins[section.name].presentation(section.name, worksheet.locale)[0]
            for section in preset.sections
        },
        section_intros={
            section.name: plugins[section.name].presentation(section.name, worksheet.locale)[1]
            for section in preset.sections
        },
    )


def _create_plugin(section: SectionSettings):
    return get_plugin_definition(section.plugin).create(section.settings)
