import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { monitoringApi } from '../services/api';
import { Summary } from '../types';
import toast from 'react-hot-toast';

const Summaries: React.FC = () => {
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [language, setLanguage] = useState<'chinese' | 'english'>('chinese');  // 添加语言状态

  useEffect(() => {
    loadSummaries();
  }, [language]);  // 当语言改变时重新加载

  const loadSummaries = async () => {
    try {
      const data = await monitoringApi.getSummaries({ limit: 20, language });  // 传递语言参数
      setSummaries(data);
    } catch (error) {
      toast.error('加载总结列表失败');
      console.error('Failed to load summaries:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateDailySummary = async () => {
    setGenerating(true);
    try {
      await monitoringApi.generateDailySummary();
      toast.success('每日总结生成成功');
      await loadSummaries(); // 重新加载列表
    } catch (error) {
      toast.error('生成每日总结失败');
      console.error('Failed to generate daily summary:', error);
    } finally {
      setGenerating(false);
    }
  };

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'chinese' ? 'english' : 'chinese');
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {language === 'chinese' ? '总结报告' : 'Summary Reports'}
          </h1>
          <p className="text-gray-600">
            {language === 'chinese' ? '查看AI生成的社交动态总结报告' : 'View AI-generated social media activity summary reports'}
          </p>
        </div>
        <div className="flex items-center space-x-4">
          {/* 语言切换按钮 */}
          <button
            onClick={toggleLanguage}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <span className="text-sm font-medium">
              {language === 'chinese' ? '🇨🇳 中文' : '🇺🇸 English'}
            </span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          <button
            onClick={generateDailySummary}
            disabled={generating}
            className="bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
          >
            {generating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>{language === 'chinese' ? '生成中...' : 'Generating...'}</span>
              </>
            ) : (
              <span>{language === 'chinese' ? '生成每日总结' : 'Generate Daily Summary'}</span>
            )}
          </button>
        </div>
      </div>

      <div className="grid gap-6">
        {summaries.map((summary) => (
          <div key={summary.id} className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">{summary.title}</h3>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  summary.summary_type === 'daily' ? 'bg-blue-100 text-blue-800' :
                  summary.summary_type === 'weekly' ? 'bg-green-100 text-green-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {summary.summary_type === 'daily' ? (language === 'chinese' ? '每日' : 'Daily') :
                   summary.summary_type === 'weekly' ? (language === 'chinese' ? '每周' : 'Weekly') : 
                   (language === 'chinese' ? '自定义' : 'Custom')}
                </span>
              </div>
              
              <div className="prose max-w-none prose-sm">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // 自定义代码块样式
                    code: ({ className, children, ...props }: any) => {
                      const match = /language-(\w+)/.exec(className || '');
                      const isInline = !match;
                      return !isInline ? (
                        <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto">
                          <code className={className} {...props}>
                            {children}
                          </code>
                        </pre>
                      ) : (
                        <code className="bg-gray-100 px-1 py-0.5 rounded text-sm" {...props}>
                          {children}
                        </code>
                      );
                    },
                    // 自定义表格样式
                    table: ({ children }: any) => (
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          {children}
                        </table>
                      </div>
                    ),
                    th: ({ children }: any) => (
                      <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {children}
                      </th>
                    ),
                    td: ({ children }: any) => (
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {children}
                      </td>
                    ),
                    // 自定义列表样式
                    ul: ({ children }: any) => (
                      <ul className="list-disc list-inside space-y-1">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }: any) => (
                      <ol className="list-decimal list-inside space-y-1">
                        {children}
                      </ol>
                    ),
                    // 自定义标题样式
                    h1: ({ children }: any) => (
                      <h1 className="text-2xl font-bold text-gray-900 mt-6 mb-4">
                        {children}
                      </h1>
                    ),
                    h2: ({ children }: any) => (
                      <h2 className="text-xl font-semibold text-gray-900 mt-5 mb-3">
                        {children}
                      </h2>
                    ),
                    h3: ({ children }: any) => (
                      <h3 className="text-lg font-medium text-gray-900 mt-4 mb-2">
                        {children}
                      </h3>
                    ),
                    // 自定义引用样式
                    blockquote: ({ children }: any) => (
                      <blockquote className="border-l-4 border-gray-300 pl-4 italic text-gray-600 my-4">
                        {children}
                      </blockquote>
                    ),
                    // 自定义链接样式
                    a: ({ children, href }: any) => (
                      <a 
                        href={href} 
                        className="text-blue-600 hover:text-blue-800 underline"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {children}
                      </a>
                    ),
                  }}
                >
                  {summary.content}
                </ReactMarkdown>
              </div>
              
              <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                <div className="flex items-center space-x-4">
                  <span>{language === 'chinese' ? '成员数' : 'Members'}: {summary.member_count}</span>
                  <span>{language === 'chinese' ? '活动数' : 'Activities'}: {summary.activity_count}</span>
                  {summary.start_date && (
                    <span>{language === 'chinese' ? '开始' : 'Start'}: {new Date(summary.start_date).toLocaleDateString()}</span>
                  )}
                  {summary.end_date && (
                    <span>{language === 'chinese' ? '结束' : 'End'}: {new Date(summary.end_date).toLocaleDateString()}</span>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <span>{language === 'chinese' ? '创建时间' : 'Created'}: {new Date(summary.created_at).toLocaleString()}</span>
                  {summary.is_sent && (
                    <span className="text-green-600">{language === 'chinese' ? '已发送' : 'Sent'}</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {summaries.length === 0 && (
          <div className="text-center py-12 bg-white shadow rounded-lg">
            <p className="text-gray-500">
              {language === 'chinese' ? '暂无总结报告' : 'No summary reports available'}
            </p>
            <button
              onClick={generateDailySummary}
              disabled={generating}
              className="mt-4 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg"
            >
              {generating ? 
                (language === 'chinese' ? '生成中...' : 'Generating...') : 
                (language === 'chinese' ? '生成第一个总结' : 'Generate First Summary')
              }
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Summaries; 