from dataclasses import dataclass
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
    french_vocabulary_display_text,
)
from kids_exo.online.models import OnlineQuestionSnapshot, PracticeSessionSnapshot


@dataclass(frozen=True)
class FrenchSoundItem:
    text: str
    label: str
    meaning: str
    audio_slug: str | None = None


FRENCH_LETTERS: tuple[FrenchSoundItem, ...] = (
    FrenchSoundItem("A", "A", "letter A"),
    FrenchSoundItem("B", "B", "letter B"),
    FrenchSoundItem("C", "C", "letter C"),
    FrenchSoundItem("D", "D", "letter D"),
    FrenchSoundItem("E", "E", "letter E"),
    FrenchSoundItem("F", "F", "letter F"),
    FrenchSoundItem("G", "G", "letter G"),
    FrenchSoundItem("H", "H", "letter H"),
    FrenchSoundItem("I", "I", "letter I"),
    FrenchSoundItem("J", "J", "letter J"),
    FrenchSoundItem("K", "K", "letter K"),
    FrenchSoundItem("L", "L", "letter L"),
    FrenchSoundItem("M", "M", "letter M"),
    FrenchSoundItem("N", "N", "letter N"),
    FrenchSoundItem("O", "O", "letter O"),
    FrenchSoundItem("P", "P", "letter P"),
    FrenchSoundItem("Q", "Q", "letter Q"),
    FrenchSoundItem("R", "R", "letter R"),
    FrenchSoundItem("S", "S", "letter S"),
    FrenchSoundItem("T", "T", "letter T"),
    FrenchSoundItem("U", "U", "letter U"),
    FrenchSoundItem("V", "V", "letter V"),
    FrenchSoundItem("W", "W", "letter W"),
    FrenchSoundItem("X", "X", "letter X"),
    FrenchSoundItem("Y", "Y", "letter Y"),
    FrenchSoundItem("Z", "Z", "letter Z"),
)

STRATEGY_LABELS = {
    "letter_name_to_letter": "letter names",
}

WORD_STRATEGY_LABELS = {
    "family_words": "family words",
}
SCHOOL_WORD_STRATEGY_LABELS = {
    "school_words": "school words",
}
FRUIT_WORD_STRATEGY_LABELS = {
    "fruit_words": "fruit words",
}
VEGETABLE_WORD_STRATEGY_LABELS = {
    "vegetable_words": "vegetable words",
}
MEAT_WORD_STRATEGY_LABELS = {
    "meat_words": "meat words",
}

FRENCH_ALPHABET_AUDIO_BASE_URL = "/audio/tts/fr/fr-FR-DeniseNeural/alphabet"
SIMILAR_LETTER_GROUPS: tuple[frozenset[str], ...] = (
    frozenset(("B", "C", "D", "G", "P", "T", "V")),
    frozenset(("M", "N")),
    frozenset(("F", "S")),
    frozenset(("I", "J")),
    frozenset(("O", "Q", "U")),
)


def create_french_alphabet_session(request) -> PracticeSessionSnapshot:
    descriptor = get_online_plugin(request.plugin)
    strategies = tuple(request.plugin_settings.get("strategies", ()))
    if not strategies:
        strategies = ("letter_name_to_letter",)
    unexpected = set(strategies) - set(STRATEGY_LABELS)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ValueError(f"Unsupported French alphabet strategy: {names}")

    rng = random.Random(request.seed)
    strategy_plan = [strategies[index % len(strategies)] for index in range(request.question_count)]
    rng.shuffle(strategy_plan)
    questions = tuple(
        _question_for_strategy(strategy, position, rng)
        for position, strategy in enumerate(strategy_plan, start=1)
    )
    return PracticeSessionSnapshot(
        plugin=request.plugin,
        subject=descriptor.subject,
        category=descriptor.category,
        skill=descriptor.title,
        plugin_settings={"strategies": list(strategies)},
        requested_locale=request.requested_locale,
        feedback_mode=request.feedback_mode,
        show_timer=request.show_timer,
        seed=request.seed,
        presentation=LocalizedPresentation(
            heading=LocalizedText("French Alphabet Sounds", "en-CA", False),
            instructions=(
                LocalizedText("Listen first, then choose the matching French letter.", "en-CA", False),
                LocalizedText("Use Replay if you want to hear it again.", "en-CA", False),
            ),
        ),
        questions=questions,
    )


