from fastapi import FastAPI

from app.routers.profile_router import router as profile_router

app = FastAPI(
    title="AI Job Hunting Assistant",
    description="User Professional Profile API",
    version="0.1.0",
)

app.include_router(profile_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
