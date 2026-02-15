#!/usr/bin/env python3
"""
Set user role in the database

This script allows you to change a user's role directly in the database.
Useful for testing and setting up teacher accounts.

Usage:
    python scripts/set_user_role.py <email> <role>
    
Examples:
    python scripts/set_user_role.py user@example.com teacher
    python scripts/set_user_role.py student@example.com student
"""

import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.insert(0, backend_dir)

# Change to backend directory to ensure database is found
os.chdir(backend_dir)

from database import SessionLocal, User


def set_user_role(email: str, role: str):
    """Set the role for a user by email"""
    
    if role not in ["teacher", "student"]:
        print(f"❌ Error: Invalid role '{role}'. Must be 'teacher' or 'student'.")
        return False
    
    db = SessionLocal()
    
    try:
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ Error: User with email '{email}' not found.")
            print("\nAvailable users:")
            all_users = db.query(User).all()
            if all_users:
                for u in all_users:
                    print(f"  - {u.email} (ID: {u.id}, Current role: {u.role})")
            else:
                print("  (No users in database yet)")
            return False
        
        # Update role
        old_role = user.role
        user.role = role
        db.commit()
        
        print(f"✅ Successfully updated user role:")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.name}")
        print(f"   Role: {old_role} → {role}")
        print(f"   User ID: {user.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating user role: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Main entry point"""
    
    if len(sys.argv) != 3:
        print("Usage: python scripts/set_user_role.py <email> <role>")
        print("\nExamples:")
        print("  python scripts/set_user_role.py user@example.com teacher")
        print("  python scripts/set_user_role.py student@example.com student")
        print("\nRoles: teacher, student")
        sys.exit(1)
    
    email = sys.argv[1]
    role = sys.argv[2]
    
    success = set_user_role(email, role)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
