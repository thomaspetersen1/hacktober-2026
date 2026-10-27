from typing import Literal

from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    budget: float = Field(gt=0, description="Total budget in USD")
    rooms: int = Field(ge=1, le=12, description="Number of rooms")
    square_feet: float | None = Field(
        default=None, gt=0, description="Optional total floor area in sq ft"
    )


class Prop(BaseModel):
    """One row of the props catalog (Snowflake PROPS table or backend/data/props.csv)."""

    id: str
    name: str
    category: str
    theme: str
    price: float


class Item(BaseModel):
    """A prop picked for a room, with the deterministic cost math done."""

    id: str
    name: str
    category: str
    unit_price: float
    quantity: int
    line_total: float


class Room(BaseModel):
    order: int
    name: str
    concept: str
    scare: str | None = None
    budget: float
    spent: float = 0
    square_feet: float | None = None
    items: list[Item] = Field(default_factory=list)


class PlanResponse(BaseModel):
    theme: str
    story: str | None = None
    budget: float
    total_allocated: float
    total_spent: float = 0
    square_feet: float | None = None
    catalog_source: Literal["snowflake", "local"] = "local"
    warnings: list[str] = Field(default_factory=list)
    rooms: list[Room]


class RerollRequest(BaseModel):
    theme: str
    order: int = Field(ge=1, le=12, description="Position of the room being replaced")
    budget: float = Field(gt=0, description="That room's budget in USD, kept as-is")
    avoid: list[str] = Field(default_factory=list, description="Room names already in the house")
    square_feet: float | None = Field(default=None, gt=0, description="That room's area, kept as-is")
