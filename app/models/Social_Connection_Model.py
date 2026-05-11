from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ..database import Base


class SocialConnection(Base):
    __tablename__ = "social_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    platform = Column(String(50), nullable=False)  # facebook, instagram etc
    account_name = Column(String(255), nullable=True)
    account_id = Column(String(255), nullable=True)

    n8n_credential_id = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True)

    connected_at = Column(
        DateTime(timezone=True),
        server_default=text("now()")
    )

    user = relationship("User", back_populates="social_connections")