#!/usr/bin/env python3
"""
快速数据库清理脚本
无需确认直接清理所有数据
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database.database import SessionLocal
from app.models.member import Member, Activity, SocialProfile, Summary
from app.models.user import User
from sqlalchemy import text

def quick_clean():
    """快速清理数据库"""
    db = SessionLocal()
    
    try:
        print("🧹 快速清理数据库...")
        
        # 删除所有数据
        db.query(Activity).delete()
        db.query(Summary).delete()
        db.query(SocialProfile).delete()
        db.query(Member).delete()
        db.query(User).delete()
        
        # 重置自增ID (如果存在 sqlite_sequence 表)
        try:
            db.execute(text("DELETE FROM sqlite_sequence"))
        except:
            # 如果 sqlite_sequence 表不存在，忽略错误
            pass
        
        # 提交更改
        db.commit()
        
        print("✅ 数据库清理完成！")
        
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    quick_clean()
