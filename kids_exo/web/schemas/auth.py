from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class AccountResponse(BaseModel):
    id: int
    email: str
    display_name: str
    active: bool


class AuthMeResponse(BaseModel):
    account: AccountResponse | None
