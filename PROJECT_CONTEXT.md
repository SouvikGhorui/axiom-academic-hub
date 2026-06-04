# Axiom – Automated Academic Hub: Project Context Snapshot

This document provides a comprehensive overview of the **Axiom** project, including its architecture, tech stack, and core code logic. This is intended for AI assistants to understand the full context of the application.

## 📁 Project Structure
```
axiom-academic-hub/
├── backend/
│   ├── app/                 # FastAPI application package
│   │   ├── main.py          # App entry point
│   │   ├── worker.py        # Celery worker tasks
│   │   ├── api/             # API Routers (auth, courses, tasks, webhooks)
│   │   ├── core/            # Core logic (dependencies, google_utils, llm)
│   │   ├── db/              # Database (models, schemas, session)
│   │   └── services/        # Business logic (classroom, gmail, sync)
│   ├── Dockerfile           # Backend container config
│   └── requirements.txt     # Python dependencies
├── frontend/
│   └── src/
│       ├── app/             # Next.js App Router
│       └── components/      # UI Components (TaskCard, ConflictModal)
└── scripts/                 # Automation and scaling scripts
```

## 🛠 Tech Stack
- **Frontend:** Next.js 16, React 19, Vanilla CSS (Glassmorphism UI).
- **Backend:** FastAPI, Python 3.13.
- **Database:** SQLite (Local) / PostgreSQL (Production) using SQLAlchemy.
- **AI:** Google Gemini API (model: `gemini-2.5-flash`).
- **Integrations:** Google Classroom, Gmail, and Google Calendar APIs.
- **Hosting:** Google Cloud Run with Docker.

---

## 🧠 Core Backend Logic

### 1. Database Schema (`backend/app/db/models.py`)
```python
# (Code truncated for brevity, focusing on core entities)
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Uuid, primary_key=True)
    title = Column(String, nullable=False)
    due_date = Column(DateTime)
    task_type = Column(Enum(TaskType)) # EXAM, HOMEWORK, etc.
    status = Column(Enum(TaskStatus))
    effort_estimate_hrs = Column(Float)
    priority_score = Column(Float)
```

### 2. AI Effort Estimation (`backend/app/core/llm.py`)
```python
async def estimate_effort(title: str, description: str, task_type: str) -> float:
    # Uses Gemini LLM to predict hours required for a student task.
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"Estimate time in hours for: {title}. Task Type: {task_type}. Respond in JSON."
    # ... logic to parse LLM response
```

### 3. Prioritization Algorithm (`backend/app/services/prioritization.py`)
```python
def calculate_priority_score(due_date, task_type, effort_hrs, weight_pct=None):
    # Score = (Urgency * 0.50) + (Impact * 0.30) + (Effort Pressure * 0.20)
    # Urgency: Exponential decay based on days remaining.
    # Impact: Based on task type (Exam=85, Reading=20).
    # Effort Pressure: Hours required per day until deadline.
```

---

## 🎨 Core Frontend Logic

### Dashboard & State Management (`frontend/src/app/page.js`)
- **OAuth Flow:** Handles token storage in `localStorage` after Google redirect.
- **Sync Logic:** Triggers backend sync for Classroom/Gmail.
- **Guest Mode:** Provides dummy data for instant preview.
- **Glassmorphism UI:** Implemented via `globals.css` and React components.

---

## 🚀 Deployment & Scaling
- **GCP:** Uses Cloud Run with `setup_gcp.ps1` and `manage_scaling.ps1`.
- **Modes:** Supports "ECO" (Scale to zero) and "LIVE" (Always-on) configurations.
