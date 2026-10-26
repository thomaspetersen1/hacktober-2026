"""Haunted house planning pipeline.

Stages (to be implemented with open-weight models):
  1. ideas     - theme + per-room concepts
  2. sourcing  - items from Snowflake that fit each room's budget
  3. cohesion  - check story flow, pacing and totals
"""

from app.schemas import PlanRequest, PlanResponse, Room
from app.services.budget import allocate


def build_plan(req: PlanRequest) -> PlanResponse:
    # TODO: replace placeholder concepts with the LLM ideas stage
    budgets = allocate(req.budget, req.rooms)
    rooms = [
        Room(
            order=i + 1,
            name=f"Room {i + 1}",
            concept="Concept coming soon from the ideas stage.",
            budget=amount,
        )
        for i, amount in enumerate(budgets)
    ]
    return PlanResponse(
        theme="Untitled Haunt",
        budget=req.budget,
        total_allocated=round(sum(budgets), 2),
        square_feet=req.square_feet,
        rooms=rooms,
    )
