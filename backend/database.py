from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine 
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker 
from sqlalchemy import text 
from dotenv import load_dotenv 
import os
import sys
from logger import logger

# Load .env once
if not hasattr(sys.modules[__name__], "_env_loaded"):
    if not os.path.isfile(".env"):
        logger.error("Missing .env file.")
        sys.exit(1)
    load_dotenv()
    setattr(sys.modules[__name__], "_env_loaded", True)

# Get database URL
DATABASE_URL = os.getenv("HOBBYMATCH_DATABASE_URL")
if not DATABASE_URL:
    logger.error("HOBBYMATCH_DATABASE_URL not set.")
    sys.exit(1)

# Ensure proper asyncpg format
if not DATABASE_URL.startswith("postgresql+asyncpg://"):
    logger.error("DATABASE_URL must start with 'postgresql+asyncpg://'.")
    sys.exit(1)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Async session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for ORM models
Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        yield session

# Test DB connection
async def test_db_connection():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info(f"DB test successful: {result.scalar()}")
            logger.info("HobbyMatch DB connection initialized.")
    except Exception as e:
        logger.error(f"DB test failed: {e}")
        sys.exit(1)

# Run test directly
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_db_connection())