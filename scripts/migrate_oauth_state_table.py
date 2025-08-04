#!/usr/bin/env python3
"""
数据库迁移脚本：添加OAuth state表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config.settings import settings
from app.core.database.database import Base
from app.models.oauth_state import OAuthState

def create_oauth_state_table():
    """创建OAuth state表"""
    print("🔧 开始创建OAuth state表...")
    
    # 创建数据库引擎
    engine = create_engine(settings.database_url)
    
    try:
        # 创建表
        Base.metadata.create_all(bind=engine, tables=[OAuthState.__table__])
        
        print("✅ 成功创建以下表:")
        print("   - oauth_states (OAuth state存储表)")
        
        # 验证表是否创建成功
        with engine.connect() as conn:
            # 检查oauth_states表
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='oauth_states'"))
            if result.fetchone():
                print("✅ oauth_states表创建成功")
            else:
                print("❌ oauth_states表创建失败")
        
        print("\n🎉 OAuth state表迁移完成!")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_oauth_state_table() 