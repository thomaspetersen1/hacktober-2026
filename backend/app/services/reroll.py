"""Swap a single room for a different one, keeping its place and budget."""

import random

from app.schemas import RerollRequest, Room
from app.services.planner import ROOM_CONCEPTS, ROOM_NAMES


def reroll_room(req: RerollRequest) -> Room:
    """Pick a room that isn't already in the house.

    Deterministic fallback for now; the AI stage can replace this later.
    """
    pairs = list(zip(ROOM_NAMES, ROOM_CONCEPTS))
    avoid = {name.lower() for name in req.avoid}
    unused = [pair for pair in pairs if pair[0].lower() not in avoid]
    name, concept = random.choice(unused or pairs)
    return Room(order=req.order, name=name, concept=concept, budget=round(req.budget, 2))
