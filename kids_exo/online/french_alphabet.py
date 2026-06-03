from dataclasses import dataclass
import random

from kids_exo.localization import LocalizedPresentation, LocalizedText
from kids_exo.online.catalog import get_online_plugin
from kids_exo.online.models import OnlineQuestionSnapshot, PracticeSessionSnapshot


@dataclass(frozen=True)
class FrenchSoundItem:
    text: str
    label: str
    meaning: str


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

FRENCH_WORDS: tuple[FrenchSoundItem, ...] = (
    FrenchSoundItem("ami", "ami", "friend"),
    FrenchSoundItem("chat", "chat", "cat"),
    FrenchSoundItem("lune", "lune", "moon"),
    FrenchSoundItem("école", "école", "school"),
    FrenchSoundItem("maman", "maman", "mom"),
    FrenchSoundItem("papa", "papa", "dad"),
    FrenchSoundItem("bonjour", "bonjour", "hello"),
    FrenchSoundItem("merci", "merci", "thank you"),
    FrenchSoundItem("livre", "livre", "book"),
    FrenchSoundItem("rouge", "rouge", "red"),
    FrenchSoundItem("bleu", "bleu", "blue"),
    FrenchSoundItem("soleil", "soleil", "sun"),
)

STRATEGY_LABELS = {
    "letter_name_to_letter": "letter names",
}

WORD_STRATEGY_LABELS = {
    "word_sound_to_word": "simple words",
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
        strategies = ("word_sound_to_word",)
    unexpected = set(strategies) - set(WORD_STRATEGY_LABELS)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ValueError(f"Unsupported French common words strategy: {names}")

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
            heading=LocalizedText("French Common Word Sounds", "en-CA", False),
            instructions=(
                LocalizedText("Listen to a common French word, then choose its meaning.", "en-CA", False),
                LocalizedText("Say the word softly after the audio if you want extra practice.", "en-CA", False),
            ),
        ),
        questions=questions,
    )


def _question_for_strategy(
    strategy: str,
    position: int,
    rng: random.Random,
) -> OnlineQuestionSnapshot:
    items = FRENCH_LETTERS if strategy == "letter_name_to_letter" else FRENCH_WORDS
    target = rng.choice(items)
    distractors = rng.sample(_distractor_pool(strategy, target, items), 3)
    choices = [target, *distractors]
    rng.shuffle(choices)
    expected_answer = choices.index(target) + 1
    labels = tuple(
        choice.label if strategy == "letter_name_to_letter" else f"{choice.label} ({choice.meaning})"
        for choice in choices
    )
    prompt = (
        "Listen to the French letter name. Which letter do you hear?"
        if strategy == "letter_name_to_letter"
        else "Listen to the French word. Which word do you hear?"
    )
    return OnlineQuestionSnapshot(
        identifier=f"question-{position}",
        prompt=prompt,
        strategy=strategy,
        expected_answer=expected_answer,
        skill_tags=("french", "pronunciation", "alphabet_sounds", strategy),
        question_type="multiple_choice",
        choices=labels,
        speech_text=target.text,
        speech_locale="fr-FR" if strategy == "letter_name_to_letter" else "fr-CA",
        audio_url=_audio_url_for_strategy(strategy, target),
    )


def _distractor_pool(
    strategy: str,
    target: FrenchSoundItem,
    items: tuple[FrenchSoundItem, ...],
) -> list[FrenchSoundItem]:
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


def _audio_url_for_strategy(strategy: str, target: FrenchSoundItem) -> str | None:
    if strategy != "letter_name_to_letter":
        return None
    return f"{FRENCH_ALPHABET_AUDIO_BASE_URL}/{target.text.lower()}.mp3"
