from dataclasses import asdict
import unittest

from kids_exo.online.session import OnlineSessionRequest, create_practice_session


class OnlinePracticeSessionTests(unittest.TestCase):
    def _request(self, **overrides) -> OnlineSessionRequest:
        values = {
            "plugin": "multiply_by_11",
            "plugin_settings": {
                "multiplicand_digits": [2],
                "strategies": ["no_carrying", "with_carrying"],
            },
            "question_count": 10,
            "requested_locale": "en-CA",
            "feedback_mode": "immediate",
            "show_timer": True,
            "seed": 1122,
        }
        values.update(overrides)
        return OnlineSessionRequest(**values)

    def test_session_snapshot_is_reproducible_from_plugin_settings_and_seed(self) -> None:
        first = create_practice_session(self._request())
        second = create_practice_session(self._request())

        self.assertEqual(first.plugin, "multiply_by_11")
        self.assertEqual(first.seed, 1122)
        self.assertEqual(first.questions, second.questions)
        self.assertEqual(len(first.questions), 10)
        self.assertEqual(
            {question.strategy for question in first.questions},
            {"no_carrying", "with_carrying"},
        )

    def test_student_question_views_do_not_expose_standard_answers(self) -> None:
        session = create_practice_session(self._request())

        student_views = session.student_questions()

        self.assertEqual(len(student_views), 10)
        self.assertEqual(student_views[0].position, 1)
        self.assertEqual(student_views[0].total_questions, 10)
        self.assertIn("= __________", student_views[0].prompt)
        self.assertNotIn("expected_answer", asdict(student_views[0]))

    def test_session_evaluates_an_integer_submission_server_side(self) -> None:
        session = create_practice_session(self._request())
        question = session.questions[0]

        correct = session.evaluate_answer(question.identifier, str(question.expected_answer))
        wrong = session.evaluate_answer(question.identifier, str(question.expected_answer + 1))

        self.assertTrue(correct.is_correct)
        self.assertFalse(wrong.is_correct)
        self.assertEqual(correct.normalized_answer, question.expected_answer)

    def test_session_snapshot_records_localization_fallbacks(self) -> None:
        session = create_practice_session(self._request(requested_locale="zh-CN"))

        self.assertEqual(session.requested_locale, "zh-CN")
        self.assertEqual(session.presentation.heading.locale, "en-CA")
        self.assertEqual(
            session.localization_fallback_keys,
            ("heading", "instruction_1"),
        )

    def test_mvp_accepts_only_configured_fixed_question_counts(self) -> None:
        with self.assertRaisesRegex(ValueError, "10, 20, or 30"):
            create_practice_session(self._request(question_count=12))


if __name__ == "__main__":
    unittest.main()
