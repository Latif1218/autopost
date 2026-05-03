from sqlalchemy import Column, String, Boolean, TIMESTAMP, text, DateTime, Enum
from datetime import datetime
from sqlalchemy.orm import relationship
from ..database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum as PyEnum



class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"
    TUTOR = "tutor"


class UserPlan(str, PyEnum):
    ESSENTIAL = "essential"
    STARTER = "starter"
    PRO = "pro"
    PREMIUM = "premium"
    


class UserStatus(str, PyEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    supabase_uid = Column(String(255), unique=True, nullable=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    plan = Column(Enum(UserPlan), default=UserPlan.ESSENTIAL, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    

    reset_code = relationship("PasswordResetCode", back_populates="user")
    businesses = relationship("Business", back_populates="user")
    subscription = relationship("Subscription", back_populates="user", uselist=False)