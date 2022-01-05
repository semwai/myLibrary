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
from fastapi.openapi.utils import get_openapi
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
import fitz

from models import Page, Base, Book
from schemas import User

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
def login(user: User, authorize: AuthJWT = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401,detail="Bad username or password")

    # subject identifier for who this token is for example id or username from database
    access_token = authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}


# protect endpoint with function jwt_required(), which requires
# a valid access token in the request headers to access.
@app.get('/user', operation_id="authorize")
def user(authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    current_user = authorize.get_jwt_subject()
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


@app.post("/book", operation_id="authorize")
async def post_book(background_tasks: BackgroundTasks,
                    name: str, author: Optional[str] = None,
                    file: UploadFile = File(...),
                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    background_tasks.add_task(upload_book, name=name, author=author, file=file)
    return {'name': name, 'author': author}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="myLibrary",
        version="0.0.1",
        description="",
        routes=app.routes,
    )

    # Custom documentation fastapi-jwt-auth
    headers = {
        "name": "Authorization",
        "in": "header",
        "required": True,
        "schema": {
            "title": "Authorization",
            "type": "string"
        },
    }

    # Get routes from index 4 because before that fastapi define router for /openapi.json, /redoc, /docs, etc
    # Get all router where operation_id is authorized
    router_authorize = [route for route in app.routes[4:] if route.operation_id == "authorize"]

    for route in router_authorize:
        method = list(route.methods)[0].lower()
        try:
            # If the router has another parameter
            openapi_schema["paths"][route.path][method]['parameters'].append(headers)
        except Exception:
            # If the router doesn't have a parameter
            openapi_schema["paths"][route.path][method].update({"parameters": [headers]})

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True, debug=True, workers=3, use_colors=True)
