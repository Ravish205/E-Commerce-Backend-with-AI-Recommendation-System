#!/usr/bin/env bash

# Exit on error
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Ensure local standalone Node is in PATH if present
if [ -d "$PROJECT_ROOT/.node/bin" ]; then
    export PATH="$PROJECT_ROOT/.node/bin:$PATH"
fi

# Ensure virtualenv is activated
if [ -d "$PROJECT_ROOT/.venv" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

echo "=========================================================="
echo " Starting ApexStore E-Commerce & AI Recommendation System "
echo "=========================================================="

# Check database
if [ ! -f "$PROJECT_ROOT/ecommerce.db" ] && [ ! -f "$PROJECT_ROOT/instance/ecommerce.db" ]; then
    echo "[1/3] Initializing and seeding database..."
    python database/seed/seed_data.py
else
    echo "[1/3] Database ready."
fi

# Cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down ApexStore services..."
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Start Backend
echo "[2/3] Starting Flask Backend API on http://127.0.0.1:5000..."
python run.py &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for API to respond on :5000..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:5000/api/health >/dev/null 2>&1; then
        echo "Backend API is online and healthy!"
        break
    fi
    sleep 0.5
done

# Start Frontend
echo "[3/3] Starting React Vite Frontend on http://localhost:5173..."
echo "=========================================================="
echo " Storefront: http://localhost:5173"
echo " Admin Panel: http://localhost:5173/admin/dashboard"
echo " REST API:    http://localhost:5000"
echo " (Press Ctrl+C to stop both backend and frontend)"
echo "=========================================================="

cd frontend
npm run dev
