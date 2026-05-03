from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from database import get_db
from models import Course, User, OAuthToken
from schemas import CourseCreate, CourseResponse
import classroom as classroom_api
from dependencies import get_current_user

router = APIRouter(prefix="/courses", tags=["courses"])

@router.post("/", response_model=CourseResponse)
async def create_course(
    course: CourseCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_course = Course(**course.model_dump(), user_id=current_user.id)
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course

@router.get("/", response_model=List[CourseResponse])
async def get_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Course).where(Course.user_id == current_user.id))
    return result.scalars().all()

@router.post("/sync-classroom", tags=["sync"])
async def sync_classroom_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetches all active courses from Google Classroom and upserts them
    into the local database. Returns a summary of what was added/updated.
    """
    # Retrieve Google OAuth token from database
    result = await db.execute(
        select(OAuthToken)
        .where(OAuthToken.user_id == current_user.id)
        .where(OAuthToken.scope_key == "google_all")
    )
    token_record = result.scalars().first()
    
    if not token_record:
        raise HTTPException(status_code=401, detail="Google account not linked or session expired")

    try:
        creds = classroom_api.build_credentials(token_record.encrypted_refresh_token)
        gc_courses = await classroom_api.fetch_classroom_courses(creds)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Classroom API error: {e}")

    added = []
    updated = []

    for gc in gc_courses:
        gc_id = gc.get("id", "")
        gc_name = gc.get("name", "Unknown Course")
        gc_desc = gc.get("descriptionHeading") or gc.get("description") or ""
        gc_section = gc.get("section", "")
        display_name = f"{gc_name}" + (f" - {gc_section}" if gc_section else "")

        # Check if this course already exists by external_id and user_id
        result = await db.execute(
            select(Course)
            .where(Course.external_id == gc_id)
            .where(Course.user_id == current_user.id)
        )
        existing = result.scalars().first()

        from sync import compute_course_hash, has_changed
        new_hash = compute_course_hash(gc)

        if existing:
            if has_changed(existing.content_hash, new_hash):
                existing.name = display_name
                existing.description = gc_desc
                existing.section = gc_section
                existing.is_active = True
                existing.content_hash = new_hash
                updated.append(display_name)
        else:
            new_course = Course(
                external_id=gc_id,
                user_id=current_user.id,
                name=display_name,
                description=gc_desc,
                section=gc_section,
                is_active=True,
                content_hash=new_hash
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
