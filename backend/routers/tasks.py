from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from database import get_db
from models import Task
from schemas import TaskCreate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    db_task = Task(**task.model_dump())
    from llm import estimate_effort
    from prioritization import calculate_priority_score
    
    db_task.effort_estimate_hrs = await estimate_effort(
        title=db_task.title, 
        description=db_task.description, 
        task_type=db_task.task_type.value if db_task.task_type else "UNKNOWN"
    )
    
    db_task.priority_score = calculate_priority_score(
        due_date=db_task.due_date,
        task_type=db_task.task_type.value if db_task.task_type else "UNKNOWN",
        effort_hrs=db_task.effort_estimate_hrs
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task))
    return result.scalars().all()
