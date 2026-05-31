from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import secrets

from sqlalchemy import select
from sqlalchemy.orm import selectinload, sessionmaker

from kids_exo.online.models import PracticeSessionSnapshot
from kids_exo.persistence.models import (
    LearnerEntity,
    PracticeSessionEntity,
    QuestionInstanceEntity,
    ResponseAttemptEntity,
)


@dataclass(frozen=True)
class LearnerSkillBreakdown:
    plugin: str
    correct_answers: int
    total_questions: int
    accuracy: float


@dataclass(frozen=True)
class LearnerMistakeEntry:
    plugin: str
    prompt: str
    expected_answer: int
    last_submitted_answer: int
    times_missed: int
    last_seen_at: datetime


@dataclass(frozen=True)
class LearnerAnalytics:
    total_sessions: int
    completed_sessions: int
    total_questions: int
    correct_answers: int
    accuracy: float
    average_elapsed_seconds: int | None
    last_completed_at: datetime | None
    skill_breakdown: tuple[LearnerSkillBreakdown, ...]
    mistake_notebook: tuple[LearnerMistakeEntry, ...]


_SESSION_TOKEN_ALPHABET = "23456789abcdefghjkmnpqrstvwxyz"


class PracticeRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def create_learner(self, nickname: str) -> LearnerEntity:
        nickname = nickname.strip()
        if not nickname:
            raise ValueError("Learner nickname is required")
        with self._session_factory() as database_session:
            learner = LearnerEntity(nickname=nickname, active=True)
            database_session.add(learner)
            database_session.commit()
            return learner

    def list_learners(self) -> list[LearnerEntity]:
        with self._session_factory() as database_session:
            return list(
                database_session.scalars(
                    select(LearnerEntity).order_by(LearnerEntity.nickname, LearnerEntity.id)
                )
            )

    def get_learner(self, learner_id: int) -> LearnerEntity:
        with self._session_factory() as database_session:
            learner = database_session.get(LearnerEntity, learner_id)
            if learner is None:
                raise ValueError(f"Unknown learner: {learner_id}")
            return learner

    def update_learner(
        self,
        learner_id: int,
        *,
        nickname: str,
        active: bool,
    ) -> LearnerEntity:
        nickname = nickname.strip()
        if not nickname:
            raise ValueError("Learner nickname is required")
        with self._session_factory() as database_session:
            learner = database_session.get(LearnerEntity, learner_id)
            if learner is None:
                raise ValueError(f"Unknown learner: {learner_id}")
            learner.nickname = nickname
            learner.active = active
            database_session.commit()
            return learner

    def delete_learner(self, learner_id: int) -> None:
        with self._session_factory() as database_session:
            learner = database_session.get(LearnerEntity, learner_id)
            if learner is None:
                raise ValueError(f"Unknown learner: {learner_id}")
            database_session.delete(learner)
            database_session.commit()

    def create_practice_session(
        self,
        learner_id: int,
        snapshot: PracticeSessionSnapshot,
        *,
        student_token: str | None = None,
    ) -> PracticeSessionEntity:
        with self._session_factory() as database_session:
            if database_session.get(LearnerEntity, learner_id) is None:
                raise ValueError(f"Unknown learner: {learner_id}")
            practice_session = PracticeSessionEntity(
                learner_id=learner_id,
                student_token=student_token or "pending-token",
                plugin=snapshot.plugin,
                plugin_settings=asdict(snapshot.plugin_settings),
                requested_locale=snapshot.requested_locale,
                feedback_mode=snapshot.feedback_mode,
                show_timer=snapshot.show_timer,
                seed=snapshot.seed,
                localization_fallback_keys=list(snapshot.localization_fallback_keys),
                status="created",
                questions=[
                    QuestionInstanceEntity(
                        public_identifier=question.identifier,
                        position=position,
                        prompt=question.prompt,
                        strategy=question.strategy,
                        expected_answer=question.expected_answer,
                        skill_tags=list(question.skill_tags),
                    )
                    for position, question in enumerate(snapshot.questions, start=1)
                ],
            )
            database_session.add(practice_session)
            database_session.flush()
            if student_token is None:
                practice_session.student_token = self._generate_student_token(
                    database_session,
                    practice_session.id,
                )
            database_session.commit()
            return practice_session

    def get_session_by_student_token(self, token: str) -> PracticeSessionEntity:
        with self._session_factory() as database_session:
            result = database_session.scalars(
                select(PracticeSessionEntity)
                .where(PracticeSessionEntity.student_token == token)
                .options(
                    selectinload(PracticeSessionEntity.questions).selectinload(
                        QuestionInstanceEntity.attempts
                    )
                )
            ).one_or_none()
            if result is None:
                raise ValueError("Unknown student session token")
            return result

    def start_student_session(self, token: str) -> PracticeSessionEntity:
        with self._session_factory() as database_session:
            practice_session = database_session.scalars(
                select(PracticeSessionEntity).where(
                    PracticeSessionEntity.student_token == token
                )
            ).one_or_none()
            if practice_session is None:
                raise ValueError("Unknown student session token")
            if practice_session.status == "created":
                practice_session.status = "in_progress"
                practice_session.started_at = datetime.now(timezone.utc)
                database_session.commit()
            return practice_session

    def list_sessions_for_learner(self, learner_id: int) -> list[PracticeSessionEntity]:
        with self._session_factory() as database_session:
            if database_session.get(LearnerEntity, learner_id) is None:
                raise ValueError(f"Unknown learner: {learner_id}")
            return list(
                database_session.scalars(
                    select(PracticeSessionEntity)
                    .where(PracticeSessionEntity.learner_id == learner_id)
                    .options(
                        selectinload(PracticeSessionEntity.questions).selectinload(
                            QuestionInstanceEntity.attempts
                        )
                    )
                    .order_by(PracticeSessionEntity.id.desc())
                )
            )

    def get_results_for_learner(
        self,
        learner_id: int,
        session_id: int,
    ) -> PracticeSessionEntity:
        with self._session_factory() as database_session:
            result = database_session.scalars(
                select(PracticeSessionEntity)
                .where(
                    PracticeSessionEntity.id == session_id,
                    PracticeSessionEntity.learner_id == learner_id,
                )
                .options(
                    selectinload(PracticeSessionEntity.questions).selectinload(
                        QuestionInstanceEntity.attempts
                    )
                )
            ).one_or_none()
            if result is None:
                raise ValueError("Unknown practice session")
            if not self._is_complete(result):
                raise ValueError("Practice session is not completed")
            return result

    def get_learner_analytics(self, learner_id: int) -> LearnerAnalytics:
        sessions = self.list_sessions_for_learner(learner_id)
        completed_sessions = [
            saved_session
            for saved_session in sessions
            if self._is_complete(saved_session)
        ]
        total_questions = sum(len(saved_session.questions) for saved_session in completed_sessions)
        correct_answers = sum(
            sum(question.attempts[0].is_correct for question in saved_session.questions if question.attempts)
            for saved_session in completed_sessions
        )
        elapsed_values = [
            elapsed
            for saved_session in completed_sessions
            if (elapsed := self._elapsed_seconds(saved_session)) is not None
        ]

        skill_totals: dict[str, dict[str, int]] = {}
        mistakes: dict[tuple[str, str, int], LearnerMistakeEntry] = {}
        for saved_session in completed_sessions:
            completed_at = saved_session.completed_at or saved_session.created_at
            for question in saved_session.questions:
                attempt = question.attempts[0]
                totals = skill_totals.setdefault(
                    saved_session.plugin,
                    {"correct_answers": 0, "total_questions": 0},
                )
                totals["total_questions"] += 1
                totals["correct_answers"] += int(attempt.is_correct)
                if attempt.is_correct:
                    continue
                key = (saved_session.plugin, question.prompt, question.expected_answer)
                previous = mistakes.get(key)
                if previous is None:
                    mistakes[key] = LearnerMistakeEntry(
                        plugin=saved_session.plugin,
                        prompt=question.prompt,
                        expected_answer=question.expected_answer,
                        last_submitted_answer=attempt.normalized_answer,
                        times_missed=1,
                        last_seen_at=completed_at,
                    )
                    continue
                if completed_at >= previous.last_seen_at:
                    last_submitted_answer = attempt.normalized_answer
                    last_seen_at = completed_at
                else:
                    last_submitted_answer = previous.last_submitted_answer
                    last_seen_at = previous.last_seen_at
                mistakes[key] = LearnerMistakeEntry(
                    plugin=previous.plugin,
                    prompt=previous.prompt,
                    expected_answer=previous.expected_answer,
                    last_submitted_answer=last_submitted_answer,
                    times_missed=previous.times_missed + 1,
                    last_seen_at=last_seen_at,
                )

        skill_breakdown = tuple(
            sorted(
                (
                    LearnerSkillBreakdown(
                        plugin=plugin,
                        correct_answers=totals["correct_answers"],
                        total_questions=totals["total_questions"],
                        accuracy=(
                            totals["correct_answers"] / totals["total_questions"]
                            if totals["total_questions"]
                            else 0.0
                        ),
                    )
                    for plugin, totals in skill_totals.items()
                ),
                key=lambda item: (item.accuracy, -item.total_questions, item.plugin),
            )
        )
        mistake_notebook = tuple(
            sorted(
                mistakes.values(),
                key=lambda item: (-item.times_missed, -item.last_seen_at.timestamp(), item.prompt),
            )
        )
        return LearnerAnalytics(
            total_sessions=len(sessions),
            completed_sessions=len(completed_sessions),
            total_questions=total_questions,
            correct_answers=correct_answers,
            accuracy=(correct_answers / total_questions if total_questions else 0.0),
            average_elapsed_seconds=(
                sum(elapsed_values) // len(elapsed_values)
                if elapsed_values
                else None
            ),
            last_completed_at=max(
                (saved_session.completed_at for saved_session in completed_sessions),
                default=None,
            ),
            skill_breakdown=skill_breakdown,
            mistake_notebook=mistake_notebook,
        )

    def get_completed_results_by_student_token(self, token: str) -> PracticeSessionEntity:
        result = self.get_session_by_student_token(token)
        if not self._is_complete(result):
            raise ValueError("Practice session is not completed")
        return result

    def submit_answer(
        self,
        token: str,
        question_identifier: str,
        submitted_answer: str,
    ) -> ResponseAttemptEntity:
        try:
            normalized_answer = int(submitted_answer.strip())
        except ValueError as exc:
            raise ValueError("Submitted answer must be an integer") from exc
        with self._session_factory() as database_session:
            practice_session = database_session.scalars(
                select(PracticeSessionEntity)
                .where(PracticeSessionEntity.student_token == token)
                .options(
                    selectinload(PracticeSessionEntity.questions).selectinload(
                        QuestionInstanceEntity.attempts
                    )
                )
            ).one_or_none()
            if practice_session is None:
                raise ValueError("Unknown student session token")
            question = next(
                (
                    saved_question
                    for saved_question in practice_session.questions
                    if saved_question.public_identifier == question_identifier
                ),
                None,
            )
            if question is None:
                raise ValueError("Unknown student question")
            if question.attempts:
                raise ValueError("Question already submitted")
            attempt = ResponseAttemptEntity(
                question_instance_id=question.id,
                attempt_number=len(question.attempts) + 1,
                submitted_answer=submitted_answer,
                normalized_answer=normalized_answer,
                is_correct=normalized_answer == question.expected_answer,
            )
            database_session.add(attempt)
            if practice_session.status == "created":
                practice_session.status = "in_progress"
                practice_session.started_at = datetime.now(timezone.utc)
            if all(
                saved_question.attempts or saved_question.id == question.id
                for saved_question in practice_session.questions
            ):
                practice_session.status = "completed"
                practice_session.completed_at = datetime.now(timezone.utc)
            database_session.commit()
            return attempt

    @staticmethod
    def _is_complete(practice_session: PracticeSessionEntity) -> bool:
        return bool(practice_session.questions) and all(
            question.attempts for question in practice_session.questions
        )

    @staticmethod
    def _elapsed_seconds(practice_session: PracticeSessionEntity) -> int | None:
        if practice_session.started_at is None or practice_session.completed_at is None:
            return None
        return max(
            0,
            int((practice_session.completed_at - practice_session.started_at).total_seconds()),
        )

    @staticmethod
    def _generate_student_token(database_session, session_id: int) -> str:
        while True:
            secret = "".join(
                secrets.choice(_SESSION_TOKEN_ALPHABET)
                for _ in range(8)
            )
            token = f"s{session_id}-{secret}"
            existing = database_session.scalar(
                select(PracticeSessionEntity.id).where(
                    PracticeSessionEntity.student_token == token
                )
            )
            if existing is None:
                return token
