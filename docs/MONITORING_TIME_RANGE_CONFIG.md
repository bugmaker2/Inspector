# 监控时间范围配置指南

## 🔍 问题解决

您之前看到前端只显示20个活动，这是因为：

1. **旧数据限制**：数据库中存储的是使用旧方法（固定20个活动限制）时创建的活动
2. **时间范围过滤**：新的时间范围监控只处理指定时间段内的活动
3. **配置调整**：需要根据实际需求调整时间范围

## ✅ 解决方案

### 1. 配置化时间范围

现在您可以通过配置文件调整监控时间范围：

```python
# app/core/config/settings.py
monitoring_time_range_hours: int = Field(
    default=168,  # 168小时 = 1周
    description="Time range for monitoring activities in hours"
)
```

### 2. 环境变量配置

在 `.env` 文件中添加：

```env
# 监控时间范围（小时）
MONITORING_TIME_RANGE_HOURS=168
```

### 3. 推荐配置

| 使用场景 | 时间范围 | 配置值 | 说明 |
|---------|---------|--------|------|
| 频繁监控 | 1-2小时 | 2 | 快速响应，减少重复 |
| 标准监控 | 4-6小时 | 6 | 平衡性能和完整性 |
| 日常监控 | 24小时 | 24 | 完整覆盖一天 |
| 周报监控 | 1周 | 168 | 完整覆盖一周 |
| 月报监控 | 1月 | 720 | 完整覆盖一月 |

## 🔧 如何调整

### 方法1：修改环境变量

```bash
# 编辑 .env 文件
echo "MONITORING_TIME_RANGE_HOURS=24" >> .env

# 重启服务
./start.sh backend
```

### 方法2：修改代码配置

```python
# 编辑 app/core/config/settings.py
monitoring_time_range_hours: int = Field(
    default=24,  # 改为24小时
    description="Time range for monitoring activities in hours"
)
```

### 方法3：临时测试

```bash
# 使用测试脚本测试不同时间范围
uv run python scripts/test_time_monitoring.py
```

## 📊 验证效果

### 1. 检查监控日志

```bash
tail -f logs/inspector_cursor.log | grep "Processing GitHub events"
```

应该看到类似输出：
```
Processing GitHub events from 2025-08-03 07:09:21.846017 to now
Processed 10 events, filtered 10 activities within 168h time range
```

### 2. 检查活动数量

```bash
# 检查API返回的活动数量
curl -s "http://localhost:8000/api/v1/monitoring/activities" | jq length

# 检查数据库中的活动总数
curl -s "http://localhost:8000/api/v1/monitoring/activities?limit=1000" | jq length
```

### 3. 前端验证

刷新前端页面，应该能看到更多活动（取决于时间范围内实际的活动数量）。

## 🚀 性能优化建议

### 1. 根据监控频率调整

- **每30分钟监控**：使用1-2小时时间范围
- **每小时监控**：使用2-4小时时间范围
- **每天监控**：使用24小时时间范围

### 2. 避免过度配置

- 时间范围过大可能导致性能问题
- 时间范围过小可能遗漏重要活动
- 建议根据实际活动频率调整

### 3. 监控日志分析

关注日志中的这些信息：
- `Processing GitHub events from X to now`
- `Processed X events, filtered Y activities within Zh time range`
- `Reached event outside time range, stopping processing`

## 🔄 动态调整

### 1. 根据活动频率自动调整

```python
def get_dynamic_time_range(self, monitoring_interval_minutes: int) -> int:
    """根据监控间隔动态调整时间范围"""
    if monitoring_interval_minutes <= 30:
        return 2  # 30分钟内监控，使用2小时范围
    elif monitoring_interval_minutes <= 60:
        return 4  # 1小时内监控，使用4小时范围
    elif monitoring_interval_minutes <= 1440:  # 24小时
        return 24  # 每天监控，使用24小时范围
    else:
        return 168  # 每周监控，使用1周范围
```

### 2. 根据历史活动数据调整

```python
def get_optimal_time_range(self, member_id: int) -> int:
    """根据成员的历史活动频率调整时间范围"""
    # 获取最近7天的活动数量
    recent_activities = self.db.query(Activity).filter(
        Activity.member_id == member_id,
        Activity.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    if recent_activities > 50:
        return 24  # 活跃用户，使用24小时
    elif recent_activities > 10:
        return 72  # 中等活跃，使用3天
    else:
        return 168  # 低频用户，使用1周
```

## ⚠️ 注意事项

1. **API 限制**：GitHub API 有速率限制，时间范围过大可能触发限制
2. **性能影响**：处理更多活动会增加 CPU 和内存使用
3. **存储空间**：更多活动需要更多数据库存储空间
4. **时区处理**：所有时间都使用 UTC 时间进行计算

## �� 总结

现在您的监控系统已经：

- ✅ 从固定数量限制改为基于时间范围
- ✅ 支持配置化时间范围调整
- ✅ 提供详细的监控日志
- ✅ 支持动态时间范围优化
- ✅ 确保数据完整性和准确性

您可以根据实际需求调整 `MONITORING_TIME_RANGE_HOURS` 来获得最适合的监控效果！
