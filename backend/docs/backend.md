# Backend Documentation

This is the backend for the HobbyMatch App, built using FastAPI. It provides a RESTful API for managing user authentication, hobby and event data, user matches, and media uploads.

### Tech Stack

The backend leverages the following technologies:
- **FastAPI** — a modern Python web framework for building APIs.
- **Uvicorn** — an ASGI server used to run the FastAPI app.
- **SQLAlchemy (async)** — an Object Relational Mapper (ORM) for interacting with PostgreSQL.
- **PostgreSQL** — the relational database system used to store persistent data.
- **Pydantic** — used for data validation and serialization.
- **Firebase Admin SDK** — handles Google Sign-In authentication and user management.
- **Cloudinary** — integrated for secure image upload and hosting (e.g., user profile pictures).
- **python-dotenv** — used for loading sensitive environment variables from a `.env` file.

### Setup Instructions

#### Step 1: Create a Virtual Environment

To isolate project dependencies, navigate to the backend folder and set up a virtual environment:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

#### Step 2: Install Dependencies and Create `.env`

Install required packages and create your `.env` file for storing environment variables like database URLs, Firebase keys, and Cloudinary credentials:

```bash
pip install -r requirements.txt
touch .env
```

Make sure your `.env` file includes keys such as:

```
DATABASE_URL=...
FIREBASE_TYPE=...
FIREBASE_PROJECT_ID=...
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

> Important:
You will also need a **secrets folder** inside the backend directory containing your Firebase Admin SDK project information JSON file (usually named something like firebase-adminsdk.json). This file is required for initializing Firebase Admin SDK securely.

#### Step 3: Update Requirements as Needed

If you install new packages, update `requirements.txt` to reflect your changes:

```bash
pip freeze > requirements.txt
```

#### Step 4: Start the Server

Run the provided shell script to start the backend: 
```bash
./backend.sh
```

This will:
- Kill any running server on the backend port
- Activate the virtual environment
- Initialize the database and tables
- Start the FastAPI server
- Cleanly shut down on exit 

### Notes

- Cloudinary is used for uploading and serving profile images. The backend handles secure media uploads and returns optimized URLs.
- Firebase handles user authentication via Google Sign-In, with restricted domain checks and token validation.
- UUIDs are used for primary keys to improve scalability and uniqueness across distributed systems.
- Redis is used for WebSocket message broadcasting across multiple server instances, so the Redis server must be running globally in your environment during development.

#### Redis Installation

To enable WebSocket broadcasting with Redis during development, you need to install the Redis server globally on your computer.

1. **Install Redis via Homebrew (recommended):**

```bash
brew install redis
```

2. **Start Redis Server:**

```bash
redis-server
```

**Note:** Make sure to start the Redis server before running the FastAPI server.You can keep this running in a separate terminal tab/window while developing.

3. **(Optional) Run Redis as a background service:**   
```bash
brew services start redis
```
4. **Verify Redis is running:**   
```bash
redis-cli ping
```
If it returns `PONG`, Redis is running successfully.

> Note: You do not install the Redis server inside the Python virtual environment. Only the Python Redis client package (redis) should be installed in your virtual environment. For production deployment, Redis should be hosted as a managed service or on your production infrastructure, not bundled with your app or installed on end users' devices.
