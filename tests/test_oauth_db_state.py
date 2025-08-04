#!/usr/bin/env python3
"""
OAuth数据库state测试脚本
"""

import asyncio
import httpx
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config.settings import settings
from app.core.database.database import SessionLocal
from app.models.oauth_state import OAuthState


async def test_oauth_db_state():
    """测试OAuth数据库state存储"""
    print("🧪 测试OAuth数据库state存储")
    print("=" * 50)
    
    base_url = f"http://localhost:{settings.api_port}"
    
    async with httpx.AsyncClient() as client:
        # 1. 测试OAuth重定向
        print("1. 测试OAuth重定向...")
        try:
            response = await client.get(
                f"{base_url}{settings.api_prefix}/auth/github", 
                follow_redirects=False,
                timeout=10.0
            )
            
            if response.status_code == 307:
                print("✅ OAuth重定向成功")
                location = response.headers.get('location', '')
                print(f"   重定向URL: {location}")
                
                # 提取state参数
                if "state=" in location:
                    state = location.split("state=")[1].split("&")[0]
                    print(f"   生成的state: {state}")
                    
                    # 2. 检查数据库中是否保存了state
                    print("\n2. 检查数据库中的state...")
                    db = SessionLocal()
                    try:
                        oauth_state = db.query(OAuthState).filter(
                            OAuthState.state == state
                        ).first()
                        
                        if oauth_state:
                            print("✅ State已保存到数据库")
                            print(f"   创建时间: {oauth_state.created_at}")
                            print(f"   过期时间: {oauth_state.expires_at}")
                            print(f"   是否过期: {oauth_state.is_expired()}")
                            
                            # 3. 测试state验证
                            print("\n3. 测试state验证...")
                            from app.services.auth import auth_service
                            
                            is_valid = auth_service.validate_state_token(db, state)
                            if is_valid:
                                print("✅ State验证成功")
                            else:
                                print("❌ State验证失败")
                            
                            # 4. 再次检查数据库中的state（应该已被删除）
                            oauth_state_after = db.query(OAuthState).filter(
                                OAuthState.state == state
                            ).first()
                            
                            if not oauth_state_after:
                                print("✅ State验证后已从数据库删除")
                            else:
                                print("❌ State验证后仍存在于数据库")
                                
                        else:
                            print("❌ State未保存到数据库")
                            
                    finally:
                        db.close()
                else:
                    print("❌ 重定向URL中未找到state参数")
                    
            else:
                print(f"❌ OAuth重定向失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ OAuth重定向异常: {e}")


async def main():
    """主测试函数"""
    print("🚀 OAuth数据库state测试")
    print("=" * 60)
    
    await test_oauth_db_state()
    
    print("\n📝 测试总结")
    print("=" * 30)
    print("这个测试验证了OAuth state的数据库存储和验证")
    print("如果所有测试都通过，说明数据库state存储工作正常")


if __name__ == "__main__":
    asyncio.run(main()) 