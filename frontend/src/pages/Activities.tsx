import React, { useState, useEffect } from 'react';
import { monitoringApi } from '../services/api';
import { Activity } from '../types';
import toast from 'react-hot-toast';

const Activities: React.FC = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadActivities();
  }, []);

  const loadActivities = async () => {
    try {
      const data = await monitoringApi.getActivities({ limit: 50 });
      setActivities(data);
    } catch (error) {
      toast.error('加载活动列表失败');
      console.error('Failed to load activities:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">活动监控</h1>
        <p className="text-gray-600">查看团队成员的最新社交动态</p>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {activities.map((activity) => (
            <li key={activity.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                        activity.platform === 'github' ? 'bg-gray-100' :
                        activity.platform === 'linkedin' ? 'bg-blue-100' :
                        'bg-gray-100'
                      }`}>
                        <span className={`text-xs font-medium ${
                          activity.platform === 'github' ? 'text-gray-800' :
                          activity.platform === 'linkedin' ? 'text-blue-800' :
                          'text-gray-800'
                        }`}>
                          {activity.platform.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="flex items-center">
                        <p className="text-sm font-medium text-gray-900">
                          {activity.title || activity.activity_type || '未知活动'}
                        </p>
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          {activity.platform}
                        </span>
                      </div>
                      {activity.content && (
                        <p className="text-sm text-gray-500 mt-1">{activity.content}</p>
                      )}
                      <div className="flex items-center text-xs text-gray-500 mt-1">
                        <span>创建时间: {new Date(activity.created_at).toLocaleString()}</span>
                        {activity.published_at && (
                          <>
                            <span className="mx-2">•</span>
                            <span>发布时间: {new Date(activity.published_at).toLocaleString()}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  {activity.url && (
                    <div className="flex items-center">
                      <a
                        href={activity.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-900 text-sm"
                      >
                        查看原文
                      </a>
                    </div>
                  )}
                </div>
              </div>
            </li>
          ))}
        </ul>
        
        {activities.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">暂无活动记录</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Activities; 