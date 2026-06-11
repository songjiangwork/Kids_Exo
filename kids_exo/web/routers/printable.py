from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from kids_exo.catalog import list_preset_entries
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.printable import generate_printable_pdf
from kids_exo.web.auth import LocalSessionStore, require_parent_account
from kids_exo.web.schemas import PrintablePdfRequest, PrintableWorksheetResponse


def create_router(
    repository: PracticeRepository | None,
    session_store: LocalSessionStore,
) -> APIRouter:
    router = APIRouter(dependencies=[Depends(require_parent_account(repository, session_store))])

    @router.get(
        "/api/printable-worksheets",
        response_model=list[PrintableWorksheetResponse],
    )
    def list_printable_worksheets() -> list[PrintableWorksheetResponse]:
        return [
            PrintableWorksheetResponse.model_validate(entry)
            for entry in list_preset_entries()
        ]

    @router.post("/api/printable-worksheets/pdf")
    def download_printable_pdf(request: PrintablePdfRequest) -> Response:
        try:
            pdf = generate_printable_pdf(
                request.preset_id,
                seed=request.seed,
                include_warmup=request.include_warmup,
                page_count=request.page_count,
                question_count=request.question_count,
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return Response(
            content=pdf.content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{pdf.filename}"',
            },
        )

    return router
