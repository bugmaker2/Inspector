"""Real-time notifications API endpoints."""

import asyncio
import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database.database import get_db
from app.models.member import Activity, Summary

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Notification models
class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str = "info"  # info, success, warning, error
    data: Optional[dict] = None

class Notification(NotificationCreate):
    id: int
    created_at: datetime
    read: bool = False

# Notification storage (in production, use Redis or database)
notifications: List[Notification] = []
notification_id_counter = 1

@router.get("/")
async def get_notifications(
    limit: int = 50,
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get notifications."""
    global notifications
    
    filtered_notifications = notifications
    if unread_only:
        filtered_notifications = [n for n in notifications if not n.read]
    
    return filtered_notifications[-limit:]

@router.post("/")
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    """Create a new notification."""
    global notifications, notification_id_counter
    
    new_notification = Notification(
        id=notification_id_counter,
        title=notification.title,
        message=notification.message,
        type=notification.type,
        data=notification.data,
        created_at=datetime.utcnow()
    )
    
    notifications.append(new_notification)
    notification_id_counter += 1
    
    # Broadcast to all connected clients
    await manager.broadcast(json.dumps({
        "type": "notification",
        "data": {
            "id": new_notification.id,
            "title": new_notification.title,
            "message": new_notification.message,
            "type": new_notification.type,
            "created_at": new_notification.created_at.isoformat()
        }
    }))
    
    return new_notification

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    global notifications
    
    for notification in notifications:
        if notification.id == notification_id:
            notification.read = True
            return {"message": "Notification marked as read"}
    
    raise HTTPException(status_code=404, detail="Notification not found")

@router.put("/read-all")
async def mark_all_notifications_read(
    db: Session = Depends(get_db)
):
    """Mark all notifications as read."""
    global notifications
    
    for notification in notifications:
        notification.read = True
    
    return {"message": "All notifications marked as read"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Delete a notification."""
    global notifications
    
    for i, notification in enumerate(notifications):
        if notification.id == notification_id:
            del notifications[i]
            return {"message": "Notification deleted"}
    
    raise HTTPException(status_code=404, detail="Notification not found")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time notifications."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for ping/pong
            await websocket.send_text(json.dumps({"type": "pong", "data": data}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# System notification functions
async def notify_new_activity(activity: Activity):
    """Notify about new activity."""
    notification = NotificationCreate(
        title="新活动",
        message=f"成员 {activity.member.name if activity.member else 'Unknown'} 在 {activity.platform} 发布了新内容",
        type="info",
        data={
            "activity_id": activity.id,
            "member_id": activity.member_id,
            "platform": activity.platform
        }
    )
    
    # Create notification
    await create_notification(notification, None)

async def notify_summary_generated(summary: Summary):
    """Notify about generated summary."""
    notification = NotificationCreate(
        title="总结生成完成",
        message=f"{summary.summary_type} 总结已生成完成",
        type="success",
        data={
            "summary_id": summary.id,
            "summary_type": summary.summary_type
        }
    )
    
    # Create notification
    await create_notification(notification, None)

async def notify_monitoring_error(platform: str, error: str):
    """Notify about monitoring error."""
    notification = NotificationCreate(
        title="监控错误",
        message=f"{platform} 平台监控出现错误: {error}",
        type="error",
        data={
            "platform": platform,
            "error": error
        }
    )
    
    # Create notification
    await create_notification(notification, None)

# HTML page for testing WebSocket
@router.get("/test", response_class=HTMLResponse)
async def get_test_page():
    """Test page for WebSocket notifications."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>WebSocket Notification Test</h1>
        <div id="messages"></div>
        <script>
            const ws = new WebSocket("ws://localhost:8000/api/v1/notifications/ws");
            const messagesDiv = document.getElementById("messages");
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const messageDiv = document.createElement("div");
                messageDiv.textContent = JSON.stringify(data, null, 2);
                messagesDiv.appendChild(messageDiv);
            };
            
            ws.onopen = function() {
                console.log("WebSocket connected");
            };
            
            ws.onclose = function() {
                console.log("WebSocket disconnected");
            };
        </script>
    </body>
    </html>
    """
