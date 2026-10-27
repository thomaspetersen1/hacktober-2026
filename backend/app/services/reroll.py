"""Swap a single room for a different one, keeping its place and budget."""

import random

from app.schemas import RerollRequest, Room
from app.services import catalog
from app.services.planner import ROOM_NAMES, make_room


def reroll_room(req: RerollRequest) -> Room:
    """Pick a room that isn't already in the house and re-shop its props.

    Deterministic fallback for now; the AI stage can replace this later.
    """
    avoid = {name.lower() for name in req.avoid}
    slots = list(range(len(ROOM_NAMES)))
    unused = [slot for slot in slots if ROOM_NAMES[slot].lower() not in avoid]
    slot = random.choice(unused or slots)
    props, _ = catalog.get_catalog()
    return make_room(slot, req.order, req.budget, req.square_feet, props, set())
