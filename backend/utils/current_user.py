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

# Initialize Firebase Admin SDK once
if not firebase_admin._apps:
    cred = credentials.Certificate("./secrets/hobbymatch-app-firebase-adminsdk-fbsvc-2e7e43ad02.json")
    initialize_app(cred)
    logger.info("Firebase Admin SDK initialized")

security = HTTPBearer() # HTTP Bearer scheme for token auth


# Get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
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

    logger.info("User authenticated")
    return user # Return the user