import uuid
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base

# Association model linking users to their hobbies with optional ranking
class UserHobby(Base):
    __tablename__ = "user_hobbies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    hobby_id = Column(UUID(as_uuid=True), ForeignKey("hobbies.id", ondelete="CASCADE"), nullable=False)
    rank = Column(Integer)
    added_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships back to User and Hobby models
    user = relationship("User", back_populates="hobbies")
    hobby = relationship("Hobby", back_populates="user_hobbies")