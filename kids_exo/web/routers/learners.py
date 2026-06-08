from fastapi import APIRouter, HTTPException

from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.dependencies import require_repository
from kids_exo.web.mappers import learner_analytics_response
from kids_exo.web.schemas import (
    LearnerAnalyticsResponse,
    LearnerCreateRequest,
    LearnerResponse,
    LearnerUpdateRequest,
)


def create_router(repository: PracticeRepository | None) -> APIRouter:
    router = APIRouter()

    @router.post("/api/learners", response_model=LearnerResponse, status_code=201)
    def create_learner(request: LearnerCreateRequest) -> LearnerResponse:
        storage = require_repository(repository)
        try:
            return LearnerResponse.model_validate(storage.create_learner(request.nickname))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @router.get("/api/learners", response_model=list[LearnerResponse])
    def list_learners() -> list[LearnerResponse]:
        storage = require_repository(repository)
        return [
            LearnerResponse.model_validate(learner)
            for learner in storage.list_learners()
        ]

    @router.get("/api/learners/{learner_id}", response_model=LearnerResponse)
    def get_learner(learner_id: int) -> LearnerResponse:
        storage = require_repository(repository)
        try:
            return LearnerResponse.model_validate(storage.get_learner(learner_id))
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.get("/api/learners/{learner_id}/analytics", response_model=LearnerAnalyticsResponse)
    def get_learner_analytics(learner_id: int) -> LearnerAnalyticsResponse:
        storage = require_repository(repository)
        try:
            return learner_analytics_response(storage.get_learner_analytics(learner_id))
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.patch("/api/learners/{learner_id}", response_model=LearnerResponse)
    def update_learner(
        learner_id: int,
        request: LearnerUpdateRequest,
    ) -> LearnerResponse:
        storage = require_repository(repository)
        try:
            return LearnerResponse.model_validate(
                storage.update_learner(
                    learner_id,
                    nickname=request.nickname,
                    active=request.active,
                )
            )
        except ValueError as exc:
            status_code = 404 if str(exc).startswith("Unknown learner") else 422
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    @router.delete("/api/learners/{learner_id}", status_code=204)
    def delete_learner(learner_id: int) -> None:
        storage = require_repository(repository)
        try:
            storage.delete_learner(learner_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return router
