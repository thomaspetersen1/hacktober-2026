"""Pipeline: ideas -> sourcing -> cohesion. Turns a budget into a full haunted house."""

from app.config import get_settings
from app.schemas import PlanRequest, PlanResponse, Prop, Room
from app.services import catalog
from app.services.budget import allocate
from app.services.cohesion import check_plan
from app.services.ideas import RoomIdea, generate_house
from app.services.sourcing import pick_items, spent


def make_room(
    idea: RoomIdea,
    order: int,
    budget: float,
    square_feet: float | None,
    props: list[Prop],
    used: set[str],
    climax: bool = False,
) -> Room:
    tags = [idea.prop_tag]
    if climax and "scream" not in tags:
        tags.append("scream")  # the big scare gets first pick of the jump-scare props
    items = pick_items(budget, tags, props, used)
    return Room(
        order=order,
        name=idea.name,
        concept=idea.concept,
        scare=idea.scare,
        theme_key=idea.prop_tag,
        budget=round(budget, 2),
        spent=spent(items),
        square_feet=square_feet,
        items=items,
    )


def build_plan(req: PlanRequest) -> PlanResponse:
    # Stage 1, ideas: theme, story and room concepts from the LLM (or the fixed house)
    house, ideas_source = generate_house(req.rooms, float(req.budget))
    budgets = allocate(float(req.budget), req.rooms)
    room_sqft = round(req.square_feet / req.rooms, 1) if req.square_feet else None
    climax = req.rooms - 2 if req.rooms >= 3 else None

    # Stage 2, sourcing: real props and prices from the catalog
    props, source = catalog.get_catalog()
    used: set[str] = set()
    rooms = [
        make_room(idea, i + 1, amount, room_sqft, props, used, climax=i == climax)
        for i, (idea, amount) in enumerate(zip(house.rooms, budgets))
    ]

    plan = PlanResponse(
        theme=house.theme,
        story=house.story,
        budget=round(float(req.budget), 2),
        total_allocated=round(sum(budgets), 2),
        total_spent=sum(round(room.spent * 100) for room in rooms) / 100,
        square_feet=req.square_feet,
        catalog_source=source,
        ideas_source=ideas_source,
        ai_model=get_settings().cortex_model if ideas_source == "ai" else None,
        rooms=rooms,
    )

    # Stage 3, cohesion: sanity-check the whole house
    plan.warnings = check_plan(plan)
    return plan
