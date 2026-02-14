from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str


class UserCreate(UserBase):
    google_id: str


class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


class GoogleAuthURL(BaseModel):
    auth_url: str


class GroupBase(BaseModel):
    name: str
    goal_description: str


class GroupCreate(GroupBase):
    pass


class Group(GroupBase):
    id: int
    teacher_id: int
    join_code: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class GroupWithQR(Group):
    qr_code_url: str
    join_url: str


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    group_id: int


class Message(MessageBase):
    id: int
    user_id: int
    group_id: int
    created_at: datetime
    user_name: str
    
    class Config:
        from_attributes = True


class GroupJoin(BaseModel):
    join_code: str
    device_id: Optional[str] = None


class ProgressEstimate(BaseModel):
    user_id: int
    user_name: str
    progress_percentage: float
    messages_count: int
    last_message_time: Optional[str] = None
