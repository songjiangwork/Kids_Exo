from fastapi import APIRouter, Depends, HTTPException

from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.auth import (
    LocalSessionStore,
    ParentContext,
    StudentAccessContext,
    require_parent_unlock,
    require_student_access,
)
from kids_exo.web.dependencies import require_repository
from kids_exo.web.mappers import learner_analytics_response
from kids_exo.web.schemas import (
    LearnerAnalyticsResponse,
    LearnerCreateRequest,
    LearnerResponse,
    LearnerUpdateRequest,
    StudentPinResetRequest,
)


def create_router(
    repository: PracticeRepository | None,
    session_store: LocalSessionStore,
) -> APIRouter:
    router = APIRouter()
    parent_unlock = require_parent_unlock(repository, session_store)
    student_access = require_student_access(repository, session_store)

    @router.post("/api/learners", response_model=LearnerResponse, status_code=201)
    def create_learner(
        request: LearnerCreateRequest,
        parent: ParentContext = Depends(parent_unlock),
    ) -> LearnerResponse:
        storage = require_repository(repository)
        try:
            return LearnerResponse.model_validate(
                storage.create_learner(request.nickname, household_id=parent.household_id)
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @router.get("/api/learners", response_model=list[LearnerResponse])
    def list_learners(parent: ParentContext = Depends(parent_unlock)) -> list[LearnerResponse]:
        storage = require_repository(repository)
        return [
            LearnerResponse.model_validate(learner)
            for learner in storage.list_learners(household_id=parent.household_id)
        ]

    @router.get("/api/learners/{learner_id}", response_model=LearnerResponse)
    def get_learner(
        learner_id: int,
        access: StudentAccessContext = Depends(student_access),
    ) -> LearnerResponse:
        storage = require_repository(repository)
        try:
            return LearnerResponse.model_validate(
                storage.get_learner(learner_id, household_id=access.household_id)
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.get("/api/learners/{learner_id}/analytics", response_model=LearnerAnalyticsResponse)
    def get_learner_analytics(
        learner_id: int,
        access: StudentAccessContext = Depends(student_access),
    ) -> LearnerAnalyticsResponse:
        storage = require_repository(repository)
        try:
            return learner_analytics_response(
                storage.get_learner_analytics(learner_id, household_id=access.household_id)
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.patch("/api/learners/{learner_id}", response_model=LearnerResponse)
    def update_learner(
        learner_id: int,
        request: LearnerUpdateRequest,
        parent: ParentContext = Depends(parent_unlock),
    ) -> LearnerResponse:
        storage = require_repository(repository)
        try:
            return LearnerResponse.model_validate(
                storage.update_learner(
                    learner_id,
                    nickname=request.nickname,
                    active=request.active,
                    household_id=parent.household_id,
                )
            )
        except ValueError as exc:
            status_code = 404 if str(exc).startswith("Unknown learner") else 422
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    @router.delete("/api/learners/{learner_id}", status_code=204)
    def delete_learner(
        learner_id: int,
        parent: ParentContext = Depends(parent_unlock),
    ) -> None:
        storage = require_repository(repository)
        try:
            storage.delete_learner(learner_id, household_id=parent.household_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.post("/api/learners/{learner_id}/student-pin", status_code=204)
    def reset_student_pin(
        learner_id: int,
        request: StudentPinResetRequest,
        parent: ParentContext = Depends(parent_unlock),
    ) -> None:
        storage = require_repository(repository)
        try:
            storage.reset_student_pin(
                learner_id,
                pin=request.pin,
                household_id=parent.household_id,
            )
        except ValueError as exc:
            status_code = 404 if str(exc).startswith("Unknown learner") else 422
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    return router
