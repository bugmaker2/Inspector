import React, { useState, useEffect } from 'react';
import { 
  BellIcon, 
  CheckIcon, 
  TrashIcon, 
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { notificationsApi } from '../services/api';
import { Notification } from '../types';
import toast from 'react-hot-toast';

const Notifications: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUnreadOnly, setShowUnreadOnly] = useState(false);
  const [filteredNotifications, setFilteredNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    loadNotifications();
  }, []);

  useEffect(() => {
    if (showUnreadOnly) {
      setFilteredNotifications(notifications.filter(n => !n.read));
    } else {
      setFilteredNotifications(notifications);
    }
  }, [notifications, showUnreadOnly]);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response = await notificationsApi.getAll(100, false);
      setNotifications(response.data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
      toast.error('加载通知失败');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (id: number) => {
    try {
      await notificationsApi.markAsRead(id);
      toast.success('已标记为已读');
      loadNotifications();
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
      toast.error('操作失败');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationsApi.markAllAsRead();
      toast.success('已全部标记为已读');
      loadNotifications();
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
      toast.error('操作失败');
    }
  };

  const handleDeleteNotification = async (id: number) => {
    if (!window.confirm('确定要删除这条通知吗？')) return;
    
    try {
      await notificationsApi.delete(id);
      toast.success('通知已删除');
      loadNotifications();
    } catch (error) {
      console.error('Failed to delete notification:', error);
      toast.error('删除失败');
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      default:
        return <InformationCircleIcon className="h-5 w-5 text-blue-500" />;
    }
  };

  const getNotificationColor = (type: string, isRead: boolean) => {
    if (isRead) return 'bg-gray-50 dark:bg-gray-800';
    
    switch (type) {
      case 'error':
        return 'bg-red-50 dark:bg-red-900/20';
      case 'warning':
        return 'bg-yellow-50 dark:bg-yellow-900/20';
      case 'success':
        return 'bg-green-50 dark:bg-green-900/20';
      default:
        return 'bg-blue-50 dark:bg-blue-900/20';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">通知中心</h1>
          <p className="text-gray-600 dark:text-gray-400">系统通知和消息管理</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={showUnreadOnly}
              onChange={(e) => setShowUnreadOnly(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">仅显示未读</span>
          </label>
          
          {notifications.some(n => !n.read) && (
            <button
              onClick={handleMarkAllAsRead}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <CheckIcon className="h-4 w-4 mr-1" />
              全部标记为已读
            </button>
          )}
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        {filteredNotifications.length === 0 ? (
          <div className="text-center py-12">
            <BellIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">暂无通知</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {showUnreadOnly ? '没有未读通知' : '当前没有任何通知'}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {filteredNotifications.map((notification) => (
              <div
                key={notification.id}
                className={`p-4 ${getNotificationColor(notification.type || 'info', notification.read)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    {getNotificationIcon(notification.type || 'info')}
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className={`text-sm font-medium ${
                          notification.read 
                            ? 'text-gray-600 dark:text-gray-400' 
                            : 'text-gray-900 dark:text-white'
                        }`}>
                          {notification.title}
                        </p>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {new Date(notification.created_at).toLocaleString('zh-CN')}
                        </span>
                      </div>
                      
                      {notification.message && (
                        <p className={`mt-1 text-sm ${
                          notification.read 
                            ? 'text-gray-500 dark:text-gray-400' 
                            : 'text-gray-700 dark:text-gray-300'
                        }`}>
                          {notification.message}
                        </p>
                      )}
                      
                      {notification.data && (
                        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                          <pre className="whitespace-pre-wrap">
                            {JSON.stringify(notification.data, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    {!notification.read && (
                      <button
                        onClick={() => handleMarkAsRead(notification.id)}
                        className="p-1 text-gray-400 hover:text-green-600 transition-colors"
                        title="标记为已读"
                      >
                        <CheckIcon className="h-4 w-4" />
                      </button>
                    )}
                    
                    <button
                      onClick={() => handleDeleteNotification(notification.id)}
                      className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                      title="删除通知"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {filteredNotifications.length > 0 && (
        <div className="text-center text-sm text-gray-500 dark:text-gray-400">
          共 {filteredNotifications.length} 条通知
          {showUnreadOnly && notifications.some(n => !n.read) && (
            <span>，其中 {notifications.filter(n => !n.read).length} 条未读</span>
          )}
        </div>
      )}
    </div>
  );
};

export default Notifications;
