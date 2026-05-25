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

    pages: list[list[str]] = []
    commands = _start_page(worksheet, text, first_page=True)
    y = 720
    for section_name in worksheet.section_order:
        questions = worksheet.sections.get(section_name, ())
        if not questions:
            continue
        heading = worksheet.section_headings[section_name]
        columns = worksheet.section_columns.get(section_name, 1)
        question_index = 0
        continued = False
        while question_index < len(questions):
            section_heading = f"{heading} (continued)" if continued else heading
            instructions = () if continued else worksheet.section_intros.get(section_name, ())
            required_header_space = 20 + (len(instructions) * 17) + 14
            if y - required_header_space < 82:
                pages.append(commands)
                commands = _start_page(worksheet, text, first_page=False)
                y = 755

            _add_text(commands, section_heading, 48, y, 13, bold=True)
            y -= 20
            for instruction in instructions:
                _add_text(commands, instruction, 48, y, 9)
                y -= 17
            y -= 14

            row_height = 31 if columns == 1 else 29
            available_rows = max(1, int((y - 58) // row_height) + 1)
            page_capacity = available_rows * columns
            chunk = questions[question_index : question_index + page_capacity]
            rows = (len(chunk) + columns - 1) // columns
            for local_index, question in enumerate(chunk):
                column = local_index // rows
                row = local_index % rows
                x = 58 + column * 250
                question_y = y - row * row_height
                _add_text(
                    commands,
                    f"{question_index + local_index + 1}.  {question.display_text}",
                    x,
                    question_y,
                    11,
                )
            y -= rows * row_height + 8
            question_index += len(chunk)
            continued = True
            if question_index < len(questions):
                pages.append(commands)
                commands = _start_page(worksheet, text, first_page=False)
                y = 755

    pages.append(commands)
    total_pages = len(pages)
    for page_number, page_commands in enumerate(pages, start=1):
        _add_text(page_commands, "Generated practice worksheet", 48, 28, 8)
        _add_text(page_commands, f"Page {page_number} of {total_pages}", 476, 28, 8)
    streams = ["\n".join(page).encode("latin-1") for page in pages]
    return _pdf_document(streams)


def _start_page(worksheet: Worksheet, text: dict[str, dict[str, str]], first_page: bool) -> list[str]:
    commands: list[str] = []
    if first_page:
        _add_text(commands, worksheet.title, 48, 795, 18, bold=True)
        field_line = "       ".join(
            f"{text['fields'].get(field, field.title())}: ____________________"
            for field in worksheet.student_fields
        )
        _add_text(commands, field_line, 48, 763, 10)
        commands.append("0.65 w 48 748 m 547 748 l S")
    else:
        _add_text(commands, worksheet.title, 48, 795, 13, bold=True)
        commands.append("0.65 w 48 778 m 547 778 l S")
    return commands


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


def _pdf_document(streams: list[bytes]) -> bytes:
    page_count = len(streams)
    page_ids = list(range(3, 3 + page_count))
    content_ids = list(range(3 + page_count, 3 + (2 * page_count)))
    normal_font_id = 3 + (2 * page_count)
    bold_font_id = normal_font_id + 1
    kid_references = " ".join(f"{page_id} 0 R" for page_id in page_ids).encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [" + kid_references + b"] /Count " + str(page_count).encode("ascii") + b" >>",
    ]
    for content_id in content_ids:
        objects.append(
            (
                b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] "
                b"/Resources << /Font << /F1 "
                + str(normal_font_id).encode("ascii")
                + b" 0 R /F2 "
                + str(bold_font_id).encode("ascii")
                + b" 0 R >> >> /Contents "
                + str(content_id).encode("ascii")
                + b" 0 R >>"
            )
        )
    for stream in streams:
        objects.append(
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )
    objects.extend(
        [
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
        ]
    )
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
