from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import plan, rooms

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


@app.get("/api/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "snowflake_configured": settings.snowflake_configured}


@app.get("/api/themes", tags=["themes"])
def get_themes() -> dict:
    return {"themes": [Victorian Mansion, Haunted Carnivel, Abandoned Asylum, Abandoend school, 
    Abandeond hospital, Abandoned Factory, Abandoned Prison, Abandoned Mine, Abandoned Amusement Park, 
    Abandoned Hotel, Abandoned Church, Abandoned Castle, Abandoned Theater, Abandoned Circus, Abandoned Zoo, 
    Abandoned Aquarium, Abandoned Library, Abandoned Museum, Abandoned Laboratory, Abandoned Observatory, 
    Abandoned Space Station]
    }

    @app.get("/api/rooms", tags=["rooms"])
def get_rooms() -> dict:
    return {"rooms": [Foyer, Living Room, Kitchen, Dining Room, Bedroom, Bathroom, Basement, Attic, Garage, 
    Garden, Patio, Balcony, Hallway, Staircase, Library, Study, Office, Workshop, Studio, Gym]
    }

    @app.get("/api/items", tags=["items"])
def get_items() -> dict:
    return{"items": [Furniture, Lighting, Decoration, Props, Sound Effects, Special Effects, Costumes, Makeup, Tools, Equipment, Electronics, Appliances,
    Craft Supplies, Cleaning Supplies, Outdoor Equiment, Saftey Equipment, Scare Actors, Fog Machine, Screens, Projectors, Speakers, Mircrophones, Cameras]
    }