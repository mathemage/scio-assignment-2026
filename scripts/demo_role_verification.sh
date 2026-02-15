#!/bin/bash
set -e  # Exit on any error

# Demo script showing role verification in action

echo "========================================="
echo "Role Verification Demo"
echo "========================================="
echo ""

# Change to repo root directory
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR/.." || {
    echo "Error: Failed to navigate to repository root"
    exit 1
}

if [ ! -f "backend/student_monitor.db" ]; then
    echo "Creating test data first..."
    cd backend
    python3 create_test_data.py
    cd ..
    echo ""
fi

echo "Current users in database:"
echo "----------------------------------------"
python3 scripts/list_users.py
echo ""

echo "========================================="
echo "Demo: Changing student1 to teacher"
echo "========================================="
echo ""

read -p "Press Enter to change student1@example.com to teacher role..."

python3 scripts/set_user_role.py student1@example.com teacher

echo ""
echo "========================================="
echo "Result: Updated users list"
echo "========================================="
echo ""

python3 scripts/list_users.py

echo ""
echo "========================================="
echo "What happens in the webapp:"
echo "========================================="
echo ""
echo "If student1@example.com was logged in:"
echo ""
echo "BEFORE (Student Role):"
echo "  - Page title: 'Student Dashboard'"
echo "  - No 'Create New Group' button"
echo "  - Can only join groups via QR code"
echo ""
echo "→ User runs: ./scripts/make_teacher.sh student1@example.com"
echo "→ User refreshes browser (F5)"
echo ""
echo "AFTER (Teacher Role):"
echo "  - Page title: 'Teacher Dashboard'"
echo "  - 'Create New Group' button visible"
echo "  - Can create groups and generate QR codes"
echo ""
echo "No logout/login required - just refresh!"
echo ""
echo "========================================="
echo "Demo: Changing back to student"
echo "========================================="
echo ""

read -p "Press Enter to change student1@example.com back to student role..."

python3 scripts/set_user_role.py student1@example.com student

echo ""
echo "Final users list:"
python3 scripts/list_users.py

echo ""
echo "========================================="
echo "Key Takeaways:"
echo "========================================="
echo ""
echo "✅ Role changes are immediate in database"
echo "✅ Just refresh browser to see changes (no re-login)"
echo "✅ Frontend fetches fresh user data on page load"
echo "✅ React renders appropriate dashboard based on role"
echo ""
echo "For detailed visual guide, see WEBAPP_VERIFICATION.md"
echo "========================================="
