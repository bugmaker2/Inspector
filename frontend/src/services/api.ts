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

// API base URL - automatically detect environment
const getApiBaseUrl = () => {
  if (process.env.NODE_ENV === 'production') {
    // In production, use relative URLs or the actual domain
    return window.location.origin + '/api';
  }
  // In development, use the proxy configuration
  return '/api';
};

const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any authentication headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized access
      console.error('Unauthorized access');
    } else if (error.response?.status === 500) {
      // Handle server errors
      console.error('Server error:', error.response.data);
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const apiEndpoints = {
  // Health check
  health: '/health',
  
  // Members
  members: '/v1/members',
  member: (id: string) => `/v1/members/${id}`,
  
  // Activities
  activities: '/v1/activities',
  activity: (id: string) => `/v1/activities/${id}`,
  
  // Summaries
  summaries: '/v1/summaries',
  summary: (id: string) => `/v1/summaries/${id}`,
  
  // Notifications
  notifications: '/v1/notifications',
  notification: (id: string) => `/v1/notifications/${id}`,
  
  // Settings
  settings: '/v1/settings',
  
  // Export
  export: '/v1/export',
  
  // Monitoring
  monitoring: '/v1/monitoring',
  monitoringStatus: '/v1/monitoring/status',
  startMonitoring: '/v1/monitoring/start',
  stopMonitoring: '/v1/monitoring/stop',
};

// API functions
export const apiService = {
  // Health check
  async getHealth() {
    const response = await api.get(apiEndpoints.health);
    return response.data;
  },

  // Members
  async getMembers() {
    const response = await api.get(apiEndpoints.members);
    return response.data;
  },

  async getMember(id: string) {
    const response = await api.get(apiEndpoints.member(id));
    return response.data;
  },

  async createMember(data: any) {
    const response = await api.post(apiEndpoints.members, data);
    return response.data;
  },

  async updateMember(id: string, data: any) {
    const response = await api.put(apiEndpoints.member(id), data);
    return response.data;
  },

  async deleteMember(id: string) {
    const response = await api.delete(apiEndpoints.member(id));
    return response.data;
  },

  // Activities
  async getActivities(params?: any) {
    const response = await api.get(apiEndpoints.activities, { params });
    return response.data;
  },

  async getActivity(id: string) {
    const response = await api.get(apiEndpoints.activity(id));
    return response.data;
  },

  // Summaries
  async getSummaries(params?: any) {
    const response = await api.get(apiEndpoints.summaries, { params });
    return response.data;
  },

  async getSummary(id: string) {
    const response = await api.get(apiEndpoints.summary(id));
    return response.data;
  },

  async createSummary(data: any) {
    const response = await api.post(apiEndpoints.summaries, data);
    return response.data;
  },

  // Notifications
  async getNotifications(params?: any) {
    const response = await api.get(apiEndpoints.notifications, { params });
    return response.data;
  },

  async getNotification(id: string) {
    const response = await api.get(apiEndpoints.notification(id));
    return response.data;
  },

  async markNotificationRead(id: string) {
    const response = await api.put(apiEndpoints.notification(id), { read: true });
    return response.data;
  },

  // Settings
  async getSettings() {
    const response = await api.get(apiEndpoints.settings);
    return response.data;
  },

  async updateSettings(data: any) {
    const response = await api.put(apiEndpoints.settings, data);
    return response.data;
  },

  // Export
  async exportData(format: 'csv' | 'excel' | 'pdf', params?: any) {
    const response = await api.get(apiEndpoints.export, {
      params: { format, ...params },
      responseType: 'blob',
    });
    return response.data;
  },

  // Monitoring
  async getMonitoringStatus() {
    const response = await api.get(apiEndpoints.monitoringStatus);
    return response.data;
  },

  async startMonitoring() {
    const response = await api.post(apiEndpoints.startMonitoring);
    return response.data;
  },

  async stopMonitoring() {
    const response = await api.post(apiEndpoints.stopMonitoring);
    return response.data;
  },
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