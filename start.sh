#!/bin/bash

# Inspector 一键启动脚本
# 支持开发环境和生产环境启动

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "Inspector 一键启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  dev         启动开发环境 (后端 + 前端)"
    echo "  backend     仅启动后端服务"
    echo "  frontend    仅启动前端服务"
    echo "  docker      使用 Docker 启动完整环境"
    echo "  stop        停止所有服务"
    echo "  status      查看服务状态"
    echo "  clean       清理数据库数据"
    echo "  check       检查代码质量"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev       # 启动开发环境"
    echo "  $0 docker    # 使用 Docker 启动"
    echo "  $0 stop      # 停止所有服务"
    echo "  $0 clean     # 清理数据库数据"
    echo "  $0 check     # 检查代码质量"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."
    
    # 检查 Python 和 uv
    if ! command -v uv &> /dev/null; then
        print_error "未找到 uv，请先安装 uv: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
    
    # 检查 Node.js (如果需要前端)
    if [[ "$1" == "dev" || "$1" == "frontend" ]]; then
        if ! command -v node &> /dev/null; then
            print_error "未找到 Node.js，请先安装 Node.js"
            exit 1
        fi
    fi
    
    print_success "依赖检查完成"
}

# 设置环境变量
setup_environment() {
    print_info "设置环境变量..."
    
    # 检查 .env 文件
    if [[ ! -f ".env" ]]; then
        print_warning "未找到 .env 文件，从模板创建..."
        if [[ -f "config/env.example" ]]; then
            cp config/env.example .env
            print_warning "请编辑 .env 文件配置你的设置"
        else
            print_error "未找到环境变量模板文件"
            exit 1
        fi
    fi
    
    # 创建必要的目录
    mkdir -p logs
    mkdir -p ssl
    
    print_success "环境设置完成"
}

# 启动后端服务
start_backend() {
    print_info "启动后端服务..."
    
    # 安装依赖
    print_info "安装 Python 依赖..."
    uv sync
    
    # 启动后端
    print_info "启动后端 API 服务..."
    print_info "API 地址: http://localhost:8000"
    print_info "API 文档: http://localhost:8000/docs"
    print_info "健康检查: http://localhost:8000/health"
    
    uv run python main.py
}

# 启动前端服务
start_frontend() {
    print_info "启动前端服务..."
    
    cd frontend
    
    # 安装依赖
    print_info "安装前端依赖..."
    npm install
    
    # 启动前端
    print_info "启动前端开发服务器..."
    print_info "前端地址: http://localhost:3000"
    
    npm start
}

# 启动开发环境
start_dev() {
    print_info "启动开发环境..."
    
    check_dependencies "dev"
    setup_environment
    
    # 启动后端 (后台运行)
    print_info "启动后端服务..."
    uv sync
    uv run python main.py &
    BACKEND_PID=$!
    
    # 等待后端启动
    sleep 3
    
    # 启动前端
    print_info "启动前端服务..."
    cd frontend
    npm install
    npm start &
    FRONTEND_PID=$!
    
    print_success "开发环境启动完成！"
    print_info "后端 PID: $BACKEND_PID"
    print_info "前端 PID: $FRONTEND_PID"
    print_info "API 地址: http://localhost:8000"
    print_info "前端地址: http://localhost:3000"
    print_info "按 Ctrl+C 停止所有服务"
    
    # 等待用户中断
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
    wait
}

# 使用 Docker 启动
start_docker() {
    print_info "使用 Docker 启动完整环境..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        print_error "未找到 Docker，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "未找到 docker-compose，请先安装 docker-compose"
        exit 1
    fi
    
    setup_environment
    
    # 启动 Docker 服务
    print_info "启动 Docker 服务..."
    docker-compose up -d --build
    
    print_success "Docker 环境启动完成！"
    print_info "API 地址: http://localhost:8000"
    print_info "前端地址: http://localhost:3000"
    print_info "使用 '$0 stop' 停止服务"
}

# 停止服务
stop_services() {
    print_info "停止所有服务..."
    
    # 停止 Docker 服务
    if [[ -f "docker-compose.yml" ]]; then
        docker-compose down 2>/dev/null || true
    fi
    
    # 停止 Python 进程
    pkill -f "python main.py" 2>/dev/null || true
    pkill -f "uvicorn" 2>/dev/null || true
    
    # 停止 Node.js 进程
    pkill -f "npm start" 2>/dev/null || true
    pkill -f "react-scripts" 2>/dev/null || true
    
    print_success "所有服务已停止"
}

# 查看服务状态
show_status() {
    print_info "服务状态检查..."
    
    # 检查后端
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "后端服务: 运行中 (http://localhost:8000)"
    else
        print_warning "后端服务: 未运行"
    fi
    
    # 检查前端
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "前端服务: 运行中 (http://localhost:3000)"
    else
        print_warning "前端服务: 未运行"
    fi
    
    # 检查 Docker 服务
    if command -v docker-compose &> /dev/null; then
        if docker-compose ps | grep -q "Up"; then
            print_success "Docker 服务: 运行中"
        else
            print_warning "Docker 服务: 未运行"
        fi
    fi
}

# 清理数据库
clean_database() {
    print_info "清理数据库数据..."
    
    # 检查数据库文件是否存在
    if [[ ! -f "inspector.db" ]]; then
        print_warning "数据库文件不存在，无需清理"
        return
    fi
    
    # 运行快速清理脚本
    if [[ -f "scripts/quick_clean.py" ]]; then
        uv run python scripts/quick_clean.py
        if [[ $? -eq 0 ]]; then
            print_success "数据库清理完成"
        else
            print_error "数据库清理失败"
            exit 1
        fi
    else
        print_error "清理脚本不存在"
        exit 1
    fi
}

# 主逻辑
main() {
    case "${1:-help}" in
        "dev")
            start_dev
            ;;
        "backend")
            check_dependencies
            setup_environment
            start_backend
            ;;
        "frontend")
            check_dependencies "frontend"
            start_frontend
            ;;
        "docker")
            start_docker
            ;;
        "stop")
            stop_services
            ;;
        "status")
            show_status
            ;;
        "clean")
            clean_database
            ;;
        "check")
            ./scripts/check_code_quality.sh
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
