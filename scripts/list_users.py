#!/usr/bin/env python3
"""
List all users in the database

This script displays all registered users with their roles and IDs.
Useful for seeing who has signed up and what roles they have.

Usage:
    python scripts/list_users.py
"""

import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.insert(0, backend_dir)

# Change to backend directory to ensure database is found
os.chdir(backend_dir)

from database import SessionLocal, User


def list_users():
    """List all users in the database"""
    
    db = SessionLocal()
    
    try:
        users = db.query(User).order_by(User.created_at).all()
        
        if not users:
            print("No users found in the database.")
            print("\nUsers are created when they first sign in with Google OAuth.")
            return
        
        print(f"\n{'='*80}")
        print(f"Total users: {len(users)}")
        print(f"{'='*80}\n")
        
        # Display users
        for i, user in enumerate(users, 1):
            print(f"{i}. {user.name}")
            print(f"   Email: {user.email}")
            print(f"   Role: {user.role}")
            print(f"   User ID: {user.id}")
            print(f"   Created: {user.created_at}")
            print()
        
        # Summary by role
        teachers = [u for u in users if u.role == "teacher"]
        students = [u for u in users if u.role == "student"]
        
        print(f"{'='*80}")
        print(f"Summary: {len(teachers)} teacher(s), {len(students)} student(s)")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    list_users()
