from .database import async_session_maker
from .models import User

from sqlalchemy import select, insert, update

class UserDAO:
        
    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as sesion:
            query = select(User).filter_by(**filter_by)
            result = await sesion.execute(query)
            return result.scalar_one_or_none() 
        

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(User).values(**data).returning(User)
            result = await session.execute(query)
            await session.commit()
            return result.scalar_one()

            
    @classmethod
    async def update(cls, user_id: int, **data):
        async with async_session_maker() as session:
            query = update(User).where(User.id == user_id).values(**data)
            await session.execute(query)
            await session.commit()
    
    @classmethod
    async def find_all(cls, code_id: int):
        async with async_session_maker() as session:
            query = select(User).where(User.code_id == code_id)
            result = await session.execute(query)
            return result.scalars().all()
