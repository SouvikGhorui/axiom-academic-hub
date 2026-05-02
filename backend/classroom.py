from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

async def fetch_classroom_courses(refresh_token: str, client_id: str, client_secret: str):
    """
    Fetches the active courses for the authenticated user from Google Classroom.
    """
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token"
    )
    
    service = build('classroom', 'v1', credentials=creds)
    results = service.courses().list(studentId='me', courseStates=['ACTIVE']).execute()
    courses = results.get('courses', [])
    return courses

async def fetch_course_assignments(course_id: str, refresh_token: str, client_id: str, client_secret: str):
    """
    Fetches the assignments (courseWork) for a given course.
    """
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token"
    )
    
    service = build('classroom', 'v1', credentials=creds)
    results = service.courses().courseWork().list(courseId=course_id).execute()
    course_work = results.get('courseWork', [])
    return course_work
