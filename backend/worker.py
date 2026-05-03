from celery import Celery
from celery.schedules import crontab
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "axiom",
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

celery_app.conf.beat_schedule = {
    "sync-all-users-every-15min": {
        "task": "worker.sync_all_users",
        "schedule": crontab(minute="*/15"),
    },
}

@celery_app.task
def sync_all_users():
    """Fan out one sync job per active user."""
    # In a fully integrated implementation, we would fetch all user IDs from DB
    # and enqueue a job for each. For now, this is a placeholder.
    pass

@celery_app.task(bind=True, max_retries=3)
def sync_user_classroom(self, user_id: str):
    print(f"Syncing Classroom for user_id={user_id}")
    try:
        # from sync import run_classroom_sync
        # run_classroom_sync(user_id) 
        recalculate_priorities.delay(user_id)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

@celery_app.task
def sync_user_gmail(user_id: str, history_id: str = None):
    print(f"Syncing Gmail for user_id={user_id}, history_id={history_id}")
    pass

@celery_app.task
def recalculate_priorities(user_id: str):
    import asyncio
    from database import AsyncSessionLocal
    from sync import run_priority_recalc
    
    async def async_recalc():
        async with AsyncSessionLocal() as session:
            await run_priority_recalc(user_id, session)
            
    asyncio.run(async_recalc())

@celery_app.task
def push_calendar_updates(user_id: str, task_id: str):
    print(f"Pushing calendar updates for user={user_id}, task={task_id}")
    pass
