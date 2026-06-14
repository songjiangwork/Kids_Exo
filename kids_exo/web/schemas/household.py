from datetime import datetime

from pydantic import BaseModel


class HouseholdStudentSummaryResponse(BaseModel):
    id: int
    nickname: str
    avatar_key: str
    student_login_enabled: bool


class HouseholdStudentsResponse(BaseModel):
    students: tuple[HouseholdStudentSummaryResponse, ...]


class PinRequest(BaseModel):
    pin: str


class ParentPinChangeRequest(BaseModel):
    current_pin: str
    new_pin: str


class ParentUnlockStatusResponse(BaseModel):
    unlocked: bool
    expires_at: datetime | None = None


class StudentLoginResponse(BaseModel):
    student: HouseholdStudentSummaryResponse


class StudentAuthMeResponse(BaseModel):
    student: HouseholdStudentSummaryResponse | None
