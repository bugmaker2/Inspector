#!/usr/bin/env python3
"""
数据库清理脚本
清空所有表的数据但保留数据库结构
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database.database import SessionLocal, engine
from app.models.member import Member, Activity, SocialProfile, Summary
from app.models.user import User
from sqlalchemy import text
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_database():
    """清空数据库中的所有数据"""
    db = SessionLocal()
    
    try:
        logger.info("开始清理数据库...")
        
        # 获取当前数据统计
        member_count = db.query(Member).count()
        profile_count = db.query(SocialProfile).count()
        activity_count = db.query(Activity).count()
        summary_count = db.query(Summary).count()
        user_count = db.query(User).count()
        
        logger.info(f"当前数据统计:")
        logger.info(f"  - 成员: {member_count}")
        logger.info(f"  - 社交配置: {profile_count}")
        logger.info(f"  - 活动: {activity_count}")
        logger.info(f"  - 总结: {summary_count}")
        logger.info(f"  - 用户: {user_count}")
        
        # 确认操作
        confirm = input("\n⚠️  警告：这将删除所有数据！输入 'YES' 确认继续: ")
        if confirm != 'YES':
            logger.info("操作已取消")
            return
        
        # 按依赖关系顺序删除数据
        logger.info("正在删除活动数据...")
        db.query(Activity).delete()
        
        logger.info("正在删除总结数据...")
        db.query(Summary).delete()
        
        logger.info("正在删除社交配置数据...")
        db.query(SocialProfile).delete()
        
        logger.info("正在删除成员数据...")
        db.query(Member).delete()
        
        logger.info("正在删除用户数据...")
        db.query(User).delete()
        
        # 提交更改
        db.commit()
        
        # 验证清理结果
        member_count_after = db.query(Member).count()
        profile_count_after = db.query(SocialProfile).count()
        activity_count_after = db.query(Activity).count()
        summary_count_after = db.query(Summary).count()
        user_count_after = db.query(User).count()
        
        logger.info("✅ 数据库清理完成！")
        logger.info(f"清理后数据统计:")
        logger.info(f"  - 成员: {member_count_after}")
        logger.info(f"  - 社交配置: {profile_count_after}")
        logger.info(f"  - 活动: {activity_count_after}")
        logger.info(f"  - 总结: {summary_count_after}")
        logger.info(f"  - 用户: {user_count_after}")
        
    except Exception as e:
        logger.error(f"清理数据库时出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def reset_auto_increment():
    """重置自增ID计数器"""
    db = SessionLocal()
    
    try:
        logger.info("正在重置自增ID计数器...")
        
        # SQLite 重置自增ID
        db.execute(text("DELETE FROM sqlite_sequence"))
        db.commit()
        
        logger.info("✅ 自增ID计数器已重置")
        
    except Exception as e:
        logger.error(f"重置自增ID时出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """主函数"""
    print("🧹 Inspector 数据库清理工具")
    print("=" * 50)
    
    try:
        clean_database()
        reset_auto_increment()
        
        print("\n🎉 数据库清理完成！")
        print("现在您可以重新配置成员和监控设置。")
        
    except Exception as e:
        logger.error(f"清理失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
