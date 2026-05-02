from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Automated Academic Hub API",
    description="Backend API for the Automated Academic Hub",
    version="1.0.0"
)

# Allow frontend to access the API
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import auth, courses, tasks

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(tasks.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Automated Academic Hub API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
