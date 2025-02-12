from fastapi import Depends, Request, HTTPException, status
from jose import jwt, JWTError

from datetime import datetime, timezone
from .config import settings
from .dao import UserDAO


def get_token(request: Request):
    token = request.cookies.get('user_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return token


async def get_current(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    expire: str = payload.get('exp')
    if (not expire) or (datetime.fromtimestamp(int(expire), tz=timezone.utc) < datetime.now(timezone.utc)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    user_id: str = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    user_id = int(user_id)

    user = await UserDAO.find_one_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user