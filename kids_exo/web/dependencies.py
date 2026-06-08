import os

from fastapi import HTTPException

from kids_exo.online.session import OnlineSessionRequest, create_practice_session
from kids_exo.persistence.database import build_engine, build_session_factory
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.schemas import PracticePreviewRequest


def create_snapshot(request: PracticePreviewRequest):
    return create_practice_session(
        OnlineSessionRequest(
            plugin=request.plugin,
            plugin_settings=request.plugin_settings,
            question_count=request.question_count,
            requested_locale=request.requested_locale,
            feedback_mode=request.feedback_mode,
            show_timer=request.show_timer,
            seed=request.seed,
        )
    )


def require_repository(repository: PracticeRepository | None) -> PracticeRepository:
    if repository is None:
        raise HTTPException(status_code=503, detail="Persistence is not configured")
    return repository


def default_repository() -> PracticeRepository:
    database_url = os.environ.get(
        "KIDS_EXO_DATABASE_URL",
        "sqlite+pysqlite:///kids-exo.db",
    )
    return PracticeRepository(build_session_factory(build_engine(database_url)))
