"""User models for authentication and GitHub OAuth."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database.database import Base


class User(Base):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # 支持密码登录
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联GitHub OAuth配置
    github_config = relationship("GitHubOAuthConfig", back_populates="user", uselist=False)


class GitHubOAuthConfig(Base):
    """GitHub OAuth configuration for users."""
    
    __tablename__ = "github_oauth_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    github_user_id = Column(Integer, nullable=False)
    github_username = Column(String(255), nullable=False)
    access_token = Column(String(500), nullable=False)  # 加密存储
    token_type = Column(String(50), default="bearer")
    scope = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联用户
    user = relationship("User", back_populates="github_config") 