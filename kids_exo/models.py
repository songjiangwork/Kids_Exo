from dataclasses import dataclass


@dataclass(frozen=True)
class Decomposition:
    """Structured mathematical breakdown provided by a question plugin."""

    operator: str
    first_part: int
    second_part: int
    round_number: int | None = None
    difference: int | None = None


@dataclass(frozen=True)
class Question:
    section: str
    format: str
    left_operand: int
    right_operand: int
    strategy: str
    decomposition: Decomposition | None
    display_text: str

    @property
    def expression(self) -> str:
        return f"{self.left_operand} x {self.right_operand}"


@dataclass(frozen=True)
class Worksheet:
    title: str
    locale: str
    student_fields: tuple[str, ...]
    sections: dict[str, tuple[Question, ...]]
    section_columns: dict[str, int]
    section_order: tuple[str, ...]
    section_headings: dict[str, str]
    section_intros: dict[str, tuple[str, ...]]

    @property
    def all_questions(self) -> tuple[Question, ...]:
        return tuple(question for questions in self.sections.values() for question in questions)
