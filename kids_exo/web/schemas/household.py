from datetime import datetime

from pydantic import BaseModel


class HouseholdStudentSummaryResponse(BaseModel):
    id: int
    nickname: str
    avatar_key: str
    student_login_enabled: bool
    student_code: str | None = None


class HouseholdSummaryResponse(BaseModel):
    id: int
    name: str
    household_code: str


class HouseholdStudentsResponse(BaseModel):
    household: HouseholdSummaryResponse
    students: tuple[HouseholdStudentSummaryResponse, ...]


class PinRequest(BaseModel):
    pin: str


class ParentPinChangeRequest(BaseModel):
    current_pin: str
    new_pin: str


class StudentDirectLoginRequest(BaseModel):
    household_code: str
    student_code: str
    pin: str


class ParentUnlockStatusResponse(BaseModel):
    unlocked: bool
    expires_at: datetime | None = None


class StudentLoginResponse(BaseModel):
    student: HouseholdStudentSummaryResponse


class StudentAuthMeResponse(BaseModel):
    student: HouseholdStudentSummaryResponse | None


class StudentDirectLoginResponse(BaseModel):
    student: HouseholdStudentSummaryResponse
    redirect_to: str


class StudentDirectAuthMeResponse(BaseModel):
    student: HouseholdStudentSummaryResponse
    household: dict[str, int | str]
