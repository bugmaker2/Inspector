import React, { useState, useEffect } from 'react';
import { monitoringApi } from '../services/api';
import { Summary } from '../types';
import toast from 'react-hot-toast';

const Summaries: React.FC = () => {
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSummaries();
  }, []);

  const loadSummaries = async () => {
    try {
      const data = await monitoringApi.getSummaries({ limit: 20 });
      setSummaries(data);
    } catch (error) {
      toast.error('加载总结列表失败');
      console.error('Failed to load summaries:', error);
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
        <h1 className="text-2xl font-bold text-gray-900">总结报告</h1>
        <p className="text-gray-600">查看AI生成的社交动态总结报告</p>
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
                  {summary.summary_type === 'daily' ? '每日' :
                   summary.summary_type === 'weekly' ? '每周' : '自定义'}
                </span>
              </div>
              
              <div className="prose max-w-none">
                <p className="text-gray-600 whitespace-pre-wrap">{summary.content}</p>
              </div>
              
              <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                <div className="flex items-center space-x-4">
                  <span>成员数: {summary.member_count}</span>
                  <span>活动数: {summary.activity_count}</span>
                  {summary.start_date && (
                    <span>开始: {new Date(summary.start_date).toLocaleDateString()}</span>
                  )}
                  {summary.end_date && (
                    <span>结束: {new Date(summary.end_date).toLocaleDateString()}</span>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <span>创建时间: {new Date(summary.created_at).toLocaleString()}</span>
                  {summary.is_sent && (
                    <span className="text-green-600">已发送</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {summaries.length === 0 && (
          <div className="text-center py-12 bg-white shadow rounded-lg">
            <p className="text-gray-500">暂无总结报告</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Summaries; 