from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, courses, tasks, webhooks
from database import engine, Base
import models # Import models to ensure they are registered with Base

app = FastAPI(
    title="Automated Academic Hub API",
    description="Backend API for the Automated Academic Hub",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

# Allow frontend to access the API
allowed_origins = [
    "http://localhost:3000",
    os.getenv("FRONTEND_URL", ""),
]
# Remove empty strings
allowed_origins = [o for o in allowed_origins if o]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(tasks.router)
app.include_router(webhooks.router)

@app.on_event("startup")
async def on_startup():
    from database import engine, Base
    import models
    async with engine.begin() as conn:
        # This will create tables if they don't exist, without dropping existing data
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Welcome to the Automated Academic Hub API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
