# 🚀 Inspector 快速启动指南

## 一键启动（推荐）

```bash
./start-all.sh
```

这个脚本会自动：
- ✅ 检查环境配置
- 🐍 启动后端服务器 (http://localhost:8000)
- ⚛️ 启动前端开发服务器 (http://localhost:3000)
- 🔍 验证服务状态
- 🛑 优雅关闭（Ctrl+C）

## 手动启动

### 1. 启动后端

```bash
# 在项目根目录
uv run python main.py
```

后端将在 http://localhost:8000 启动

### 2. 启动前端

```bash
# 新开一个终端，进入frontend目录
cd frontend
npm start
```

前端将在 http://localhost:3000 启动

## 访问地址

- **🎨 前端界面**: http://localhost:3000
- **🔧 后端API**: http://localhost:8000
- **📚 API文档**: http://localhost:8000/docs
- **🏥 健康检查**: http://localhost:8000/health

## 功能演示

### 1. 创建团队成员
1. 访问 http://localhost:3000
2. 点击"成员管理"
3. 点击"添加成员"
4. 填写成员信息并保存

### 2. 配置社交链接
1. 在成员列表中找到刚创建的成员
2. 点击"添加社交配置"
3. 选择平台（GitHub/LinkedIn）
4. 输入用户名或URL

### 3. 运行监控
1. 回到仪表板
2. 点击"运行监控"按钮
3. 查看监控结果

### 4. 生成总结
1. 在仪表板点击"生成每日总结"
2. 查看AI生成的报告

## 环境配置

### 必需的环境变量

创建 `.env` 文件：

```bash
# 复制示例配置
cp env.example .env
```

编辑 `.env` 文件：

```ini
# OpenAI API (用于生成总结)
OPENAI_API_KEY=your-openai-api-key-here

# GitHub Token (用于GitHub监控)
GITHUB_TOKEN=your-github-personal-access-token

# 数据库配置
DATABASE_URL=sqlite:///./inspector.db

# 其他配置保持默认即可
```

### 获取API密钥

#### OpenAI API Key
1. 访问 https://platform.openai.com/api-keys
2. 创建新的API密钥
3. 复制到 `.env` 文件

#### GitHub Token
1. 访问 https://github.com/settings/tokens
2. 创建新的Personal Access Token
3. 选择 `public_repo` 权限
4. 复制到 `.env` 文件

## 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 检查端口占用
lsof -i :8000
lsof -i :3000

# 杀死占用进程
kill -9 <PID>
```

#### 2. 前端无法连接后端
- 确认后端在 http://localhost:8000 运行
- 检查浏览器控制台错误
- 确认CORS配置正确

#### 3. 数据库错误
```bash
# 删除现有数据库重新开始
rm inspector.db
uv run python main.py
```

#### 4. 依赖问题
```bash
# 重新安装后端依赖
uv sync

# 重新安装前端依赖
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 日志查看

#### 后端日志
后端启动时会显示详细日志，包括：
- API请求记录
- 监控任务执行
- 错误信息

#### 前端日志
在浏览器开发者工具中查看：
- Console: JavaScript错误
- Network: API请求状态

## 开发模式

### 后端热重载
后端已配置自动重载，修改代码后会自动重启。

### 前端热重载
前端使用React开发服务器，修改代码后会自动刷新浏览器。

## 生产部署

### Docker部署
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 手动部署
1. 构建前端：`cd frontend && npm run build`
2. 配置生产环境变量
3. 使用生产WSGI服务器启动后端

## 下一步

- 📖 阅读 [README.md](README.md) 了解详细功能
- 🔧 查看 [FRONTEND_README.md](FRONTEND_README.md) 前端开发指南
- 🐳 参考 [docker-compose.yml](docker-compose.yml) 进行容器化部署
- 📊 运行 [example_usage.py](example_usage.py) 测试API功能

---

🎉 **享受使用 Inspector！** 