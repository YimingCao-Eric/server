from fastapi import FastAPI

from app.routers.education_router import router as education_router
from app.routers.job_router import router as job_router
from app.routers.profile_router import router as profile_router
from app.routers.project_router import router as project_router
from app.routers.work_experience_router import router as work_experience_router

app = FastAPI(
    title="AI Job Hunting Assistant",
    description="User Professional Profile API",
    version="0.1.0",
)

app.include_router(profile_router)
app.include_router(education_router)
app.include_router(work_experience_router)
app.include_router(project_router)
app.include_router(job_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
