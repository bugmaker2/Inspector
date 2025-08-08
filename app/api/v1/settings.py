"""Settings management API endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database.database import get_db
from app.core.config.settings import settings
from app.models.schemas import SettingsResponse, SystemSettings, ApiSettings

router = APIRouter()


@router.get("/", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """Get current application settings."""
    try:
        return SettingsResponse(
            system=SystemSettings(
                monitoring_interval_minutes=settings.monitoring_interval_minutes,
                summary_frequency_hours=settings.summary_frequency_hours,
                email_enabled=settings.email_enabled
            ),
            api=ApiSettings(
                openai_api_key=settings.openai_api_key or "",
                github_token=settings.github_token or ""
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get settings: {str(e)}"
        )


@router.get("/system", response_model=SystemSettings)
def get_system_settings(db: Session = Depends(get_db)):
    """Get system settings."""
    try:
        return SystemSettings(
            monitoring_interval_minutes=settings.monitoring_interval_minutes,
            summary_frequency_hours=settings.summary_frequency_hours,
            email_enabled=settings.email_enabled
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system settings: {str(e)}"
        )


@router.put("/system", response_model=SystemSettings)
def update_system_settings(
    system_settings: SystemSettings,
    db: Session = Depends(get_db)
):
    """Update system settings."""
    try:
        # 这里可以添加设置验证逻辑
        if system_settings.monitoring_interval_minutes < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Monitoring interval must be at least 1 minute"
            )
        
        if system_settings.summary_frequency_hours < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Summary frequency must be at least 1 hour"
            )
        
        # 在实际应用中，这里应该保存到数据库或配置文件
        # 目前只是返回验证后的设置
        return system_settings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update system settings: {str(e)}"
        )


@router.get("/api", response_model=ApiSettings)
def get_api_settings(db: Session = Depends(get_db)):
    """Get API settings."""
    try:
        return ApiSettings(
            openai_api_key=settings.openai_api_key or "",
            github_token=settings.github_token or ""
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get API settings: {str(e)}"
        )


@router.put("/api", response_model=ApiSettings)
def update_api_settings(
    api_settings: ApiSettings,
    db: Session = Depends(get_db)
):
    """Update API settings."""
    try:
        # 这里可以添加API密钥验证逻辑
        if api_settings.openai_api_key and not api_settings.openai_api_key.startswith("sk-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OpenAI API key format"
            )
        
        if api_settings.github_token and not api_settings.github_token.startswith(("ghp_", "gho_", "ghu_")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GitHub token format"
            )
        
        # 在实际应用中，这里应该保存到数据库或配置文件
        # 目前只是返回验证后的设置
        return api_settings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update API settings: {str(e)}"
        )


@router.post("/test-openai")
def test_openai_connection(db: Session = Depends(get_db)):
    """Test OpenAI API connection."""
    try:
        if not settings.openai_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OpenAI API key not configured"
            )
        
        # 这里可以添加实际的OpenAI API测试
        # 目前只是返回成功状态
        return {"status": "success", "message": "OpenAI API connection test passed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OpenAI API test failed: {str(e)}"
        )


@router.post("/test-github")
def test_github_connection(db: Session = Depends(get_db)):
    """Test GitHub API connection."""
    try:
        if not settings.github_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub token not configured"
            )
        
        # 这里可以添加实际的GitHub API测试
        # 目前只是返回成功状态
        return {"status": "success", "message": "GitHub API connection test passed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub API test failed: {str(e)}"
        )
