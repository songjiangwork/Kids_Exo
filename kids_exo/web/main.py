from fastapi import FastAPI

from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.dependencies import default_repository
from kids_exo.web.routers import (
    assignments,
    auth,
    catalog,
    learners,
    parent_sessions,
    printable,
    student_sessions,
)


def create_app(repository: PracticeRepository | None = None) -> FastAPI:
    app = FastAPI(title="Kids Exo API", version="0.1.0")
    app.include_router(auth.create_router(repository))
    app.include_router(catalog.create_router())
    app.include_router(printable.create_router())
    app.include_router(learners.create_router(repository))
    app.include_router(assignments.create_router(repository))
    app.include_router(parent_sessions.create_router(repository))
    app.include_router(student_sessions.create_router(repository))
    return app


app = create_app(default_repository())
