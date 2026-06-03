from dataclasses import dataclass
from typing import Any

from kids_exo.localization import LocalizedPresentation


@dataclass(frozen=True)
class StudentQuestionView:
    identifier: str
    position: int
    total_questions: int
    prompt: str
    question_type: str = "numeric"
    choices: tuple[str, ...] = ()
    speech_text: str | None = None
    speech_locale: str | None = None
    audio_url: str | None = None


@dataclass(frozen=True)
class OnlineQuestionSnapshot:
    identifier: str
    prompt: str
    strategy: str
    expected_answer: int
    skill_tags: tuple[str, ...]
    question_type: str = "numeric"
    choices: tuple[str, ...] = ()
    speech_text: str | None = None
    speech_locale: str | None = None
    audio_url: str | None = None


@dataclass(frozen=True)
class AnswerEvaluation:
    question_identifier: str
    normalized_answer: int
    is_correct: bool


@dataclass(frozen=True)
class PracticeSessionSnapshot:
    plugin: str
    subject: str
    category: str
    skill: str
    plugin_settings: Any
    requested_locale: str
    feedback_mode: str
    show_timer: bool
    seed: int | None
    presentation: LocalizedPresentation
    questions: tuple[OnlineQuestionSnapshot, ...]

    @property
    def localization_fallback_keys(self) -> tuple[str, ...]:
        return self.presentation.fallback_keys

    def student_questions(self) -> tuple[StudentQuestionView, ...]:
        total = len(self.questions)
        return tuple(
            StudentQuestionView(
                identifier=question.identifier,
                position=position,
                total_questions=total,
                prompt=question.prompt,
                question_type=question.question_type,
                choices=question.choices,
                speech_text=question.speech_text,
                speech_locale=question.speech_locale,
                audio_url=question.audio_url,
            )
            for position, question in enumerate(self.questions, start=1)
        )

    def evaluate_answer(self, question_identifier: str, submitted_answer: str) -> AnswerEvaluation:
        question = self._find_question(question_identifier)
        try:
            normalized_answer = int(submitted_answer.strip())
        except ValueError as exc:
            raise ValueError("Submitted answer must be an integer") from exc
        return AnswerEvaluation(
            question_identifier=question_identifier,
            normalized_answer=normalized_answer,
            is_correct=normalized_answer == question.expected_answer,
        )

    def _find_question(self, identifier: str) -> OnlineQuestionSnapshot:
        for question in self.questions:
            if question.identifier == identifier:
                return question
        raise ValueError(f"Unknown question identifier: {identifier}")
