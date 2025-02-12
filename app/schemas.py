from typing import Optional
from pydantic import BaseModel, EmailStr


class SUserRegister(BaseModel):
    email: EmailStr
    password: str
    referral_code: Optional[str] = None

class SUserLogin(BaseModel):
    email: EmailStr
    password: str