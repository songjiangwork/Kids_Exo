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
        self.assertEqual(first.subject, "Math")
        self.assertEqual(first.category, "Mental Multiplication")
        self.assertEqual(first.skill, "Multiply by 11")
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
        self.assertEqual(student_views[0].renderer_type, "numeric_answer")
        self.assertEqual(student_views[0].prompt_payload, {"display_text": student_views[0].prompt})
        self.assertEqual(
            student_views[0].public_payload,
            {"tools": {"scratch_pad": True, "audio": False}},
        )
        student_view_payload = asdict(student_views[0])
        self.assertNotIn("expected_answer", student_view_payload)
        self.assertNotIn("answer_type", student_view_payload)
        self.assertNotIn("evaluation_payload", student_view_payload)

    def test_session_evaluates_an_integer_submission_server_side(self) -> None:
        session = create_practice_session(self._request())
        question = session.questions[0]

        self.assertEqual(question.renderer_type, "numeric_answer")
        self.assertEqual(question.answer_type, "integer_exact")
        self.assertEqual(
            question.evaluation_payload,
            {"expected_value": question.expected_answer},
        )
        self.assertEqual(question.prompt_payload, {"display_text": question.prompt})
        correct = session.evaluate_answer(question.identifier, str(question.expected_answer))
        wrong = session.evaluate_answer(question.identifier, str(question.expected_answer + 1))

        self.assertTrue(correct.is_correct)
        self.assertFalse(wrong.is_correct)
        self.assertEqual(correct.normalized_answer, question.expected_answer)
        self.assertEqual(
            correct.detail,
            {"answer_type": "integer_exact", "expected_value": question.expected_answer},
        )

    def test_session_snapshot_records_localization_fallbacks(self) -> None:
        session = create_practice_session(self._request(requested_locale="zh-CN"))

        self.assertEqual(session.requested_locale, "zh-CN")
        self.assertEqual(session.presentation.heading.locale, "en-CA")
        self.assertEqual(
            session.localization_fallback_keys,
            ("heading", "instruction_1"),
        )

    def test_mvp_accepts_only_configured_fixed_question_counts(self) -> None:
        with self.assertRaisesRegex(ValueError, "10, 20, 30, 40, 50, or 100"):
            create_practice_session(self._request(question_count=12))

    def test_session_accepts_a_hundred_question_practice(self) -> None:
        session = create_practice_session(self._request(question_count=100))

        self.assertEqual(len(session.questions), 100)
        self.assertTrue(session.plugin_settings.allow_duplicates)
        self.assertEqual(session.student_questions()[-1].total_questions, 100)

    def test_each_added_online_plugin_generates_integer_answer_questions(self) -> None:
        requests = (
            OnlineSessionRequest(
                plugin="same_tens_ones_sum_to_ten",
                plugin_settings={"strategies": ["two_digit_ones_product"]},
                question_count=10,
                seed=12,
            ),
            OnlineSessionRequest(
                plugin="square_ending_in_5",
                plugin_settings={"strategies": ["ending_in_5_square"]},
                question_count=10,
                seed=12,
            ),
            OnlineSessionRequest(
                plugin="multiply_by_9_99_999",
                plugin_settings={
                    "multiplicand_digits": [2],
                    "strategies": ["times_9", "times_99", "times_999"],
                },
                question_count=10,
                seed=12,
            ),
        )

        for request in requests:
            with self.subTest(plugin=request.plugin):
                session = create_practice_session(request)
                first = session.questions[0]
                self.assertEqual(len(session.questions), 10)
                self.assertIn("= __________", first.prompt)
                self.assertTrue(
                    session.evaluate_answer(first.identifier, str(first.expected_answer)).is_correct
                )
                self.assertEqual(session.presentation.heading.locale, "en-CA")

    def test_signed_integer_session_generates_addition_and_subtraction_questions(self) -> None:
        first = create_practice_session(
            OnlineSessionRequest(
                plugin="integer_signed_addition_subtraction",
                plugin_settings={
                    "number_range": ["within_20"],
                    "operations": ["addition", "subtraction"],
                },
                question_count=10,
                seed=42,
            )
        )
        second = create_practice_session(
            OnlineSessionRequest(
                plugin="integer_signed_addition_subtraction",
                plugin_settings={
                    "number_range": ["within_20"],
                    "operations": ["addition", "subtraction"],
                },
                question_count=10,
                seed=42,
            )
        )
        question = first.questions[0]

        self.assertEqual(first.plugin, "integer_signed_addition_subtraction")
        self.assertEqual(first.subject, "Math")
        self.assertEqual(first.category, "Integer Arithmetic")
        self.assertEqual(first.skill, "Signed Integer Addition and Subtraction")
        self.assertEqual(first.questions, second.questions)
        self.assertEqual({item.strategy for item in first.questions}, {"addition", "subtraction"})
        self.assertEqual(question.renderer_type, "numeric_answer")
        self.assertEqual(question.answer_type, "signed_integer_exact")
        self.assertEqual(question.evaluation_payload, {"expected_value": question.expected_answer})
        self.assertIn("= __________", question.prompt)
        self.assertTrue(
            first.evaluate_answer(question.identifier, str(question.expected_answer)).is_correct
        )
        self.assertEqual(
            first.student_questions()[0].public_payload,
            {"tools": {"scratch_pad": True, "audio": False}},
        )

    def test_french_alphabet_session_generates_audio_choice_questions(self) -> None:
        session = create_practice_session(
            OnlineSessionRequest(
                plugin="french_alphabet_sounds",
                plugin_settings={"strategies": ["letter_name_to_letter"]},
                question_count=10,
                seed=123,
            )
        )
        first = session.questions[0]
        student_view = session.student_questions()[0]

        self.assertEqual(session.plugin, "french_alphabet_sounds")
        self.assertEqual(session.subject, "French")
        self.assertEqual(session.category, "Pronunciation")
        self.assertEqual(session.skill, "French Alphabet Sounds")
        self.assertEqual({question.strategy for question in session.questions}, {"letter_name_to_letter"})
        self.assertEqual(first.question_type, "multiple_choice")
        self.assertEqual(first.renderer_type, "listening_choice")
        self.assertEqual(first.answer_type, "multiple_choice_index")
        self.assertEqual(first.evaluation_payload, {"expected_index": first.expected_answer})
        self.assertEqual(first.prompt_payload["choices"], list(first.choices))
        self.assertEqual(first.prompt_payload["speech_locale"], "fr-FR")
        self.assertEqual(len(first.choices), 4)
        self.assertEqual(first.speech_locale, "fr-FR")
        self.assertIsNotNone(first.speech_text)
        self.assertEqual(
            first.audio_url,
            f"/audio/tts/fr/fr-FR-DeniseNeural/alphabet/{first.speech_text.lower()}.mp3",
        )
        for question in session.questions:
            similar = [
                "B",
                "C",
                "D",
                "G",
                "P",
                "T",
                "V",
            ]
            if question.speech_text in similar:
                self.assertEqual(
                    len(set(question.choices) & set(similar)),
                    1,
                )
        self.assertTrue(session.evaluate_answer(first.identifier, str(first.expected_answer)).is_correct)
        self.assertEqual(student_view.choices, first.choices)
        self.assertEqual(student_view.speech_text, first.speech_text)
        self.assertEqual(student_view.renderer_type, "listening_choice")
        self.assertEqual(student_view.prompt_payload["choices"], list(first.choices))
        self.assertEqual(
            student_view.public_payload,
            {"tools": {"scratch_pad": False, "audio": True}},
        )

    def test_french_common_words_session_generates_word_meaning_choices(self) -> None:
        session = create_practice_session(
            OnlineSessionRequest(
                plugin="french_common_word_sounds",
                plugin_settings={"strategies": ["family_words"]},
                question_count=10,
                seed=123,
            )
        )
        first = session.questions[0]

        self.assertEqual(session.plugin, "french_common_word_sounds")
        self.assertEqual(session.subject, "French")
        self.assertEqual(session.category, "Pronunciation")
        self.assertEqual(session.skill, "French Common Word Sounds")
        self.assertEqual({question.strategy for question in session.questions}, {"family_words"})
        self.assertEqual(len({question.speech_text for question in session.questions}), 10)
        self.assertEqual(first.question_type, "multiple_choice")
        self.assertTrue(all("(" in choice and ")" in choice for choice in first.choices))
        self.assertEqual(first.speech_locale, "fr-FR")
        self.assertIsNotNone(first.speech_text)
        self.assertTrue(first.audio_url.startswith("/audio/tts/fr/fr-FR-DeniseNeural/common-words/family/"))
        self.assertTrue(first.audio_url.endswith(".mp3"))

    def test_chicken_rabbit_word_problem_session_generates_structured_questions(self) -> None:
        session = create_practice_session(
            OnlineSessionRequest(
                plugin="chicken_rabbit_word_problems",
                plugin_settings={"difficulty": ["intro"]},
                question_count=10,
                seed=77,
            )
        )
        first = session.questions[0]
        student_view = session.student_questions()[0]
        expected_values = first.evaluation_payload["expected_values"]

        self.assertEqual(session.plugin, "chicken_rabbit_word_problems")
        self.assertEqual(session.subject, "Math")
        self.assertEqual(session.category, "Word Problems")
        self.assertEqual(session.skill, "Chicken and Rabbit Word Problems")
        self.assertEqual(first.renderer_type, "word_problem_answer")
        self.assertEqual(first.answer_type, "structured_word_problem")
        self.assertEqual(first.question_type, "word_problem")
        self.assertIn("answer_schema", first.public_payload)
        self.assertIn("work_area", first.public_payload)
        self.assertNotIn("expected_values", first.public_payload)
        self.assertNotIn("answer_type", student_view.public_payload)
        self.assertNotIn("evaluation_payload", student_view.public_payload)
        self.assertEqual(first.evaluation_payload["field_rules"].keys(), expected_values.keys())
        self.assertTrue(
            session.evaluate_answer(
                first.identifier,
                {"values": expected_values, "work": ""},
            ).is_correct
        )


if __name__ == "__main__":
    unittest.main()
