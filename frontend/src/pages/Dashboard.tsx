import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  ChartBarIcon, 
  UsersIcon, 
  DocumentTextIcon, 
  ClockIcon,
  ArrowDownTrayIcon,
  BellIcon
} from '@heroicons/react/24/outline';
import { monitoringApi, exportApi, notificationsApi, downloadFile } from '../services/api';
import { DashboardStats, Summary, Notification } from '../types';
import toast from 'react-hot-toast';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [latestSummary, setLatestSummary] = useState<Summary | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [summaryExpanded, setSummaryExpanded] = useState(false);

  useEffect(() => {
    loadDashboardData();
    loadNotifications();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsResponse, summariesResponse] = await Promise.all([
        monitoringApi.getStats(),
        monitoringApi.getSummaries()
      ]);
      
      setStats(statsResponse.data);
      if (summariesResponse.data.length > 0) {
        setLatestSummary(summariesResponse.data[0]);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast.error('加载仪表板数据失败');
    } finally {
      setLoading(false);
    }
  };

  const loadNotifications = async () => {
    try {
      const response = await notificationsApi.getAll(5, true);
      setNotifications(response.data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  };

  const handleRunMonitoring = async () => {
    try {
      await monitoringApi.runMonitoring();
      toast.success('监控任务已启动');
      loadDashboardData();
    } catch (error) {
      console.error('Failed to run monitoring:', error);
      toast.error('启动监控失败');
    }
  };

  const handleGenerateSummary = async () => {
    try {
      await monitoringApi.generateDailySummary();
      toast.success('总结生成任务已启动');
      loadDashboardData();
    } catch (error) {
      console.error('Failed to generate summary:', error);
      toast.error('生成总结失败');
    }
  };

  const handleExport = async (type: string) => {
    setExporting(true);
    try {
      let response;
      let filename;
      
      switch (type) {
        case 'activities-csv':
          response = await exportApi.exportActivitiesCsv();
          filename = `activities_${new Date().toISOString().split('T')[0]}.csv`;
          break;
        case 'activities-excel':
          response = await exportApi.exportActivitiesExcel();
          filename = `activities_${new Date().toISOString().split('T')[0]}.xlsx`;
          break;
        case 'summaries-pdf':
          response = await exportApi.exportSummariesPdf();
          filename = `summaries_${new Date().toISOString().split('T')[0]}.pdf`;
          break;
        case 'members-json':
          response = await exportApi.exportMembersJson();
          filename = `members_${new Date().toISOString().split('T')[0]}.json`;
          break;
        case 'dashboard-stats':
          response = await exportApi.exportDashboardStats();
          filename = `dashboard_stats_${new Date().toISOString().split('T')[0]}.json`;
          break;
        default:
          throw new Error('Unknown export type');
      }
      
      downloadFile(response.data, filename);
      toast.success('导出成功');
    } catch (error) {
      console.error('Export failed:', error);
      toast.error('导出失败');
    } finally {
      setExporting(false);
    }
  };

  const markNotificationAsRead = async (id: number) => {
    try {
      await notificationsApi.markAsRead(id);
      loadNotifications();
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">仪表板</h1>
        
        {/* 通知图标 */}
        <div className="relative">
          <button className="p-2 text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">
            <BellIcon className="h-6 w-6" />
            {notifications.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                {notifications.length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <UsersIcon className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">总成员数</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.total_members || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">今日活动</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.activities_today || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-yellow-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">本周活动</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.activities_this_week || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <DocumentTextIcon className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">总活动数</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.total_activities || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* 快速操作 */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">快速操作</h2>
        <div className="flex flex-wrap gap-4">
          <button
            onClick={handleRunMonitoring}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <ChartBarIcon className="h-4 w-4 mr-2" />
            运行监控
          </button>
          
          <button
            onClick={handleGenerateSummary}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            生成总结
          </button>
        </div>
      </div>

      {/* 导出功能 */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">数据导出</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <button
            onClick={() => handleExport('activities-csv')}
            disabled={exporting}
            className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            导出活动 (CSV)
          </button>
          
          <button
            onClick={() => handleExport('activities-excel')}
            disabled={exporting}
            className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            导出活动 (Excel)
          </button>
          
          <button
            onClick={() => handleExport('summaries-pdf')}
            disabled={exporting}
            className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            导出总结 (PDF)
          </button>
          
          <button
            onClick={() => handleExport('members-json')}
            disabled={exporting}
            className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            导出成员 (JSON)
          </button>
          
          <button
            onClick={() => handleExport('dashboard-stats')}
            disabled={exporting}
            className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            导出统计 (JSON)
          </button>
        </div>
        {exporting && (
          <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
            正在导出，请稍候...
          </div>
        )}
      </div>

      {/* 最新总结 */}
      {latestSummary && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">最新总结</h2>
          <div className="space-y-2">
            <h3 className="font-medium text-gray-900 dark:text-white">{latestSummary.title}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              类型: {latestSummary.summary_type} | 
              成员数: {latestSummary.member_count} | 
              活动数: {latestSummary.activity_count}
            </p>
            <p className="text-gray-700 dark:text-gray-300 text-sm line-clamp-3">
              {latestSummary.content}
            </p>
          </div>
        </div>
      )}

      {/* 通知列表 */}
      {notifications.length > 0 && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">最新通知</h2>
          <div className="space-y-3">
            {notifications.map((notification) => (
              <div
                key={notification.id}
                className={`p-3 rounded-lg border-l-4 ${
                  notification.type === 'error' ? 'border-red-500 bg-red-50 dark:bg-red-900/20' :
                  notification.type === 'warning' ? 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20' :
                  notification.type === 'success' ? 'border-green-500 bg-green-50 dark:bg-green-900/20' :
                  'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">{notification.title}</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{notification.message}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                      {new Date(notification.created_at).toLocaleString()}
                    </p>
                  </div>
                  {!notification.read && (
                    <button
                      onClick={() => markNotificationAsRead(notification.id)}
                      className="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                    >
                      标记已读
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard; 