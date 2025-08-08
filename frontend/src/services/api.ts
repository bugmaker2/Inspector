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

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 成员相关API
export const membersApi = {
  getAll: () => api.get('/members/'),
  create: (data: any) => api.post('/members/', data),
  update: (id: number, data: any) => api.put(`/members/${id}`, data),
  delete: (id: number) => api.delete(`/members/${id}`),
  addSocialProfile: (memberId: number, data: any) => 
    api.post(`/members/${memberId}/social-profiles`, data),
  getSocialProfiles: (memberId: number) => 
    api.get(`/members/${memberId}/social-profiles`),
  deleteSocialProfile: (memberId: number, profileId: number) => 
    api.delete(`/members/${memberId}/social-profiles/${profileId}`),
};

// 监控相关API
export const monitoringApi = {
  getStats: () => api.get('/monitoring/stats'),
  runMonitoring: () => api.post('/monitoring/run-monitoring'),
  getActivities: () => api.get('/monitoring/activities'),
  generateDailySummary: () => api.post('/monitoring/generate-daily-summary'),
  generateWeeklySummary: () => api.post('/monitoring/generate-weekly-summary'),
  getSummaries: (language?: string) => 
    api.get(`/monitoring/summaries${language ? `?language=${language}` : ''}`),
  generateStreamingSummary: (summaryType: string, language?: string) => 
    api.post(`/monitoring/generate-${summaryType}-summary-streaming${language ? `?language=${language}` : ''}`),
};

// 设置相关API
export const settingsApi = {
  getSystemSettings: () => api.get('/settings/system'),
  updateSystemSettings: (data: any) => api.put('/settings/system', data),
  getApiSettings: () => api.get('/settings/api'),
  updateApiSettings: (data: any) => api.put('/settings/api', data),
  testApiConnection: (data: any) => api.post('/settings/test-api', data),
};

// 导出相关API
export const exportApi = {
  // 活动导出
  exportActivitiesCsv: (params?: any) => 
    api.get('/export/activities/csv', { params, responseType: 'blob' }),
  exportActivitiesExcel: (params?: any) => 
    api.get('/export/activities/excel', { params, responseType: 'blob' }),
  
  // 总结导出
  exportSummariesPdf: (params?: any) => 
    api.get('/export/summaries/pdf', { params, responseType: 'blob' }),
  
  // 成员导出
  exportMembersJson: (includeInactive?: boolean) => 
    api.get('/export/members/json', { 
      params: { include_inactive: includeInactive }, 
      responseType: 'blob' 
    }),
  
  // 仪表板统计导出
  exportDashboardStats: () => 
    api.get('/export/dashboard/stats', { responseType: 'blob' }),
};

// 通知相关API
export const notificationsApi = {
  getAll: (limit?: number, unreadOnly?: boolean) => 
    api.get('/notifications/', { 
      params: { limit, unread_only: unreadOnly } 
    }),
  create: (data: any) => api.post('/notifications/', data),
  markAsRead: (id: number) => api.put(`/notifications/${id}/read`),
  markAllAsRead: () => api.put('/notifications/read-all'),
  delete: (id: number) => api.delete(`/notifications/${id}`),
};

// 健康检查API
export const healthApi = {
  getHealth: () => api.get('/health'),
  getDetailedHealth: () => api.get('/health/detailed'),
};

// 通用下载函数
export const downloadFile = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export default api; 