from fastapi import APIRouter

from kids_exo.online.catalog import get_online_catalog
from kids_exo.web.schemas import OnlineCatalogResponse


def create_router() -> APIRouter:
    router = APIRouter()

    @router.get("/api/practice-plugins", response_model=OnlineCatalogResponse)
    def list_practice_plugins() -> OnlineCatalogResponse:
        return OnlineCatalogResponse.model_validate(get_online_catalog())

    return router
