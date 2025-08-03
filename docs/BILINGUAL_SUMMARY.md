# 双语摘要功能使用指南

## 概述

Inspector 现在支持双语摘要生成功能，可以同时生成中文和英文版本的社交动态总结报告。用户可以在前端界面中通过语言切换按钮来查看不同语言版本的报告。

## 功能特性

### 🎯 核心功能
- **双语生成**: 自动生成中文和英文两个版本的摘要内容
- **语言切换**: 前端界面支持一键切换显示语言
- **智能提示**: 根据选择的语言显示相应的界面文本
- **向后兼容**: 现有的中文摘要内容保持不变

### 🔧 技术实现
- **数据库扩展**: 在 `summaries` 表中添加 `content_en` 字段存储英文内容
- **LLM优化**: 针对不同语言使用专门的提示词和系统消息
- **API增强**: 后端API支持语言参数，前端动态获取对应语言内容
- **UI适配**: 前端界面根据语言选择动态显示文本和标签

## 安装和配置

### 1. 数据库迁移

首先需要运行数据库迁移脚本来添加新的字段：

```bash
# 运行迁移脚本
python scripts/migrate_bilingual_summary.py
```

### 2. 验证安装

运行测试脚本验证功能是否正常工作：

```bash
# 测试双语摘要生成
python tests/test_bilingual_summary.py
```

### 3. 重启应用

迁移完成后，重启应用以使用新功能：

```bash
# 重启后端服务
uv run python main.py

# 重启前端服务
cd frontend && npm start
```

## 使用方法

### 生成双语摘要

1. **访问摘要页面**: 在浏览器中打开 `http://localhost:3000/summaries`
2. **生成摘要**: 点击"生成每日总结"按钮
3. **等待生成**: 系统会自动生成中文和英文两个版本的摘要
4. **查看结果**: 摘要生成完成后会显示在列表中

### 切换语言显示

1. **语言切换**: 点击页面右上角的语言切换按钮
   - 🇨🇳 中文: 显示中文版本
   - 🇺🇸 English: 显示英文版本
2. **动态更新**: 页面内容会根据选择的语言自动更新
3. **保持状态**: 语言选择会在当前会话中保持

### API 使用

#### 获取摘要列表（支持语言参数）

```bash
# 获取中文摘要
curl "http://localhost:8000/api/v1/monitoring/summaries?language=chinese"

# 获取英文摘要
curl "http://localhost:8000/api/v1/monitoring/summaries?language=english"
```

#### 获取单个摘要（支持语言参数）

```bash
# 获取指定ID的中文摘要
curl "http://localhost:8000/api/v1/monitoring/summaries/1?language=chinese"

# 获取指定ID的英文摘要
curl "http://localhost:8000/api/v1/monitoring/summaries/1?language=english"
```

## 技术细节

### 数据库结构

```sql
-- summaries 表新增字段
ALTER TABLE summaries ADD COLUMN content_en TEXT;
```

### API 参数

- `language`: 语言选择参数
  - `chinese` (默认): 返回中文内容
  - `english`: 返回英文内容

### LLM 提示词

系统会根据选择的语言使用不同的提示词：

**中文提示词**:
```
你是一位专业的社交媒体活动分析师。请为团队成员在各种平台上的活动创建简洁、信息丰富的总结报告。请用中文回答。
```

**英文提示词**:
```
You are a professional social media activity analyst. Create concise, informative summaries of team member activities across various platforms.
```

### 前端状态管理

```typescript
const [language, setLanguage] = useState<'chinese' | 'english'>('chinese');

const toggleLanguage = () => {
  setLanguage(prev => prev === 'chinese' ? 'english' : 'chinese');
};
```

## 故障排除

### 常见问题

1. **迁移失败**
   ```
   ❌ Database file not found: inspector.db
   ```
   **解决方案**: 先启动应用创建数据库，然后运行迁移脚本

2. **英文内容为空**
   ```
   content_en 字段为空
   ```
   **解决方案**: 检查 OpenAI API 配置，确保 API 调用正常

3. **语言切换不生效**
   ```
   切换语言后内容没有变化
   ```
   **解决方案**: 检查浏览器控制台是否有错误，确认 API 调用正常

### 调试步骤

1. **检查数据库结构**:
   ```bash
   sqlite3 inspector.db ".schema summaries"
   ```

2. **验证 API 响应**:
   ```bash
   curl -v "http://localhost:8000/api/v1/monitoring/summaries?language=english"
   ```

3. **查看应用日志**:
   ```bash
   tail -f logs/app.log
   ```

## 性能考虑

### 生成时间
- 双语生成需要调用两次 LLM API
- 预计生成时间比单语言版本增加 50-100%
- 建议在网络良好时进行批量生成

### 存储空间
- 英文内容会增加约 30-50% 的存储空间
- 建议定期清理旧的摘要数据

### API 调用
- 每次生成摘要会消耗双倍的 API 调用配额
- 建议监控 API 使用量，避免超出限制

## 未来改进

### 计划功能
- [ ] 支持更多语言（日语、韩语等）
- [ ] 语言偏好设置保存
- [ ] 批量语言转换工具
- [ ] 多语言内容对比功能

### 优化方向
- [ ] 并行生成多语言内容
- [ ] 智能语言检测
- [ ] 内容质量评估
- [ ] 用户反馈收集

## 支持

如果在使用过程中遇到问题，请：

1. 查看本文档的故障排除部分
2. 运行测试脚本验证功能
3. 检查应用日志获取详细错误信息
4. 提交 Issue 到项目仓库

---

*最后更新: 2024年12月* 