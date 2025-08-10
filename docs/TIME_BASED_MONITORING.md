# 基于时间范围的监控改进

## 🔄 改进概述

将 GitHub 监控从固定数量限制（20个活动）改为基于时间范围的监控，确保获取指定时间段内的所有活动。

## 🛠️ 主要改进

### 1. 时间范围过滤

**修改前**：
```python
for event in events[:20]:  # Limit to recent 20 events
```

**修改后**：
```python
def _parse_github_events(self, events: List[Dict], username: str, time_range_hours: int = 24) -> List[Dict[str, Any]]:
    """Parse GitHub events into activities based on time range."""
    activities = []
    
    # Calculate time range cutoff
    cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
    logger.info(f"Processing GitHub events from {cutoff_time} to now")
    
    for event in events:  # Process all events within time range
        try:
            # Check if event is within time range
            event_time = datetime.fromisoformat(event.get("created_at", "").replace("Z", "+00:00"))
            if event_time < cutoff_time:
                # Stop processing if we reach events outside time range
                logger.info(f"Reached event outside time range ({event_time}), stopping processing")
                break
            
            # Process event...
```

### 2. 智能处理逻辑

- **时间范围计算**：基于当前时间减去指定小时数计算截止时间
- **事件过滤**：只处理在时间范围内的 GitHub 事件
- **早期停止**：一旦遇到超出时间范围的事件就停止处理
- **详细日志**：记录处理的事件数量和过滤的活动数量

### 3. 配置化时间范围

默认时间范围设置为 24 小时，可以通过修改 `time_range_hours` 参数调整：

```python
# 在 fetch_activities 方法中
activities = self._parse_github_events(events, username, time_range_hours=24)
```

## 📊 优势对比

### 基于数量的限制（旧方式）
- ❌ 可能遗漏重要活动
- ❌ 无法保证时间覆盖范围
- ❌ 对于活跃用户数据不完整
- ❌ 硬编码限制不够灵活

### 基于时间的过滤（新方式）
- ✅ 确保获取指定时间段内的所有活动
- ✅ 数据更完整和准确
- ✅ 可以根据监控频率调整时间范围
- ✅ 避免处理过期的历史数据
- ✅ 性能更优（早期停止处理）

## 🔧 配置选项

### 时间范围设置

可以通过修改 `time_range_hours` 参数来调整监控时间范围：

```python
# 监控最近 12 小时的活动
activities = self._parse_github_events(events, username, time_range_hours=12)

# 监控最近 48 小时的活动
activities = self._parse_github_events(events, username, time_range_hours=48)

# 监控最近 7 天的活动
activities = self._parse_github_events(events, username, time_range_hours=168)  # 7 * 24
```

### 推荐配置

根据不同的监控频率：

| 监控频率 | 推荐时间范围 | 说明 |
|---------|-------------|------|
| 每30分钟 | 1-2小时 | 快速响应，减少重复 |
| 每小时 | 2-4小时 | 平衡性能和完整性 |
| 每2小时 | 4-8小时 | 标准配置 |
| 每天 | 24-48小时 | 完整覆盖 |

## 📈 性能优化

### 1. 早期停止机制

```python
if event_time < cutoff_time:
    # Stop processing if we reach events outside time range
    logger.info(f"Reached event outside time range ({event_time}), stopping processing")
    break
```

### 2. 详细统计信息

```python
logger.info(f"Processed {processed_count} events, filtered {filtered_count} activities within {time_range_hours}h time range")
```

### 3. 内存优化

- 只处理时间范围内的事件
- 避免存储过期数据
- 减少数据库写入操作

## 🚀 使用示例

### 测试时间范围监控

```bash
# 重启后端服务
./start.sh backend

# 手动运行监控
curl -X POST http://localhost:8000/api/v1/monitoring/run-monitoring

# 查看日志中的时间范围信息
tail -f logs/inspector_cursor.log | grep "Processing GitHub events"
```

### 查看监控结果

```bash
# 获取监控统计
curl -s http://localhost:8000/api/v1/monitoring/stats | jq

# 获取活动列表
curl -s http://localhost:8000/api/v1/monitoring/activities | jq length
```

## 🔍 日志示例

修改后的监控会输出详细的日志信息：

```
2025-08-10 15:30:00,123 - app.services.monitors.github_monitor - INFO - Processing GitHub events from 2025-08-09 15:30:00 to now
2025-08-10 15:30:01,456 - app.services.monitors.github_monitor - INFO - Reached event outside time range (2025-08-09 14:30:00), stopping processing
2025-08-10 15:30:01,789 - app.services.monitors.github_monitor - INFO - Processed 15 events, filtered 12 activities within 24h time range
```

## ⚠️ 注意事项

1. **API 限制**：GitHub API 仍然有速率限制，时间范围过大可能触发限制
2. **性能考虑**：时间范围过大可能影响处理性能
3. **数据完整性**：确保时间范围覆盖监控间隔，避免遗漏数据
4. **时区处理**：所有时间都使用 UTC 时间进行计算

## 🔄 未来扩展

### 1. 配置化时间范围

可以将时间范围添加到系统设置中：

```python
# app/core/config/settings.py
monitoring_time_range_hours: int = Field(
    default=24, 
    description="Time range for monitoring activities in hours"
)
```

### 2. 动态时间范围

根据监控频率动态调整时间范围：

```python
def get_dynamic_time_range(self, monitoring_interval_minutes: int) -> int:
    """Calculate time range based on monitoring interval."""
    if monitoring_interval_minutes <= 30:
        return 2  # 2 hours for frequent monitoring
    elif monitoring_interval_minutes <= 60:
        return 4  # 4 hours for hourly monitoring
    else:
        return 24  # 24 hours for daily monitoring
```

### 3. 多平台支持

将时间范围过滤扩展到其他监控平台（LinkedIn 等）。

---

现在您的 GitHub 监控将基于时间范围而不是固定数量来处理活动，确保获取到指定时间段内的所有相关活动！
