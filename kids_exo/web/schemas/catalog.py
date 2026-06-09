from kids_exo.web.schemas.base import FromDomainModel


class SettingOptionResponse(FromDomainModel):
    value: int | str
    label: str


class PluginSettingSchemaResponse(FromDomainModel):
    name: str
    label: str
    control: str
    default: tuple[int | str, ...]
    options: tuple[SettingOptionResponse, ...]


class LocaleCoverageResponse(FromDomainModel):
    locale: str
    full_sections: tuple[str, ...]
    partial_sections: tuple[str, ...]


class OnlinePluginResponse(FromDomainModel):
    plugin: str
    subject: str
    category: str
    title: str
    description: str
    default_locale: str
    locale_coverage: tuple[LocaleCoverageResponse, ...]
    settings: tuple[PluginSettingSchemaResponse, ...]
    supported_delivery_modes: tuple[str, ...] = ()
    answer_types: tuple[str, ...] = ()
    release_stage: str = "published"


class OnlineCatalogResponse(FromDomainModel):
    default_locale: str
    question_counts: tuple[int, ...]
    feedback_modes: tuple[str, ...]
    show_timer_configurable: bool
    plugins: tuple[OnlinePluginResponse, ...]
