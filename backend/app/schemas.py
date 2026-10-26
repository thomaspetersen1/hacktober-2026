from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    budget: float = Field(gt=0, description="Total budget in USD")
    rooms: int = Field(ge=1, le=12, description="Number of rooms")


class Room(BaseModel):
    order: int
    name: str
    concept: str
    budget: float


class PlanResponse(BaseModel):
    theme: str
    budget: float
    total_allocated: float
    rooms: list[Room]
