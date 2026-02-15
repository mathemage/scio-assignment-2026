# Webapp Role Verification Guide

This guide shows you exactly what to expect in the webapp when verifying role changes.

## Quick Summary

**After changing your role with a script, simply refresh your browser (F5) to see the changes.**

No logout/login required. No backend restart needed. Just refresh!

## Step-by-Step Visual Guide

### Step 1: Initial Sign-In (Student Role - Default)

When you first sign in with Google OAuth, you'll see:

```
┌─────────────────────────────────────────────┐
│ Student Dashboard                   Logout  │
│ Welcome, Your Name                          │
├─────────────────────────────────────────────┤
│                                             │
│   Your Groups                               │
│                                             │
│   You haven't joined any groups yet.        │
│   Scan a QR code from your teacher to       │
│   join a group!                             │
│                                             │
└─────────────────────────────────────────────┘
```

**Key Indicators:**
- Title: "Student Dashboard"
- No "Create New Group" button
- Message about scanning QR codes

### Step 2: Change Role Using Script

In your terminal:

```bash
$ ./scripts/make_teacher.sh your@email.com

Setting role to 'teacher' for: your@email.com

✅ Successfully updated user role:
   Email: your@email.com
   Name: Your Name
   Role: student → teacher
   User ID: 1
```

**Keep your browser window open** - don't logout!

### Step 3: Refresh Browser

Press F5 (Windows/Linux) or Cmd+R (Mac)

### Step 4: See Teacher Dashboard

After refresh, you'll now see:

```
┌─────────────────────────────────────────────┐
│ Teacher Dashboard                   Logout  │
│ Welcome, Your Name                          │
├─────────────────────────────────────────────┤
│                                             │
│  [+ Create New Group]                       │
│                                             │
│   Your Groups                               │
│                                             │
│   No groups yet. Create your first group    │
│   to get started!                           │
│                                             │
└─────────────────────────────────────────────┘
```

**Key Indicators:**
- Title: "Teacher Dashboard"
- "Create New Group" button is visible (blue button)
- Different empty state message

### Step 5: Test Teacher Features

Click "Create New Group" to verify it works:

```
┌─────────────────────────────────────────────┐
│ Teacher Dashboard                   Logout  │
│ Welcome, Your Name                          │
├─────────────────────────────────────────────┤
│                                             │
│  [Cancel]                                   │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ Create New Group                      │ │
│  │                                       │ │
│  │ Group Name                            │ │
│  │ [________________________]            │ │
│  │                                       │ │
│  │ Goal Description                      │ │
│  │ [________________________]            │ │
│  │ [________________________]            │ │
│  │                                       │ │
│  │ [Create Group]                        │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

If you can create a group, your teacher role is working!

## What's Happening Under the Hood

```
Browser                          Backend
   |                                |
   | 1. Page loads, reads token    |
   |    from localStorage          |
   |                                |
   | 2. GET /auth/me               |
   |------------------------------>|
   |                                |
   |                                | 3. Queries database
   |                                |    Returns user with
   |                                |    updated role
   |                                |
   | 4. Receives user data         |
   |<------------------------------|
   |    { role: "teacher" }         |
   |                                |
   | 5. React renders              |
   |    TeacherDashboard           |
   |    component                  |
   v                                v
```

## Common Visual Indicators

| Feature | Student Dashboard | Teacher Dashboard |
|---------|------------------|-------------------|
| Title | "Student Dashboard" | "Teacher Dashboard" |
| Create Button | ❌ Not visible | ✅ Visible (blue) |
| Empty State | "Scan QR code..." | "Create first group..." |
| Group Cards | Shows joined groups | Shows created groups |
| Group View | Read-only chat | Full monitoring + QR |

## Testing Checklist

After changing role and refreshing:

- [ ] Page title shows "Teacher Dashboard"
- [ ] "Create New Group" button is visible
- [ ] Can click button and see create form
- [ ] Can fill out form and create a group
- [ ] Group appears in "Your Groups" section
- [ ] Can click group to see QR code

## Troubleshooting Visual Issues

### Still Seeing Student Dashboard After Refresh?

1. **Check the browser console:**
   - F12 → Console tab
   - Look for errors in red
   - Common issue: Network error fetching user data

2. **Verify the role in database:**
   ```bash
   python scripts/list_users.py
   ```
   Your email should show `Role: teacher`

3. **Hard refresh:**
   - Ctrl+F5 (Windows/Linux)
   - Cmd+Shift+R (Mac)
   - This clears the cache

4. **Check Network tab:**
   - F12 → Network tab
   - Refresh page
   - Find `me` request
   - Click it → Response tab
   - Should show `"role": "teacher"`

5. **Last resort - Clear everything:**
   ```javascript
   // In browser console (F12):
   localStorage.clear();
   // Then sign in again
   ```

## Pro Tips

1. **Keep DevTools open** during testing:
   - F12 → Console tab
   - You'll see any errors immediately

2. **Use two browsers** for testing both roles:
   - Chrome for teacher
   - Firefox for student
   - Test interactions in real-time

3. **Test the switch both ways:**
   - Student → Teacher → Student
   - Verify each transition works

4. **Bookmark the scripts:**
   - Keep terminal window with scripts handy
   - Quick switch for demos
