import React, { useState, useEffect } from 'react';
import { settingsApi } from '../services/api';
import toast from 'react-hot-toast';

interface SettingsData {
  monitoring_interval_minutes: number;
  summary_frequency_hours: number;
  email_enabled: boolean;
  openai_api_key: string;
  github_token: string;
}

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<SettingsData>({
    monitoring_interval_minutes: 60,
    summary_frequency_hours: 24,
    email_enabled: false,
    openai_api_key: '',
    github_token: ''
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const [systemResponse, apiResponse] = await Promise.all([
        settingsApi.getSystemSettings(),
        settingsApi.getApiSettings()
      ]);
      
      setSettings({
        monitoring_interval_minutes: systemResponse.data.monitoring_interval_minutes,
        summary_frequency_hours: systemResponse.data.summary_frequency_hours,
        email_enabled: systemResponse.data.email_enabled,
        openai_api_key: apiResponse.data.openai_api_key,
        github_token: apiResponse.data.github_token
      });
    } catch (error) {
      toast.error('加载设置失败');
      console.error('Failed to load settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSystemSettingsSave = async () => {
    try {
      setSaving(true);
      await settingsApi.updateSystemSettings({
        monitoring_interval_minutes: settings.monitoring_interval_minutes,
        summary_frequency_hours: settings.summary_frequency_hours,
        email_enabled: settings.email_enabled
      });
      toast.success('系统设置保存成功');
    } catch (error) {
      toast.error('保存系统设置失败');
      console.error('Failed to save system settings:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleApiSettingsSave = async () => {
    try {
      setSaving(true);
      await settingsApi.updateApiSettings({
        openai_api_key: settings.openai_api_key,
        github_token: settings.github_token
      });
      toast.success('API配置保存成功');
    } catch (error) {
      toast.error('保存API配置失败');
      console.error('Failed to save API settings:', error);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

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
                value={settings.monitoring_interval_minutes}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  monitoring_interval_minutes: parseInt(e.target.value) || 60
                }))}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                总结频率（小时）
              </label>
              <input
                type="number"
                value={settings.summary_frequency_hours}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  summary_frequency_hours: parseInt(e.target.value) || 24
                }))}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.email_enabled}
                  onChange={(e) => setSettings(prev => ({
                    ...prev,
                    email_enabled: e.target.checked
                  }))}
                  className="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                />
                <span className="ml-2 text-sm text-gray-700">启用邮件通知</span>
              </label>
            </div>
          </div>
          <div className="mt-6">
            <button
              type="button"
              onClick={handleSystemSettingsSave}
              disabled={saving}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
            >
              {saving ? '保存中...' : '保存设置'}
            </button>
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
                value={settings.openai_api_key}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  openai_api_key: e.target.value
                }))}
                placeholder="sk-..."
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                GitHub Token
              </label>
              <input
                type="password"
                value={settings.github_token}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  github_token: e.target.value
                }))}
                placeholder="ghp_..."
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>
          <div className="mt-6">
            <button
              type="button"
              onClick={handleApiSettingsSave}
              disabled={saving}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
            >
              {saving ? '保存中...' : '保存配置'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings; 