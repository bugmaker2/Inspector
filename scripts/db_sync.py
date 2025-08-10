#!/usr/bin/env python3
"""
数据库同步和状态检查脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database.database import SessionLocal, engine
from app.models.member import Member, Activity, SocialProfile, Summary
from sqlalchemy import text
import sqlite3
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_files():
    """检查数据库文件状态"""
    print("🔍 检查数据库文件...")
    
    db_files = {
        'inspector.db': '主数据库文件',
        'inspector.db-shm': '共享内存文件',
        'inspector.db-wal': '预写日志文件'
    }
    
    for filename, description in db_files.items():
        if Path(filename).exists():
            size = Path(filename).stat().st_size
            print(f"✅ {filename} ({description}) - {size} bytes")
        else:
            print(f"❌ {filename} ({description}) - 不存在")

def sync_wal_files():
    """同步 WAL 文件到主数据库"""
    print("\n🔄 同步 WAL 文件...")
    
    try:
        # 连接到数据库并执行检查点
        conn = sqlite3.connect('inspector.db')
        conn.execute('PRAGMA wal_checkpoint(FULL)')
        conn.close()
        print("✅ WAL 文件同步完成")
    except Exception as e:
        print(f"❌ WAL 同步失败: {e}")

def check_database_content():
    """检查数据库内容"""
    print("\n📊 检查数据库内容...")
    
    db = SessionLocal()
    try:
        # 检查各表的数据量
        member_count = db.query(Member).count()
        profile_count = db.query(SocialProfile).count()
        activity_count = db.query(Activity).count()
        summary_count = db.query(Summary).count()
        
        print(f"成员数量: {member_count}")
        print(f"社交配置数量: {profile_count}")
        print(f"活动数量: {activity_count}")
        print(f"总结数量: {summary_count}")
        
        # 显示成员详情
        if member_count > 0:
            print("\n📋 成员详情:")
            members = db.query(Member).all()
            for member in members:
                print(f"  - ID: {member.id}, 姓名: {member.name}, 邮箱: {member.email}")
                
                # 检查该成员的社交配置
                profiles = db.query(SocialProfile).filter(SocialProfile.member_id == member.id).all()
                if profiles:
                    print(f"    社交配置:")
                    for profile in profiles:
                        print(f"      - {profile.platform}: {profile.profile_url}")
                else:
                    print(f"    社交配置: 无")
        
    except Exception as e:
        print(f"❌ 检查数据库内容失败: {e}")
    finally:
        db.close()

def check_database_integrity():
    """检查数据库完整性"""
    print("\n🔧 检查数据库完整性...")
    
    try:
        conn = sqlite3.connect('inspector.db')
        
        # 检查数据库完整性
        result = conn.execute('PRAGMA integrity_check').fetchone()
        if result[0] == 'ok':
            print("✅ 数据库完整性检查通过")
        else:
            print(f"❌ 数据库完整性检查失败: {result[0]}")
        
        # 检查外键约束
        conn.execute('PRAGMA foreign_key_check')
        print("✅ 外键约束检查通过")
        
        conn.close()
    except Exception as e:
        print(f"❌ 数据库完整性检查失败: {e}")

def reset_database():
    """重置数据库（谨慎使用）"""
    print("\n⚠️  重置数据库...")
    
    confirm = input("这将删除所有数据！输入 'RESET' 确认: ")
    if confirm != 'RESET':
        print("操作已取消")
        return
    
    db = SessionLocal()
    try:
        # 删除所有数据
        db.query(Activity).delete()
        db.query(Summary).delete()
        db.query(SocialProfile).delete()
        db.query(Member).delete()
        
        # 重置自增ID
        try:
            db.execute(text("DELETE FROM sqlite_sequence"))
        except:
            pass
        
        db.commit()
        print("✅ 数据库重置完成")
        
    except Exception as e:
        print(f"❌ 数据库重置失败: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """主函数"""
    print("🗄️  Inspector 数据库同步工具")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "sync":
            check_database_files()
            sync_wal_files()
            check_database_content()
        elif command == "check":
            check_database_files()
            check_database_content()
            check_database_integrity()
        elif command == "reset":
            reset_database()
        else:
            print(f"未知命令: {command}")
            print("可用命令: sync, check, reset")
    else:
        # 默认执行完整检查
        check_database_files()
        sync_wal_files()
        check_database_content()
        check_database_integrity()

if __name__ == "__main__":
    main()
