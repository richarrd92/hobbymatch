import asyncio
from datetime import datetime
from sqlalchemy import select, delete
from models import UserPost, PostComment, PostReaction
from database import SessionLocal
import cloudinary.uploader
import logging

logger = logging.getLogger(__name__)

async def delete_expired_posts():
    while True:
        try:
            now = datetime.utcnow()
            async with SessionLocal() as session:
                expired_stmt = select(UserPost.id, UserPost.image_public_id).where(UserPost.expires_at <= now)
                result = await session.execute(expired_stmt)
                expired_posts = result.all()

                expired_post_ids = [post.id for post in expired_posts]

                if expired_post_ids:
                    for post_id, public_id in expired_posts:
                        if public_id:
                            try:
                                cloudinary.uploader.destroy(public_id, invalidate=True)
                            except Exception as e:
                                logger.error(f"Failed to delete Cloudinary image {public_id}: {e}")

                    await session.execute(delete(PostComment).where(PostComment.post_id.in_(expired_post_ids)))
                    await session.execute(delete(PostReaction).where(PostReaction.post_id.in_(expired_post_ids)))
                    deleted_posts = await session.execute(delete(UserPost).where(UserPost.id.in_(expired_post_ids)))
                    logger.info(f"Deleted {deleted_posts.rowcount} expired posts.")
                    await session.commit()
                else:
                    logger.warning("No posts to delete.")
        except Exception as e:
            logger.error(f"Error deleting expired posts/comments/reactions: {e}")
        await asyncio.sleep(5)
