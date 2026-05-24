from typing import Protocol
import random

from kids_exo.config import SectionSettings
from kids_exo.models import Question


class QuestionPlugin(Protocol):
    def generate(
        self,
        section_name: str,
        section: SectionSettings,
        rng: random.Random,
        used_expressions: set[str],
    ) -> tuple[Question, ...]: ...
