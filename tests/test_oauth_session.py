#!/usr/bin/env python3
"""
OAuth Session测试脚本
"""

import asyncio
import httpx
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config.settings import settings


async def test_oauth_session():
    """测试OAuth session流程"""
    print("🧪 测试OAuth Session流程")
    print("=" * 50)
    
    base_url = f"http://localhost:{settings.api_port}"
    
    async with httpx.AsyncClient() as client:
        # 1. 测试OAuth重定向并保存session
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
                
                # 检查session cookie
                session_cookie = response.cookies.get('session')
                if session_cookie:
                    print(f"✅ Session cookie设置: {session_cookie[:50]}...")
                else:
                    print("❌ 未设置session cookie")
                
                # 2. 测试回调端点（模拟）
                print("\n2. 测试回调端点...")
                try:
                    # 使用相同的session cookie
                    cookies = {"session": session_cookie}
                    
                    # 模拟回调请求
                    callback_response = await client.get(
                        f"{base_url}{settings.api_prefix}/auth/github/callback?code=test_code&state=test_state",
                        cookies=cookies,
                        timeout=10.0
                    )
                    
                    print(f"   回调响应状态: {callback_response.status_code}")
                    if callback_response.status_code == 302:
                        redirect_location = callback_response.headers.get('location', '')
                        print(f"   重定向到: {redirect_location}")
                        
                        if "localhost:3000" in redirect_location:
                            print("✅ 重定向到前端页面")
                        else:
                            print("❌ 重定向URL不正确")
                    else:
                        print(f"   响应内容: {callback_response.text}")
                        
                except Exception as e:
                    print(f"❌ 回调测试异常: {e}")
                    
            else:
                print(f"❌ OAuth重定向失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ OAuth重定向异常: {e}")


async def main():
    """主测试函数"""
    print("🚀 OAuth Session测试")
    print("=" * 60)
    
    await test_oauth_session()
    
    print("\n📝 测试总结")
    print("=" * 30)
    print("这个测试验证了OAuth session的创建和传递")
    print("如果session cookie正确设置，说明session中间件工作正常")


if __name__ == "__main__":
    asyncio.run(main()) 