from dataclasses import asdict

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
                .options(selectinload(PracticeSessionEntity.questions))
            ).one_or_none()
            if result is None:
                raise ValueError("Unknown student session token")
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
            question = database_session.scalars(
                select(QuestionInstanceEntity)
                .join(QuestionInstanceEntity.practice_session)
                .where(
                    PracticeSessionEntity.student_token == token,
                    QuestionInstanceEntity.public_identifier == question_identifier,
                )
                .options(selectinload(QuestionInstanceEntity.attempts))
            ).one_or_none()
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
            database_session.commit()
            return attempt
