from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

# Enum for different types of reactions
class ReactionType(str, Enum):
    like = "like"
    love = "love"
    fire = "fire"
    laugh = "laugh"
    sad = "sad"

# Schema for creating a post
class PostCreate(BaseModel):
    content: str
    hobby_id: Optional[UUID] = None

# Schema for adding a reaction to a post
class PostReactionCreate(BaseModel):
    type: ReactionType

# Schema for creating a comment
class CommentCreate(BaseModel):
    content: str

# Schema for reading a comment (with user info)
class CommentRead(BaseModel):
    id: UUID
    post_id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    user_name: str
    profile_pic_url: Optional[str]

    class Config:
        from_attributes = True

# Schema for reading a post (with optional image, comments, and reactions)
class PostRead(BaseModel):
    id: UUID
    user_id: UUID
    content: str
    image_url: Optional[str]
    hobby_id: Optional[UUID]
    created_at: datetime
    expires_at: datetime
    name: str # Author name
    profile_pic_url: Optional[str]
    reaction_counts: Dict[str, int] = {} # e.g., {"like": 3, "fire": 1}
    comment_count: int
    comments: Optional[List[CommentRead]] = None

    class Config:
        from_attributes = True
