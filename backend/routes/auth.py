from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User, UserRole
from database import get_db
from schemas import LoginRequest, LoginResponse, SignupRequest
from logger import logger
from utils.firebase_token import verify_firebase_token

# Define API router for authentication endpoints
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer() # HTTP Bearer scheme for token auth

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
    logger.info(f"{User.name} signed up")
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
    logger.info(f"{User.name} logged in")
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
    logger.info(f"{User.name} logged out")
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