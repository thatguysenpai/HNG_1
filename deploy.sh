#!/usr/bin/env bash
set -e

# Install dependencies
pip install -r requirements.txt

# Start FastAPI using Uvicorn
uvicorn main:app --host 0.0.0.0 --port $PORT

