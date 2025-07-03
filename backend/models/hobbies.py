import uuid
from sqlalchemy import Column, String, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
from models.enums import HobbyCategory
from sqlalchemy import Enum

# Hobby model representing a user-defined interest or activity
class Hobby(Base):
    __tablename__ = "hobbies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(Enum(HobbyCategory), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    creator = relationship("User")
    tags = relationship("HobbyTag", cascade="all, delete", back_populates="hobby")
    user_hobbies = relationship("UserHobby", cascade="all, delete", back_populates="hobby")