#!/usr/bin/env python3
"""
测试基于时间范围的监控
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.monitors.github_monitor import GitHubMonitor
from app.core.database.database import SessionLocal
from app.models.member import SocialProfile

async def test_time_based_monitoring():
    """测试不同时间范围的监控效果"""
    db = SessionLocal()
    
    try:
        # 创建测试用的 GitHub 监控器
        monitor = GitHubMonitor(db)
        
        # 创建测试用的社交配置
        test_profile = SocialProfile(
            id=999,  # 临时ID
            member_id=1,
            platform="github",
            profile_url="https://github.com/bugmaker2",
            username="bugmaker2",
            is_active=True
        )
        
        print("🔍 测试基于时间范围的 GitHub 监控")
        print("=" * 50)
        
        # 测试不同的时间范围
        time_ranges = [1, 6, 12, 24, 48, 168]  # 1小时到1周
        
        for hours in time_ranges:
            print(f"\n⏰ 测试 {hours} 小时时间范围:")
            print("-" * 30)
            
            # 模拟获取活动
            activities = await monitor.fetch_activities(test_profile)
            
            # 手动调用时间范围解析
            import httpx
            headers = {}
            from app.core.config.settings import settings
            if settings.github_token:
                headers["Authorization"] = f"token {settings.github_token}"
            
            async with httpx.AsyncClient() as client:
                events_url = f"https://api.github.com/users/bugmaker2/events"
                response = await client.get(events_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    events = response.json()
                    # 使用不同的时间范围
                    activities = monitor._parse_github_events(events, "bugmaker2", time_range_hours=hours)
                    print(f"   找到 {len(activities)} 个活动")
                    
                    if activities:
                        print(f"   最新活动: {activities[0]['title']}")
                        print(f"   活动时间: {activities[0]['published_at']}")
                else:
                    print(f"   ❌ API 请求失败: {response.status_code}")
            
            # 等待一下避免 API 限制
            await asyncio.sleep(1)
        
        print("\n✅ 时间范围监控测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_time_based_monitoring())
