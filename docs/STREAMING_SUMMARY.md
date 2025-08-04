# 流式报告生成功能

## 概述

Inspector 项目现在支持流式报告生成，用户可以在报告生成过程中实时看到进度，而不需要等待整个生成过程完成。这大大改善了用户体验，特别是在生成大型报告时。

## 功能特性

### 1. 实时进度显示
- 显示当前生成阶段（数据收集、中文生成、英文生成、保存等）
- 实时进度条显示完成百分比
- 详细的状态消息

### 2. 流式响应
- 使用 Server-Sent Events (SSE) 技术
- 支持实时数据传输
- 减少超时风险

### 3. 错误处理
- 实时错误反馈
- 详细的错误信息
- 优雅的错误恢复

### 4. 向后兼容
- 保留原有的同步生成接口
- 新增流式生成接口
- 前端自动选择最佳方式

## 技术实现

### 后端实现

#### 1. 流式API端点

```python
@router.post("/generate-daily-summary-stream")
async def generate_daily_summary_stream(
    date: str = None,
    db: Session = Depends(get_db)
):
    """Generate daily activity summary with streaming response."""
    # 实现流式响应
```

#### 2. LLM流式生成

```python
async def _generate_language_content_stream(
    self,
    activity_data: List[Dict],
    summary_type: str,
    start_date: datetime,
    end_date: datetime,
    language: str
) -> Optional[str]:
    """Generate content in specific language with streaming support."""
    # 支持OpenAI和阿里云通义千问的流式生成
```

#### 3. Server-Sent Events格式

```python
# 进度更新
yield f"data: {json.dumps({'type': 'progress', 'message': '正在生成中文总结...', 'progress': 30})}\n\n"

# 完成信号
yield f"data: {json.dumps({'type': 'complete', 'summary': summary_data})}\n\n"

# 错误信号
yield f"data: {json.dumps({'type': 'error', 'message': '生成失败'})}\n\n"
```

### 前端实现

#### 1. 流式API调用

```typescript
generateDailySummaryStream: async (
  date?: string,
  onProgress?: (data: any) => void,
  onComplete?: (summary: Summary) => void,
  onError?: (error: string) => void
): Promise<void> => {
  // 使用fetch API处理流式响应
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    // 解析SSE数据
    const lines = decoder.decode(value).split('\n');
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        onProgress?.(data);
      }
    }
  }
}
```

#### 2. 进度显示组件

```tsx
const [generationProgress, setGenerationProgress] = useState<{
  progress: number;
  message: string;
  isVisible: boolean;
}>({
  progress: 0,
  message: '',
  isVisible: false
});

// 进度条组件
{generationProgress.isVisible && (
  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
    <div className="flex items-center justify-between mb-2">
      <span className="text-sm font-medium text-blue-800">
        {generationProgress.message}
      </span>
      <span className="text-sm text-blue-600">
        {generationProgress.progress}%
      </span>
    </div>
    <div className="w-full bg-blue-200 rounded-full h-2">
      <div 
        className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
        style={{ width: `${generationProgress.progress}%` }}
      ></div>
    </div>
  </div>
)}
```

## 使用方法

### 1. 生成每日总结（流式）

```typescript
await monitoringApi.generateDailySummaryStream(
  undefined, // date
  (data) => {
    // 进度回调
    if (data.type === 'progress') {
      setGenerationProgress({
        progress: data.progress,
        message: data.message,
        isVisible: true
      });
    }
  },
  (summary) => {
    // 完成回调
    setGenerationProgress({
      progress: 100,
      message: '生成完成！',
      isVisible: false
    });
    toast.success('每日总结生成成功');
  },
  (error) => {
    // 错误回调
    setGenerationProgress({
      progress: 0,
      message: '',
      isVisible: false
    });
    toast.error(`生成失败: ${error}`);
  }
);
```

### 2. 生成每周总结（流式）

```typescript
await monitoringApi.generateWeeklySummaryStream(
  undefined, // startDate
  onProgress,
  onComplete,
  onError
);
```

## 生成流程

### 1. 数据收集阶段 (0-20%)
- 验证LLM配置
- 收集指定时间范围的活动数据
- 准备生成参数

### 2. 中文内容生成 (20-60%)
- 调用LLM API生成中文总结
- 实时显示生成进度
- 处理流式响应

### 3. 英文内容生成 (60-90%)
- 调用LLM API生成英文总结
- 实时显示生成进度
- 处理流式响应

### 4. 保存阶段 (90-100%)
- 创建总结记录
- 保存到数据库
- 返回完整结果

## 错误处理

### 1. 常见错误类型

- **配置错误**: LLM API未配置
- **数据错误**: 未找到活动数据
- **网络错误**: API调用超时
- **生成错误**: LLM生成失败

### 2. 错误恢复

- 自动重试机制
- 用户友好的错误消息
- 详细的错误日志

## 性能优化

### 1. 并发处理
- 支持多个用户同时生成报告
- 异步处理避免阻塞

### 2. 缓存机制
- 缓存活动数据
- 减少重复计算

### 3. 超时控制
- 设置合理的超时时间
- 自动取消长时间运行的任务

## 兼容性

### 1. 浏览器支持
- 现代浏览器支持fetch API和ReadableStream
- 降级到同步模式（如果需要）

### 2. API兼容性
- 保留原有同步接口
- 新增流式接口
- 前端自动选择最佳方式

## 监控和日志

### 1. 性能监控
- 生成时间统计
- 成功率监控
- 用户行为分析

### 2. 错误日志
- 详细的错误信息
- 堆栈跟踪
- 用户上下文

## 未来改进

### 1. 功能增强
- 支持更多报告类型
- 自定义生成模板
- 批量生成功能

### 2. 性能优化
- 更智能的进度估算
- 并行生成优化
- 缓存策略改进

### 3. 用户体验
- 更丰富的进度动画
- 可中断的生成过程
- 生成历史记录 