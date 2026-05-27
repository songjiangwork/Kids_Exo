import unittest

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

from kids_exo.persistence.database import build_engine, build_session_factory
from kids_exo.persistence.models import Base
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.app import create_app


class PracticeWebApiTests(unittest.TestCase):
    def setUp(self) -> None:
        engine = build_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        self.client = TestClient(
            create_app(PracticeRepository(build_session_factory(engine)))
        )

    def test_catalog_endpoint_returns_ui_driven_plugin_schema(self) -> None:
        response = self.client.get("/api/practice-plugins")

        self.assertEqual(response.status_code, 200)
        catalog = response.json()
        self.assertEqual(catalog["question_counts"], [10, 20, 30])
        self.assertEqual(catalog["feedback_modes"], ["immediate", "deferred"])
        plugin = catalog["plugins"][0]
        self.assertEqual(plugin["plugin"], "multiply_by_11")
        self.assertEqual(
            [setting["name"] for setting in plugin["settings"]],
            ["multiplicand_digits", "strategies"],
        )

    def test_preview_endpoint_returns_student_safe_questions_and_fallback_warning(self) -> None:
        response = self.client.post(
            "/api/practice-sessions/preview",
            json={
                "plugin": "multiply_by_11",
                "plugin_settings": {
                    "multiplicand_digits": [2],
                    "strategies": ["no_carrying", "with_carrying"],
                },
                "question_count": 10,
                "requested_locale": "zh-CN",
                "feedback_mode": "immediate",
                "show_timer": True,
                "seed": 1122,
            },
        )

        self.assertEqual(response.status_code, 200)
        preview = response.json()
        self.assertEqual(preview["requested_locale"], "zh-CN")
        self.assertEqual(preview["localization_fallback_keys"], ["heading", "instruction_1"])
        self.assertEqual(len(preview["questions"]), 10)
        self.assertIn("prompt", preview["questions"][0])
        self.assertNotIn("expected_answer", preview["questions"][0])
        self.assertNotIn("expected_answer", response.text)

    def test_preview_endpoint_rejects_non_public_plugin_settings(self) -> None:
        response = self.client.post(
            "/api/practice-sessions/preview",
            json={
                "plugin": "multiply_by_11",
                "plugin_settings": {
                    "multiplicand_digits": [2],
                    "allow_duplicates": True,
                },
                "question_count": 10,
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("not configurable online", response.json()["detail"])

    def test_saved_session_can_be_opened_by_student_without_exposing_answers(self) -> None:
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()
        response = self.client.post(
            f"/api/learners/{learner['id']}/sessions",
            json={
                "plugin": "multiply_by_11",
                "plugin_settings": {"multiplicand_digits": [2]},
                "question_count": 10,
                "seed": 23,
            },
        )

        self.assertEqual(response.status_code, 201)
        created = response.json()
        student = self.client.get(
            f"/api/student/sessions/{created['student_token']}"
        )
        self.assertEqual(student.status_code, 200)
        self.assertEqual(len(student.json()["questions"]), 10)
        self.assertNotIn("expected_answer", student.text)

    def test_student_can_submit_a_saved_question_answer(self) -> None:
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()
        created = self.client.post(
            f"/api/learners/{learner['id']}/sessions",
            json={
                "plugin": "multiply_by_11",
                "plugin_settings": {"multiplicand_digits": [2]},
                "question_count": 10,
                "seed": 23,
            },
        ).json()
        question = created["questions"][0]
        prompt_numbers = question["prompt"].split(" x ")
        expected = int(prompt_numbers[0]) * 11

        response = self.client.post(
            f"/api/student/sessions/{created['student_token']}/questions/{question['identifier']}/attempts",
            json={"answer": str(expected)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["is_correct"])

    def test_deferred_feedback_does_not_reveal_correctness_on_submission(self) -> None:
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()
        created = self.client.post(
            f"/api/learners/{learner['id']}/sessions",
            json={
                "plugin": "multiply_by_11",
                "plugin_settings": {"multiplicand_digits": [2]},
                "question_count": 10,
                "feedback_mode": "deferred",
                "seed": 23,
            },
        ).json()
        question = created["questions"][0]

        response = self.client.post(
            f"/api/student/sessions/{created['student_token']}/questions/{question['identifier']}/attempts",
            json={"answer": "0"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["is_correct"])

    def test_student_cannot_formally_submit_the_same_question_twice(self) -> None:
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()
        created = self.client.post(
            f"/api/learners/{learner['id']}/sessions",
            json={
                "plugin": "multiply_by_11",
                "plugin_settings": {"multiplicand_digits": [2]},
                "question_count": 10,
                "seed": 23,
            },
        ).json()
        question = created["questions"][0]
        url = (
            f"/api/student/sessions/{created['student_token']}"
            f"/questions/{question['identifier']}/attempts"
        )

        self.client.post(url, json={"answer": "0"})
        repeated = self.client.post(url, json={"answer": "1"})

        self.assertEqual(repeated.status_code, 422)
        self.assertIn("already submitted", repeated.json()["detail"])


if __name__ == "__main__":
    unittest.main()
