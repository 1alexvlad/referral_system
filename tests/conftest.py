from datetime import datetime
import pytest
import os

os.environ["MODE"] = "TEST"

from app.database import Base, async_session_maker, engine
from app.config import settings
from app.models import User
from referral_code.models import ReferralLink
from app.main import app as fastapi_app

from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:

        expiration_date = datetime.strptime("2025-02-20", "%Y-%m-%d")

        referral_code_1 = ReferralLink(code="TESTCODE1", expiration_date=expiration_date)
        referral_code_2 = ReferralLink(code="TESTCODE2", expiration_date=expiration_date)


        session.add(referral_code_1)
        session.add(referral_code_2)
        await session.commit()

        hashed_password_1 = pwd_context.hash("password1")
        hashed_password_2 = pwd_context.hash("password2")
        hashed_password_3 = pwd_context.hash("password3")


        user_1 = User(email="test1@example.com", password=hashed_password_1, code_id=referral_code_1.id)
        user_2 = User(email="test2@example.com", password=hashed_password_2, code_id=referral_code_2.id)
        user_3 = User(email="test3@example.com", password=hashed_password_3, code_id=None)

        session.add(user_1)
        session.add(user_2)
        session.add(user_3)
        await session.commit()

@pytest.fixture(scope="session")
async def async_session():
    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
async def session():
    async with async_session_maker() as session:
        yield session