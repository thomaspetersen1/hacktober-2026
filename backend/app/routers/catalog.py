from fastapi import APIRouter

from app.services.catalog import get_catalog

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/catalog")
def list_catalog() -> dict:
    """Every prop the planner can buy, and whether it came from Snowflake or the local CSV."""
    props, source = get_catalog()
    return {"source": source, "count": len(props), "props": props}
