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

    def test_signed_integer_exact_accepts_negative_answers(self) -> None:
        result = evaluate_answer(
            "signed_integer_exact",
            {"expected_value": -7},
            " -7 ",
        )

        self.assertTrue(result.is_correct)
        self.assertEqual(result.normalized_answer, -7)
        self.assertEqual(
            result.detail,
            {"answer_type": "signed_integer_exact", "expected_value": -7},
        )

    def test_signed_integer_exact_rejects_non_integer_answers(self) -> None:
        with self.assertRaisesRegex(ValueError, "Submitted answer must be an integer"):
            evaluate_answer("signed_integer_exact", {"expected_value": -7}, "-7.5")

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

    def test_structured_word_problem_accepts_correct_integer_fields_and_work(self) -> None:
        result = evaluate_answer(
            "structured_word_problem",
            {
                "expected_values": {"chicken_count": 12, "rabbit_count": 8},
                "field_rules": {
                    "chicken_count": {"value_type": "integer"},
                    "rabbit_count": {"value_type": "integer"},
                },
            },
            {
                "values": {"chicken_count": "12", "rabbit_count": 8},
                "work": "Assume all are chickens, then adjust by two legs.",
            },
        )

        self.assertTrue(result.is_correct)
        self.assertEqual(
            result.normalized_answer,
            {
                "values": {"chicken_count": 12, "rabbit_count": 8},
                "work": "Assume all are chickens, then adjust by two legs.",
            },
        )
        self.assertEqual(result.detail["answer_type"], "structured_word_problem")
        self.assertTrue(result.detail["field_results"]["chicken_count"]["is_correct"])
        self.assertTrue(result.detail["work_submitted"])

    def test_structured_word_problem_rejects_wrong_integer_fields(self) -> None:
        result = evaluate_answer(
            "structured_word_problem",
            {
                "expected_values": {"chicken_count": 12, "rabbit_count": 8},
                "field_rules": {
                    "chicken_count": {"value_type": "integer"},
                    "rabbit_count": {"value_type": "integer"},
                },
            },
            {"values": {"chicken_count": 10, "rabbit_count": 10}},
        )

        self.assertFalse(result.is_correct)
        self.assertFalse(result.detail["field_results"]["chicken_count"]["is_correct"])
        self.assertFalse(result.detail["work_submitted"])

    def test_structured_word_problem_rejects_missing_required_field(self) -> None:
        with self.assertRaisesRegex(ValueError, "Missing required answer field"):
            evaluate_answer(
                "structured_word_problem",
                {
                    "expected_values": {"chicken_count": 12, "rabbit_count": 8},
                    "field_rules": {
                        "chicken_count": {"value_type": "integer"},
                        "rabbit_count": {"value_type": "integer"},
                    },
                },
                {"values": {"chicken_count": 12}},
            )

    def test_structured_word_problem_records_total_unit_diagnostics(self) -> None:
        result = evaluate_answer(
            "structured_word_problem",
            {
                "expected_values": {"chicken_count": 12, "rabbit_count": 8},
                "field_rules": {
                    "chicken_count": {"value_type": "integer"},
                    "rabbit_count": {"value_type": "integer"},
                },
                "diagnostic_checks": {
                    "total_count": 20,
                    "unit_label": "legs",
                    "total_units": 56,
                    "unit_values": {"chicken_count": 2, "rabbit_count": 4},
                },
            },
            {"values": {"chicken_count": 10, "rabbit_count": 10}},
        )

        self.assertFalse(result.is_correct)
        self.assertEqual(result.detail["feedback_code"], "total_units_mismatch")
        self.assertTrue(result.detail["checks"]["total_count_matches"])
        self.assertFalse(result.detail["checks"]["total_units_matches"])
        self.assertEqual(result.detail["checks"]["submitted_total_count"], 20)
        self.assertEqual(result.detail["checks"]["submitted_total_units"], 60)
        self.assertEqual(result.detail["checks"]["expected_total_units"], 56)
        self.assertEqual(result.detail["checks"]["unit_label"], "legs")

    def test_structured_word_problem_detects_swapped_values(self) -> None:
        result = evaluate_answer(
            "structured_word_problem",
            {
                "expected_values": {"chicken_count": 12, "rabbit_count": 8},
                "field_rules": {
                    "chicken_count": {"value_type": "integer"},
                    "rabbit_count": {"value_type": "integer"},
                },
                "diagnostic_checks": {
                    "total_count": 20,
                    "unit_label": "legs",
                    "total_units": 56,
                    "unit_values": {"chicken_count": 2, "rabbit_count": 4},
                },
            },
            {"values": {"chicken_count": 8, "rabbit_count": 12}},
        )

        self.assertFalse(result.is_correct)
        self.assertTrue(result.detail["checks"]["values_swapped"])
        self.assertEqual(result.detail["feedback_code"], "values_swapped")

    def test_unknown_answer_type_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported answer_type"):
            evaluate_answer("spelling", {"expected_text": "maman"}, "maman")


if __name__ == "__main__":
    unittest.main()
