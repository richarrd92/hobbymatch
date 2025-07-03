import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from models.base import Base

# Tag model representing a label that can be associated with hobbies
class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)

    # Relationship to HobbyTag association table
    hobby_tags = relationship("HobbyTag", cascade="all, delete", back_populates="tag")
