import uuid
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
from models import UserRole
from sqlalchemy import Enum

# User model representing a platform user with profile and role info
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firebase_uid = Column(String(128), unique=True, nullable=False) # Firebase Authentication UID (unique)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    age = Column(Integer)
    bio = Column(Text)
    profile_pic_url = Column(Text)
    profile_pic_public_id = Column(String, nullable=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id", ondelete="SET NULL"))
    role = Column(Enum(UserRole, name="user_role"), default=UserRole.user)
    is_verified = Column(Boolean, default=False)
    verification_method = Column(String(50))
    is_private = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    location = relationship("Location", backref="users")
    user_hobbies = relationship("UserHobby", cascade="all, delete", back_populates="user")
    matches_initiated = relationship("Match", foreign_keys="Match.initiator_id", back_populates="initiator")
    matches_received = relationship("Match", foreign_keys="Match.receiver_id", back_populates="receiver")
    posts = relationship("UserPost", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("PostComment", back_populates="user", cascade="all, delete-orphan")
    reactions = relationship("PostReaction", back_populates="user", cascade="all, delete-orphan")