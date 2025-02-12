from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base
from referral_code.models import ReferralLink


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    code_id = Column(Integer, ForeignKey('referral_link.id'), nullable=True) 

    code = relationship('ReferralLink', back_populates='users') 