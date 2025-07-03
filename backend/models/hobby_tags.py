from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from models.base import Base

# Association table linking hobbies and tags (many-to-many)
class HobbyTag(Base):
    __tablename__ = "hobby_tags"

    hobby_id = Column(UUID(as_uuid=True), ForeignKey("hobbies.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    hobby = relationship("Hobby", back_populates="tags")
    tag = relationship("Tag", back_populates="hobby_tags")