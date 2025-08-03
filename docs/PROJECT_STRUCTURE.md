# Inspector 项目结构

## 📁 目录结构

```
Inspector/
├── README.md                 # 项目主要文档
├── main.py                   # 应用入口点
├── pyproject.toml            # Python项目配置
├── .python-version           # Python版本
├── .gitignore               # Git忽略文件
├── docker-compose.yml       # Docker Compose配置
├── Dockerfile               # Docker镜像配置
├── inspector.db      # SQLite数据库文件
│
├── app/                     # 后端应用代码
│   ├── api/                 # API路由
│   ├── core/                # 核心配置
│   ├── models/              # 数据模型
│   └── services/            # 业务服务
│
├── frontend/                # 前端React应用
│   ├── src/                 # 源代码
│   ├── public/              # 静态文件
│   └── package.json         # 前端依赖
│
├── tests/                   # 测试文件
│   ├── validate_config.py   # 配置验证脚本
│   ├── test_api_endpoints.py # API端点测试
│   ├── test_aliyun_openai.py # 阿里云API测试
│   ├── test_github_token.py # GitHub API测试
│   ├── test_openai_config.py # OpenAI配置测试
│   ├── test_social_profile.py # 社交配置测试
│   ├── test_app.py          # 应用测试
│   └── quick_test.py        # 快速测试
│
├── docs/                    # 文档
│   ├── API_TEST_RESULTS.md  # API测试结果
│   ├── ALIYUN_SETUP.md      # 阿里云配置指南
│   └── GITHUB_SETUP.md      # GitHub配置指南
│
├── scripts/                 # 脚本文件
│   ├── start-all.sh         # 启动所有服务
│   ├── start-frontend.sh    # 启动前端
│   ├── deploy.sh            # 部署脚本
│   └── example_usage.py     # 使用示例
│
├── config/                  # 配置文件
│   └── env.example          # 环境变量示例
│
├── logs/                    # 日志文件目录
└── .venv/                   # Python虚拟环境
```

## 📋 文件说明

### 根目录文件
- **README.md**: 项目主要文档，包含安装、配置、使用说明
- **main.py**: FastAPI应用入口点
- **pyproject.toml**: Python项目配置，包含依赖和构建设置
- **docker-compose.yml**: Docker容器编排配置
- **Dockerfile**: Docker镜像构建配置
- **inspector.db**: SQLite数据库文件

### 应用代码 (app/)
- **api/**: FastAPI路由和端点定义
- **core/**: 核心配置、数据库连接等
- **models/**: SQLAlchemy数据模型和Pydantic模式
- **services/**: 业务逻辑服务（监控、总结等）

### 测试文件 (tests/)
- **validate_config.py**: 配置验证脚本
- **test_api_endpoints.py**: API端点测试
- **test_aliyun_openai.py**: 阿里云通义千问API测试
- **test_github_token.py**: GitHub API测试
- **test_openai_config.py**: OpenAI配置测试
- **test_social_profile.py**: 社交配置测试
- **test_app.py**: 应用功能测试
- **quick_test.py**: 快速功能验证

### 文档 (docs/)
- **API_TEST_RESULTS.md**: API测试结果和状态
- **ALIYUN_SETUP.md**: 阿里云通义千问配置指南
- **GITHUB_SETUP.md**: GitHub API配置指南

### 脚本 (scripts/)
- **start-all.sh**: 启动后端和前端服务
- **start-frontend.sh**: 仅启动前端服务
- **deploy.sh**: 部署脚本
- **example_usage.py**: API使用示例

### 配置 (config/)
- **env.example**: 环境变量配置示例

## 🚀 快速开始

### 1. 安装依赖
```bash
uv sync
```

### 2. 配置环境变量
```bash
cp config/env.example .env
# 编辑 .env 文件，配置必要的API密钥
```

### 3. 验证配置
```bash
uv run python tests/validate_config.py
```

### 4. 启动服务
```bash
# 启动所有服务
./scripts/start-all.sh

# 或分别启动
uv run python main.py  # 后端
cd frontend && npm start  # 前端
```

### 5. 运行测试
```bash
# 配置验证
uv run python tests/validate_config.py

# API端点测试
uv run python tests/test_api_endpoints.py

# 特定功能测试
uv run python tests/test_aliyun_openai.py
uv run python tests/test_github_token.py
```

## 📖 文档导航

- **主要文档**: [README.md](README.md)
- **API测试结果**: [docs/API_TEST_RESULTS.md](docs/API_TEST_RESULTS.md)
- **阿里云配置**: [docs/ALIYUN_SETUP.md](docs/ALIYUN_SETUP.md)
- **GitHub配置**: [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md)

## 🔧 开发指南

### 添加新功能
1. 在 `app/` 目录下添加相应的模块
2. 在 `tests/` 目录下添加测试文件
3. 更新相关文档

### 运行测试
```bash
# 运行所有测试
uv run python -m pytest tests/

# 运行特定测试
uv run python tests/test_api_endpoints.py
```

### 代码格式化
```bash
uv run black app/ tests/
uv run isort app/ tests/
```

---

**项目结构版本**: 1.0.0
**最后更新**: 2025-07-30 