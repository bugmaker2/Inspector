# Inspector 前端界面

## 概述

Inspector 前端是一个现代化的 React + TypeScript + Tailwind CSS 管理界面，提供了直观的交互式管理功能。

## 技术栈

- **React 18** - 用户界面框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 样式框架
- **React Router** - 路由管理
- **Axios** - HTTP 客户端
- **React Hot Toast** - 通知组件
- **Heroicons** - 图标库

## 功能特性

### 🏠 仪表板

- 实时统计数据展示
- 快速操作按钮
- 最新总结预览
- 一键运行监控

### 👥 成员管理

- 团队成员 CRUD 操作
- 社交配置管理
- 批量操作支持
- 搜索和筛选

### 📊 活动监控

- 实时活动列表
- 平台分类显示
- 时间轴展示
- 详情查看

### 📝 总结报告

- AI 生成报告展示
- 报告类型分类
- 时间范围筛选
- 内容预览

### ⚙️ 设置

- 系统配置
- API 密钥管理
- 通知设置
- 监控参数调整

## 快速开始

### 1. 环境要求

- Node.js 16+
- npm 或 yarn

### 2. 安装依赖

```bash
cd frontend
npm install
```

### 3. 启动开发服务器

```bash
npm start
```

前端将在 `http://localhost:3000` 启动。

### 4. 构建生产版本

```bash
npm run build
```

## 项目结构

```
frontend/
├── public/                 # 静态资源
│   ├── index.html         # HTML 模板
│   └── manifest.json      # Web 应用清单
├── src/
│   ├── components/        # 可复用组件
│   │   └── Layout.tsx     # 布局组件
│   ├── pages/            # 页面组件
│   │   ├── Dashboard.tsx  # 仪表板
│   │   ├── Members.tsx    # 成员管理
│   │   ├── Activities.tsx # 活动监控
│   │   ├── Summaries.tsx  # 总结报告
│   │   └── Settings.tsx   # 设置页面
│   ├── services/         # API 服务
│   │   └── api.ts        # API 客户端
│   ├── types/            # TypeScript 类型
│   │   └── index.ts      # 类型定义
│   ├── App.tsx           # 主应用组件
│   ├── index.tsx         # 应用入口
│   └── index.css         # 全局样式
├── package.json          # 项目配置
├── tailwind.config.js    # Tailwind 配置
├── tsconfig.json         # TypeScript 配置
└── postcss.config.js     # PostCSS 配置
```

## API 集成

前端通过 `src/services/api.ts` 与后端 API 进行通信：

### 主要 API 模块

- `membersApi` - 成员管理
- `socialProfilesApi` - 社交配置
- `monitoringApi` - 监控管理
- `healthApi` - 健康检查

### 配置代理

前端已配置代理到后端 API：

```json
{
  "proxy": "http://localhost:8000"
}
```

## 自定义配置

### 修改主题颜色

编辑 `tailwind.config.js`：

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          // ... 更多颜色
        },
      },
    },
  },
}
```

### 添加新页面

1. 在 `src/pages/` 创建新页面组件
2. 在 `src/App.tsx` 添加路由
3. 在 `src/components/Layout.tsx` 添加导航项

### 扩展 API 服务

在 `src/services/api.ts` 中添加新的 API 方法：

```typescript
export const newApi = {
  method: async (params: any): Promise<any> => {
    const response = await api.get('/api/v1/endpoint', { params });
    return response.data;
  },
};
```

## 开发指南

### 组件开发

使用函数式组件和 TypeScript：

```typescript
interface ComponentProps {
  title: string;
  onAction: () => void;
}

const MyComponent: React.FC<ComponentProps> = ({ title, onAction }) => {
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-lg font-medium">{title}</h2>
      <button onClick={onAction}>操作</button>
    </div>
  );
};
```

### 状态管理

使用 React Hooks 进行状态管理：

```typescript
const [data, setData] = useState<DataType[]>([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
  loadData();
}, []);
```

### 错误处理

使用 toast 通知用户：

```typescript
import toast from 'react-hot-toast';

try {
  await apiCall();
  toast.success('操作成功');
} catch (error) {
  toast.error('操作失败');
}
```

## 部署

### 开发环境

```bash
npm start
```

### 生产环境

```bash
npm run build
```

构建后的文件在 `build/` 目录中。

### Docker 部署

```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 故障排除

### 常见问题

1. **端口冲突**

   - 修改 `package.json` 中的 start 脚本
   - 或使用 `PORT=3001 npm start`
2. **API 连接失败**

   - 检查后端服务是否运行
   - 确认代理配置正确
   - 检查 CORS 设置
3. **样式不生效**

   - 确认 Tailwind CSS 配置正确
   - 检查 PostCSS 配置
   - 重启开发服务器

### 调试技巧

- 使用浏览器开发者工具
- 查看控制台错误信息
- 使用 React Developer Tools
- 检查网络请求

## 贡献

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License
