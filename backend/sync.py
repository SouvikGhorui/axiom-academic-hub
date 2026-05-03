import hashlib
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Task, TaskStatus, Course, SyncState

def compute_task_hash(external_data: dict) -> str:
    """Deterministic hash of the fields that matter for priority/calendar."""
    fields = {
        "title": external_data.get("title", ""),
        "due_date": external_data.get("dueDate", {}),
        "max_points": external_data.get("maxPoints", 0),
        "description": external_data.get("description", ""),
        "state": external_data.get("state", ""),
    }
    canonical = json.dumps(fields, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()

def compute_course_hash(external_data: dict) -> str:
    """Deterministic hash of course fields."""
    fields = {
        "name": external_data.get("name", ""),
        "description": external_data.get("descriptionHeading", "") or external_data.get("description", ""),
        "section": external_data.get("section", "")
    }
    canonical = json.dumps(fields, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()

def has_changed(stored_hash: str | None, new_hash: str) -> bool:
    return stored_hash != new_hash

async def get_sync_state(db: AsyncSession, user_id: str, service: str):
    result = await db.execute(
        select(SyncState)
        .where(SyncState.user_id == user_id)
        .where(SyncState.service == service)
    )
    return result.scalars().first()

async def upsert_sync_state(db: AsyncSession, user_id: str, service: str, sync_token: str = None, history_id: str = None):
    sync_state = await get_sync_state(db, user_id, service)
    if sync_state:
        if sync_token:
            sync_state.sync_token = sync_token
        if history_id:
            sync_state.history_id = history_id
        sync_state.last_synced_at = datetime.utcnow()
    else:
        new_state = SyncState(
            user_id=user_id,
            service=service,
            sync_token=sync_token,
            history_id=history_id,
            last_synced_at=datetime.utcnow()
        )
        db.add(new_state)
    await db.commit()

async def run_priority_recalc(user_id: str, db: AsyncSession):
    from prioritization import calculate_priority_score
    
    result = await db.execute(
        select(Task)
        .join(Course)
        .where(Course.user_id == user_id)
        .where(Task.status != TaskStatus.COMPLETED)
    )
    tasks = result.scalars().all()
    now = datetime.utcnow()

    for task in tasks:
        task.priority_score = calculate_priority_score(
            due_date=task.due_date,
            task_type=task.task_type.value if task.task_type else "HOMEWORK",
            effort_hrs=task.effort_estimate_hrs or 2.0,
            weight_pct=task.weight,
            now=now,
        )
        task.last_priority_calc = now

    await db.commit()
