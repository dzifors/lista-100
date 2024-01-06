from datetime import datetime, timedelta

from bcrypt import gensalt, hashpw, checkpw
from fastapi import Cookie
from jose import JWTError, jwt
from pydantic import BaseModel

from objects.settings import SECRET_KEY
from objects.users import get_user

SECRET_KEY = SECRET_KEY if SECRET_KEY is not None else ""

HASH_ALGORITHM = "HS256"
TOKEN_EXPIRE_TIME = 60


class Token(BaseModel):
    token: str
    token_type: str


class TokenData(BaseModel):
    email: str


def get_password_hash(password: str):
    return hashpw(password.encode(), gensalt(13))


def verify_password(password_to_check: str, password_hash: str):
    return checkpw(password_to_check.encode(), password_hash.encode())


async def authenticate_user(email: str, password: str):
    user = await get_user(email)

    if not user:
        return False

    if not verify_password(password, user.auth_hash):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    encodable = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )

    encodable.update({"expire_time": expire.timestamp()})

    encoded_jwt = jwt.encode(encodable, SECRET_KEY, algorithm=HASH_ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Cookie(None)):
    if token is None:
        return False

    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[HASH_ALGORITHM])

        email = payload.get("current_user")

        if email is None:
            return False

        token_data = TokenData(email=email)

    except JWTError:
        return False

    user = await get_user(email=token_data.email)

    if user is None:
        return False

    return user
