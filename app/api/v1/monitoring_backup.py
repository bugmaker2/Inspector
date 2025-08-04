"""Monitoring and summarization API endpoints."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database.database import get_db
from app.models.member import Member, Activity, Summary
from app.models.schemas import Activity as ActivitySchema, Summary as SummarySchema, DashboardStats, MonitoringResult, Member as MemberSchema
from app.services.monitors.monitor_manager import MonitorManager
from app.services.summarizers.llm_summarizer import LLMSummarizer
import json
import asyncio

router = APIRouter()

def prepare_activity_data_for_llm(activities: List[Activity], db: Session) -> List[Dict]:
    """Prepare activity data for LLM summarization."""
    # Group activities by member
    activities_by_member = {}
    for activity in activities:
        member_id = activity.member_id
        if member_id not in activities_by_member:
            activities_by_member[member_id] = []
        activities_by_member[member_id].append(activity)
    
    # Prepare activity data for LLM
    activity_data = []
    for member_id, member_activities in activities_by_member.items():
        member = db.query(Member).filter(Member.id == member_id).first()
        if member:
            member_activity_summary = {
                "member_name": member.name,
                "member_position": member.position,
                "activities": []
            }
            
            for activity in member_activities:
                member_activity_summary["activities"].append({
                    "platform": activity.platform,
                    "type": activity.activity_type,
                    "title": activity.title,
                    "content": activity.content,
                    "url": activity.url,
                    "published_at": activity.published_at.isoformat() if activity.published_at else None
                })
            
            activity_data.append(member_activity_summary)
    
    return activity_data


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


@router.post("/generate-daily-summary-stream")
async def generate_daily_summary_stream(
    date: str = None,
    db: Session = Depends(get_db)
):
    """Generate daily activity summary with streaming response."""
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
        
        async def generate_stream():
            try:
                # 发送开始信号
                yield f"data: {json.dumps({'type': 'start', 'message': '开始生成每日总结...'})}\n\n"
                
                # 获取活动数据
                yield f"data: {json.dumps({'type': 'progress', 'message': '正在收集活动数据...', 'progress': 10})}\n\n"
                
                # 确定目标日期
                final_target_date = target_date if target_date is not None else datetime.utcnow().date()
                
                start_date = datetime.combine(final_target_date, datetime.min.time())
                end_date = datetime.combine(final_target_date, datetime.max.time())
                
                activities = summarizer._get_activities_in_range(start_date, end_date)
                
                if not activities:
                    yield f"data: {json.dumps({'type': 'error', 'message': '未找到指定日期的活动数据'})}\n\n"
                    return
                
                yield f"data: {json.dumps({'type': 'progress', 'message': f'找到 {len(activities)} 个活动', 'progress': 20})}\n\n"
                
                # 生成中文内容
                yield f"data: {json.dumps({'type': 'progress', 'message': '正在生成中文总结...', 'progress': 30})}\n\n"
                
                activity_data = [
                    {
                        "member_name": activity.member.name if activity.member else "Unknown",
                        "platform": activity.platform,
                        "content": activity.content,
                        "url": activity.url,
                        "created_at": activity.created_at.isoformat()
                    }
                    for activity in activities
                ]
                
                chinese_content = await summarizer._generate_language_content_stream(
                    activity_data, "daily", start_date, end_date, "chinese"
                )
                
                if not chinese_content:
                    yield f"data: {json.dumps({'type': 'error', 'message': '中文总结生成失败'})}\n\n"
                    return
                
                yield f"data: {json.dumps({'type': 'progress', 'message': '中文总结生成完成', 'progress': 60})}\n\n"
                
                # 生成英文内容
                yield f"data: {json.dumps({'type': 'progress', 'message': '正在生成英文总结...', 'progress': 70})}\n\n"
                
                english_content = await summarizer._generate_language_content_stream(
                    activity_data, "daily", start_date, end_date, "english"
                )
                
                if not english_content:
                    yield f"data: {json.dumps({'type': 'error', 'message': '英文总结生成失败'})}\n\n"
                    return
                
                yield f"data: {json.dumps({'type': 'progress', 'message': '英文总结生成完成', 'progress': 90})}\n\n"
                
                # 保存到数据库
                yield f"data: {json.dumps({'type': 'progress', 'message': '正在保存总结...', 'progress': 95})}\n\n"
                
                summary = Summary(
                    title=f"Daily Activity Summary - {final_target_date.strftime('%Y-%m-%d')}",
                    content=chinese_content,
                    content_en=english_content,
                    summary_type="daily",
                    start_date=start_date,
                    end_date=end_date,
                    member_count=len(set(activity.member_id for activity in activities)),
                    activity_count=len(activities)
                )
                
                db.add(summary)
                db.commit()
                db.refresh(summary)
                
                yield f"data: {json.dumps({'type': 'progress', 'message': '总结保存完成', 'progress': 100})}\n\n"
                
                # 发送完成信号和结果
                yield f"data: {json.dumps({'type': 'complete', 'summary': SummarySchema.from_orm(summary).dict()})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': f'生成失败: {str(e)}'})}\n\n"
        

        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
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


@router.post("/generate-weekly-summary-stream")
async def generate_weekly_summary_stream(
    start_date: str = None,
    db: Session = Depends(get_db)
):
    """Generate weekly activity summary with streaming response."""
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
        
        async def generate_stream():
            try:
                # 发送开始信号
                yield f"data: {json.dumps({'type': 'start', 'message': '开始生成每周总结...'})}\n\n"
                
                # 获取活动数据
                yield f"data: {json.dumps({'type': 'progress', 'message': '正在收集活动数据...', 'progress': 10})}\n\n"
                
                # 确定目标开始日期
                final_target_start_date = target_start_date
                if final_target_start_date is None:
                    # Start from Monday of current week
                    today = datetime.utcnow().date()
                    final_target_start_date = today - timedelta(days=today.weekday())
                
                end_date = final_target_start_date + timedelta(days=6)
                start_datetime = datetime.combine(final_target_start_date, datetime.min.time())
                end_datetime = datetime.combine(end_date, datetime.max.time())
                
                activities = summarizer._get_activities_in_range(start_datetime, end_datetime)
                
                if not activities:
                    yield f"data: {json.dumps({'type': 'error', 'message': '未找到指定周的活动数据'})}\n\n"
                    return
                
                yield f"data: {json.dumps({'type': 'progress', 'message': f'找到 {len(activities)} 个活动', 'progress': 20})}\n\n"
                
                # 生成中文内容
                yield f"data: {json.dumps({'type': 'progress', 'message': '正在生成中文总结...', 'progress': 30})}\n\n"
                
                activity_data = [
                    {
                        "member_name": activity.member.name if activity.member else "Unknown",
                        "platform": activity.platform,
                        "content": activity.content,
                        "url": activity.url,
                        "created_at": activity.created_at.isoformat()
                    }
                    for activity in activities
                ]
                
                chinese_content = await summarizer._generate_language_content_stream(
                    activity_data, "weekly", start_datetime, end_datetime, "chinese"
                )
                
                if not chinese_content:
                    yield f"data: {json.dumps({'type': 'error', 'message': '中文总结生成失败'})}\n\n"
                    return
                
                yield f"data: {json.dumps({'type': 'progress', 'message': '中文总结生成完成', 'progress': 60})}\n\n"
                
                # 生成英文内容
                yield f"data: {json.dumps({'type': 'progress', 'message': '正在生成英文总结...', 'progress': 70})}\n\n"
                
                english_content = await summarizer._generate_language_content_stream(
                    activity_data, "weekly", start_datetime, end_datetime, "english"
                )
                
                if not english_content:
                    yield f"data: {json.dumps({'type': 'error', 'message': '英文总结生成失败'})}\n\n"
                    return
                
                yield f"data: {json.dumps({'type': 'progress', 'message': '英文总结生成完成', 'progress': 90})}\n\n"
                
                # 保存到数据库
                yield f"data: {json.dumps({'type': 'progress', 'message': '正在保存总结...', 'progress': 95})}\n\n"
                
                summary = Summary(
                    title=f"Weekly Activity Summary - {final_target_start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                    content=chinese_content,
                    content_en=english_content,
                    summary_type="weekly",
                    start_date=start_datetime,
                    end_date=end_datetime,
                    member_count=len(set(activity.member_id for activity in activities)),
                    activity_count=len(activities)
                )
                
                db.add(summary)
                db.commit()
                db.refresh(summary)
                
                yield f"data: {json.dumps({'type': 'progress', 'message': '总结保存完成', 'progress': 100})}\n\n"
                
                # 发送完成信号和结果
                yield f"data: {json.dumps({'type': 'complete', 'summary': SummarySchema.from_orm(summary).dict()})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': f'生成失败: {str(e)}'})}\n\n"
        

        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
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