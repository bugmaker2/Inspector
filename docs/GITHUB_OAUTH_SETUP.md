# GitHub OAuth 设置指南

## 1. 创建GitHub OAuth应用

### 1.1 访问GitHub开发者设置
1. 登录GitHub账户
2. 点击右上角头像 → Settings
3. 左侧菜单选择 "Developer settings"
4. 点击 "OAuth Apps"
5. 点击 "New OAuth App"

### 1.2 配置OAuth应用
填写以下信息：

**应用信息：**
- **Application name**: Inspector
- **Homepage URL**: `https://your-domain.com` (生产环境) 或 `http://localhost:3000` (开发环境)
- **Application description**: Social media activity monitoring service

**授权配置：**
- **Authorization callback URL**: `https://your-domain.com/api/v1/auth/github/callback` (生产环境) 或 `http://localhost:8000/api/v1/auth/github/callback` (开发环境)

### 1.3 获取Client ID和Client Secret
创建完成后，你会看到：
- **Client ID**: 复制这个值
- **Client Secret**: 点击 "Generate a new client secret" 生成并复制

## 2. 配置环境变量

### 2.1 开发环境
在项目根目录创建 `.env` 文件：

```bash
# GitHub OAuth Configuration
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/auth/github/callback
```

### 2.2 生产环境
在生产服务器上配置环境变量：

```bash
# GitHub OAuth Configuration
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=https://your-domain.com/api/v1/auth/github/callback
```

## 3. 运行数据库迁移

### 3.1 安装依赖
```bash
uv add cryptography itsdangerous
```

### 3.2 运行迁移脚本
```bash
uv run python scripts/migrate_oauth_tables.py
```

## 4. 测试OAuth功能

### 4.1 启动应用
```bash
# 启动后端
uv run python app/main.py

# 启动前端 (新终端)
cd frontend
npm start
```

### 4.2 测试连接
1. 访问 `http://localhost:3000/settings`
2. 点击 "连接 GitHub" 按钮
3. 完成GitHub授权
4. 验证连接状态

## 5. 权限说明

### 5.1 请求的权限范围
- `read:user` - 读取用户基本信息
- `read:email` - 读取邮箱信息
- `repo` - 访问私有仓库
- `read:org` - 读取组织信息

### 5.2 权限用途
- **用户信息**: 显示GitHub用户名和头像
- **邮箱**: 用于用户账户关联
- **仓库访问**: 监控代码提交和活动
- **组织信息**: 监控组织相关活动

## 6. 安全注意事项

### 6.1 环境变量安全
- 不要将Client Secret提交到代码仓库
- 使用环境变量或密钥管理服务
- 定期轮换Client Secret

### 6.2 HTTPS要求
- 生产环境必须使用HTTPS
- 确保SSL证书有效
- 配置正确的回调URL

### 6.3 数据保护
- Access Token使用AES加密存储
- 实现Token过期处理
- 提供用户撤销授权功能

## 7. 故障排除

### 7.1 常见错误

**"Invalid state token"**
- 检查session配置
- 确保state参数正确传递

**"OAuth error: bad_verification_code"**
- 检查Client ID和Client Secret
- 验证回调URL配置

**"Redirect URI mismatch"**
- 确保GitHub应用的回调URL与配置一致
- 检查协议(http/https)和端口

### 7.2 调试步骤
1. 检查环境变量是否正确设置
2. 验证数据库表是否创建成功
3. 查看应用日志获取详细错误信息
4. 确认网络连接和防火墙设置

## 8. 生产部署

### 8.1 域名配置
- 配置HTTPS域名
- 更新GitHub OAuth应用的回调URL
- 设置正确的环境变量

### 8.2 监控和日志
- 监控OAuth成功率
- 记录授权和错误日志
- 设置告警机制

### 8.3 备份和恢复
- 定期备份用户数据
- 准备OAuth配置恢复方案
- 测试故障恢复流程 