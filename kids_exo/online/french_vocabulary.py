from dataclasses import dataclass


@dataclass(frozen=True)
class FrenchVocabularyItem:
    text: str
    label: str
    meaning: str
    audio_slug: str | None = None
    language: str = "fr-FR"
    is_proper_noun: bool = False
    accepted_spellings: tuple[str, ...] = ()


FRENCH_FAMILY_WORD_AUDIO_BASE_URL = "/audio/tts/fr/fr-FR-DeniseNeural/common-words/family"
FRENCH_SCHOOL_WORD_AUDIO_BASE_URL = "/audio/tts/fr/fr-FR-DeniseNeural/common-words/school"

FRENCH_FAMILY_WORDS: tuple[FrenchVocabularyItem, ...] = (
    FrenchVocabularyItem("maman", "maman", "mom", "maman"),
    FrenchVocabularyItem("papa", "papa", "dad", "papa"),
    FrenchVocabularyItem("parents", "parents", "parents", "parents"),
    FrenchVocabularyItem("famille", "famille", "family", "famille"),
    FrenchVocabularyItem("bébé", "bébé", "baby", "bebe"),
    FrenchVocabularyItem("enfant", "enfant", "child", "enfant"),
    FrenchVocabularyItem("fils", "fils", "son", "fils"),
    FrenchVocabularyItem("fille", "fille", "daughter / girl", "fille"),
    FrenchVocabularyItem("frère", "frère", "brother", "frere"),
    FrenchVocabularyItem("sœur", "sœur", "sister", "soeur"),
    FrenchVocabularyItem("grand-mère", "grand-mère", "grandmother", "grand-mere"),
    FrenchVocabularyItem("grand-père", "grand-père", "grandfather", "grand-pere"),
    FrenchVocabularyItem("grands-parents", "grands-parents", "grandparents", "grands-parents"),
    FrenchVocabularyItem("oncle", "oncle", "uncle", "oncle"),
    FrenchVocabularyItem("tante", "tante", "aunt", "tante"),
    FrenchVocabularyItem("cousin", "cousin", "male cousin", "cousin"),
    FrenchVocabularyItem("cousine", "cousine", "female cousin", "cousine"),
    FrenchVocabularyItem("mari", "mari", "husband", "mari"),
    FrenchVocabularyItem("femme", "femme", "wife / woman", "femme"),
)


FRENCH_SCHOOL_WORDS: tuple[FrenchVocabularyItem, ...] = (
    FrenchVocabularyItem("école", "école", "school", "ecole"),
    FrenchVocabularyItem("élève", "élève", "student", "eleve"),
    FrenchVocabularyItem("professeur", "professeur", "teacher", "professeur"),
    FrenchVocabularyItem("classe", "classe", "class", "classe"),
    FrenchVocabularyItem("cahier", "cahier", "notebook", "cahier"),
    FrenchVocabularyItem("livre", "livre", "book", "livre"),
    FrenchVocabularyItem("crayon", "crayon", "pencil", "crayon"),
    FrenchVocabularyItem("stylo", "stylo", "pen", "stylo"),
    FrenchVocabularyItem("gomme", "gomme", "eraser", "gomme"),
    FrenchVocabularyItem("règle", "règle", "ruler", "regle"),
    FrenchVocabularyItem("tableau", "tableau", "board", "tableau"),
    FrenchVocabularyItem("bureau", "bureau", "desk", "bureau"),
    FrenchVocabularyItem("sac", "sac", "bag / backpack", "sac"),
    FrenchVocabularyItem("devoir", "devoir", "homework", "devoir"),
    FrenchVocabularyItem("récréation", "récréation", "recess", "recreation"),
)


def french_family_word_audio_url(item: FrenchVocabularyItem) -> str | None:
    if not item.audio_slug:
        return None
    return f"{FRENCH_FAMILY_WORD_AUDIO_BASE_URL}/{item.audio_slug}.mp3"


def french_school_word_audio_url(item: FrenchVocabularyItem) -> str | None:
    if not item.audio_slug:
        return None
    return f"{FRENCH_SCHOOL_WORD_AUDIO_BASE_URL}/{item.audio_slug}.mp3"
