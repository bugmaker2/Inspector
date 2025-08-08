#!/usr/bin/env python3
"""
直接测试健康检查
"""

import sys
import os
import requests

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_health_direct():
    """直接测试健康检查函数"""
    try:
        from app.core.database.database import health_check
        print("调用健康检查函数...")
        result = health_check()
        print(f"结果: {result}")
        return result
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_health_via_main():
    """通过main模块测试健康检查"""
    try:
        from app.main import health_check_endpoint
        print("通过main模块调用健康检查...")
        import asyncio
        result = asyncio.run(health_check_endpoint())
        print(f"结果: {result}")
        return result
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_health_http():
    """通过HTTP测试健康检查"""
    try:
        print("通过HTTP调用健康检查...")
        response = requests.get("http://localhost:8000/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"错误: {e}")
        return None

def main():
    """主函数"""
    print("🔍 直接健康检查测试")
    print("=" * 30)
    
    # 直接测试
    print("\n1. 直接调用健康检查函数:")
    result1 = test_health_direct()
    
    print("\n2. 通过main模块调用:")
    result2 = test_health_via_main()
    
    print("\n3. 通过HTTP调用:")
    result3 = test_health_http()
    
    print("\n" + "=" * 30)
    print("测试完成")

if __name__ == "__main__":
    main()
