from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import firebase_admin
from firebase_admin import credentials, initialize_app
from models import User
from database import get_db
from logger import logger
from utils.firebase_token import verify_firebase_token
import random

# Initialize Firebase Admin SDK once
if not firebase_admin._apps:
    cred = credentials.Certificate("./secrets/hobbymatch-app-firebase-adminsdk-fbsvc-2e7e43ad02.json")
    initialize_app(cred)

security = HTTPBearer() # HTTP Bearer scheme for token auth


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract and verify the Firebase authentication token from the Authorization header,
    then retrieve the corresponding User from the database.

    Parameters:
    - credentials (HTTPAuthorizationCredentials): Contains the Bearer token from the request header.
    - db (AsyncSession): Async SQLAlchemy database session.

    Returns:
    - User: The user object associated with the valid Firebase UID.

    Raises:
    - HTTPException 401 Unauthorized: If token is missing UID or token verification fails.
    - HTTPException 404 Not Found: If no user matches the Firebase UID.
    """

    token = credentials.credentials
    decoded_token = verify_firebase_token(token)
    firebase_uid = decoded_token.get("uid")

    # Check if the token has a valid Firebase UID
    if not firebase_uid:
        logger.error("Token missing UID")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing UID")

    # Get the user from the database
    result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
    user = result.scalars().first()

    # Check if the user exists
    if not user:
        logger.error("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user # Return the user

def blur_and_round(value: float, range: float = 0.02, decimals: int = 1) -> float:
    """
    Adds a small random noise to a floating-point coordinate and rounds it to reduce precision,
    providing basic location privacy by obfuscation.

    Parameters:
    - value (float): The original coordinate (latitude or longitude).
    - range (float): The maximum absolute noise to add/subtract (default 0.02).
    - decimals (int): Number of decimal places to round the result to (default 1).

    Returns:
    - float: The obfuscated and rounded coordinate.
    """

    noise = random.uniform(-range, range)
    return round(value + noise, decimals)