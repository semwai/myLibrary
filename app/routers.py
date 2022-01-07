import sqlalchemy.exc
from fastapi import APIRouter
import io
import os

from typing import Optional, Dict
from fastapi import File, UploadFile, BackgroundTasks, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.mysql import insert
import fitz

from dotenv import load_dotenv

from .models import Page, Book, User as UserModel, users_progress
from .schemas import User, UserRegister, HTTPError, UserMe
from .session import session

router = APIRouter()

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# in production you can use Settings management
# from pydantic to get secret key from .env
class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv('KEY')


# callback to get your configuration
@AuthJWT.load_config
def get_config():
    return Settings()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token to use authorization
# later in endpoint protected
@router.post('/login', tags=['User'])
def login(user: User, authorize: AuthJWT = Depends()):
    query = session.query(UserModel).filter_by(name=user.username)
    if query.count() == 0:
        raise HTTPException(status_code=401, detail="Bad username or password")
    db_user = query.one()
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Bad username or password")

    # subject identifier for who this token is for example id or username from database
    access_token = authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}


@router.post('/logout', tags=['User'])
def login(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    return "ok"


@router.post('/register', tags=['User'], responses={
        200: {"model": User},
        409: {
            "model": HTTPError,
            "description": "User already exist",
        },
    },)
def register(user: UserRegister):
    hashed_password = pwd_context.hash(user.password)
    new_user = UserModel(name=user.username, email=user.mail, password=hashed_password)
    session.add(new_user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="User already exist")
    return user


# protect endpoint with function jwt_required(), which requires
# a valid access token in the request headers to access.
@router.get('/user', tags=['User'], responses={
        200: {"model": UserMe},
        401: {
            "model": HTTPError,
            "description": "Missing Authorization Header",
        },
        422: {
            "model": HTTPError,
            "description": "Signature fail",
        },
    },)
def user(authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    current_user = authorize.get_jwt_subject()
    return {"user": current_user}


@router.get("/book/{book_id}/{page}", tags=['Books'], response_class=StreamingResponse)
def get_page(book_id: int, page: int = 0, authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    res = session.query(Page).filter_by(book_id=book_id, number=page).first()
    if res is None:
        return HTTPException(status_code=404, detail="Page not found")
    current_user = authorize.get_jwt_subject()
    user = session.query(UserModel).filter_by(name=current_user).one()

    ins = insert(users_progress).values(user_id=user.id, book_id=book_id, page=page).on_duplicate_key_update(page=page)
    session.execute(ins)
    session.commit()
    print(user.books)
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


@router.post("/book", tags=['Books'])
async def post_book(background_tasks: BackgroundTasks,
                    name: str, author: Optional[str] = None,
                    file: UploadFile = File(...),
                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    background_tasks.add_task(upload_book, name=name, author=author, file=file)
    return {'name': name, 'author': author}


@router.get("/")
def read_root():
    return {"Hello": "World"}
