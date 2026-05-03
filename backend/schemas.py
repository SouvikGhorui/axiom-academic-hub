from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from models import TaskType, TaskStatus, ConflictStatus

class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None
    section: Optional[str] = None
    room: Optional[str] = None
    external_id: Optional[str] = None
    is_active: bool = True

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: UUID
    user_id: UUID
    content_hash: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    task_type: Optional[TaskType] = None
    status: TaskStatus = TaskStatus.PENDING
    weight: Optional[float] = None
    max_points: Optional[float] = None
    external_id: Optional[str] = None

class TaskCreate(TaskBase):
    course_id: UUID

class TaskResponse(TaskBase):
    id: UUID
    course_id: UUID
    effort_estimate_hrs: Optional[float] = None
    priority_score: Optional[float] = None
    content_hash: Optional[str] = None
    last_priority_calc: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
