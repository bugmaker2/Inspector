#!/usr/bin/env python3
"""
测试社交配置创建功能
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_social_profile():
    """测试创建社交配置"""
    
    # 1. 首先创建一个成员
    member_data = {
        "name": "测试用户",
        "email": "test@example.com",
        "position": "开发工程师",
        "department": "技术部"
    }
    
    print("1. 创建成员...")
    response = requests.post(f"{BASE_URL}/api/v1/members/", json=member_data)
    if response.status_code == 201:
        member = response.json()
        member_id = member['id']
        print(f"   成员创建成功，ID: {member_id}")
    else:
        print(f"   成员创建失败: {response.status_code} - {response.text}")
        return
    
    # 2. 创建GitHub社交配置
    github_profile = {
        "platform": "github",
        "profile_url": "https://github.com/testuser",
        "username": "testuser"
    }
    
    print("2. 创建GitHub社交配置...")
    response = requests.post(f"{BASE_URL}/api/v1/members/{member_id}/social-profiles", json=github_profile)
    if response.status_code == 201:
        profile = response.json()
        print(f"   GitHub配置创建成功，ID: {profile['id']}")
    else:
        print(f"   GitHub配置创建失败: {response.status_code}")
        print(f"   错误详情: {response.text}")
        return
    
    # 3. 创建LinkedIn社交配置
    linkedin_profile = {
        "platform": "linkedin",
        "profile_url": "https://linkedin.com/in/testuser",
        "username": "testuser"
    }
    
    print("3. 创建LinkedIn社交配置...")
    response = requests.post(f"{BASE_URL}/api/v1/members/{member_id}/social-profiles", json=linkedin_profile)
    if response.status_code == 201:
        profile = response.json()
        print(f"   LinkedIn配置创建成功，ID: {profile['id']}")
    else:
        print(f"   LinkedIn配置创建失败: {response.status_code}")
        print(f"   错误详情: {response.text}")
        return
    
    # 4. 获取成员的所有社交配置
    print("4. 获取成员的所有社交配置...")
    response = requests.get(f"{BASE_URL}/api/v1/members/{member_id}/social-profiles")
    if response.status_code == 200:
        profiles = response.json()
        print(f"   找到 {len(profiles)} 个社交配置:")
        for profile in profiles:
            print(f"     - {profile['platform']}: {profile['profile_url']}")
    else:
        print(f"   获取社交配置失败: {response.status_code}")
    
    print("\n✅ 测试完成！")

if __name__ == "__main__":
    test_create_social_profile() 