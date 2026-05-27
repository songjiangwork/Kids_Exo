from dataclasses import dataclass
from datetime import datetime

from kids_exo.catalog import get_preset_entry
from kids_exo.config import load_preset
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
    generated_at: datetime | None = None,
) -> PrintablePdf:
    entry = get_preset_entry(preset_id)
    preset = load_preset(entry.preset_path)
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
