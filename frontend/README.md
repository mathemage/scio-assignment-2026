# Student Progress Monitor - Frontend

React + TypeScript frontend for real-time student progress monitoring.

## Features

- Google OAuth2 authentication
- Role-based dashboards (Teacher/Student)
- Real-time chat with WebSockets
- QR code generation and scanning
- Live progress tracking
- Responsive UI

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```bash
VITE_API_URL=http://localhost:8000
```

## Development

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build

```bash
npm run build
```

## Project Structure

```
src/
├── components/      # Reusable components
├── pages/          # Page components
├── hooks/          # Custom hooks (auth, etc.)
├── services/       # API services
├── types/          # TypeScript types
├── utils/          # Utility functions
├── App.tsx         # Main app component
└── main.tsx        # Entry point
```

## Pages

- `/login` - Login page
- `/dashboard` - Role-based dashboard
- `/teacher/group/:id` - Teacher group view with QR and progress
- `/student/group/:id` - Student chat view
- `/join/:code` - Group join page

## Technology Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Routing
- **react-qr-code** - QR code generation
- **WebSocket** - Real-time communication
