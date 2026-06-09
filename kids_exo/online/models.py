from dataclasses import dataclass, field
from typing import Any

from kids_exo.localization import LocalizedPresentation
from kids_exo.online.evaluation import evaluate_answer


@dataclass(frozen=True)
class StudentQuestionView:
    identifier: str
    position: int
    total_questions: int
    prompt: str
    renderer_type: str = "numeric_answer"
    prompt_payload: dict[str, Any] = field(default_factory=dict)
    public_payload: dict[str, Any] = field(default_factory=dict)
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
    skill_tags: tuple[str, ...]
    expected_answer: int | None = None
    renderer_type: str = "numeric_answer"
    answer_type: str = "integer_exact"
    evaluation_payload: dict[str, Any] = field(default_factory=dict)
    prompt_payload: dict[str, Any] = field(default_factory=dict)
    public_payload: dict[str, Any] = field(default_factory=dict)
    question_type: str = "numeric"
    choices: tuple[str, ...] = ()
    speech_text: str | None = None
    speech_locale: str | None = None
    audio_url: str | None = None


@dataclass(frozen=True)
class AnswerEvaluation:
    question_identifier: str
    normalized_answer: int | str | dict[str, Any]
    is_correct: bool
    detail: dict[str, Any] = field(default_factory=dict)


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
                renderer_type=question.renderer_type,
                prompt_payload=question.prompt_payload,
                public_payload=question.public_payload,
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
        result = evaluate_answer(
            question.answer_type,
            question.evaluation_payload,
            submitted_answer,
        )
        return AnswerEvaluation(
            question_identifier=question_identifier,
            normalized_answer=result.normalized_answer,
            is_correct=result.is_correct,
            detail=result.detail,
        )

    def _find_question(self, identifier: str) -> OnlineQuestionSnapshot:
        for question in self.questions:
            if question.identifier == identifier:
                return question
        raise ValueError(f"Unknown question identifier: {identifier}")
