from fastapi import APIRouter

from app.schemas import PlanRequest, PlanResponse
from app.services.planner import build_plan

router = APIRouter(prefix="/api", tags=["plan"])


@router.post("/plan", response_model=PlanResponse)
def create_plan(req: PlanRequest) -> PlanResponse:
    return build_plan(req)
