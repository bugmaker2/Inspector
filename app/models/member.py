"""Member and social media profile models."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database.database import Base


class Member(Base):
    """Member model for storing team member information."""
    
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True)
    position = Column(String(100))
    department = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    social_profiles = relationship("SocialProfile", back_populates="member", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="member", cascade="all, delete-orphan")


class SocialProfile(Base):
    """Social media profile model."""
    
    __tablename__ = "social_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    platform = Column(String(50), nullable=False)  # linkedin, github, twitter, etc.
    profile_url = Column(String(500), nullable=False)
    username = Column(String(100))
    is_active = Column(Boolean, default=True)
    last_checked = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    member = relationship("Member", back_populates="social_profiles")
    activities = relationship("Activity", back_populates="social_profile", cascade="all, delete-orphan")


class Activity(Base):
    """Social media activity model."""
    
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    social_profile_id = Column(Integer, ForeignKey("social_profiles.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    activity_type = Column(String(50))  # post, comment, like, follow, etc.
    title = Column(String(500))
    content = Column(Text)
    url = Column(String(500))
    external_id = Column(String(255), unique=True, index=True)  # Platform-specific ID
    published_at = Column(DateTime)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    member = relationship("Member", back_populates="activities")
    social_profile = relationship("SocialProfile", back_populates="activities")


class Summary(Base):
    """Summary report model."""
    
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # 中文内容
    content_en = Column(Text)  # 英文内容
    summary_type = Column(String(50))  # daily, weekly, monthly
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    member_count = Column(Integer, default=0)
    activity_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime) 