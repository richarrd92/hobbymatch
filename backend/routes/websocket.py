from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from logger import logger
from utils.firebase_token import verify_firebase_token
from utils.redis_ws_manager import manager
from database import get_db
from models import User

# Define API router for websocket endpoint
router = APIRouter()

@router.websocket("/ws/feed")
async def websocket_feed(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint to provide a live feed connection for authenticated users.

    Workflow:
    - Authenticates the connection using a Firebase ID token passed as a query parameter.
    - Validates the token and fetches the corresponding user from the database.
    - Registers the WebSocket connection for broadcasting.
    - Keeps the connection alive until the client disconnects or an error occurs.

    Parameters:
    - websocket (WebSocket): The WebSocket connection instance.
    - db (AsyncSession): Async database session dependency.

    Returns:
    - None: This is a WebSocket handler; it accepts and maintains the connection.

    Behavior:
    - Closes the connection with code 1008 (policy violation) if authentication fails.
    - Closes with code 1011 (internal error) if database errors occur.
    - Logs connection and disconnection events.
    """

    # Extract Firebase token from WebSocket query parameters for authentication
    token = websocket.query_params.get("token")
    if not token:
        # Close connection with policy violation code if token is missing
        logger.warning("WebSocket rejected: missing token")
        await websocket.close(code=1008)
        return

    # Verify the Firebase ID token to authenticate the user
    try:
        decoded_token = verify_firebase_token(token)
        firebase_uid = decoded_token.get("uid")
        if not firebase_uid:
            # Close connection if token does not contain a user ID
            logger.warning("WebSocket rejected: token missing uid")
            await websocket.close(code=1008)
            return
    except Exception as e:
        # Close connection if token verification fails
        logger.warning(f"WebSocket rejected: invalid token: {e}")
        await websocket.close(code=1008)
        return

    # Query the database for the user associated with the verified Firebase UID
    try:
        result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
        user = result.scalars().first()
        if not user:
            # Close connection if user is not found in the database
            logger.warning("WebSocket rejected: user not found")
            await websocket.close(code=1008)
            return
    except Exception as e:
        # On database errors, close connection with internal error code
        logger.error(f"DB error during WebSocket auth: {e}")
        await websocket.close(code=1011)
        return

    # Accept the WebSocket connection and register it with the manager for broadcasting
    await manager.connect(websocket)
    try:
        # Keep the connection alive by continuously waiting for messages
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Clean up connection on client disconnect
        await manager.disconnect(websocket)
    except Exception as e:
        # Handle unexpected errors: cleanup, log, but do not raise furtheron
        logger.error(f"Unexpected WebSocket error for user {user.id}: {e}")
        await manager.disconnect(websocket)