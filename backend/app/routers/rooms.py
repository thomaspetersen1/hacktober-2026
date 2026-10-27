from fastapi import APIRouter

from app.schemas import RerollRequest, Room
from app.services.reroll import reroll_room

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.post("/reroll", response_model=Room)
def reroll(req: RerollRequest) -> Room:
    return reroll_room(req)
