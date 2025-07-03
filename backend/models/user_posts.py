import uuid
from sqlalchemy import Column, ForeignKey, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base

# UserPost model representing user-generated posts linked to hobbies
class UserPost(Base):
    __tablename__ = "user_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)

    # Hobby associated with the post
    hobby_id = Column(UUID(as_uuid=True), ForeignKey("hobbies.id", ondelete="SET NULL"))

    # Relationships
    user = relationship("User")
    hobby = relationship("Hobby")
    reactions = relationship("PostReaction", cascade="all, delete", back_populates="post")
    comments = relationship("PostComment", cascade="all, delete", back_populates="post")
