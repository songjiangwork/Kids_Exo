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
    raise ValueError(f"Unsupported question type plugin: {plugin_name}")
