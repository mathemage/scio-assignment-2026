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
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Replace the default SECRET_KEY in .env with the generated one
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|SECRET_KEY=your-secret-key-change-in-production|SECRET_KEY=$SECRET_KEY|" .env
    else
        # Linux
        sed -i "s|SECRET_KEY=your-secret-key-change-in-production|SECRET_KEY=$SECRET_KEY|" .env
    fi
    
    echo "   ✅ Secure SECRET_KEY generated and saved to .env"
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
