from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class FrenchVocabularyItem:
    text: str
    label: str
    meaning: str
    audio_slug: str | None = None
    language: str = "fr-FR"
    is_proper_noun: bool = False
    accepted_spellings: tuple[str, ...] = ()
    part_of_speech: str = "noun"
    gender: str | None = None
    number: str = "singular"
    indefinite_article: str | None = None
    definite_article: str | None = None
    learning_article: str | None = None
    article_joiner: str = " "
    teaches_gender: bool = True


FRENCH_FAMILY_WORD_AUDIO_BASE_URL = "/audio/tts/fr/fr-FR-DeniseNeural/common-words/family"
FRENCH_SCHOOL_WORD_AUDIO_BASE_URL = "/audio/tts/fr/fr-FR-DeniseNeural/common-words/school"
FRENCH_FRUIT_WORD_AUDIO_BASE_URL = "/audio/tts/fr/fr-FR-DeniseNeural/common-words/fruit"


def _french_noun(
    text: str,
    meaning: str,
    audio_slug: str,
    *,
    gender: str | None,
    indefinite_article: str | None,
    definite_article: str | None,
    learning_article: str | None,
    number: str = "singular",
    teaches_gender: bool = True,
) -> FrenchVocabularyItem:
    return FrenchVocabularyItem(
        text=text,
        label=text,
        meaning=meaning,
        audio_slug=audio_slug,
        gender=gender,
        number=number,
        indefinite_article=indefinite_article,
        definite_article=definite_article,
        learning_article=learning_article,
        teaches_gender=teaches_gender,
    )


FRENCH_FAMILY_WORDS: tuple[FrenchVocabularyItem, ...] = (
    _french_noun("maman", "mom", "maman", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("papa", "dad", "papa", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("parents", "parents", "parents", gender="plural", number="plural", indefinite_article="des", definite_article="les", learning_article="des", teaches_gender=False),
    _french_noun("famille", "family", "famille", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("bébé", "baby", "bebe", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("enfant", "child", "enfant", gender="masculine", indefinite_article="un", definite_article="l'", learning_article="un"),
    _french_noun("fils", "son", "fils", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("fille", "daughter / girl", "fille", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("frère", "brother", "frere", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("sœur", "sister", "soeur", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("grand-mère", "grandmother", "grand-mere", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("grand-père", "grandfather", "grand-pere", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("grands-parents", "grandparents", "grands-parents", gender="plural", number="plural", indefinite_article="des", definite_article="les", learning_article="des", teaches_gender=False),
    _french_noun("oncle", "uncle", "oncle", gender="masculine", indefinite_article="un", definite_article="l'", learning_article="un"),
    _french_noun("tante", "aunt", "tante", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("cousin", "male cousin", "cousin", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("cousine", "female cousin", "cousine", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("mari", "husband", "mari", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("femme", "wife / woman", "femme", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
)


FRENCH_SCHOOL_WORDS: tuple[FrenchVocabularyItem, ...] = (
    _french_noun("école", "school", "ecole", gender="feminine", indefinite_article="une", definite_article="l'", learning_article="une"),
    _french_noun("élève", "student", "eleve", gender="common", indefinite_article=None, definite_article="l'", learning_article=None, teaches_gender=False),
    _french_noun("professeur", "teacher", "professeur", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("classe", "class", "classe", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("cahier", "notebook", "cahier", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("livre", "book", "livre", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("crayon", "pencil", "crayon", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("stylo", "pen", "stylo", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("gomme", "eraser", "gomme", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("règle", "ruler", "regle", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("tableau", "board", "tableau", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("bureau", "desk", "bureau", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("sac", "bag / backpack", "sac", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("devoir", "homework", "devoir", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("récréation", "recess", "recreation", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
)


FRENCH_FRUIT_WORDS: tuple[FrenchVocabularyItem, ...] = (
    _french_noun("pomme", "apple", "pomme", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("banane", "banana", "banane", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("orange", "orange", "orange", gender="feminine", indefinite_article="une", definite_article="l'", learning_article="une"),
    _french_noun("poire", "pear", "poire", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("fraise", "strawberry", "fraise", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("cerise", "cherry", "cerise", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("pêche", "peach", "peche", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("abricot", "apricot", "abricot", gender="masculine", indefinite_article="un", definite_article="l'", learning_article="un"),
    _french_noun("prune", "plum", "prune", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("citron", "lemon", "citron", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("melon", "melon", "melon", gender="masculine", indefinite_article="un", definite_article="le", learning_article="un"),
    _french_noun("pastèque", "watermelon", "pasteque", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("ananas", "pineapple", "ananas", gender="masculine", indefinite_article="un", definite_article="l'", learning_article="un"),
    _french_noun("framboise", "raspberry", "framboise", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
    _french_noun("myrtille", "blueberry", "myrtille", gender="feminine", indefinite_article="une", definite_article="la", learning_article="une"),
)


def french_vocabulary_display_text(
    item: FrenchVocabularyItem,
    *,
    include_article: bool = False,
) -> str:
    if include_article and item.learning_article:
        return f"{item.learning_article}{item.article_joiner}{item.text}"
    return item.text


def french_vocabulary_article_hint(item: FrenchVocabularyItem) -> dict[str, str | bool] | None:
    if not item.learning_article:
        return None
    return {
        "article": item.learning_article,
        "gender": item.gender or "",
        "number": item.number,
        "display_text": item.learning_article,
        "full_display_text": french_vocabulary_display_text(item, include_article=True),
        "mode": "prefix",
        "teaches_gender": item.teaches_gender,
    }


def french_vocabulary_audio_url(
    item: FrenchVocabularyItem,
    *,
    base_url: str,
    include_article: bool = False,
) -> str | None:
    if not item.audio_slug:
        return None
    if include_article and item.learning_article:
        phrase_slug = f"{item.learning_article}-{item.audio_slug}"
        return f"{base_url}/with-article/{phrase_slug}.mp3"
    return f"{base_url}/{item.audio_slug}.mp3"


def french_family_word_audio_url(item: FrenchVocabularyItem, *, include_article: bool = False) -> str | None:
    return french_vocabulary_audio_url(
        item,
        base_url=FRENCH_FAMILY_WORD_AUDIO_BASE_URL,
        include_article=include_article,
    )


def french_school_word_audio_url(item: FrenchVocabularyItem, *, include_article: bool = False) -> str | None:
    return french_vocabulary_audio_url(
        item,
        base_url=FRENCH_SCHOOL_WORD_AUDIO_BASE_URL,
        include_article=include_article,
    )


def french_fruit_word_audio_url(item: FrenchVocabularyItem, *, include_article: bool = False) -> str | None:
    return french_vocabulary_audio_url(
        item,
        base_url=FRENCH_FRUIT_WORD_AUDIO_BASE_URL,
        include_article=include_article,
    )


FrenchVocabularyAudioUrl = Callable[[FrenchVocabularyItem], str | None]
