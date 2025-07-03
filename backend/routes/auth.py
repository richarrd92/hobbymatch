from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import firebase_admin
from firebase_admin import auth, credentials, initialize_app
from models import User, UserRole
from database import get_db
from schemas import LoginRequest, LoginResponse, SignupRequest
from logger import logger
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

# Initialize Firebase Admin SDK once
if not firebase_admin._apps:
    cred = credentials.Certificate("./secrets/hobbymatch-app-firebase-adminsdk-fbsvc-2e7e43ad02.json")
    initialize_app(cred)
    logger.info("Firebase Admin SDK initialized")

# Define API router for authentication endpoints
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer() # HTTP Bearer scheme for token auth

# Verifies Firebase ID token and returns decoded payload
def verify_firebase_token(id_token: str):
    try:
        decoded = auth.verify_id_token(id_token)

        # Check if email is verified
        if not decoded.get("email_verified", False):
            logger.error("Email not verified")
            raise HTTPException(status_code=401, detail="Email not verified")
        logger.info("Token verified")
        return decoded # Decoded token
    
    # Handle token verification errors
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

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

# Upload base64 image to Cloudinary, return URL
async def upload_base64_image_to_cloudinary(base64_str: str) -> str:

    # Cloudinary expects a data URI scheme with MIME type prefix
    data_uri = f"data:image/jpeg;base64,{base64_str}"
    try:
        resp = cloudinary.uploader.upload(data_uri)
        url = resp.get("secure_url") # Get the secure URL of the uploaded image
        if not url:
            logger.error("No URL returned from Cloudinary")
            raise Exception("No URL returned from Cloudinary")
        return url
    
    # Handle Cloudinary upload errors
    except Exception as e:
        logger.error(f"Cloudinary upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image")

# Signup new user using Firebase token
@router.post("/signup", response_model=LoginResponse)
async def signup_user(signup: SignupRequest, db: AsyncSession = Depends(get_db)):
    decoded_token = verify_firebase_token(signup.id_token)
    firebase_uid = decoded_token["uid"]
    email = decoded_token["email"]
    name = decoded_token.get("name", "Unnamed User")
    is_verified = decoded_token.get("email_verified", False)
    verification_method = decoded_token.get("firebase", {}).get("sign_in_provider", "unknown")

    # Check if user already exists
    result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
    user = result.scalars().first()
    if user:
        logger.error("User already exists")
        raise HTTPException(status_code=400, detail="User already exists")

    # Create new user
    new_user = User(
        firebase_uid=firebase_uid,
        name=name,
        email=email,
        role=UserRole.user,
        is_verified=is_verified,
        verification_method=verification_method,
    )

    # Add new user to database
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Return user info
    logger.info(f"User signed up (verified={is_verified}, method={verification_method})")
    return {
        "token": signup.id_token,
        "role": new_user.role,
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
    }

# Login existing user via Firebase token
@router.post("/login", response_model=LoginResponse)
async def login_user(login: LoginRequest, db: AsyncSession = Depends(get_db)):
    decoded_token = verify_firebase_token(login.id_token)
    firebase_uid = decoded_token["uid"]

    # Get the user from the database
    result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
    user = result.scalars().first()

    # Check if the user exists
    if not user:
        logger.error("User not found")
        raise HTTPException(status_code=404, detail="User not found")

    # Return user info
    logger.info("User logged in")
    return {
        "token": login.id_token,
        "role": user.role,
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }

# Logout endpoint (informs client)
@router.post("/logout")
def logout_user():
    logger.info("User logged out")
    return {"message": "User logged out. Clear token on client side."}


# TODO: Implement additional auth endpoints:
# - POST /auth/refresh-token      # Token refresh
# - GET /auth/me                  # Get current user profile (email uneditable)
# - PATCH /auth/me                # Update current user profile
# - POST /auth/link-provider      # Link OAuth providers (GitHub, Apple)
# - POST /auth/unlink-provider    # Unlink OAuth providers
# - POST /auth/signup-email       # Signup with email/password (optional)
# - POST /auth/login-email        # Login with email/password (optional)
# - POST /auth/password-reset     # Password reset (optional)
# - DELETE /auth/delete-account   # Delete account
# - Additional security (MFA, rate limiting)