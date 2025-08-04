// API响应类型
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: string;
}

// 成员相关类型
export interface Member {
  id: number;
  name: string;
  email: string;
  position?: string;
  department?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  social_profiles?: SocialProfile[];
  activities?: Activity[];
}

export interface MemberCreate {
  name: string;
  email: string;
  position?: string;
  department?: string;
}

export interface MemberUpdate {
  name?: string;
  email?: string;
  position?: string;
  department?: string;
  is_active?: boolean;
}

// 社交配置相关类型
export interface SocialProfile {
  id: number;
  member_id: number;
  platform: string;
  profile_url: string;
  username?: string;
  is_active: boolean;
  last_checked?: string;
  created_at: string;
  updated_at: string;
}

export interface SocialProfileCreate {
  platform: string;
  profile_url: string;
  username?: string;
}

export interface SocialProfileUpdate {
  profile_url?: string;
  username?: string;
  is_active?: boolean;
}

// 活动相关类型
export interface Activity {
  id: number;
  member_id: number;
  social_profile_id: number;
  platform: string;
  activity_type?: string;
  title?: string;
  content?: string;
  url?: string;
  external_id?: string;
  published_at?: string;
  is_processed: boolean;
  created_at: string;
}

// 总结相关类型
export interface Summary {
  id: number;
  title: string;
  content: string;
  content_en?: string;  // 英文内容
  summary_type: string;
  start_date?: string;
  end_date?: string;
  member_count: number;
  activity_count: number;
  created_at: string;
  is_sent: boolean;
  sent_at?: string;
}

// 仪表板统计类型
export interface DashboardStats {
  total_members: number;
  active_members: number;
  total_activities: number;
  activities_today: number;
  activities_this_week: number;
  latest_summary?: Summary;
}

// 监控配置类型
export interface MonitoringConfig {
  monitoring_interval_minutes: number;
  summary_frequency_hours: number;
  platforms_to_monitor: string[];
}

// 监控结果类型
export interface MonitoringResult {
  status: string;
  new_activities: number;
  platform_results?: Record<string, Activity[]>;
}

// 表单错误类型
export interface FormErrors {
  [key: string]: string;
}

// 分页类型
export interface Pagination {
  skip: number;
  limit: number;
  total: number;
}

// 导航项类型
export interface NavItem {
  name: string;
  href: string;
  icon: any; // React.ComponentType<React.SVGProps<SVGSVGElement>>;
  current: boolean;
} 