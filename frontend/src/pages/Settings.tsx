import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Settings: React.FC = () => {
  const [githubConnected, setGithubConnected] = useState(false);
  const [githubUsername, setGithubUsername] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkGitHubStatus();
    
    // 检查URL参数中的OAuth结果
    const urlParams = new URLSearchParams(window.location.search);
    const githubConnected = urlParams.get('github_connected');
    const error = urlParams.get('error');
    const username = urlParams.get('username');
    
    if (githubConnected === 'true') {
      setGithubConnected(true);
      setGithubUsername(username);
      setError(null);
      // 清除URL参数
      window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    if (error) {
      setError(decodeURIComponent(error));
      setGithubConnected(false);
      // 清除URL参数
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const checkGitHubStatus = async () => {
    try {
      const response = await api.get('/api/v1/auth/users/me/github-status');
      setGithubConnected(response.data.connected);
      setGithubUsername(response.data.github_username);
    } catch (err) {
      console.error('Failed to check GitHub status:', err);
    }
  };

  const connectGitHub = () => {
    setLoading(true);
    setError(null);
    // 重定向到GitHub OAuth页面
    const apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    window.location.href = `${apiBaseUrl}/api/v1/auth/github`;
  };

  const disconnectGitHub = async () => {
    try {
      setLoading(true);
      await api.delete('/api/v1/auth/users/me/github-connection');
      setGithubConnected(false);
      setGithubUsername(null);
    } catch (err) {
      setError('断开连接失败');
      console.error('Failed to disconnect GitHub:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">设置</h1>
        <p className="text-gray-600">系统配置和偏好设置</p>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            系统设置
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                监控间隔（分钟）
              </label>
              <input
                type="number"
                defaultValue="60"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                总结频率（小时）
              </label>
              <input
                type="number"
                defaultValue="24"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                />
                <span className="ml-2 text-sm text-gray-700">启用邮件通知</span>
              </label>
            </div>
          </div>
          <div className="mt-6">
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700"
            >
              保存设置
            </button>
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            GitHub 连接
          </h3>
          
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}
          
          <div className="space-y-4">
            {githubConnected ? (
              <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-md">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-green-800">
                      已连接到 GitHub
                    </p>
                    <p className="text-sm text-green-600">
                      用户名: {githubUsername}
                    </p>
                  </div>
                </div>
                <button
                  onClick={disconnectGitHub}
                  disabled={loading}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                >
                  {loading ? '断开中...' : '断开连接'}
                </button>
              </div>
            ) : (
              <div className="text-center">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">未连接 GitHub</h3>
                <p className="mt-1 text-sm text-gray-500">
                  连接 GitHub 以监控您的代码活动
                </p>
                <div className="mt-6">
                  <button
                    onClick={connectGitHub}
                    disabled={loading}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-gray-800 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50"
                  >
                    {loading ? '连接中...' : '连接 GitHub'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            API配置
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                OpenAI API Key
              </label>
              <input
                type="password"
                placeholder="sk-..."
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>
          <div className="mt-6">
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700"
            >
              保存配置
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings; 