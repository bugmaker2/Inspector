#!/usr/bin/env python3
"""
测试应用启动
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有关键导入"""
    print("🔍 测试导入...")
    
    try:
        from app.core.config.settings import settings
        print("✅ 设置导入成功")
        print(f"   调试模式: {settings.debug}")
        print(f"   数据库URL: {settings.database_url}")
    except Exception as e:
        print(f"❌ 设置导入失败: {e}")
        return False
    
    try:
        from app.core.database.database import engine, Base, init_db
        print("✅ 数据库导入成功")
    except Exception as e:
        print(f"❌ 数据库导入失败: {e}")
        return False
    
    try:
        from app.models.member import Member, Activity, Summary, SocialProfile
        print("✅ 模型导入成功")
    except Exception as e:
        print(f"❌ 模型导入失败: {e}")
        return False
    
    try:
        from app.api.v1 import members, monitoring, settings as settings_api, export, notifications
        print("✅ API路由导入成功")
    except Exception as e:
        print(f"❌ API路由导入失败: {e}")
        return False
    
    try:
        from app.services.monitors.monitor_manager import MonitorManager
        from app.services.summarizers.llm_summarizer import LLMSummarizer
        print("✅ 服务导入成功")
    except Exception as e:
        print(f"❌ 服务导入失败: {e}")
        return False
    
    return True

def test_database_init():
    """测试数据库初始化"""
    print("\n🗄️ 测试数据库初始化...")
    
    try:
        from app.core.database.database import init_db
        init_db()
        print("✅ 数据库初始化成功")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def test_app_creation():
    """测试应用创建"""
    print("\n🚀 测试应用创建...")
    
    try:
        from app.main import app
        print("✅ 应用创建成功")
        print(f"   应用标题: {app.title}")
        print(f"   应用版本: {app.version}")
        return True
    except Exception as e:
        print(f"❌ 应用创建失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Inspector 启动测试")
    print("=" * 40)
    
    # 测试导入
    if not test_imports():
        print("\n❌ 导入测试失败，请检查代码")
        return False
    
    # 测试数据库初始化
    if not test_database_init():
        print("\n❌ 数据库初始化失败")
        return False
    
    # 测试应用创建
    if not test_app_creation():
        print("\n❌ 应用创建失败")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 所有测试通过！应用可以正常启动")
    print("=" * 40)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
