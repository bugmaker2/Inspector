#!/usr/bin/env python3
"""
数据库迁移脚本：添加OAuth相关表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config.settings import settings
from app.core.database.database import Base
from app.models.user import User, GitHubOAuthConfig

def create_oauth_tables():
    """创建OAuth相关的数据库表"""
    print("🔧 开始创建OAuth相关表...")
    
    # 创建数据库引擎
    engine = create_engine(settings.database_url)
    
    try:
        # 创建表
        Base.metadata.create_all(bind=engine, tables=[User.__table__, GitHubOAuthConfig.__table__])
        
        print("✅ 成功创建以下表:")
        print("   - users (用户表)")
        print("   - github_oauth_configs (GitHub OAuth配置表)")
        
        # 验证表是否创建成功
        with engine.connect() as conn:
            # 检查users表
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'"))
            if result.fetchone():
                print("✅ users表创建成功")
            else:
                print("❌ users表创建失败")
            
            # 检查github_oauth_configs表
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='github_oauth_configs'"))
            if result.fetchone():
                print("✅ github_oauth_configs表创建成功")
            else:
                print("❌ github_oauth_configs表创建失败")
        
        print("\n🎉 OAuth表迁移完成!")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_oauth_tables() 