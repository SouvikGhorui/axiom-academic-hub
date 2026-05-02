from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from database import get_db
from models import Course
from schemas import CourseCreate, CourseResponse

router = APIRouter(prefix="/courses", tags=["courses"])

@router.post("/", response_model=CourseResponse)
async def create_course(course: CourseCreate, db: AsyncSession = Depends(get_db)):
    # Assuming user_id is injected from auth in the future. For now, we mock it.
    import uuid
    # Usually this comes from the authenticated user
    mock_user_id = uuid.uuid4() 
    db_course = Course(**course.model_dump(), user_id=mock_user_id)
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course

@router.get("/", response_model=List[CourseResponse])
async def get_courses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course))
    return result.scalars().all()
