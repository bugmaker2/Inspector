import React, { useState, useEffect } from 'react';
import { PlayIcon, DocumentTextIcon, UsersIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import { monitoringApi } from '../services/api';
import { DashboardStats } from '../types';
import toast from 'react-hot-toast';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [monitoringLoading, setMonitoringLoading] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await monitoringApi.getStats();
      setStats(data);
    } catch (error) {
      toast.error('加载统计数据失败');
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const runMonitoring = async () => {
    setMonitoringLoading(true);
    try {
      const result = await monitoringApi.runMonitoring();
      toast.success(`监控完成！发现 ${result.new_activities} 个新活动`);
      loadStats(); // 重新加载统计数据
    } catch (error) {
      toast.error('运行监控失败');
      console.error('Failed to run monitoring:', error);
    } finally {
      setMonitoringLoading(false);
    }
  };

  const generateDailySummary = async () => {
    try {
      await monitoringApi.generateDailySummary();
      toast.success('每日总结生成成功！');
    } catch (error) {
      toast.error('生成总结失败');
      console.error('Failed to generate summary:', error);
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
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 break-words">仪表板</h1>
          <p className="text-gray-600 break-words">监控团队成员社交动态的概览</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={runMonitoring}
            disabled={monitoringLoading}
            className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            <PlayIcon className="h-4 w-4 mr-2" />
            <span className="whitespace-nowrap">{monitoringLoading ? '监控中...' : '运行监控'}</span>
          </button>
          <button
            onClick={generateDailySummary}
            className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            <span className="whitespace-nowrap">生成总结</span>
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      {stats && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <UsersIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">总成员数</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.total_members}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">总活动数</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.total_activities}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-6 w-6 text-green-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">今日活动</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.activities_today}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-6 w-6 text-blue-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">本周活动</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.activities_this_week}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Latest Summary */}
      {stats?.latest_summary && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">最新总结</h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">{stats.latest_summary.title}</h4>
              <p className="text-sm text-gray-600 mb-3">{stats.latest_summary.content}</p>
              <div className="flex items-center text-xs text-gray-500">
                <span>类型: {stats.latest_summary.summary_type}</span>
                <span className="mx-2">•</span>
                <span>成员: {stats.latest_summary.member_count}</span>
                <span className="mx-2">•</span>
                <span>活动: {stats.latest_summary.activity_count}</span>
                <span className="mx-2">•</span>
                <span>创建时间: {new Date(stats.latest_summary.created_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">快速操作</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <button
              onClick={runMonitoring}
              disabled={monitoringLoading}
              className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-lg border border-gray-200 hover:border-gray-300"
            >
              <div>
                <span className="rounded-lg inline-flex p-3 bg-primary-50 text-primary-700 ring-4 ring-white">
                  <PlayIcon className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-8">
                <h3 className="text-lg font-medium">
                  <span className="absolute inset-0" aria-hidden="true" />
                  运行监控
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  立即检查所有社交配置的最新动态
                </p>
              </div>
            </button>

            <button
              onClick={generateDailySummary}
              className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-lg border border-gray-200 hover:border-gray-300"
            >
              <div>
                <span className="rounded-lg inline-flex p-3 bg-green-50 text-green-700 ring-4 ring-white">
                  <DocumentTextIcon className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-8">
                <h3 className="text-lg font-medium">
                  <span className="absolute inset-0" aria-hidden="true" />
                  生成总结
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  使用AI生成今日活动总结报告
                </p>
              </div>
            </button>

            <a
              href="/members"
              className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-lg border border-gray-200 hover:border-gray-300"
            >
              <div>
                <span className="rounded-lg inline-flex p-3 bg-blue-50 text-blue-700 ring-4 ring-white">
                  <UsersIcon className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-8">
                <h3 className="text-lg font-medium">
                  <span className="absolute inset-0" aria-hidden="true" />
                  管理成员
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  添加或编辑团队成员信息
                </p>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 