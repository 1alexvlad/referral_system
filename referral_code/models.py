from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class ReferralLink(Base):
    __tablename__ = "referral_link"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(255), unique=True, index=True)
    expiration_date = Column(DateTime)

    users = relationship("User", back_populates="code")
