from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from models import UserPost, PostComment, PostReaction, User
from schemas import PostRead, CommentCreate, CommentRead, PostReactionCreate
from utils.current_user import get_current_user
from database import get_db
from logger import logger
from utils.cloudinary import upload_photo_to_cloudinary

router = APIRouter(prefix="/posts", tags=["Posts"])

# Create a new post
@router.post("/", response_model=PostRead)
async def create_post(
    content: str = Form(...),
    hobby_id: Optional[UUID] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    image_url = None
    image_public_id = None
    file_bytes = None

    # Check if a file was uploaded
    if file:
        file_bytes = await file.read()
        upload_result = await upload_photo_to_cloudinary(file_bytes, user.id, usage="post")
        image_url = upload_result["url"]
        image_public_id = upload_result["public_id"]

    now = datetime.utcnow()

    # TODO: Temporary post expiry for testing
    expires_at = now + timedelta(seconds=60) 
    # expires_at = now + timedelta(hours=24)

    post = UserPost(
        id=uuid4(),
        user_id=user.id,
        content=content,
        hobby_id=hobby_id,
        image_url=image_url,
        image_public_id=image_public_id,
        created_at=now,
        expires_at=expires_at,
    )

    db.add(post)
    await db.commit()
    await db.refresh(post)

    return PostRead(
        id=post.id,
        user_id=user.id,
        content=post.content,
        image_url=post.image_url,
        hobby_id=post.hobby_id,
        created_at=post.created_at,
        expires_at=post.expires_at,
        name=user.name,
        profile_pic_url=user.profile_pic_url,
        reaction_counts={},
        comment_count=0,
    )

# Get public feed with posts, reactions, and comments
@router.get("/feed", response_model=List[PostRead])
async def get_public_feed(db: AsyncSession = Depends(get_db)):
    """
    Get recent posts from all non-private users,
    including reaction counts and comments with user info.
    """
    stmt = (
        select(UserPost, User)
        .join(User, User.id == UserPost.user_id)
        .where(User.is_private == False)
        .order_by(UserPost.created_at.desc())
    )
    results = (await db.execute(stmt)).all()

    feed = []
    for post, user in results:
        # Reaction counts grouped by type
        reaction_stmt = (
            select(PostReaction.type, func.count())
            .where(PostReaction.post_id == post.id)
            .group_by(PostReaction.type)
        )
        reactions = await db.execute(reaction_stmt)

        # Comments with user info
        comment_stmt = (
            select(PostComment, User)
            .join(User, User.id == PostComment.user_id)
            .where(PostComment.post_id == post.id)
            .order_by(PostComment.created_at.asc())
        )
        comments_result = await db.execute(comment_stmt)
        comment_rows = comments_result.all()  # List of tuples (PostComment, User)

        reaction_counts = {r[0].value: r[1] for r in reactions}
        comment_list = [
            CommentRead(
                id=c.id,
                post_id=c.post_id,
                user_id=c.user_id,
                content=c.content,
                created_at=c.created_at,
                user_name=u.name,
                profile_pic_url=u.profile_pic_url,
            )
            for c, u in comment_rows
        ]

        feed.append(PostRead(
            id=post.id,
            user_id=user.id,
            content=post.content,
            image_url=post.image_url,
            hobby_id=post.hobby_id,
            created_at=post.created_at,
            expires_at=post.expires_at,
            name=user.name,
            profile_pic_url=user.profile_pic_url,
            reaction_counts=reaction_counts,
            comment_count=len(comment_list),
            comments=comment_list
        ))

    return feed

# Get a single post by ID with reactions and comments
@router.get("/{post_id}", response_model=PostRead)
async def get_single_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(UserPost, User).join(User).where(UserPost.id == post_id)
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")

    post, user = row

    # Reaction counts grouped by type
    reaction_stmt = (
        select(PostReaction.type, func.count())
        .where(PostReaction.post_id == post.id)
        .group_by(PostReaction.type)
    )

    # Comments with user info
    comment_stmt = (
        select(PostComment, User)
        .join(User, User.id == PostComment.user_id)
        .where(PostComment.post_id == post.id)
        .order_by(PostComment.created_at.asc())
    )

    reactions = await db.execute(reaction_stmt)
    comments = await db.execute(comment_stmt)

    reaction_counts = {r[0].value: r[1] for r in reactions}
    comment_list = [
        CommentRead(
            id=c.id,
            post_id=c.post_id,
            user_id=c.user_id,
            content=c.content,
            created_at=c.created_at,
            user_name=u.name,
            profile_pic_url=u.profile_pic_url
        )
        for c, u in comments
    ]

    return PostRead(
        id=post.id,
        user_id=user.id,
        content=post.content,
        image_url=post.image_url,
        hobby_id=post.hobby_id,
        created_at=post.created_at,
        expires_at=post.expires_at,
        name=user.name,
        profile_pic_url=user.profile_pic_url,
        reaction_counts=reaction_counts,
        comment_count=len(comment_list),
        comments=comment_list
    )

# Add a comment to a post
@router.post("/{post_id}/comments", response_model=CommentRead)
async def add_comment(
    post_id: UUID,
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    
    new_comment = PostComment(
        id=uuid4(),
        post_id=post_id,
        user_id=user.id,
        content=comment.content,
        created_at=datetime.utcnow()
    )

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    return CommentRead(
        id=new_comment.id,
        post_id=new_comment.post_id,
        user_id=user.id,
        content=new_comment.content,
        created_at=new_comment.created_at,
        user_name=user.name,
        profile_pic_url=user.profile_pic_url
    )

# Add or update a reaction to a post
@router.post("/{post_id}/reactions")
async def add_reaction(
    post_id: UUID,
    reaction: PostReactionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    
    # Remove existing reaction by the same user on the post
    await db.execute(
        delete(PostReaction).where(
            (PostReaction.post_id == post_id) &
            (PostReaction.user_id == user.id)
        )
    )

    new_reaction = PostReaction(
        id=uuid4(),
        post_id=post_id,
        user_id=user.id,
        type=reaction.type
    )

    db.add(new_reaction)
    await db.commit()
    return {"status": "ok", "type": reaction.type}