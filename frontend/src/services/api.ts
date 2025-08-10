import axios from 'axios';

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
  members: '/v1/members/',
  member: (id: string) => `/v1/members/${id}`,
  
  // Activities
  activities: '/v1/monitoring/activities',
  activity: (id: string) => `/v1/monitoring/activities/${id}`,
  
  // Summaries
  summaries: '/v1/summaries/',
  summary: (id: string) => `/v1/summaries/${id}`,
  
  // Notifications
  notifications: '/v1/notifications/',
  notification: (id: string) => `/v1/notifications/${id}`,
  
  // Settings
  settings: '/v1/settings/',
  
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

  async getMember(id: string | number) {
    const response = await api.get(apiEndpoints.member(id.toString()));
    return response.data;
  },

  async createMember(data: any) {
    const response = await api.post(apiEndpoints.members, data);
    return response.data;
  },

  async updateMember(id: string | number, data: any) {
    const response = await api.put(apiEndpoints.member(id.toString()), data);
    return response.data;
  },

  async deleteMember(id: string | number) {
    const response = await api.delete(apiEndpoints.member(id.toString()));
    return response.data;
  },

  // Social Profiles
  async getMemberSocialProfiles(memberId: string | number) {
    const response = await api.get(`/v1/members/${memberId}/social-profiles`);
    return response.data;
  },

  async createSocialProfile(memberId: string | number, data: any) {
    const response = await api.post(`/v1/members/${memberId}/social-profiles`, data);
    return response.data;
  },

  async updateSocialProfile(memberId: string | number, profileId: string | number, data: any) {
    const response = await api.put(`/v1/members/${memberId}/social-profiles/${profileId}`, data);
    return response.data;
  },

  async deleteSocialProfile(memberId: string | number, profileId: string | number) {
    const response = await api.delete(`/v1/members/${memberId}/social-profiles/${profileId}`);
    return response.data;
  },

  // Activities
  async getActivities(params?: any) {
    const response = await api.get(apiEndpoints.activities, { params });
    return response.data;
  },

  async getActivity(id: string | number) {
    const response = await api.get(apiEndpoints.activity(id.toString()));
    return response.data;
  },

  // Summaries
  async getSummaries(params?: any) {
    const response = await api.get(apiEndpoints.summaries, { params });
    return response.data;
  },

  async getSummary(id: string | number) {
    const response = await api.get(apiEndpoints.summary(id.toString()));
    return response.data;
  },

  async createSummary(data: any) {
    const response = await api.post(apiEndpoints.summaries, data);
    return response.data;
  },

  async generateDailySummary(date?: string) {
    const response = await api.post('/v1/monitoring/generate-daily-summary', { date });
    return response.data;
  },

  async generateWeeklySummary(startDate?: string) {
    const response = await api.post('/v1/monitoring/generate-weekly-summary', { start_date: startDate });
    return response.data;
  },

  async generateDailySummaryStream(date?: string) {
    const response = await api.post('/v1/monitoring/generate-daily-summary-stream', { date }, {
      responseType: 'stream'
    });
    return response.data;
  },

  // Notifications
  async getNotifications(params?: any) {
    const response = await api.get(apiEndpoints.notifications, { params });
    return response.data;
  },

  async getNotification(id: string | number) {
    const response = await api.get(apiEndpoints.notification(id.toString()));
    return response.data;
  },

  async markNotificationRead(id: string | number) {
    const response = await api.put(apiEndpoints.notification(id.toString()), { read: true });
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
  async exportData(format: 'csv' | 'excel' | 'pdf' | 'json', params?: any) {
    const { type, ...otherParams } = params || {};
    
    // Use specific endpoints based on type and format
    let endpoint = '';
    if (type === 'members') {
      if (format === 'json') {
        endpoint = '/v1/export/members/json';
      } else if (format === 'csv') {
        endpoint = '/v1/export/members/csv';
      }
    } else if (type === 'activities') {
      if (format === 'csv') {
        endpoint = '/v1/export/activities/csv';
      } else if (format === 'excel') {
        endpoint = '/v1/export/activities/excel';
      }
    } else if (type === 'summaries') {
      if (format === 'pdf') {
        endpoint = '/v1/export/summaries/pdf';
      } else if (format === 'json') {
        endpoint = '/v1/export/summaries/json';
      }
    } else if (type === 'stats') {
      if (format === 'json') {
        endpoint = '/v1/export/dashboard/stats';
      } else if (format === 'csv') {
        endpoint = '/v1/export/stats/csv';
      }
    }
    
    if (!endpoint) {
      throw new Error(`Unsupported export type: ${type} with format: ${format}`);
    }
    
    const response = await api.get(endpoint, {
      params: otherParams,
      responseType: 'blob',
    });
    return response.data;
  },

  // Monitoring
  async getMonitoringStatus() {
    const response = await api.get(apiEndpoints.monitoringStatus);
    return response.data;
  },

  async getMonitoringStats() {
    const response = await api.get('/v1/monitoring/stats');
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

// 导出各个 API 模块以兼容现有代码
export const membersApi = {
  getMembers: apiService.getMembers,
  getMember: apiService.getMember,
  createMember: apiService.createMember,
  updateMember: apiService.updateMember,
  deleteMember: apiService.deleteMember,
  getMemberSocialProfiles: apiService.getMemberSocialProfiles,
  createSocialProfile: apiService.createSocialProfile,
  updateSocialProfile: apiService.updateSocialProfile,
  deleteSocialProfile: apiService.deleteSocialProfile,
};

export const monitoringApi = {
  getMonitoringStatus: apiService.getMonitoringStatus,
  getMonitoringStats: apiService.getMonitoringStats,
  startMonitoring: apiService.startMonitoring,
  stopMonitoring: apiService.stopMonitoring,
  getActivities: apiService.getActivities,
  getActivity: apiService.getActivity,
};

export const exportApi = {
  exportData: apiService.exportData,
};

export const notificationsApi = {
  getNotifications: apiService.getNotifications,
  getNotification: apiService.getNotification,
  markNotificationRead: apiService.markNotificationRead,
};

export const settingsApi = {
  getSettings: apiService.getSettings,
  updateSettings: apiService.updateSettings,
};

export default api; 