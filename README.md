# Axiom – Automated Academic Hub 🎓

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/SouvikGhorui/axiom-academic-hub)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js-000000?logo=next.js)](https://nextjs.org/)

Axiom is an AI-powered academic orchestration platform designed to streamline student workflows. By integrating directly with Google Workspace (Classroom, Gmail, Calendar) and leveraging the power of Gemini AI, Axiom automatically imports, prioritizes, and schedules academic tasks, allowing students to focus on what matters most: learning.

---

## ✨ Key Features

- 🔄 **Intelligent Syncing**
  - **Google Classroom**: Automatic import of courses, assignments, and due dates.
  - **Gmail Pipeline**: AI-driven extraction of deadline info from enrollment and syllabus emails.
  - **Google Calendar**: Bi-directional sync of study blocks and academic events.

- 🧠 **AI-Powered Prioritization**
  - Uses **Gemini AI** for realistic effort estimation (in hours) based on task complexity.
  - Calculates dynamic **Priority Scores** using urgency, impact, and effort pressure.

- 📅 **Smart Scheduling & Conflict Management**
  - Automatically identifies gaps in your schedule for dedicated study blocks.
  - Interactive **Conflict Detection** alerts you when academic tasks overlap with personal events.

- 🎨 **Modern Dashboard**
  - High-performance, **Glassmorphism-inspired UI** built with Next.js.
  - Interactive task timers and real-time statistics tracking.

---

## 🏗 Project Architecture

Axiom follows a modular, professional-grade directory structure designed for scalability and maintainability.

```text
axiom-academic-hub/
├── backend/
│   ├── app/                 # FastAPI core application
│   │   ├── api/             # RESTful API endpoints (auth, tasks, courses)
│   │   ├── core/            # System-wide logic (auth, AI, utils)
│   │   ├── db/              # Database models, schemas, and sessions
│   │   ├── services/        # Business logic & external integrations
│   │   ├── main.py          # API Entry Point
│   │   └── worker.py        # Background task processor (Celery)
│   ├── Dockerfile           # Backend containerization
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router (pages & layouts)
│   │   └── components/      # Modular UI components (Atomic design)
│   └── Dockerfile           # Frontend containerization
├── scripts/                 # Deployment & automation scripts
└── docker-compose.yml       # Local orchestration
```

---

## 🛠 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | [Next.js](https://nextjs.org/), [React](https://reactjs.org/), [Vanilla CSS](https://developer.mozilla.org/en-US/docs/Web/CSS) |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/), [Python 3.13](https://www.python.org/) |
| **Database** | [PostgreSQL](https://www.postgresql.org/) (Production) / [SQLite](https://www.sqlite.org/) (Dev) |
| **ORM** | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) |
| **AI Engine** | [Google Gemini 2.5 Flash](https://ai.google.dev/) |
| **Infrastructure** | [Docker](https://www.docker.com/), [Google Cloud Run](https://cloud.google.com/run) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Cloud Project with OAuth 2.0 Credentials
- Gemini API Key

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/SouvikGhorui/axiom-academic-hub.git
   cd axiom-academic-hub
   ```

2. **Backend Configuration**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   cp .env.example .env      # Fill in your secrets
   python -m app.db.init_db  # Initialize database
   uvicorn app.main:app --reload
   ```

3. **Frontend Configuration**
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

### 🐳 Docker Deployment
For a consistent environment across all layers:
```bash
docker-compose up --build
```

---

## ☁️ Cloud Deployment (GCP)

Axiom is optimized for **Google Cloud Run**. Use the automated scripts for zero-touch provisioning:

1. **Provision Infrastructure**:
   ```powershell
   # Automates API activation, DB creation, and Secret Management
   .\scripts\setup_gcp.ps1
   ```

2. **Deploy via Cloud Build**:
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

3. **Scale Management**:
   ```powershell
   # Toggle between ECO (Scale-to-zero) and LIVE (Always-on)
   .\scripts\manage_scaling.ps1 -Mode "LIVE"
   ```

---

## 🔑 Environment Variables

Essential variables required in your `backend/app/.env` (or Secret Manager):

| Key | Description |
| :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string |
| `GOOGLE_CLIENT_ID` | OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth 2.0 Client Secret |
| `GEMINI_API_KEY` | API Key for Gemini AI |
| `JWT_SECRET_KEY` | Secret for signing auth tokens |

---

## 🛡 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🤝 Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

Developed with ⚡ by [Souvik](https://github.com/SouvikGhorui)
