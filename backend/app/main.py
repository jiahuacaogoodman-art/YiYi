from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routers import admin, auth, exams, feedback, interactions, practice, questions, statistics, taxonomy
from app.core.config import resolve_backend_path, settings
from app.core.exceptions import register_exception_handlers

app = FastAPI(
    title=settings.app_name,
    description="医学刷题平台后端 API，支持题库管理、刷题、错题本、收藏、考试、统计和后台运营。",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth.router, prefix="/api")
app.include_router(taxonomy.router, prefix="/api")
app.include_router(questions.router, prefix="/api")
app.include_router(practice.router, prefix="/api")
app.include_router(exams.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(interactions.router, prefix="/api")
app.include_router(statistics.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

upload_dir = resolve_backend_path(settings.upload_dir)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}