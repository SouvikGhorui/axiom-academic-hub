import os
import asyncio
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes needed for both Gmail and Classroom
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me',
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
]

TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')


def _get_credentials() -> Credentials:
    """
    Loads or refreshes OAuth 2.0 credentials.
    If existing token.json lacks classroom scopes, re-runs the auth flow.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}. Re-authenticating...")
                creds = None

        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    "Missing 'credentials.json'. Download your OAuth 2.0 Client ID "
                    "JSON from Google Cloud Console and place it in the backend directory."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def _sync_fetch_courses() -> list:
    """Synchronous: fetch all active courses for the authenticated student."""
    creds = _get_credentials()
    service = build('classroom', 'v1', credentials=creds)
    results = service.courses().list(studentId='me', courseStates=['ACTIVE']).execute()
    return results.get('courses', [])


def _sync_fetch_assignments(course_id: str) -> list:
    """Synchronous: fetch all courseWork for a given course."""
    creds = _get_credentials()
    service = build('classroom', 'v1', credentials=creds)
    results = service.courses().courseWork().list(courseId=course_id).execute()
    return results.get('courseWork', [])


def _sync_fetch_student_submissions(course_id: str, course_work_id: str) -> list:
    """Synchronous: fetch student submissions for a given assignment."""
    creds = _get_credentials()
    service = build('classroom', 'v1', credentials=creds)
    results = (
        service.courses()
        .courseWork()
        .studentSubmissions()
        .list(courseId=course_id, courseWorkId=course_work_id, userId='me')
        .execute()
    )
    return results.get('studentSubmissions', [])


# ── Async wrappers ────────────────────────────────────────────────────────────

async def fetch_classroom_courses() -> list:
    """Async: returns list of active Google Classroom courses for the current user."""
    return await asyncio.to_thread(_sync_fetch_courses)


async def fetch_course_assignments(course_id: str) -> list:
    """Async: returns list of assignments for a course."""
    return await asyncio.to_thread(_sync_fetch_assignments, course_id)


async def fetch_student_submissions(course_id: str, course_work_id: str) -> list:
    """Async: returns submission status for an assignment."""
    return await asyncio.to_thread(_sync_fetch_student_submissions, course_id, course_work_id)
