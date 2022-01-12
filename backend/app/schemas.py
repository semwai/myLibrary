from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    password: str


class UserMe(BaseModel):
    username: str


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


class BookInfo(BaseModel):
    name: str
    author: str | None
    pages: int
