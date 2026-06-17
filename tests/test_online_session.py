from dataclasses import asdict
import unittest

from kids_exo.online.session import OnlineSessionRequest, create_practice_session
from kids_exo.online.french_vocabulary import (
    FRENCH_FRUIT_WORDS,
    FRENCH_SCHOOL_WORDS,
    FRENCH_VEGETABLE_WORDS,
    french_vocabulary_article_hint,
    french_vocabulary_audio_phrase_slug,
    french_vocabulary_display_text,
)


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
        self.assertEqual(session.skill, "French Family Word Sounds")
        self.assertEqual({question.strategy for question in session.questions}, {"family_words"})
        self.assertEqual(len({question.speech_text for question in session.questions}), 10)
        self.assertEqual(first.question_type, "multiple_choice")
        self.assertTrue(all("(" in choice and ")" in choice for choice in first.choices))
        self.assertEqual(first.speech_locale, "fr-FR")
        self.assertIsNotNone(first.speech_text)
        self.assertTrue(first.audio_url.startswith("/audio/tts/fr/fr-FR-DeniseNeural/common-words/family/"))
        self.assertTrue(first.audio_url.endswith(".mp3"))

    def test_french_school_words_session_generates_word_meaning_choices(self) -> None:
        session = create_practice_session(
            OnlineSessionRequest(
                plugin="french_school_word_sounds",
                plugin_settings={"strategies": ["school_words"]},
                question_count=10,
                seed=123,
            )
        )
        first = session.questions[0]

        self.assertEqual(session.plugin, "french_school_word_sounds")
        self.assertEqual(session.subject, "French")
        self.assertEqual(session.category, "Pronunciation")
        self.assertEqual(session.skill, "French School Word Sounds")
        self.assertEqual({question.strategy for question in session.questions}, {"school_words"})
        self.assertEqual(len({question.speech_text for question in session.questions}), 10)
        self.assertEqual(first.question_type, "multiple_choice")
        self.assertTrue(all("(" in choice and ")" in choice for choice in first.choices))
        all_choices = [choice for question in session.questions for choice in question.choices]
        self.assertTrue(any(choice.startswith("une école ") for choice in all_choices))
        self.assertTrue(any(choice.startswith("un livre ") for choice in all_choices))
        self.assertEqual(first.speech_locale, "fr-FR")
        self.assertIsNotNone(first.speech_text)
        self.assertTrue(any(question.speech_text.startswith(("un ", "une ")) for question in session.questions))
        self.assertTrue(first.audio_url.startswith("/audio/tts/fr/fr-FR-DeniseNeural/common-words/school/"))
        self.assertTrue(first.audio_url.endswith(".mp3"))

    def test_french_fruit_words_session_generates_word_meaning_choices(self) -> None:
        session = create_practice_session(
            OnlineSessionRequest(
                plugin="french_fruit_word_sounds",
                plugin_settings={"strategies": ["fruit_words"]},
                question_count=20,
                seed=123,
            )
        )
        first = session.questions[0]

        self.assertEqual(session.plugin, "french_fruit_word_sounds")
        self.assertEqual(session.subject, "French")
        self.assertEqual(session.category, "Pronunciation")
        self.assertEqual(session.skill, "French Fruit Word Sounds")
        self.assertEqual({question.strategy for question in session.questions}, {"fruit_words"})
        self.assertEqual(first.question_type, "multiple_choice")
        all_choices = [choice for question in session.questions for choice in question.choices]
        self.assertTrue(any(choice.startswith("une pomme ") for choice in all_choices))
        self.assertTrue(any(choice.startswith("un citron ") for choice in all_choices))
        self.assertEqual(first.speech_locale, "fr-FR")
        self.assertTrue(any(question.speech_text.startswith(("un ", "une ")) for question in session.questions))
        self.assertTrue(first.audio_url.startswith("/audio/tts/fr/fr-FR-DeniseNeural/common-words/fruit/"))
        self.assertIn("/with-article/", first.audio_url)
        self.assertTrue(first.audio_url.endswith(".mp3"))

    def test_french_vegetable_words_session_generates_word_meaning_choices(self) -> None:
        session = create_practice_session(
            OnlineSessionRequest(
                plugin="french_vegetable_word_sounds",
                plugin_settings={"strategies": ["vegetable_words"]},
                question_count=20,
                seed=123,
            )
        )
        first = session.questions[0]

        self.assertEqual(session.plugin, "french_vegetable_word_sounds")
        self.assertEqual(session.subject, "French")
        self.assertEqual(session.category, "Pronunciation")
        self.assertEqual(session.skill, "French Vegetable Word Sounds")
        self.assertEqual({question.strategy for question in session.questions}, {"vegetable_words"})
        self.assertEqual(first.question_type, "multiple_choice")
        all_choices = [choice for question in session.questions for choice in question.choices]
        self.assertTrue(any(choice.startswith("une carotte ") for choice in all_choices))
        self.assertTrue(any(choice.startswith("de l'ail ") for choice in all_choices))
        self.assertTrue(any(choice.startswith("des épinards ") for choice in all_choices))
        self.assertEqual(first.speech_locale, "fr-FR")
        self.assertTrue(any(question.speech_text.startswith(("un ", "une ", "des ", "de l'")) for question in session.questions))
        self.assertTrue(first.audio_url.startswith("/audio/tts/fr/fr-FR-DeniseNeural/common-words/vegetable/"))
        self.assertIn("/with-article/", first.audio_url)
        self.assertTrue(first.audio_url.endswith(".mp3"))

    def test_french_vocabulary_article_helpers_format_school_words(self) -> None:
        words = {item.text: item for item in FRENCH_SCHOOL_WORDS}

        self.assertEqual(words["école"].gender, "feminine")
        self.assertEqual(words["livre"].gender, "masculine")
        self.assertEqual(words["règle"].learning_article, "une")
        self.assertEqual(words["bureau"].learning_article, "un")
        self.assertEqual(
            french_vocabulary_display_text(words["école"], include_article=True),
            "une école",
        )
        self.assertEqual(
            french_vocabulary_display_text(words["livre"], include_article=True),
            "un livre",
        )
        self.assertEqual(
            french_vocabulary_article_hint(words["école"]),
            {
                "article": "une",
                "gender": "feminine",
                "number": "singular",
                "display_text": "une",
                "full_display_text": "une école",
                "mode": "prefix",
                "teaches_gender": True,
            },
        )

    def test_french_vocabulary_article_helpers_format_fruit_words(self) -> None:
        words = {item.text: item for item in FRENCH_FRUIT_WORDS}

        self.assertEqual(words["pomme"].gender, "feminine")
        self.assertEqual(words["citron"].gender, "masculine")
        self.assertEqual(words["pastèque"].learning_article, "une")
        self.assertEqual(words["ananas"].learning_article, "un")
        self.assertEqual(
            french_vocabulary_display_text(words["pomme"], include_article=True),
            "une pomme",
        )
        self.assertEqual(
            french_vocabulary_display_text(words["citron"], include_article=True),
            "un citron",
        )

    def test_french_vocabulary_article_helpers_format_vegetable_words(self) -> None:
        words = {item.text: item for item in FRENCH_VEGETABLE_WORDS}

        self.assertEqual(words["carotte"].gender, "feminine")
        self.assertEqual(words["concombre"].gender, "masculine")
        self.assertEqual(words["épinards"].number, "plural")
        self.assertEqual(words["ail"].learning_article, "de l'")
        self.assertEqual(
            french_vocabulary_display_text(words["ail"], include_article=True),
            "de l'ail",
        )
        self.assertEqual(french_vocabulary_audio_phrase_slug(words["ail"]), "de-l-ail")
        self.assertEqual(
            french_vocabulary_display_text(words["pomme de terre"], include_article=True),
            "une pomme de terre",
        )

    def test_french_common_word_spelling_generates_dictation_questions(self) -> None:
        session = create_practice_session(
            OnlineSessionRequest(
                plugin="french_common_word_spelling",
                plugin_settings={"strategy": ["dictation"]},
                question_count=10,
                seed=123,
            )
        )
        first = session.questions[0]

        self.assertEqual(session.subject, "French")
        self.assertEqual(session.category, "Spelling")
        self.assertEqual(session.skill, "French Family Word Spelling")
        self.assertEqual(first.renderer_type, "spelling_answer")
        self.assertEqual(first.answer_type, "spelling_text")
        self.assertEqual(first.public_payload["prompt_mode"], "dictation")
        self.assertIn("audio_url", first.public_payload)
        self.assertNotIn("translation", first.public_payload)
        self.assertNotIn("expected_text", first.public_payload)
        self.assertIsNotNone(first.public_payload["article_hint"])
        self.assertEqual(first.public_payload["article_hint"]["full_display_text"], first.speech_text)
        self.assertEqual(
            first.public_payload["speech_text"],
            first.speech_text,
        )
        self.assertNotEqual(first.evaluation_payload["expected_text"], first.speech_text)
        self.assertTrue(
            session.evaluate_answer(
                first.identifier,
                {"text": first.evaluation_payload["expected_text"].upper()},
            ).is_correct
        )

    def test_french_common_word_spelling_generates_translation_questions(self) -> None:
        session = create_practice_session(
            OnlineSessionRequest(
                plugin="french_common_word_spelling",
                plugin_settings={"strategy": ["translation"]},
                question_count=10,
                seed=123,
            )
        )
        first = session.questions[0]

        self.assertEqual(first.public_payload["prompt_mode"], "translation")
        self.assertIn("translation", first.public_payload)
        self.assertNotIn("audio_url", first.public_payload)
        self.assertIsNone(first.audio_url)
        self.assertNotIn("expected_text", first.public_payload)
        self.assertIn("article_hint", first.public_payload)
        self.assertIn("full_display_text", first.public_payload["article_hint"])

    def test_french_school_word_spelling_generates_combined_questions(self) -> None:
        session = create_practice_session(
            OnlineSessionRequest(
                plugin="french_school_word_spelling",
                plugin_settings={"strategy": ["combined"]},
                question_count=10,
                seed=123,
            )
        )
        first = session.questions[0]

        self.assertEqual(session.plugin, "french_school_word_spelling")
        self.assertEqual(session.subject, "French")
        self.assertEqual(session.category, "Spelling")
        self.assertEqual(session.skill, "French School Word Spelling")
        self.assertEqual(first.renderer_type, "spelling_answer")
        self.assertEqual(first.answer_type, "spelling_text")
        self.assertEqual(first.public_payload["prompt_mode"], "combined")
        self.assertIn("translation", first.public_payload)
        self.assertIn("audio_url", first.public_payload)
        self.assertIn("/common-words/school/", first.public_payload["audio_url"])
        self.assertIn("/with-article/", first.public_payload["audio_url"])
        article_question = next(
            question for question in session.questions if question.public_payload["article_hint"]
        )
        self.assertEqual(
            article_question.public_payload["article_hint"]["full_display_text"],
            article_question.speech_text,
        )
        self.assertNotIn("expected_text", first.public_payload)

    def test_french_fruit_word_spelling_generates_combined_questions(self) -> None:
        session = create_practice_session(
            OnlineSessionRequest(
                plugin="french_fruit_word_spelling",
                plugin_settings={"strategy": ["combined"]},
                question_count=10,
                seed=123,
            )
        )
        first = session.questions[0]

        self.assertEqual(session.plugin, "french_fruit_word_spelling")
        self.assertEqual(session.subject, "French")
        self.assertEqual(session.category, "Spelling")
        self.assertEqual(session.skill, "French Fruit Word Spelling")
        self.assertEqual(first.renderer_type, "spelling_answer")
        self.assertEqual(first.answer_type, "spelling_text")
        self.assertEqual(first.public_payload["prompt_mode"], "combined")
        self.assertIn("translation", first.public_payload)
        self.assertIn("audio_url", first.public_payload)
        self.assertIn("/common-words/fruit/", first.public_payload["audio_url"])
        self.assertIn("/with-article/", first.public_payload["audio_url"])
        self.assertIn("article_hint", first.public_payload)
        self.assertNotIn("expected_text", first.public_payload)
        self.assertTrue(
            session.evaluate_answer(
                first.identifier,
                {"text": first.evaluation_payload["expected_text"].upper()},
            ).is_correct
        )

    def test_french_vegetable_word_spelling_generates_combined_questions(self) -> None:
        session = create_practice_session(
            OnlineSessionRequest(
                plugin="french_vegetable_word_spelling",
                plugin_settings={"strategy": ["combined"]},
                question_count=20,
                seed=123,
            )
        )
        first = session.questions[0]

        self.assertEqual(session.plugin, "french_vegetable_word_spelling")
        self.assertEqual(session.subject, "French")
        self.assertEqual(session.category, "Spelling")
        self.assertEqual(session.skill, "French Vegetable Word Spelling")
        self.assertEqual(first.renderer_type, "spelling_answer")
        self.assertEqual(first.answer_type, "spelling_text")
        self.assertEqual(first.public_payload["prompt_mode"], "combined")
        self.assertIn("translation", first.public_payload)
        self.assertIn("audio_url", first.public_payload)
        self.assertIn("/common-words/vegetable/", first.public_payload["audio_url"])
        self.assertIn("/with-article/", first.public_payload["audio_url"])
        self.assertIn("article_hint", first.public_payload)
        self.assertNotIn("expected_text", first.public_payload)
        self.assertTrue(
            session.evaluate_answer(
                first.identifier,
                {"text": first.evaluation_payload["expected_text"].upper()},
            ).is_correct
        )

    def test_french_common_word_spelling_generates_combined_questions(self) -> None:
        session = create_practice_session(
            OnlineSessionRequest(
                plugin="french_common_word_spelling",
                plugin_settings={"strategy": ["combined"]},
                question_count=10,
                seed=123,
            )
        )
        first = session.questions[0]

        self.assertEqual(first.public_payload["prompt_mode"], "combined")
        self.assertIn("translation", first.public_payload)
        self.assertIn("audio_url", first.public_payload)
        self.assertIn("œ", first.public_payload["accent_keys"])
        self.assertIn("’", first.public_payload["accent_keys"])
        self.assertNotIn("expected_text", first.public_payload)

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
        self.assertNotIn(" things ", first.prompt)
        self.assertTrue(
            any(group_label in first.prompt for group_label in ("animals", "vehicles"))
        )
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
