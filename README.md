# Student Progress Monitor

Real-time application for monitoring student learning progress. Teachers can create groups with learning goals, students join via QR codes, and the system tracks progress through chat interactions.

## Features

✅ **Authentication & Authorization**
- Google OAuth2 sign-in
- Role-based access control (Teacher/Student)
- Backend authorization enforcement

✅ **Teacher Features**
- Create and manage learning groups
- Define learning goals for each group
- Generate QR codes for group joining
- Monitor student progress in real-time
- View live chat activity

✅ **Student Features**
- Join groups via QR code
- Text-based chat interface
- Real-time progress feedback
- Device-based join restrictions (localStorage)

✅ **Real-time Communication**
- WebSocket-based chat
- Live progress updates
- Instant message delivery

## Architecture

### Backend (FastAPI)
- Python 3.x with FastAPI
- SQLAlchemy ORM + SQLite database
- Google OAuth2 authentication
- WebSocket support for real-time features
- JWT token-based authorization

### Frontend (React + TypeScript)
- React 18 with TypeScript
- Vite build tool
- React Router for navigation
- WebSocket client for real-time updates
- QR code generation and display

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Cloud project with OAuth2 credentials

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Generate a secure SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy the output and update SECRET_KEY in .env
# Also add your Google OAuth2 credentials to .env
```

4. Run the server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

App: http://localhost:3000

## Google OAuth2 Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Configure the OAuth consent screen (APIs & Services → OAuth consent screen)
4. Create an OAuth 2.0 Client ID (Web application) under APIs & Services → Credentials
5. In the client configuration, add the authorized redirect URI: `http://localhost:8000/auth/google/callback`
6. Copy the Client ID and Client Secret into the backend `.env` file

## Usage

### For Teachers

1. Sign in with Google account
2. Set your role to "teacher" using one of these methods:
   - **Quick script**: `./scripts/make_teacher.sh your@email.com`
   - **Database directly**: `python scripts/set_user_role.py your@email.com teacher`
   - **API endpoint**: See "Setting User Roles" section below
3. Create a new group with name and learning goal
4. Share the QR code with students
5. Monitor real-time progress on the group page

### For Students

1. Sign in with Google account (default role is "student")
2. Scan teacher's QR code or use join link
3. Start chatting to demonstrate progress
4. See your progress percentage update in real-time

### Setting User Roles

By default, all users who sign in are assigned the "student" role. To use teacher features, you need to set your role to "teacher".

#### Method 1: Quick Script (Recommended)

After signing in at least once with Google OAuth:

```bash
# List all registered users
python scripts/list_users.py

# Set a user's role to teacher
./scripts/make_teacher.sh your@email.com
```

#### Method 2: Python Script

```bash
# Set role to teacher
python scripts/set_user_role.py your@email.com teacher

# Set role back to student
python scripts/set_user_role.py your@email.com student
```

#### Method 3: Database Direct Edit

```bash
cd backend
sqlite3 student_monitor.db
UPDATE users SET role = 'teacher' WHERE email = 'your@email.com';
.quit
```

#### Method 4: API Endpoint (Development Only)

For development/testing, you can enable self-service role changes:

1. Add to your `backend/.env`:
   ```
   DEMO_ALLOW_SELF_ROLE_CHANGE=true
   ```

2. Restart the backend server

3. Use the API endpoint:
   ```bash
   # Get your user ID
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/auth/me
   
   # Set your role to teacher
   curl -X POST "http://localhost:8000/auth/set-role/YOUR_USER_ID?role=teacher" \
        -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

   Or use the interactive API docs at http://localhost:8000/docs

**Note**: The API endpoint method is disabled by default for security. Use database or script methods in production.

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database models & setup
│   ├── schemas.py           # Pydantic schemas
│   ├── auth_utils.py        # JWT utilities
│   ├── dependencies.py      # Auth dependencies
│   ├── routers/
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── groups.py       # Group management
│   │   └── chat.py         # Chat & WebSocket
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API services
│   │   ├── types/          # TypeScript types
│   │   ├── utils/          # Utilities
│   │   └── App.tsx         # Main app
│   └── package.json
│
└── README.md
```

## Security Features

- JWT token-based authentication
- Role-based access control enforced on backend
- Device-based join restrictions
- CORS configuration
- Secure WebSocket connections
- Authorization checks on all protected endpoints

## Progress Estimation

The current implementation uses a simple heuristic (message count) for progress estimation. In a production system, this would be replaced with:
- Natural Language Processing to analyze message content
- AI/ML models to assess understanding
- Teacher-defined criteria matching
- Multi-dimensional progress metrics

## Development

### Backend Development
```bash
cd backend
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Type Checking (Frontend)
```bash
npm run type-check
```

## License

GPL-3.0-or-later License - See LICENSE file for details

## Contributing

This is a prototype/MVP. Contributions welcome for:
- Enhanced progress estimation algorithms
- UI/UX improvements
- Additional features (file sharing, video, etc.)
- Performance optimizations
- Test coverage
