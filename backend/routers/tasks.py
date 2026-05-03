from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from database import get_db
from models import Task, Course, User
from schemas import TaskCreate, TaskResponse
from dependencies import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify course belongs to user
    course_result = await db.execute(select(Course).where(Course.id == task.course_id).where(Course.user_id == current_user.id))
    if not course_result.scalars().first():
        raise HTTPException(status_code=403, detail="Course not found or access denied")
        
    db_task = Task(**task.model_dump())
    from llm import estimate_effort
    from prioritization import calculate_priority_score
    from datetime import datetime
    
    db_task.effort_estimate_hrs = await estimate_effort(
        title=db_task.title, 
        description=db_task.description, 
        task_type=db_task.task_type.value if db_task.task_type else "UNKNOWN"
    )
    
    now = datetime.utcnow()
    db_task.priority_score = calculate_priority_score(
        due_date=db_task.due_date,
        task_type=db_task.task_type.value if db_task.task_type else "UNKNOWN",
        effort_hrs=db_task.effort_estimate_hrs,
        weight_pct=db_task.weight,
        now=now
    )
    db_task.last_priority_calc = now
    
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Task)
        .join(Course)
        .where(Course.user_id == current_user.id)
    )
    return result.scalars().all()
