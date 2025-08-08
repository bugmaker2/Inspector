#!/usr/bin/env python3
"""
测试新实现的改进功能
"""

import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_health_check():
    """测试健康检查功能"""
    print("🔍 测试健康检查功能...")
    
    # 基础健康检查
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 基础健康检查通过: {data['status']}")
        print(f"   数据库状态: {data['database']['status']}")
        print(f"   连接池统计: {data['database']['pool_stats']}")
    else:
        print(f"❌ 基础健康检查失败: {response.status_code}")
    
    # 详细健康检查
    response = requests.get(f"{BASE_URL}/health/detailed")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 详细健康检查通过: {data['status']}")
        print(f"   组件状态: {data['components']}")
    else:
        print(f"❌ 详细健康检查失败: {response.status_code}")

def test_export_functions():
    """测试数据导出功能"""
    print("\n📊 测试数据导出功能...")
    
    # 测试CSV导出
    response = requests.get(f"{API_BASE}/export/activities/csv")
    if response.status_code == 200:
        print("✅ CSV导出功能正常")
        print(f"   文件大小: {len(response.content)} bytes")
    else:
        print(f"❌ CSV导出失败: {response.status_code}")
    
    # 测试Excel导出
    response = requests.get(f"{API_BASE}/export/activities/excel")
    if response.status_code == 200:
        print("✅ Excel导出功能正常")
        print(f"   文件大小: {len(response.content)} bytes")
    else:
        print(f"❌ Excel导出失败: {response.status_code}")
    
    # 测试PDF导出
    response = requests.get(f"{API_BASE}/export/summaries/pdf")
    if response.status_code == 200:
        print("✅ PDF导出功能正常")
        print(f"   文件大小: {len(response.content)} bytes")
    else:
        print(f"❌ PDF导出失败: {response.status_code}")
    
    # 测试JSON导出
    response = requests.get(f"{API_BASE}/export/members/json")
    if response.status_code == 200:
        print("✅ JSON导出功能正常")
        data = response.json()
        print(f"   导出成员数: {len(data)}")
    else:
        print(f"❌ JSON导出失败: {response.status_code}")

def test_notification_system():
    """测试通知系统"""
    print("\n🔔 测试通知系统...")
    
    # 创建测试通知
    notification_data = {
        "title": "测试通知",
        "message": "这是一个测试通知",
        "type": "info",
        "data": {"test": True}
    }
    
    response = requests.post(f"{API_BASE}/notifications/", json=notification_data)
    if response.status_code == 200:
        print("✅ 通知创建成功")
        notification = response.json()
        print(f"   通知ID: {notification['id']}")
        print(f"   通知标题: {notification['title']}")
    else:
        print(f"❌ 通知创建失败: {response.status_code}")
    
    # 获取通知列表
    response = requests.get(f"{API_BASE}/notifications/")
    if response.status_code == 200:
        notifications = response.json()
        print(f"✅ 获取通知列表成功，共 {len(notifications)} 条通知")
    else:
        print(f"❌ 获取通知列表失败: {response.status_code}")

def test_database_performance():
    """测试数据库性能"""
    print("\n🗄️ 测试数据库性能...")
    
    # 测试连接池状态
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        pool_stats = data['database']['pool_stats']
        print(f"✅ 连接池状态:")
        print(f"   连接池大小: {pool_stats['pool_size']}")
        print(f"   已连接: {pool_stats['checked_in']}")
        print(f"   使用中: {pool_stats['checked_out']}")
        print(f"   溢出连接: {pool_stats['overflow']}")
    else:
        print(f"❌ 无法获取连接池状态: {response.status_code}")

def test_api_performance():
    """测试API性能"""
    print("\n⚡ 测试API性能...")
    
    # 测试成员API响应时间
    start_time = time.time()
    response = requests.get(f"{API_BASE}/members/")
    end_time = time.time()
    
    if response.status_code == 200:
        response_time = (end_time - start_time) * 1000  # 转换为毫秒
        print(f"✅ 成员API响应时间: {response_time:.2f}ms")
        
        if response_time < 200:
            print("   🚀 性能优秀 (< 200ms)")
        elif response_time < 500:
            print("   ✅ 性能良好 (< 500ms)")
        else:
            print("   ⚠️ 性能需要优化 (> 500ms)")
    else:
        print(f"❌ 成员API测试失败: {response.status_code}")
    
    # 测试监控统计API响应时间
    start_time = time.time()
    response = requests.get(f"{API_BASE}/monitoring/stats")
    end_time = time.time()
    
    if response.status_code == 200:
        response_time = (end_time - start_time) * 1000
        print(f"✅ 监控统计API响应时间: {response_time:.2f}ms")
    else:
        print(f"❌ 监控统计API测试失败: {response.status_code}")

def test_export_with_filters():
    """测试带过滤条件的导出功能"""
    print("\n🔍 测试带过滤条件的导出功能...")
    
    # 测试带日期过滤的CSV导出
    params = {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    
    response = requests.get(f"{API_BASE}/export/activities/csv", params=params)
    if response.status_code == 200:
        print("✅ 带日期过滤的CSV导出成功")
        print(f"   文件大小: {len(response.content)} bytes")
    else:
        print(f"❌ 带日期过滤的CSV导出失败: {response.status_code}")

def main():
    """主测试函数"""
    print("🚀 Inspector 改进功能测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试目标: {BASE_URL}")
    print("=" * 50)
    
    try:
        # 测试健康检查
        test_health_check()
        
        # 测试数据导出
        test_export_functions()
        
        # 测试通知系统
        test_notification_system()
        
        # 测试数据库性能
        test_database_performance()
        
        # 测试API性能
        test_api_performance()
        
        # 测试带过滤条件的导出
        test_export_with_filters()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试完成！")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请确保Inspector后端正在运行")
        print("   启动命令: uv run python main.py")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    main()
