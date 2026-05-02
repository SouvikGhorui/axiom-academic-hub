from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "academic_hub_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task
def sync_classroom_data(user_id: str):
    """
    Background task to sync Google Classroom data for a specific user.
    """
    # In a real scenario, this would:
    # 1. Fetch user's refresh token from DB.
    # 2. Call classroom.fetch_classroom_courses
    # 3. Call classroom.fetch_course_assignments for each course.
    # 4. Save new courses/tasks to DB.
    # 5. For each new task, invoke LLM to estimate effort.
    print(f"Syncing Google Classroom data for user {user_id}...")
    return f"Success: Sync completed for {user_id}"
