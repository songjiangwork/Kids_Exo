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

FRENCH_FAMILY_WORDS: tuple[FrenchSoundItem, ...] = (
    FrenchSoundItem("maman", "maman", "mom", "maman"),
    FrenchSoundItem("papa", "papa", "dad", "papa"),
    FrenchSoundItem("parents", "parents", "parents", "parents"),
    FrenchSoundItem("famille", "famille", "family", "famille"),
    FrenchSoundItem("bébé", "bébé", "baby", "bebe"),
    FrenchSoundItem("enfant", "enfant", "child", "enfant"),
    FrenchSoundItem("fils", "fils", "son", "fils"),
    FrenchSoundItem("fille", "fille", "daughter / girl", "fille"),
    FrenchSoundItem("frère", "frère", "brother", "frere"),
    FrenchSoundItem("sœur", "sœur", "sister", "soeur"),
    FrenchSoundItem("grand-mère", "grand-mère", "grandmother", "grand-mere"),
    FrenchSoundItem("grand-père", "grand-père", "grandfather", "grand-pere"),
    FrenchSoundItem("grands-parents", "grands-parents", "grandparents", "grands-parents"),
    FrenchSoundItem("oncle", "oncle", "uncle", "oncle"),
    FrenchSoundItem("tante", "tante", "aunt", "tante"),
    FrenchSoundItem("cousin", "cousin", "male cousin", "cousin"),
    FrenchSoundItem("cousine", "cousine", "female cousin", "cousine"),
    FrenchSoundItem("mari", "mari", "husband", "mari"),
    FrenchSoundItem("femme", "femme", "wife / woman", "femme"),
)

STRATEGY_LABELS = {
    "letter_name_to_letter": "letter names",
}

WORD_STRATEGY_LABELS = {
    "family_words": "family words",
}

FRENCH_ALPHABET_AUDIO_BASE_URL = "/audio/tts/fr/fr-FR-DeniseNeural/alphabet"
FRENCH_FAMILY_WORD_AUDIO_BASE_URL = "/audio/tts/fr/fr-FR-DeniseNeural/common-words/family"
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

    rng = random.Random(request.seed)
    questions = _family_word_questions(request.question_count, rng)
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
                LocalizedText("Listen to a French family word, then choose its meaning.", "en-CA", False),
                LocalizedText("Say the word softly after the audio if you want extra practice.", "en-CA", False),
            ),
        ),
        questions=questions,
    )


def _question_for_strategy(
    strategy: str,
    position: int,
    rng: random.Random,
    target: FrenchSoundItem | None = None,
) -> OnlineQuestionSnapshot:
    items = FRENCH_LETTERS if strategy == "letter_name_to_letter" else FRENCH_FAMILY_WORDS
    target = target or rng.choice(items)
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
        else "Listen to the French family word. Which word do you hear?"
    )
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
            "speech_text": target.text,
            "speech_locale": "fr-FR",
        },
        public_payload={"tools": {"scratch_pad": False, "audio": True}},
        question_type="multiple_choice",
        choices=labels,
        speech_text=target.text,
        speech_locale="fr-FR",
        audio_url=_audio_url_for_strategy(strategy, target),
    )


def _family_word_questions(
    question_count: int,
    rng: random.Random,
) -> tuple[OnlineQuestionSnapshot, ...]:
    targets: list[FrenchSoundItem] = []
    while len(targets) < question_count:
        shuffled = list(FRENCH_FAMILY_WORDS)
        rng.shuffle(shuffled)
        targets.extend(shuffled)
    return tuple(
        _question_for_strategy("family_words", position, rng, target)
        for position, target in enumerate(targets[:question_count], start=1)
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
    if strategy == "letter_name_to_letter":
        return f"{FRENCH_ALPHABET_AUDIO_BASE_URL}/{target.text.lower()}.mp3"
    if strategy == "family_words" and target.audio_slug:
        return f"{FRENCH_FAMILY_WORD_AUDIO_BASE_URL}/{target.audio_slug}.mp3"
    return None


def _skill_tag_for_strategy(strategy: str) -> str:
    return "alphabet_sounds" if strategy == "letter_name_to_letter" else "common_word_sounds"
