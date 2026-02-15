# Helper Scripts

This directory contains utility scripts to help you set up and manage the Student Progress Monitor application.

## Requirements Verification

### verify_requirements.py

Automated verification script that checks the implementation against all assignment requirements.

**Usage:**
```bash
python scripts/verify_requirements.py
```

**What it checks:**
- ✅ Authentication & RBAC (Google OAuth, roles)
- ✅ Group management (create, view)
- ✅ QR code generation and joining
- ✅ Real-time chat (WebSocket)
- ✅ Progress tracking
- ✅ Teacher dashboard features
- ✅ Technology stack
- ✅ Bonus features (math rendering, voice input, etc.)
- ✅ Helper scripts and documentation

**Output:**
- Console output with color-coded results
- JSON file: `verification_results.json`
- Detailed tracking: `REQUIREMENTS_TRACKING.md`

**Example:**
```bash
$ python scripts/verify_requirements.py

======================================================================
                   REQUIREMENTS VERIFICATION REPORT                   
======================================================================

✅ 1. Authentication & RBAC
   Status: PASS
   Checks passed: 6/6

⚠️ 2. Progress Tracking
   Status: PARTIAL (62%)
   Basic checks passed: 5/5
   Advanced features: 0/3

Overall Completion: 58.7%
```

See [REQUIREMENTS_TRACKING.md](../REQUIREMENTS_TRACKING.md) for detailed analysis.

## Quick Demo

### quick_demo.sh

Run a complete demo setup with test data.

**Usage:**
```bash
./scripts/quick_demo.sh
```

This script will:
1. Create test users, groups, and messages using `backend/create_test_data.py`
2. Show you how to use the user management scripts
3. Display next steps to start the application

Perfect for quickly exploring the application or running a demo.

## User Management Scripts

### list_users.py

List all registered users in the database with their roles and IDs.

**Usage:**
```bash
python scripts/list_users.py
```

**Example Output:**
```
================================================================================
Total users: 3
================================================================================

1. John Doe
   Email: john@example.com
   Role: teacher
   User ID: 1
   Created: 2024-01-15 10:30:00

2. Jane Smith
   Email: jane@example.com
   Role: student
   User ID: 2
   Created: 2024-01-15 11:00:00

================================================================================
Summary: 1 teacher(s), 2 student(s)
================================================================================
```

### set_user_role.py

Change a user's role by email address.

**Usage:**
```bash
python scripts/set_user_role.py <email> <role>
```

**Arguments:**
- `email`: User's email address (as registered via Google OAuth)
- `role`: Either "teacher" or "student"

**Examples:**
```bash
# Set user to teacher
python scripts/set_user_role.py john@example.com teacher

# Set user to student
python scripts/set_user_role.py jane@example.com student
```

**Example Output:**
```
✅ Successfully updated user role:
   Email: john@example.com
   Name: John Doe
   Role: student → teacher
   User ID: 1
```

### make_teacher.sh

Quick shell script to set a user's role to "teacher".

**Usage:**
```bash
./scripts/make_teacher.sh <email>
```

**Example:**
```bash
./scripts/make_teacher.sh your@email.com
```

This is a convenience wrapper around `set_user_role.py` that specifically sets the role to "teacher".

## Typical Workflow

1. **Start the application** (backend and frontend)

2. **Sign in with Google OAuth** to create your user account

3. **List users to find your email:**
   ```bash
   python scripts/list_users.py
   ```

4. **Set your role to teacher:**
   ```bash
   ./scripts/make_teacher.sh your@email.com
   ```

5. **Refresh the webapp** (F5 or Cmd+R) - you should now see teacher features (Create Group button, etc.)

6. **No logout/login needed** - just refresh!

## Verifying in the Webapp

After running any role-changing script:

1. **Simply refresh your browser** (F5 or Cmd+R)
2. The app fetches fresh user data from the backend
3. You'll see the updated dashboard immediately

**What you'll see:**
- **Student role**: "Student Dashboard" title, no create button
- **Teacher role**: "Teacher Dashboard" title, "Create New Group" button visible

For detailed visual guide, see [WEBAPP_VERIFICATION.md](../WEBAPP_VERIFICATION.md)

## Notes

- Users are created when they first sign in with Google OAuth
- All users default to "student" role
- You must sign in at least once before you can change your role
- Changes take effect immediately - just refresh the page
- The backend must be running and the database must exist

## Backend Test Data

The backend also includes a test data generation script:

```bash
cd backend
python create_test_data.py
```

This creates sample users, groups, and messages for testing. Only works on a fresh database.
