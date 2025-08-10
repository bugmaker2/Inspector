#!/bin/bash

# Inspector 代码质量检查脚本

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

# 检查 Python 代码质量
check_python_code() {
    print_info "检查 Python 代码质量..."
    
    # 检查是否安装了必要的工具
    if ! command -v uv &> /dev/null; then
        print_error "未找到 uv，请先安装 uv"
        return 1
    fi
    
    # 检查 Python 语法
    print_info "检查 Python 语法..."
    if uv run python -m py_compile app/main.py; then
        print_success "Python 语法检查通过"
    else
        print_error "Python 语法检查失败"
        return 1
    fi
    
    # 检查导入
    print_info "检查 Python 导入..."
    if uv run python -c "import app.main; print('导入检查通过')"; then
        print_success "Python 导入检查通过"
    else
        print_error "Python 导入检查失败"
        return 1
    fi
    
    # 检查数据库模型
    print_info "检查数据库模型..."
    if uv run python -c "from app.models.member import Member, Activity, SocialProfile, Summary; print('数据库模型检查通过')"; then
        print_success "数据库模型检查通过"
    else
        print_error "数据库模型检查失败"
        return 1
    fi
}

# 检查前端代码质量
check_frontend_code() {
    print_info "检查前端代码质量..."
    
    cd frontend
    
    # 检查是否安装了 Node.js
    if ! command -v node &> /dev/null; then
        print_error "未找到 Node.js，请先安装 Node.js"
        return 1
    fi
    
    # 检查 TypeScript 编译
    print_info "检查 TypeScript 编译..."
    if npx tsc --noEmit; then
        print_success "TypeScript 编译检查通过"
    else
        print_error "TypeScript 编译检查失败"
        return 1
    fi
    
    # 检查依赖
    print_info "检查前端依赖..."
    if npm list --depth=0 > /dev/null 2>&1; then
        print_success "前端依赖检查通过"
    else
        print_warning "前端依赖可能有问题，请运行 npm install"
    fi
    
    cd ..
}

# 检查 API 端点
check_api_endpoints() {
    print_info "检查 API 端点..."
    
    # 检查后端是否运行
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_warning "后端服务未运行，跳过 API 端点检查"
        return 0
    fi
    
    # 测试主要端点
    local endpoints=(
        "/api/v1/members/"
        "/api/v1/summaries/"
        "/api/v1/notifications/"
        "/api/v1/settings/"
        "/api/v1/monitoring/activities"
        "/health"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -s -w "%{http_code}" "http://localhost:8000$endpoint" | grep -q "200\|404"; then
            print_success "端点 $endpoint 正常"
        else
            print_warning "端点 $endpoint 可能有问题"
        fi
    done
}

# 检查数据库
check_database() {
    print_info "检查数据库..."
    
    if [[ ! -f "inspector.db" ]]; then
        print_warning "数据库文件不存在"
        return 0
    fi
    
    # 检查数据库连接
    if uv run python -c "from app.core.database.database import SessionLocal; db = SessionLocal(); db.close(); print('数据库连接正常')"; then
        print_success "数据库连接检查通过"
    else
        print_error "数据库连接检查失败"
        return 1
    fi
}

# 检查环境配置
check_environment() {
    print_info "检查环境配置..."
    
    # 检查 .env 文件
    if [[ -f ".env" ]]; then
        print_success "环境配置文件存在"
    else
        print_warning "环境配置文件不存在，请从 config/env.example 创建"
    fi
    
    # 检查必要的目录
    local dirs=("logs" "ssl" "scripts" "docs")
    for dir in "${dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            print_success "目录 $dir 存在"
        else
            print_warning "目录 $dir 不存在"
        fi
    done
}

# 主函数
main() {
    echo "🔍 Inspector 代码质量检查"
    echo "=" * 50
    
    local exit_code=0
    
    # 检查环境配置
    check_environment || exit_code=1
    
    # 检查数据库
    check_database || exit_code=1
    
    # 检查 Python 代码
    check_python_code || exit_code=1
    
    # 检查前端代码
    check_frontend_code || exit_code=1
    
    # 检查 API 端点
    check_api_endpoints || exit_code=1
    
    echo ""
    if [[ $exit_code -eq 0 ]]; then
        print_success "所有检查通过！代码质量良好。"
    else
        print_error "部分检查失败，请查看上面的错误信息。"
    fi
    
    exit $exit_code
}

# 运行主函数
main "$@"
