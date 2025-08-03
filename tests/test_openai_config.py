#!/usr/bin/env python3
"""
测试OpenAI配置的脚本
用于验证base URL和API密钥配置是否正确
"""

import os
import sys
from openai import OpenAI
from app.core.config.settings import settings

def test_openai_config():
    """测试OpenAI配置"""
    print("🔧 测试OpenAI配置...")
    
    # 显示当前配置
    print(f"📋 当前配置:")
    print(f"   API Key: {'已配置' if settings.openai_api_key else '未配置'}")
    print(f"   Base URL: {settings.openai_base_url}")
    print(f"   Model: {settings.openai_model}")
    
    if not settings.openai_api_key:
        print("❌ 错误: 未配置OpenAI API密钥")
        print("请在.env文件中设置OPENAI_API_KEY")
        return False
    
    try:
        # 创建OpenAI客户端
        client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        
        print(f"✅ OpenAI客户端创建成功")
        print(f"   使用Base URL: {settings.openai_base_url}")
        
        # 测试API连接
        print("\n🧪 测试API连接...")
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "user", "content": "Hello! Please respond with 'API test successful' in Chinese."}
            ],
            max_tokens=50
        )
        
        print(f"✅ API连接测试成功!")
        print(f"   响应: {response.choices[0].message.content}")
        print(f"   使用模型: {settings.openai_model}")
        
        return True
        
    except Exception as e:
        print(f"❌ API连接测试失败: {str(e)}")
        print("\n💡 可能的解决方案:")
        print("1. 检查API密钥是否正确")
        print("2. 检查Base URL是否正确")
        print("3. 检查网络连接")
        print("4. 检查API配额是否充足")
        return False

def show_usage_examples():
    """显示使用示例"""
    print("\n📚 使用示例:")
    print("\n1. 使用OpenAI官方API:")
    print("   OPENAI_API_KEY=sk-...")
    print("   OPENAI_BASE_URL=https://api.openai.com/v1")
    print("   OPENAI_MODEL=gpt-3.5-turbo")
    
    print("\n2. 使用Azure OpenAI:")
    print("   OPENAI_API_KEY=your-azure-api-key")
    print("   OPENAI_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment")
    print("   OPENAI_MODEL=gpt-35-turbo")
    
    print("\n3. 使用其他兼容平台:")
    print("   OPENAI_API_KEY=your-api-key")
    print("   OPENAI_BASE_URL=https://api.your-platform.com/v1")
    print("   OPENAI_MODEL=gpt-3.5-turbo")

def main():
    """主函数"""
    print("🚀 Inspector - OpenAI配置测试")
    print("=" * 50)
    
    # 测试配置
    success = test_openai_config()
    
    if not success:
        show_usage_examples()
        sys.exit(1)
    
    print("\n🎉 配置测试完成! 系统可以正常使用AI总结功能。")

if __name__ == "__main__":
    main() 