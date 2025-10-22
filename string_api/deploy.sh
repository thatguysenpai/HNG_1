#!/bin/sh

# Exit on any error
set -e

echo "🚀 Deploying String Analyzer API..."

# Install dependencies if not present
if ! command -v pip3 >/dev/null 2>&1; then
  echo "Python3 and pip3 are required. Exiting."
  exit 1
fi

pip3 install -r requirements.txt

echo "✅ Dependencies installed."

# Run FastAPI using Uvicorn
echo "Starting server on http://127.0.0.1:8000 ..."
uvicorn main:app --host 127.0.0.1 --port 8000
