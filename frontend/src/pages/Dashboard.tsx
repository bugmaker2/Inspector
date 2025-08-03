import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { PlayIcon, DocumentTextIcon, UsersIcon, ChartBarIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import { monitoringApi } from '../services/api';
import { DashboardStats } from '../types';
import toast from 'react-hot-toast';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [monitoringLoading, setMonitoringLoading] = useState(false);
  const [summaryExpanded, setSummaryExpanded] = useState(false);

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
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg leading-6 font-medium text-gray-900">最新总结</h3>
              <button
                onClick={() => setSummaryExpanded(!summaryExpanded)}
                className="flex items-center text-sm text-gray-500 hover:text-gray-700"
              >
                {summaryExpanded ? (
                  <>
                    <span>收起</span>
                    <ChevronUpIcon className="h-4 w-4 ml-1" />
                  </>
                ) : (
                  <>
                    <span>展开</span>
                    <ChevronDownIcon className="h-4 w-4 ml-1" />
                  </>
                )}
              </button>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-900 mb-3 break-words">{stats.latest_summary.title}</h4>
              
              <div className={`overflow-hidden transition-all duration-300 relative ${
                summaryExpanded ? 'max-h-none' : 'max-h-32'
              }`}>
                <div className="prose prose-sm max-w-none prose-headings:break-words prose-p:break-words">
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      // 自定义代码块样式 - 改善文字显示
                      code: ({ className, children, ...props }: any) => {
                        const match = /language-(\w+)/.exec(className || '');
                        const isInline = !match;
                        return !isInline ? (
                          <pre className="bg-gray-900 text-gray-100 p-3 rounded-lg overflow-x-auto text-xs font-mono leading-relaxed">
                            <code className={className} {...props}>
                              {children}
                            </code>
                          </pre>
                        ) : (
                          <code className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono text-gray-800" {...props}>
                            {children}
                          </code>
                        );
                      },
                      // 自定义表格样式 - 添加响应式
                      table: ({ children }: any) => (
                        <div className="overflow-x-auto border border-gray-200 rounded-lg">
                          <table className="min-w-full divide-y divide-gray-200">
                            {children}
                          </table>
                        </div>
                      ),
                      th: ({ children }: any) => (
                        <th className="px-3 py-2 bg-gray-50 text-left text-xs font-medium text-gray-700 uppercase tracking-wider break-words">
                          {children}
                        </th>
                      ),
                      td: ({ children }: any) => (
                        <td className="px-3 py-2 text-xs text-gray-900 break-words">
                          {children}
                        </td>
                      ),
                      // 自定义列表样式
                      ul: ({ children }: any) => (
                        <ul className="list-disc list-inside space-y-1 break-words">
                          {children}
                        </ul>
                      ),
                      ol: ({ children }: any) => (
                        <ol className="list-decimal list-inside space-y-1 break-words">
                          {children}
                        </ol>
                      ),
                      // 自定义标题样式 - 添加换行支持
                      h1: ({ children }: any) => (
                        <h1 className="text-lg font-bold text-gray-900 mt-4 mb-2 break-words">
                          {children}
                        </h1>
                      ),
                      h2: ({ children }: any) => (
                        <h2 className="text-base font-semibold text-gray-900 mt-3 mb-2 break-words">
                          {children}
                        </h2>
                      ),
                      h3: ({ children }: any) => (
                        <h3 className="text-sm font-medium text-gray-900 mt-3 mb-1 break-words">
                          {children}
                        </h3>
                      ),
                      // 自定义段落样式 - 添加换行支持
                      p: ({ children }: any) => (
                        <p className="text-sm text-gray-700 leading-relaxed break-words mb-2">
                          {children}
                        </p>
                      ),
                      // 自定义引用样式
                      blockquote: ({ children }: any) => (
                        <blockquote className="border-l-4 border-gray-300 pl-3 italic text-gray-600 my-2 break-words">
                          {children}
                        </blockquote>
                      ),
                      // 自定义链接样式
                      a: ({ children, href }: any) => (
                        <a 
                          href={href} 
                          className="text-blue-600 hover:text-blue-800 underline break-all text-xs"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {children}
                        </a>
                      ),
                      // 自定义列表项样式
                      li: ({ children }: any) => (
                        <li className="break-words text-sm">
                          {children}
                        </li>
                      ),
                    }}
                  >
                    {stats.latest_summary.content}
                  </ReactMarkdown>
                </div>
                
                {!summaryExpanded && (
                  <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-gray-50 to-transparent pointer-events-none"></div>
                )}
              </div>
              
              <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500 mt-3">
                <span className="whitespace-nowrap">类型: {stats.latest_summary.summary_type}</span>
                <span className="hidden sm:inline">•</span>
                <span className="whitespace-nowrap">成员: {stats.latest_summary.member_count}</span>
                <span className="hidden sm:inline">•</span>
                <span className="whitespace-nowrap">活动: {stats.latest_summary.activity_count}</span>
                <span className="hidden sm:inline">•</span>
                <span className="whitespace-nowrap">创建时间: {new Date(stats.latest_summary.created_at).toLocaleString()}</span>
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