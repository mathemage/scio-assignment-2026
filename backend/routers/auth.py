from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
import os
import logging
from dotenv import load_dotenv

from database import get_db, User
from schemas import User as UserSchema
from auth_utils import create_access_token
from dependencies import get_current_user

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter()

# OAuth configuration
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@router.get("/google")
async def google_login(request: Request):
    """Initiate Google OAuth2 login flow"""
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/google/callback')
    
    # Return the authorization redirect response directly
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth2 callback"""
    try:
        # Get token from Google
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")
        
        email = user_info.get('email')
        name = user_info.get('name')
        google_id = user_info.get('sub')
        
        # Check if user exists
        user = db.query(User).filter(User.google_id == google_id).first()
        
        if not user:
            # Create new user - default role is student
            # Teachers must be designated by admin or through specific signup
            user = User(
                email=email,
                name=name,
                google_id=google_id,
                role="student"  # Default role
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create access token
        access_token = create_access_token(data={"sub": user.id})
        
        # Redirect to frontend with token
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?token={access_token}"
        )
    
    except Exception as e:
        # Log the error server-side
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authentication failed"
        )


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.post("/set-role/{user_id}")
async def set_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Set user role (for demo purposes only).
    
    For safety, this endpoint only allows users to change their own role
    and is gated behind a feature flag. To enable this demo behavior, 
    set DEMO_ALLOW_SELF_ROLE_CHANGE=true in environment variables.
    """
    # Feature flag: disable role changes by default
    demo_allow_self_change = os.getenv("DEMO_ALLOW_SELF_ROLE_CHANGE", "false").lower() == "true"
    if not demo_allow_self_change:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role change is disabled. Set DEMO_ALLOW_SELF_ROLE_CHANGE=true to enable for demo."
        )
    
    # Only allow users to change their own role
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only change your own role"
        )
    
    if role not in ["teacher", "student"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = role
    db.commit()
    db.refresh(user)
    
    return {"message": f"User role updated to {role}", "user": user}
