#!/bin/bash
cd "$(dirname "$0")/backend"

echo "==================================="
echo "  AI Livestream Host"
echo "==================================="
echo ""

# Check .env
if [ ! -f .env ]; then
    echo "⚠️  No .env file found."
    echo "   Copy .env.example to .env and add your Groq API key:"
    echo "   cp .env.example .env"
    echo ""
    echo "   Get a free key at: https://console.groq.com"
    exit 1
fi

# Install deps
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q --break-system-packages 2>/dev/null

echo ""
echo "🚀 Starting server..."
echo "   Open http://localhost:8000 in your browser"
echo ""

python3 -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
