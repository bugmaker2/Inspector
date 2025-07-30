"""LLM-based activity summarization service."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from openai import OpenAI
from app.models.member import Activity, Summary, Member
from app.core.config.settings import settings


class LLMSummarizer:
    """LLM-based summarization service."""
    
    def __init__(self, db: Session):
        self.db = db
        self.client = None
        if settings.openai_api_key:
            self.client = OpenAI(api_key=settings.openai_api_key)
    
    def can_summarize(self) -> bool:
        """Check if LLM summarization is available."""
        return self.client is not None and settings.openai_api_key is not None
    
    async def generate_daily_summary(self, date: Optional[datetime] = None) -> Optional[Summary]:
        """Generate daily activity summary."""
        if not self.can_summarize():
            return None
        
        if date is None:
            date = datetime.utcnow().date()
        
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        activities = self._get_activities_in_range(start_date, end_date)
        
        if not activities:
            return None
        
        summary_content = await self._generate_summary_content(
            activities, "daily", start_date, end_date
        )
        
        if not summary_content:
            return None
        
        # Create summary record
        summary = Summary(
            title=f"Daily Activity Summary - {date.strftime('%Y-%m-%d')}",
            content=summary_content,
            summary_type="daily",
            start_date=start_date,
            end_date=end_date,
            member_count=len(set(activity.member_id for activity in activities)),
            activity_count=len(activities)
        )
        
        self.db.add(summary)
        self.db.commit()
        self.db.refresh(summary)
        
        return summary
    
    async def generate_weekly_summary(self, start_date: Optional[datetime] = None) -> Optional[Summary]:
        """Generate weekly activity summary."""
        if not self.can_summarize():
            return None
        
        if start_date is None:
            # Start from Monday of current week
            today = datetime.utcnow().date()
            start_date = today - timedelta(days=today.weekday())
        
        end_date = start_date + timedelta(days=6)
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        activities = self._get_activities_in_range(start_datetime, end_datetime)
        
        if not activities:
            return None
        
        summary_content = await self._generate_summary_content(
            activities, "weekly", start_datetime, end_datetime
        )
        
        if not summary_content:
            return None
        
        # Create summary record
        summary = Summary(
            title=f"Weekly Activity Summary - {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            content=summary_content,
            summary_type="weekly",
            start_date=start_datetime,
            end_date=end_datetime,
            member_count=len(set(activity.member_id for activity in activities)),
            activity_count=len(activities)
        )
        
        self.db.add(summary)
        self.db.commit()
        self.db.refresh(summary)
        
        return summary
    
    async def generate_custom_summary(
        self, 
        start_date: datetime, 
        end_date: datetime,
        title: str
    ) -> Optional[Summary]:
        """Generate custom date range summary."""
        if not self.can_summarize():
            return None
        
        activities = self._get_activities_in_range(start_date, end_date)
        
        if not activities:
            return None
        
        summary_content = await self._generate_summary_content(
            activities, "custom", start_date, end_date
        )
        
        if not summary_content:
            return None
        
        # Create summary record
        summary = Summary(
            title=title,
            content=summary_content,
            summary_type="custom",
            start_date=start_date,
            end_date=end_date,
            member_count=len(set(activity.member_id for activity in activities)),
            activity_count=len(activities)
        )
        
        self.db.add(summary)
        self.db.commit()
        self.db.refresh(summary)
        
        return summary
    
    def _get_activities_in_range(self, start_date: datetime, end_date: datetime) -> List[Activity]:
        """Get activities within the specified date range."""
        return self.db.query(Activity).filter(
            Activity.created_at >= start_date,
            Activity.created_at <= end_date
        ).order_by(Activity.created_at.desc()).all()
    
    async def _generate_summary_content(
        self, 
        activities: List[Activity], 
        summary_type: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[str]:
        """Generate summary content using LLM."""
        if not activities:
            return None
        
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
            member = self.db.query(Member).filter(Member.id == member_id).first()
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
        
        # Create prompt for LLM
        prompt = self._create_summary_prompt(activity_data, summary_type, start_date, end_date)
        
        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional social media activity analyst. Create concise, informative summaries of team member activities across various platforms."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating LLM summary: {e}")
            return None
    
    def _create_summary_prompt(
        self, 
        activity_data: List[Dict], 
        summary_type: str,
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """Create prompt for LLM summarization."""
        
        date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        prompt = f"""
Please create a {summary_type} summary of team member social media activities for the period {date_range}.

Activity Data:
{self._format_activity_data(activity_data)}

Please provide a comprehensive summary that includes:
1. Overall activity overview and trends
2. Key highlights from each team member
3. Platform-specific insights (LinkedIn, GitHub, etc.)
4. Notable achievements or milestones
5. Recommendations or observations

Format the summary in a professional, easy-to-read format with clear sections and bullet points where appropriate.
"""
        
        return prompt
    
    def _format_activity_data(self, activity_data: List[Dict]) -> str:
        """Format activity data for LLM prompt."""
        formatted = ""
        
        for member_data in activity_data:
            formatted += f"\n{member_data['member_name']} ({member_data['member_position']}):\n"
            
            for activity in member_data['activities']:
                formatted += f"- {activity['platform'].upper()}: {activity['type']}"
                if activity['title']:
                    formatted += f" - {activity['title']}"
                if activity['content']:
                    formatted += f"\n  Content: {activity['content'][:200]}..."
                formatted += "\n"
        
        return formatted 