from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
import secrets

from sqlalchemy import select
from sqlalchemy.orm import selectinload, sessionmaker

from kids_exo.online.answer_display import (
    AnswerValue,
    answer_display,
    expected_answer_value_for_question,
    submitted_answer_value_for_attempt,
    value_for_legacy_integer_column,
)
from kids_exo.online.evaluation import evaluate_answer
from kids_exo.online.models import PracticeSessionSnapshot
from kids_exo.persistence.models import (
    AssignmentEntity,
    AssignmentItemEntity,
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
    expected_answer: AnswerValue
    last_submitted_answer: AnswerValue
    expected_display: str | None
    last_submitted_display: str | None
    answer_type: str | None
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


@dataclass(frozen=True)
class AssignmentStartResult:
    assignment: AssignmentEntity
    item: AssignmentItemEntity
    practice_session: PracticeSessionEntity


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

    def create_assignment(
        self,
        learner_id: int,
        *,
        title: str,
        description: str = "",
        source_type: str = "parent_assigned",
        due_at: datetime | None = None,
        created_by_role: str = "parent",
        items: list[dict] | tuple[dict, ...],
    ) -> AssignmentEntity:
        title = title.strip()
        if not title:
            raise ValueError("Assignment title is required")
        if not items:
            raise ValueError("Assignment must include at least one item")
        with self._session_factory() as database_session:
            if database_session.get(LearnerEntity, learner_id) is None:
                raise ValueError(f"Unknown learner: {learner_id}")
            now = self._now()
            assignment = AssignmentEntity(
                learner_id=learner_id,
                title=title,
                description=description.strip(),
                status="assigned",
                source_type=source_type,
                due_at=due_at,
                created_by_role=created_by_role,
                created_at=now,
                updated_at=now,
                items=[
                    AssignmentItemEntity(
                        item_type=item.get("item_type", "practice_plugin"),
                        plugin=item["plugin"],
                        plugin_settings=dict(item.get("plugin_settings", {})),
                        question_count=int(item["question_count"]),
                        feedback_mode=item.get("feedback_mode", "immediate"),
                        show_timer=bool(item.get("show_timer", True)),
                        order_index=position,
                        required=bool(item.get("required", True)),
                        status="assigned",
                        created_at=now,
                    )
                    for position, item in enumerate(items, start=1)
                ],
            )
            database_session.add(assignment)
            database_session.commit()
            return assignment

    def list_assignments_for_learner(
        self,
        learner_id: int,
        *,
        status: str | None = None,
    ) -> list[AssignmentEntity]:
        with self._session_factory() as database_session:
            if database_session.get(LearnerEntity, learner_id) is None:
                raise ValueError(f"Unknown learner: {learner_id}")
            query = (
                select(AssignmentEntity)
                .where(AssignmentEntity.learner_id == learner_id)
                .options(
                    selectinload(AssignmentEntity.items).selectinload(
                        AssignmentItemEntity.linked_session
                    )
                )
                .order_by(AssignmentEntity.created_at.desc(), AssignmentEntity.id.desc())
            )
            if status and status != "all":
                query = query.where(AssignmentEntity.status == status)
            elif status is None:
                query = query.where(AssignmentEntity.status != "archived")
            return list(database_session.scalars(query))

    def get_assignment(self, assignment_id: int) -> AssignmentEntity:
        with self._session_factory() as database_session:
            assignment = database_session.scalars(
                select(AssignmentEntity)
                .where(AssignmentEntity.id == assignment_id)
                .options(
                    selectinload(AssignmentEntity.items).selectinload(
                        AssignmentItemEntity.linked_session
                    )
                )
            ).one_or_none()
            if assignment is None:
                raise ValueError(f"Unknown assignment: {assignment_id}")
            return assignment

    def update_assignment_status(self, assignment_id: int, status: str) -> AssignmentEntity:
        with self._session_factory() as database_session:
            assignment = self._get_assignment_for_update(database_session, assignment_id)
            now = self._now()
            assignment.status = status
            assignment.updated_at = now
            assignment.completed_at = now if status == "completed" else assignment.completed_at
            database_session.commit()
            return assignment

    def archive_assignment(self, assignment_id: int) -> AssignmentEntity:
        return self.update_assignment_status(assignment_id, "archived")

    def start_assignment_item(
        self,
        assignment_id: int,
        item_id: int,
        snapshot: PracticeSessionSnapshot | None = None,
    ) -> AssignmentStartResult:
        with self._session_factory() as database_session:
            assignment = self._get_assignment_for_update(database_session, assignment_id)
            item = next((candidate for candidate in assignment.items if candidate.id == item_id), None)
            if item is None:
                raise ValueError(f"Unknown assignment item: {item_id}")
            if item.item_type != "practice_plugin":
                raise ValueError(f"Unsupported assignment item type: {item.item_type}")
            now = self._now()
            if item.linked_session is None:
                if snapshot is None:
                    raise ValueError("Practice snapshot is required to start this assignment item")
                practice_session = self._build_practice_session(assignment.learner_id, snapshot)
                database_session.add(practice_session)
                database_session.flush()
                practice_session.student_token = self._generate_student_token(
                    database_session,
                    practice_session.id,
                )
                item.linked_session = practice_session
            else:
                practice_session = item.linked_session
            if item.status == "assigned":
                item.status = "in_progress"
            if assignment.status == "assigned":
                assignment.status = "in_progress"
            assignment.updated_at = now
            database_session.commit()
            return AssignmentStartResult(assignment, item, practice_session)

    def mark_assignment_item_completed(
        self,
        assignment_id: int,
        item_id: int,
    ) -> AssignmentEntity:
        with self._session_factory() as database_session:
            assignment = self._get_assignment_for_update(database_session, assignment_id)
            item = next((candidate for candidate in assignment.items if candidate.id == item_id), None)
            if item is None:
                raise ValueError(f"Unknown assignment item: {item_id}")
            self._mark_item_completed(database_session, assignment, item, self._now())
            database_session.commit()
            return assignment

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
            practice_session = self._build_practice_session(learner_id, snapshot)
            if student_token is not None:
                practice_session.student_token = student_token
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
            now = self._now()
            practice_session = database_session.scalars(
                select(PracticeSessionEntity).where(
                    PracticeSessionEntity.student_token == token
                )
            ).one_or_none()
            if practice_session is None:
                raise ValueError("Unknown student session token")
            should_commit = False
            if practice_session.status == "created":
                practice_session.status = "in_progress"
                practice_session.started_at = now
                should_commit = True
            if practice_session.show_timer and practice_session.status != "completed":
                self._settle_stale_timer(practice_session)
                practice_session.timer_started_at = now
                should_commit = True
            if should_commit:
                database_session.commit()
            return practice_session

    def pause_student_timer(self, token: str) -> PracticeSessionEntity:
        with self._session_factory() as database_session:
            practice_session = self._get_session_for_timer_update(database_session, token)
            self._settle_timer(practice_session, self._now())
            database_session.commit()
            return practice_session

    def resume_student_timer(self, token: str) -> PracticeSessionEntity:
        with self._session_factory() as database_session:
            now = self._now()
            practice_session = self._get_session_for_timer_update(database_session, token)
            if practice_session.status == "created":
                practice_session.status = "in_progress"
                practice_session.started_at = now
            if self._is_complete(practice_session):
                practice_session.status = "completed"
                database_session.commit()
                return practice_session
            if practice_session.show_timer:
                self._settle_stale_timer(practice_session)
                practice_session.timer_started_at = now
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
        mistakes: dict[tuple[str, str, str | None], LearnerMistakeEntry] = {}
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
                expected_answer = expected_answer_value_for_question(question)
                expected_display = _expected_answer_display(question)
                submitted_answer = submitted_answer_value_for_attempt(attempt)
                submitted_display = answer_display(submitted_answer)
                key = (saved_session.plugin, question.prompt, expected_display)
                previous = mistakes.get(key)
                if previous is None:
                    mistakes[key] = LearnerMistakeEntry(
                        plugin=saved_session.plugin,
                        prompt=question.prompt,
                        expected_answer=expected_answer,
                        last_submitted_answer=submitted_answer,
                        expected_display=expected_display,
                        last_submitted_display=submitted_display,
                        answer_type=question.answer_type,
                        times_missed=1,
                        last_seen_at=completed_at,
                    )
                    continue
                if completed_at >= previous.last_seen_at:
                    last_submitted_answer = submitted_answer
                    last_submitted_display = submitted_display
                    last_seen_at = completed_at
                else:
                    last_submitted_answer = previous.last_submitted_answer
                    last_submitted_display = previous.last_submitted_display
                    last_seen_at = previous.last_seen_at
                mistakes[key] = LearnerMistakeEntry(
                    plugin=previous.plugin,
                    prompt=previous.prompt,
                    expected_answer=previous.expected_answer,
                    last_submitted_answer=last_submitted_answer,
                    expected_display=previous.expected_display,
                    last_submitted_display=last_submitted_display,
                    answer_type=previous.answer_type,
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
                (
                    saved_session.completed_at or saved_session.created_at
                    for saved_session in completed_sessions
                ),
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
            evaluation = evaluate_answer(
                question.answer_type,
                question.evaluation_payload,
                submitted_answer,
            )
            normalized_answer = _normalized_answer_for_legacy_integer_column(
                evaluation.normalized_answer
            )
            now = self._now()
            if practice_session.show_timer and practice_session.timer_started_at is not None:
                self._settle_timer(practice_session, now)
            attempt = ResponseAttemptEntity(
                question_instance_id=question.id,
                attempt_number=len(question.attempts) + 1,
                submitted_answer=submitted_answer,
                normalized_answer=normalized_answer,
                submitted_payload={"raw": submitted_answer},
                normalized_payload={"value": evaluation.normalized_answer},
                evaluation_detail=evaluation.detail,
                is_correct=evaluation.is_correct,
                submitted_at=now,
            )
            database_session.add(attempt)
            if practice_session.status == "created":
                practice_session.status = "in_progress"
                practice_session.started_at = now
            practice_session.last_answered_at = now
            if practice_session.show_timer:
                practice_session.timer_started_at = now
            if all(
                saved_question.attempts or saved_question.id == question.id
                for saved_question in practice_session.questions
            ):
                practice_session.status = "completed"
                practice_session.completed_at = now
                practice_session.timer_started_at = None
                self._sync_assignment_items_for_completed_session(
                    database_session,
                    practice_session,
                    now,
                )
            database_session.commit()
            return attempt

    def _get_assignment_for_update(self, database_session, assignment_id: int) -> AssignmentEntity:
        assignment = database_session.scalars(
            select(AssignmentEntity)
            .where(AssignmentEntity.id == assignment_id)
            .options(
                selectinload(AssignmentEntity.items).selectinload(
                    AssignmentItemEntity.linked_session
                )
            )
        ).one_or_none()
        if assignment is None:
            raise ValueError(f"Unknown assignment: {assignment_id}")
        return assignment

    def _sync_assignment_items_for_completed_session(
        self,
        database_session,
        practice_session: PracticeSessionEntity,
        now: datetime,
    ) -> None:
        items = list(
            database_session.scalars(
                select(AssignmentItemEntity)
                .where(AssignmentItemEntity.linked_session_id == practice_session.id)
                .options(selectinload(AssignmentItemEntity.assignment).selectinload(AssignmentEntity.items))
            )
        )
        for item in items:
            self._mark_item_completed(database_session, item.assignment, item, now)

    def _mark_item_completed(
        self,
        database_session,
        assignment: AssignmentEntity,
        item: AssignmentItemEntity,
        now: datetime,
    ) -> None:
        item.status = "completed"
        item.completed_at = now
        assignment.updated_at = now
        required_items = [candidate for candidate in assignment.items if candidate.required]
        if required_items and all(candidate.status == "completed" for candidate in required_items):
            assignment.status = "completed"
            assignment.completed_at = now
        elif assignment.status == "assigned":
            assignment.status = "in_progress"
        database_session.add(assignment)

    def _build_practice_session(
        self,
        learner_id: int,
        snapshot: PracticeSessionSnapshot,
    ) -> PracticeSessionEntity:
        return PracticeSessionEntity(
            learner_id=learner_id,
            student_token="pending-token",
            plugin=snapshot.plugin,
            subject=snapshot.subject,
            category=snapshot.category,
            skill=snapshot.skill,
            plugin_settings=(
                asdict(snapshot.plugin_settings)
                if is_dataclass(snapshot.plugin_settings)
                else dict(snapshot.plugin_settings)
            ),
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
                    expected_answer=_expected_answer_for_legacy_integer_column(question),
                    skill_tags=list(question.skill_tags),
                    renderer_type=question.renderer_type,
                    answer_type=question.answer_type,
                    evaluation_payload=dict(question.evaluation_payload),
                    prompt_payload=dict(question.prompt_payload),
                    public_payload=dict(question.public_payload),
                    question_type=question.question_type,
                    choices=list(question.choices),
                    speech_text=question.speech_text,
                    speech_locale=question.speech_locale,
                    audio_url=question.audio_url,
                )
                for position, question in enumerate(snapshot.questions, start=1)
            ],
        )

    @staticmethod
    def _is_complete(practice_session: PracticeSessionEntity) -> bool:
        return bool(practice_session.questions) and all(
            question.attempts for question in practice_session.questions
        )

    @staticmethod
    def _elapsed_seconds(practice_session: PracticeSessionEntity) -> int | None:
        active_elapsed_seconds = getattr(practice_session, "active_elapsed_seconds", 0) or 0
        if active_elapsed_seconds:
            return active_elapsed_seconds
        if practice_session.started_at is None or practice_session.completed_at is None:
            return None
        completed_at = PracticeRepository._normalize_datetime(practice_session.completed_at)
        started_at = PracticeRepository._normalize_datetime(practice_session.started_at)
        return max(
            0,
            int((completed_at - started_at).total_seconds()),
        )

    @staticmethod
    def _timer_status(practice_session: PracticeSessionEntity) -> str:
        if practice_session.timer_started_at is not None:
            return "running"
        return "paused"

    def _get_session_for_timer_update(self, database_session, token: str) -> PracticeSessionEntity:
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
        return practice_session

    def _settle_stale_timer(self, practice_session: PracticeSessionEntity) -> None:
        if practice_session.timer_started_at is None:
            return
        end_at = practice_session.last_answered_at
        timer_started_at = self._normalize_datetime(practice_session.timer_started_at)
        if end_at is None or self._normalize_datetime(end_at) < timer_started_at:
            end_at = practice_session.timer_started_at
        self._settle_timer(practice_session, end_at)

    @staticmethod
    def _settle_timer(practice_session: PracticeSessionEntity, end_at: datetime) -> None:
        if practice_session.timer_started_at is None:
            return
        timer_started_at = PracticeRepository._normalize_datetime(
            practice_session.timer_started_at
        )
        normalized_end_at = PracticeRepository._normalize_datetime(end_at)
        elapsed = max(
            0,
            int((normalized_end_at - timer_started_at).total_seconds()),
        )
        practice_session.active_elapsed_seconds = (
            (practice_session.active_elapsed_seconds or 0) + elapsed
        )
        practice_session.timer_started_at = None

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None)

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


def _expected_answer_for_legacy_integer_column(question) -> int | None:
    # Compatibility value for the legacy integer column.
    # Generic answer data is stored in evaluation_payload.
    return value_for_legacy_integer_column(expected_answer_value_for_question(question))


def _normalized_answer_for_legacy_integer_column(normalized_answer: AnswerValue) -> int | None:
    # Compatibility value for the legacy integer column.
    # Generic answer data is stored in normalized_payload/evaluation_detail.
    return value_for_legacy_integer_column(normalized_answer)


def _expected_answer_display(question) -> str | None:
    return answer_display(
        expected_answer_value_for_question(question),
        choices=tuple(getattr(question, "choices", ()) or ()),
        answer_type=getattr(question, "answer_type", None),
    )
