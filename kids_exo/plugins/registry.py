from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class PluginDefinition:
    load_settings: Callable[[dict], Any]
    validate_format: Callable[[str, str], None]
    create: Callable[[Any], Any]


PluginDefinitionFactory = Callable[[], PluginDefinition]


def _integer_multiplication_distributive_definition() -> PluginDefinition:
    from kids_exo.plugins.integer_multiplication_distributive.plugin import (
        IntegerMultiplicationDistributivePlugin,
    )
    from kids_exo.plugins.integer_multiplication_distributive.settings import (
        load_settings,
        validate_format,
    )

    return PluginDefinition(
        load_settings=load_settings,
        validate_format=validate_format,
        create=IntegerMultiplicationDistributivePlugin,
    )


def _multiply_by_11_definition() -> PluginDefinition:
    from kids_exo.plugins.multiply_by_11.plugin import MultiplyBy11Plugin
    from kids_exo.plugins.multiply_by_11.settings import (
        load_settings,
        validate_format,
    )

    return PluginDefinition(
        load_settings=load_settings,
        validate_format=validate_format,
        create=MultiplyBy11Plugin,
    )


def _multiply_by_nines_definition() -> PluginDefinition:
    from kids_exo.plugins.multiply_by_9_99_999.plugin import MultiplyByNinesPlugin
    from kids_exo.plugins.multiply_by_9_99_999.settings import (
        load_settings,
        validate_format,
    )

    return PluginDefinition(
        load_settings=load_settings,
        validate_format=validate_format,
        create=MultiplyByNinesPlugin,
    )


def _multiply_by_five_family_definition() -> PluginDefinition:
    from kids_exo.plugins.multiply_by_5_25_125.plugin import MultiplyByFiveFamilyPlugin
    from kids_exo.plugins.multiply_by_5_25_125.settings import (
        load_settings,
        validate_format,
    )

    return PluginDefinition(
        load_settings=load_settings,
        validate_format=validate_format,
        create=MultiplyByFiveFamilyPlugin,
    )


def _same_tens_ones_sum_to_ten_definition() -> PluginDefinition:
    from kids_exo.plugins.same_tens_ones_sum_to_ten.plugin import (
        SameTensOnesSumToTenPlugin,
    )
    from kids_exo.plugins.same_tens_ones_sum_to_ten.settings import (
        load_settings,
        validate_format,
    )

    return PluginDefinition(
        load_settings=load_settings,
        validate_format=validate_format,
        create=SameTensOnesSumToTenPlugin,
    )


def _tens_sum_to_ten_same_ones_definition() -> PluginDefinition:
    from kids_exo.plugins.tens_sum_to_ten_same_ones.plugin import (
        TensSumToTenSameOnesPlugin,
    )
    from kids_exo.plugins.tens_sum_to_ten_same_ones.settings import (
        load_settings,
        validate_format,
    )

    return PluginDefinition(
        load_settings=load_settings,
        validate_format=validate_format,
        create=TensSumToTenSameOnesPlugin,
    )


def _near_round_pair_multiplication_definition() -> PluginDefinition:
    from kids_exo.plugins.near_round_pair_multiplication.plugin import (
        NearRoundPairMultiplicationPlugin,
    )
    from kids_exo.plugins.near_round_pair_multiplication.settings import (
        load_settings,
        validate_format,
    )

    return PluginDefinition(
        load_settings=load_settings,
        validate_format=validate_format,
        create=NearRoundPairMultiplicationPlugin,
    )


def _difference_of_squares_definition() -> PluginDefinition:
    from kids_exo.plugins.difference_of_squares.plugin import (
        DifferenceOfSquaresPlugin,
    )
    from kids_exo.plugins.difference_of_squares.settings import (
        load_settings,
        validate_format,
    )

    return PluginDefinition(
        load_settings=load_settings,
        validate_format=validate_format,
        create=DifferenceOfSquaresPlugin,
    )


def _square_ending_in_5_definition() -> PluginDefinition:
    from kids_exo.plugins.square_ending_in_5.plugin import SquareEndingIn5Plugin
    from kids_exo.plugins.square_ending_in_5.settings import (
        load_settings,
        validate_format,
    )

    return PluginDefinition(
        load_settings=load_settings,
        validate_format=validate_format,
        create=SquareEndingIn5Plugin,
    )


def _three_digit_same_prefix_ones_sum_to_ten_definition() -> PluginDefinition:
    from kids_exo.plugins.three_digit_same_prefix_ones_sum_to_ten.plugin import (
        ThreeDigitSamePrefixOnesSumToTenPlugin,
    )
    from kids_exo.plugins.three_digit_same_prefix_ones_sum_to_ten.settings import (
        load_settings,
        validate_format,
    )

    return PluginDefinition(
        load_settings=load_settings,
        validate_format=validate_format,
        create=ThreeDigitSamePrefixOnesSumToTenPlugin,
    )


PLUGIN_DEFINITION_FACTORIES: dict[str, PluginDefinitionFactory] = {
    "integer_multiplication_distributive": _integer_multiplication_distributive_definition,
    "multiply_by_11": _multiply_by_11_definition,
    "multiply_by_9_99_999": _multiply_by_nines_definition,
    "multiply_by_5_25_125": _multiply_by_five_family_definition,
    "same_tens_ones_sum_to_ten": _same_tens_ones_sum_to_ten_definition,
    "tens_sum_to_ten_same_ones": _tens_sum_to_ten_same_ones_definition,
    "near_round_pair_multiplication": _near_round_pair_multiplication_definition,
    "difference_of_squares": _difference_of_squares_definition,
    "square_ending_in_5": _square_ending_in_5_definition,
    "three_digit_same_prefix_ones_sum_to_ten": _three_digit_same_prefix_ones_sum_to_ten_definition,
}


def get_plugin_definition(plugin_name: str) -> PluginDefinition:
    try:
        factory = PLUGIN_DEFINITION_FACTORIES[plugin_name]
    except KeyError as exc:
        raise ValueError(f"Unsupported question type plugin: {plugin_name}") from exc
    return factory()
