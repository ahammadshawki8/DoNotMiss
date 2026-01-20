#!/bin/bash

# DoNotMiss Backend - Local Development Script

echo "🚀 Starting DoNotMiss Backend (Local Development)"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if PostgreSQL is running
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found. Install it first:"
    echo "   macOS: brew install postgresql"
    echo "   Ubuntu: sudo apt-get install postgresql"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create database if it doesn't exist
echo "🗄️  Setting up database..."
createdb donotmiss 2>/dev/null || echo "Database already exists"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✏️  Please edit .env with your database URL"
fi

# Run the application
echo ""
echo "✅ Starting Flask server on http://localhost:5000"
echo "=================================================="
echo ""
python app.py
