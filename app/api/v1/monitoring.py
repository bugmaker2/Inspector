"""Monitoring and summarization API endpoints."""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database.database import get_db
from app.models.member import Member, Activity, Summary
from app.models.schemas import Activity as ActivitySchema, Summary as SummarySchema, DashboardStats
from app.services.monitors.monitor_manager import MonitorManager
from app.services.summarizers.llm_summarizer import LLMSummarizer

router = APIRouter()


@router.post("/run-monitoring", status_code=status.HTTP_200_OK)
async def run_monitoring(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run monitoring for all social profiles."""
    try:
        monitor_manager = MonitorManager(db)
        result = await monitor_manager.run_scheduled_monitoring()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Monitoring failed: {str(e)}"
        )


@router.post("/monitor-profile/{profile_id}", status_code=status.HTTP_200_OK)
async def monitor_specific_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """Monitor a specific social profile."""
    try:
        monitor_manager = MonitorManager(db)
        activities = await monitor_manager.monitor_specific_profile(profile_id)
        return {
            "profile_id": profile_id,
            "new_activities": len(activities),
            "activities": [ActivitySchema.from_orm(activity) for activity in activities]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile monitoring failed: {str(e)}"
        )


@router.get("/stats", response_model=DashboardStats)
def get_monitoring_stats(db: Session = Depends(get_db)):
    """Get monitoring statistics and dashboard data."""
    try:
        monitor_manager = MonitorManager(db)
        stats = monitor_manager.get_monitoring_stats()
        
        # Get recent activities
        today = datetime.utcnow().date()
        start_of_week = today - timedelta(days=today.weekday())
        
        activities_today = db.query(Activity).filter(
            Activity.created_at >= datetime.combine(today, datetime.min.time()),
            Activity.created_at <= datetime.combine(today, datetime.max.time())
        ).count()
        
        activities_this_week = db.query(Activity).filter(
            Activity.created_at >= datetime.combine(start_of_week, datetime.min.time())
        ).count()
        
        total_activities = db.query(Activity).count()
        
        # Get latest summary
        latest_summary = db.query(Summary).order_by(Summary.created_at.desc()).first()
        
        # Get actual member counts
        total_members = db.query(Member).count()
        active_members = db.query(Member).filter(Member.is_active == True).count()
        
        return DashboardStats(
            total_members=total_members,
            active_members=active_members,
            total_activities=total_activities,
            activities_today=activities_today,
            activities_this_week=activities_this_week,
            latest_summary=SummarySchema.from_orm(latest_summary) if latest_summary else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/activities", response_model=List[ActivitySchema])
def get_activities(
    skip: int = 0,
    limit: int = 50,
    platform: str = None,
    member_id: int = None,
    db: Session = Depends(get_db)
):
    """Get recent activities with optional filtering."""
    query = db.query(Activity)
    
    if platform:
        query = query.filter(Activity.platform == platform)
    
    if member_id:
        query = query.filter(Activity.member_id == member_id)
    
    activities = query.order_by(Activity.created_at.desc()).offset(skip).limit(limit).all()
    return activities


@router.post("/generate-daily-summary", response_model=SummarySchema, status_code=status.HTTP_201_CREATED)
async def generate_daily_summary(
    date: str = None,
    db: Session = Depends(get_db)
):
    """Generate daily activity summary."""
    try:
        summarizer = LLMSummarizer(db)
        
        if not summarizer.can_summarize():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LLM summarization not available. Please configure OpenAI API key."
            )
        
        target_date = None
        if date:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        
        summary = await summarizer.generate_daily_summary(target_date)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No activities found for the specified date"
            )
        
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation failed: {str(e)}"
        )


@router.post("/generate-weekly-summary", response_model=SummarySchema, status_code=status.HTTP_201_CREATED)
async def generate_weekly_summary(
    start_date: str = None,
    db: Session = Depends(get_db)
):
    """Generate weekly activity summary."""
    try:
        summarizer = LLMSummarizer(db)
        
        if not summarizer.can_summarize():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LLM summarization not available. Please configure OpenAI API key."
            )
        
        target_start_date = None
        if start_date:
            try:
                target_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        
        summary = await summarizer.generate_weekly_summary(target_start_date)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No activities found for the specified week"
            )
        
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation failed: {str(e)}"
        )


@router.get("/summaries", response_model=List[SummarySchema])
def get_summaries(
    skip: int = 0,
    limit: int = 20,
    summary_type: str = None,
    language: str = "chinese",  # 添加语言参数，默认为中文
    db: Session = Depends(get_db)
):
    """Get summaries with optional filtering and language selection."""
    try:
        query = db.query(Summary)
        
        if summary_type:
            query = query.filter(Summary.summary_type == summary_type)
        
        summaries = query.order_by(Summary.created_at.desc()).offset(skip).limit(limit).all()
        
        # 根据语言参数返回相应的内容
        result = []
        for summary in summaries:
            summary_dict = SummarySchema.from_orm(summary).dict()
            if language == "english" and summary.content_en:
                summary_dict["content"] = summary.content_en
            # 如果选择英文但没有英文内容，保持中文内容
            result.append(SummarySchema(**summary_dict))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summaries: {str(e)}"
        )


@router.get("/summaries/{summary_id}", response_model=SummarySchema)
def get_summary(
    summary_id: int, 
    language: str = "chinese",  # 添加语言参数，默认为中文
    db: Session = Depends(get_db)
):
    """Get a specific summary by ID with language selection."""
    try:
        summary = db.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found"
            )
        
        summary_dict = SummarySchema.from_orm(summary).dict()
        if language == "english" and summary.content_en:
            summary_dict["content"] = summary.content_en
        # 如果选择英文但没有英文内容，保持中文内容
        
        return SummarySchema(**summary_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary: {str(e)}"
        )


@router.post("/generate-member-summary/{member_id}", response_model=SummarySchema, status_code=status.HTTP_201_CREATED)
async def generate_member_summary(
    member_id: int,
    days: int = 7,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Generate summary for a specific member's activities."""
    try:
        summarizer = LLMSummarizer(db)
        
        if not summarizer.can_summarize():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LLM summarization not available. Please configure OpenAI API key."
            )
        
        # Parse dates if provided
        parsed_start_date = None
        parsed_end_date = None
        
        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use YYYY-MM-DD"
                )
        
        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use YYYY-MM-DD"
                )
        
        summary = await summarizer.generate_member_summary(
            member_id=member_id,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            days=days
        )
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No activities found for the specified member and date range"
            )
        
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Member summary generation failed: {str(e)}"
        ) 