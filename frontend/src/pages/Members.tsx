import React, { useState, useEffect } from 'react';
import { PlusIcon, TrashIcon, EyeIcon, PencilIcon } from '@heroicons/react/24/outline';
import { membersApi } from '../services/api';
import { Member, MemberCreate, SocialProfileCreate, SocialProfile } from '../types';
import toast from 'react-hot-toast';

const Members: React.FC = () => {
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedMember, setSelectedMember] = useState<Member | null>(null);
  const [memberProfiles, setMemberProfiles] = useState<SocialProfile[]>([]);
  const [formData, setFormData] = useState<MemberCreate>({
    name: '',
    email: '',
    position: '',
    department: '',
  });
  const [profileFormData, setProfileFormData] = useState<SocialProfileCreate>({
    platform: '',
    profile_url: '',
    username: '',
  });

  useEffect(() => {
    loadMembers();
  }, []);

  const loadMembers = async () => {
    try {
      const response = await membersApi.getAll();
      setMembers(response.data);
    } catch (error) {
      toast.error('加载成员列表失败');
      console.error('Failed to load members:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMemberProfiles = async (memberId: number) => {
    try {
      const response = await membersApi.getSocialProfiles(memberId);
      setMemberProfiles(response.data);
    } catch (error) {
      toast.error('加载社交配置失败');
      console.error('Failed to load member profiles:', error);
    }
  };

  const handleViewDetails = async (member: Member) => {
    setSelectedMember(member);
    await loadMemberProfiles(member.id);
    setShowDetailsModal(true);
  };

  const handleCreateMember = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await membersApi.create(formData);
      toast.success('成员创建成功');
      setShowCreateModal(false);
      setFormData({ name: '', email: '', position: '', department: '' });
      loadMembers();
    } catch (error) {
      toast.error('创建成员失败');
      console.error('Failed to create member:', error);
    }
  };

  const handleCreateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMember) return;
    
    try {
      await membersApi.addSocialProfile(selectedMember.id, profileFormData);
      toast.success('社交配置添加成功');
      setShowProfileModal(false);
      setProfileFormData({ platform: '', profile_url: '', username: '' });
      loadMembers();
      // 如果详情模态框是打开的，重新加载配置
      if (showDetailsModal) {
        await loadMemberProfiles(selectedMember.id);
      }
    } catch (error) {
      toast.error('添加社交配置失败');
      console.error('Failed to create profile:', error);
    }
  };

  const handleDeleteMember = async (id: number) => {
    if (!window.confirm('确定要删除这个成员吗？')) return;
    
    try {
      await membersApi.delete(id);
      toast.success('成员删除成功');
      loadMembers();
    } catch (error) {
      toast.error('删除成员失败');
      console.error('Failed to delete member:', error);
    }
  };

  const handleDeleteProfile = async (memberId: number, profileId: number) => {
    if (!window.confirm('确定要删除这个社交配置吗？')) return;
    
    try {
      await membersApi.deleteSocialProfile(memberId, profileId);
      toast.success('社交配置删除成功');
      await loadMemberProfiles(memberId);
      loadMembers();
    } catch (error) {
      toast.error('删除社交配置失败');
      console.error('Failed to delete profile:', error);
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'github':
        return '🐙';
      case 'linkedin':
        return '💼';
      case 'twitter':
        return '🐦';
      default:
        return '🌐';
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'github':
        return 'bg-gray-800 text-white';
      case 'linkedin':
        return 'bg-blue-600 text-white';
      case 'twitter':
        return 'bg-blue-400 text-white';
      default:
        return 'bg-gray-500 text-white';
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
          <h1 className="text-2xl font-bold text-gray-900 break-words">成员管理</h1>
          <p className="text-gray-600 break-words">管理团队成员和社交配置</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          添加成员
        </button>
      </div>

      {/* Members List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {members.map((member) => (
            <li key={member.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                        <span className="text-primary-800 font-medium">
                          {member.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4 flex-1 min-w-0">
                      <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                        <p className="text-sm font-medium text-gray-900 break-words">{member.name}</p>
                        {!member.is_active && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 whitespace-nowrap">
                            非活跃
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-500 break-all">{member.email}</p>
                      {member.position && (
                        <p className="text-sm text-gray-500 break-words">{member.position}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-wrap items-center gap-2 lg:flex-shrink-0">
                    <button
                      onClick={() => handleViewDetails(member)}
                      className="text-primary-600 hover:text-primary-900 flex items-center text-sm"
                      title="查看详情"
                    >
                      <EyeIcon className="h-4 w-4 mr-1" />
                      <span className="whitespace-nowrap">查看配置</span>
                    </button>
                    <button
                      onClick={() => {
                        setSelectedMember(member);
                        setShowProfileModal(true);
                      }}
                      className="text-green-600 hover:text-green-900 flex items-center text-sm"
                      title="添加配置"
                    >
                      <PlusIcon className="h-4 w-4 mr-1" />
                      <span className="whitespace-nowrap">添加配置</span>
                    </button>
                    <button
                      onClick={() => handleDeleteMember(member.id)}
                      className="text-red-600 hover:text-red-900"
                      title="删除成员"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                
                {/* Social Profiles Summary */}
                {member.social_profiles && member.social_profiles.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2 break-words">社交配置 ({member.social_profiles.length})</h4>
                    <div className="flex flex-wrap gap-2">
                      {member.social_profiles.map((profile) => (
                        <span
                          key={profile.id}
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPlatformColor(profile.platform)} break-words`}
                        >
                          {profile.platform}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Member Details Modal */}
      {showDetailsModal && selectedMember && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-medium text-gray-900">
                  {selectedMember.name} - 详细配置
                </h3>
                <button
                  onClick={() => setShowDetailsModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Member Information */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h4 className="text-lg font-medium text-gray-900 mb-3">成员信息</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">姓名</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedMember.name}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">邮箱</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedMember.email}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">职位</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedMember.position || '未设置'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">部门</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedMember.department || '未设置'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">状态</label>
                    <span className={`mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      selectedMember.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {selectedMember.is_active ? '活跃' : '非活跃'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Social Profiles */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-medium text-gray-900">社交配置</h4>
                  <button
                    onClick={() => {
                      setShowDetailsModal(false);
                      setShowProfileModal(true);
                    }}
                    className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-primary-600 bg-primary-50 hover:bg-primary-100"
                  >
                    <PlusIcon className="h-4 w-4 mr-1" />
                    添加配置
                  </button>
                </div>
                
                {memberProfiles.length > 0 ? (
                  <div className="space-y-4">
                    {memberProfiles.map((profile) => (
                      <div key={profile.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <span className="text-2xl">{getPlatformIcon(profile.platform)}</span>
                            <div>
                              <h5 className="text-sm font-medium text-gray-900 capitalize">{profile.platform}</h5>
                              {profile.username && (
                                <p className="text-sm text-gray-500">@{profile.username}</p>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            {profile.profile_url && (
                              <a
                                href={profile.profile_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-primary-600 hover:text-primary-900 text-sm"
                              >
                                查看资料
                              </a>
                            )}
                            <button
                              onClick={() => handleDeleteProfile(selectedMember.id, profile.id)}
                              className="text-red-600 hover:text-red-900"
                              title="删除配置"
                            >
                              <TrashIcon className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                        {profile.profile_url && (
                          <div className="mt-2">
                            <label className="block text-xs font-medium text-gray-700">个人资料URL</label>
                            <p className="mt-1 text-xs text-gray-500 break-all">{profile.profile_url}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 bg-gray-50 rounded-lg">
                    <p className="text-gray-500">暂无社交配置</p>
                    <button
                      onClick={() => {
                        setShowDetailsModal(false);
                        setShowProfileModal(true);
                      }}
                      className="mt-2 inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-primary-600 bg-primary-50 hover:bg-primary-100"
                    >
                      <PlusIcon className="h-4 w-4 mr-1" />
                      添加第一个配置
                    </button>
                  </div>
                )}
              </div>

              <div className="flex justify-end">
                <button
                  onClick={() => setShowDetailsModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  关闭
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Member Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">添加新成员</h3>
              <form onSubmit={handleCreateMember} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">姓名</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">邮箱</label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">职位</label>
                  <input
                    type="text"
                    value={formData.position}
                    onChange={(e) => setFormData({ ...formData, position: e.target.value })}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">部门</label>
                  <input
                    type="text"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    取消
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
                  >
                    创建
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Create Profile Modal */}
      {showProfileModal && selectedMember && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                为 {selectedMember.name} 添加社交配置
              </h3>
              <form onSubmit={handleCreateProfile} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">平台</label>
                  <select
                    required
                    value={profileFormData.platform}
                    onChange={(e) => setProfileFormData({ ...profileFormData, platform: e.target.value })}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">选择平台</option>
                    <option value="linkedin">LinkedIn</option>
                    <option value="github">GitHub</option>
                    <option value="twitter">Twitter</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">个人资料URL</label>
                  <input
                    type="url"
                    required
                    value={profileFormData.profile_url}
                    onChange={(e) => setProfileFormData({ ...profileFormData, profile_url: e.target.value })}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">用户名</label>
                  <input
                    type="text"
                    value={profileFormData.username}
                    onChange={(e) => setProfileFormData({ ...profileFormData, username: e.target.value })}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowProfileModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    取消
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
                  >
                    添加
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Members; 