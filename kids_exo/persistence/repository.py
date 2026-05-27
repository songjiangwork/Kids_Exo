from dataclasses import asdict
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload, sessionmaker

from kids_exo.online.models import PracticeSessionSnapshot
from kids_exo.persistence.models import (
    LearnerEntity,
    PracticeSessionEntity,
    QuestionInstanceEntity,
    ResponseAttemptEntity,
)


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

    def create_practice_session(
        self,
        learner_id: int,
        snapshot: PracticeSessionSnapshot,
        *,
        student_token: str,
    ) -> PracticeSessionEntity:
        with self._session_factory() as database_session:
            if database_session.get(LearnerEntity, learner_id) is None:
                raise ValueError(f"Unknown learner: {learner_id}")
            practice_session = PracticeSessionEntity(
                learner_id=learner_id,
                student_token=student_token,
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
