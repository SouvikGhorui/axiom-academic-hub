import os
import asyncio
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_utils import build_credentials

def _sync_fetch_courses(creds: Credentials) -> list:
    """Synchronous: fetch all active courses for the authenticated student."""
    service = build('classroom', 'v1', credentials=creds)
    results = service.courses().list(studentId='me', courseStates=['ACTIVE']).execute()
    return results.get('courses', [])


def _sync_fetch_assignments(creds: Credentials, course_id: str) -> list:
    """Synchronous: fetch all courseWork for a given course."""
    service = build('classroom', 'v1', credentials=creds)
    results = service.courses().courseWork().list(courseId=course_id).execute()
    return results.get('courseWork', [])


def _sync_fetch_student_submissions(creds: Credentials, course_id: str, course_work_id: str) -> list:
    """Synchronous: fetch student submissions for a given assignment."""
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

async def fetch_classroom_courses(creds: Credentials) -> list:
    """Async: returns list of active Google Classroom courses for the current user."""
    return await asyncio.to_thread(_sync_fetch_courses, creds)


async def fetch_course_assignments(creds: Credentials, course_id: str) -> list:
    """Async: returns list of assignments for a course."""
    return await asyncio.to_thread(_sync_fetch_assignments, creds, course_id)


async def fetch_student_submissions(creds: Credentials, course_id: str, course_work_id: str) -> list:
    """Async: returns submission status for an assignment."""
    return await asyncio.to_thread(_sync_fetch_student_submissions, creds, course_id, course_work_id)
