"""Pipeline: ideas -> sourcing -> cohesion. Turns a budget into a full haunted house."""

from app.schemas import PlanRequest, PlanResponse, Room
from app.services import catalog
from app.services.budget import allocate
from app.services.cohesion import check_plan
from app.services.sourcing import pick_items, spent

THEME = "Midnight Manor"
STORY = (
    "The Blackwood family vanished from their manor at midnight a century ago. "
    "Every Halloween the house wakes up and leads guests deeper, room by room, toward the clocktower "
    "where the family is still waiting."
)

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

ROOM_SCARES = [
    "The front door slams shut behind the last guest.",
    "One reflection keeps moving after the guests stop.",
    "A rocking chair starts on its own and a doll turns its head.",
    "A trunk lid bangs open as a figure drops from the rafters.",
    "A 'statue' in an alcove steps forward as guests pass.",
    "The altar candles blow out and the voice is suddenly right behind them.",
    "The witch lunges from behind the bubbling cauldron.",
    "The table rises and every candle flares at once.",
    "Hands burst from the hedges at ankle height.",
    "The tunnel lights cut out and something brushes past in the dark.",
    "The clock strikes midnight and the whole family lunges out at once.",
    "One last actor waits just past the exit curtain.",
]

ENTRY, CLIMAX, EXIT = 0, len(ROOM_NAMES) - 2, len(ROOM_NAMES) - 1
MIDDLE = list(range(1, CLIMAX))


def room_slots(rooms: int) -> list[int]:
    """Which of the rooms above to use, in walking order.

    Always opens on the entry and, with room for it, ends on the climax then
    the exit, which matches where budget.allocate puts the most money.
    """
    if rooms == 1:
        return [ENTRY]
    if rooms == 2:
        return [ENTRY, EXIT]
    return [ENTRY, *MIDDLE[: rooms - 3], CLIMAX, EXIT]


def make_room(slot: int, order: int, budget: float, square_feet: float | None, props, used: set[str]) -> Room:
    name, concept = ROOM_NAMES[slot], ROOM_CONCEPTS[slot]
    themes = [catalog.room_theme(name, concept)]
    if slot == CLIMAX:
        themes.append("scream")  # the big scare gets first pick of the jump-scare props
    items = pick_items(budget, themes, props, used)
    return Room(
        order=order,
        name=name,
        concept=concept,
        scare=ROOM_SCARES[slot],
        budget=round(budget, 2),
        spent=spent(items),
        square_feet=square_feet,
        items=items,
    )


def build_plan(req: PlanRequest) -> PlanResponse:
    # Stage 1, ideas: theme, story and room concepts (fixed lists for now)
    slots = room_slots(req.rooms)
    budgets = allocate(float(req.budget), req.rooms)
    room_sqft = round(req.square_feet / req.rooms, 1) if req.square_feet else None

    # Stage 2, sourcing: real props and prices from the catalog
    props, source = catalog.get_catalog()
    used: set[str] = set()
    rooms = [
        make_room(slot, order, amount, room_sqft, props, used)
        for order, (slot, amount) in enumerate(zip(slots, budgets), start=1)
    ]

    plan = PlanResponse(
        theme=THEME,
        story=STORY,
        budget=round(float(req.budget), 2),
        total_allocated=round(sum(budgets), 2),
        total_spent=sum(round(room.spent * 100) for room in rooms) / 100,
        square_feet=req.square_feet,
        catalog_source=source,
        rooms=rooms,
    )

    # Stage 3, cohesion: sanity-check the whole house
    plan.warnings = check_plan(plan)
    return plan
