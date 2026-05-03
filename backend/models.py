import uuid
import hashlib
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Float, DateTime,
    Enum, ForeignKey, UniqueConstraint, Uuid
)
from sqlalchemy.orm import relationship
import enum
from database import Base

# ── Enums ─────────────────────────────────────────────────────────────────────

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

class CalendarEventType(str, enum.Enum):
    STUDY_BLOCK = "STUDY_BLOCK"
    DEADLINE = "DEADLINE"
    CLASS_SESSION = "CLASS_SESSION"

# ── Users ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    picture_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime)

    oauth_tokens = relationship("OAuthToken", back_populates="user", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="user", cascade="all, delete-orphan")
    sync_states = relationship("SyncState", back_populates="user", cascade="all, delete-orphan")

# ── OAuth Tokens ──────────────────────────────────────────────────────────────

class OAuthToken(Base):
    __tablename__ = "oauth_tokens"
    __table_args__ = (UniqueConstraint("user_id", "scope_key"),)

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    scope_key = Column(String, nullable=False)
    # Store encrypted; decrypt in application layer using Fernet or AWS KMS
    encrypted_refresh_token = Column(Text, nullable=False)
    access_token_hint = Column(String)
    token_expiry = Column(DateTime)
    granted_scopes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="oauth_tokens")

# ── Sync State ────────────────────────────────────────────────────────────────

class SyncState(Base):
    __tablename__ = "sync_states"
    __table_args__ = (UniqueConstraint("user_id", "service"),)

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    service = Column(String, nullable=False)
    sync_token = Column(String)
    history_id = Column(String)
    last_synced_at = Column(DateTime)
    webhook_expiry = Column(DateTime)
    webhook_channel_id = Column(String)

    user = relationship("User", back_populates="sync_states")

# ── Courses ───────────────────────────────────────────────────────────────────

class Course(Base):
    __tablename__ = "courses"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    external_id = Column(String, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    section = Column(String)
    room = Column(String)
    is_active = Column(Boolean, default=True)
    content_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="courses")
    tasks = relationship("Task", back_populates="course", cascade="all, delete-orphan")

# ── Tasks (Assignments) ───────────────────────────────────────────────────────

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(Uuid(as_uuid=True), ForeignKey("courses.id"), nullable=False, index=True)
    external_id = Column(String, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    task_type = Column(Enum(TaskType))
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    effort_estimate_hrs = Column(Float)
    priority_score = Column(Float, index=True)
    weight = Column(Float)
    max_points = Column(Float)
    content_hash = Column(String)
    last_priority_calc = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    course = relationship("Course", back_populates="tasks")
    study_blocks = relationship("StudyBlock", back_populates="task", cascade="all, delete-orphan")
    calendar_events = relationship("CalendarEvent", back_populates="task", cascade="all, delete-orphan")

# ── Study Blocks ──────────────────────────────────────────────────────────────

class StudyBlock(Base):
    __tablename__ = "study_blocks"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(Uuid(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    conflict_status = Column(Enum(ConflictStatus), default=ConflictStatus.NONE)

    task = relationship("Task", back_populates="study_blocks")
    calendar_event = relationship("CalendarEvent", back_populates="study_block", uselist=False)

# ── Calendar Events ───────────────────────────────────────────────────────────

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    task_id = Column(Uuid(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    study_block_id = Column(Uuid(as_uuid=True), ForeignKey("study_blocks.id"), nullable=True)
    google_event_id = Column(String, unique=True, nullable=False)
    calendar_id = Column(String, default="primary")
    event_type = Column(Enum(CalendarEventType))
    title = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    content_hash = Column(String)
    last_synced_at = Column(DateTime)
    is_deleted = Column(Boolean, default=False)

    task = relationship("Task", back_populates="calendar_events")
    study_block = relationship("StudyBlock", back_populates="calendar_event")
