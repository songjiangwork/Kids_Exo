import unittest

from kids_exo.online.catalog import get_online_catalog, get_online_plugin
from kids_exo.online.session import OnlineSessionRequest, create_practice_session


class OnlinePluginCatalogTests(unittest.TestCase):
    def test_catalog_exposes_mvp_session_options_and_first_plugin(self) -> None:
        catalog = get_online_catalog()

        self.assertEqual(catalog.default_locale, "en-CA")
        self.assertEqual(catalog.question_counts, (10, 20, 30))
        self.assertEqual(catalog.feedback_modes, ("immediate", "deferred"))
        self.assertTrue(catalog.show_timer_configurable)
        self.assertEqual(
            tuple(plugin.plugin for plugin in catalog.plugins),
            ("multiply_by_11",),
        )

    def test_multiply_by_11_schema_exposes_only_parent_configurable_settings(self) -> None:
        plugin = get_online_plugin("multiply_by_11")

        self.assertEqual(plugin.title, "Multiply by 11")
        self.assertEqual(plugin.default_locale, "en-CA")
        self.assertEqual(
            {coverage.locale for coverage in plugin.locale_coverage},
            {"en-CA", "zh-CN"},
        )
        self.assertEqual(
            tuple(setting.name for setting in plugin.settings),
            ("multiplicand_digits", "strategies"),
        )
        digits = plugin.settings[0]
        self.assertEqual(digits.control, "single_choice")
        self.assertEqual(tuple(option.value for option in digits.options), (2, 3))
        self.assertEqual(digits.default, (2,))

    def test_session_accepts_public_settings_and_applies_safe_internal_defaults(self) -> None:
        session = create_practice_session(
            OnlineSessionRequest(
                plugin="multiply_by_11",
                plugin_settings={
                    "multiplicand_digits": [3],
                    "strategies": ["with_carrying"],
                },
                question_count=10,
                seed=88,
            )
        )

        self.assertEqual(session.plugin_settings.multiplicand_digits, (3,))
        self.assertFalse(session.plugin_settings.allow_duplicates)
        self.assertEqual(
            session.plugin_settings.strategy_weights,
            {"with_carrying": 1.0},
        )
        self.assertTrue(all(question.strategy == "with_carrying" for question in session.questions))

    def test_session_rejects_internal_plugin_settings_from_a_web_request(self) -> None:
        with self.assertRaisesRegex(ValueError, "not configurable online"):
            create_practice_session(
                OnlineSessionRequest(
                    plugin="multiply_by_11",
                    plugin_settings={
                        "multiplicand_digits": [2],
                        "strategies": ["no_carrying"],
                        "allow_duplicates": True,
                    },
                    question_count=10,
                )
            )


if __name__ == "__main__":
    unittest.main()
