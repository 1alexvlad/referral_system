from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from app.models import User
from .dao import UserDAO
from .schemas import SUserRegister, SUserLogin
from .auth import get_current_user, get_password_hash, authenticate_user, create_access_token
from app.config import settings
from referral_code.dao import CodeDAO



router = APIRouter(
    prefix='/auth',
    tags=['Пользователь']
)



@router.post('/token')
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        email: EmailStr = form_data.username
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат email в поле username"
        )

    user = await authenticate_user(email, form_data.password) 
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль"
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    response.set_cookie('user_access_token', access_token, httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}



@router.post('/register')
async def register_user(response: Response, user_data: SUserRegister):
    existing_user = await UserDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        raise HTTPException(status_code=409, detail='Email уже существует')
    
    hashed_password = get_password_hash(user_data.password)
    
    user = await UserDAO.add(email=user_data.email, password=hashed_password)
    if not user:
        raise HTTPException(status_code=500, detail='Ошибка при создании пользователя')
    
    if user_data.referral_code:
        referral_code = await CodeDAO.find_one_or_none(code=user_data.referral_code)
        if not referral_code or referral_code.expiration_date < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Недействительный или истекший реферальный код"
            )

        await UserDAO.update(user.id, code_id=referral_code.id)
    
    access_token = create_access_token({'sub': str(user.id)})
    response.set_cookie('user_access_token', access_token, httponly=True)
    return 'Пользователь зарегистрировался'


@router.post('/login')
async def login_user(response: Response, user_data: SUserLogin):
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")
    access_token = create_access_token({'sub': str(user.id)})

    response.set_cookie('user_access_token', access_token, httponly=True)
    return access_token


@router.post('/logout')
async def logout_user(response: Response):
    response.delete_cookie('user_access_token')
    return 'Пользователь вышел из системы'


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
