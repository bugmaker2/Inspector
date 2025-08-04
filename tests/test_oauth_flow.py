#!/usr/bin/env python3
"""
OAuth流程测试脚本
"""

import asyncio
import httpx
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config.settings import settings


async def test_oauth_flow():
    """测试完整的OAuth流程"""
    print("🧪 测试OAuth流程")
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
                
                # 检查重定向URL是否包含GitHub OAuth参数
                if "github.com/login/oauth/authorize" in location:
                    print("✅ 重定向到GitHub OAuth页面")
                    
                    # 解析URL参数
                    if "client_id=" in location:
                        print("✅ 包含client_id参数")
                    else:
                        print("❌ 缺少client_id参数")
                    
                    if "redirect_uri=" in location:
                        print("✅ 包含redirect_uri参数")
                    else:
                        print("❌ 缺少redirect_uri参数")
                    
                    if "scope=" in location:
                        print("✅ 包含scope参数")
                    else:
                        print("❌ 缺少scope参数")
                    
                    if "state=" in location:
                        print("✅ 包含state参数")
                    else:
                        print("❌ 缺少state参数")
                    
                    # 检查session cookie
                    if 'session' in response.cookies:
                        print("✅ 设置了session cookie")
                    else:
                        print("❌ 未设置session cookie")
                        
                else:
                    print("❌ 重定向URL不是GitHub OAuth页面")
                    
            else:
                print(f"❌ OAuth重定向失败: {response.status_code}")
                print(f"   响应内容: {response.text}")
                
        except Exception as e:
            print(f"❌ OAuth重定向异常: {e}")
        
        # 2. 测试回调端点（模拟）
        print("\n2. 测试回调端点...")
        try:
            # 这里我们只是测试端点是否存在，不进行实际的OAuth交换
            response = await client.get(
                f"{base_url}{settings.api_prefix}/auth/github/callback?code=test&state=test",
                timeout=10.0
            )
            
            if response.status_code in [400, 500]:  # 预期的错误状态码
                print("✅ 回调端点存在（返回预期的错误）")
            else:
                print(f"⚠️  回调端点返回: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 回调端点异常: {e}")
        
        # 3. 检查配置
        print("\n3. 检查OAuth配置...")
        if settings.github_client_id:
            print(f"✅ Client ID已配置: {settings.github_client_id[:10]}...")
        else:
            print("❌ Client ID未配置")
        
        if settings.github_client_secret:
            print("✅ Client Secret已配置")
        else:
            print("❌ Client Secret未配置")
        
        print(f"✅ 重定向URI: {settings.github_redirect_uri}")
        
        # 4. 测试用户状态端点
        print("\n4. 测试用户状态端点...")
        try:
            response = await client.get(
                f"{base_url}{settings.api_prefix}/auth/users/me/github-status",
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 用户状态端点正常")
                print(f"   连接状态: {data.get('connected', 'Unknown')}")
            else:
                print(f"❌ 用户状态端点异常: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 用户状态端点异常: {e}")


async def main():
    """主测试函数"""
    print("🚀 OAuth流程测试")
    print("=" * 60)
    
    await test_oauth_flow()
    
    print("\n📝 测试总结")
    print("=" * 30)
    print("如果所有测试都通过，说明OAuth流程配置正确")
    print("下一步：")
    print("1. 在浏览器中访问 http://localhost:3000/settings")
    print("2. 点击'连接GitHub'按钮")
    print("3. 应该会跳转到GitHub OAuth页面")
    print("4. 完成授权后应该会回到应用")


if __name__ == "__main__":
    asyncio.run(main()) 