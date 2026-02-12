from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from database import init_db
from routers import auth, groups, chat

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()
    yield


app = FastAPI(
    title="Student Progress Monitor",
    description="Real-time application for monitoring student learning progress",
    version="1.0.0",
    lifespan=lifespan
)

# Validate required environment variables
secret_key = os.getenv("SECRET_KEY")
if not secret_key or secret_key == "your-secret-key-change-in-production":
    raise RuntimeError(
        "SECRET_KEY environment variable must be set to a secure, non-default value.\n"
        "To fix this:\n"
        "1. Generate a secure key: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\"\n"
        "2. Set SECRET_KEY in your .env file with the generated value\n"
        "3. Never commit the .env file to version control"
    )

# Validate Google OAuth credentials
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

if not google_client_id or google_client_id == "your-google-client-id":
    raise RuntimeError(
        "GOOGLE_CLIENT_ID environment variable must be set to a valid Google OAuth client ID.\n"
        "To fix this:\n"
        "1. Go to Google Cloud Console: https://console.cloud.google.com\n"
        "2. Create a new project or select an existing one\n"
        "3. Enable the Google+ API (or Google Identity)\n"
        "4. Go to 'Credentials' and create OAuth 2.0 Client ID (Web application)\n"
        "5. Add authorized redirect URI: http://localhost:8000/auth/google/callback\n"
        "6. Copy the Client ID and set GOOGLE_CLIENT_ID in your .env file\n"
        "7. Never commit the .env file to version control"
    )

if not google_client_secret or google_client_secret == "your-google-client-secret":
    raise RuntimeError(
        "GOOGLE_CLIENT_SECRET environment variable must be set to a valid Google OAuth client secret.\n"
        "To fix this:\n"
        "1. Go to Google Cloud Console: https://console.cloud.google.com\n"
        "2. Navigate to your project's Credentials page\n"
        "3. Find your OAuth 2.0 Client ID\n"
        "4. Copy the Client Secret and set GOOGLE_CLIENT_SECRET in your .env file\n"
        "5. Never commit the .env file to version control"
    )

# Session middleware (required for OAuth)

environment = os.getenv("ENVIRONMENT", "development").lower()
https_only = environment == "production"
app.add_middleware(
    SessionMiddleware,
    secret_key=secret_key,
    https_only=https_only,
    same_site="lax",
    max_age=60 * 60 * 24 * 7,  # 1 week
)

# CORS configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(groups.router, prefix="/groups", tags=["Groups"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])


@app.get("/")
async def root():
    return {
        "message": "Student Progress Monitor API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
