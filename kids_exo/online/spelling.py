import random

from kids_exo.localization import LocalizedPresentation, LocalizedText
from kids_exo.online.catalog import get_online_plugin
from kids_exo.online.french_vocabulary import (
    FRENCH_FAMILY_WORDS,
    FrenchVocabularyItem,
    french_family_word_audio_url,
)
from kids_exo.online.models import OnlineQuestionSnapshot, PracticeSessionSnapshot
from kids_exo.plugins.french_common_word_spelling.settings import (
    FrenchCommonWordSpellingSettings,
)


FRENCH_ACCENT_KEYS = (
    "é",
    "è",
    "ê",
    "ë",
    "à",
    "â",
    "î",
    "ï",
    "ô",
    "ù",
    "û",
    "ü",
    "ç",
    "œ",
    "æ",
    "-",
    "’",
)


def create_french_common_word_spelling_session(request, settings: FrenchCommonWordSpellingSettings):
    descriptor = get_online_plugin(request.plugin)
    rng = random.Random(request.seed)
    targets = _family_word_targets(request.question_count, rng)
    questions = tuple(
        _spelling_question(settings.strategy, target, position)
        for position, target in enumerate(targets, start=1)
    )
    return PracticeSessionSnapshot(
        plugin=request.plugin,
        subject=descriptor.subject,
        category=descriptor.category,
        skill=descriptor.title,
        plugin_settings=settings,
        requested_locale=request.requested_locale,
        feedback_mode=request.feedback_mode,
        show_timer=request.show_timer,
        seed=request.seed,
        presentation=LocalizedPresentation(
            heading=LocalizedText("French Common Word Spelling", "en-CA", False),
            instructions=(
                LocalizedText(
                    "Spell each French family word from audio, meaning, or both.",
                    "en-CA",
                    False,
                ),
            ),
        ),
        questions=questions,
    )


def _family_word_targets(question_count: int, rng: random.Random) -> list[FrenchVocabularyItem]:
    targets: list[FrenchVocabularyItem] = []
    while len(targets) < question_count:
        shuffled = list(FRENCH_FAMILY_WORDS)
        rng.shuffle(shuffled)
        targets.extend(shuffled)
    return targets[:question_count]


def _spelling_question(
    strategy: str,
    target: FrenchVocabularyItem,
    position: int,
) -> OnlineQuestionSnapshot:
    prompt = _prompt_for_strategy(strategy)
    public_payload = _public_payload_for_strategy(strategy, target)
    return OnlineQuestionSnapshot(
        identifier=f"question-{position}",
        prompt=prompt,
        strategy=strategy,
        skill_tags=("french", "spelling", "common_words", strategy),
        renderer_type="spelling_answer",
        answer_type="spelling_text",
        evaluation_payload={
            "expected_text": target.text,
            "accepted_answers": (target.text, *target.accepted_spellings),
            "case_sensitive": target.is_proper_noun,
            "accent_sensitive": True,
            "hyphen_sensitive": True,
            "normalize_apostrophe": True,
        },
        prompt_payload=dict(public_payload),
        public_payload=public_payload,
        question_type="spelling",
        speech_text=target.text if strategy in {"dictation", "combined"} else None,
        speech_locale=target.language if strategy in {"dictation", "combined"} else None,
        audio_url=public_payload.get("audio_url"),
    )


def _prompt_for_strategy(strategy: str) -> str:
    if strategy == "dictation":
        return "Listen and spell the French word."
    if strategy == "translation":
        return "Spell the French word for the meaning shown."
    return "Spell the French word from the meaning and audio."


def _public_payload_for_strategy(
    strategy: str,
    target: FrenchVocabularyItem,
) -> dict:
    payload = {
        "prompt_mode": strategy,
        "language": target.language,
        "input_label": "French word",
        "accent_keys": list(FRENCH_ACCENT_KEYS),
        "tools": {"scratch_pad": False, "audio": strategy in {"dictation", "combined"}},
    }
    if strategy in {"translation", "combined"}:
        payload["translation"] = target.meaning
        payload["translation_locale"] = "en-CA"
    if strategy in {"dictation", "combined"}:
        payload["audio_url"] = french_family_word_audio_url(target)
        payload["speech_text"] = target.text
        payload["speech_locale"] = target.language
    return payload
