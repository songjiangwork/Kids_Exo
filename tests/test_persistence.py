from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime, timedelta, timezone
import unittest

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from kids_exo.online.session import OnlineSessionRequest, create_practice_session
from kids_exo.persistence.database import build_engine, build_session_factory
from kids_exo.persistence.models import Base, PracticeSessionEntity
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
                {"learners", "practice_sessions", "question_instances", "response_attempts"}
                <= tables
            )
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
