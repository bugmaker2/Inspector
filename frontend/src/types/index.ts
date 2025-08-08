// API响应类型
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: string;
}

// 基础类型
export interface BaseEntity {
  id: number;
  created_at: string;
  updated_at?: string;
}

// 成员相关类型
export interface Member extends BaseEntity {
  name: string;
  email: string;
  position?: string;
  department?: string;
  is_active: boolean;
  social_profiles?: SocialProfile[];
  activities?: Activity[];
}

export interface MemberCreate {
  name: string;
  email: string;
  position?: string;
  department?: string;
}

export interface MemberUpdate extends Partial<MemberCreate> {
  is_active?: boolean;
}

// 社交配置相关类型
export interface SocialProfile extends BaseEntity {
  member_id: number;
  platform: string;
  profile_url: string;
  username?: string;
  is_active: boolean;
  last_checked?: string;
  member?: Member;
  activities?: Activity[];
}

export interface SocialProfileCreate {
  platform: string;
  profile_url: string;
  username?: string;
}

export interface SocialProfileUpdate extends Partial<SocialProfileCreate> {
  is_active?: boolean;
}

// 活动相关类型
export interface Activity extends BaseEntity {
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
  member?: Member;
  social_profile?: SocialProfile;
}

// 总结相关类型
export interface Summary extends BaseEntity {
  title: string;
  content: string;
  content_en?: string;
  summary_type?: string;
  start_date?: string;
  end_date?: string;
  member_count: number;
  activity_count: number;
  is_sent: boolean;
  sent_at?: string;
}

// 监控相关类型
export interface MonitoringResult {
  status: string;
  new_activities: number;
  platform_results?: Record<string, any>;
}

export interface DashboardStats {
  total_members: number;
  active_members: number;
  total_activities: number;
  activities_today: number;
  activities_this_week: number;
  latest_summary?: Summary;
}

// 设置相关类型
export interface SystemSettings {
  monitoring_interval_minutes: number;
  summary_frequency_hours: number;
  platforms_to_monitor: string[];
}

export interface ApiSettings {
  openai_api_key?: string;
  openai_model: string;
  openai_base_url: string;
  github_token?: string;
}

// 导出相关类型
export interface ExportParams {
  start_date?: string;
  end_date?: string;
  platform?: string;
  member_id?: number;
  summary_type?: string;
  include_inactive?: boolean;
}

// 通知相关类型
export interface Notification extends BaseEntity {
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  data?: Record<string, any>;
  read: boolean;
}

export interface NotificationCreate {
  title: string;
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error';
  data?: Record<string, any>;
}

// 健康检查相关类型
export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
}

export interface DatabaseHealth {
  status: 'healthy' | 'unhealthy';
  pool_stats?: {
    pool_size: number;
    checked_in: number;
    checked_out: number;
    overflow: number;
    invalid?: number;
  };
  error?: string;
}

export interface DetailedHealth extends HealthStatus {
  database: DatabaseHealth;
  components: {
    database: DatabaseHealth;
    api: { status: string };
    monitoring: { status: string };
    ai_summarizer: { status: string };
    notifications: { status: string };
  };
}

// 搜索和过滤相关类型
export interface FilterOption {
  value: string;
  label: string;
}

export interface SearchFilterConfig {
  name: string;
  label: string;
  options: FilterOption[];
}

// 流式总结相关类型
export interface StreamingProgress {
  type: string;
  progress?: number;
  message?: string;
  content?: string;
  language?: string;
  summary?: Summary;
  error?: string;
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