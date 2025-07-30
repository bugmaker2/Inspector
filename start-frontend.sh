#!/bin/bash

# Inspector Cursor Frontend Startup Script

echo "🚀 Starting Inspector Cursor Frontend..."
echo "======================================"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the frontend directory."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting development server..."
echo "   Frontend will be available at http://localhost:3000"
echo "   Backend API should be running at http://localhost:8000"
echo "   Press Ctrl+C to stop"

npm start 