"""
Firebase Admin SDK wrapper.
Provides: token verification, Firestore user_link CRUD.

Firestore Document Schema:
  Collection: user_links
  Document ID: <google_uid>  (from Firebase Auth)
  Fields:
    staff_no: str           # Staff number from SQLite users table
    mobile: str             # Mobile number entered during setup
    is_admin: bool          # True if email in ADMIN_EMAILS whitelist
    linked_email: str       # Google account email address
    created_at: Timestamp   # Firestore server timestamp

Lazy initialization: Firebase Admin SDK is initialized on first call.
This avoids requiring the service account file at import time.
"""
import os
from typing import Optional

import firebase_admin
from firebase_admin import credentials, auth, firestore
from config import FIREBASE

_initialized = False
_firestore_db = None


def _ensure_initialized():
    """Initialize Firebase Admin SDK on first use. Raises RuntimeError if
    service account file is missing."""
    global _initialized, _firestore_db
    if _initialized:
        return _firestore_db

    sa_path = FIREBASE.get("service_account_path", "firebase-service-account.json")
    if not os.path.exists(sa_path):
        raise RuntimeError(
            f"Firebase service account not found at {sa_path}. "
            "Download from Firebase Console -> Project Settings -> Service Accounts"
        )
    cred = credentials.Certificate(sa_path)
    firebase_admin.initialize_app(cred)
    _firestore_db = firestore.client()
    _initialized = True
    return _firestore_db


def verify_google_token(id_token: str) -> dict:
    """Verify a Firebase ID token and return decoded claims.

    Returns dict with keys: uid, email, name, etc.
    Raises ValueError if the token is invalid, expired, or malformed.
    """
    _ensure_initialized()
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        raise ValueError(f"Invalid Firebase token: {e}")


def get_user_link(google_uid: str) -> Optional[dict]:
    """Fetch user_link document from Firestore user_links collection.

    Returns the document data dict, or None if not found.
    """
    db = _ensure_initialized()
    doc = db.collection("user_links").document(google_uid).get()
    return doc.to_dict() if doc.exists else None


def save_user_link(
    google_uid: str,
    linked_email: str,
    staff_no: str,
    mobile: str,
    is_admin: bool,
) -> None:
    """Create or update a user_link document in Firestore.

    Args:
        google_uid: Firebase Auth UID (used as document ID)
        linked_email: Google account email address
        staff_no: Employee staff number
        mobile: Mobile phone number
        is_admin: Whether this user has admin privileges
    """
    db = _ensure_initialized()
    db.collection("user_links").document(google_uid).set({
        "staff_no": staff_no,
        "mobile": mobile,
        "is_admin": is_admin,
        "linked_email": linked_email,
        "created_at": firestore.SERVER_TIMESTAMP,
    })


def delete_user_link(google_uid: str) -> None:
    """Remove a user_link document from Firestore (unlink Google account)."""
    db = _ensure_initialized()
    db.collection("user_links").document(google_uid).delete()


def list_all_user_links() -> list[dict]:
    """Fetch all user_link documents (admin function).

    Returns a list of document data dicts, each including the google_uid field.
    """
    db = _ensure_initialized()
    docs = db.collection("user_links").stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        if data:
            data["google_uid"] = doc.id
            results.append(data)
    return results
