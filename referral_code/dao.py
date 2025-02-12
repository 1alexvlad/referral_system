from datetime import datetime, timezone
from app.database import async_session_maker
from app.models import User
from .models import ReferralLink
from functools import lru_cache


from sqlalchemy import delete, select, insert, update

class CodeDAO:

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as sesion:
            query = select(User).filter_by(**filter_by)
            users = await sesion.execute(query)
            return users.scalars().all()

    @classmethod
    async def find_active_code_by_user(cls, user_id: int):
        async with async_session_maker() as session:
            current_time = datetime.now(timezone.utc)
            current_time = current_time.replace(tzinfo=None)

            query = select(ReferralLink).join(User).where(
                (User.id == user_id) &
                (User.code_id == ReferralLink.id) &
                (ReferralLink.expiration_date > current_time)
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()
        
    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(ReferralLink).values(**data).returning(ReferralLink)
            result = await session.execute(query)
            await session.commit()
            return result.scalar_one()
    
    @classmethod
    async def delete(cls, code_id: int) -> bool:
        async with async_session_maker() as session:
            stmt = update(User).where(User.code_id == code_id).values(code_id=None)
            await session.execute(stmt)

            stmt = delete(ReferralLink).where(ReferralLink.id == code_id)
            result = await session.execute(stmt)
            await session.commit()
    
    @classmethod
    @lru_cache(maxsize=30)
    async def find_active_code_by_email(cls, email: str):
        async with async_session_maker() as session:
            user_query = select(User).where(User.email == email)
            user_result = await session.execute(user_query)
            user = user_result.scalar_one_or_none()

            if not user:
                return None
            
            current_time = datetime.now(timezone.utc).replace(tzinfo=None)

            code_query = select(ReferralLink).where(
                (ReferralLink.id == user.code_id) &  
                (ReferralLink.expiration_date > current_time)
            )

            code_result = await session.execute(code_query)
            return code_result.scalar_one_or_none()

    
    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as sesion:
            query = select(ReferralLink).filter_by(**filter_by)
            result = await sesion.execute(query)
            return result.scalar_one_or_none() 