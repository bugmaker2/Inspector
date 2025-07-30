#!/usr/bin/env python3
"""
GitHub Token 测试脚本
用于验证GitHub Personal Access Token是否有效
"""

import asyncio
import httpx
from app.core.config.settings import settings

async def test_github_token():
    """测试GitHub Token"""
    print("🔑 测试GitHub Personal Access Token")
    print("=" * 50)
    
    # 检查Token是否配置
    if not settings.github_token:
        print("❌ 错误: 未配置GitHub Token")
        print("💡 请在.env文件中设置GITHUB_TOKEN")
        return False
    
    # 检查是否是示例Token
    if settings.github_token in ["your-github-personal-access-token", "SECRET_KEY", ""]:
        print("❌ 错误: 使用的是示例Token")
        print("💡 请参考 GITHUB_SETUP.md 创建真实的GitHub Token")
        return False
    
    print(f"📋 Token: {settings.github_token[:10]}...{settings.github_token[-4:]}")
    
    try:
        headers = {
            "Authorization": f"token {settings.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            # 测试用户信息API
            print("\n🧪 测试用户信息API...")
            response = await client.get(
                "https://api.github.com/user",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ 用户信息获取成功!")
                print(f"   用户名: {user_data.get('login', 'Unknown')}")
                print(f"   姓名: {user_data.get('name', 'Unknown')}")
                print(f"   邮箱: {user_data.get('email', 'Unknown')}")
                print(f"   仓库数: {user_data.get('public_repos', 0)}")
                
                # 测试速率限制信息
                print("\n📊 检查API速率限制...")
                rate_limit = response.headers.get('x-ratelimit-remaining', 'Unknown')
                rate_limit_reset = response.headers.get('x-ratelimit-reset', 'Unknown')
                print(f"   剩余请求数: {rate_limit}")
                print(f"   重置时间: {rate_limit_reset}")
                
                # 测试仓库访问权限
                print("\n📁 测试仓库访问权限...")
                repos_response = await client.get(
                    "https://api.github.com/user/repos?per_page=1",
                    headers=headers,
                    timeout=10.0
                )
                
                if repos_response.status_code == 200:
                    print("✅ 仓库访问权限正常")
                else:
                    print(f"⚠️  仓库访问受限: {repos_response.status_code}")
                
                return True
                
            else:
                print(f"❌ API请求失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                
                if response.status_code == 401:
                    print("\n💡 可能的原因:")
                    print("   - Token无效或已过期")
                    print("   - Token格式错误")
                    print("   - Token权限不足")
                elif response.status_code == 403:
                    print("\n💡 可能的原因:")
                    print("   - API速率限制")
                    print("   - Token权限不足")
                    print("   - 账户被限制")
                
                return False
                
    except httpx.TimeoutException:
        print("❌ 请求超时")
        print("💡 检查网络连接")
        return False
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

def show_token_help():
    """显示Token帮助信息"""
    print("\n📚 GitHub Token 创建指南:")
    print("1. 访问 https://github.com/settings/tokens")
    print("2. 点击 'Generate new token (classic)'")
    print("3. 选择权限: repo, read:user, read:org")
    print("4. 复制生成的Token")
    print("5. 在.env文件中设置: GITHUB_TOKEN=你的Token")
    print("\n详细指南请查看: GITHUB_SETUP.md")

async def main():
    """主函数"""
    success = await test_github_token()
    
    if not success:
        show_token_help()
        return False
    
    print("\n🎉 GitHub Token 配置成功!")
    print("💡 现在可以监控GitHub活动了")
    return True

if __name__ == "__main__":
    asyncio.run(main()) 