# Dashboard 数据显示问题修复说明

## 🔍 问题描述

用户反映 Dashboard 中看不到成员统计数据和活动统计数据，即使监控已经成功运行并找到了20个新活动。

## 🛠️ 问题原因

通过代码分析发现，前端 Dashboard 组件调用了错误的 API 端点：

1. **错误的 API 调用**：前端调用 `apiService.getMonitoringStatus()` 而不是 `apiService.getMonitoringStats()`
2. **API 端点不匹配**：
   - `/api/v1/monitoring/status` 只返回监控服务状态
   - `/api/v1/monitoring/stats` 返回统计数据

### 具体问题

**在 `frontend/src/pages/Dashboard.tsx` 中：**
```typescript
// 问题代码
const loadDashboardData = async () => {
  try {
    const [statsResponse, summariesResponse] = await Promise.all([
      apiService.getMonitoringStatus(),  // ← 错误的 API 调用
      apiService.getSummaries()
    ]);
    
    setStats(statsResponse);  // ← 这里设置的是状态数据，不是统计数据
    // ...
  } catch (error) {
    // ...
  }
};
```

**API 返回数据对比：**

`/api/v1/monitoring/status` 返回：
```json
{
  "status": "ready",
  "timestamp": "2025-08-10T06:53:27.699968",
  "service": "monitoring"
}
```

`/api/v1/monitoring/stats` 返回：
```json
{
  "total_members": 1,
  "active_members": 1,
  "total_activities": 20,
  "activities_today": 20,
  "activities_this_week": 20,
  "latest_summary": null
}
```

## ✅ 解决方案

### 1. 添加缺失的 API 函数

在 `frontend/src/services/api.ts` 中添加 `getMonitoringStats` 函数：

```typescript
async getMonitoringStats() {
  const response = await api.get('/v1/monitoring/stats');
  return response.data;
},
```

### 2. 修复 Dashboard 组件

在 `frontend/src/pages/Dashboard.tsx` 中使用正确的 API 调用：

```typescript
// 修复后的代码
const loadDashboardData = async () => {
  try {
    const [statsResponse, summariesResponse] = await Promise.all([
      apiService.getMonitoringStats(),  // ← 正确的 API 调用
      apiService.getSummaries()
    ]);
    
    setStats(statsResponse);  // ← 现在设置的是统计数据
    if (summariesResponse.length > 0) {
      setLatestSummary(summariesResponse[0]);
    }
  } catch (error) {
    console.error('Failed to load dashboard data:', error);
    toast.error('加载仪表板数据失败');
  } finally {
    setLoading(false);
  }
};
```

### 3. 更新 API 导出

在 `monitoringApi` 导出中添加新函数：

```typescript
export const monitoringApi = {
  getMonitoringStatus: apiService.getMonitoringStatus,
  getMonitoringStats: apiService.getMonitoringStats,  // 新增
  startMonitoring: apiService.startMonitoring,
  stopMonitoring: apiService.stopMonitoring,
  getActivities: apiService.getActivities,
  getActivity: apiService.getActivity,
};
```

## 🧪 验证修复

### 测试 API 端点

```bash
# 1. 测试监控状态 API
curl -s http://localhost:8000/api/v1/monitoring/status
# 预期输出: {"status":"ready","timestamp":"...","service":"monitoring"}

# 2. 测试统计数据 API
curl -s http://localhost:8000/api/v1/monitoring/stats
# 预期输出: {"total_members":1,"active_members":1,"total_activities":20,"activities_today":20,"activities_this_week":20,"latest_summary":null}
```

### 前端验证

修复后，Dashboard 应该显示：
- **总成员数**: 1
- **今日活动**: 20
- **本周活动**: 20
- **总活动数**: 20

## 📝 相关 API 端点

### 监控状态 API
- `GET /api/v1/monitoring/status` - 获取监控服务状态
  - 返回：服务状态、时间戳、服务名称

### 统计数据 API
- `GET /api/v1/monitoring/stats` - 获取监控统计数据
  - 返回：成员数量、活动数量、总结信息

### 前端 API 函数
- `apiService.getMonitoringStatus()` - 获取监控状态
- `apiService.getMonitoringStats()` - 获取统计数据

## 🔧 故障排除

### 如果 Dashboard 仍然不显示数据

1. **检查后端服务**：确保后端服务正在运行
   ```bash
   ./start.sh backend
   ```

2. **检查 API 端点**：测试统计数据 API
   ```bash
   curl -s http://localhost:8000/api/v1/monitoring/stats
   ```

3. **检查前端控制台**：查看浏览器开发者工具中的错误信息

4. **清除浏览器缓存**：强制刷新页面 (Ctrl+F5 或 Cmd+Shift+R)

5. **重启前端服务**：重新启动开发服务器
   ```bash
   cd frontend && npm start
   ```

### 如果数据显示为 0

1. **检查监控是否运行**：确保监控任务已经执行
   ```bash
   curl -X POST http://localhost:8000/api/v1/monitoring/run-monitoring
   ```

2. **检查数据库状态**：使用数据库同步工具检查
   ```bash
   uv run python scripts/db_sync.py check
   ```

3. **检查活动数据**：查看是否有活动数据
   ```bash
   curl -s http://localhost:8000/api/v1/monitoring/activities
   ```

---

现在 Dashboard 应该能正确显示成员统计数据和活动统计数据了！
