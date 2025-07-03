#!/bin/bash

# Start HobbyMatch backend, then frontend

echo
echo "====== STARTING HOBBYMATCH BACKEND ======"
echo

# Navigate to backend
cd backend || { echo "[ERROR] Could not find backend directory."; exit 1; }

# Create virtual environment if missing
if [ ! -d "venv" ]; then
  echo " - No virtual environment found. Creating one..."
  python3 -m venv venv || { echo "[ERROR] Failed to create venv."; exit 1; }
  NEW_VENV=true
else
  NEW_VENV=false
fi

# Activate virtual environment
echo " - Activating virtual environment..."
source venv/bin/activate || { echo "[ERROR] Failed to activate venv."; exit 1; }

# Install requirements if new venv or missing packages
if [ "$NEW_VENV" = true ] || [ ! -d "venv/lib" ]; then
  echo " - Installing dependencies from requirements.txt..."
  pip install -r requirements.txt || { echo "[ERROR] Failed to install dependencies."; deactivate; exit 1; }
fi

# Update requirements.txt
echo " - Updating requirements.txt..."
pip freeze > requirements.txt && echo " - Updated" || echo "[Warning] Could not update"

# Test DB connection
python3 database.py || { echo "[ERROR] DB init failed."; deactivate; exit 1; }

# Start FastAPI app in background
echo
echo " - Starting FastAPI app in background..."
uvicorn main:app --reload &

BACKEND_PID=$!
cd ..

echo
echo "====== STARTING HOBBYMATCH FRONTEND ======"
echo

# Navigate to frontend directory
cd frontend || { echo "[ERROR] Could not find frontend directory."; kill $BACKEND_PID; exit 1; }

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
  echo " - Installing frontend dependencies..."
  npm install || { echo "[ERROR] Failed to install frontend deps."; kill $BACKEND_PID; exit 1; }
fi

# Start frontend app
echo " - Starting frontend..."
npm run dev || { echo "[ERROR] Failed to start frontend."; kill $BACKEND_PID; exit 1; }

# Wait for backend to exit (optional cleanup)
wait $BACKEND_PID

# Usage:
# chmod +x start.sh
# ./start.sh
