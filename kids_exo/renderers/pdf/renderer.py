from pathlib import Path

from kids_exo.models import Worksheet
from kids_exo.renderers.pdf.settings import PdfOutputOptions


A4_WIDTH = 595.28
A4_HEIGHT = 841.89

TEXT_RESOURCES = {
    "en-CA": {
        "fields": {
            "name": "Name",
            "date": "Date",
            "time": "Time",
            "score": "Score",
        },
    }
}


def write_pdf(
    worksheet: Worksheet,
    options: PdfOutputOptions,
    output_path: str | Path,
) -> None:
    """Write the first printable layout from generated worksheet content."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_build_pdf(worksheet, options))


def _build_pdf(worksheet: Worksheet, options: PdfOutputOptions) -> bytes:
    if options.paper_size != "A4" or options.orientation != "portrait":
        raise ValueError("The first PDF renderer supports A4 portrait worksheets only")
    try:
        text = TEXT_RESOURCES[worksheet.locale]
    except KeyError as exc:
        raise ValueError(f"Unsupported PDF locale: {worksheet.locale}") from exc

    commands: list[str] = []
    _add_text(commands, worksheet.title, 48, 795, 18, bold=True)
    field_line = "       ".join(
        f"{text['fields'].get(field, field.title())}: ____________________"
        for field in worksheet.student_fields
    )
    _add_text(commands, field_line, 48, 763, 10)
    commands.append("0.65 w 48 748 m 547 748 l S")

    y = 720
    for section_name in worksheet.section_order:
        questions = worksheet.sections.get(section_name, ())
        if not questions:
            continue
        heading = worksheet.section_headings[section_name]
        _add_text(commands, heading, 48, y, 13, bold=True)
        y -= 20
        for instruction in worksheet.section_intros.get(section_name, ()):
            _add_text(commands, instruction, 48, y, 9)
            y -= 17
        y -= 14
        columns = worksheet.section_columns.get(section_name, 1)
        rows = (len(questions) + columns - 1) // columns
        column_width = 250
        for index, question in enumerate(questions):
            column = index // rows
            row = index % rows
            x = 58 + column * column_width
            question_y = y - row * (31 if columns == 1 else 29)
            _add_text(commands, f"{index + 1}.  {question.display_text}", x, question_y, 11)
        y -= rows * (31 if columns == 1 else 29) + 8

    _add_text(commands, "Generated practice worksheet", 48, 28, 8)
    stream = "\n".join(commands).encode("latin-1")
    return _pdf_document(stream)


def _add_text(
    commands: list[str],
    value: str,
    x: float,
    y: float,
    font_size: int,
    bold: bool = False,
) -> None:
    font = "F2" if bold else "F1"
    commands.append(
        f"BT /{font} {font_size} Tf {x:.2f} {y:.2f} Td ({_escape_text(value)}) Tj ET"
    )


def _escape_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _pdf_document(stream: bytes) -> bytes:
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] "
            b"/Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> /Contents 4 0 R >>"
        ),
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
    ]
    document = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(document))
        document.extend(f"{number} 0 obj\n".encode("ascii"))
        document.extend(obj)
        document.extend(b"\nendobj\n")

    xref_offset = len(document)
    document.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    document.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        document.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    document.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(document)
