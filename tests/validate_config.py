#!/usr/bin/env python3
"""
配置验证脚本
真正测试所有配置项是否有效工作
"""

import os
import sys
import argparse
from sqlalchemy import create_engine, text
from openai import OpenAI
import httpx
from app.core.config.settings import settings

def test_database_connection():
    """测试数据库连接"""
    print("🗄️  测试数据库连接...")
    
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print(f"✅ 数据库连接成功: {settings.database_url}")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

async def test_openai_connection():
    """测试OpenAI连接"""
    print("\n🤖 测试OpenAI连接...")
    
    if not settings.openai_api_key:
        print("⚠️  警告: 未配置OpenAI API密钥 (AI总结功能将不可用)")
        return False
    
    # 检查是否是示例密钥
    if settings.openai_api_key in ["your-openai-api-key-here", "sk-your-openai-api-key", "SECRET_KEY", ""]:
        print("⚠️  警告: 使用的是示例API密钥或未配置，跳过连接测试")
        print("💡 提示: 请在.env文件中配置真实的OpenAI API密钥")
        return False
    
    try:
        # 检查是否是阿里云通义千问
        if "dashscope.aliyuncs.com" in settings.openai_base_url:
            # 使用HTTP请求测试阿里云API
            headers = {
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": settings.openai_model,
                "messages": [
                    {"role": "user", "content": "请回复'连接测试成功'"}
                ],
                "max_tokens": 20
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.openai_base_url,
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    print(f"✅ 阿里云通义千问连接成功!")
                    print(f"   使用模型: {settings.openai_model}")
                    print(f"   响应: {content}")
                    return True
                else:
                    print(f"❌ 阿里云API连接失败: {response.status_code}")
                    print(f"   错误信息: {response.text}")
                    return False
        else:
            # 使用OpenAI官方库测试
            client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )
            
            # 测试API连接
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "user", "content": "请回复'连接测试成功'"}
                ],
                max_tokens=20
            )
            
            print(f"✅ OpenAI连接成功!")
            print(f"   使用模型: {settings.openai_model}")
            print(f"   响应: {response.choices[0].message.content}")
            return True
        
    except Exception as e:
        print(f"❌ OpenAI连接失败: {str(e)}")
        print("💡 可能的原因:")
        print("   - API密钥错误")
        print("   - Base URL不正确")
        print("   - 网络连接问题")
        print("   - API配额不足")
        return False

async def test_github_api():
    """测试GitHub API"""
    print("\n🐙 测试GitHub API...")
    
    if not settings.github_token:
        print("⚠️  警告: 未配置GitHub Token (GitHub监控功能将不可用)")
        return False
    
    # 检查是否是示例Token
    if settings.github_token in ["your-github-personal-access-token", "SECRET_KEY", ""]:
        print("⚠️  警告: 使用的是示例GitHub Token或未配置，跳过连接测试")
        print("💡 提示: 请在.env文件中配置真实的GitHub Token")
        return False
    
    try:
        headers = {
            "Authorization": f"token {settings.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers=headers,
                timeout=10.0
            )
            
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ GitHub API连接成功!")
            print(f"   用户: {user_data.get('login', 'Unknown')}")
            return True
        else:
            print(f"❌ GitHub API连接失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ GitHub API连接失败: {str(e)}")
        return False

async def test_api_endpoints():
    """测试API端点"""
    print("\n🌐 测试API端点...")
    
    try:
        # 使用localhost而不是0.0.0.0进行本地测试
        base_url = f"http://localhost:{settings.api_port}"
        
        async with httpx.AsyncClient() as client:
            # 测试健康检查端点
            response = await client.get(f"{base_url}/health", timeout=5.0)
            
        if response.status_code == 200:
            print(f"✅ API端点可访问: {base_url}")
            print(f"   健康检查: ✅")
            return True
        else:
            print(f"⚠️  API端点响应异常: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API端点不可访问: {str(e)}")
        print("💡 可能的原因:")
        print("   - 后端服务未启动")
        print("   - 端口被占用")
        print("   - 防火墙阻止")
        print("💡 提示: 运行 'uv run python main.py' 启动后端服务")
        return False

