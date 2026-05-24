from dataclasses import dataclass


@dataclass(frozen=True)
class PdfOutputOptions:
    paper_size: str
    orientation: str


def load_options(data: dict) -> PdfOutputOptions:
    options = PdfOutputOptions(
        paper_size=data.get("paper_size", "A4"),
        orientation=data.get("orientation", "portrait"),
    )
    if options.paper_size != "A4":
        raise ValueError("Version 1 currently supports A4 paper size only")
    if options.orientation != "portrait":
        raise ValueError("Version 1 currently supports portrait orientation only")
    return options
