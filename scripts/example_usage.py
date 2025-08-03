"""Example usage of Inspector API."""

import requests
import json
from datetime import datetime


class InspectorClient:
    """Client for Inspector API."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1"
    
    def create_member(self, name, email, position=None, department=None):
        """Create a new team member."""
        data = {
            "name": name,
            "email": email,
            "position": position,
            "department": department
        }
        
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/members/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create member: {response.text}")
    
    def add_social_profile(self, member_id, platform, profile_url, username=None):
        """Add a social profile to a member."""
        data = {
            "platform": platform,
            "profile_url": profile_url,
            "username": username
        }
        
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/members/{member_id}/social-profiles",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to add social profile: {response.text}")
    
    def run_monitoring(self):
        """Run monitoring for all profiles."""
        response = requests.post(f"{self.base_url}{self.api_prefix}/monitoring/run-monitoring")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to run monitoring: {response.text}")
    
    def generate_daily_summary(self, date=None):
        """Generate daily summary."""
        params = {}
        if date:
            params["date"] = date
        
        response = requests.post(
            f"{self.base_url}{self.api_prefix}/monitoring/generate-daily-summary",
            params=params
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to generate summary: {response.text}")
    
    def get_stats(self):
        """Get monitoring statistics."""
        response = requests.get(f"{self.base_url}{self.api_prefix}/monitoring/stats")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get stats: {response.text}")
    
    def get_members(self):
        """Get all members."""
        response = requests.get(f"{self.base_url}{self.api_prefix}/members/")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get members: {response.text}")


def main():
    """Example usage of Inspector."""
    print("🔍 Inspector Example Usage")
    print("=" * 50)
    
    # Initialize client
    client = InspectorClient()
    
    try:
        # Get current stats
        print("\n📊 Current Statistics:")
        stats = client.get_stats()
        print(f"   Total members: {stats['total_members']}")
        print(f"   Total activities: {stats['total_activities']}")
        print(f"   Activities today: {stats['activities_today']}")
        
        # Create a sample member
        print("\n👥 Creating sample member...")
        member = client.create_member(
            name="张三",
            email="zhangsan@example.com",
            position="软件工程师",
            department="技术部"
        )
        print(f"   Created member: {member['name']} (ID: {member['id']})")
        
        # Add social profiles
        print("\n🔗 Adding social profiles...")
        
        # GitHub profile
        github_profile = client.add_social_profile(
            member_id=member['id'],
            platform="github",
            profile_url="https://github.com/bugmaker2",
            username="bugmaker2"
        )
        print(f"   Added GitHub profile: {github_profile['platform']}")
        
        # LinkedIn profile
        linkedin_profile = client.add_social_profile(
            member_id=member['id'],
            platform="linkedin",
            profile_url="https://linkedin.com/in/bugmaker2",
            username="bugmaker2"
        )
        print(f"   Added LinkedIn profile: {linkedin_profile['platform']}")
        
        # Run monitoring
        print("\n🔍 Running monitoring...")
        monitoring_result = client.run_monitoring()
        print(f"   Monitoring status: {monitoring_result['status']}")
        print(f"   New activities: {monitoring_result['new_activities']}")
        
        # Get updated stats
        print("\n📊 Updated Statistics:")
        updated_stats = client.get_stats()
        print(f"   Total members: {updated_stats['total_members']}")
        print(f"   Total activities: {updated_stats['total_activities']}")
        
        # List all members
        print("\n👥 All Members:")
        members = client.get_members()
        for member in members:
            print(f"   - {member['name']} ({member['email']}) - {member['position']}")
        
        print("\n✅ Example completed successfully!")
        print("\n📖 Next steps:")
        print("1. Configure real social media profiles")
        print("2. Set up OpenAI API key for LLM summaries")
        print("3. Configure monitoring schedules")
        print("4. Set up email notifications")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 