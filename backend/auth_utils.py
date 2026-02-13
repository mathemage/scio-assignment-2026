from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Parse ACCESS_TOKEN_EXPIRE_MINUTES with error handling
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
except ValueError:
    # Log warning - this will only execute during import if env var is invalid
    import logging
    logging.warning("Invalid ACCESS_TOKEN_EXPIRE_MINUTES value, using default of 30")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[verify_token] Attempting to verify token: {token[:20]}...")
        logger.info(f"[verify_token] Using SECRET_KEY: {SECRET_KEY[:10]}... and ALGORITHM: {ALGORITHM}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"[verify_token] Token verified successfully, payload: {payload}")
        return payload
    except JWTError as e:
        logger.error(f"[verify_token] JWT verification error: {str(e)}")
        return None
