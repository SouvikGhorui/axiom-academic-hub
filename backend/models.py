import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, Float, DateTime, Enum, ForeignKey, Uuid

from sqlalchemy.orm import relationship
import enum
from database import Base

class TaskType(str, enum.Enum):
    EXAM = "EXAM"
    HOMEWORK = "HOMEWORK"
    READING = "READING"
    PROJECT = "PROJECT"

class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class ConflictStatus(str, enum.Enum):
    NONE = "NONE"
    PENDING_RESOLUTION = "PENDING_RESOLUTION"
    OVERRIDDEN = "OVERRIDDEN"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    google_refresh_token = Column(String) # Should be encrypted in practice
    created_at = Column(DateTime, default=datetime.utcnow)

    courses = relationship("Course", back_populates="user")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"))
    external_id = Column(String, index=True) # Google Classroom Course ID
    name = Column(String, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="courses")
    tasks = relationship("Task", back_populates="course")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(Uuid(as_uuid=True), ForeignKey("courses.id"))
    external_id = Column(String, index=True) # Google Classroom Assignment ID
    title = Column(String, nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    task_type = Column(Enum(TaskType))
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    effort_estimate_hrs = Column(Float)
    priority_score = Column(Float)
    weight = Column(Float)

    course = relationship("Course", back_populates="tasks")
    study_blocks = relationship("StudyBlock", back_populates="task")

class StudyBlock(Base):
    __tablename__ = "study_blocks"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(Uuid(as_uuid=True), ForeignKey("tasks.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    synced_to_calendar = Column(Boolean, default=False)
    calendar_event_id = Column(String)
    conflict_status = Column(Enum(ConflictStatus), default=ConflictStatus.NONE)

    task = relationship("Task", back_populates="study_blocks")
