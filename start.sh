#!/usr/bin/env bash
set -e

echo "================================================================"
echo "          CodeSupply - Software Supply-Chain Platform          "
echo "================================================================"

# Start backend
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

sleep 2

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "[OK] CodeSupply is launching!"
echo " - Frontend Dashboard: http://localhost:3000"
echo " - Backend OpenAPI Docs: http://localhost:8000/docs"
echo "Press Ctrl+C to terminate both servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
