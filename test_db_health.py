#!/usr/bin/env python3
"""
测试数据库健康检查
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_db_health():
    """测试数据库健康检查"""
    try:
        from app.core.database.database import health_check
        result = health_check()
        print("数据库健康检查结果:")
        print(f"状态: {result['status']}")
        if 'pool_stats' in result:
            print(f"连接池统计: {result['pool_stats']}")
        if 'error' in result:
            print(f"错误: {result['error']}")
        return result['status'] == 'healthy'
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_db_connection():
    """测试数据库连接"""
    try:
        from app.core.database.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("数据库连接测试成功")
            return True
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🗄️ 数据库健康检查测试")
    print("=" * 30)
    
    # 测试数据库连接
    if test_db_connection():
        print("✅ 数据库连接正常")
    else:
        print("❌ 数据库连接失败")
        return False
    
    # 测试健康检查
    if test_db_health():
        print("✅ 数据库健康检查通过")
    else:
        print("❌ 数据库健康检查失败")
        return False
    
    print("\n🎉 所有测试通过！")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
