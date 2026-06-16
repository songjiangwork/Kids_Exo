from dataclasses import dataclass


SUPPORTED_DIFFICULTIES = {"intro", "mixed"}


@dataclass(frozen=True)
class ChickenRabbitWordProblemSettings:
    difficulty: str = "intro"


def load_settings(data: dict) -> ChickenRabbitWordProblemSettings:
    unexpected_keys = set(data) - {"difficulty"}
    if unexpected_keys:
        names = ", ".join(sorted(unexpected_keys))
        raise ValueError(f"Plugin settings are not configurable online: {names}")
    difficulties = tuple(data.get("difficulty", ("intro",)))
    difficulty = str(difficulties[0]) if difficulties else "intro"
    if len(difficulties) != 1 or difficulty not in SUPPORTED_DIFFICULTIES:
        raise ValueError("Unsupported word problem difficulty")
    return ChickenRabbitWordProblemSettings(difficulty=difficulty)
