import React, { useState, useEffect } from 'react';
import { ArrowDownTrayIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { monitoringApi, exportApi, downloadFile, membersApi } from '../services/api';
import { Activity, Member, SearchFilterConfig } from '../types';
import SearchFilter from '../components/SearchFilter';
import toast from 'react-hot-toast';

const Activities: React.FC = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [filteredActivities, setFilteredActivities] = useState<Activity[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [activitiesResponse, membersResponse] = await Promise.all([
        monitoringApi.getActivities(),
        membersApi.getMembers()
      ]);
      
      setActivities(activitiesResponse);
      setFilteredActivities(activitiesResponse);
      setMembers(membersResponse);
    } catch (error) {
      console.error('Failed to load activities:', error);
      toast.error('加载活动数据失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query: string) => {
    if (!query.trim()) {
      setFilteredActivities(activities);
      return;
    }

    const filtered = activities.filter(activity => 
      activity.title?.toLowerCase().includes(query.toLowerCase()) ||
      activity.content?.toLowerCase().includes(query.toLowerCase()) ||
      activity.platform.toLowerCase().includes(query.toLowerCase()) ||
      activity.member?.name.toLowerCase().includes(query.toLowerCase())
    );
    setFilteredActivities(filtered);
  };

  const handleFilter = (filters: Record<string, string>) => {
    let filtered = activities;

    if (filters.platform) {
      filtered = filtered.filter(activity => activity.platform === filters.platform);
    }

    if (filters.member_id) {
      filtered = filtered.filter(activity => activity.member_id.toString() === filters.member_id);
    }

    if (filters.activity_type) {
      filtered = filtered.filter(activity => activity.activity_type === filters.activity_type);
    }

    setFilteredActivities(filtered);
  };

  const handleExport = async (type: string) => {
    setExporting(true);
    try {
      let response;
      let filename;
      
      switch (type) {
        case 'csv':
          response = await exportApi.exportData('csv');
          filename = `activities_${new Date().toISOString().split('T')[0]}.csv`;
          break;
        case 'excel':
          response = await exportApi.exportData('excel');
          filename = `activities_${new Date().toISOString().split('T')[0]}.xlsx`;
          break;
        default:
          throw new Error('Unknown export type');
      }
      
      downloadFile(response, filename);
      toast.success('导出成功');
    } catch (error) {
      console.error('Export failed:', error);
      toast.error('导出失败');
    } finally {
      setExporting(false);
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'github':
        return '🐙';
      case 'linkedin':
        return '💼';
      case 'twitter':
        return '🐦';
      default:
        return '📱';
    }
  };

  const getActivityTypeColor = (type?: string) => {
    switch (type) {
      case 'post':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'comment':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'like':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'follow':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
  };

  // 搜索过滤配置
  const filterConfigs: SearchFilterConfig[] = [
    {
      name: 'platform',
      label: '平台',
      options: [
        { value: 'github', label: 'GitHub' },
        { value: 'linkedin', label: 'LinkedIn' },
        { value: 'twitter', label: 'Twitter' }
      ]
    },
    {
      name: 'activity_type',
      label: '活动类型',
      options: [
        { value: 'post', label: '发布' },
        { value: 'comment', label: '评论' },
        { value: 'like', label: '点赞' },
        { value: 'follow', label: '关注' }
      ]
    }
  ];

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
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">活动监控</h1>
        
        {/* 导出按钮 */}
        <div className="flex gap-2">
          <button
            onClick={() => handleExport('csv')}
            disabled={exporting}
            className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            导出CSV
          </button>
          <button
            onClick={() => handleExport('excel')}
            disabled={exporting}
            className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            导出Excel
          </button>
        </div>
      </div>

      {/* 搜索和过滤 */}
      <SearchFilter
        onSearch={handleSearch}
        onFilter={handleFilter}
        placeholder="搜索活动内容、标题或成员..."
        filters={filterConfigs}
      />

      {/* 统计信息 */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600 dark:text-gray-400">
            共找到 {filteredActivities.length} 个活动
          </span>
          {exporting && (
            <span className="text-sm text-blue-600 dark:text-blue-400">
              正在导出，请稍候...
            </span>
          )}
        </div>
      </div>

      {/* 活动列表 */}
      <div className="space-y-4">
        {filteredActivities.length === 0 ? (
          <div className="text-center py-12">
            <MagnifyingGlassIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">没有找到活动</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              尝试调整搜索条件或运行监控任务
            </p>
          </div>
        ) : (
          filteredActivities.map((activity) => (
            <div
              key={activity.id}
              className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  {/* 平台图标 */}
                  <div className="flex-shrink-0">
                    <span className="text-2xl">{getPlatformIcon(activity.platform)}</span>
                  </div>
                  
                  {/* 活动内容 */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {activity.member?.name || '未知成员'}
                      </span>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        •
                      </span>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {activity.platform}
                      </span>
                      {activity.activity_type && (
                        <>
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            •
                          </span>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getActivityTypeColor(activity.activity_type)}`}>
                            {activity.activity_type}
                          </span>
                        </>
                      )}
                    </div>
                    
                    {activity.title && (
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                        {activity.title}
                      </h3>
                    )}
                    
                    {activity.content && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3">
                        {activity.content}
                      </p>
                    )}
                    
                    {activity.url && (
                      <a
                        href={activity.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 mt-2 inline-block"
                      >
                        查看原文 →
                      </a>
                    )}
                  </div>
                </div>
                
                {/* 时间信息 */}
                <div className="flex-shrink-0 ml-4">
                  <div className="text-xs text-gray-500 dark:text-gray-400 text-right">
                    <div>
                      {activity.published_at 
                        ? new Date(activity.published_at).toLocaleDateString()
                        : new Date(activity.created_at).toLocaleDateString()
                      }
                    </div>
                    <div>
                      {activity.published_at 
                        ? new Date(activity.published_at).toLocaleTimeString()
                        : new Date(activity.created_at).toLocaleTimeString()
                      }
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Activities; 