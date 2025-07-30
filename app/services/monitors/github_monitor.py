"""GitHub platform monitor."""

import re
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urlparse
import httpx
from app.services.monitors.base_monitor import BaseMonitor
from app.models.member import SocialProfile
from app.core.config.settings import settings


class GitHubMonitor(BaseMonitor):
    """GitHub platform monitor implementation."""
    
    def get_platform_name(self) -> str:
        return "github"
    
    def can_monitor(self, profile: SocialProfile) -> bool:
        """Check if this is a GitHub profile."""
        return (
            profile.platform.lower() == "github" and
            "github.com" in profile.profile_url.lower()
        )
    
    async def fetch_activities(self, profile: SocialProfile) -> List[Dict[str, Any]]:
        """Fetch GitHub activities using GitHub API."""
        activities = []
        
        try:
            # Extract username from profile URL
            username = self._extract_github_username(profile.profile_url)
            if not username:
                return activities
            
            # Use GitHub API
            headers = {}
            if settings.github_token:
                headers["Authorization"] = f"token {settings.github_token}"
            
            async with httpx.AsyncClient() as client:
                # Get user events
                events_url = f"https://api.github.com/users/{username}/events"
                response = await client.get(
                    events_url,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    events = response.json()
                    activities = self._parse_github_events(events, username)
                
        except Exception as e:
            print(f"Error fetching GitHub activities: {e}")
        
        return activities
    
    def _extract_github_username(self, profile_url: str) -> str:
        """Extract GitHub username from profile URL."""
        try:
            parsed = urlparse(profile_url)
            path_parts = parsed.path.strip('/').split('/')
            if path_parts:
                return path_parts[0]
        except:
            pass
        return ""
    
    def _parse_github_events(self, events: List[Dict], username: str) -> List[Dict[str, Any]]:
        """Parse GitHub events into activities."""
        activities = []
        
        for event in events[:20]:  # Limit to recent 20 events
            try:
                event_type = event.get("type", "")
                repo = event.get("repo", {})
                repo_name = repo.get("name", "") if repo else ""
                
                # Determine activity type and content
                activity_type, content, title = self._parse_event_type(event, username)
                
                if content or title:
                    activities.append({
                        "activity_type": activity_type,
                        "title": title,
                        "content": content,
                        "url": f"https://github.com/{repo_name}" if repo_name else "",
                        "published_at": datetime.fromisoformat(event.get("created_at", "").replace('Z', '+00:00')),
                        "external_id": f"github_{event.get('id')}"
                    })
                    
            except Exception as e:
                print(f"Error parsing GitHub event: {e}")
                continue
        
        return activities
    
    def _parse_event_type(self, event: Dict, username: str) -> tuple:
        """Parse GitHub event type and extract relevant information."""
        event_type = event.get("type", "")
        payload = event.get("payload", {})
        
        if event_type == "PushEvent":
            commits = payload.get("commits", [])
            commit_messages = [commit.get("message", "") for commit in commits]
            return (
                "push",
                f"Pushed {len(commits)} commits: " + "; ".join(commit_messages[:3]),
                f"Pushed {len(commits)} commits to {event.get('repo', {}).get('name', '')}"
            )
        
        elif event_type == "CreateEvent":
            ref_type = payload.get("ref_type", "")
            ref = payload.get("ref", "")
            return (
                "create",
                f"Created {ref_type}: {ref}",
                f"Created {ref_type} '{ref}' in {event.get('repo', {}).get('name', '')}"
            )
        
        elif event_type == "PullRequestEvent":
            pr = payload.get("pull_request", {})
            action = payload.get("action", "")
            return (
                "pull_request",
                f"{action.capitalize()} pull request: {pr.get('title', '')}",
                f"{action.capitalize()} PR #{pr.get('number', '')} in {event.get('repo', {}).get('name', '')}"
            )
        
        elif event_type == "IssuesEvent":
            issue = payload.get("issue", {})
            action = payload.get("action", "")
            return (
                "issue",
                f"{action.capitalize()} issue: {issue.get('title', '')}",
                f"{action.capitalize()} issue #{issue.get('number', '')} in {event.get('repo', {}).get('name', '')}"
            )
        
        elif event_type == "ForkEvent":
            forkee = payload.get("forkee", {})
            return (
                "fork",
                f"Forked repository: {forkee.get('full_name', '')}",
                f"Forked {event.get('repo', {}).get('name', '')} to {forkee.get('full_name', '')}"
            )
        
        else:
            return (
                event_type.lower(),
                f"GitHub activity: {event_type}",
                f"{event_type} in {event.get('repo', {}).get('name', '')}"
            )
    
    def parse_activity(self, raw_activity: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw GitHub activity data."""
        return {
            "activity_type": raw_activity.get("activity_type", "activity"),
            "title": raw_activity.get("title"),
            "content": raw_activity.get("content", ""),
            "url": raw_activity.get("url"),
            "external_id": raw_activity.get("external_id"),
            "published_at": raw_activity.get("published_at")
        } 