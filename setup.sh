#!/bin/bash

# Setup script for Student Progress Monitor

echo "Setting up Student Progress Monitor..."
echo ""

# Backend setup
echo "1. Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "   Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "   Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "   Creating .env file from example..."
    cp .env.example .env
    
    # Generate a secure SECRET_KEY
    echo "   Generating secure SECRET_KEY..."
    if ! SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null); then
        echo "   ⚠️  Warning: Could not auto-generate SECRET_KEY"
        echo "   Please manually generate one using:"
        echo "      python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
        echo "   Then update SECRET_KEY in backend/.env"
    else
        # Use Python to safely replace the SECRET_KEY (handles special characters)
        python3 -c "
import sys
secret_key = sys.argv[1]

with open('.env', 'r') as f:
    content = f.read()

# Replace the default SECRET_KEY with the generated one
content = content.replace(
    'SECRET_KEY=your-secret-key-change-in-production',
    f'SECRET_KEY={secret_key}'
)

with open('.env', 'w') as f:
    f.write(content)
" "$SECRET_KEY"
        
        echo "   ✅ Secure SECRET_KEY generated and saved to .env"
    fi
    
    echo "   ⚠️  Please edit backend/.env with your Google OAuth2 credentials"
fi

cd ..

# Frontend setup
echo ""
echo "2. Setting up frontend..."
cd frontend

# Install Node.js dependencies
echo "   Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure Google OAuth2 credentials in backend/.env"
echo "2. Start the backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "3. Start the frontend: cd frontend && npm run dev"
echo ""
echo "Backend will run on: http://localhost:8000"
echo "Frontend will run on: http://localhost:3000"
echo "API docs: http://localhost:8000/docs"
