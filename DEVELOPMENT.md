# Development Guide

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Google Cloud account (for OAuth2 credentials)

### Quick Setup

Run the setup script:

```bash
./setup.sh
```

Or manually:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Generate a secure SECRET_KEY:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy the output and update SECRET_KEY in .env
# Also add your Google OAuth2 credentials to .env
```

**Frontend:**
```bash
cd frontend
npm install
```

### Google OAuth2 Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable Google Identity Services (if not already enabled)
4. Create OAuth2 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8000/auth/google/callback`
5. Copy Client ID and Client Secret to `backend/.env`

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development Workflow

### Backend Development

The backend uses FastAPI with SQLAlchemy. Key files:

- `main.py` - Application entry point
- `database.py` - Database models
- `routers/` - API endpoints
- `schemas.py` - Pydantic schemas
- `auth_utils.py` - JWT utilities
- `dependencies.py` - Authentication dependencies

**Adding a new endpoint:**
1. Define schema in `schemas.py`
2. Add endpoint to appropriate router in `routers/`
3. Add authorization dependencies if needed

**Database changes:**
1. Modify models in `database.py`
2. Delete `student_monitor.db` for development
3. Restart the backend (auto-creates new DB)

**Testing API:**
- Use the interactive docs at http://localhost:8000/docs
- Or use curl/Postman

### Frontend Development

The frontend uses React with TypeScript and Vite.

Key directories:
- `src/pages/` - Page components
- `src/components/` - Reusable components (if needed)
- `src/hooks/` - Custom hooks (useAuth)
- `src/services/` - API service layer
- `src/types/` - TypeScript type definitions
- `src/utils/` - Utility functions

**Adding a new page:**
1. Create component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add TypeScript types in `src/types/`

**Calling backend API:**
Use the `apiService` from `src/services/api.ts`:
```typescript
const data = await apiService.getGroups(token);
```

**Type checking:**
```bash
npm run type-check
```

## Testing

### Manual Testing Flow

**Teacher Flow:**
1. Sign in with Google
2. Set role to "teacher" (use API docs or database)
3. Create a group with name and goal
4. View QR code on group page
5. Monitor student progress in real-time

**Student Flow:**
1. Sign in with Google  
2. Scan teacher's QR code or visit join URL
3. Join the group
4. Send messages in chat
5. See progress percentage update

### Setting User Roles

Option 1 - API:
1. Go to http://localhost:8000/docs
2. Use `/auth/me` to get your user ID
3. Use `/auth/set-role/{user_id}?role=teacher` to set role

Option 2 - Database:
```bash
cd backend
sqlite3 student_monitor.db
UPDATE users SET role = 'teacher' WHERE email = 'your@email.com';
.quit
```

## Common Issues

**Backend won't start:**
- Check Python version: `python --version` (need 3.9+)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check .env file exists and has valid values
- **If you see "SECRET_KEY environment variable must be set":**
  - Generate a new key: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
  - Update SECRET_KEY in .env with the generated value
  - Make sure you don't use the default value from .env.example

**Frontend won't start:**
- Check Node version: `node --version` (need 18+)
- Clear node_modules: `rm -rf node_modules && npm install`
- Check for port conflicts on 3000

**OAuth redirect fails:**
- Verify redirect URI in Google Console matches exactly
- Check GOOGLE_REDIRECT_URI in backend/.env
- Ensure backend is running on http://localhost:8000

**WebSocket not connecting:**
- Check browser console for errors
- Verify token is valid
- Check backend logs

**Database errors:**
- Delete `student_monitor.db` and restart backend
- Check file permissions

## Architecture Notes

### Authentication Flow

1. User clicks "Sign in with Google"
2. Frontend redirects to `/auth/google`
3. Backend redirects to Google OAuth
4. Google redirects back to `/auth/google/callback`
5. Backend creates/finds user, generates JWT
6. Redirects to frontend with token
7. Frontend stores token in localStorage
8. All API requests include token in Authorization header

### Real-time Communication

- WebSocket connection per group
- Messages broadcast to all group members
- Progress updates sent after each message
- Connection manager handles multiple simultaneous connections

### Progress Estimation

Current implementation is simple (message count based):
- 1 message = 10% progress
- Max 100% at 10 messages

In production, this would use:
- NLP to analyze message content
- AI/ML to assess understanding
- Teacher-defined criteria
- Multiple progress dimensions

## File Structure

```
.
├── backend/
│   ├── venv/                  # Python virtual env
│   ├── main.py               # FastAPI app
│   ├── database.py           # DB models
│   ├── schemas.py            # Pydantic schemas
│   ├── auth_utils.py         # JWT utilities
│   ├── dependencies.py       # Auth dependencies
│   ├── routers/
│   │   ├── auth.py          # Auth endpoints
│   │   ├── groups.py        # Group management
│   │   └── chat.py          # Chat & WebSocket
│   ├── requirements.txt
│   ├── .env
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API services
│   │   ├── types/           # TypeScript types
│   │   ├── utils/           # Utilities
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── README.md
├── DEVELOPMENT.md
└── setup.sh
```

## Production Deployment

For production deployment, consider:

1. **Backend:**
   - Use PostgreSQL instead of SQLite
   - Set strong SECRET_KEY
   - Use environment-specific .env files
   - Add rate limiting
   - Enable HTTPS only
   - Use production ASGI server (Gunicorn + Uvicorn)

2. **Frontend:**
   - Build for production: `npm run build`
   - Serve from CDN or static hosting
   - Configure production API URL
   - Enable security headers

3. **Infrastructure:**
   - Deploy backend and frontend separately
   - Use reverse proxy (nginx)
   - Enable WebSocket support in proxy
   - Set up SSL certificates
   - Configure CORS properly

4. **Database:**
   - Use managed database service
   - Set up backups
   - Add database migrations
   - Monitor performance

5. **Security:**
   - Audit dependencies regularly
   - Implement rate limiting
   - Add request validation
   - Enable logging and monitoring
   - Regular security reviews
