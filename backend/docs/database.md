# How `database.py` Works

This module initializes and manages an **asynchronous** SQLAlchemy connection to a PostgreSQL database using credentials stored securely in a `.env` file.

### Environment Loading

- Loads environment variables from `.env` once per module load.
- Validates existence of `.env` file and critical variable `HOBBYMATCH_DATABASE_URL`.
- Ensures the database URL uses the proper async driver prefix: `postgresql+asyncpg://`.

### Async Database Initialization

- Creates an **async engine** using `create_async_engine()` from SQLAlchemy.
- Defines an **async session factory** (`SessionLocal`) with `sessionmaker()` bound to the async engine.
- Declares a **base ORM class** (`Base`) with `declarative_base()` for model definitions.

### FastAPI Dependency: `get_db()`

Provides a clean, async-scoped database session for each request, using an async context manager. This ensures sessions are properly closed after use, supporting async database operations:

```python
async def get_db():
    async with SessionLocal() as session:
        yield session
```

### Database Connection Test: `test_db_connection()`

An async function that runs a simple query `SELECT 1` to verify connectivity. Logs success or failure and terminates the app if the connection fails:

```python
async def test_db_connection():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
```

### Script Execution Behavior

- When run directly (`python3 database.py`), runs `test_db_connection()` to verify environment and DB setup.

### Summary

This async setup:

- Loads environment config once.
- Validates DB URL format.
- Initializes async engine and session factory.
- Provides FastAPI dependency for async DB sessions.
- Includes a test connection method with detailed logging.
- Integrates smoothly with async FastAPI backend apps.
