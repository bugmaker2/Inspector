#!/usr/bin/env python3
"""
阿里云通义千问API测试脚本
用于验证阿里云通义千问的OpenAI兼容模式是否正常工作
"""

import asyncio
import httpx
import json
from app.core.config.settings import settings

async def test_aliyun_openai():
    """测试阿里云通义千问API"""
    print("🤖 测试阿里云通义千问API")
    print("=" * 50)
    
    # 显示当前配置
    print(f"📋 当前配置:")
    print(f"   Base URL: {settings.openai_base_url}")
    print(f"   Model: {settings.openai_model}")
    print(f"   API Key: {settings.openai_api_key[:10]}...{settings.openai_api_key[-4:]}")
    
    # 检查配置
    if not settings.openai_api_key:
        print("❌ 错误: 未配置API密钥")
        return False
    
    if "dashscope.aliyuncs.com" not in settings.openai_base_url:
        print("⚠️  警告: 当前配置不是阿里云通义千问")
        print("💡 建议使用: https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
    
    try:
        # 准备请求数据
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": settings.openai_model,
            "messages": [
                {"role": "user", "content": "请回复'阿里云通义千问API测试成功'"}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        print(f"\n🧪 发送测试请求...")
        print(f"   URL: {settings.openai_base_url}")
        print(f"   Model: {settings.openai_model}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.openai_base_url,
                headers=headers,
                json=data,
                timeout=30.0
            )
            
            print(f"\n📊 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API调用成功!")
                
                # 解析响应
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    print(f"   响应内容: {content}")
                
                # 显示使用情况
                if "usage" in result:
                    usage = result["usage"]
                    print(f"   使用情况:")
                    print(f"     输入tokens: {usage.get('prompt_tokens', 'N/A')}")
                    print(f"     输出tokens: {usage.get('completion_tokens', 'N/A')}")
                    print(f"     总tokens: {usage.get('total_tokens', 'N/A')}")
                
                return True
                
            else:
                print(f"❌ API调用失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                
                # 尝试解析错误信息
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error = error_data["error"]
                        print(f"   错误类型: {error.get('type', 'Unknown')}")
                        print(f"   错误消息: {error.get('message', 'Unknown')}")
                        print(f"   错误代码: {error.get('code', 'Unknown')}")
                except:
                    pass
                
                return False
                
    except httpx.TimeoutException:
        print("❌ 请求超时")
        print("💡 检查网络连接或增加超时时间")
        return False
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

def test_different_models():
    """测试不同的模型名称"""
    print("\n🔍 测试不同的模型名称...")
    
    # 阿里云通义千问支持的模型名称
    models = [
        "gpt-3.5-turbo",
        "qwen-turbo",
        "qwen-plus",
        "qwen-max",
        "qwen-max-longcontext"
    ]
    
    print("📋 阿里云通义千问支持的模型:")
    for i, model in enumerate(models, 1):
        print(f"   {i}. {model}")
    
    print("\n💡 建议:")
    print("   - 如果 gpt-3.5-turbo 不工作，尝试使用 qwen-turbo")
    print("   - 在.env文件中设置: OPENAI_MODEL=qwen-turbo")

def show_aliyun_help():
    """显示阿里云配置帮助"""
    print("\n📚 阿里云通义千问配置指南:")
    print("1. 访问 https://dashscope.console.aliyun.com/")
    print("2. 创建API密钥")
    print("3. 在.env文件中配置:")
    print("   OPENAI_API_KEY=你的API密钥")
    print("   OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
    print("   OPENAI_MODEL=qwen-turbo")
    print("\n💡 注意:")
    print("   - 确保API密钥有足够的余额")
    print("   - 检查模型名称是否正确")
    print("   - 确认网络连接正常")

async def main():
    """主函数"""
    success = await test_aliyun_openai()
    
    if not success:
        test_different_models()
        show_aliyun_help()
        return False
    
    print("\n🎉 阿里云通义千问API配置成功!")
    print("💡 现在可以使用AI总结功能了")
    return True

if __name__ == "__main__":
    asyncio.run(main()) 