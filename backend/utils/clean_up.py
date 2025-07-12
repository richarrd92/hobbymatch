import asyncio
from datetime import datetime
from sqlalchemy import select, delete
from models import UserPost, PostComment, PostReaction
from database import SessionLocal
from routes.websocket import manager 
import cloudinary.uploader
from logger import logger

async def delete_expired_posts():
    """
    Find and delete all posts that have expired based on their expiration timestamp.

    Workflow:
    - Queries the database for UserPost entries where expires_at <= current UTC time.
    - Deletes associated images from Cloudinary if they exist.
    - Deletes related PostComments and PostReactions linked to expired posts.
    - Deletes the expired UserPost records from the database.
    - Commits all deletions in a transaction.
    - Broadcasts a WebSocket message to notify connected clients about each deleted post.

    Parameters:
    - None

    Returns:
    - None

    Logs:
    - Errors during image deletion or database operations are logged.

    Raises:
    - Catches and logs any unexpected exceptions to avoid crashing the loop.
    """

    try:
        now = datetime.utcnow()
        async with SessionLocal() as session:
            # Query expired posts with their IDs and Cloudinary public IDs
            expired_stmt = select(UserPost.id, UserPost.image_public_id).where(UserPost.expires_at <= now)
            result = await session.execute(expired_stmt)
            expired_posts = result.all()
            
            expired_post_ids = [post.id for post in expired_posts]

            # Delete Cloudinary images associated with expired posts
            for post_id, public_id in expired_posts:
                if public_id:
                    try:
                        cloudinary.uploader.destroy(public_id, invalidate=True)
                    except Exception as e:
                        logger.error(f"Failed to delete Cloudinary image {public_id}: {e}")

            # Delete all related comments and reactions from database
            await session.execute(delete(PostComment).where(PostComment.post_id.in_(expired_post_ids)))
            await session.execute(delete(PostReaction).where(PostReaction.post_id.in_(expired_post_ids)))
            # Delete the expired posts themselves
            await session.execute(delete(UserPost).where(UserPost.id.in_(expired_post_ids)))
            await session.commit() # Commit the transaction to apply deletions

            # Broadcast and Notify connected WebSocket clients about deleted posts
            for post_id in expired_post_ids:
                await manager.broadcast({
                    "type": "delete_post",
                    "data": {
                        "post_id": str(post_id)
                    }
                })

    except Exception as e:
        logger.error(f"Error deleting expired posts/comments/reactions: {e}")


async def delete_expired_posts_loop():
    """
    Continuously run the `delete_expired_posts` coroutine every 60 seconds.

    This creates a background loop that periodically cleans up expired posts.

    Parameters:
    - None

    Returns:
    - None

    Behavior:
    - Runs indefinitely until the application shuts down.
    - Waits 60 seconds between each execution cycle.
    """
    
    while True:
        await delete_expired_posts()
        await asyncio.sleep(60)  # wait 60 seconds between runs