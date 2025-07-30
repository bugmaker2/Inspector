#!/bin/bash

# Inspector Cursor - 全栈应用启动脚本

echo "🚀 Starting Inspector Cursor Full Stack Application..."
echo "=================================================="

# 检查后端依赖
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# 检查前端依赖
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: frontend/package.json not found."
    exit 1
fi

# 检查环境配置
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating from example..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ Created .env from env.example"
    else
        echo "❌ Error: env.example not found. Please create .env file manually."
        exit 1
    fi
fi

# 启动后端（后台运行）
echo "🐍 Starting Backend Server..."
echo "   Backend will be available at http://localhost:8000"
echo "   API documentation at http://localhost:8000/docs"

uv run python main.py &
BACKEND_PID=$!

# 等待后端启动
echo "⏳ Waiting for backend to start..."
sleep 5

# 检查后端是否启动成功
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend started successfully"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# 启动前端（后台运行）
echo "⚛️  Starting Frontend Development Server..."
echo "   Frontend will be available at http://localhost:3000"

cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# 等待前端启动
echo "⏳ Waiting for frontend to start..."
sleep 10

# 检查前端是否启动成功
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend started successfully"
else
    echo "⚠️  Frontend may still be starting..."
fi

echo ""
echo "🎉 Inspector Cursor is now running!"
echo "=================================="
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# 等待用户中断
trap 'echo ""; echo "🛑 Stopping servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

# 保持脚本运行
wait 