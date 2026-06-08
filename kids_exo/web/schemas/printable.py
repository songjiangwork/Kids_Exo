from pydantic import BaseModel, Field

from kids_exo.web.schemas.base import FromDomainModel


class PrintableWorksheetResponse(FromDomainModel):
    identifier: str
    subject: str
    category: str
    title: str


class PrintablePdfRequest(BaseModel):
    preset_id: str
    seed: int | None = None
    include_warmup: bool = True
    page_count: int = Field(default=1, ge=1, le=20)
    question_count: int | None = Field(default=None, ge=1, le=500)
