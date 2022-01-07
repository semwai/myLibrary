import os

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from ..models import User as UserModel
from ..schemas import User, UserRegister, HTTPError, UserMe
from ..session import session

user_router = APIRouter()

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
@user_router.post('/login', tags=['User'])
def login(user_in: User, authorize: AuthJWT = Depends()):
    query = session.query(UserModel).filter_by(name=user_in.username)
    if query.count() == 0:
        raise HTTPException(status_code=401, detail="Bad username or password")
    db_user = query.one()
    if not verify_password(user_in.password, db_user.password):
        raise HTTPException(status_code=401, detail="Bad username or password")

    # subject identifier for who this token is for example id or username from database
    access_token = authorize.create_access_token(subject=user_in.username)
    return {"access_token": access_token}


@user_router.post('/logout', tags=['User'])
def login(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    return "ok"


@user_router.post('/register', tags=['User'], responses={
        200: {"model": User},
        409: {
            "model": HTTPError,
            "description": "User already exist",
        },
    }, )
def register(user_in: UserRegister):
    hashed_password = pwd_context.hash(user_in.password)
    new_user = UserModel(name=user_in.username, email=user_in.mail, password=hashed_password)
    session.add(new_user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="User already exist")
    return user_in


# protect endpoint with function jwt_required(), which requires
# a valid access token in the request headers to access.
@user_router.get('/user', tags=['User'], responses={
        200: {"model": UserMe},
        401: {
            "model": HTTPError,
            "description": "Missing Authorization Header",
        },
        422: {
            "model": HTTPError,
            "description": "Signature fail",
        },
    }, )
def user(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    return {"user": current_user}
