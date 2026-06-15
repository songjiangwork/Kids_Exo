from fastapi import APIRouter, Depends, HTTPException, Request

from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.auth import (
    LocalSessionStore,
    ParentContext,
    StudentAccessContext,
    require_parent_unlock,
    require_parent_context,
    require_student_access,
    SESSION_COOKIE_NAME,
)
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
    router = APIRouter()
    parent_unlock = require_parent_unlock(repository, session_store)
    parent_context = require_parent_context(repository, session_store)
    student_access = require_student_access(repository, session_store)

    @router.post(
        "/api/learners/{learner_id}/assignments",
        response_model=AssignmentResponse,
        status_code=201,
    )
    def create_assignment(
        learner_id: int,
        request: AssignmentCreateRequest,
        access: StudentAccessContext = Depends(student_access),
    ) -> AssignmentResponse:
        storage = require_repository(repository)
        try:
            _validated_items(request.items)
            source_type = "parent_assigned" if access.parent_unlocked else "learner_added"
            created_by_role = "parent" if access.parent_unlocked else "learner"
            assignment = storage.create_assignment(
                learner_id,
                title=request.title,
                description=request.description,
                source_type=source_type,
                due_at=request.due_at,
                created_by_role=created_by_role,
                items=[item.model_dump() for item in request.items],
                household_id=access.household_id,
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
        access: StudentAccessContext = Depends(student_access),
    ) -> list[AssignmentResponse]:
        storage = require_repository(repository)
        try:
            return [
                assignment_response(assignment)
                for assignment in storage.list_assignments_for_learner(
                    learner_id,
                    status=status,
                    household_id=access.household_id,
                )
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
        fastapi_request: Request,
    ) -> AssignmentItemStartResponse:
        storage = require_repository(repository)
        try:
            token = fastapi_request.cookies.get(SESSION_COOKIE_NAME)
            state = session_store.get_state(token)
            if state is not None and state.session_type == "student":
                if state.household_id is None or state.active_student_id is None:
                    raise PermissionError("Student access required")
                household_id = state.household_id
                active_student_id = state.active_student_id
                parent_unlocked = False
            else:
                parent = parent_context(fastapi_request)
                household_id = parent.household_id
                active_student_id = session_store.active_student_id(token)
                parent_unlocked = session_store.is_parent_unlocked(token)
            assignment = storage.get_assignment(assignment_id, household_id=household_id)
            if (
                not parent_unlocked
                and active_student_id != assignment.learner_id
            ):
                raise PermissionError("Student access required")
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
            result = storage.start_assignment_item(
                assignment_id,
                item_id,
                snapshot,
                household_id=household_id,
            )
        except ValueError as exc:
            status_code = 404 if str(exc).startswith("Unknown assignment") else 422
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
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
    def archive_assignment(
        assignment_id: int,
        parent: ParentContext = Depends(parent_unlock),
    ) -> AssignmentResponse:
        storage = require_repository(repository)
        try:
            return assignment_response(
                storage.archive_assignment(assignment_id, household_id=parent.household_id)
            )
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
