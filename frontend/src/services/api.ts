import axios from 'axios';
import {
  Member,
  MemberCreate,
  MemberUpdate,
  SocialProfile,
  SocialProfileCreate,
  SocialProfileUpdate,
  Activity,
  Summary,
  DashboardStats,
  MonitoringResult,
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 成员管理API
export const membersApi = {
  // 获取所有成员
  getAll: async (params?: { skip?: number; limit?: number; active_only?: boolean }): Promise<Member[]> => {
    const response = await api.get(`${API_PREFIX}/members/`, { params });
    return response.data;
  },

  // 获取单个成员
  getById: async (id: number): Promise<Member> => {
    const response = await api.get(`${API_PREFIX}/members/${id}`);
    return response.data;
  },

  // 创建成员
  create: async (member: MemberCreate): Promise<Member> => {
    const response = await api.post(`${API_PREFIX}/members/`, member);
    return response.data;
  },

  // 更新成员
  update: async (id: number, member: MemberUpdate): Promise<Member> => {
    const response = await api.put(`${API_PREFIX}/members/${id}`, member);
    return response.data;
  },

  // 删除成员
  delete: async (id: number): Promise<void> => {
    await api.delete(`${API_PREFIX}/members/${id}`);
  },
};

// 社交配置API
export const socialProfilesApi = {
  // 获取成员的社交配置
  getByMemberId: async (memberId: number): Promise<SocialProfile[]> => {
    const response = await api.get(`${API_PREFIX}/members/${memberId}/social-profiles`);
    return response.data;
  },

  // 创建社交配置
  create: async (memberId: number, profile: SocialProfileCreate): Promise<SocialProfile> => {
    const response = await api.post(`${API_PREFIX}/members/${memberId}/social-profiles`, profile);
    return response.data;
  },

  // 更新社交配置
  update: async (memberId: number, profileId: number, profile: SocialProfileUpdate): Promise<SocialProfile> => {
    const response = await api.put(`${API_PREFIX}/members/${memberId}/social-profiles/${profileId}`, profile);
    return response.data;
  },

  // 删除社交配置
  delete: async (memberId: number, profileId: number): Promise<void> => {
    await api.delete(`${API_PREFIX}/members/${memberId}/social-profiles/${profileId}`);
  },
};

// 监控管理API
export const monitoringApi = {
  // 运行监控
  runMonitoring: async (): Promise<MonitoringResult> => {
    const response = await api.post(`${API_PREFIX}/monitoring/run-monitoring`);
    return response.data;
  },

  // 监控特定配置
  monitorProfile: async (profileId: number): Promise<MonitoringResult> => {
    const response = await api.post(`${API_PREFIX}/monitoring/monitor-profile/${profileId}`);
    return response.data;
  },

  // 获取统计信息
  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get(`${API_PREFIX}/monitoring/stats`);
    return response.data;
  },

  // 获取活动列表
  getActivities: async (params?: {
    skip?: number;
    limit?: number;
    platform?: string;
    member_id?: number;
  }): Promise<Activity[]> => {
    const response = await api.get(`${API_PREFIX}/monitoring/activities`, { params });
    return response.data;
  },

  // 生成每日总结
  generateDailySummary: async (date?: string): Promise<Summary> => {
    const params = date ? { date } : {};
    const response = await api.post(`${API_PREFIX}/monitoring/generate-daily-summary`, null, { params });
    return response.data;
  },

  // 生成每周总结
  generateWeeklySummary: async (startDate?: string): Promise<Summary> => {
    const params = startDate ? { start_date: startDate } : {};
    const response = await api.post(`${API_PREFIX}/monitoring/generate-weekly-summary`, null, { params });
    return response.data;
  },

  // 获取总结列表
  getSummaries: async (params?: {
    skip?: number;
    limit?: number;
    summary_type?: string;
    language?: string;  // 添加语言参数
  }): Promise<Summary[]> => {
    const response = await api.get(`${API_PREFIX}/monitoring/summaries`, { params });
    return response.data;
  },

  // 获取单个总结
  getSummary: async (id: number, language?: string): Promise<Summary> => {  // 添加语言参数
    const params = language ? { language } : {};
    const response = await api.get(`${API_PREFIX}/monitoring/summaries/${id}`, { params });
    return response.data;
  },
};

// 健康检查API
export const healthApi = {
  check: async (): Promise<{ status: string; timestamp: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api; 