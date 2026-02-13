# Debug Instructions for 401 Unauthorized Issue

## Problem
After successful Google OAuth callback, requests to `/auth/me` return 401 Unauthorized, causing the user to be redirected back to the login page.

## Debug Logging Added

### Frontend Console Logs
When you run the application and go through the OAuth flow, check the browser console for these logs:

1. **AuthCallback Component:**
   - `[AuthCallback] Token from URL: ...` - Shows if token is being extracted from URL
   - `[AuthCallback] Calling login with token...` - Confirms login is being called
   - `[AuthCallback] Login result: true/false` - Shows if login succeeded
   - `[AuthCallback] Navigating to /dashboard` or `[AuthCallback] Login failed, navigating to /login`

2. **useAuth Hook:**
   - `[useAuth] Loading user with token: ...` - Shows the token being used
   - `[useAuth] Token test result: ...` - Shows if token can be transmitted
   - `[useAuth] User loaded successfully: ...` - Shows user data if successful
   - `[useAuth] Failed to load user: ...` - Shows error if failed

3. **ApiService:**
   - `[ApiService] Adding Authorization header with token: ...` - Confirms header is being set
   - `[ApiService] No token available for Authorization header` - Warning if no token

### Backend Logs
Check the backend terminal for these logs:

1. **Google Callback:**
   - `[google_callback] User authenticated via Google: {email}`
   - `[google_callback] Creating new user:` or `[google_callback] Existing user found:`
   - `[google_callback] Created access token for user {id}: {token}...`
   - `[google_callback] Redirecting to: ...`

2. **Token Verification:**
   - `[verify_token] Attempting to verify token: ...`
   - `[verify_token] Using SECRET_KEY: ... and ALGORITHM: ...`
   - `[verify_token] Token verified successfully, payload: ...` OR
   - `[verify_token] JWT verification error: ...`

3. **User Authentication:**
   - `[get_current_user] Received token: ...`
   - `[get_current_user] Token verification result: ...`
   - `[get_current_user] Extracted user_id from payload: ...`
   - `[get_current_user] User authenticated successfully: {email}` OR
   - `[get_current_user] Token verification failed - payload is None` OR
   - `[get_current_user] No user_id in token payload` OR
   - `[get_current_user] User not found in database for user_id: ...`

4. **Test Endpoint:**
   - `[/auth/test-token] Authorization header: ...`
   - `[/auth/test-token] Extracted token: ...`

## Troubleshooting Steps

### 1. Verify Token is Being Extracted
Check frontend console for `[AuthCallback] Token from URL:`. If this shows "null", the token is not in the URL.

**Solution:** Check backend logs to ensure the redirect URL includes the token.

### 2. Verify Token is Being Sent
Check frontend console for `[ApiService] Adding Authorization header with token:`. If you see "No token available", the token is not being passed to the API.

**Solution:** Check that the token is being passed to `apiService.getCurrentUser(authToken)`.

### 3. Verify Token Format
The token test endpoint will show if the token is being transmitted correctly. Check the response from `/auth/test-token`.

**Expected:** `{"success": true, "payload": {"sub": 1, "exp": ...}}`

**If error:** Check what the error message says.

### 4. Verify Token Signature
Check backend logs for `[verify_token] JWT verification error:`. Common errors:

- **"Signature verification failed":** The SECRET_KEY used to create the token doesn't match the one used to verify it.
  - **Solution:** Ensure the backend wasn't restarted with a different SECRET_KEY between callback and /auth/me.
  
- **"Token is expired":** The token has expired.
  - **Solution:** Check ACCESS_TOKEN_EXPIRE_MINUTES in .env.
  
- **"Invalid token":** The token is malformed.
  - **Solution:** Check if the token is being corrupted during URL transmission.

### 5. Verify User Exists
Check backend logs for `[get_current_user] User not found in database for user_id:`.

**Solution:** Check the database to ensure the user was created successfully during the Google callback.

### 6. Check CORS
If you see CORS errors in the browser console, the backend CORS configuration might be incorrect.

**Solution:** Ensure `FRONTEND_URL` in backend/.env matches the frontend URL (http://localhost:3000).

### 7. Check SECRET_KEY
Ensure the SECRET_KEY in backend/.env is:
1. Set to a secure value (not the default "your-secret-key-change-in-production")
2. The same value between when the token is created (Google callback) and verified (/auth/me)

**To verify:** Check backend logs for `[verify_token] Using SECRET_KEY:` and ensure it's consistent.

## Common Issues and Solutions

### Issue: Token is null in URL
**Cause:** Google callback failed or redirect URL is incorrect.
**Solution:** Check backend logs for Google callback errors. Verify GOOGLE_REDIRECT_URI and FRONTEND_URL in backend/.env.

### Issue: Token verification fails with "Signature verification failed"
**Cause:** SECRET_KEY mismatch between token creation and verification.
**Solution:** Restart the backend and try again. Ensure SECRET_KEY in .env is not changing.

### Issue: Multiple /auth/me requests
**Cause:** React StrictMode causes components to render twice in development.
**Solution:** This is normal in development. The issue is why they return 401, not that there are multiple requests.

### Issue: Authorization header not being sent
**Cause:** Token not being passed to API methods.
**Solution:** Verify that all API calls pass the token parameter. The API service should auto-inject from localStorage as a fallback.

## Next Steps

After identifying the issue from the logs:
1. Remove the debug logging
2. Remove the test endpoint
3. Implement the actual fix
4. Test the auth flow again
