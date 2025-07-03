# HobbyMatch Backend

This is the backend for HobbyMatch, a social platform for connecting users based on shared hobbies and events. Built with FastAPI, PostgreSQL, SQLAlchemy, and Firebase Authentication.

### Features

- Firebase Authentication (Google Sign-In only)
- User Profiles with UUID-based IDs
- Hobby creation and user-hobby matching
- Event planning and participation
- Posts, comments, and reactions
- Modular tests with mocked Firebase tokens
- Async SQLAlchemy (PostgreSQL)

### Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- Firebase Admin SDK
- Cloudinary SDK (image upload and storage)
- Pydantic
- Uvicorn

### Directory Structure

```
backend/
├── main.py              # FastAPI app entrypoint
├── database.py          # DB config and async session
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic request/response schemas
├── routes/              # API endpoints
├── db_setup.sql         # Database setup schema
├── backend.sh           # Python script to start backend server
├── logger.py            # Shared logging config
└── requirements.txt     # Project dependencies
```

> **Note:** More detailed backend documentation files can be found in the `docs` directory located at the root of the `backend` folder.
