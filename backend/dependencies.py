from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db, User
from auth_utils import verify_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    import logging
    logger = logging.getLogger(__name__)
    
    token = credentials.credentials
    logger.info(f"[get_current_user] Received token: {token[:20]}...")
    
    payload = verify_token(token)
    logger.info(f"[get_current_user] Token verification result: {payload}")
    
    if payload is None:
        logger.error("[get_current_user] Token verification failed - payload is None")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id_str = payload.get("sub")
    logger.info(f"[get_current_user] Extracted user_id from payload: {user_id_str}")
    
    if user_id_str is None:
        logger.error("[get_current_user] No user_id in token payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    # Convert string user_id back to integer
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        logger.error(f"[get_current_user] Invalid user_id format: {user_id_str}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.error(f"[get_current_user] User not found in database for user_id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    logger.info(f"[get_current_user] User authenticated successfully: {user.email}")
    return user


def require_teacher(current_user: User = Depends(get_current_user)) -> User:
    """Require that the current user is a teacher"""
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher role required"
        )
    return current_user


def require_student(current_user: User = Depends(get_current_user)) -> User:
    """Require that the current user is a student"""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student role required"
        )
    return current_user
