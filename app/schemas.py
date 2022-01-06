from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    password: str
    mail: EmailStr
