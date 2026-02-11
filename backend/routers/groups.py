from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import secrets
import qrcode
from io import BytesIO
import base64
import os

from database import get_db, Group, User, GroupMembership
from schemas import GroupCreate, Group as GroupSchema, GroupWithQR, GroupJoin
from dependencies import get_current_user, require_teacher

router = APIRouter()


def generate_join_code() -> str:
    """Generate a unique join code for a group"""
    return secrets.token_urlsafe(16)


def generate_qr_code(join_url: str) -> str:
    """Generate QR code image as base64 string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(join_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


@router.post("/", response_model=GroupWithQR, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Create a new group (teacher only)"""
    # Generate unique join code
    join_code = generate_join_code()
    
    # Create group
    group = Group(
        name=group_data.name,
        goal_description=group_data.goal_description,
        teacher_id=current_user.id,
        join_code=join_code
    )
    
    db.add(group)
    db.commit()
    db.refresh(group)
    
    # Generate join URL and QR code
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    join_url = f"{frontend_url}/join/{join_code}"
    qr_code_url = generate_qr_code(join_url)
    
    return GroupWithQR(
        id=group.id,
        name=group.name,
        goal_description=group.goal_description,
        teacher_id=group.teacher_id,
        join_code=group.join_code,
        created_at=group.created_at.isoformat(),
        qr_code_url=qr_code_url,
        join_url=join_url
    )


@router.get("/", response_model=List[GroupSchema])
async def list_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List groups based on user role"""
    if current_user.role == "teacher":
        # Teachers see groups they created
        groups = db.query(Group).filter(Group.teacher_id == current_user.id).all()
    else:
        # Students see groups they've joined
        memberships = db.query(GroupMembership).filter(
            GroupMembership.user_id == current_user.id
        ).all()
        group_ids = [m.group_id for m in memberships]
        groups = db.query(Group).filter(Group.id.in_(group_ids)).all() if group_ids else []
    
    return [
        GroupSchema(
            id=g.id,
            name=g.name,
            goal_description=g.goal_description,
            teacher_id=g.teacher_id,
            join_code=g.join_code,
            created_at=g.created_at.isoformat()
        )
        for g in groups
    ]


@router.get("/{group_id}", response_model=GroupWithQR)
async def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get group details with QR code"""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check authorization
    if current_user.role == "teacher":
        if group.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this group")
    else:
        # Check if student is a member
        membership = db.query(GroupMembership).filter(
            GroupMembership.user_id == current_user.id,
            GroupMembership.group_id == group_id
        ).first()
        if not membership:
            raise HTTPException(status_code=403, detail="Not a member of this group")
    
    # Generate join URL and QR code
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    join_url = f"{frontend_url}/join/{group.join_code}"
    qr_code_url = generate_qr_code(join_url)
    
    return GroupWithQR(
        id=group.id,
        name=group.name,
        goal_description=group.goal_description,
        teacher_id=group.teacher_id,
        join_code=group.join_code,
        created_at=group.created_at.isoformat(),
        qr_code_url=qr_code_url,
        join_url=join_url
    )


@router.post("/join", status_code=status.HTTP_200_OK)
async def join_group(
    join_data: GroupJoin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a group using join code"""
    # Find group by join code
    group = db.query(Group).filter(Group.join_code == join_data.join_code).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Invalid join code")
    
    # Check if already a member
    existing_membership = db.query(GroupMembership).filter(
        GroupMembership.user_id == current_user.id,
        GroupMembership.group_id == group.id
    ).first()
    
    if existing_membership:
        return {
            "message": "Already a member of this group",
            "group_id": group.id,
            "group_name": group.name
        }
    
    # Check device-based restriction if device_id provided
    if join_data.device_id:
        device_membership = db.query(GroupMembership).filter(
            GroupMembership.group_id == group.id,
            GroupMembership.device_id == join_data.device_id
        ).first()
        
        if device_membership:
            raise HTTPException(
                status_code=403,
                detail="This device has already joined the group"
            )
    
    # Create membership
    membership = GroupMembership(
        user_id=current_user.id,
        group_id=group.id,
        device_id=join_data.device_id
    )
    
    db.add(membership)
    db.commit()
    
    return {
        "message": "Successfully joined group",
        "group_id": group.id,
        "group_name": group.name
    }


@router.get("/{group_id}/members")
async def get_group_members(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Get list of group members (teacher only)"""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    if group.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    memberships = db.query(GroupMembership).filter(
        GroupMembership.group_id == group_id
    ).all()
    
    members = []
    for membership in memberships:
        user = db.query(User).filter(User.id == membership.user_id).first()
        if user:
            members.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "joined_at": membership.joined_at.isoformat()
            })
    
    return {"members": members}
