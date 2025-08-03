#!/usr/bin/env python3
"""
快速测试社交配置修复效果
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """测试服务健康状态"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return False

def test_social_profile_creation():
    """测试社交配置创建"""
    print("\n🧪 测试社交配置创建...")
    
    # 1. 创建测试成员
    import time
    timestamp = int(time.time())
    member_data = {
        "name": "测试用户",
        "email": f"test{timestamp}@example.com",
        "position": "开发工程师"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/members/", json=member_data, timeout=10)
        if response.status_code == 201:
            member = response.json()
            member_id = member['id']
            print(f"✅ 成员创建成功，ID: {member_id}")
        else:
            print(f"❌ 成员创建失败: {response.status_code}")
            print(f"   错误详情: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 成员创建异常: {e}")
        return False
    
    # 2. 创建GitHub配置
    github_profile = {
        "platform": "github",
        "profile_url": "https://github.com/testuser",
        "username": "testuser"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/members/{member_id}/social-profiles", 
            json=github_profile, 
            timeout=10
        )
        if response.status_code == 201:
            profile = response.json()
            print(f"✅ GitHub配置创建成功，ID: {profile['id']}")
            print(f"   平台: {profile['platform']}")
            print(f"   URL: {profile['profile_url']}")
            return True
        else:
            print(f"❌ GitHub配置创建失败: {response.status_code}")
            print(f"   错误详情: {response.text}")
            return False
    except Exception as e:
        print(f"❌ GitHub配置创建异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🔧 Inspector 社交配置修复验证")
    print("=" * 50)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(2)
    
    # 测试健康状态
    if not test_health():
        print("\n💡 请确保后端服务正在运行:")
        print("   uv run python main.py")
        return
    
    # 测试社交配置创建
    if test_social_profile_creation():
        print("\n🎉 修复验证成功！")
        print("✅ 社交配置创建功能正常工作")
        print("\n💡 现在可以在前端界面正常添加社交配置了")
    else:
        print("\n❌ 修复验证失败")
        print("💡 请检查后端日志获取更多信息")

if __name__ == "__main__":
    main() 