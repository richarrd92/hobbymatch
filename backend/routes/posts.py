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
from utils.redis_ws_manager import manager

# Define API router for post-related endpoints
router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("", response_model=PostRead)
async def create_post(
    content: str = Form(...),
    hobby_id: Optional[UUID] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new post with optional content, image, and hobby association.

    Parameters:
    - content (str): Post text content.
    - hobby_id (Optional[UUID]): Related hobby.
    - file (Optional[UploadFile]): Optional image file.
    - db (AsyncSession): DB session.
    - user (User): Authenticated user.

    Returns:
    - PostRead: Serialized post with metadata.
    """

    image_url = None
    image_public_id = None
    file_bytes = None

    # If image file is provided, upload to Cloudinary
    if file:
        file_bytes = await file.read()
        upload_result = await upload_photo_to_cloudinary(file_bytes, user.id, usage="post")
        image_url = upload_result["url"]
        image_public_id = upload_result["public_id"]

    now = datetime.utcnow()
    expires_at = now + timedelta(seconds=30) # Temporary expiration 
    # expires_at = now + timedelta(hours=24)

    # Create and persist post
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

    # Add post to database
    db.add(post)
    await db.commit()
    await db.refresh(post)

    # Broadcast new post via WebSocket
    await manager.broadcast({
        "type": "new_post",
        "data": {
            "id": str(post.id),
            "content": post.content,
            "created_at": post.created_at.isoformat(),
            "expires_at": post.expires_at.isoformat(),
            "user_id": str(user.id),
            "name": user.name,
            "profile_pic_url": user.profile_pic_url,
            "image_url": post.image_url,
            "hobby_id": str(post.hobby_id) if post.hobby_id else None,
            "reaction_counts": {},
            "comment_count": 0
        }
    })

    # Return post data
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

@router.get("/feed", response_model=List[PostRead])
async def get_public_feed(db: AsyncSession = Depends(get_db)):
    """
    Fetch public posts from non-private users with reaction and comment info.

    Parameters:
    - db (AsyncSession): DB session.

    Returns:
    - List[PostRead]: Posts with reactions and comments.
    """

    # Query public posts with user info
    stmt = (
        select(UserPost, User)
        .join(User, User.id == UserPost.user_id)
        .where(User.is_private == False)
        .order_by(UserPost.created_at.desc())
    )
    results = (await db.execute(stmt)).all()

    feed = []
    for post, user in results:
        # Fetch reaction counts grouped by type
        reaction_stmt = (
            select(PostReaction.type, func.count())
            .where(PostReaction.post_id == post.id)
            .group_by(PostReaction.type)
        )
        reactions = await db.execute(reaction_stmt)

        # Fetch comments and associated user info
        comment_stmt = (
            select(PostComment, User)
            .join(User, User.id == PostComment.user_id)
            .where(PostComment.post_id == post.id)
            .order_by(PostComment.created_at.asc())
        )
        comments_result = await db.execute(comment_stmt)
        comment_rows = comments_result.all()  # List of tuples (PostComment, User)

        reaction_counts = {reaction_type.value: count for reaction_type, count in reactions}
        comment_list = [
            CommentRead(
                id=comment.id,
                post_id=comment.post_id,
                user_id=comment.user_id,
                content=comment.content,
                created_at=comment.created_at,
                user_name=comment_user.name,
                profile_pic_url=comment_user.profile_pic_url,
            )
            for comment, comment_user in comment_rows
        ]

        # Append full post object to feed
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

@router.get("/{post_id}", response_model=PostRead)
async def get_single_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Fetch a single post by its ID including comments and reactions.

    Parameters:
    - post_id (UUID): Post identifier.
    - db (AsyncSession): DB session.

    Returns:
    - PostRead: Post data with metadata.

    Raises:
    - HTTP 404 if post is not found.
    """

    # Query post with user info
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

    # Fetch comments and user info
    comment_stmt = (
        select(PostComment, User)
        .join(User, User.id == PostComment.user_id)
        .where(PostComment.post_id == post.id)
        .order_by(PostComment.created_at.asc())
    )

    reactions = await db.execute(reaction_stmt)
    comments = await db.execute(comment_stmt)

    reaction_counts = {reaction_type.value: count for reaction_type, count in reactions}
    comment_list = [
        CommentRead(
            id=comment.id,
            post_id=comment.post_id,
            user_id=comment.user_id,
            content=comment.content,
            created_at=comment.created_at,
            user_name=comment_user.name,
            profile_pic_url=comment_user.profile_pic_url,
        )
        for comment, comment_user in comments
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

@router.post("/{post_id}/comments", response_model=CommentRead)
async def add_comment(
    post_id: UUID,
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Add a new comment to the given post.

    Parameters:
    - post_id (UUID): Target post ID.
    - comment (CommentCreate): Comment content.
    - db (AsyncSession): DB session.
    - user (User): Authenticated user.

    Returns:
    - CommentRead: Serialized comment data.
    """

    new_comment = PostComment(
        id=uuid4(),
        post_id=post_id,
        user_id=user.id,
        content=comment.content,
        created_at=datetime.utcnow()
    )

    # Add comment to DB
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    # Broadcast and Notify clients of new comment
    await manager.broadcast({
        "type": "new_comment",
        "data": {
            "id": str(new_comment.id),
            "post_id": str(new_comment.post_id),
            "user_id": str(user.id),
            "content": new_comment.content,
            "created_at": new_comment.created_at.isoformat(),
            "user_name": user.name,
            "profile_pic_url": user.profile_pic_url,
        }
    })

    return CommentRead(
        id=new_comment.id,
        post_id=new_comment.post_id,
        user_id=user.id,
        content=new_comment.content,
        created_at=new_comment.created_at,
        user_name=user.name,
        profile_pic_url=user.profile_pic_url
    )

@router.post("/{post_id}/reactions")
async def add_reaction(
    post_id: UUID,
    reaction: PostReactionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Add or replace the user's reaction on a post.

    Parameters:
    - post_id (UUID): Post to react to.
    - reaction (PostReactionCreate): Reaction type (enum).
    - db (AsyncSession): DB session.
    - user (User): Authenticated user.

    Returns:
    - dict: Confirmation with reaction type.
    """
    
    # Remove any existing reaction by user on this post
    await db.execute(
        delete(PostReaction).where(
            (PostReaction.post_id == post_id) &
            (PostReaction.user_id == user.id)
        )
    )

    # Create new reaction
    new_reaction = PostReaction(
        id=uuid4(),
        post_id=post_id,
        user_id=user.id,
        type=reaction.type
    )

    # Add reaction to DB
    db.add(new_reaction)
    await db.commit()

    # Broadcast and Notify clients of new reaction
    await manager.broadcast({
        "type": "new_reaction",
        "data": {
            "post_id": str(post_id),
            "user_id": str(user.id),
            "reaction_type": reaction.type.value
        }
    })
    return {"status": "ok", "type": reaction.type}

@router.get("/me", response_model=List[PostRead])
async def get_my_posts(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Fetch posts created by the authenticated user.

    Parameters:
    - db (AsyncSession): DB session.
    - user (User): Authenticated user.

    Returns:
    - List[PostRead]: User's posts with metadata.
    """

    # Fetch posts by current user
    stmt = select(UserPost).where(UserPost.user_id == user.id).order_by(UserPost.created_at.desc())
    results = await db.execute(stmt)
    posts = results.scalars().all()

    # Build list with comment and reaction info
    response = []
    for post in posts:
        # Reaction counts
        reaction_stmt = (
            select(PostReaction.type, func.count())
            .where(PostReaction.post_id == post.id)
            .group_by(PostReaction.type)
        )
        reactions = await db.execute(reaction_stmt)

        # Comment count
        comment_stmt = select(func.count()).where(PostComment.post_id == post.id)
        comment_count = (await db.execute(comment_stmt)).scalar()

        reaction_counts = {rtype.value: count for rtype, count in reactions}

        response.append(PostRead(
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
            comment_count=comment_count
        ))

    return response