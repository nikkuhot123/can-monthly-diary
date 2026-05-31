# Google Auth + Firebase + Role-Based Access Design

**Date:** 2026-05-31
**Status:** Draft
**Author:** System Design

## Overview

Add Google OAuth login via Firebase Authentication to the Audit Diary System. Replace the existing staff_no/password login with Google-only authentication. Implement role-based access control: regular users can only view/edit calendar, view holidays, and view generated Excel reports. Admin (staff 861198 / whitelisted email) has full access.

## Architecture

```
Browser (Firebase JS SDK) ──① Google OAuth──▶ FastAPI Backend
                                                    │
                                             ② Verify token
                                         (Firebase Admin SDK)
                                                    │
                                         ┌──────────┴──────────┐
                                         ▼                     ▼
                                    Firebase              SQLite
                                    ────────              ──────
                                    Authentication        users
                                    Firestore             monthly_diaries
                                    └ user_links/         attendance_records
                                      {google_uid,        travel_legs,
                                       email,             hotel_stays,
                                       staff_no,          local_conveyance,
                                       mobile,            other_expenses,
                                       is_admin}          bills
                                                           holidays
```

### Data Flow

1. User clicks "Sign in with Google" → Firebase JS SDK handles OAuth popup
2. Backend receives Firebase ID token → verifies via Firebase Admin SDK
3. Backend queries Firestore `user_links/{google_uid}` for linked staff_no
4. If linked: create JWT session → redirect to dashboard
5. If not linked: show setup form → user enters staff_no + mobile → save to Firestore → create JWT
6. All subsequent requests use existing JWT cookie (no change to middleware)
7. Route-level permission gates check `is_admin` from JWT payload

## Firebase Setup

### A. Create Firebase Project
1. Go to https://console.firebase.google.com
2. Click "Add project" → name it (e.g., "Audit-Diary")
3. Disable Google Analytics → Create project

### B. Enable Authentication
1. Authentication → Sign-in method → Enable Google provider
2. Add admin email as support email
3. Note the Web client ID and Web client secret

### C. Register Web App
1. Project Settings → General → Your apps → Add app → Web
2. Name: "Audit-Diary-Web"
3. Copy the `firebaseConfig` object

### D. Enable Firestore
1. Firestore Database → Create database
2. Start in test mode → choose region (e.g., `asia-south1`)

### E. Service Account
1. Project Settings → Service accounts → Generate new private key
2. Save as `firebase-service-account.json` in project root

### F. Firestore Security Rules
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /user_links/{google_uid} {
      allow read, write: if request.auth != null
                         && request.auth.uid == google_uid;
    }
  }
}
```

## Firestore Document Structure

```
Collection: user_links
Document ID: <google_uid>
{
  google_uid: "abc123...",
  google_email: "user@gmail.com",
  staff_no: "12345",
  mobile: "9876543210",
  is_admin: false,
  created_at: <server_timestamp>,
  linked_at: <server_timestamp>
}
```

## Configuration

### `config.py` additions
```python
FIREBASE = {
    "api_key": os.getenv("FIREBASE_API_KEY", ""),
    "auth_domain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
    "project_id": os.getenv("FIREBASE_PROJECT_ID", ""),
    "storage_bucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
    "messaging_sender_id": os.getenv("FIREBASE_MSG_SENDER_ID", ""),
    "app_id": os.getenv("FIREBASE_APP_ID", ""),
    "service_account_path": "firebase-service-account.json",
}
ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "admin@gmail.com").split(",")
```

### `.env` additions
```
FIREBASE_API_KEY=AIza...
FIREBASE_AUTH_DOMAIN=audit-diary.firebaseapp.com
FIREBASE_PROJECT_ID=audit-diary
FIREBASE_STORAGE_BUCKET=audit-diary.appspot.com
FIREBASE_MSG_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456789:web:abc...
ADMIN_EMAILS=admin@gmail.com
```

### `.gitignore` additions
```
firebase-service-account.json
uploads/
```

## Files to Create/Modify

### New Files

| File | Purpose |
|------|---------|
| `services/firebase_service.py` | Firebase Admin SDK initialization, token verification, Firestore queries |
| `templates/setup_account.html` | First-time Google login → staff_no + mobile form |
| `firebase-service-account.json` | Firebase service account private key (gitignored) |

### Modified Files

| File | Changes |
|------|---------|
| `config.py` | Add Firebase config + ADMIN_EMAILS |
| `routers/auth.py` | Replace staff_no/password with Google-only auth |
| `routers/attendance.py` | Gate delete + upload-whatsapp routes to admin only |
| `routers/travel.py` | Add `admin_required` dependency to all routes |
| `routers/hotel.py` | Add `admin_required` dependency to all routes |
| `routers/local.py` | Add `admin_required` dependency to all routes |
| `routers/other.py` | Add `admin_required` dependency to all routes |
| `routers/bills.py` | Add `admin_required` dependency to all routes |
| `routers/upload_bill.py` | Add `admin_required` dependency |
| `routers/admin.py` | Add user linking management view |
| `templates/base.html` | Hide navigation items based on role |
| `templates/login.html` | Replace form with Google Sign-In button |
| `templates/calendar.html` | Conditional admin-only action buttons |

## Auth Routes (New Flow)

### `POST /auth/google-login`
1. Accept `id_token` from Firebase client SDK
2. Verify with Firebase Admin SDK → get `google_uid` + email
3. Query Firestore `user_links/{google_uid}`:
   - **If found**: Create JWT session, `is_admin` from Firestore data → redirect to dashboard
   - **If not found**: Return a temporary token → frontend shows setup page
4. Admin check: if `google_email` is in `ADMIN_EMAILS`, set `is_admin = True` (even at setup stage)

### `POST /auth/google-setup`
1. Accept `temp_token` (Google session), `staff_no`, `mobile`
2. Verify Firebase ID token
3. Look up `staff_no` in SQLite `users` table
   - **If not found**: Return error "Account not found. Please contact your administrator to create your account first."
   - **If found but mobile doesn't match**: Return warning "Staff number found but mobile does not match. Contact admin if this is your correct staff number." (Still allow linking with manual admin approval flag)
   - **If found and mobile matches**: Proceed normally
4. Check if email is in `ADMIN_EMAILS` → determine `is_admin`
5. Update SQLite `User.is_admin` for the matched staff_no
6. Save `user_link` document to Firestore
7. Create JWT session → redirect to dashboard

### `GET /auth/logout`
- Unchanged: clear JWT cookie

## JWT Payload
```json
{
  "user_id": 123,
  "staff_no": "12345",
  "is_admin": false,
  "exp": 1717000000
}
```

## Permission Gating

```python
def regular_user(request: Request, db: Session = Depends(get_db)):
    """Minimum authentication check - any authenticated user"""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=302, detail="Login required")
    return user

