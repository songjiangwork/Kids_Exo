from dataclasses import dataclass


@dataclass(frozen=True)
class PresetCatalogEntry:
    identifier: str
    subject: str
    category: str
    title: str
    preset_path: str
    default_output_filename: str


_PRESET_ENTRIES = (
    PresetCatalogEntry(
        "math.mental_multiplication.distributive_property.beginner",
        "Math",
        "Mental Multiplication",
        "Distributive Property Multiplication",
        "presets/distributive_property_beginner.toml",
        "distributive-practice.pdf",
    ),
    PresetCatalogEntry(
        "math.mental_multiplication.multiply_by_11.two_digit_beginner",
        "Math",
        "Mental Multiplication",
        "Multiply by 11 - Two Digits",
        "presets/multiply_by_11_beginner.toml",
        "multiply-by-11-practice.pdf",
    ),
    PresetCatalogEntry(
        "math.mental_multiplication.multiply_by_11.three_digit_beginner",
        "Math",
        "Mental Multiplication",
        "Multiply by 11 - Three Digits",
        "presets/multiply_by_11_three_digit_beginner.toml",
        "multiply-by-11-three-digit.pdf",
    ),
    PresetCatalogEntry(
        "math.mental_multiplication.multiply_by_nines.beginner",
        "Math",
        "Mental Multiplication",
        "Multiply by 9, 99, and 999",
        "presets/multiply_by_9_99_999_beginner.toml",
        "multiply-by-nines.pdf",
    ),
    PresetCatalogEntry(
        "math.mental_multiplication.multiply_by_five_family.beginner",
        "Math",
        "Mental Multiplication",
        "Multiply by 5, 25, and 125",
        "presets/multiply_by_5_25_125_beginner.toml",
        "multiply-by-five-family.pdf",
    ),
    PresetCatalogEntry(
        "math.mental_multiplication.same_tens_ones_sum_to_ten.beginner",
        "Math",
        "Mental Multiplication",
        "Same Tens, Ones Sum to 10",
        "presets/same_tens_ones_sum_to_ten_beginner.toml",
        "same-tens-practice.pdf",
    ),
    PresetCatalogEntry(
        "math.mental_multiplication.square_ending_in_5.beginner",
        "Math",
        "Mental Multiplication",
        "Squares Ending in 5",
        "presets/square_ending_in_5_beginner.toml",
        "squares-ending-in-5.pdf",
    ),
    PresetCatalogEntry(
        "math.mental_multiplication.same_prefix_three_digit.beginner",
        "Math",
        "Mental Multiplication",
        "Three-Digit Same Prefix, Ones Sum to 10",
        "presets/three_digit_same_prefix_ones_sum_to_ten_beginner.toml",
        "three-digit-same-prefix.pdf",
    ),
    PresetCatalogEntry(
        "math.mental_multiplication.tens_sum_to_ten_same_ones.beginner",
        "Math",
        "Mental Multiplication",
        "Tens Sum to 10, Same Ones",
        "presets/tens_sum_to_ten_same_ones_beginner.toml",
        "tens-sum-to-ten-same-ones.pdf",
    ),
    PresetCatalogEntry(
        "math.mental_multiplication.near_round_pair.beginner",
        "Math",
        "Mental Multiplication",
        "Near Round-Number Pair Multiplication",
        "presets/near_round_pair_multiplication_beginner.toml",
        "near-round-pair.pdf",
    ),
    PresetCatalogEntry(
        "math.mental_multiplication.difference_of_squares.beginner",
        "Math",
        "Mental Multiplication",
        "Difference of Squares",
        "presets/difference_of_squares_beginner.toml",
        "difference-of-squares.pdf",
    ),
    PresetCatalogEntry(
        "math.mental_multiplication.mixed_practice",
        "Math",
        "Mental Multiplication",
        "Mixed Practice - No Warm-up",
        "presets/mental_multiplication_mixed_practice.toml",
        "mental-multiplication-mixed-practice.pdf",
    ),
    PresetCatalogEntry(
        "math.mental_multiplication.mixed_practice_100",
        "Math",
        "Mental Multiplication",
        "Mixed Practice - 100 Questions",
        "presets/mental_multiplication_mixed_100.toml",
        "mental-multiplication-mixed-100.pdf",
    ),
)


def list_preset_entries() -> tuple[PresetCatalogEntry, ...]:
    return _PRESET_ENTRIES


def get_preset_entry(identifier: str) -> PresetCatalogEntry:
    for entry in _PRESET_ENTRIES:
        if entry.identifier == identifier:
            return entry
    raise ValueError(f"Unknown preset id: {identifier}")
