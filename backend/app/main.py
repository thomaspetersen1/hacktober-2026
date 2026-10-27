from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import catalog, plan, rooms

settings = get_settings()

app = FastAPI(title="Haunted House Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plan.router)
app.include_router(rooms.router)
app.include_router(catalog.router)


@app.get("/api/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "snowflake_configured": settings.snowflake_configured}


THEMES = [
    "Victorian Mansion", "Haunted Carnival", "Abandoned Asylum", "Abandoned School",
    "Abandoned Hospital", "Abandoned Factory", "Abandoned Prison", "Abandoned Mine",
    "Abandoned Amusement Park", "Abandoned Hotel", "Abandoned Church", "Abandoned Castle",
    "Abandoned Theater", "Abandoned Circus", "Abandoned Zoo", "Abandoned Aquarium",
    "Abandoned Library", "Abandoned Museum", "Abandoned Laboratory", "Abandoned Observatory",
    "Abandoned Space Station",
]

ROOM_TYPES = [
    "Foyer", "Living Room", "Kitchen", "Dining Room", "Bedroom", "Bathroom", "Basement",
    "Attic", "Garage", "Garden", "Patio", "Balcony", "Hallway", "Staircase", "Library",
    "Study", "Office", "Workshop", "Studio", "Gym",
]

ITEM_CATEGORIES = [
    "Furniture", "Lighting", "Decoration", "Props", "Sound Effects", "Special Effects",
    "Costumes", "Makeup", "Tools", "Equipment", "Electronics", "Appliances", "Craft Supplies",
    "Cleaning Supplies", "Outdoor Equipment", "Safety Equipment", "Scare Actors", "Fog Machine",
    "Screens", "Projectors", "Speakers", "Microphones", "Cameras",
]


@app.get("/api/themes", tags=["themes"])
def get_themes() -> dict:
    return {"themes": THEMES}


@app.get("/api/rooms", tags=["rooms"])
def get_rooms() -> dict:
    return {"rooms": ROOM_TYPES}


@app.get("/api/items", tags=["items"])
def get_items() -> dict:
    return {"items": ITEM_CATEGORIES}
