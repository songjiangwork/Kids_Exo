from fastapi import APIRouter, Depends, HTTPException

from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.auth import LocalSessionStore, require_parent_account
from kids_exo.web.dependencies import create_snapshot, require_repository
from kids_exo.web.mappers import assignment_item_response, assignment_response
from kids_exo.web.schemas import (
    AssignmentCreateRequest,
    AssignmentItemCreateRequest,
    AssignmentItemStartResponse,
    AssignmentResponse,
    PracticePreviewRequest,
)


def create_router(
    repository: PracticeRepository | None,
    session_store: LocalSessionStore,
) -> APIRouter:
    router = APIRouter(dependencies=[Depends(require_parent_account(repository, session_store))])

    @router.post(
        "/api/learners/{learner_id}/assignments",
        response_model=AssignmentResponse,
        status_code=201,
    )
    def create_assignment(
        learner_id: int,
        request: AssignmentCreateRequest,
    ) -> AssignmentResponse:
        storage = require_repository(repository)
        try:
            _validated_items(request.items)
            assignment = storage.create_assignment(
                learner_id,
                title=request.title,
                description=request.description,
                source_type=request.source_type,
                due_at=request.due_at,
                created_by_role=request.created_by_role,
                items=[item.model_dump() for item in request.items],
            )
        except ValueError as exc:
            status_code = 404 if str(exc).startswith("Unknown learner") else 422
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc
        return assignment_response(assignment)

    @router.get(
        "/api/learners/{learner_id}/assignments",
        response_model=list[AssignmentResponse],
    )
    def list_assignments(
        learner_id: int,
        status: str | None = None,
    ) -> list[AssignmentResponse]:
        storage = require_repository(repository)
        try:
            return [
                assignment_response(assignment)
                for assignment in storage.list_assignments_for_learner(learner_id, status=status)
            ]
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.post(
        "/api/assignments/{assignment_id}/items/{item_id}/start",
        response_model=AssignmentItemStartResponse,
    )
    def start_assignment_item(
        assignment_id: int,
        item_id: int,
    ) -> AssignmentItemStartResponse:
        storage = require_repository(repository)
        try:
            assignment = storage.get_assignment(assignment_id)
            item = next((candidate for candidate in assignment.items if candidate.id == item_id), None)
            if item is None:
                raise ValueError(f"Unknown assignment item: {item_id}")
            snapshot = None
            if item.linked_session_id is None:
                snapshot = create_snapshot(
                    PracticePreviewRequest(
                        plugin=item.plugin,
                        plugin_settings=item.plugin_settings,
                        question_count=item.question_count,
                        feedback_mode=item.feedback_mode,
                        show_timer=item.show_timer,
                    )
                )
            result = storage.start_assignment_item(assignment_id, item_id, snapshot)
        except ValueError as exc:
            status_code = 404 if str(exc).startswith("Unknown assignment") else 422
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc
        token = result.practice_session.student_token
        return AssignmentItemStartResponse(
            assignment=assignment_response(result.assignment),
            item=assignment_item_response(result.item),
            student_token=token,
            student_url=f"/s/{token}",
        )

    @router.post(
        "/api/assignments/{assignment_id}/archive",
        response_model=AssignmentResponse,
    )
    def archive_assignment(assignment_id: int) -> AssignmentResponse:
        storage = require_repository(repository)
        try:
            return assignment_response(storage.archive_assignment(assignment_id))
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return router


def _validated_items(items: tuple[AssignmentItemCreateRequest, ...]) -> None:
    if not items:
        raise ValueError("Assignment must include at least one item")
    for item in items:
        if item.item_type != "practice_plugin":
            raise ValueError(f"Unsupported assignment item type: {item.item_type}")
        create_snapshot(
            PracticePreviewRequest(
                plugin=item.plugin,
                plugin_settings=item.plugin_settings,
                question_count=item.question_count,
                feedback_mode=item.feedback_mode,
                show_timer=item.show_timer,
            )
        )
