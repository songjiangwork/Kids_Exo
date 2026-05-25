import random

from kids_exo.config import Preset, SectionSettings
from kids_exo.models import Worksheet
from kids_exo.plugins.registry import get_plugin_definition


def generate_worksheet(preset: Preset, seed: int | None = None) -> Worksheet:
    """Generate worksheet content without coupling it to an output renderer."""

    rng = random.Random(seed)
    used_expressions: set[str] = set()
    plugin_sources = [(section, _create_plugin(section)) for section in preset.sections]
    grouped_questions: dict[str, list] = {}
    first_sources: dict[str, tuple[SectionSettings, object]] = {}
    for section, plugin in plugin_sources:
        questions = plugin.generate(
            section.name,
            section,
            rng,
            used_expressions,
        )
        grouped_questions.setdefault(section.display_name, []).extend(questions)
        first_sources.setdefault(section.display_name, (section, plugin))
    for display_name, (section, _) in first_sources.items():
        if section.shuffle:
            rng.shuffle(grouped_questions[display_name])

    worksheet = preset.worksheet
    return Worksheet(
        title=worksheet.title,
        locale=worksheet.locale,
        student_fields=worksheet.student_fields,
        sections={
            display_name: tuple(questions)
            for display_name, questions in grouped_questions.items()
        },
        section_columns={
            display_name: section.columns
            for display_name, (section, _) in first_sources.items()
        },
        section_order=tuple(first_sources),
        section_headings={
            display_name: (
                section.heading
                or plugin.presentation(section.name, worksheet.locale)[0]
            )
            for display_name, (section, plugin) in first_sources.items()
        },
        section_intros={
            display_name: (
                section.instructions
                or plugin.presentation(section.name, worksheet.locale)[1]
            )
            for display_name, (section, plugin) in first_sources.items()
        },
    )


def _create_plugin(section: SectionSettings):
    return get_plugin_definition(section.plugin).create(section.settings)
