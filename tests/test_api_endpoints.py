#!/usr/bin/env python3
"""
API端点测试脚本
用于测试Inspector Cursor的所有API端点
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_health_endpoint():
    """测试健康检查端点"""
    print("🏥 测试健康检查端点...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过")
            print(f"   状态: {data.get('status')}")
            print(f"   时间: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False

async def test_root_endpoint():
    """测试根端点"""
    print("\n🏠 测试根端点...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/")
            
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 根端点正常")
            print(f"   消息: {data.get('message')}")
            print(f"   版本: {data.get('version')}")
            print(f"   状态: {data.get('status')}")
            return True
        else:
            print(f"❌ 根端点失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 根端点异常: {str(e)}")
        return False

async def test_monitoring_stats():
    """测试监控统计端点"""
    print("\n📊 测试监控统计端点...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/monitoring/stats")
            
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 监控统计正常")
            print(f"   总成员数: {data.get('total_members')}")
            print(f"   活跃成员数: {data.get('active_members')}")
            print(f"   总活动数: {data.get('total_activities')}")
            print(f"   今日活动: {data.get('activities_today')}")
            print(f"   本周活动: {data.get('activities_this_week')}")
            return True
        else:
            print(f"❌ 监控统计失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 监控统计异常: {str(e)}")
        return False

async def test_members_endpoints():
    """测试成员相关端点"""
    print("\n👥 测试成员端点...")
    
    try:
        async with httpx.AsyncClient() as client:
            # 获取成员列表
            response = await client.get(f"{BASE_URL}/api/v1/members/")
            
            if response.status_code == 200:
                members = response.json()
                print(f"✅ 成员列表获取成功")
                print(f"   成员数量: {len(members)}")
                
                # 创建测试成员
                test_member = {
                    "name": f"测试用户_{datetime.now().strftime('%H%M%S')}",
                    "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
                    "position": "开发工程师",
                    "is_active": True
                }
                
                create_response = await client.post(
                    f"{BASE_URL}/api/v1/members/",
                    json=test_member
                )
                
                if create_response.status_code == 201:
                    created_member = create_response.json()
                    print(f"✅ 成员创建成功")
                    print(f"   成员ID: {created_member.get('id')}")
                    print(f"   成员姓名: {created_member.get('name')}")
                    
                    # 获取单个成员
                    member_id = created_member.get('id')
                    get_response = await client.get(f"{BASE_URL}/api/v1/members/{member_id}")
                    
                    if get_response.status_code == 200:
                        member_data = get_response.json()
                        print(f"✅ 成员详情获取成功")
                        print(f"   邮箱: {member_data.get('email')}")
                        print(f"   职位: {member_data.get('position')}")
                    else:
                        print(f"❌ 成员详情获取失败: {get_response.status_code}")
                    
                    return True
                else:
                    print(f"❌ 成员创建失败: {create_response.status_code}")
                    print(f"   错误: {create_response.text}")
                    return False
            else:
                print(f"❌ 成员列表获取失败: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ 成员端点异常: {str(e)}")
        return False

async def test_activities_endpoints():
    """测试活动相关端点"""
    print("\n📈 测试活动端点...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/monitoring/activities")
            
        if response.status_code == 200:
            activities = response.json()
            print(f"✅ 活动列表获取成功")
            print(f"   活动数量: {len(activities)}")
            return True
        else:
            print(f"❌ 活动列表获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 活动端点异常: {str(e)}")
        return False

async def test_summaries_endpoints():
    """测试总结相关端点"""
    print("\n📝 测试总结端点...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/monitoring/summaries")
            
        if response.status_code == 200:
            summaries = response.json()
            print(f"✅ 总结列表获取成功")
            print(f"   总结数量: {len(summaries)}")
            return True
        else:
            print(f"❌ 总结列表获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 总结端点异常: {str(e)}")
        return False

async def test_docs_endpoint():
    """测试API文档端点"""
    print("\n📚 测试API文档端点...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/docs")
            
        if response.status_code == 200:
            print(f"✅ API文档可访问")
            print(f"   文档URL: {BASE_URL}/docs")
            return True
        else:
            print(f"❌ API文档访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API文档异常: {str(e)}")
        return False

async def main():
    """主函数"""
    print("🚀 Inspector Cursor - API端点测试")
    print("=" * 60)
    
    # 测试所有端点
    results = []
    
    results.append(("健康检查", await test_health_endpoint()))
    results.append(("根端点", await test_root_endpoint()))
    results.append(("监控统计", await test_monitoring_stats()))
    results.append(("成员管理", await test_members_endpoints()))
    results.append(("活动监控", await test_activities_endpoints()))
    results.append(("总结报告", await test_summaries_endpoints()))
    results.append(("API文档", await test_docs_endpoint()))
    
    # 显示总结
    print("\n" + "=" * 60)
    print("📋 API端点测试总结:")
    
    all_passed = True
    for name, is_passed in results:
        status = "✅ 通过" if is_passed else "❌ 失败"
        print(f"   {name}: {status}")
        if not is_passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有API端点测试通过!")
        print("💡 后端服务运行正常")
    else:
        print("⚠️  部分API端点测试失败")
        print("💡 请检查后端服务状态")
    
    print(f"\n📖 API文档: {BASE_URL}/docs")
    print(f"🔍 健康检查: {BASE_URL}/health")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main()) 