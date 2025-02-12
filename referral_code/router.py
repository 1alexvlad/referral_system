import random
import string
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr

from .dao import CodeDAO
from app.dao import UserDAO
from app.dependencies import get_current
from app.models import User
from .schemas import SReferralLink, ReferralSchema


router = APIRouter(
    prefix="/referral",
    tags=["Referral"]
)

def generate_referral_code(length: int = 20) -> str:
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))


@router.post('/create-link', name="Создание реферальной ссылке")
async def create_referral_code(code_data: SReferralLink, current_user: User = Depends(get_current)):
    active_code = await CodeDAO.find_active_code_by_user(current_user.id)
    if active_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У вас уже есть активный реферальный код"
        )
   
    unique_code = generate_referral_code()

    expiration_date = code_data.expiration_date

    if expiration_date < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Число не может быть отрицательным или равно 0')

    if expiration_date > 30:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Срок действия реферального кода не может превышать 30 дней")
    
    expiration_date = datetime.now(timezone.utc) + timedelta(days=expiration_date)

    expiration_date = expiration_date.replace(tzinfo=None)

    new_code = await CodeDAO.add(
        code=unique_code,
        expiration_date=expiration_date,
    )

    return {"message": new_code.code}



@router.get('/show_my_link', name="Показать мою реферальную ссылку")
async def show_my_link(current_user: User = Depends(get_current)):
    active_code = await CodeDAO.find_active_code_by_user(current_user.id)
    if not active_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У вас нет реферального кода"
        )
    return {"Ваша реферальная ссылка": active_code.code}


@router.delete('/delete-link', name="Удалить реферальную ссылку")
async def delete_link(current_user: User = Depends(get_current)):
    active_code = await CodeDAO.find_active_code_by_user(current_user.id)
    if not active_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У вас нет реферального кода"
        )
    deleted = await CodeDAO.delete(code_id=active_code.id)
    return {'message': "Реферальный код успешно удален"}


@router.get("/get-code-by-email", name="Получения реферального кода по email адресу реферера")
async def get_referral_code_by_email(email: EmailStr):
    referral_code = await CodeDAO.find_active_code_by_email(email)
    if not referral_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Реферальный код не найден"
        )
    return {"Реферальный код": referral_code.code}

@router.get("/{referral_link_id}", name='Получение информации о рефералах по ID реферальной ссылки')
async def get_referrals(referral_link_id: int) -> list[ReferralSchema]:
    # Ищем реферальную ссылку по ID
    referral_link = await CodeDAO.find_one_or_none(id=referral_link_id)
    if not referral_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Реферальная ссылка не найдена"
        )

    users = await UserDAO.find_all(code_id=referral_link_id)
    return users