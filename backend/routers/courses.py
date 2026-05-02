from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import get_db
from models import Course
from schemas import CourseCreate, CourseResponse
import classroom as classroom_api

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/", response_model=CourseResponse)
async def create_course(course: CourseCreate, db: AsyncSession = Depends(get_db)):
    import uuid
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


@router.post("/sync-classroom", tags=["sync"])
async def sync_classroom_courses(db: AsyncSession = Depends(get_db)):
    """
    Fetches all active courses from Google Classroom and upserts them
    into the local database. Returns a summary of what was added/updated.
    """
    try:
        gc_courses = await classroom_api.fetch_classroom_courses()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Classroom API error: {e}")

    added = []
    updated = []

    for gc in gc_courses:
        gc_id = gc.get("id", "")
        gc_name = gc.get("name", "Unknown Course")
        gc_desc = gc.get("descriptionHeading") or gc.get("description") or ""
        gc_section = gc.get("section", "")
        display_name = f"{gc_name}" + (f" – {gc_section}" if gc_section else "")

        # Check if this course already exists by external_id
        result = await db.execute(select(Course).where(Course.external_id == gc_id))
        existing = result.scalars().first()

        if existing:
            existing.name = display_name
            existing.description = gc_desc
            existing.is_active = True
            updated.append(display_name)
        else:
            new_course = Course(
                external_id=gc_id,
                name=display_name,
                description=gc_desc,
                is_active=True,
            )
            db.add(new_course)
            added.append(display_name)

    await db.commit()

    return {
        "status": "ok",
        "added": added,
        "updated": updated,
        "total_from_classroom": len(gc_courses),
    }
