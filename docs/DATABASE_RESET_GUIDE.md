# 数据库重置和重新配置指南

## 🧹 数据库清理

数据库已成功清理，所有数据已删除但数据库结构保持不变。

### 清理的内容
- ✅ 成员数据 (Members)
- ✅ 社交配置数据 (Social Profiles)  
- ✅ 活动数据 (Activities)
- ✅ 总结数据 (Summaries)
- ✅ 用户数据 (Users)

## 🔄 重新配置步骤

### 1. 启动应用程序
```bash
# 启动开发环境
./start.sh dev

# 或者只启动后端
./start.sh backend
```

### 2. 配置成员信息
访问 `http://localhost:3000/members` 或使用 API：

```bash
# 创建新成员
curl -X POST http://localhost:8000/api/v1/members/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "email": "zhangsan@example.com",
    "position": "软件工程师",
    "department": "技术部"
  }'
```

### 3. 添加社交配置
为成员添加社交平台配置：

```bash
# 添加 GitHub 配置
curl -X POST http://localhost:8000/api/v1/members/1/social-profiles \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "github",
    "profile_url": "https://github.com/username",
    "username": "username"
  }'

# 添加 LinkedIn 配置
curl -X POST http://localhost:8000/api/v1/members/1/social-profiles \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "linkedin",
    "profile_url": "https://linkedin.com/in/username",
    "username": "username"
  }'
```

### 4. 配置监控设置
访问 `http://localhost:3000/settings` 配置：

- **监控间隔**: 设置监控频率
- **OpenAI API**: 配置 AI 总结功能
- **GitHub Token**: 配置 GitHub 监控

### 5. 启动监控
```bash
# 启动监控
curl -X POST http://localhost:8000/api/v1/monitoring/start

# 手动运行一次监控
curl -X POST http://localhost:8000/api/v1/monitoring/run-monitoring
```

## 🛠️ 清理工具

### 快速清理
```bash
# 使用启动脚本
./start.sh clean

# 或直接运行脚本
uv run python scripts/quick_clean.py
```

### 交互式清理
```bash
# 带确认的清理
uv run python scripts/clean_database.py
```

## 📊 验证配置

### 检查成员
```bash
curl http://localhost:8000/api/v1/members/
```

### 检查活动
```bash
curl http://localhost:8000/api/v1/monitoring/activities
```

### 检查监控状态
```bash
curl http://localhost:8000/api/v1/monitoring/status
```

## 🔧 故障排除

### 如果清理失败
1. 确保没有应用程序正在运行
2. 检查数据库文件权限
3. 手动删除数据库文件重新初始化：
   ```bash
   rm inspector.db*
   uv run python -c "from app.core.database.database import init_db; init_db()"
   ```

### 如果配置失败
1. 检查 API 端点是否正确
2. 验证 JSON 格式
3. 查看应用程序日志

## 📝 注意事项

- 清理操作不可逆，请确保备份重要数据
- 清理后需要重新配置所有成员和监控设置
- 建议在清理前导出重要数据
- 数据库结构保持不变，无需重新初始化

---

现在您可以开始重新配置您的 Inspector 系统了！
