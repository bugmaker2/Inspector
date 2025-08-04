#!/usr/bin/env python3
"""
OAuth端点测试脚本
"""

import asyncio
import httpx
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config.settings import settings


async def test_oauth_endpoints():
    """测试OAuth相关端点"""
    print("🧪 测试OAuth端点")
    print("=" * 50)
    
    base_url = f"http://localhost:{settings.api_port}"
    
    async with httpx.AsyncClient() as client:
        # 测试健康检查
        print("1. 测试健康检查...")
        try:
            response = await client.get(f"{base_url}/health", timeout=10.0)
            if response.status_code == 200:
                print("✅ 健康检查通过")
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
        
        # 测试GitHub OAuth重定向
        print("\n2. 测试GitHub OAuth重定向...")
        try:
            response = await client.get(f"{base_url}{settings.api_prefix}/auth/github", follow_redirects=False, timeout=10.0)
            if response.status_code == 307:  # 临时重定向
                print("✅ OAuth重定向正常")
                print(f"   重定向到: {response.headers.get('location', 'Unknown')}")
            else:
                print(f"❌ OAuth重定向异常: {response.status_code}")
        except Exception as e:
            print(f"❌ OAuth重定向异常: {e}")
        
        # 测试GitHub状态端点
        print("\n3. 测试GitHub状态端点...")
        try:
            response = await client.get(f"{base_url}{settings.api_prefix}/auth/users/me/github-status", timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                print("✅ GitHub状态端点正常")
                print(f"   连接状态: {data.get('connected', 'Unknown')}")
            else:
                print(f"❌ GitHub状态端点异常: {response.status_code}")
        except Exception as e:
            print(f"❌ GitHub状态端点异常: {e}")
        
        # 测试GitHub配置
        print("\n4. 检查GitHub OAuth配置...")
        if settings.github_client_id:
            print(f"✅ Client ID已配置: {settings.github_client_id[:10]}...")
        else:
            print("⚠️  Client ID未配置")
        
        if settings.github_client_secret:
            print("✅ Client Secret已配置")
        else:
            print("⚠️  Client Secret未配置")
        
        print(f"✅ 重定向URI: {settings.github_redirect_uri}")
    
    return True


async def test_frontend_connection():
    """测试前端连接"""
    print("\n🌐 测试前端连接")
    print("=" * 30)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3000")
            if response.status_code == 200:
                print("✅ 前端服务器正常")
                return True
            else:
                print(f"❌ 前端服务器异常: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 前端连接失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 OAuth端点测试")
    print("=" * 60)
    
    # 测试后端端点
    backend_ok = await test_oauth_endpoints()
    
    # 测试前端连接
    frontend_ok = await test_frontend_connection()
    
    # 总结
    print("\n📊 测试总结")
    print("=" * 30)
    print(f"后端端点: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"前端连接: {'✅ 正常' if frontend_ok else '❌ 异常'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 所有测试通过！")
        print("\n📝 下一步:")
        print("1. 访问 http://localhost:3000/settings")
        print("2. 配置GitHub OAuth应用")
        print("3. 测试GitHub连接功能")
    else:
        print("\n⚠️  部分测试失败，请检查配置")


if __name__ == "__main__":
    asyncio.run(main()) 