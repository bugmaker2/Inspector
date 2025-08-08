"""Data export API endpoints."""

import io
import csv
import json
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

from app.core.database.database import get_db
from app.models.member import Member, Activity, Summary, SocialProfile
from app.models.schemas import Activity as ActivitySchema, Summary as SummarySchema

router = APIRouter()


@router.get("/activities/csv")
async def export_activities_csv(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    platform: Optional[str] = Query(None, description="Platform filter"),
    member_id: Optional[int] = Query(None, description="Member ID filter"),
    db: Session = Depends(get_db)
):
    """Export activities to CSV format."""
    try:
        # Build query
        query = db.query(Activity).join(Member).join(SocialProfile)
        
        # Apply filters
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Activity.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Activity.created_at < end_dt)
        
        if platform:
            query = query.filter(SocialProfile.platform == platform)
        
        if member_id:
            query = query.filter(Activity.member_id == member_id)
        
        activities = query.all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "ID", "Member", "Platform", "Activity Type", "Title", "Content", 
            "URL", "Created At", "Updated At"
        ])
        
        # Write data
        for activity in activities:
            writer.writerow([
                activity.id,
                activity.member.name if activity.member else "",
                activity.platform,
                activity.activity_type or "",
                activity.title or "",
                activity.content or "",
                activity.url or "",
                activity.created_at.isoformat() if activity.created_at else "",
                activity.created_at.isoformat() if activity.created_at else ""  # Activity没有updated_at字段
            ])
        
        output.seek(0)
        
        # Generate filename
        filename = f"activities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/activities/excel")
async def export_activities_excel(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    platform: Optional[str] = Query(None, description="Platform filter"),
    member_id: Optional[int] = Query(None, description="Member ID filter"),
    db: Session = Depends(get_db)
):
    """Export activities to Excel format."""
    try:
        # Build query
        query = db.query(Activity).join(Member).join(SocialProfile)
        
        # Apply filters
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Activity.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Activity.created_at < end_dt)
        
        if platform:
            query = query.filter(SocialProfile.platform == platform)
        
        if member_id:
            query = query.filter(Activity.member_id == member_id)
        
        activities = query.all()
        
        # Prepare data for pandas
        data = []
        for activity in activities:
            data.append({
                "ID": activity.id,
                "Member": activity.member.name if activity.member else "",
                "Platform": activity.platform,
                "Activity Type": activity.activity_type or "",
                "Title": activity.title or "",
                "Content": activity.content or "",
                "URL": activity.url or "",
                "Created At": activity.created_at.isoformat() if activity.created_at else "",
                "Updated At": activity.created_at.isoformat() if activity.created_at else ""  # Activity没有updated_at字段
            })
        
        # Create DataFrame and Excel file
        df = pd.DataFrame(data)
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Activities', index=False)
        
        output.seek(0)
        
        # Generate filename
        filename = f"activities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/summaries/pdf")
async def export_summaries_pdf(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    summary_type: Optional[str] = Query(None, description="Summary type (daily/weekly)"),
    db: Session = Depends(get_db)
):
    """Export summaries to PDF format."""
    try:
        # Build query
        query = db.query(Summary)
        
        # Apply filters
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Summary.start_date >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Summary.end_date < end_dt)
        
        if summary_type:
            query = query.filter(Summary.summary_type == summary_type)
        
        summaries = query.order_by(Summary.created_at.desc()).all()
        
        # Create PDF
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph("Inspector - 团队活动总结报告", title_style))
        story.append(Spacer(1, 20))
        
        # Summary table
        if summaries:
            data = [["类型", "开始日期", "结束日期", "创建时间", "状态"]]
            for summary in summaries:
                data.append([
                    summary.summary_type or "",
                    summary.start_date.strftime("%Y-%m-%d") if summary.start_date else "",
                    summary.end_date.strftime("%Y-%m-%d") if summary.end_date else "",
                    summary.created_at.strftime("%Y-%m-%d %H:%M") if summary.created_at else "",
                    "已发送" if summary.sent_at else "未发送"
                ])
            
            table = Table(data, colWidths=[1*inch, 1.2*inch, 1.2*inch, 1.5*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Add summary content
            for summary in summaries[:3]:  # Show first 3 summaries
                story.append(Paragraph(f"<b>{summary.summary_type} 总结</b>", styles['Heading2']))
                story.append(Paragraph(f"时间范围: {summary.start_date.strftime('%Y-%m-%d')} 至 {summary.end_date.strftime('%Y-%m-%d')}", styles['Normal']))
                story.append(Spacer(1, 10))
                
                # Add content (truncated for PDF)
                content = summary.content[:500] + "..." if len(summary.content) > 500 else summary.content
                story.append(Paragraph(content, styles['Normal']))
                story.append(Spacer(1, 20))
        else:
            story.append(Paragraph("暂无总结数据", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,
            textColor=colors.grey
        )
        story.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
        
        doc.build(story)
        output.seek(0)
        
        # Generate filename
        filename = f"summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return StreamingResponse(
            output,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/members/json")
async def export_members_json(
    include_inactive: bool = Query(False, description="Include inactive members"),
    db: Session = Depends(get_db)
):
    """Export members to JSON format."""
    try:
        query = db.query(Member)
        if not include_inactive:
            query = query.filter(Member.is_active == True)
        
        members = query.all()
        
        # Prepare data
        data = []
        for member in members:
            member_data = {
                "id": member.id,
                "name": member.name,
                "email": member.email,
                "position": member.position,
                "is_active": member.is_active,
                "created_at": member.created_at.isoformat() if member.created_at else None,
                "updated_at": member.updated_at.isoformat() if member.updated_at else None,
                "social_profiles": []
            }
            
            # Add social profiles
            for profile in member.social_profiles:
                member_data["social_profiles"].append({
                    "platform": profile.platform,
                    "profile_url": profile.profile_url,
                    "username": profile.username,
                    "is_active": profile.is_active
                })
            
            data.append(member_data)
        
        # Generate filename
        filename = f"members_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return StreamingResponse(
            io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/dashboard/stats")
async def export_dashboard_stats(
    db: Session = Depends(get_db)
):
    """Export dashboard statistics."""
    try:
        from app.api.v1.monitoring import get_monitoring_stats
        
        # Get stats
        stats = get_monitoring_stats(db)
        
        # Add export timestamp
        stats["exported_at"] = datetime.now().isoformat()
        stats["export_format"] = "json"
        
        # Generate filename
        filename = f"dashboard_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return StreamingResponse(
            io.BytesIO(json.dumps(stats, ensure_ascii=False, indent=2).encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
