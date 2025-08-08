#!/usr/bin/env python3
"""Test script to verify all API endpoints are working correctly."""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, expected_status=200, base_url=None):
    """Test a single API endpoint."""
    if base_url is None:
        base_url = BASE_URL
    url = f"{base_url}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url)
        else:
            print(f"❌ Unknown method: {method}")
            return False
            
        if response.status_code == expected_status:
            print(f"✅ {method} {endpoint} - {response.status_code}")
            if response.content:
                try:
                    data = response.json()
                    if isinstance(data, dict) and len(data) > 0:
                        print(f"   📄 Response: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    pass
            return True
        else:
            print(f"❌ {method} {endpoint} - {response.status_code} (expected {expected_status})")
            if response.content:
                try:
                    error_data = response.json()
                    print(f"   💥 Error: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"   💥 Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - Connection Error (server not running?)")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Exception: {str(e)}")
        return False

def main():
    """Run all API tests."""
    print("🚀 Inspector API Integration Test")
    print("=" * 50)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    print()
    
    # Test results
    total_tests = 0
    passed_tests = 0
    
    # Health check
    print("🏥 Health Check:")
    total_tests += 1
    if test_endpoint("GET", "/health", expected_status=200, base_url=HEALTH_URL):
        passed_tests += 1
    print()
    
    # Settings endpoints
    print("⚙️ Settings API:")
    total_tests += 2
    if test_endpoint("GET", "/settings/system"):
        passed_tests += 1
    if test_endpoint("GET", "/settings/api"):
        passed_tests += 1
    print()
    
    # Members endpoints
    print("👥 Members API:")
    total_tests += 1
    if test_endpoint("GET", "/members/"):
        passed_tests += 1
    print()
    
    # Monitoring endpoints
    print("📊 Monitoring API:")
    total_tests += 3
    if test_endpoint("GET", "/monitoring/stats"):
        passed_tests += 1
    if test_endpoint("GET", "/monitoring/activities"):
        passed_tests += 1
    if test_endpoint("GET", "/monitoring/summaries"):
        passed_tests += 1
    print()
    
    # Notifications endpoints
    print("🔔 Notifications API:")
    total_tests += 1
    if test_endpoint("GET", "/notifications/"):
        passed_tests += 1
    print()
    
    # Export endpoints
    print("📤 Export API:")
    total_tests += 2
    if test_endpoint("GET", "/export/activities/csv"):
        passed_tests += 1
    if test_endpoint("GET", "/export/members/json"):
        passed_tests += 1
    print()
    
    # Summary
    print("=" * 50)
    print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("🎉 All API endpoints are working correctly!")
        print("✅ Frontend should be able to communicate with backend successfully.")
    else:
        print("⚠️  Some API endpoints have issues.")
        print("🔧 Please check the failed endpoints above.")
    
    print()
    print("🌐 Frontend URL: http://localhost:3000")
    print("📚 API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