def test_email_config():
    """测试邮件配置"""
    print("\n📧 测试邮件配置...")
    
    if not settings.email_enabled:
        print("ℹ️  邮件通知: 已禁用")
        return True
    
    if not all([settings.email_smtp_server, settings.email_username, settings.email_password]):
        print("❌ 邮件通知已启用但配置不完整")
        return False
    
    # 检查是否是示例配置
    if any([
        settings.email_username in ["your-email@gmail.com"],
        settings.email_password in ["your-app-password"]
    ]):
        print("⚠️  警告: 使用的是示例邮件配置，跳过连接测试")
        print("💡 提示: 请在.env文件中配置真实的邮件信息")
        return False
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        # 创建测试邮件
        msg = MIMEText("这是一封测试邮件")
        msg['Subject'] = "Inspector 配置测试"
        msg['From'] = settings.email_username
        msg['To'] = settings.email_recipients_list[0] if settings.email_recipients_list else settings.email_username
        
        # 测试SMTP连接
        with smtplib.SMTP(settings.email_smtp_server, settings.email_smtp_port) as server:
            server.starttls()
            server.login(settings.email_username, settings.email_password)
            print(f"✅ SMTP连接成功: {settings.email_smtp_server}")
            return True
            
    except Exception as e:
        print(f"❌ 邮件配置测试失败: {str(e)}")
        return False

def check_file_permissions():
    """检查文件权限"""
    print("\n📁 检查文件权限...")
    
    issues = []
    
    # 检查日志目录
    if settings.log_file:
        log_dir = os.path.dirname(settings.log_file)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
                print(f"✅ 创建日志目录: {log_dir}")
            except Exception as e:
                issues.append(f"无法创建日志目录: {str(e)}")
    
    # 检查数据库文件权限
    if settings.database_url.startswith("sqlite:///"):
        db_path = settings.database_url.replace("sqlite:///", "")
        if os.path.exists(db_path):
            if not os.access(db_path, os.R_OK | os.W_OK):
                issues.append(f"数据库文件权限不足: {db_path}")
            else:
                print(f"✅ 数据库文件权限正常: {db_path}")
    
    if not issues:
        print("✅ 文件权限检查通过")
        return True
    else:
        for issue in issues:
            print(f"❌ {issue}")
        return False

def check_config_values():
    """检查配置值"""
    print("\n⚙️  检查配置值...")
    
    issues = []
    
    # 检查关键配置
    if settings.secret_key == "your-secret-key-change-in-production":
        issues.append("使用默认密钥，建议在生产环境中更改")
    
    if settings.database_url == "sqlite:///./inspector.db":
        print("ℹ️  使用SQLite数据库 (开发环境)")
    
    if settings.api_host == "0.0.0.0":
        print("ℹ️  API监听所有网络接口")
    
    if not issues:
        print("✅ 配置值检查通过")
        return True
    else:
        for issue in issues:
            print(f"⚠️  {issue}")
        return True  # 配置问题不影响启动

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Inspector 配置验证工具")
    parser.add_argument("--skip-api", action="store_true", help="跳过API端点测试")
    parser.add_argument("--skip-external", action="store_true", help="跳过外部服务测试(OpenAI, GitHub)")
    args = parser.parse_args()
    
    print("🔍 Inspector - 配置有效性验证")
    print("=" * 60)
    
    # 检查.env文件是否存在
    if not os.path.exists('.env'):
        print("⚠️  警告: 未找到.env文件，使用默认配置")
    
    # 执行各项测试
    results = []
    
    # 基础测试
    results.append(("数据库连接", test_database_connection()))
    results.append(("文件权限", check_file_permissions()))
    results.append(("配置值", check_config_values()))
    
    # 外部服务测试
    if not args.skip_external:
        results.append(("OpenAI连接", await test_openai_connection()))
        results.append(("GitHub API", await test_github_api()))
    
    # API端点测试
    if not args.skip_api:
        results.append(("API端点", await test_api_endpoints()))
    
    # 邮件测试
    results.append(("邮件配置", test_email_config()))
    
    # 显示总结
    print("\n" + "=" * 60)
    print("📋 配置验证总结:")
    
    all_valid = True
    for name, is_valid in results:
        status = "✅ 通过" if is_valid else "❌ 失败"
        print(f"   {name}: {status}")
        if not is_valid:
            all_valid = False
    
    print("\n" + "=" * 60)
    if all_valid:
        print("🎉 所有配置验证通过! 系统可以正常启动。")
        print("💡 提示: 运行 'uv run python main.py' 启动后端服务")
    else:
        print("⚠️  发现配置问题，请根据上述错误信息进行修复。")
        print("💡 提示:")
        print("   - 检查.env文件中的配置")
        print("   - 确保网络连接正常")
        print("   - 验证API密钥和Token的有效性")
        print("   - 使用 --skip-api 跳过API端点测试")
        print("   - 使用 --skip-external 跳过外部服务测试")
        sys.exit(1)
    
    return all_valid

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 