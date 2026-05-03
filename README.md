# Axiom – Automated Academic Hub 🎓

An AI-powered academic task manager that automatically syncs your **Google Classroom** courses and assignments, prioritizes tasks using Gemini LLM, and presents them in a beautiful dashboard.

## ✨ Features

- 📚 **Google Classroom Sync** — One-click import of all active courses and assignments
- 🤖 **AI Prioritization** — Gemini LLM estimates effort and calculates priority scores for each task
- 📧 **Gmail Pipeline** — Extracts course information from enrollment emails
- 📅 **Calendar Integration** — Study blocks synced to Google Calendar
- ⚡ **Conflict Detection** — Alerts when study blocks overlap with calendar events
- 🎨 **Glassmorphism UI** — Beautiful dark-mode dashboard built with Next.js

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, Vanilla CSS |
| Backend | FastAPI, Python 3.13 |
| Database | SQLite (via SQLAlchemy async + aiosqlite) |
| AI | Google Gemini API |
| Auth | Google OAuth 2.0 + JWT |
| APIs | Gmail API, Google Classroom API, Google Calendar API |

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Google Cloud project with OAuth 2.0 credentials
- APIs enabled: Gmail, Google Classroom, Google Calendar, Gemini

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install fastapi uvicorn sqlalchemy aiosqlite python-dotenv \
    google-auth google-auth-oauthlib google-api-python-client \
    google-generativeai python-jose requests

# Copy and fill in your credentials
cp .env.example .env

# Initialize the database
python init_db.py

# Start the server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🐳 Running with Docker

The easiest way to run both the frontend and backend is using Docker Compose.

### 1. Configure Environment
Ensure you have your `.env` file in the `backend/` directory with all the required keys (see [Environment Variables](#-environment-variables)).

### 2. Launch with Docker Compose
From the root directory, run:
```bash
docker-compose up --build
```

- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

*Note: On the first run, the system will attempt to initiate the Google OAuth flow. Check the terminal logs if a browser window does not automatically open.*

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials (Desktop app type)
3. Download `credentials.json` and place it in the `backend/` folder
4. Enable: Gmail API, Google Classroom API, Google Calendar API
5. On first run, a browser window will open for authentication

## 📁 Project Structure

```
Task manager app/
├── docker-compose.yml       # Docker orchestration
├── backend/
│   ├── Dockerfile           # Backend container config
│   ├── requirements.txt     # Python dependencies
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # DB engine & session
│   ├── classroom.py         # Google Classroom API client
│   ├── gmail_pipeline.py    # Gmail → LLM → DB pipeline
│   ├── llm.py               # Gemini AI integration
│   ├── prioritization.py    # Priority score calculator
│   ├── calendar_sync.py     # Google Calendar sync
│   ├── init_db.py           # DB initializer
│   ├── .env.example         # Environment variable template
│   └── routers/
│       ├── auth.py          # Google OAuth endpoints
│       ├── courses.py       # Course CRUD + Classroom sync
│       └── tasks.py         # Task CRUD
└── frontend/
    ├── Dockerfile           # Frontend container config
    └── src/
        ├── app/
        │   ├── page.js      # Main dashboard
        │   ├── layout.js    # Root layout
        │   └── globals.css  # Global styles
        └── components/
            ├── TaskCard.js  # Task display card
            └── ConflictModal.js  # Schedule conflict dialog
```

## 🔑 Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
DATABASE_URL=sqlite+aiosqlite:///./academic_hub.db
JWT_SECRET_KEY=...
GEMINI_API_KEY=...
```

