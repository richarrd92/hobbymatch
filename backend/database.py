from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine 
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker 
from sqlalchemy import text 
from dotenv import load_dotenv 
import os
import sys
from logger import logger

# Load environment variables from .env file once
if not hasattr(sys.modules[__name__], "_env_loaded"):
    if not os.path.isfile(".env"):
        logger.error("Missing .env file.")
        sys.exit(1)
    load_dotenv()
    setattr(sys.modules[__name__], "_env_loaded", True)

# Read the database URL from environment variable
DATABASE_URL = os.getenv("HOBBYMATCH_DATABASE_URL")
if not DATABASE_URL:
    logger.error("HOBBYMATCH_DATABASE_URL not set.")
    sys.exit(1)

# Validate that DATABASE_URL uses asyncpg dialect prefix
if not DATABASE_URL.startswith("postgresql+asyncpg://"):
    logger.error("DATABASE_URL must start with 'postgresql+asyncpg://'.")
    sys.exit(1)

# Create the SQLAlchemy async engine for database connections
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Create an async session factory bound to the engine
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base declarative class for ORM models to inherit fr
Base = declarative_base()

async def get_db():
    """
    Async generator dependency that provides a database session.

    Yields:
    - AsyncSession: A new SQLAlchemy asynchronous session for DB operations.

    Usage:
    - Use as a FastAPI dependency in path operations.
    - Session is automatically closed after usage.
    """
    async with SessionLocal() as session:
        yield session

async def test_db_connection():
    """
    Test the database connection by executing a simple SQL query.

    Raises:
    - Logs error and exits if connection or query fails.

    Usage:
    - Can be run on app startup or standalone to verify DB connectivity.
    """
    try:
        async with engine.connect() as conn:
            # Execute a simple raw SQL to verify connection
            await conn.execute(text("SELECT 1"))
            logger.info("HobbyMatch DB connection initialized.")
    except Exception as e:
        logger.error(f"DB test failed: {e}")
        sys.exit(1) # Exit application on failure

# Run the test_db_connection function if this module is run as main
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_db_connection())