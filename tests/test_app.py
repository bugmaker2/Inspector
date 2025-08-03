"""Test script for Inspector application."""

import asyncio
import requests
import json
from datetime import datetime


def test_api_endpoints():
    """Test basic API endpoints."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Inspector API...")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data.get('message', 'Unknown')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False
    
    # Test members endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/members/")
        if response.status_code == 200:
            members = response.json()
            print(f"✅ Members endpoint: {len(members)} members found")
        else:
            print(f"❌ Members endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Members endpoint error: {e}")
    
    # Test monitoring stats
    try:
        response = requests.get(f"{base_url}/api/v1/monitoring/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Monitoring stats: {stats.get('total_members', 0)} members, {stats.get('total_activities', 0)} activities")
        else:
            print(f"❌ Monitoring stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Monitoring stats error: {e}")
    
    return True


def test_member_creation():
    """Test member creation functionality."""
    base_url = "http://localhost:8000"
    
    print("\n👥 Testing member creation...")
    
    # Create a test member
    member_data = {
        "name": "测试用户",
        "email": "test@example.com",
        "position": "测试工程师",
        "department": "测试部门"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/members/",
            json=member_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            member = response.json()
            print(f"✅ Member created: {member['name']} (ID: {member['id']})")
            return member['id']
        else:
            print(f"❌ Member creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Member creation error: {e}")
        return None


def test_social_profile_creation(member_id):
    """Test social profile creation."""
    base_url = "http://localhost:8000"
    
    print(f"\n🔗 Testing social profile creation for member {member_id}...")
    
    # Create a GitHub profile
    github_profile = {
        "platform": "github",
        "profile_url": "https://github.com/testuser",
        "username": "testuser"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/members/{member_id}/social-profiles",
            json=github_profile,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            profile = response.json()
            print(f"✅ GitHub profile created: {profile['platform']}")
            return profile['id']
        else:
            print(f"❌ GitHub profile creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ GitHub profile creation error: {e}")
        return None


def test_monitoring():
    """Test monitoring functionality."""
    base_url = "http://localhost:8000"
    
    print("\n🔍 Testing monitoring functionality...")
    
    try:
        response = requests.post(f"{base_url}/api/v1/monitoring/run-monitoring")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Monitoring completed: {result.get('status', 'unknown')}")
            print(f"   New activities: {result.get('new_activities', 0)}")
        else:
            print(f"❌ Monitoring failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Monitoring error: {e}")


def main():
    """Run all tests."""
    print("🚀 Inspector Test Suite")
    print("=" * 50)
    
    # Test basic API
    if not test_api_endpoints():
        print("❌ Basic API tests failed. Make sure the application is running.")
        return
    
    # Test member creation
    member_id = test_member_creation()
    if member_id:
        # Test social profile creation
        profile_id = test_social_profile_creation(member_id)
        
        # Test monitoring
        test_monitoring()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\n📖 Next steps:")
    print("1. Visit http://localhost:8000/docs for API documentation")
    print("2. Configure your .env file with API keys")
    print("3. Add real team members and social profiles")
    print("4. Set up monitoring schedules")


if __name__ == "__main__":
    main() 