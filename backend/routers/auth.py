from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
import os
import logging
from dotenv import load_dotenv
from urllib.parse import urlencode, urlparse

from database import get_db, User
from schemas import User as UserSchema
from auth_utils import create_access_token
from dependencies import get_current_user

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter()

# Default frontend URL for fallback scenarios
DEFAULT_FRONTEND_URL = "http://localhost:3000"

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
        
        logger.info(f"[google_callback] User authenticated via Google: {email}")
        
        # Check if user exists
        user = db.query(User).filter(User.google_id == google_id).first()
        
        if not user:
            # Create new user - default role is student
            # Teachers must be designated by admin or through specific signup
            logger.info(f"[google_callback] Creating new user: {email}")
            user = User(
                email=email,
                name=name,
                google_id=google_id,
                role="student"  # Default role
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            logger.info(f"[google_callback] Existing user found: {email} (id={user.id})")
        
        # Create access token
        access_token = create_access_token(data={"sub": user.id})
        logger.info(f"[google_callback] Created access token for user {user.id}: {access_token[:20]}...")
        
        # Redirect to frontend with token
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        redirect_url = f"{frontend_url}/auth/callback?token={access_token}"
        logger.info(f"[google_callback] Redirecting to: {redirect_url[:100]}...")
        return RedirectResponse(url=redirect_url)
    
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


@router.get("/callback")
async def auth_callback(request: Request):
    """
    Handle authentication callback - this endpoint catches misconfigured redirects.
    
    This endpoint should normally not be called. If it is being called, it means
    that FRONTEND_URL is misconfigured and pointing to the backend instead of frontend.
    
    The proper flow should redirect to the frontend's /auth/callback endpoint.
    """
    # Get the token from query params
    token = request.query_params.get("token")
    
    if token:
        # Get FRONTEND_URL from env, with safe default
        frontend_url = os.getenv('FRONTEND_URL', DEFAULT_FRONTEND_URL)
        
        # Detect if FRONTEND_URL points to the backend (would cause redirect loop)
        # Compare the host:port of frontend_url with the current request
        frontend_parsed = urlparse(frontend_url)
        backend_host = request.url.hostname
        backend_port = request.url.port
        
        # Normalize ports: use default port if not explicitly specified
        frontend_port = frontend_parsed.port
        if frontend_port is None:
            frontend_port = 443 if frontend_parsed.scheme == "https" else 80
        if backend_port is None:
            backend_port = 443 if request.url.scheme == "https" else 80
        
        # Check if frontend_url resolves to the same host:port as the backend
        is_same_host = (
            frontend_parsed.hostname == backend_host and
            frontend_port == backend_port
        )
        
        if is_same_host:
            # FRONTEND_URL points to backend - use safe fallback
            logger.warning(
                f"Backend /auth/callback was called with token, and FRONTEND_URL "
                f"({frontend_url}) points to the backend. Using safe fallback: {DEFAULT_FRONTEND_URL}"
            )
            frontend_url = DEFAULT_FRONTEND_URL
        else:
            # Log warning about misconfiguration
            logger.warning(
                f"Backend /auth/callback was called with token. "
                f"This suggests FRONTEND_URL might be misconfigured. "
                f"Redirecting to frontend: {frontend_url}/auth/callback"
            )
        
        # Build redirect URL with properly encoded token
        redirect_url = f"{frontend_url}/auth/callback?{urlencode({'token': token})}"
        
        return RedirectResponse(url=redirect_url)
    
    # No token provided - return error
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Missing authentication token"
    )


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
