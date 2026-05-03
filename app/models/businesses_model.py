from sqlalchemy import Column, ForeignKey, String, Boolean, TIMESTAMP, func, text, DateTime, Enum
from datetime import datetime
from sqlalchemy.orm import relationship
from ..database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..schemas.businesses_schema import BrandColor, BrandTone, IndustryType


class Business(Base):
    __tablename__ = "businesses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    business_name = Column(String(255), nullable=True)
    industry = Column(Enum(IndustryType), nullable=True)
    location = Column(String(255), nullable=True)
    services = Column(String(500), nullable=True)
    tone = Column(Enum(BrandTone), nullable=True)
    brand_color = Column(Enum(BrandColor), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="businesses")
    