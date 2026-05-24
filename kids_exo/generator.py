import random

from kids_exo.config import Preset, SectionSettings
from kids_exo.models import Worksheet
from kids_exo.plugins.integer_multiplication_distributive.plugin import (
    IntegerMultiplicationDistributivePlugin,
)


def generate_worksheet(preset: Preset, seed: int | None = None) -> Worksheet:
    """Generate worksheet content without coupling it to an output renderer."""

    rng = random.Random(seed)
    used_expressions: set[str] = set()
    sections = {
        section.name: _create_plugin(section).generate(
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
    )


def _create_plugin(section: SectionSettings) -> IntegerMultiplicationDistributivePlugin:
    if section.plugin == "integer_multiplication_distributive":
        return IntegerMultiplicationDistributivePlugin(section.settings)
    raise ValueError(f"Unsupported question type plugin: {section.plugin}")
