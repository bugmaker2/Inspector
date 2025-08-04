#!/usr/bin/env python3
"""
GitHub OAuth 功能测试脚本
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.auth import auth_service
from app.core.config.settings import settings


async def test_oauth_configuration():
    """测试OAuth配置"""
    print("🔧 测试GitHub OAuth配置")
    print("=" * 50)
    
    # 检查配置
    if not settings.github_client_id:
        print("❌ 未配置 GITHUB_CLIENT_ID")
        return False
    
    if not settings.github_client_secret:
        print("❌ 未配置 GITHUB_CLIENT_SECRET")
        return False
    
    print(f"✅ Client ID: {settings.github_client_id[:10]}...")
    print(f"✅ Client Secret: {'*' * len(settings.github_client_secret)}")
    print(f"✅ Redirect URI: {settings.github_redirect_uri}")
    
    return True


def test_encryption():
    """测试token加密功能"""
    print("\n🔐 测试Token加密功能")
    print("=" * 30)
    
    test_token = "ghp_test_token_12345"
    
    try:
        # 加密
        encrypted = auth_service.encrypt_token(test_token)
        print(f"✅ Token加密成功: {encrypted[:20]}...")
        
        # 解密
        decrypted = auth_service.decrypt_token(encrypted)
        print(f"✅ Token解密成功: {decrypted}")
        
        # 验证
        if decrypted == test_token:
            print("✅ 加密/解密验证通过")
            return True
        else:
            print("❌ 加密/解密验证失败")
            return False
            
    except Exception as e:
        print(f"❌ 加密测试失败: {e}")
        return False


def test_state_generation():
    """测试state token生成"""
    print("\n🎲 测试State Token生成")
    print("=" * 25)
    
    try:
        state1 = auth_service.generate_state_token()
        state2 = auth_service.generate_state_token()
        
        print(f"✅ State 1: {state1}")
        print(f"✅ State 2: {state2}")
        
        if state1 != state2 and len(state1) > 20:
            print("✅ State Token生成正常")
            return True
        else:
            print("❌ State Token生成异常")
            return False
            
    except Exception as e:
        print(f"❌ State Token测试失败: {e}")
        return False


def test_oauth_url_generation():
    """测试OAuth URL生成"""
    print("\n🔗 测试OAuth URL生成")
    print("=" * 25)
    
    try:
        state = auth_service.generate_state_token()
        oauth_url = auth_service.get_github_oauth_url(state)
        
        print(f"✅ OAuth URL: {oauth_url}")
        
        # 验证URL格式
        if "github.com/login/oauth/authorize" in oauth_url:
            print("✅ OAuth URL格式正确")
            return True
        else:
            print("❌ OAuth URL格式错误")
            return False
            
    except Exception as e:
        print(f"❌ OAuth URL测试失败: {e}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("🧪 GitHub OAuth 功能测试")
    print("=" * 50)
    
    tests = [
        ("OAuth配置", test_oauth_configuration()),
        ("Token加密", test_encryption()),
        ("State生成", test_state_generation()),
        ("OAuth URL", test_oauth_url_generation()),
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出结果
    print("\n📊 测试结果汇总")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过!")
        return True
    else:
        print("⚠️  部分测试失败，请检查配置")
        return False


if __name__ == "__main__":
    asyncio.run(run_all_tests()) 