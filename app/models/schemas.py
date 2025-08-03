"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, EmailStr


# Member schemas
class MemberBase(BaseModel):
    name: str
    email: EmailStr
    position: Optional[str] = None
    department: Optional[str] = None


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    position: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class Member(MemberBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Social Profile schemas
class SocialProfileBase(BaseModel):
    platform: str
    profile_url: HttpUrl
    username: Optional[str] = None


class SocialProfileCreate(SocialProfileBase):
    pass


class SocialProfileUpdate(BaseModel):
    profile_url: Optional[HttpUrl] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None


class SocialProfile(SocialProfileBase):
    id: int
    member_id: int
    is_active: bool
    last_checked: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Activity schemas
class ActivityBase(BaseModel):
    platform: str
    activity_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    url: Optional[HttpUrl] = None
    external_id: Optional[str] = None
    published_at: Optional[datetime] = None


class ActivityCreate(ActivityBase):
    member_id: int
    social_profile_id: int


class Activity(ActivityBase):
    id: int
    member_id: int
    social_profile_id: int
    is_processed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Summary schemas
class SummaryBase(BaseModel):
    title: str
    content: str
    content_en: Optional[str] = None  # 英文内容
    summary_type: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SummaryCreate(SummaryBase):
    member_count: int = 0
    activity_count: int = 0


class Summary(SummaryBase):
    id: int
    member_count: int
    activity_count: int
    created_at: datetime
    is_sent: bool
    sent_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Member with social profiles
class MemberWithProfiles(Member):
    social_profiles: List[SocialProfile] = []


# Member with activities
class MemberWithActivities(Member):
    activities: List[Activity] = []


# Dashboard response
class DashboardStats(BaseModel):
    total_members: int
    active_members: int
    total_activities: int
    activities_today: int
    activities_this_week: int
    latest_summary: Optional[Summary] = None


# Monitoring configuration
class MonitoringConfig(BaseModel):
    monitoring_interval_minutes: int
    summary_frequency_hours: int
    platforms_to_monitor: List[str] 