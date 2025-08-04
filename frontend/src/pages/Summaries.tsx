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
  const [language, setLanguage] = useState<'chinese' | 'english'>('chinese');
  const [generationProgress, setGenerationProgress] = useState<{
    progress: number;
    message: string;
    isVisible: boolean;
  }>({
    progress: 0,
    message: '',
    isVisible: false
  });

  const [streamingContent, setStreamingContent] = useState<{
    chinese: string;
    english: string;
    isGenerating: boolean;
  }>({
    chinese: '',
    english: '',
    isGenerating: false
  });

  useEffect(() => {
    loadSummaries();
  }, [language]);

  const loadSummaries = async () => {
    try {
      const data = await monitoringApi.getSummaries({ limit: 20, language });
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
    setGenerationProgress({
      progress: 0,
      message: '准备生成...',
      isVisible: true
    });
    setStreamingContent({
      chinese: '',
      english: '',
      isGenerating: true
    });

    try {
      await monitoringApi.generateDailySummaryStream(
        undefined, // date
        (data) => {
          // 进度回调
          if (data.type === 'progress') {
            setGenerationProgress({
              progress: data.progress,
              message: data.message,
              isVisible: true
            });
          } else if (data.type === 'start') {
            setGenerationProgress({
              progress: 0,
              message: data.message,
              isVisible: true
            });
          } else if (data.type === 'content_start') {
            // 开始生成内容
            setGenerationProgress({
              progress: data.language === 'chinese' ? 35 : 75,
              message: `正在生成${data.language === 'chinese' ? '中文' : '英文'}总结...`,
              isVisible: true
            });
          } else if (data.type === 'content_end') {
            // 内容生成完成
            setGenerationProgress({
              progress: data.language === 'chinese' ? 60 : 90,
              message: `${data.language === 'chinese' ? '中文' : '英文'}总结生成完成`,
              isVisible: true
            });
          }
        },
        (summary) => {
          // 完成回调
          setGenerationProgress({
            progress: 100,
            message: '生成完成！',
            isVisible: false
          });
          setStreamingContent({
            chinese: '',
            english: '',
            isGenerating: false
          });
          toast.success('每日总结生成成功');
          loadSummaries(); // 重新加载列表
        },
        (error) => {
          // 错误回调
          setGenerationProgress({
            progress: 0,
            message: '',
            isVisible: false
          });
          setStreamingContent({
            chinese: '',
            english: '',
            isGenerating: false
          });
          toast.error(`生成每日总结失败: ${error}`);
        },
        (language, content) => {
          // 内容片段回调
          setStreamingContent(prev => ({
            ...prev,
            [language as keyof typeof prev]: prev[language as keyof typeof prev] + content
          }));
        }
      );
    } catch (error) {
      setGenerationProgress({
        progress: 0,
        message: '',
        isVisible: false
      });
      setStreamingContent({
        chinese: '',
        english: '',
        isGenerating: false
      });
      toast.error('生成每日总结失败');
      console.error('Failed to generate daily summary:', error);
    } finally {
      setGenerating(false);
    }
  };

  const generateWeeklySummary = async () => {
    setGenerating(true);
    setGenerationProgress({
      progress: 0,
      message: '准备生成...',
      isVisible: true
    });

    try {
      await monitoringApi.generateWeeklySummaryStream(
        undefined, // startDate
        (data) => {
          // 进度回调
          if (data.type === 'progress') {
            setGenerationProgress({
              progress: data.progress,
              message: data.message,
              isVisible: true
            });
          } else if (data.type === 'start') {
            setGenerationProgress({
              progress: 0,
              message: data.message,
              isVisible: true
            });
          }
        },
        (summary) => {
          // 完成回调
          setGenerationProgress({
            progress: 100,
            message: '生成完成！',
            isVisible: false
          });
          toast.success('每周总结生成成功');
          loadSummaries(); // 重新加载列表
        },
        (error) => {
          // 错误回调
          setGenerationProgress({
            progress: 0,
            message: '',
            isVisible: false
          });
          toast.error(`生成每周总结失败: ${error}`);
        }
      );
    } catch (error) {
      setGenerationProgress({
        progress: 0,
        message: '',
        isVisible: false
      });
      toast.error('生成每周总结失败');
      console.error('Failed to generate weekly summary:', error);
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
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 break-words">
            {language === 'chinese' ? '总结报告' : 'Summary Reports'}
          </h1>
          <p className="text-gray-600 break-words">
            {language === 'chinese' ? '查看AI生成的社交动态总结报告' : 'View AI-generated social media activity summary reports'}
          </p>
        </div>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          {/* 语言切换按钮 */}
          <button
            onClick={toggleLanguage}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg flex items-center justify-center space-x-2 transition-colors"
          >
            <span className="text-sm font-medium">
              {language === 'chinese' ? '🇨🇳 中文' : '🇺🇸 English'}
            </span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {/* 生成按钮组 */}
          <div className="flex gap-2">
            <button
              onClick={generateDailySummary}
              disabled={generating}
              className="bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg flex items-center justify-center space-x-2"
            >
              {generating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span className="whitespace-nowrap">{language === 'chinese' ? '生成中...' : 'Generating...'}</span>
                </>
              ) : (
                <span className="whitespace-nowrap">{language === 'chinese' ? '生成每日总结' : 'Generate Daily Summary'}</span>
              )}
            </button>
            
            <button
              onClick={generateWeeklySummary}
              disabled={generating}
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg flex items-center justify-center space-x-2"
            >
              {generating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span className="whitespace-nowrap">{language === 'chinese' ? '生成中...' : 'Generating...'}</span>
                </>
              ) : (
                <span className="whitespace-nowrap">{language === 'chinese' ? '生成每周总结' : 'Generate Weekly Summary'}</span>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* 生成进度条 */}
      {generationProgress.isVisible && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-800">
              {generationProgress.message}
            </span>
            <span className="text-sm text-blue-600">
              {generationProgress.progress}%
            </span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${generationProgress.progress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* 流式内容显示 */}
      {streamingContent.isGenerating && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {language === 'chinese' ? '实时生成内容' : 'Real-time Generation'}
          </h3>
          
          {/* 中文内容 */}
          {streamingContent.chinese && (
            <div className="mb-6">
              <h4 className="text-md font-medium text-gray-800 mb-3 flex items-center">
                <span className="mr-2">🇨🇳</span>
                中文总结
                <div className="ml-2 w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              </h4>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-96 overflow-y-auto prose prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {streamingContent.chinese}
                </ReactMarkdown>
              </div>
            </div>
          )}
          
          {/* 英文内容 */}
          {streamingContent.english && (
            <div>
              <h4 className="text-md font-medium text-gray-800 mb-3 flex items-center">
                <span className="mr-2">🇺🇸</span>
                English Summary
                <div className="ml-2 w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              </h4>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-96 overflow-y-auto prose prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {streamingContent.english}
                </ReactMarkdown>
              </div>
            </div>
          )}
          
          {/* 等待内容生成 */}
          {!streamingContent.chinese && !streamingContent.english && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-500">
                {language === 'chinese' ? '正在生成内容，请稍候...' : 'Generating content, please wait...'}
              </p>
            </div>
          )}
        </div>
      )}

      {/* 总结列表 */}
      <div className="space-y-4">
        {summaries.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">📊</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {language === 'chinese' ? '暂无总结报告' : 'No Summary Reports'}
            </h3>
            <p className="text-gray-500">
              {language === 'chinese' ? '点击上方按钮生成您的第一份总结报告' : 'Click the button above to generate your first summary report'}
            </p>
          </div>
        ) : (
          summaries.map((summary) => (
            <div key={summary.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {summary.title}
                  </h3>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>
                      {language === 'chinese' ? '类型' : 'Type'}: {summary.summary_type}
                    </span>
                    <span>
                      {language === 'chinese' ? '成员数' : 'Members'}: {summary.member_count}
                    </span>
                    <span>
                      {language === 'chinese' ? '活动数' : 'Activities'}: {summary.activity_count}
                    </span>
                    <span>
                      {new Date(summary.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h1: ({children}) => <h1 className="text-xl font-bold text-gray-900 mb-3">{children}</h1>,
                    h2: ({children}) => <h2 className="text-lg font-semibold text-gray-800 mb-2 mt-4">{children}</h2>,
                    h3: ({children}) => <h3 className="text-base font-medium text-gray-700 mb-2 mt-3">{children}</h3>,
                    p: ({children}) => <p className="text-gray-600 mb-3 leading-relaxed">{children}</p>,
                    ul: ({children}) => <ul className="list-disc list-inside text-gray-600 mb-3 space-y-1">{children}</ul>,
                    ol: ({children}) => <ol className="list-decimal list-inside text-gray-600 mb-3 space-y-1">{children}</ol>,
                    li: ({children}) => <li className="text-gray-600">{children}</li>,
                    strong: ({children}) => <strong className="font-semibold text-gray-800">{children}</strong>,
                    em: ({children}) => <em className="italic text-gray-700">{children}</em>,
                    code: ({children}) => <code className="bg-gray-100 text-gray-800 px-1 py-0.5 rounded text-sm">{children}</code>,
                    pre: ({children}) => <pre className="bg-gray-100 p-3 rounded-lg overflow-x-auto text-sm">{children}</pre>,
                    blockquote: ({children}) => <blockquote className="border-l-4 border-gray-300 pl-4 italic text-gray-600">{children}</blockquote>,
                    table: ({children}) => <div className="overflow-x-auto"><table className="min-w-full border border-gray-300">{children}</table></div>,
                    th: ({children}) => <th className="border border-gray-300 px-3 py-2 bg-gray-50 font-medium text-gray-700">{children}</th>,
                    td: ({children}) => <td className="border border-gray-300 px-3 py-2 text-gray-600">{children}</td>,
                  }}
                >
                  {language === 'chinese' ? summary.content : summary.content_en}
                </ReactMarkdown>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Summaries; 