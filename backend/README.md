# Student Progress Monitor - Backend

FastAPI backend for real-time student progress monitoring application.

## Features

- Google OAuth2 authentication
- Role-based access control (Teacher/Student)
- Group management with QR codes
- Real-time chat via WebSockets
- Progress estimation and monitoring

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file from example:
```bash
cp .env.example .env
```

3. Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output and replace the `SECRET_KEY` value in your `.env` file.

4. Configure your `.env` file with:
   - The generated SECRET_KEY from step 3
   - Google OAuth2 credentials (get from Google Cloud Console)
   - Database URL (defaults to SQLite)

## Running

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## API Endpoints

### Authentication
- `GET /auth/google` - Initiate Google OAuth2 login
- `GET /auth/google/callback` - OAuth2 callback
- `GET /auth/me` - Get current user info
- `POST /auth/set-role/{user_id}` - Set user role

### Groups
- `POST /groups/` - Create new group (teacher only)
- `GET /groups/` - List user's groups
- `GET /groups/{group_id}` - Get group details with QR code
- `POST /groups/join` - Join group with join code
- `GET /groups/{group_id}/members` - Get group members (teacher only)

### Chat
- `WebSocket /chat/ws/{group_id}?token={jwt_token}` - WebSocket for real-time chat
- `GET /chat/{group_id}/messages` - Get message history
- `GET /chat/{group_id}/progress` - Get student progress (teacher only)

## Architecture

- **FastAPI**: Modern async web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Database (easily switchable to PostgreSQL)
- **WebSockets**: Real-time communication
- **JWT**: Token-based authentication
- **Google OAuth2**: User authentication

## Security

- RBAC enforced on backend
- JWT token authentication
- CORS configuration
- Authorization checks on all protected endpoints
