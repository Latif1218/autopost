import uuid
from sqlalchemy import Column, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base

class ScheduledPostQueue(Base):
    __tablename__ = "scheduled_post_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    email = Column(Text, nullable=True)
    plan_type = Column(Text, nullable=True)
    business_name = Column(Text, nullable=True)
    industry = Column(Text, nullable=True)
    location = Column(Text, nullable=True)
    services = Column(Text, nullable=True)
    tone = Column(Text, nullable=True)
    brand_color = Column(Text, nullable=True)
    scheduled_date = Column(Text, nullable=True)
    scheduled_time = Column(Text, nullable=True)
    post_number = Column(Numeric, nullable=True)
    generation_status = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="scheduled_post_queues")
    generated_posts = relationship("GeneratedPost", back_populates="queue")