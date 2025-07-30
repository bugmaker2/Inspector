import React, { useState, useEffect } from 'react';
import { PlusIcon, TrashIcon } from '@heroicons/react/24/outline';
import { membersApi, socialProfilesApi } from '../services/api';
import { Member, MemberCreate, SocialProfileCreate } from '../types';
import toast from 'react-hot-toast';

const Members: React.FC = () => {
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [selectedMember, setSelectedMember] = useState<Member | null>(null);
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
      const data = await membersApi.getAll();
      setMembers(data);
    } catch (error) {
      toast.error('加载成员列表失败');
      console.error('Failed to load members:', error);
    } finally {
      setLoading(false);
    }
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
      await socialProfilesApi.create(selectedMember.id, profileFormData);
      toast.success('社交配置添加成功');
      setShowProfileModal(false);
      setProfileFormData({ platform: '', profile_url: '', username: '' });
      loadMembers();
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">成员管理</h1>
          <p className="text-gray-600">管理团队成员和社交配置</p>
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
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                        <span className="text-primary-800 font-medium">
                          {member.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="flex items-center">
                        <p className="text-sm font-medium text-gray-900">{member.name}</p>
                        {!member.is_active && (
                          <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            非活跃
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-500">{member.email}</p>
                      {member.position && (
                        <p className="text-sm text-gray-500">{member.position}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => {
                        setSelectedMember(member);
                        setShowProfileModal(true);
                      }}
                      className="text-primary-600 hover:text-primary-900"
                    >
                      添加社交配置
                    </button>
                    <button
                      onClick={() => handleDeleteMember(member.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                
                {/* Social Profiles */}
                {member.social_profiles && member.social_profiles.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">社交配置</h4>
                    <div className="flex flex-wrap gap-2">
                      {member.social_profiles.map((profile) => (
                        <span
                          key={profile.id}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
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