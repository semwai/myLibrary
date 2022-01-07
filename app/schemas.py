from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    password: str
    mail: EmailStr


class HTTPError(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "HTTPException raised."},
        }
