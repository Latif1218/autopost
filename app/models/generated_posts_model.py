import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base

class GeneratedPost(Base):
    __tablename__ = "generated_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    platform = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    media_urls = Column(Text, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=True)
    n8n_execution_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    queue_id = Column(UUID(as_uuid=True), ForeignKey("scheduled_post_queue.id"), nullable=True)

    user = relationship("User", back_populates="generated_posts")
    queue = relationship("ScheduledPostQueue", back_populates="generated_posts")