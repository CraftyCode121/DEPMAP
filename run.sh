#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

echo "Starting DEPMAP API on http://localhost:8000 ..."
uvicorn api.main:app --reload &
API_PID=$!
trap "kill $API_PID 2>/dev/null" EXIT

sleep 2

FRONTEND="file://$DIR/frontend/index.html"
echo "Opening frontend..."
if command -v xdg-open > /dev/null; then
  xdg-open "$FRONTEND"       # Linux
elif command -v open > /dev/null; then
  open "$FRONTEND"           # macOS
else
  echo "Open this URL manually: $FRONTEND"
fi

echo ""
echo "DEPMAP is running. Press Ctrl+C to stop the API."
wait $API_PID