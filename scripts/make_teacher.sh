#!/bin/bash
# Quick script to set user role to teacher
# Usage: ./scripts/make_teacher.sh <email>

if [ -z "$1" ]; then
    echo "Usage: ./scripts/make_teacher.sh <email>"
    echo ""
    echo "Example:"
    echo "  ./scripts/make_teacher.sh your@email.com"
    exit 1
fi

EMAIL="$1"

echo "Setting role to 'teacher' for: $EMAIL"
echo ""

cd "$(dirname "$0")/.."
python3 scripts/set_user_role.py "$EMAIL" teacher
