#!/usr/bin/env python3
"""
Test data generator for Student Progress Monitor

This script creates sample users and groups for testing purposes.
Run after starting the backend at least once to create the database.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, User, Group, GroupMembership, Message, init_db
from routers.groups import generate_join_code

def create_test_data():
    """Create sample test data"""
    
    # Initialize database
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"Database already has {existing_users} users. Skipping test data creation.")
            print("Delete student_monitor.db to start fresh.")
            return
        
        # Create teacher
        teacher = User(
            email="teacher@example.com",
            name="Professor Smith",
            role="teacher",
            google_id="teacher_google_123"
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        print(f"✅ Created teacher: {teacher.name} (ID: {teacher.id})")
        
        # Create students
        students = []
        student_names = ["Alice Johnson", "Bob Williams", "Charlie Brown"]
        for i, name in enumerate(student_names):
            student = User(
                email=f"student{i+1}@example.com",
                name=name,
                role="student",
                google_id=f"student_google_{i+1}"
            )
            db.add(student)
            students.append(student)
        
        db.commit()
        for student in students:
            db.refresh(student)
            print(f"✅ Created student: {student.name} (ID: {student.id})")
        
        # Create groups
        groups_data = [
            {
                "name": "A2 – Quadratic Equations 1",
                "goal": "Solve independently 3 different quadratic equations ax² + bx + c using the discriminant"
            },
            {
                "name": "B1 – Introduction to Calculus",
                "goal": "Understand and apply the concept of derivatives to solve basic problems"
            }
        ]
        
        groups = []
        for group_data in groups_data:
            group = Group(
                name=group_data["name"],
                goal_description=group_data["goal"],
                teacher_id=teacher.id,
                join_code=generate_join_code()
            )
            db.add(group)
            groups.append(group)
        
        db.commit()
        for group in groups:
            db.refresh(group)
            print(f"✅ Created group: {group.name} (ID: {group.id}, Join Code: {group.join_code})")
        
        # Add students to first group
        for student in students[:2]:  # Only first 2 students
            membership = GroupMembership(
                user_id=student.id,
                group_id=groups[0].id,
                device_id=f"device_{student.id}"
            )
            db.add(membership)
        
        db.commit()
        print(f"✅ Added {len(students[:2])} students to group: {groups[0].name}")
        
        # Add some sample messages
        messages_data = [
            (students[0].id, "Hi! I'm working on the first equation: x² - 5x + 6 = 0"),
            (students[0].id, "Using the discriminant: b² - 4ac = 25 - 24 = 1"),
            (students[0].id, "So x = (5 ± 1) / 2, which gives x = 3 or x = 2"),
            (students[1].id, "I'm starting with 2x² + 3x - 2 = 0"),
            (students[1].id, "Discriminant = 9 + 16 = 25, so x = (-3 ± 5) / 4"),
        ]
        
        for user_id, content in messages_data:
            message = Message(
                content=content,
                user_id=user_id,
                group_id=groups[0].id
            )
            db.add(message)
        
        db.commit()
        print(f"✅ Added {len(messages_data)} sample messages")
        
        print("\n" + "="*60)
        print("Test data created successfully!")
        print("="*60)
        print("\nLogin credentials (for testing with custom auth):")
        print(f"Teacher: {teacher.email}")
        for student in students:
            print(f"Student: {student.email}")
        print("\nGroup join codes:")
        for group in groups:
            print(f"  {group.name}: {group.join_code}")
        print("\nNote: In production, use Google OAuth to sign in.")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()
