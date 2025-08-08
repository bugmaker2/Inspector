"""Pydantic schemas for data validation and serialization."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Member schemas
class MemberBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    position: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)


class MemberCreate(MemberBase):
    pass


class MemberUpdate(MemberBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$")
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
    platform: str = Field(..., min_length=1, max_length=50)
    profile_url: str = Field(..., min_length=1, max_length=500)
    username: Optional[str] = Field(None, max_length=100)


class SocialProfileCreate(SocialProfileBase):
    pass


class SocialProfileUpdate(SocialProfileBase):
    platform: Optional[str] = Field(None, min_length=1, max_length=50)
    profile_url: Optional[str] = Field(None, min_length=1, max_length=500)
    is_active: Optional[bool] = None


class SocialProfile(SocialProfileBase):
    id: int
    member_id: int
    is_active: bool
    last_checked: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Activity schemas
class Activity(BaseModel):
    id: int
    member_id: int
    social_profile_id: int
    platform: str
    activity_type: str
    title: Optional[str]
    content: Optional[str]
    url: Optional[str]
    external_id: Optional[str]
    published_at: Optional[datetime]
    is_processed: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# Summary schemas
class Summary(BaseModel):
    id: int
    summary_type: str
    title: str
    content: str
    content_en: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    member_count: int = 0
    activity_count: int = 0
    created_at: datetime
    is_sent: bool = False
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True


# Monitoring schemas
class MonitoringResult(BaseModel):
    status: str
    new_activities: int
    platform_results: Optional[dict] = None


# Member schemas with relationships
class MemberWithProfiles(Member):
    social_profiles: List[SocialProfile] = []


class MemberWithActivities(Member):
    activities: List[Activity] = []


# Dashboard schemas
class DashboardStats(BaseModel):
    total_members: int
    active_members: int
    total_activities: int
    activities_today: int
    activities_this_week: int
    latest_summary: Optional[Summary] = None


# Configuration schemas
class MonitoringConfig(BaseModel):
    monitoring_interval_minutes: int
    summary_frequency_hours: int
    platforms_to_monitor: List[str]


# Settings schemas
class SystemSettings(BaseModel):
    monitoring_interval_minutes: int = Field(..., ge=1, le=1440)
    summary_frequency_hours: int = Field(..., ge=1, le=168)
    email_enabled: bool = False


class ApiSettings(BaseModel):
    openai_api_key: str = ""
    github_token: str = ""


class SettingsResponse(BaseModel):
    system: SystemSettings
    api: ApiSettings 