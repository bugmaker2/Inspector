#!/usr/bin/env python3
"""
用户创建逻辑测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database.database import SessionLocal
from app.models.user import User


def test_user_creation_logic():
    """测试用户创建逻辑"""
    print("🧪 测试用户创建逻辑")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # 测试场景1：GitHub用户有邮箱
        print("1. 测试GitHub用户有邮箱的情况...")
        github_user_info_with_email = {
            "login": "testuser1",
            "email": "testuser1@example.com"
        }
        
        github_email = github_user_info_with_email.get("email")
        if not github_email:
            github_email = f"{github_user_info_with_email['login']}@github.com"
            print(f"⚠️  GitHub用户没有公开邮箱，使用生成邮箱: {github_email}")
        else:
            print(f"✅ GitHub用户有邮箱: {github_email}")
        
        # 测试场景2：GitHub用户没有邮箱
        print("\n2. 测试GitHub用户没有邮箱的情况...")
        github_user_info_no_email = {
            "login": "testuser2"
        }
        
        github_email = github_user_info_no_email.get("email")
        if not github_email:
            github_email = f"{github_user_info_no_email['login']}@github.com"
            print(f"⚠️  GitHub用户没有公开邮箱，使用生成邮箱: {github_email}")
        else:
            print(f"✅ GitHub用户有邮箱: {github_email}")
        
        # 测试场景3：检查数据库中的用户
        print("\n3. 检查数据库中的用户...")
        users = db.query(User).all()
        print(f"   数据库中共有 {len(users)} 个用户")
        
        for user in users:
            print(f"   用户: {user.username} ({user.email})")
        
        print("\n✅ 用户创建逻辑测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    test_user_creation_logic() 