def create_french_common_words_session(request) -> PracticeSessionSnapshot:
    descriptor = get_online_plugin(request.plugin)
    strategies = tuple(request.plugin_settings.get("strategies", ()))
    if not strategies:
        strategies = ("family_words",)
    unexpected = set(strategies) - set(WORD_STRATEGY_LABELS)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ValueError(f"Unsupported French common words strategy: {names}")

    return _create_word_sound_session(
        request,
        strategies,
        words=FRENCH_FAMILY_WORDS,
        strategy="family_words",
        title="French Family Word Sounds",
        instruction="Listen to a French family word, then choose its meaning.",
    )


def create_french_school_words_session(request) -> PracticeSessionSnapshot:
    strategies = tuple(request.plugin_settings.get("strategies", ()))
    if not strategies:
        strategies = ("school_words",)
    unexpected = set(strategies) - set(SCHOOL_WORD_STRATEGY_LABELS)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ValueError(f"Unsupported French school words strategy: {names}")

    return _create_word_sound_session(
        request,
        strategies,
        words=FRENCH_SCHOOL_WORDS,
        strategy="school_words",
        title="French School Word Sounds",
        instruction="Listen to a French school word, then choose its meaning.",
    )


def create_french_fruit_words_session(request) -> PracticeSessionSnapshot:
    strategies = tuple(request.plugin_settings.get("strategies", ()))
    if not strategies:
        strategies = ("fruit_words",)
    unexpected = set(strategies) - set(FRUIT_WORD_STRATEGY_LABELS)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ValueError(f"Unsupported French fruit words strategy: {names}")

    return _create_word_sound_session(
        request,
        strategies,
        words=FRENCH_FRUIT_WORDS,
        strategy="fruit_words",
        title="French Fruit Word Sounds",
        instruction="Listen to a French fruit word, then choose its meaning.",
    )


def create_french_vegetable_words_session(request) -> PracticeSessionSnapshot:
    strategies = tuple(request.plugin_settings.get("strategies", ()))
    if not strategies:
        strategies = ("vegetable_words",)
    unexpected = set(strategies) - set(VEGETABLE_WORD_STRATEGY_LABELS)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ValueError(f"Unsupported French vegetable words strategy: {names}")

    return _create_word_sound_session(
        request,
        strategies,
        words=FRENCH_VEGETABLE_WORDS,
        strategy="vegetable_words",
        title="French Vegetable Word Sounds",
        instruction="Listen to a French vegetable word, then choose its meaning.",
    )


def create_french_meat_words_session(request) -> PracticeSessionSnapshot:
    strategies = tuple(request.plugin_settings.get("strategies", ()))
    if not strategies:
        strategies = ("meat_words",)
    unexpected = set(strategies) - set(MEAT_WORD_STRATEGY_LABELS)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ValueError(f"Unsupported French meat words strategy: {names}")

    return _create_word_sound_session(
        request,
        strategies,
        words=FRENCH_MEAT_WORDS,
        strategy="meat_words",
        title="French Meat Word Sounds",
        instruction="Listen to a French meat word, then choose its meaning.",
    )


def _create_word_sound_session(
    request,
    strategies: tuple[str, ...],
    *,
    words: tuple[FrenchVocabularyItem, ...],
    strategy: str,
    title: str,
    instruction: str,
) -> PracticeSessionSnapshot:
    descriptor = get_online_plugin(request.plugin)
    rng = random.Random(request.seed)
    questions = _word_questions(request.question_count, rng, words, strategy)
    return PracticeSessionSnapshot(
        plugin=request.plugin,
        subject=descriptor.subject,
        category=descriptor.category,
        skill=descriptor.title,
        plugin_settings={"strategies": list(strategies)},
        requested_locale=request.requested_locale,
        feedback_mode=request.feedback_mode,
        show_timer=request.show_timer,
        seed=request.seed,
        presentation=LocalizedPresentation(
            heading=LocalizedText(title, "en-CA", False),
            instructions=(
                LocalizedText(instruction, "en-CA", False),
                LocalizedText("Say the word softly after the audio if you want extra practice.", "en-CA", False),
            ),
        ),
        questions=questions,
    )


