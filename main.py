from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import uvicorn

import os
from dotenv import load_dotenv
import io

from typing import Optional
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
import fitz

from models import Page, Base, Book

load_dotenv()

engine = create_engine(os.getenv('DB_CONNECTION'), echo=False)
session = Session(engine)
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://project.test",
    "http://api.project.test"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, allow_methods=["*"],
    allow_headers=["*"], )


app = FastAPI()


class User(BaseModel):
    username: str
    password: str


# in production you can use Settings management
# from pydantic to get secret key from .env
class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv('KEY')


# callback to get your configuration
@AuthJWT.load_config
def get_config():
    return Settings()


# exception handler for authjwt
# in production, you can tweak performance using orjson response
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


# provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token to use authorization
# later in endpoint protected
@app.post('/login')
def login(user: User, Authorize: AuthJWT = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401,detail="Bad username or password")

    # subject identifier for who this token is for example id or username from database
    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}


# protect endpoint with function jwt_required(), which requires
# a valid access token in the request headers to access.
@app.get('/user')
def user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}


@app.get("/book/{book_id}/{page}", responses={200: {"content": {"image/jpeg": {}}}})
def get_page(book_id: int, page: int = 0):
    res = session.query(Page).filter_by(book_id=book_id, number=page).first()
    file = io.BytesIO()
    file.write(res.data)
    file.seek(0)
    return StreamingResponse(file, media_type="image/jpeg")


async def upload_book(name: str, file, author: Optional[str] = None):
    data = await file.read()
    db_book = Book(name=name, author=author)
    session.add(db_book)
    session.flush()
    book = fitz.open(stream=data, filetype="pdf")
    for i, page in enumerate(book):
        raw_data = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).pil_tobytes('jpeg', quality=80)
        elem = Page(number=i, book_id=db_book.id, data=raw_data)
        session.add(elem)
    session.commit()


@app.post("/book")
async def post_book(background_tasks: BackgroundTasks,
                    name: str, author: Optional[str] = None,
                    file: UploadFile = File(...),
                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    background_tasks.add_task(upload_book, name=name, author=author, file=file)
    return {'name': name, 'author': author}


if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True, debug=True, workers=3, use_colors=True)
