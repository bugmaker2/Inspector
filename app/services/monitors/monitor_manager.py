"""Monitor manager for coordinating all platform monitors."""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.member import SocialProfile, Activity
from app.services.monitors.linkedin_monitor import LinkedInMonitor
from app.services.monitors.github_monitor import GitHubMonitor
from app.core.config.settings import settings

logger = logging.getLogger(__name__)


class MonitorManager:
    """Manages all social media platform monitors."""
    
    def __init__(self, db: Session):
        self.db = db
        self.monitors = {
            "linkedin": LinkedInMonitor(db),
            "github": GitHubMonitor(db)
        }
    
    async def monitor_all_profiles(self) -> Dict[str, List[Activity]]:
        """Monitor all active social profiles."""
        results = {}
        
        # Get all active social profiles
        profiles = self.db.query(SocialProfile).filter(
            SocialProfile.is_active == True
        ).all()
        
        # Group profiles by platform
        profiles_by_platform = {}
        for profile in profiles:
            platform = profile.platform.lower()
            if platform not in profiles_by_platform:
                profiles_by_platform[platform] = []
            profiles_by_platform[platform].append(profile)
        
        # Monitor each platform
        for platform, platform_profiles in profiles_by_platform.items():
            if platform in self.monitors:
                monitor = self.monitors[platform]
                platform_activities = []
                
                for profile in platform_profiles:
                    try:
                        activities = await monitor.monitor_profile(profile)
                        platform_activities.extend(activities)
                    except Exception as e:
                        logger.error(f"Error monitoring profile {profile.id}: {e}")
                
                results[platform] = platform_activities
        
        return results
    
    async def monitor_specific_profile(self, profile_id: int) -> List[Activity]:
        """Monitor a specific social profile."""
        profile = self.db.query(SocialProfile).filter(
            SocialProfile.id == profile_id,
            SocialProfile.is_active == True
        ).first()
        
        if not profile:
            return []
        
        platform = profile.platform.lower()
        if platform not in self.monitors:
            return []
        
        monitor = self.monitors[platform]
        try:
            return await monitor.monitor_profile(profile)
        except Exception as e:
            logger.error(f"Error monitoring profile {profile_id}: {e}")
            return []
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        total_profiles = self.db.query(SocialProfile).filter(
            SocialProfile.is_active == True
        ).count()
        
        profiles_by_platform = {}
        for platform in self.monitors.keys():
            count = self.db.query(SocialProfile).filter(
                SocialProfile.platform == platform,
                SocialProfile.is_active == True
            ).count()
            profiles_by_platform[platform] = count
        
        recent_activities = self.db.query(Activity).filter(
            Activity.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return {
            "total_profiles": total_profiles,
            "profiles_by_platform": profiles_by_platform,
            "recent_activities": recent_activities,
            "supported_platforms": list(self.monitors.keys())
        }
    
    def get_profiles_needing_update(self, hours: int = 24) -> List[SocialProfile]:
        """Get profiles that haven't been checked recently."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return self.db.query(SocialProfile).filter(
            SocialProfile.is_active == True,
            (SocialProfile.last_checked.is_(None) | 
             SocialProfile.last_checked <= cutoff_time)
        ).all()
    
    async def run_scheduled_monitoring(self) -> Dict[str, Any]:
        """Run scheduled monitoring for all profiles."""
        logger.info(f"Starting scheduled monitoring at {datetime.utcnow()}")
        
        # Get profiles that need updating
        profiles_to_update = self.get_profiles_needing_update()
        
        if not profiles_to_update:
            logger.info("No profiles need updating")
            return {"status": "no_updates_needed"}
        
        # Monitor all profiles
        results = await self.monitor_all_profiles()
        
        # Count total new activities
        total_new_activities = sum(len(activities) for activities in results.values())
        
        logger.info(f"Monitoring completed. Found {total_new_activities} new activities")
        
        return {
            "status": "completed",
            "new_activities": total_new_activities,
            "platform_results": results
        } 