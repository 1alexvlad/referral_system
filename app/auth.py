from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status
from passlib.context import CryptContext
from pydantic import EmailStr
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer


from .dao import UserDAO
from .config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token') 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def authenticate_user(email: EmailStr, password: str):
    user = await UserDAO.find_one_or_none(email=email)
    if not user:
        return None 
    if not verify_password(password, user.password):
        return None
    return user

async def get_current_user(request: Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get('user_access_token')
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await UserDAO.find_one_or_none(id=int(user_id))
    if user is None:
        raise credentials_exception
    return user