def admin_user(request: Request, db: Session = Depends(get_db)):
    """Admin-only check"""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=302, detail="Login required")
    # Check JWT payload for is_admin
    token = request.cookies.get("access_token")
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
```

## Permission Matrix

| Feature | Regular User | Admin |
|---------|:-----------:|:-----:|
| View Calendar | ✅ | ✅ |
| Add Attendance | ✅ | ✅ |
| Edit Attendance | ✅ | ✅ |
| Delete Attendance | ❌ | ✅ |
| View Holidays | ✅ | ✅ |
| Upload WhatsApp | ❌ | ✅ |
| Travel (all) | ❌ | ✅ |
| Hotel (all) | ❌ | ✅ |
| Local (all) | ❌ | ✅ |
| Other Expenses (all) | ❌ | ✅ |
| Bills (all) | ❌ | ✅ |
| View Preview/Excel | ✅ | ✅ |
| Admin Users | ❌ | ✅ |
| Admin All Diaries | ❌ | ✅ |

## Implementation Order

| Phase | Description | Dependencies |
|-------|-------------|-------------|
| 1 | Firebase project setup (manual) | None |
| 2 | `config.py` + `firebase_service.py` | Phase 1 |
| 3 | Rewrite `routers/auth.py` | Phase 2 |
| 4 | Create `templates/setup_account.html` | Phase 3 |
| 5 | Rewrite `templates/login.html` | Phase 3 |
| 6 | Gate non-admin routes in all routers | Phase 3 |
| 7 | Update `templates/base.html` navigation | Phase 6 |
| 8 | Update admin user linking UI | Phase 3 |
| 9 | Test full flow end-to-end | All |

## Security Considerations

1. Firebase ID tokens expire after 1 hour — JWT session cookie handles session persistence
2. Firestore rules restrict user_links access to the owning user
3. `ADMIN_EMAILS` whitelist is set via environment variable, not hardcoded
4. `firebase-service-account.json` must be added to `.gitignore`
5. All existing input validation remains intact
6. Route-level gating prevents unauthorized access even if a user navigates directly

## Cleanup

### Routes to remove after migration
- `POST /auth/login` — staff_no/password login (replaced by Google)
- `GET /auth/register` — registration page (users are created by admin)
- `POST /auth/register` — registration handler

### Templates to remove
- Old `login.html` form content (replaced by Google Sign-In button)

## Open Questions
1. What happens to existing staff_no/password user accounts after migration? (Answer: They continue existing in SQLite, just accessed via Google login instead of password)
2. Should the admin be able to manually link Google accounts for users? (Not in v1 — users self-link via the setup form)
3. Should there be a way for admin to unlink a Google account? (Yes — admin can delete a Firestore document via Firebase Console or future admin UI)
