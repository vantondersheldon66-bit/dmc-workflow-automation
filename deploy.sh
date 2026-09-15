#!/usr/bin/env bash
# ==============================================================================
# DMC Operations Platform - Automated Linux Deployment Script
# ==============================================================================
set -e

echo "================================================================="
echo "🚀 DMC OPERATIONS PLATFORM: DEPLOYMENT START"
echo "================================================================="

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ and re-run."
    exit 1
fi
echo "✓ Found Python: $(python3 --version)"

# Check or copy .env
if [ ! -f .env ]; then
    echo "ℹ️  No .env file found. Copying .env.example to .env..."
    cp .env.example .env
fi

# Initialize database
echo "ℹ️  Initializing SQLite database..."
python3 db.py

# Launch option
echo ""
echo "Select deployment mode:"
echo "1) Run with Docker Compose (DMC Platform + n8n workflows)"
echo "2) Run directly in background with Systemd / nohup"
echo "3) Run in foreground for development"
read -p "Enter choice [1-3] (Default: 1): " CHOICE
CHOICE=${CHOICE:-1}

case $CHOICE in
    1)
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker not found. Falling back to background process."
            nohup python3 server.py --no-browser > server.log 2>&1 &
            echo "✓ DMC server started in background (PID: $!). Logs in server.log"
        else
            echo "🚀 Starting Docker Compose containers..."
            docker compose up -d --build
            echo "✓ Containers started!"
            echo "👉 DMC Command Center: http://localhost:8080"
            echo "👉 n8n Workflow Automation: http://localhost:5678"
        fi
        ;;
    2)
        nohup python3 server.py --no-browser > server.log 2>&1 &
        echo "✓ DMC server started in background (PID: $!)."
        echo "👉 Access at: http://localhost:8080"
        echo "Logs: tail -f server.log"
        ;;
    3)
        echo "🚀 Starting server in foreground..."
        python3 server.py
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
