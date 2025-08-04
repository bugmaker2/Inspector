#!/usr/bin/env python3
"""
简单的流式功能测试
"""

import asyncio
import json
import httpx
from datetime import datetime

async def test_streaming_endpoints():
    """测试流式端点是否可访问"""
    base_url = "http://localhost:8000"
    
    print("🚀 测试流式API端点...")
    
    # 测试端点是否可访问
    endpoints = [
        "/api/v1/monitoring/generate-daily-summary-stream",
        "/api/v1/monitoring/generate-weekly-summary-stream"
    ]
    
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            try:
                response = await client.post(
                    f"{base_url}{endpoint}",
                    headers={"Content-Type": "application/json"},
                    json={},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    print(f"✅ {endpoint} - 端点可访问")
                    # 检查响应头
                    content_type = response.headers.get("content-type", "")
                    if "text/event-stream" in content_type or "text/plain" in content_type:
                        print(f"   📡 响应类型: {content_type}")
                    else:
                        print(f"   ⚠️  响应类型: {content_type}")
                else:
                    print(f"❌ {endpoint} - 状态码: {response.status_code}")
                    print(f"   响应: {response.text[:200]}...")
                    
            except httpx.ConnectError:
                print(f"❌ {endpoint} - 连接失败 (服务器可能未启动)")
            except Exception as e:
                print(f"❌ {endpoint} - 错误: {e}")
    
    print("\n🎉 流式API端点测试完成！")

if __name__ == "__main__":
    asyncio.run(test_streaming_endpoints()) 