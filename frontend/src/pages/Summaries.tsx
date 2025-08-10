import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { apiService } from '../services/api';
import { Summary } from '../types';
import toast from 'react-hot-toast';
import { DocumentTextIcon } from '@heroicons/react/24/outline';

const Summaries: React.FC = () => {
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [language, setLanguage] = useState<'chinese' | 'english'>('chinese');

  const loadSummaries = async () => {
    try {
      const response = await apiService.getSummaries();
      setSummaries(response);
    } catch (error) {
      toast.error('加载总结列表失败');
      console.error('Failed to load summaries:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummaries();
  }, [language]);

  const generateDailySummary = async () => {
    setGenerating(true);
    try {
      await apiService.generateDailySummary();
      toast.success('每日总结生成成功');
      loadSummaries(); // 重新加载列表
    } catch (error: any) {
      toast.error(`生成每日总结失败: ${error.message || '未知错误'}`);
    } finally {
      setGenerating(false);
    }
  };

  const generateWeeklySummary = async () => {
    setGenerating(true);
    try {
      await apiService.generateWeeklySummary();
      toast.success('每周总结生成成功');
      loadSummaries(); // 重新加载列表
    } catch (error: any) {
      toast.error(`生成每周总结失败: ${error.message || '未知错误'}`);
    } finally {
      setGenerating(false);
    }
  };

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'chinese' ? 'english' : 'chinese');
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
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">总结报告</h1>
          <p className="text-gray-600 dark:text-gray-400">AI生成的团队活动总结</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={toggleLanguage}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            {language === 'chinese' ? 'English' : '中文'}
          </button>
          
          <button
            onClick={generateDailySummary}
            disabled={generating}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {generating ? '生成中...' : '生成日报'}
          </button>
          
          <button
            onClick={generateWeeklySummary}
            disabled={generating}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
          >
            {generating ? '生成中...' : '生成周报'}
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        {summaries.length === 0 ? (
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">暂无总结</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              点击上方按钮生成新的总结报告
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {summaries.map((summary) => (
              <div key={summary.id} className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {summary.title}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {new Date(summary.created_at).toLocaleString('zh-CN')}
                    </p>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    summary.summary_type === 'daily' 
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                      : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  }`}>
                    {summary.summary_type === 'daily' ? '日报' : '周报'}
                  </span>
                </div>
                
                                 <div className="prose prose-sm max-w-none dark:prose-invert">
                   <ReactMarkdown 
                     remarkPlugins={[remarkGfm]}
                   >
                     {summary.content}
                   </ReactMarkdown>
                 </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Summaries; 