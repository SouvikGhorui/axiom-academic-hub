import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes needed for Gmail, Classroom, and Calendar
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me',
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
    'https://www.googleapis.com/auth/calendar',
    'openid',
    'email',
    'profile'
]

def build_credentials(refresh_token: str) -> Credentials:
    """Builds Google OAuth2 Credentials from a refresh token."""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    if not client_id or client_secret is None:
        raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment")

    creds = Credentials(
        token=None,  # Will be populated on refresh
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES
    )
    
    # Force a refresh to get a valid access token
    creds.refresh(Request())
    return creds
