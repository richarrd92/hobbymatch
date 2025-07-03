#!/bin/bash

# Start HobbyMatch backend with optional venv setup and DB check
echo
echo "------ STARTING HOBBYMATCH BACKEND ------"
echo

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

# Run FastAPI app
echo
echo "-------- RUNNING FASTAPI APP --------"
echo
python3 main.py

# Usage:
# chmod +x backend.sh
# ./backend.sh
