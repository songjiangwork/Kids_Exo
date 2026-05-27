from dataclasses import dataclass, replace
from datetime import datetime

from kids_exo.catalog import get_preset_entry
from kids_exo.config import Preset, SectionSettings, load_preset
from kids_exo.generator import generate_worksheet
from kids_exo.renderers.pdf import render_pdf


@dataclass(frozen=True)
class PrintablePdf:
    filename: str
    content: bytes


def generate_printable_pdf(
    preset_id: str,
    *,
    seed: int | None = None,
    include_warmup: bool = True,
    page_count: int = 1,
    question_count: int | None = None,
    generated_at: datetime | None = None,
) -> PrintablePdf:
    entry = get_preset_entry(preset_id)
    preset = load_preset(entry.preset_path)
    if not include_warmup:
        preset = replace(
            preset,
            sections=tuple(
                section for section in preset.sections if section.name != "warmup"
            ),
        )
    target_question_count = question_count or practice_question_count_for_pages(
        page_count,
        include_warmup=include_warmup,
    )
    preset = _with_practice_question_count(preset, target_question_count)
    worksheet = generate_worksheet(preset, seed=seed)
    if preset.output.renderer != "pdf":
        raise ValueError(f"Unsupported output renderer: {preset.output.renderer}")
    marker = (
        f"seed-{seed}"
        if seed is not None
        else (generated_at or datetime.now()).strftime("%Y%m%d-%H%M%S")
    )
    stem = entry.default_output_filename.removesuffix(".pdf")
    return PrintablePdf(
        filename=f"{stem}-{marker}.pdf",
        content=render_pdf(worksheet, preset.output.options),
    )


def practice_question_count_for_pages(page_count: int, *, include_warmup: bool) -> int:
    """Estimate practice count from the current A4 PDF layout capacity."""

    if page_count < 1:
        raise ValueError("page_count must be at least 1")
    first_page_capacity = 30 if include_warmup else 44
    return first_page_capacity + ((page_count - 1) * 46)


def _with_practice_question_count(preset: Preset, question_count: int) -> Preset:
    if question_count < 1:
        raise ValueError("question_count must be at least 1")
    target_indexes = tuple(
        index for index, section in enumerate(preset.sections) if section.name != "warmup"
    )
    if not target_indexes:
        raise ValueError("A printable worksheet must contain at least one practice section")
    allocated_counts = _allocate_counts(
        question_count,
        tuple(preset.sections[index].count for index in target_indexes),
    )
    sections = list(preset.sections)
    for index, count in zip(target_indexes, allocated_counts, strict=True):
        section = sections[index]
        sections[index] = replace(
            section,
            count=count,
            settings=_allow_duplicates_if_expanded(section, count),
        )
    return replace(preset, sections=tuple(sections))


def _allocate_counts(total_count: int, source_counts: tuple[int, ...]) -> tuple[int, ...]:
    if len(source_counts) == 1:
        return (total_count,)
    source_total = sum(source_counts)
    if source_total <= 0:
        base = [total_count // len(source_counts)] * len(source_counts)
        for index in range(total_count % len(source_counts)):
            base[index] += 1
        return tuple(base)
    raw_allocations = [
        (total_count * count, index)
        for index, count in enumerate(source_counts)
    ]
    base = [value // source_total for value, _ in raw_allocations]
    remaining = total_count - sum(base)
    remainders = sorted(
        ((value % source_total, index) for value, index in raw_allocations),
        reverse=True,
    )
    for _, index in remainders[:remaining]:
        base[index] += 1
    return tuple(base)


def _allow_duplicates_if_expanded(section: SectionSettings, count: int):
    if count <= section.count or not hasattr(section.settings, "allow_duplicates"):
        return section.settings
    return replace(section.settings, allow_duplicates=True)
