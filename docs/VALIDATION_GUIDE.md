# 配置验证指南

Inspector 提供了强大的配置验证工具，帮助你确保系统配置正确。

## 🔍 验证脚本功能

### `validate_config.py` - 全面配置验证

这个脚本会真正测试所有配置项的有效性，包括：

- ✅ **数据库连接测试** - 验证数据库是否可以正常连接
- ✅ **文件权限检查** - 确保日志目录和数据库文件权限正确
- ✅ **配置值检查** - 检查关键配置项是否合理
- ✅ **OpenAI连接测试** - 验证AI服务是否可用
- ✅ **GitHub API测试** - 验证GitHub监控功能
- ✅ **API端点测试** - 检查后端服务是否正常运行
- ✅ **邮件配置测试** - 验证邮件通知功能

### `test_openai_config.py` - AI配置专用测试

专门用于测试AI平台配置，提供详细的错误诊断。

## 🚀 使用方法

### 1. 完整验证 (推荐)

```bash
uv run python validate_config.py
```

**适用场景**: 系统已完全配置并启动

### 2. 开发环境验证

```bash
uv run python validate_config.py --skip-external --skip-api
```

**适用场景**: 
- 开发阶段，还未配置真实的API密钥
- 后端服务未启动
- 只想验证基础配置

### 3. 跳过外部服务测试

```bash
uv run python validate_config.py --skip-external
```

**适用场景**: 
- 网络环境限制
- 暂时无法访问外部API
- 只想验证本地配置

### 4. 跳过API端点测试

```bash
uv run python validate_config.py --skip-api
```

**适用场景**: 
- 后端服务未启动
- 只想验证配置文件的正确性

## 📋 验证结果说明

### ✅ 通过
配置项正常工作，无需处理。

### ⚠️ 警告
配置项存在问题但不影响系统启动，建议修复。

### ❌ 失败
配置项存在严重问题，需要修复后才能正常使用。

## 🔧 常见问题解决

### OpenAI连接失败

**错误信息**: `Incorrect API key provided`

**解决方案**:
1. 检查 `.env` 文件中的 `OPENAI_API_KEY`
2. 确认API密钥格式正确 (以 `sk-` 开头)
3. 验证API密钥是否有效
4. 检查网络连接

**跳过测试**: 使用 `--skip-external` 参数

### GitHub API失败

**错误信息**: `Bad credentials`

**解决方案**:
1. 检查 `.env` 文件中的 `GITHUB_TOKEN`
2. 确认Token具有正确的权限
3. 验证Token是否过期

**跳过测试**: 使用 `--skip-external` 参数

### API端点不可访问

**错误信息**: `Connection refused`

**解决方案**:
1. 启动后端服务: `uv run python main.py`
2. 检查端口是否被占用
3. 确认防火墙设置

**跳过测试**: 使用 `--skip-api` 参数

### 数据库连接失败

**错误信息**: `Unable to open database file`

**解决方案**:
1. 检查数据库文件路径
2. 确认文件权限
3. 验证磁盘空间

## 💡 最佳实践

### 1. 开发阶段
```bash
# 只验证基础配置
uv run python validate_config.py --skip-external --skip-api
```

### 2. 部署前
```bash
# 完整验证所有配置
uv run python validate_config.py
```

### 3. 故障排查
```bash
# 逐步验证，先基础后外部
uv run python validate_config.py --skip-external --skip-api
uv run python validate_config.py --skip-external
uv run python validate_config.py
```

### 4. 定期检查
```bash
# 建议定期运行完整验证
uv run python validate_config.py
```

## 📞 获取帮助

如果验证脚本显示错误，可以：

1. 查看错误信息中的具体提示
2. 检查 `.env` 文件配置
3. 参考 [AI平台配置示例](ai_config_examples.md)
4. 查看项目 [README.md](README.md) 文档

---

**提示**: 验证脚本会智能识别示例配置，自动跳过需要真实凭据的测试，避免不必要的错误。 