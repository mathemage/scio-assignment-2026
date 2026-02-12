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

# Session middleware (required for OAuth)
secret_key = os.getenv("SECRET_KEY")
if not secret_key or secret_key == "your-secret-key-change-in-production":
    raise RuntimeError(
        "SECRET_KEY environment variable must be set to a secure, non-default value.\n"
        "To fix this:\n"
        "1. Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(32))'\n"
        "2. Set SECRET_KEY in your .env file with the generated value\n"
        "3. Never commit the .env file to version control"
    )

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
