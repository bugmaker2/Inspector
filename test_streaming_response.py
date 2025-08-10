#!/usr/bin/env python3
"""Test StreamingResponse functionality."""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient
import io
import json

app = FastAPI()

@app.get("/test-streaming")
def test_streaming():
    """Test StreamingResponse with JSON data."""
    data = [{"id": 1, "name": "Test"}]
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    
    return StreamingResponse(
        io.BytesIO(json_str.encode('utf-8')),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=test.json"}
    )

client = TestClient(app)

def test_streaming_response():
    """Test the streaming response."""
    try:
        print("Testing StreamingResponse...")
        response = client.get("/test-streaming")
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")
        print("StreamingResponse test completed successfully")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_streaming_response()