def _question_for_strategy(
    strategy: str,
    position: int,
    rng: random.Random,
    target: FrenchSoundItem | FrenchVocabularyItem | None = None,
) -> OnlineQuestionSnapshot:
    if strategy == "letter_name_to_letter":
        items = FRENCH_LETTERS
    elif strategy == "meat_words":
        items = FRENCH_MEAT_WORDS
    elif strategy == "vegetable_words":
        items = FRENCH_VEGETABLE_WORDS
    elif strategy == "fruit_words":
        items = FRENCH_FRUIT_WORDS
    elif strategy == "school_words":
        items = FRENCH_SCHOOL_WORDS
    else:
        items = FRENCH_FAMILY_WORDS
    target = target or rng.choice(items)
    distractors = rng.sample(_distractor_pool(strategy, target, items), 3)
    choices = [target, *distractors]
    rng.shuffle(choices)
    expected_answer = choices.index(target) + 1
    labels = tuple(_choice_label(strategy, choice) for choice in choices)
    prompt = (
        "Listen to the French letter name. Which letter do you hear?"
        if strategy == "letter_name_to_letter"
        else "Listen to the French word. Which word do you hear?"
    )
    speech_text = _speech_text_for_strategy(strategy, target)
    return OnlineQuestionSnapshot(
        identifier=f"question-{position}",
        prompt=prompt,
        strategy=strategy,
        expected_answer=expected_answer,
        skill_tags=("french", "pronunciation", _skill_tag_for_strategy(strategy), strategy),
        renderer_type="listening_choice",
        answer_type="multiple_choice_index",
        evaluation_payload={"expected_index": expected_answer},
        prompt_payload={
            "display_text": prompt,
            "choices": list(labels),
            "speech_text": speech_text,
            "speech_locale": "fr-FR",
        },
        public_payload={"tools": {"scratch_pad": False, "audio": True}},
        question_type="multiple_choice",
        choices=labels,
        speech_text=speech_text,
        speech_locale="fr-FR",
        audio_url=_audio_url_for_strategy(strategy, target),
    )


def _word_questions(
    question_count: int,
    rng: random.Random,
    words: tuple[FrenchVocabularyItem, ...],
    strategy: str,
) -> tuple[OnlineQuestionSnapshot, ...]:
    targets: list[FrenchVocabularyItem] = []
    while len(targets) < question_count:
        shuffled = list(words)
        rng.shuffle(shuffled)
        targets.extend(shuffled)
    return tuple(
        _question_for_strategy(strategy, position, rng, target)
        for position, target in enumerate(targets[:question_count], start=1)
    )


def _distractor_pool(
    strategy: str,
    target: FrenchSoundItem | FrenchVocabularyItem,
    items: tuple[FrenchSoundItem | FrenchVocabularyItem, ...],
) -> list[FrenchSoundItem | FrenchVocabularyItem]:
    if strategy != "letter_name_to_letter":
        return [item for item in items if item.text != target.text]
    confusing = _similar_letters(target.text)
    return [
        item
        for item in items
        if item.text != target.text and item.text not in confusing
    ]


def _similar_letters(letter: str) -> frozenset[str]:
    for group in SIMILAR_LETTER_GROUPS:
        if letter in group:
            return group
    return frozenset((letter,))


def _choice_label(strategy: str, choice: FrenchSoundItem | FrenchVocabularyItem) -> str:
    if strategy == "letter_name_to_letter":
        return choice.label
    if isinstance(choice, FrenchVocabularyItem):
        display_text = french_vocabulary_display_text(choice, include_article=True)
        return f"{display_text} ({choice.meaning})"
    return choice.label


def _speech_text_for_strategy(strategy: str, target: FrenchSoundItem | FrenchVocabularyItem) -> str:
    if strategy == "letter_name_to_letter":
        return target.text
    if isinstance(target, FrenchVocabularyItem):
        return french_vocabulary_display_text(target, include_article=True)
    return target.text


def _audio_url_for_strategy(strategy: str, target: FrenchSoundItem | FrenchVocabularyItem) -> str | None:
    if strategy == "letter_name_to_letter":
        return f"{FRENCH_ALPHABET_AUDIO_BASE_URL}/{target.text.lower()}.mp3"
    if strategy == "family_words" and isinstance(target, FrenchVocabularyItem):
        return french_family_word_audio_url(target, include_article=True)
    if strategy == "fruit_words" and isinstance(target, FrenchVocabularyItem):
        return french_fruit_word_audio_url(target, include_article=True)
    if strategy == "vegetable_words" and isinstance(target, FrenchVocabularyItem):
        return french_vegetable_word_audio_url(target, include_article=True)
    if strategy == "meat_words" and isinstance(target, FrenchVocabularyItem):
        return french_meat_word_audio_url(target, include_article=True)
    if strategy == "school_words" and isinstance(target, FrenchVocabularyItem):
        return french_school_word_audio_url(target, include_article=True)
    return None


def _skill_tag_for_strategy(strategy: str) -> str:
    if strategy == "letter_name_to_letter":
        return "alphabet_sounds"
    if strategy == "school_words":
        return "school_word_sounds"
    if strategy == "fruit_words":
        return "fruit_word_sounds"
    if strategy == "vegetable_words":
        return "vegetable_word_sounds"
    if strategy == "meat_words":
        return "meat_word_sounds"
    return "family_word_sounds"
