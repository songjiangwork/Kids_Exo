import unittest

from kids_exo.online.evaluation import evaluate_answer


class OnlineEvaluationTests(unittest.TestCase):
    def test_integer_exact_normalizes_and_compares_answers(self) -> None:
        result = evaluate_answer(
            "integer_exact",
            {"expected_value": 2021},
            " 2021 ",
        )

        self.assertTrue(result.is_correct)
        self.assertEqual(result.normalized_answer, 2021)
        self.assertEqual(
            result.detail,
            {"answer_type": "integer_exact", "expected_value": 2021},
        )

    def test_integer_exact_rejects_non_integer_answers(self) -> None:
        with self.assertRaisesRegex(ValueError, "Submitted answer must be an integer"):
            evaluate_answer("integer_exact", {"expected_value": 2021}, "twenty")

    def test_integer_exact_marks_valid_wrong_answers_incorrect(self) -> None:
        result = evaluate_answer(
            "integer_exact",
            {"expected_value": 2021},
            "2020",
        )

        self.assertFalse(result.is_correct)
        self.assertEqual(result.normalized_answer, 2020)
        self.assertEqual(
            result.detail,
            {"answer_type": "integer_exact", "expected_value": 2021},
        )

    def test_multiple_choice_index_normalizes_and_compares_answers(self) -> None:
        result = evaluate_answer(
            "multiple_choice_index",
            {"expected_index": 3},
            "3",
        )

        self.assertTrue(result.is_correct)
        self.assertEqual(result.normalized_answer, 3)
        self.assertEqual(
            result.detail,
            {"answer_type": "multiple_choice_index", "expected_index": 3},
        )

    def test_multiple_choice_index_marks_valid_wrong_choices_incorrect(self) -> None:
        result = evaluate_answer(
            "multiple_choice_index",
            {"expected_index": 3},
            "2",
        )

        self.assertFalse(result.is_correct)
        self.assertEqual(result.normalized_answer, 2)
        self.assertEqual(
            result.detail,
            {"answer_type": "multiple_choice_index", "expected_index": 3},
        )

    def test_text_exact_accepts_matching_trimmed_text(self) -> None:
        result = evaluate_answer(
            "text_exact",
            {"expected_text": "maman"},
            " maman ",
        )

        self.assertTrue(result.is_correct)
        self.assertEqual(result.normalized_answer, "maman")
        self.assertEqual(
            result.detail,
            {"answer_type": "text_exact", "expected_text": "maman"},
        )

    def test_text_exact_keeps_case_sensitive_comparison(self) -> None:
        result = evaluate_answer(
            "text_exact",
            {"expected_text": "maman"},
            "Maman",
        )

        self.assertFalse(result.is_correct)
        self.assertEqual(result.normalized_answer, "Maman")

    def test_text_case_insensitive_accepts_different_case_and_trims(self) -> None:
        result = evaluate_answer(
            "text_case_insensitive",
            {"expected_text": "maman"},
            " MAMAN ",
        )

        self.assertTrue(result.is_correct)
        self.assertEqual(result.normalized_answer, "MAMAN")
        self.assertEqual(
            result.detail,
            {
                "answer_type": "text_case_insensitive",
                "expected_text": "maman",
                "comparison_text": "maman",
            },
        )

    def test_text_case_insensitive_marks_wrong_text_incorrect(self) -> None:
        result = evaluate_answer(
            "text_case_insensitive",
            {"expected_text": "maman"},
            "mama",
        )

        self.assertFalse(result.is_correct)
        self.assertEqual(result.normalized_answer, "mama")

    def test_unknown_answer_type_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported answer_type"):
            evaluate_answer("spelling", {"expected_text": "maman"}, "maman")


if __name__ == "__main__":
    unittest.main()
