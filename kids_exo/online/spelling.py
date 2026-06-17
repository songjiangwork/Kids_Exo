import random

from kids_exo.localization import LocalizedPresentation, LocalizedText
from kids_exo.online.catalog import get_online_plugin
from kids_exo.online.french_vocabulary import (
    FRENCH_FAMILY_WORDS,
    FRENCH_FRUIT_WORDS,
    FRENCH_MEAT_WORDS,
    FRENCH_SCHOOL_WORDS,
    FRENCH_VEGETABLE_WORDS,
    FrenchVocabularyItem,
    french_family_word_audio_url,
    french_fruit_word_audio_url,
    french_meat_word_audio_url,
    french_school_word_audio_url,
    french_vegetable_word_audio_url,
    french_vocabulary_article_hint,
    french_vocabulary_display_text,
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
    return _create_french_word_spelling_session(
        request,
        settings,
        words=FRENCH_FAMILY_WORDS,
        title="French Family Word Spelling",
        instruction="Spell each French family word from audio, meaning, or both.",
        topic_tag="family_words",
        audio_url_for_word=french_family_word_audio_url,
    )


def create_french_school_word_spelling_session(request, settings: FrenchCommonWordSpellingSettings):
    return _create_french_word_spelling_session(
        request,
        settings,
        words=FRENCH_SCHOOL_WORDS,
        title="French School Word Spelling",
        instruction="Spell each French school word from audio, meaning, or both.",
        topic_tag="school_words",
        audio_url_for_word=french_school_word_audio_url,
    )


def create_french_fruit_word_spelling_session(request, settings: FrenchCommonWordSpellingSettings):
    return _create_french_word_spelling_session(
        request,
        settings,
        words=FRENCH_FRUIT_WORDS,
        title="French Fruit Word Spelling",
        instruction="Spell each French fruit word from audio, meaning, or both.",
        topic_tag="fruit_words",
        audio_url_for_word=french_fruit_word_audio_url,
    )


def create_french_vegetable_word_spelling_session(request, settings: FrenchCommonWordSpellingSettings):
    return _create_french_word_spelling_session(
        request,
        settings,
        words=FRENCH_VEGETABLE_WORDS,
        title="French Vegetable Word Spelling",
        instruction="Spell each French vegetable word from audio, meaning, or both.",
        topic_tag="vegetable_words",
        audio_url_for_word=french_vegetable_word_audio_url,
    )


def create_french_meat_word_spelling_session(request, settings: FrenchCommonWordSpellingSettings):
    return _create_french_word_spelling_session(
        request,
        settings,
        words=FRENCH_MEAT_WORDS,
        title="French Meat Word Spelling",
        instruction="Spell each French meat word from audio, meaning, or both.",
        topic_tag="meat_words",
        audio_url_for_word=french_meat_word_audio_url,
    )


def _create_french_word_spelling_session(
    request,
    settings: FrenchCommonWordSpellingSettings,
    *,
    words: tuple[FrenchVocabularyItem, ...],
    title: str,
    instruction: str,
    topic_tag: str,
    audio_url_for_word,
):
    descriptor = get_online_plugin(request.plugin)
    rng = random.Random(request.seed)
    targets = _word_targets(request.question_count, rng, words)
    questions = tuple(
        _spelling_question(settings.strategy, target, position, topic_tag, audio_url_for_word)
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
            heading=LocalizedText(title, "en-CA", False),
            instructions=(
                LocalizedText(
                    instruction,
                    "en-CA",
                    False,
                ),
            ),
        ),
        questions=questions,
    )


def _word_targets(
    question_count: int,
    rng: random.Random,
    words: tuple[FrenchVocabularyItem, ...],
) -> list[FrenchVocabularyItem]:
    targets: list[FrenchVocabularyItem] = []
    while len(targets) < question_count:
        shuffled = list(words)
        rng.shuffle(shuffled)
        targets.extend(shuffled)
    return targets[:question_count]


def _spelling_question(
    strategy: str,
    target: FrenchVocabularyItem,
    position: int,
    topic_tag: str,
    audio_url_for_word,
) -> OnlineQuestionSnapshot:
    prompt = _prompt_for_strategy(strategy)
    public_payload = _public_payload_for_strategy(strategy, target, audio_url_for_word)
    speech_text = french_vocabulary_display_text(target, include_article=True)
    return OnlineQuestionSnapshot(
        identifier=f"question-{position}",
        prompt=prompt,
        strategy=strategy,
        skill_tags=("french", "spelling", topic_tag, strategy),
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
        speech_text=speech_text if strategy in {"dictation", "combined"} else None,
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
    audio_url_for_word,
) -> dict:
    payload = {
        "prompt_mode": strategy,
        "language": target.language,
        "input_label": "French word",
        "article_hint": french_vocabulary_article_hint(target),
        "accent_keys": list(FRENCH_ACCENT_KEYS),
        "tools": {"scratch_pad": False, "audio": strategy in {"dictation", "combined"}},
    }
    if strategy in {"translation", "combined"}:
        payload["translation"] = target.meaning
        payload["translation_locale"] = "en-CA"
    if strategy in {"dictation", "combined"}:
        payload["audio_url"] = audio_url_for_word(target, include_article=True)
        payload["speech_text"] = french_vocabulary_display_text(target, include_article=True)
        payload["speech_locale"] = target.language
    return payload
