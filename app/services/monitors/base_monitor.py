"""Base monitor class for social media platforms."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.member import SocialProfile, Activity


class BaseMonitor(ABC):
    """Base class for social media platform monitors."""
    
    def __init__(self, db: Session):
        self.db = db
        self.platform_name = self.get_platform_name()
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return the platform name."""
        pass
    
    @abstractmethod
    def can_monitor(self, profile: SocialProfile) -> bool:
        """Check if this monitor can handle the given profile."""
        pass
    
    @abstractmethod
    async def fetch_activities(self, profile: SocialProfile) -> List[Dict[str, Any]]:
        """Fetch recent activities from the platform."""
        pass
    
    @abstractmethod
    def parse_activity(self, raw_activity: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw activity data into standardized format."""
        pass
    
    async def monitor_profile(self, profile: SocialProfile) -> List[Activity]:
        """Monitor a single profile and return new activities."""
        if not self.can_monitor(profile):
            return []
        
        try:
            # Fetch activities from platform
            raw_activities = await self.fetch_activities(profile)
            new_activities = []
            
            for raw_activity in raw_activities:
                # Parse activity
                parsed_activity = self.parse_activity(raw_activity)
                
                # Check if activity already exists
                existing_activity = self.db.query(Activity).filter(
                    Activity.external_id == parsed_activity.get("external_id"),
                    Activity.social_profile_id == profile.id
                ).first()
                
                if not existing_activity:
                    # Create new activity
                    activity = Activity(
                        member_id=profile.member_id,
                        social_profile_id=profile.id,
                        platform=self.platform_name,
                        **parsed_activity
                    )
                    self.db.add(activity)
                    new_activities.append(activity)
            
            # Update last checked time
            profile.last_checked = datetime.utcnow()
            self.db.commit()
            
            return new_activities
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error monitoring {self.platform_name} profile: {str(e)}")
    
    def get_existing_activity_ids(self, profile_id: int) -> List[str]:
        """Get list of existing activity external IDs for a profile."""
        activities = self.db.query(Activity.external_id).filter(
            Activity.social_profile_id == profile_id,
            Activity.external_id.isnot(None)
        ).all()
        return [activity[0] for activity in activities] 