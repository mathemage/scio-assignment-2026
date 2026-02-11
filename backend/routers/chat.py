from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime
import json

from database import get_db, Message, User, Group, GroupMembership
from schemas import MessageCreate, Message as MessageSchema, ProgressEstimate
from dependencies import get_current_user
from auth_utils import verify_token

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, group_id: int):
        await websocket.accept()
        if group_id not in self.active_connections:
            self.active_connections[group_id] = []
        self.active_connections[group_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, group_id: int):
        if group_id in self.active_connections:
            self.active_connections[group_id].remove(websocket)
    
    async def broadcast(self, message: dict, group_id: int):
        if group_id in self.active_connections:
            for connection in self.active_connections[group_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass


manager = ConnectionManager()


@router.websocket("/ws/{group_id}")
async def websocket_endpoint(websocket: WebSocket, group_id: int, token: str):
    """WebSocket endpoint for real-time chat and progress updates"""
    # Verify token
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=1008)
        return
    
    user_id = payload.get("sub")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close(code=1008)
            return
        
        # Verify group exists
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            await websocket.close(code=1008)
            return
        
        # Verify authorization
        if user.role == "teacher":
            if group.teacher_id != user_id:
                await websocket.close(code=1008)
                return
        else:
            membership = db.query(GroupMembership).filter(
                GroupMembership.user_id == user_id,
                GroupMembership.group_id == group_id
            ).first()
            if not membership:
                await websocket.close(code=1008)
                return
        
        # Connect
        await manager.connect(websocket, group_id)
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "user_id": user_id,
            "user_name": user.name,
            "group_id": group_id
        })
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                # Save message to database
                message = Message(
                    content=message_data.get("content"),
                    user_id=user_id,
                    group_id=group_id
                )
                db.add(message)
                db.commit()
                db.refresh(message)
                
                # Broadcast to all connections in the group
                await manager.broadcast({
                    "type": "message",
                    "id": message.id,
                    "content": message.content,
                    "user_id": user_id,
                    "user_name": user.name,
                    "created_at": message.created_at.isoformat()
                }, group_id)
                
                # If teacher is connected, also send progress update
                if user.role == "student":
                    progress = calculate_student_progress(db, user_id, group_id)
                    await manager.broadcast({
                        "type": "progress_update",
                        "user_id": user_id,
                        "user_name": user.name,
                        "progress": progress
                    }, group_id)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, group_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, group_id)
    finally:
        db.close()


# Constants for progress calculation
PROGRESS_PER_MESSAGE = 10  # Each message contributes 10% to progress
MAX_PROGRESS = 100  # Maximum progress percentage


def calculate_student_progress(db: Session, user_id: int, group_id: int) -> dict:
    """Calculate simple progress estimate based on message count"""
    messages = db.query(Message).filter(
        Message.user_id == user_id,
        Message.group_id == group_id
    ).all()
    
    message_count = len(messages)
    
    # Simple heuristic: PROGRESS_PER_MESSAGE% per message
    # In production, this would use AI/NLP to analyze actual progress
    progress_percentage = min(message_count * PROGRESS_PER_MESSAGE, MAX_PROGRESS)
    
    last_message_time = None
    if messages:
        last_message = max(messages, key=lambda m: m.created_at)
        last_message_time = last_message.created_at.isoformat()
    
    return {
        "progress_percentage": progress_percentage,
        "messages_count": message_count,
        "last_message_time": last_message_time
    }


@router.get("/{group_id}/messages", response_model=List[MessageSchema])
async def get_messages(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all messages for a group"""
    # Verify group exists
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Verify authorization
    if current_user.role == "teacher":
        if group.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    else:
        membership = db.query(GroupMembership).filter(
            GroupMembership.user_id == current_user.id,
            GroupMembership.group_id == group_id
        ).first()
        if not membership:
            raise HTTPException(status_code=403, detail="Not a member of this group")
    
    # Get messages
    messages = db.query(Message).filter(Message.group_id == group_id).order_by(Message.created_at).all()
    
    result = []
    for msg in messages:
        user = db.query(User).filter(User.id == msg.user_id).first()
        result.append(MessageSchema(
            id=msg.id,
            content=msg.content,
            user_id=msg.user_id,
            group_id=msg.group_id,
            created_at=msg.created_at.isoformat(),
            user_name=user.name if user else "Unknown"
        ))
    
    return result


@router.get("/{group_id}/progress", response_model=List[ProgressEstimate])
async def get_group_progress(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get progress for all students in a group (teacher only)"""
    # Verify group exists
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Verify teacher authorization
    if current_user.role != "teacher" or group.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the group teacher can view progress")
    
    # Get all members
    memberships = db.query(GroupMembership).filter(
        GroupMembership.group_id == group_id
    ).all()
    
    progress_list = []
    for membership in memberships:
        user = db.query(User).filter(User.id == membership.user_id).first()
        if user:
            progress = calculate_student_progress(db, user.id, group_id)
            progress_list.append(ProgressEstimate(
                user_id=user.id,
                user_name=user.name,
                progress_percentage=progress["progress_percentage"],
                messages_count=progress["messages_count"],
                last_message_time=progress["last_message_time"]
            ))
    
    return progress_list
