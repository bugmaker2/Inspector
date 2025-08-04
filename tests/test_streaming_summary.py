#!/usr/bin/env python3
"""
测试流式报告生成功能
"""

import asyncio
import json
import httpx
from datetime import datetime

async def test_streaming_summary():
    """测试流式报告生成"""
    base_url = "http://localhost:8000"
    
    print("🚀 开始测试流式报告生成功能...")
    
    # 测试每日总结流式生成
    print("\n📊 测试每日总结流式生成...")
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{base_url}/api/v1/monitoring/generate-daily-summary-stream",
                headers={"Content-Type": "application/json"},
                json={},
                timeout=120.0
            ) as response:
                if response.status_code == 200:
                    print("✅ 流式连接建立成功")
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                print(f"📡 收到数据: {data['type']} - {data.get('message', '')} - {data.get('progress', 0)}%")
                                
                                if data['type'] == 'complete':
                                    print("✅ 每日总结生成完成！")
                                    print(f"📋 总结标题: {data['summary']['title']}")
                                    break
                                elif data['type'] == 'error':
                                    print(f"❌ 生成失败: {data['message']}")
                                    break
                            except json.JSONDecodeError:
                                continue
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                    print(await response.text())
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 测试每周总结流式生成
    print("\n📈 测试每周总结流式生成...")
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{base_url}/api/v1/monitoring/generate-weekly-summary-stream",
                headers={"Content-Type": "application/json"},
                json={},
                timeout=120.0
            ) as response:
                if response.status_code == 200:
                    print("✅ 流式连接建立成功")
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                print(f"📡 收到数据: {data['type']} - {data.get('message', '')} - {data.get('progress', 0)}%")
                                
                                if data['type'] == 'complete':
                                    print("✅ 每周总结生成完成！")
                                    print(f"📋 总结标题: {data['summary']['title']}")
                                    break
                                elif data['type'] == 'error':
                                    print(f"❌ 生成失败: {data['message']}")
                                    break
                            except json.JSONDecodeError:
                                continue
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                    print(await response.text())
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n🎉 流式报告生成功能测试完成！")

if __name__ == "__main__":
    asyncio.run(test_streaming_summary()) 