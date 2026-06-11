import unittest

from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

from kids_exo.auth.passwords import hash_password
from kids_exo.localization import LocalizedPresentation, LocalizedText
from kids_exo.online.models import OnlineQuestionSnapshot, PracticeSessionSnapshot
from kids_exo.persistence.database import build_engine, build_session_factory
from kids_exo.persistence.models import AccountEntity, Base, HouseholdEntity, HouseholdMemberEntity
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.auth import LocalSessionStore, require_parent_account
from kids_exo.web.app import create_app
from kids_exo.web.mappers import practice_results_response


class PracticeWebApiTests(unittest.TestCase):
    def setUp(self) -> None:
        engine = build_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        self.repository = PracticeRepository(build_session_factory(engine))
        self.app = create_app(self.repository)
        self.client = TestClient(self.app)
        self.session_factory = build_session_factory(engine)
        self.parent_account = self.repository.create_parent_account(
            email="parent@example.com",
            display_name="Parent",
            password="secret password",
            household_name="Song Family",
        )
        self.client.post(
            "/api/auth/login",
            json={"email": "parent@example.com", "password": "secret password"},
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

    def test_catalog_endpoint_returns_ui_driven_plugin_schema(self) -> None:
        response = self.client.get("/api/practice-plugins")

        self.assertEqual(response.status_code, 200)
        catalog = response.json()
        self.assertEqual(catalog["question_counts"], [10, 20, 30, 40, 50, 100])
        self.assertEqual(catalog["feedback_modes"], ["immediate", "deferred"])
        self.assertEqual(
            [plugin["plugin"] for plugin in catalog["plugins"]],
            [
                "multiply_by_11",
                "integer_multiplication_distributive",
                "same_tens_ones_sum_to_ten",
                "square_ending_in_5",
                "multiply_by_9_99_999",
                "multiply_by_5_25_125",
                "three_digit_same_prefix_ones_sum_to_ten",
                "tens_sum_to_ten_same_ones",
                "near_round_pair_multiplication",
                "difference_of_squares",
                "french_alphabet_sounds",
                "french_common_word_sounds",
            ],
        )
        plugin = catalog["plugins"][0]
        self.assertEqual(plugin["plugin"], "multiply_by_11")
        self.assertEqual(plugin["supported_delivery_modes"], ["web_practice", "pdf_printable"])
        self.assertEqual(plugin["answer_types"], ["integer_exact"])
        self.assertEqual(plugin["release_stage"], "published")
        self.assertEqual(
            [setting["name"] for setting in plugin["settings"]],
            ["multiplicand_digits", "strategies"],
        )
        french_plugin = next(
            item for item in catalog["plugins"] if item["plugin"] == "french_alphabet_sounds"
        )
        self.assertEqual(french_plugin["supported_delivery_modes"], ["web_practice"])
        self.assertEqual(french_plugin["answer_types"], ["multiple_choice_index"])
        self.assertEqual(french_plugin["release_stage"], "published")

    def test_local_auth_login_me_and_logout(self) -> None:
        client = TestClient(self.app)

        anonymous = client.get("/api/auth/me")
        login = client.post(
            "/api/auth/login",
            json={"email": "PARENT@example.com", "password": "secret password"},
        )
        authenticated = client.get("/api/auth/me")
        logout = client.post("/api/auth/logout")
        after_logout = client.get("/api/auth/me")

        self.assertEqual(anonymous.status_code, 200)
        self.assertIsNone(anonymous.json()["account"])
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.json()["account"]["id"], self.parent_account.id)
        self.assertEqual(login.json()["account"]["email"], "parent@example.com")
        self.assertIn("kids_exo_session", login.cookies)
        self.assertEqual(authenticated.json()["account"]["id"], self.parent_account.id)
        self.assertEqual(logout.status_code, 200)
        self.assertIsNone(logout.json()["account"])
        self.assertIsNone(after_logout.json()["account"])

    def test_local_auth_rejects_bad_credentials(self) -> None:
        response = TestClient(self.app).post(
            "/api/auth/login",
            json={"email": "parent@example.com", "password": "wrong password"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid email or password")

    def test_parent_facing_apis_require_login(self) -> None:
        anonymous = TestClient(self.app)

        protected_requests = [
            anonymous.get("/api/learners"),
            anonymous.post("/api/learners", json={"nickname": "Alex"}),
            anonymous.get("/api/printable-worksheets"),
            anonymous.post(
                "/api/practice-sessions/preview",
                json={
                    "plugin": "multiply_by_11",
                    "plugin_settings": {"multiplicand_digits": [2], "strategies": ["no_carrying"]},
                    "question_count": 10,
                    "feedback_mode": "immediate",
                    "show_timer": True,
                },
            ),
        ]

        self.assertTrue(all(response.status_code == 401 for response in protected_requests))

    def test_parent_only_sees_their_own_household_learners(self) -> None:
        first_parent_learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()
        self.repository.create_parent_account(
            email="second@example.com",
            display_name="Second Parent",
            password="secret password",
            household_name="Second Family",
        )
        second_client = TestClient(self.app)
        second_client.post(
            "/api/auth/login",
            json={"email": "second@example.com", "password": "secret password"},
        )

        second_parent_list_before = second_client.get("/api/learners")
        second_parent_learner = second_client.post("/api/learners", json={"nickname": "Bailey"}).json()
        first_parent_list = self.client.get("/api/learners")
        second_parent_list_after = second_client.get("/api/learners")

        self.assertEqual(second_parent_list_before.json(), [])
        self.assertEqual([learner["nickname"] for learner in first_parent_list.json()], ["Alex"])
        self.assertEqual([learner["nickname"] for learner in second_parent_list_after.json()], ["Bailey"])
        self.assertEqual(second_client.get(f"/api/learners/{first_parent_learner['id']}").status_code, 404)
        self.assertEqual(self.client.get(f"/api/learners/{second_parent_learner['id']}").status_code, 404)

    def test_parent_cannot_access_other_household_sessions_or_assignments(self) -> None:
        first_parent_learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()
        second_client = TestClient(self.app)
        self.repository.create_parent_account(
            email="second@example.com",
            display_name="Second Parent",
            password="secret password",
            household_name="Second Family",
        )
        second_client.post(
            "/api/auth/login",
            json={"email": "second@example.com", "password": "secret password"},
        )

        session = self.client.post(
            f"/api/learners/{first_parent_learner['id']}/sessions",
            json={
                "plugin": "multiply_by_11",
                "plugin_settings": {"multiplicand_digits": [2], "strategies": ["no_carrying"]},
                "question_count": 10,
                "feedback_mode": "immediate",
                "show_timer": True,
            },
        ).json()
        assignment = self.client.post(
            f"/api/learners/{first_parent_learner['id']}/assignments",
            json={
                "title": "Private homework",
                "items": [
                    {
                        "plugin": "multiply_by_11",
                        "plugin_settings": {"multiplicand_digits": [2], "strategies": ["no_carrying"]},
                        "question_count": 10,
                        "feedback_mode": "immediate",
                        "show_timer": True,
                    }
                ],
            },
        ).json()

        self.assertEqual(
            second_client.post(
                f"/api/learners/{first_parent_learner['id']}/sessions",
                json={
                    "plugin": "multiply_by_11",
                    "plugin_settings": {"multiplicand_digits": [2], "strategies": ["no_carrying"]},
                    "question_count": 10,
                    "feedback_mode": "immediate",
                    "show_timer": True,
                },
            ).status_code,
            422,
        )
        self.assertEqual(second_client.get(f"/api/learners/{first_parent_learner['id']}/sessions").status_code, 404)
        self.assertEqual(
            second_client.get(
                f"/api/learners/{first_parent_learner['id']}/sessions/{session['id']}/results"
            ).status_code,
            404,
        )
        self.assertEqual(
            second_client.get(f"/api/learners/{first_parent_learner['id']}/assignments").status_code,
            404,
        )
        self.assertEqual(
            second_client.post(
                f"/api/assignments/{assignment['id']}/items/{assignment['items'][0]['id']}/start"
            ).status_code,
            404,
        )
        self.assertEqual(
            second_client.post(f"/api/assignments/{assignment['id']}/archive").status_code,
            404,
        )
        self.assertEqual(
            second_client.get(f"/api/student/sessions/{session['student_token']}").status_code,
            200,
        )

    def test_parent_auth_dependency_requires_parent_membership(self) -> None:
        session_store = LocalSessionStore()
        app = create_app(self.repository)

        @app.get("/api/test-parent-only")
        def parent_only(_account=Depends(require_parent_account(self.repository, session_store))):
            return {"ok": True}

        child = self._create_child_account()

        anonymous = TestClient(app)
        parent_client = TestClient(app)
        child_client = TestClient(app)
        parent_client.cookies.set("kids_exo_session", session_store.create_session(self.parent_account.id))
        child_client.cookies.set("kids_exo_session", session_store.create_session(child.id))

        self.assertEqual(anonymous.get("/api/test-parent-only").status_code, 401)
        self.assertEqual(parent_client.get("/api/test-parent-only").status_code, 200)
        child_response = child_client.get("/api/test-parent-only")
        self.assertEqual(child_response.status_code, 403)
        self.assertEqual(child_response.json()["detail"], "Parent account required")

    def _create_child_account(self) -> AccountEntity:
        with self.session_factory() as database_session:
            parent = AccountEntity(
                email="child@example.com",
                display_name="Child",
                password_hash=hash_password("secret password"),
                active=True,
            )
            database_session.add(parent)
            database_session.flush()
            household = HouseholdEntity(name="Child Household", owner_account_id=parent.id)
            database_session.add(household)
            database_session.flush()
            database_session.add(
                HouseholdMemberEntity(
                    household_id=household.id,
                    account_id=parent.id,
                    role="child",
                )
            )
            database_session.commit()
            return parent

    def test_printable_catalog_exposes_all_existing_pdf_presets(self) -> None:
        response = self.client.get("/api/printable-worksheets")

        self.assertEqual(response.status_code, 200)
        entries = response.json()
        self.assertGreaterEqual(len(entries), 13)
        self.assertIn(
            "math.mental_multiplication.mixed_practice_100",
            [entry["identifier"] for entry in entries],
        )
        self.assertIn(
            "Squares Ending in 5",
            [entry["title"] for entry in entries],
        )

    def test_parent_can_download_a_pdf_from_a_printable_preset(self) -> None:
        response = self.client.post(
            "/api/printable-worksheets/pdf",
            json={
                "preset_id": "math.mental_multiplication.square_ending_in_5.beginner",
                "seed": 525,
                "include_warmup": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertIn(
            "squares-ending-in-5-seed-525.pdf",
            response.headers["content-disposition"],
        )
        self.assertTrue(response.content.startswith(b"%PDF-1.4"))

    def test_parent_can_download_a_pdf_without_the_warmup_section(self) -> None:
        response = self.client.post(
            "/api/printable-worksheets/pdf",
            json={
                "preset_id": "math.mental_multiplication.square_ending_in_5.beginner",
                "seed": 525,
                "include_warmup": False,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"A. Warm-up", response.content)
        self.assertNotIn(b"B. Practice", response.content)
        self.assertIn(b"Practice", response.content)
        self.assertIn(b"44.", response.content)

    def test_parent_can_choose_two_page_printable_length_with_warmup(self) -> None:
        response = self.client.post(
            "/api/printable-worksheets/pdf",
            json={
                "preset_id": "math.mental_multiplication.square_ending_in_5.beginner",
                "seed": 525,
                "include_warmup": True,
                "page_count": 2,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"/Count 2", response.content)
        self.assertIn(b"76.", response.content)

    def test_parent_can_choose_two_page_printable_length_without_warmup(self) -> None:
        response = self.client.post(
            "/api/printable-worksheets/pdf",
            json={
                "preset_id": "math.mental_multiplication.square_ending_in_5.beginner",
                "seed": 525,
                "include_warmup": False,
                "page_count": 2,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"/Count 2", response.content)
        self.assertIn(b"90.", response.content)

    def test_parent_can_choose_a_custom_printable_question_count(self) -> None:
        response = self.client.post(
            "/api/printable-worksheets/pdf",
            json={
                "preset_id": "math.mental_multiplication.square_ending_in_5.beginner",
                "seed": 525,
                "include_warmup": False,
                "question_count": 12,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"12.", response.content)
        self.assertNotIn(b"13.", response.content)

    def test_pdf_download_rejects_an_unknown_preset(self) -> None:
        response = self.client.post(
            "/api/printable-worksheets/pdf",
            json={"preset_id": "math.unknown"},
        )

        self.assertEqual(response.status_code, 404)

    def test_parent_can_create_a_session_for_an_added_online_plugin(self) -> None:
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()

        response = self.client.post(
            f"/api/learners/{learner['id']}/sessions",
            json={
                "plugin": "square_ending_in_5",
                "plugin_settings": {"strategies": ["ending_in_5_square"]},
                "question_count": 10,
                "seed": 15,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["plugin"], "square_ending_in_5")
        self.assertEqual(response.json()["subject"], "Math")
        self.assertEqual(response.json()["category"], "Mental Multiplication")
        self.assertEqual(response.json()["skill"], "Squares Ending in 5")
        self.assertIn(" x ", response.json()["questions"][0]["prompt"])
        self.assertRegex(
            response.json()["student_token"],
            rf"^s{response.json()['id']}-[23456789abcdefghjkmnpqrstvwxyz]{{8}}$",
        )

    def test_parent_can_view_learner_analytics_and_mistake_notebook(self) -> None:
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()
        session = self.client.post(
            f"/api/learners/{learner['id']}/sessions",
            json={
                "plugin": "multiply_by_11",
                "plugin_settings": {
                    "multiplicand_digits": [2],
                    "strategies": ["no_carrying"],
                },
                "question_count": 10,
                "seed": 88,
            },
        ).json()

        self.client.get(f"/api/student/sessions/{session['student_token']}")
        first_question = session["questions"][0]
        self.client.post(
            f"/api/student/sessions/{session['student_token']}/questions/{first_question['identifier']}/attempts",
            json={"answer": "0"},
        )
        for question in session["questions"][1:]:
            left_operand, remainder = question["prompt"].split(" x ")
            right_operand = remainder.split(" = ")[0]
            self.client.post(
                f"/api/student/sessions/{session['student_token']}/questions/{question['identifier']}/attempts",
                json={"answer": str(int(left_operand) * int(right_operand))},
            )

        response = self.client.get(f"/api/learners/{learner['id']}/analytics")

        self.assertEqual(response.status_code, 200)
        analytics = response.json()
        self.assertEqual(analytics["total_sessions"], 1)
        self.assertEqual(analytics["completed_sessions"], 1)
        self.assertEqual(analytics["total_questions"], 10)
        self.assertEqual(analytics["correct_answers"], 9)
        self.assertAlmostEqual(analytics["accuracy"], 0.9)
        self.assertEqual(analytics["skill_breakdown"][0]["plugin"], "multiply_by_11")
        self.assertEqual(analytics["skill_breakdown"][0]["title"], "Multiply by 11")
        self.assertEqual(analytics["mistake_notebook"][0]["times_missed"], 1)

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
        self.assertEqual(preview["subject"], "Math")
        self.assertEqual(preview["skill"], "Multiply by 11")
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
        self.assertEqual(student.json()["status"], "in_progress")
        self.assertEqual(student.json()["timer_status"], "running")
        self.assertEqual(student.json()["answered_questions"], 0)
        self.assertEqual(student.json()["correct_answers"], 0)
        self.assertEqual(student.json()["active_elapsed_seconds"], 0)
        self.assertNotIn("expected_answer", student.text)

    def test_french_alphabet_session_exposes_audio_choices_without_answers(self) -> None:
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()
        response = self.client.post(
            f"/api/learners/{learner['id']}/sessions",
            json={
                "plugin": "french_alphabet_sounds",
                "plugin_settings": {"strategies": ["letter_name_to_letter"]},
                "question_count": 10,
                "seed": 23,
            },
        )

        self.assertEqual(response.status_code, 201)
        created = response.json()
        student = self.client.get(
            f"/api/student/sessions/{created['student_token']}"
        )
        first_question = student.json()["questions"][0]

        self.assertEqual(student.status_code, 200)
        self.assertEqual(first_question["question_type"], "multiple_choice")
        self.assertEqual(len(first_question["choices"]), 4)
        self.assertEqual(first_question["speech_locale"], "fr-FR")
        self.assertIsNotNone(first_question["speech_text"])
        self.assertTrue(first_question["audio_url"].endswith(".mp3"))
        self.assertNotIn("expected_answer", student.text)

    def test_french_common_words_session_exposes_word_meaning_choices(self) -> None:
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()
        response = self.client.post(
            f"/api/learners/{learner['id']}/sessions",
            json={
                "plugin": "french_common_word_sounds",
                "plugin_settings": {"strategies": ["family_words"]},
                "question_count": 10,
                "seed": 23,
            },
        )

        self.assertEqual(response.status_code, 201)
        created = response.json()
        self.assertEqual(created["subject"], "French")
        self.assertEqual(created["skill"], "French Common Word Sounds")
        student = self.client.get(
            f"/api/student/sessions/{created['student_token']}"
        )
        first_question = student.json()["questions"][0]

        self.assertEqual(student.status_code, 200)
        self.assertEqual(first_question["question_type"], "multiple_choice")
        self.assertTrue(all("(" in choice and ")" in choice for choice in first_question["choices"]))
        self.assertEqual(first_question["speech_locale"], "fr-FR")
        self.assertIsNotNone(first_question["speech_text"])
        self.assertTrue(
            first_question["audio_url"].startswith(
                "/audio/tts/fr/fr-FR-DeniseNeural/common-words/family/"
            )
        )
        self.assertNotIn("expected_answer", student.text)

    def test_student_session_reports_resume_progress_without_exposing_answers(self) -> None:
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

        for question in created["questions"][:3]:
            left_operand = question["prompt"].split(" x ")[0]
            self.client.post(
                f"/api/student/sessions/{created['student_token']}/questions/{question['identifier']}/attempts",
                json={"answer": str(int(left_operand) * 11)},
            )

        student = self.client.get(
            f"/api/student/sessions/{created['student_token']}"
        )

        self.assertEqual(student.status_code, 200)
        self.assertEqual(student.json()["status"], "in_progress")
        self.assertEqual(student.json()["answered_questions"], 3)
        self.assertEqual(student.json()["correct_answers"], 3)
        self.assertNotIn("expected_answer", student.text)

    def test_student_can_pause_and_resume_visible_timer(self) -> None:
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()
        created = self.client.post(
            f"/api/learners/{learner['id']}/sessions",
            json={
                "plugin": "multiply_by_11",
                "plugin_settings": {"multiplicand_digits": [2]},
                "question_count": 10,
                "show_timer": True,
                "seed": 23,
            },
        ).json()

        opened = self.client.get(f"/api/student/sessions/{created['student_token']}")
        paused = self.client.post(
            f"/api/student/sessions/{created['student_token']}/timer/pause"
        )
        resumed = self.client.post(
            f"/api/student/sessions/{created['student_token']}/timer/resume"
        )

        self.assertEqual(opened.json()["timer_status"], "running")
        self.assertEqual(paused.status_code, 200)
        self.assertEqual(paused.json()["timer_status"], "paused")
        self.assertEqual(resumed.status_code, 200)
        self.assertEqual(resumed.json()["timer_status"], "running")

    def test_parent_can_list_learners_and_their_session_history(self) -> None:
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

        learners = self.client.get("/api/learners")
        history = self.client.get(f"/api/learners/{learner['id']}/sessions")

        self.assertEqual(learners.status_code, 200)
        self.assertEqual(learners.json()[0]["nickname"], "Alex")
        self.assertEqual(history.status_code, 200)
        self.assertEqual(history.json()[0]["id"], created["id"])
        self.assertEqual(history.json()[0]["status"], "created")
        self.assertEqual(history.json()[0]["total_questions"], 10)
        self.assertEqual(history.json()[0]["answered_questions"], 0)

    def test_parent_can_update_learner_profile(self) -> None:
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()

        fetched = self.client.get(f"/api/learners/{learner['id']}")
        response = self.client.patch(
            f"/api/learners/{learner['id']}",
            json={"nickname": "Herbert", "active": False},
        )

        self.assertEqual(fetched.status_code, 200)
        self.assertEqual(fetched.json()["nickname"], "Alex")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["nickname"], "Herbert")
        self.assertFalse(response.json()["active"])
        learners = self.client.get("/api/learners").json()
        self.assertEqual(learners[0]["nickname"], "Herbert")

    def test_update_learner_rejects_unknown_learner(self) -> None:
        response = self.client.patch(
            "/api/learners/999",
            json={"nickname": "Nobody", "active": True},
        )

        self.assertEqual(response.status_code, 404)

    def test_parent_can_delete_learner_profile(self) -> None:
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()

        response = self.client.delete(f"/api/learners/{learner['id']}")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get("/api/learners").json(), [])

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

    def test_finished_session_reveals_student_results_and_parent_review(self) -> None:
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()
        created = self.client.post(
            f"/api/learners/{learner['id']}/sessions",
            json={
                "plugin": "multiply_by_11",
                "plugin_settings": {"multiplicand_digits": [2]},
                "question_count": 10,
                "feedback_mode": "deferred",
                "show_timer": True,
                "seed": 23,
            },
        ).json()
        token = created["student_token"]
        self.client.get(f"/api/student/sessions/{token}")

        incomplete = self.client.get(f"/api/student/sessions/{token}/results")
        self.assertEqual(incomplete.status_code, 409)

        for position, question in enumerate(created["questions"]):
            first_number = int(question["prompt"].split(" x ")[0])
            correct_answer = first_number * 11
            submitted_answer = correct_answer if position else 0
            response = self.client.post(
                f"/api/student/sessions/{token}/questions/{question['identifier']}/attempts",
                json={"answer": str(submitted_answer)},
            )
            self.assertEqual(response.status_code, 200)
            self.assertIsNone(response.json()["is_correct"])

        student_results = self.client.get(f"/api/student/sessions/{token}/results")
        parent_results = self.client.get(
            f"/api/learners/{learner['id']}/sessions/{created['id']}/results"
        )
        history = self.client.get(f"/api/learners/{learner['id']}/sessions").json()

        self.assertEqual(student_results.status_code, 200)
        results = student_results.json()
        self.assertEqual(results["status"], "completed")
        self.assertEqual(results["correct_answers"], 9)
        self.assertEqual(results["answered_questions"], 10)
        self.assertEqual(len(results["incorrect_questions"]), 1)
        missed = results["incorrect_questions"][0]
        self.assertEqual(missed["submitted_answer"], 0)
        self.assertEqual(missed["submitted_display"], "0")
        self.assertIn("expected_answer", missed)
        self.assertEqual(missed["expected_display"], str(missed["expected_answer"]))
        self.assertEqual(missed["answer_type"], "integer_exact")
        self.assertIsNotNone(results["elapsed_seconds"])
        self.assertEqual(parent_results.json(), results)
        self.assertEqual(history[0]["status"], "completed")
        self.assertEqual(history[0]["correct_answers"], 9)

    def test_result_review_displays_non_integer_wrong_answers(self) -> None:
        learner = self.repository.create_learner("Alex")
        self.repository.create_practice_session(
            learner.id,
            self._text_answer_snapshot(),
            student_token="text-token",
        )
        session = self.repository.get_session_by_student_token("text-token")
        question = session.questions[0]

        self.repository.submit_answer(
            "text-token",
            question.public_identifier,
            "mama",
        )
        completed = self.repository.get_completed_results_by_student_token("text-token")

        results = practice_results_response(completed)

        self.assertEqual(results.correct_answers, 0)
        self.assertEqual(len(results.incorrect_questions), 1)
        missed = results.incorrect_questions[0]
        self.assertEqual(missed.prompt, "Spell the word for mother in French.")
        self.assertEqual(missed.submitted_answer, "mama")
        self.assertEqual(missed.expected_answer, "maman")
        self.assertEqual(missed.submitted_display, "mama")
        self.assertEqual(missed.expected_display, "maman")
        self.assertEqual(missed.answer_type, "text_case_insensitive")

    def test_parent_can_create_list_start_and_complete_assignment(self) -> None:
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()
        create_response = self.client.post(
            f"/api/learners/{learner['id']}/assignments",
            json={
                "title": "Multiply by 11 practice",
                "description": "Finish 10 questions",
                "items": [
                    {
                        "plugin": "multiply_by_11",
                        "plugin_settings": {"multiplicand_digits": [2]},
                        "question_count": 10,
                        "feedback_mode": "immediate",
                        "show_timer": True,
                    }
                ],
            },
        )
        self.assertEqual(create_response.status_code, 201)
        assignment = create_response.json()
        self.assertEqual(assignment["status"], "assigned")
        self.assertEqual(assignment["items"][0]["status"], "assigned")

        listed = self.client.get(f"/api/learners/{learner['id']}/assignments")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json()), 1)

        item_id = assignment["items"][0]["id"]
        start_response = self.client.post(
            f"/api/assignments/{assignment['id']}/items/{item_id}/start"
        )
        self.assertEqual(start_response.status_code, 200)
        started = start_response.json()
        self.assertEqual(started["assignment"]["status"], "in_progress")
        self.assertEqual(started["item"]["status"], "in_progress")
        self.assertTrue(started["student_url"].startswith("/s/s"))

        student = self.client.get(f"/api/student/sessions/{started['student_token']}").json()
        for question in student["questions"]:
            left_operand, remainder = question["prompt"].split(" x ")
            right_operand = remainder.split(" = ")[0]
            self.client.post(
                f"/api/student/sessions/{started['student_token']}/questions/{question['identifier']}/attempts",
                json={"answer": str(int(left_operand) * int(right_operand))},
            )

        completed = self.client.get(f"/api/learners/{learner['id']}/assignments?status=completed")
        self.assertEqual(completed.status_code, 200)
        self.assertEqual(len(completed.json()), 1)
        self.assertEqual(completed.json()[0]["status"], "completed")
        self.assertEqual(completed.json()[0]["items"][0]["status"], "completed")

    def test_assignment_archive_is_hidden_unless_requested(self) -> None:
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()
        assignment = self.client.post(
            f"/api/learners/{learner['id']}/assignments",
            json={
                "title": "Archive me",
                "items": [{"plugin": "multiply_by_11", "question_count": 10}],
            },
        ).json()
        archive = self.client.post(f"/api/assignments/{assignment['id']}/archive")
        self.assertEqual(archive.status_code, 200)
        self.assertEqual(archive.json()["status"], "archived")
        self.assertEqual(self.client.get(f"/api/learners/{learner['id']}/assignments").json(), [])
        archived = self.client.get(f"/api/learners/{learner['id']}/assignments?status=archived")
        self.assertEqual(len(archived.json()), 1)

    def test_assignment_rejects_invalid_learner_and_plugin_settings(self) -> None:
        missing = self.client.post(
            "/api/learners/999/assignments",
            json={
                "title": "Missing learner",
                "items": [{"plugin": "multiply_by_11", "question_count": 10}],
            },
        )
        self.assertEqual(missing.status_code, 404)
        learner = self.client.post("/api/learners", json={"nickname": "Alex"}).json()
        invalid = self.client.post(
            f"/api/learners/{learner['id']}/assignments",
            json={
                "title": "Invalid settings",
                "items": [
                    {
                        "plugin": "multiply_by_11",
                        "plugin_settings": {"allow_duplicates": True},
                        "question_count": 10,
                    }
                ],
            },
        )
        self.assertEqual(invalid.status_code, 422)
        self.assertIn("not configurable online", invalid.json()["detail"])


if __name__ == "__main__":
    unittest.main()
