from typing import Any

from kids_exo.plugins.enabled import ENABLED_ONLINE_PLUGIN_METADATA
from kids_exo.plugins.metadata import (
    LocaleCoverage,
    OnlineCatalog,
    OnlinePluginDescriptor,
    PluginSettingSchema,
    SettingOption,
)
from kids_exo.plugins.registry import get_plugin_definition


_ONLINE_CATALOG = OnlineCatalog(
    default_locale="en-CA",
    question_counts=(10, 20, 30, 40, 50, 100),
    feedback_modes=("immediate", "deferred"),
    show_timer_configurable=True,
    plugins=ENABLED_ONLINE_PLUGIN_METADATA,
)


def get_online_catalog() -> OnlineCatalog:
    return _ONLINE_CATALOG


def get_online_plugin(plugin_name: str) -> OnlinePluginDescriptor:
    for plugin in _ONLINE_CATALOG.plugins:
        if plugin.plugin == plugin_name:
            return plugin
    raise ValueError(f"Plugin is not enabled for online practice: {plugin_name}")


def load_online_plugin_settings(plugin_name: str, values: dict[str, Any]):
    """Validate public settings before handing them to an existing plugin."""

    descriptor = get_online_plugin(plugin_name)
    schemas = {setting.name: setting for setting in descriptor.settings}
    unexpected_keys = set(values) - set(schemas)
    if unexpected_keys:
        names = ", ".join(sorted(unexpected_keys))
        raise ValueError(f"Plugin settings are not configurable online: {names}")
    merged_values = {
        name: list(schema.default)
        for name, schema in schemas.items()
    }
    merged_values.update(values)
    definition = get_plugin_definition(plugin_name)
    return definition.load_settings(merged_values)
