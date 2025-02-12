from typing import List
from pydantic import BaseModel


class SReferralLink(BaseModel):
    expiration_date: int

class ReferralSchema(BaseModel):
    id: int
    email: str