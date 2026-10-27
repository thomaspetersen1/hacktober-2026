"""Swap a single room for a different one, keeping its place and budget."""

from app.schemas import RerollRequest, Room
from app.services import catalog
from app.services.ideas import generate_room
from app.services.planner import make_room


def reroll_room(req: RerollRequest) -> Room:
    """Ask for a room that isn't already in the house and re-shop its props."""
    idea, _ = generate_room(req.theme, req.order, req.avoid)
    props, _ = catalog.get_catalog()
    return make_room(idea, req.order, req.budget, req.square_feet, props, set())
