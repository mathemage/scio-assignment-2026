#!/bin/bash
# Quick Demo Setup Script
# This script sets up the application with test data and shows how to manage user roles

echo "========================================="
echo "Student Progress Monitor - Quick Demo"
echo "========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Error: Please run this script from the repository root directory"
    exit 1
fi

# Step 1: Navigate to backend
echo "Step 1: Setting up test data..."
cd backend

# Create test data
python3 create_test_data.py
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to create test data"
    exit 1
fi

echo ""
echo "========================================="
echo "Step 2: Available Helper Scripts"
echo "========================================="
echo ""
echo "The following scripts are now available:"
echo ""
echo "1. List all users:"
echo "   python scripts/list_users.py"
echo ""
echo "2. Set a user's role to teacher:"
echo "   ./scripts/make_teacher.sh <email>"
echo "   OR"
echo "   python scripts/set_user_role.py <email> teacher"
echo ""
echo "3. Set a user's role to student:"
echo "   python scripts/set_user_role.py <email> student"
echo ""

cd ..

# Step 3: Demonstrate the scripts
echo "========================================="
echo "Step 3: Demonstrating the scripts"
echo "========================================="
echo ""

echo "📋 Listing all users:"
echo ""
python scripts/list_users.py

echo ""
echo "========================================="
echo "Demo Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the backend server:"
echo "   cd backend && uvicorn main:app --reload"
echo ""
echo "2. Start the frontend server (in another terminal):"
echo "   cd frontend && npm run dev"
echo ""
echo "3. Sign in with Google OAuth (creates your real user account)"
echo ""
echo "4. Set your role to teacher:"
echo "   ./scripts/make_teacher.sh your@email.com"
echo ""
echo "5. Refresh the webapp to see teacher features!"
echo ""
echo "Note: Test data includes:"
echo "  - 1 teacher (teacher@example.com)"
echo "  - 3 students"
echo "  - 2 groups with join codes"
echo "  - Sample messages"
echo ""
echo "These are for backend testing only. For the webapp, use Google OAuth."
echo "========================================="
