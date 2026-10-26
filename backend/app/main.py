from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import plan

settings = get_settings()

app = FastAPI(title="Haunted House Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plan.router)


@app.get("/api/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "snowflake_configured": settings.snowflake_configured}
