from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime, timedelta, timezone
import unittest

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from kids_exo.localization import LocalizedPresentation, LocalizedText
from kids_exo.online.models import OnlineQuestionSnapshot, PracticeSessionSnapshot
from kids_exo.online.session import OnlineSessionRequest, create_practice_session
from kids_exo.persistence.database import build_engine, build_session_factory
from kids_exo.auth.passwords import verify_password
from kids_exo.persistence.models import (
    AccountEntity,
    Base,
    HouseholdEntity,
    LearnerEntity,
    PracticeSessionEntity,
)
from kids_exo.persistence.repository import PracticeRepository


class PracticeRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = build_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session_factory = build_session_factory(self.engine)
        self.repository = PracticeRepository(self.session_factory)

    def _snapshot(self):
        return create_practice_session(
            OnlineSessionRequest(
                plugin="multiply_by_11",
                plugin_settings={
                    "multiplicand_digits": [2],
                    "strategies": ["no_carrying", "with_carrying"],
                },
                question_count=10,
                requested_locale="zh-CN",
                feedback_mode="immediate",
                show_timer=True,
                seed=1122,
            )
        )

    def _text_answer_snapshot(self) -> PracticeSessionSnapshot:
        return PracticeSessionSnapshot(
            plugin="test_text_plugin",
            subject="English",
            category="Spelling",
            skill="Text answer smoke test",
            plugin_settings={},
            requested_locale="en-CA",
            feedback_mode="immediate",
            show_timer=False,
            seed=None,
            presentation=LocalizedPresentation(
                heading=LocalizedText("Text answer smoke test", "en-CA"),
                instructions=(),
            ),
            questions=(
                OnlineQuestionSnapshot(
                    identifier="question-1",
                    prompt="Spell the word for mother in French.",
                    strategy="text_case_insensitive",
                    skill_tags=("text", "spelling"),
                    renderer_type="text_answer",
                    answer_type="text_case_insensitive",
                    evaluation_payload={"expected_text": "maman"},
                    prompt_payload={"display_text": "Spell the word for mother in French."},
                    public_payload={"tools": {"scratch_pad": False, "audio": False}},
                ),
            ),
        )

    def test_saves_learner_session_and_private_question_answers(self) -> None:
        learner = self.repository.create_learner("Alex")
        saved = self.repository.create_practice_session(
            learner.id,
            self._snapshot(),
            student_token="student-token",
        )

        retrieved = self.repository.get_session_by_student_token("student-token")

        self.assertEqual(saved.learner_id, learner.id)
        self.assertEqual(retrieved.subject, "Math")
        self.assertEqual(retrieved.category, "Mental Multiplication")
        self.assertEqual(retrieved.skill, "Multiply by 11")
        self.assertEqual(retrieved.requested_locale, "zh-CN")
        self.assertEqual(retrieved.localization_fallback_keys, ["heading", "instruction_1"])
        self.assertEqual(len(retrieved.questions), 10)
        self.assertIsInstance(retrieved.questions[0].expected_answer, int)
        self.assertEqual(retrieved.questions[0].renderer_type, "numeric_answer")
        self.assertEqual(retrieved.questions[0].answer_type, "integer_exact")
        self.assertEqual(
            retrieved.questions[0].evaluation_payload,
            {"expected_value": retrieved.questions[0].expected_answer},
        )
        self.assertEqual(
            retrieved.questions[0].prompt_payload,
            {"display_text": retrieved.questions[0].prompt},
        )
        self.assertEqual(
            retrieved.questions[0].public_payload,
            {"tools": {"scratch_pad": True, "audio": False}},
        )

    def test_new_learner_is_assigned_to_default_household(self) -> None:
        learner = self.repository.create_learner("Alex")

        with self.session_factory() as database_session:
            saved = database_session.get(LearnerEntity, learner.id)
            household = database_session.get(HouseholdEntity, saved.household_id)
            household_id = saved.household_id
            household_name = household.name
            household_code = household.household_code
            student_code = saved.student_code
            owner_email = household.owner_account.email
            member_role = household.members[0].role

        self.assertIsNotNone(household_id)
        self.assertEqual(household_name, "Default Household")
        self.assertIsNotNone(household_code)
        self.assertIsNotNone(student_code)
        self.assertEqual(owner_email, "local-parent@example.local")
        self.assertEqual(member_role, "parent")

    def test_creates_parent_account_with_hashed_password_and_household(self) -> None:
        account = self.repository.create_parent_account(
            email=" Parent@Example.COM ",
            display_name="Parent",
            password="correct horse battery staple",
            household_name="Song Family",
        )

        with self.session_factory() as database_session:
            saved_account = database_session.get(AccountEntity, account.id)
            household = database_session.scalar(
                text("SELECT id FROM households WHERE owner_account_id = :account_id"),
                {"account_id": account.id},
            )
            household_code = database_session.scalar(
                text("SELECT household_code FROM households WHERE owner_account_id = :account_id"),
                {"account_id": account.id},
            )
            membership = database_session.scalar(
                text("SELECT role FROM household_members WHERE account_id = :account_id"),
                {"account_id": account.id},
            )

        self.assertEqual(saved_account.email, "parent@example.com")
        self.assertNotEqual(saved_account.password_hash, "correct horse battery staple")
        self.assertTrue(verify_password("correct horse battery staple", saved_account.password_hash))
        self.assertIsNotNone(household)
        self.assertIsNotNone(household_code)
        self.assertEqual(membership, "parent")

    def test_student_code_uniqueness_is_scoped_to_household(self) -> None:
        first_account = self.repository.create_parent_account(
            email="first@example.com",
            display_name="First",
            password="secret password",
            household_name="First Family",
        )
        second_account = self.repository.create_parent_account(
            email="second@example.com",
            display_name="Second",
            password="secret password",
            household_name="Second Family",
        )
        with self.session_factory() as database_session:
            first_household_id = database_session.scalar(
                text("SELECT household_id FROM household_members WHERE account_id = :account_id"),
                {"account_id": first_account.id},
            )
            second_household_id = database_session.scalar(
                text("SELECT household_id FROM household_members WHERE account_id = :account_id"),
                {"account_id": second_account.id},
            )

        first = self.repository.create_learner("Herbert", household_id=first_household_id)
        second = self.repository.create_learner("Herbert", household_id=second_household_id)
        third = self.repository.create_learner("Helen", household_id=first_household_id)

        self.assertEqual(first.student_code, "H")
        self.assertEqual(second.student_code, "H")
        self.assertEqual(third.student_code, "H2")

    def test_direct_student_login_verifies_household_code_student_code_and_pin(self) -> None:
        learner = self.repository.create_learner("Alex")
        with self.session_factory() as database_session:
            household = database_session.get(HouseholdEntity, learner.household_id)

        verified = self.repository.verify_direct_student_login(
            household_code=household.household_code.lower(),
            student_code=learner.student_code.lower(),
            pin="1234",
        )

        self.assertEqual(verified.id, learner.id)

    def test_direct_student_login_uses_generic_errors_and_lockout(self) -> None:
        learner = self.repository.create_learner("Alex")
        with self.session_factory() as database_session:
            household = database_session.get(HouseholdEntity, learner.household_id)

        with self.assertRaisesRegex(ValueError, "Household code, student code, or PIN is incorrect"):
            self.repository.verify_direct_student_login(
                household_code="wrong",
                student_code=learner.student_code,
                pin="1234",
            )
        with self.assertRaisesRegex(ValueError, "Household code, student code, or PIN is incorrect"):
            self.repository.verify_direct_student_login(
                household_code=household.household_code,
                student_code="wrong",
                pin="1234",
            )
        for _ in range(5):
            with self.assertRaisesRegex(ValueError, "Household code, student code, or PIN is incorrect"):
                self.repository.verify_direct_student_login(
                    household_code=household.household_code,
                    student_code=learner.student_code,
                    pin="0000",
                )
        with self.assertRaisesRegex(ValueError, "Too many failed attempts"):
            self.repository.verify_direct_student_login(
                household_code=household.household_code,
                student_code=learner.student_code,
                pin="1234",
            )

    def test_changes_parent_unlock_pin(self) -> None:
        account = self.repository.create_parent_account(
            email="parent@example.com",
            display_name="Parent",
            password="correct horse battery staple",
            household_name="Song Family",
        )
        with self.session_factory() as database_session:
            household_id = database_session.scalar(
                text("SELECT household_id FROM household_members WHERE account_id = :account_id"),
                {"account_id": account.id},
            )

        self.repository.change_parent_unlock_pin(
            account.id,
            household_id,
            current_pin="1234",
            new_pin="5678",
        )

        with self.assertRaisesRegex(ValueError, "Invalid parent PIN"):
            self.repository.verify_parent_unlock_pin(account.id, household_id, "1234")
        self.repository.verify_parent_unlock_pin(account.id, household_id, "5678")

    def test_change_parent_unlock_pin_rejects_invalid_new_pin(self) -> None:
        account = self.repository.create_parent_account(
            email="parent@example.com",
            display_name="Parent",
            password="correct horse battery staple",
            household_name="Song Family",
        )
        with self.session_factory() as database_session:
            household_id = database_session.scalar(
                text("SELECT household_id FROM household_members WHERE account_id = :account_id"),
                {"account_id": account.id},
            )

        with self.assertRaisesRegex(ValueError, "Parent PIN must be 4 to 12 digits"):
            self.repository.change_parent_unlock_pin(
                account.id,
                household_id,
                current_pin="1234",
                new_pin="12ab",
            )

    def test_rejects_duplicate_parent_account_email(self) -> None:
        self.repository.create_parent_account(
            email="parent@example.com",
            display_name="Parent",
            password="secret one",
            household_name="Song Family",
        )

        with self.assertRaisesRegex(ValueError, "already exists"):
            self.repository.create_parent_account(
                email=" PARENT@example.com ",
                display_name="Parent",
                password="secret two",
                household_name="Another Family",
            )

    def test_verifies_parent_account_password(self) -> None:
        created = self.repository.create_parent_account(
            email="parent@example.com",
            display_name="Parent",
            password="secret one",
            household_name="Song Family",
        )

        verified = self.repository.verify_account_password("PARENT@example.com", "secret one")

        self.assertEqual(verified.id, created.id)
        with self.assertRaisesRegex(ValueError, "Invalid account credentials"):
            self.repository.verify_account_password("parent@example.com", "wrong password")

    def test_saves_french_choice_session_evaluation_metadata(self) -> None:
        learner = self.repository.create_learner("Alex")
        snapshot = create_practice_session(
            OnlineSessionRequest(
                plugin="french_alphabet_sounds",
                plugin_settings={"strategies": ["letter_name_to_letter"]},
                question_count=10,
                seed=123,
            )
        )

        self.repository.create_practice_session(
            learner.id,
            snapshot,
            student_token="french-token",
        )
        retrieved = self.repository.get_session_by_student_token("french-token")
        question = retrieved.questions[0]

        self.assertEqual(question.renderer_type, "listening_choice")
        self.assertEqual(question.answer_type, "multiple_choice_index")
        self.assertEqual(question.evaluation_payload, {"expected_index": question.expected_answer})
        self.assertEqual(question.prompt_payload["choices"], list(question.choices))
        self.assertEqual(question.public_payload, {"tools": {"scratch_pad": False, "audio": True}})

    def test_records_an_answer_attempt_against_saved_question(self) -> None:
        learner = self.repository.create_learner("Alex")
        self.repository.create_practice_session(
            learner.id,
            self._snapshot(),
            student_token="student-token",
        )
        session = self.repository.get_session_by_student_token("student-token")
        question = session.questions[0]

        attempt = self.repository.submit_answer(
            "student-token",
            question.public_identifier,
            str(question.expected_answer),
        )

        self.assertTrue(attempt.is_correct)
        self.assertEqual(attempt.normalized_answer, question.expected_answer)
        self.assertEqual(attempt.submitted_payload, {"raw": str(question.expected_answer)})
        self.assertEqual(attempt.normalized_payload, {"value": question.expected_answer})
        self.assertEqual(
            attempt.evaluation_detail,
            {"answer_type": "integer_exact", "expected_value": question.expected_answer},
        )

    def test_records_multiple_choice_attempts_with_generic_evaluation(self) -> None:
        learner = self.repository.create_learner("Alex")
        snapshot = create_practice_session(
            OnlineSessionRequest(
                plugin="french_alphabet_sounds",
                plugin_settings={"strategies": ["letter_name_to_letter"]},
                question_count=10,
                seed=123,
            )
        )
        self.repository.create_practice_session(
            learner.id,
            snapshot,
            student_token="french-token",
        )
        session = self.repository.get_session_by_student_token("french-token")
        question = session.questions[0]

        attempt = self.repository.submit_answer(
            "french-token",
            question.public_identifier,
            str(question.expected_answer),
        )

        self.assertTrue(attempt.is_correct)
        self.assertEqual(attempt.normalized_answer, question.expected_answer)
        self.assertEqual(attempt.submitted_payload, {"raw": str(question.expected_answer)})
        self.assertEqual(attempt.normalized_payload, {"value": question.expected_answer})
        self.assertEqual(
            attempt.evaluation_detail,
            {"answer_type": "multiple_choice_index", "expected_index": question.expected_answer},
        )

    def test_persists_non_integer_answer_in_generic_payload(self) -> None:
        learner = self.repository.create_learner("Alex")
        self.repository.create_practice_session(
            learner.id,
            self._text_answer_snapshot(),
            student_token="text-token",
        )
        session = self.repository.get_session_by_student_token("text-token")
        question = session.questions[0]

        attempt = self.repository.submit_answer(
            "text-token",
            question.public_identifier,
            "MAMAN",
        )

        self.assertTrue(attempt.is_correct)
        self.assertIsNone(question.expected_answer)
        self.assertIsNone(attempt.normalized_answer)
        self.assertEqual(attempt.submitted_payload, {"raw": "MAMAN"})
        self.assertEqual(attempt.normalized_payload, {"value": "MAMAN"})
        self.assertEqual(
            attempt.evaluation_detail,
            {
                "answer_type": "text_case_insensitive",
                "expected_text": "maman",
                "comparison_text": "maman",
            },
        )
        completed = self.repository.get_completed_results_by_student_token("text-token")
        self.assertEqual(completed.status, "completed")

    def test_persists_structured_word_problem_answer_and_work_in_generic_payload(self) -> None:
        learner = self.repository.create_learner("Alex")
        snapshot = create_practice_session(
            OnlineSessionRequest(
                plugin="chicken_rabbit_word_problems",
                plugin_settings={"difficulty": ["intro"]},
                question_count=10,
                seed=77,
            )
        )
        self.repository.create_practice_session(
            learner.id,
            snapshot,
            student_token="word-token",
        )
        session = self.repository.get_session_by_student_token("word-token")
        question = session.questions[0]
        expected_values = question.evaluation_payload["expected_values"]

        attempt = self.repository.submit_answer(
            "word-token",
            question.public_identifier,
            {"values": expected_values, "work": "Assume all are the first type."},
        )

        self.assertTrue(attempt.is_correct)
        self.assertIsNone(attempt.normalized_answer)
        self.assertEqual(
            attempt.submitted_payload,
            {"raw": {"values": expected_values, "work": "Assume all are the first type."}},
        )
        self.assertEqual(
            attempt.normalized_payload,
            {"value": {"values": expected_values, "work": "Assume all are the first type."}},
        )
        self.assertTrue(attempt.evaluation_detail["work_submitted"])

    def test_persists_spelling_answer_in_generic_payload(self) -> None:
        learner = self.repository.create_learner("Alex")
        snapshot = create_practice_session(
            OnlineSessionRequest(
                plugin="french_common_word_spelling",
                plugin_settings={"strategy": ["translation"]},
                question_count=10,
                seed=123,
            )
        )
        self.repository.create_practice_session(
            learner.id,
            snapshot,
            student_token="spelling-token",
        )
        session = self.repository.get_session_by_student_token("spelling-token")
        question = session.questions[0]
        expected_text = question.evaluation_payload["expected_text"]

        attempt = self.repository.submit_answer(
            "spelling-token",
            question.public_identifier,
            {"text": expected_text.upper()},
        )

        self.assertTrue(attempt.is_correct)
        self.assertIsNone(attempt.normalized_answer)
        self.assertEqual(attempt.submitted_payload, {"raw": {"text": expected_text.upper()}})
        self.assertEqual(attempt.normalized_payload, {"value": {"text": expected_text.upper()}})
        self.assertEqual(attempt.evaluation_detail["answer_type"], "spelling_text")

    def test_tracks_active_elapsed_time_and_settles_stale_timer_on_reopen(self) -> None:
        learner = self.repository.create_learner("Alex")
        self.repository.create_practice_session(
            learner.id,
            self._snapshot(),
            student_token="student-token",
        )
        self.repository.start_student_session("student-token")
        session = self.repository.get_session_by_student_token("student-token")
        question = session.questions[0]
        with self.session_factory() as database_session:
            saved = database_session.get(PracticeSessionEntity, session.id)
            saved.timer_started_at = datetime.now(timezone.utc) - timedelta(seconds=12)
            database_session.commit()

        self.repository.submit_answer(
            "student-token",
            question.public_identifier,
            str(question.expected_answer),
        )
        answered = self.repository.get_session_by_student_token("student-token")
        self.assertGreaterEqual(answered.active_elapsed_seconds, 10)
        self.assertIsNotNone(answered.timer_started_at)

        with self.session_factory() as database_session:
            saved = database_session.get(PracticeSessionEntity, session.id)
            saved.timer_started_at = saved.last_answered_at
            database_session.commit()

        reopened = self.repository.start_student_session("student-token")

        self.assertLess(reopened.active_elapsed_seconds, 60)
        self.assertIsNotNone(reopened.timer_started_at)

    def test_can_pause_and_resume_student_timer(self) -> None:
        learner = self.repository.create_learner("Alex")
        self.repository.create_practice_session(
            learner.id,
            self._snapshot(),
            student_token="student-token",
        )
        session = self.repository.start_student_session("student-token")
        with self.session_factory() as database_session:
            saved = database_session.get(PracticeSessionEntity, session.id)
            saved.timer_started_at = datetime.now(timezone.utc) - timedelta(seconds=8)
            database_session.commit()

        paused = self.repository.pause_student_timer("student-token")
        resumed = self.repository.resume_student_timer("student-token")

        self.assertGreaterEqual(paused.active_elapsed_seconds, 6)
        self.assertIsNone(paused.timer_started_at)
        self.assertIsNotNone(resumed.timer_started_at)

    def test_tracks_session_progress_and_lists_learner_history(self) -> None:
        learner = self.repository.create_learner("Alex")
        self.repository.create_practice_session(
            learner.id,
            self._snapshot(),
            student_token="student-token",
        )
        self.repository.start_student_session("student-token")
        session = self.repository.get_session_by_student_token("student-token")

        for question in session.questions:
            self.repository.submit_answer(
                "student-token",
                question.public_identifier,
                str(question.expected_answer),
            )

        history = self.repository.list_sessions_for_learner(learner.id)
        completed = self.repository.get_completed_results_by_student_token("student-token")

        self.assertEqual(self.repository.list_learners()[0].nickname, "Alex")
        self.assertEqual(history[0].status, "completed")
        self.assertIsNotNone(history[0].started_at)
        self.assertIsNotNone(history[0].completed_at)
        self.assertEqual(completed.id, history[0].id)

    def test_updates_learner_profile_and_active_status(self) -> None:
        learner = self.repository.create_learner("Alex")

        updated = self.repository.update_learner(
            learner.id,
            nickname="Herbert",
            active=False,
        )

        self.assertEqual(updated.nickname, "Herbert")
        self.assertFalse(updated.active)
        self.assertEqual(self.repository.list_learners()[0].nickname, "Herbert")

    def test_update_learner_rejects_empty_nickname(self) -> None:
        learner = self.repository.create_learner("Alex")

        with self.assertRaisesRegex(ValueError, "Learner nickname is required"):
            self.repository.update_learner(learner.id, nickname="   ", active=True)

    def test_resets_student_pin_and_clears_failed_login_state(self) -> None:
        learner = self.repository.create_learner("Alex")
        with self.assertRaisesRegex(ValueError, "Invalid student PIN"):
            self.repository.verify_student_pin(
                student_id=learner.id,
                household_id=learner.household_id,
                pin="0000",
            )

        self.repository.reset_student_pin(learner.id, pin="5678")

        with self.assertRaisesRegex(ValueError, "Invalid student PIN"):
            self.repository.verify_student_pin(
                student_id=learner.id,
                household_id=learner.household_id,
                pin="1234",
            )
        verified = self.repository.verify_student_pin(
            student_id=learner.id,
            household_id=learner.household_id,
            pin="5678",
        )
        with self.session_factory() as database_session:
            saved = database_session.get(LearnerEntity, learner.id)
            failed_count = saved.student_login_failed_count
            locked_until = saved.student_login_locked_until

        self.assertEqual(verified.id, learner.id)
        self.assertEqual(failed_count, 0)
        self.assertIsNone(locked_until)

    def test_reset_student_pin_rejects_invalid_pin(self) -> None:
        learner = self.repository.create_learner("Alex")

        with self.assertRaisesRegex(ValueError, "Student PIN must be 4 to 12 digits"):
            self.repository.reset_student_pin(learner.id, pin="12ab")

    def test_deletes_a_learner_profile(self) -> None:
        learner = self.repository.create_learner("Alex")

        self.repository.delete_learner(learner.id)

        self.assertEqual(self.repository.list_learners(), [])
        with self.assertRaisesRegex(ValueError, "Unknown learner"):
            self.repository.delete_learner(learner.id)

    def test_completed_results_remain_available_for_sessions_answered_before_timing_upgrade(self) -> None:
        learner = self.repository.create_learner("Alex")
        self.repository.create_practice_session(
            learner.id,
            self._snapshot(),
            student_token="legacy-student-token",
        )
        session = self.repository.get_session_by_student_token("legacy-student-token")
        for question in session.questions:
            self.repository.submit_answer(
                "legacy-student-token",
                question.public_identifier,
                str(question.expected_answer),
            )
        with self.session_factory() as database_session:
            legacy_session = database_session.get(PracticeSessionEntity, session.id)
            legacy_session.status = "created"
            legacy_session.started_at = None
            legacy_session.completed_at = None
            database_session.commit()

        results = self.repository.get_completed_results_by_student_token("legacy-student-token")

        self.assertEqual(results.id, session.id)

    def test_learner_analytics_supports_completed_legacy_sessions_without_completed_at(self) -> None:
        learner = self.repository.create_learner("Alex")
        self.repository.create_practice_session(
            learner.id,
            self._snapshot(),
            student_token="legacy-student-token",
        )
        session = self.repository.get_session_by_student_token("legacy-student-token")
        for question in session.questions:
            self.repository.submit_answer(
                "legacy-student-token",
                question.public_identifier,
                str(question.expected_answer),
            )
        with self.session_factory() as database_session:
            legacy_session = database_session.get(PracticeSessionEntity, session.id)
            legacy_session.status = "completed"
            legacy_session.completed_at = None
            database_session.commit()

        analytics = self.repository.get_learner_analytics(learner.id)

        self.assertEqual(analytics.total_sessions, 1)
        self.assertEqual(analytics.completed_sessions, 1)
        self.assertIsNotNone(analytics.last_completed_at)

    def test_aggregates_learner_analytics_and_mistake_notebook(self) -> None:
        learner = self.repository.create_learner("Alex")
        self.repository.create_practice_session(
            learner.id,
            self._snapshot(),
            student_token="student-token-1",
        )
        first_session = self.repository.get_session_by_student_token("student-token-1")
        first_question = first_session.questions[0]
        self.repository.submit_answer(
            "student-token-1",
            first_question.public_identifier,
            "0",
        )
        for question in first_session.questions[1:]:
            self.repository.submit_answer(
                "student-token-1",
                question.public_identifier,
                str(question.expected_answer),
            )

        self.repository.create_practice_session(
            learner.id,
            self._snapshot(),
            student_token="student-token-2",
        )
        second_session = self.repository.get_session_by_student_token("student-token-2")
        self.repository.submit_answer(
            "student-token-2",
            second_session.questions[0].public_identifier,
            "1",
        )
        for question in second_session.questions[1:]:
            self.repository.submit_answer(
                "student-token-2",
                question.public_identifier,
                str(question.expected_answer),
            )

        analytics = self.repository.get_learner_analytics(learner.id)

        self.assertEqual(analytics.total_sessions, 2)
        self.assertEqual(analytics.completed_sessions, 2)
        self.assertEqual(analytics.total_questions, 20)
        self.assertEqual(analytics.correct_answers, 18)
        self.assertAlmostEqual(analytics.accuracy, 0.9)
        self.assertEqual(len(analytics.skill_breakdown), 1)
        self.assertEqual(analytics.skill_breakdown[0].plugin, "multiply_by_11")
        self.assertEqual(analytics.skill_breakdown[0].correct_answers, 18)
        self.assertEqual(analytics.skill_breakdown[0].total_questions, 20)
        self.assertEqual(len(analytics.mistake_notebook), 1)
        self.assertEqual(analytics.mistake_notebook[0].times_missed, 2)
        self.assertEqual(analytics.mistake_notebook[0].expected_answer, first_question.expected_answer)

    def test_creates_lists_starts_and_completes_assignment_item(self) -> None:
        learner = self.repository.create_learner("Alex")
        assignment = self.repository.create_assignment(
            learner.id,
            title="Multiply by 11 practice",
            description="Finish 10 questions",
            items=[
                {
                    "plugin": "multiply_by_11",
                    "plugin_settings": {
                        "multiplicand_digits": [2],
                        "strategies": ["no_carrying"],
                    },
                    "question_count": 10,
                    "feedback_mode": "immediate",
                    "show_timer": True,
                    "required": True,
                }
            ],
        )

        listed = self.repository.list_assignments_for_learner(learner.id)
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0].status, "assigned")
        self.assertEqual(listed[0].items[0].status, "assigned")

        started = self.repository.start_assignment_item(
            assignment.id,
            assignment.items[0].id,
            self._snapshot(),
        )

        self.assertEqual(started.assignment.status, "in_progress")
        self.assertEqual(started.item.status, "in_progress")
        self.assertIsNotNone(started.item.linked_session_id)
        self.assertTrue(started.practice_session.student_token.startswith("s"))

        session = self.repository.get_session_by_student_token(started.practice_session.student_token)
        for question in session.questions:
            self.repository.submit_answer(
                session.student_token,
                question.public_identifier,
                str(question.expected_answer),
            )

        completed = self.repository.get_assignment(assignment.id)
        self.assertEqual(completed.status, "completed")
        self.assertIsNotNone(completed.completed_at)
        self.assertEqual(completed.items[0].status, "completed")
        self.assertIsNotNone(completed.items[0].completed_at)

    def test_archived_assignment_is_hidden_from_active_list_unless_requested(self) -> None:
        learner = self.repository.create_learner("Alex")
        assignment = self.repository.create_assignment(
            learner.id,
            title="Archive me",
            items=[{"plugin": "multiply_by_11", "question_count": 10}],
        )

        self.repository.archive_assignment(assignment.id)

        self.assertEqual(self.repository.list_assignments_for_learner(learner.id), [])
        archived = self.repository.list_assignments_for_learner(learner.id, status="archived")
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0].status, "archived")

    def test_assignment_rejects_unknown_learner(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown learner"):
            self.repository.create_assignment(
                999,
                title="Missing learner",
                items=[{"plugin": "multiply_by_11", "question_count": 10}],
            )


class AlembicMigrationTests(unittest.TestCase):
    def test_initial_migration_creates_online_practice_tables(self) -> None:
        with TemporaryDirectory() as directory:
            database_path = Path(directory) / "kids-exo.db"
            config = Config("alembic.ini")
            config.set_main_option(
                "sqlalchemy.url",
                f"sqlite+pysqlite:///{database_path}",
            )

            command.upgrade(config, "head")

            tables = set(inspect(build_engine(f"sqlite+pysqlite:///{database_path}")).get_table_names())
            self.assertTrue(
                {
                    "learners",
                    "accounts",
                    "households",
                    "household_members",
                    "practice_sessions",
                    "question_instances",
                    "response_attempts",
                    "assignments",
                    "assignment_items",
                }
                <= tables
            )
            learner_columns = {
                column["name"]
                for column in inspect(
                    build_engine(f"sqlite+pysqlite:///{database_path}")
                ).get_columns("learners")
            }
            household_columns = {
                column["name"]
                for column in inspect(
                    build_engine(f"sqlite+pysqlite:///{database_path}")
                ).get_columns("households")
            }
            self.assertTrue({"household_code"} <= household_columns)
            self.assertTrue({"household_id", "optional_account_id", "student_code"} <= learner_columns)
            with build_engine(f"sqlite+pysqlite:///{database_path}").connect() as connection:
                self.assertEqual(
                    connection.execute(
                        text("SELECT email FROM accounts WHERE email = 'local-parent@example.local'")
                    ).scalar_one(),
                    "local-parent@example.local",
                )
                self.assertEqual(
                    connection.execute(text("SELECT name FROM households")).scalar_one(),
                    "Default Household",
                )
                self.assertIsNotNone(
                    connection.execute(text("SELECT household_code FROM households")).scalar_one()
                )
            indexes = inspect(build_engine(f"sqlite+pysqlite:///{database_path}")).get_indexes("households")
            unique_constraints = inspect(
                build_engine(f"sqlite+pysqlite:///{database_path}")
            ).get_unique_constraints("households")
            household_code_is_unique = any(
                index.get("unique") and index.get("column_names") == ["household_code"]
                for index in indexes
            ) or any(
                constraint.get("column_names") == ["household_code"]
                for constraint in unique_constraints
            )
            self.assertTrue(household_code_is_unique)
            session_columns = {
                column["name"]
                for column in inspect(
                    build_engine(f"sqlite+pysqlite:///{database_path}")
                ).get_columns("practice_sessions")
            }
            self.assertTrue(
                {
                    "created_at",
                    "started_at",
                    "completed_at",
                    "active_elapsed_seconds",
                    "timer_started_at",
                    "last_answered_at",
                    "subject",
                    "category",
                    "skill",
                }
                <= session_columns
            )
            attempt_column_details = {
                column["name"]: column
                for column in inspect(
                    build_engine(f"sqlite+pysqlite:///{database_path}")
                ).get_columns("response_attempts")
            }
            attempt_columns = set(attempt_column_details)
            self.assertIn("submitted_at", attempt_columns)
            self.assertTrue(attempt_column_details["normalized_answer"]["nullable"])
            question_column_details = {
                column["name"]: column
                for column in inspect(
                    build_engine(f"sqlite+pysqlite:///{database_path}")
                ).get_columns("question_instances")
            }
            question_columns = set(question_column_details)
            self.assertTrue(question_column_details["expected_answer"]["nullable"])
            self.assertTrue(
                {
                    "question_type",
                    "choices",
                    "speech_text",
                    "speech_locale",
                    "audio_url",
                    "renderer_type",
                    "answer_type",
                    "evaluation_payload",
                    "prompt_payload",
                    "public_payload",
                }
                <= question_columns
            )
            self.assertTrue(
                {"submitted_payload", "normalized_payload", "evaluation_detail"}
                <= attempt_columns
            )


if __name__ == "__main__":
    unittest.main()
