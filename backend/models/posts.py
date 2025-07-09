from sqlalchemy import Column, ForeignKey, Text, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime
from models.base import Base
import enum


# Enum for different reaction types
class ReactionType(str, enum.Enum):
    like = "like"
    love = "love"
    fire = "fire"
    laugh = "laugh"
    sad = "sad"

# Represents a post created by a user
class UserPost(Base):
    __tablename__ = "user_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    image_public_id = Column(String, nullable=True)
    hobby_id = Column(UUID(as_uuid=True), ForeignKey("hobbies.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="posts")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")
    reactions = relationship("PostReaction", back_populates="post", cascade="all, delete-orphan")

# Represents a comment on a user post
class PostComment(Base):
    __tablename__ = "post_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_posts.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    post = relationship("UserPost", back_populates="comments")
    user = relationship("User", back_populates="comments")

# Represents a reaction (like, love, etc.) on a user post
class PostReaction(Base):
    __tablename__ = "post_reactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("user_posts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(Enum(ReactionType, name="reaction_type"), nullable=False)

    # Relationships
    post = relationship("UserPost", back_populates="reactions")
    user = relationship("User", back_populates="reactions")
