import os
from datetime import timedelta

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from redis import Redis
from sqlalchemy.orm import Session

from ..models import User as UserModel
from ..schemas import User, UserRegister, HTTPError, UserMe
from ..session import get_db

user_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# in production you can use Settings management
# from pydantic to get secret key from .env
class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv('KEY')
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}
    authjwt_access_token_expires: int = timedelta(days=15)
    authjwt_refresh_token_expires: int = timedelta(days=30)


settings = Settings()
redis_conn = Redis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')), db=0, decode_responses=True)


# callback to get your configuration
@AuthJWT.load_config
def get_config():
    return Settings()


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    entry = redis_conn.get(jti)
    return entry and entry == 'true'


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token to use authorization
# later in endpoint protected
@user_router.post('/login', tags=['User'])
def login(user_in: User, authorize: AuthJWT = Depends(), session: Session = Depends(get_db)):
    query = session.query(UserModel).filter_by(name=user_in.username)
    if query.count() == 0:
        raise HTTPException(status_code=401, detail="Bad username or password")
    db_user = query.one()
    if not verify_password(user_in.password, db_user.password):
        raise HTTPException(status_code=401, detail="Bad username or password")

    # subject identifier for who this token is for example id or username from database
    access_token = authorize.create_access_token(subject=user_in.username, headers={'id': db_user.id})
    refresh_token = authorize.create_refresh_token(subject=user_in.username, headers={'id': db_user.id})
    return {'access_token': access_token, 'refresh_token': refresh_token}


@user_router.post('/refresh', tags=['User'])
def refresh(authorize: AuthJWT = Depends(), session: Session = Depends(get_db)):
    """
    The jwt_refresh_token_required() function insures a valid refresh
    token is present in the request before running any code below that function.
    we can use the get_jwt_subject() function to get the subject of the refresh
    token, and use the create_access_token() function again to make a new access token
    """
    authorize.jwt_refresh_token_required()

    current_user = authorize.get_jwt_subject()

    db_user = session.query(UserModel).filter_by(name=current_user).one()

    new_access_token = authorize.create_access_token(subject=current_user, headers={'id': db_user.id})
    return {"access_token": new_access_token}


@user_router.post('/logout', tags=['User'])
def login(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    jti = authorize.get_raw_jwt()['jti']
    redis_conn.setex(jti, settings.authjwt_access_token_expires, 'true')
    return {"detail": "Access token has been revoke"}


@user_router.post('/register', tags=['User'], responses={
        200: {"model": User},
        409: {
            "model": HTTPError,
            "description": "User already exist",
        },
    }, )
def register(user_in: UserRegister, session: Session = Depends(get_db)):
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
    return {'user': current_user, 'id': authorize.get_unverified_jwt_headers()['id']}
