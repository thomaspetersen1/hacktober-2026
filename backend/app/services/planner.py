"""Deterministic haunted-house planner that turns a budget into a room-by-room concept."""

from app.schemas import PlanRequest, PlanResponse, Room
from app.services.budget import allocate

ROOM_NAMES = [
    "Entry Hall",
    "Mirror Gallery",
    "Whispering Nursery",
    "Attic Archive",
    "Crypt Passage",
    "Hidden Chapel",
    "Witch's Kitchen",
    "Seance Room",
    "Creeping Garden",
    "Moonlit Cellar",
    "Clocktower Landing",
    "Final Exit",
]

ROOM_CONCEPTS = [
    "A foggy threshold where guests first hear distant chains and a flickering chandelier.",
    "Broken mirrors and silver reflections create a disorienting, false-escape corridor.",
    "A nursery of old toys and dry whispers that grow louder as the floorboards creak.",
    "Dusty trunks, stained glass, and hidden footprints make the attic feel psychologically unsafe.",
    "The crypt is dim, cold, and lined with candlelight that reveals moving silhouettes.",
    "A forgotten chapel where a hidden voice repeats prayers in reverse behind the altar.",
    "A witch's kitchen full of cauldrons, hanging herbs, and the smell of smoke and rust.",
    "A seance room of velvet curtains, black candles, and unsettling psychic activity.",
    "A moonlit garden path where vines move like fingers and the fog changes shape.",
    "The cellar pulses with low bass thumps and narrow tunnels that twist under the house.",
    "The clocktower landing is the buildup space before the big scare and final reveal.",
    "The exit is a chosen calm, a final breath after the climax with just enough dread to linger.",
]


def _room_name(order: int) -> str:
    return ROOM_NAMES[min(order, len(ROOM_NAMES) - 1)]


def _room_concept(order: int) -> str:
    return ROOM_CONCEPTS[min(order, len(ROOM_CONCEPTS) - 1)]


def build_plan(req: PlanRequest) -> PlanResponse:
    """Turn the user input into a deterministic haunted-house layout."""
    budget_values = allocate(float(req.budget), int(req.rooms))
    total_allocated = round(sum(budget_values), 2)
    rooms = [
        Room(
            order=index + 1,
            name=_room_name(index),
            concept=_room_concept(index),
            budget=round(amount, 2),
        )
        for index, amount in enumerate(budget_values)
    ]
    return PlanResponse(
        theme="Midnight Manor",
        budget=round(float(req.budget), 2),
        total_allocated=total_allocated,
        rooms=rooms,
    )
