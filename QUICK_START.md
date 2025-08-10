# Inspector 快速启动指南

## 🚀 一键启动

项目现在提供了一个简单的一键启动脚本，支持多种启动方式：

### 基本用法

```bash
# 查看帮助信息
./start.sh help

# 启动开发环境 (推荐)
./start.sh dev

# 仅启动后端
./start.sh backend

# 仅启动前端
./start.sh frontend

# 使用 Docker 启动完整环境
./start.sh docker

# 停止所有服务
./start.sh stop

# 查看服务状态
./start.sh status
```

## 📋 启动选项详解

### 1. 开发环境启动 (`./start.sh dev`)
**推荐用于日常开发**

- ✅ 自动检查依赖
- ✅ 自动设置环境变量
- ✅ 同时启动后端和前端
- ✅ 支持热重载
- ✅ 彩色日志输出

**访问地址：**
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 前端界面: http://localhost:3000
- 健康检查: http://localhost:8000/health

### 2. 仅启动后端 (`./start.sh backend`)
**适用于 API 开发和测试**

- 只启动后端服务
- 适合 API 开发和调试
- 支持热重载

### 3. 仅启动前端 (`./start.sh frontend`)
**适用于前端开发**

- 只启动前端服务
- 需要后端服务已经运行
- 支持热重载

### 4. Docker 环境 (`./start.sh docker`)
**适用于生产环境或完整测试**

- 使用 Docker Compose 启动完整环境
- 包含数据库、后端、前端、Nginx
- 适合生产环境部署

## 🔧 环境配置

### 首次启动

1. **自动配置**：脚本会自动创建 `.env` 文件（如果不存在）
2. **手动配置**：编辑 `.env` 文件设置你的配置

```bash
# 复制环境变量模板
cp config/env.example .env

# 编辑配置文件
nano .env
```

### 重要配置项

```bash
# OpenAI API 配置 (必需)
OPENAI_API_KEY=your-openai-api-key-here

# 数据库配置 (可选，默认使用 SQLite)
DATABASE_URL=sqlite:///./inspector.db

# GitHub Token (可选)
GITHUB_TOKEN=your-github-token

# LinkedIn 配置 (可选)
LINKEDIN_USERNAME=your-linkedin-username
LINKEDIN_PASSWORD=your-linkedin-password
```

## 📦 依赖要求

### 开发环境
- **uv**: Python 包管理器
- **Node.js**: 前端开发
- **npm**: 前端包管理器

### Docker 环境
- **Docker**: 容器化平台
- **Docker Compose**: 多容器编排

## 🛠️ 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查看端口占用
   lsof -i :8000
   lsof -i :3000
   
   # 停止占用进程
   ./start.sh stop
   ```

2. **依赖安装失败**
   ```bash
   # 清理并重新安装
   uv sync --reinstall
   cd frontend && npm install
   ```

3. **环境变量问题**
   ```bash
   # 重新创建环境文件
   cp config/env.example .env
   # 编辑 .env 文件
   ```

4. **数据库问题**
   ```bash
   # 删除数据库文件重新初始化
   rm inspector.db
   ./start.sh backend
   ```

### 日志查看

```bash
# 查看后端日志
tail -f logs/inspector.log

# 查看 Docker 日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f inspector
```

## 🎯 快速验证

启动后，可以通过以下方式验证服务是否正常：

```bash
# 检查服务状态
./start.sh status

# 测试 API 健康检查
curl http://localhost:8000/health

# 测试前端访问
curl http://localhost:3000
```

## 📚 下一步

1. **配置社交平台**：在 `.env` 文件中配置 GitHub 和 LinkedIn 信息
2. **添加成员**：通过前端界面或 API 添加团队成员
3. **设置监控**：配置监控间隔和通知设置
4. **查看文档**：访问 http://localhost:8000/docs 查看完整 API 文档

## 🆘 获取帮助

- **API 文档**: http://localhost:8000/docs
- **项目文档**: 查看 `docs/` 目录
- **部署指南**: `docs/DEPLOYMENT_GUIDE.md`
- **清理总结**: `docs/CLEANUP_SUMMARY.md`
