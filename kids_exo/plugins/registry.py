from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class PluginDefinition:
    load_settings: Callable[[dict], Any]
    validate_format: Callable[[str, str], None]
    create: Callable[[Any], Any]


def get_plugin_definition(plugin_name: str) -> PluginDefinition:
    if plugin_name == "integer_multiplication_distributive":
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
    if plugin_name == "multiply_by_11":
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
    if plugin_name == "same_tens_ones_sum_to_ten":
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
    if plugin_name == "square_ending_in_5":
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
    raise ValueError(f"Unsupported question type plugin: {plugin_name}")
