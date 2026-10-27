"""Props catalog: where every price comes from.

Reads the Snowflake PROPS table when Snowflake is set up, and falls back to
backend/data/props.csv (the same rows) so the app works offline and in tests.
"""

import csv
import logging
import re
import threading
import time
from pathlib import Path

from app.config import get_settings
from app.schemas import Prop

logger = logging.getLogger(__name__)

LOCAL_CSV = Path(__file__).resolve().parents[2] / "data" / "props.csv"

# How long to trust a loaded catalog before reading it again.
CACHE_SECONDS = 300

# Room keyword -> theme tag. Mirrors frontend/src/data/roomThemes.js so the
# props match the picture on each room. First match wins.
ROOM_THEMES = [
    ("vampire", r"^(vampire|dracula|fang|blood|count)"),
    ("doll", r"^(chucky|doll|toy|nursery|clown|carnival|circus|jester)"),
    ("mirror", r"^(mirror|reflection|vanish|invisible)"),
    ("witch", r"^(witch|cauldron|coven|kitchen|brew|potion|hex)"),
    ("seance", r"^(seance|séance|crystal|psychic|fortune|oracle)"),
    ("zombie", r"^(zombie|undead|corpse|morgue|infect)"),
    ("coffin", r"^(coffin|funeral|mortuary|wake)"),
    ("skull", r"^(skull|bone|crypt|tomb|grave|catacomb|skeleton)"),
    ("spider", r"^(spider|web|attic|archive|dust)"),
    ("bat", r"^(bat|cellar|cave|belfry|basement|tunnel)"),
    ("devil", r"^(devil|demon|hell|chapel|altar|ritual|cult|possess)"),
    ("brain", r"^(asylum|brain|lab|doctor|surgeon|experiment|ward)"),
    ("eye", r"^(eye|portrait|gallery|watch|stare)"),
    ("clock", r"^(clock|tower|time|landing)"),
    ("fire", r"^(fire|furnace|burn|flame|inferno)"),
    ("storm", r"^(storm|lightning|thunder)"),
    ("snake", r"^(snake|serpent|swamp|bog)"),
    ("garden", r"^(garden|vine|forest|graveyard|thorn|flower)"),
    ("alien", r"^(alien|ufo|space)"),
    ("scream", r"^(exit|escape|final|scream|climax)"),
    ("pumpkin", r"^(entry|entrance|hall|foyer|threshold|porch|pumpkin)"),
    ("ghost", r"^(ghost|spirit|whisper|haunt|phantom|poltergeist)"),
]
_ROOM_THEMES = [(key, re.compile(pattern)) for key, pattern in ROOM_THEMES]

GENERAL_THEME = "any"

_cache: tuple[list[Prop], str, float] | None = None
_lock = threading.Lock()


def room_theme(name: str, concept: str = "") -> str:
    """Theme tag for a room, matched on whole-word prefixes like the frontend."""
    words = re.split(r"[^a-zé]+", f"{name} {concept}".lower())
    for key, pattern in _ROOM_THEMES:
        if any(pattern.match(word) for word in words if word):
            return key
    return "ghost"


def _to_prop(index: int, row: dict) -> Prop:
    return Prop(
        id=f"p{index}",
        name=str(row["name"]).strip(),
        category=str(row["category"]).strip(),
        theme=str(row["theme"]).strip().lower(),
        price=round(float(row["price"]), 2),
    )


def load_local() -> list[Prop]:
    with LOCAL_CSV.open(newline="", encoding="utf-8") as f:
        return [_to_prop(i, row) for i, row in enumerate(csv.DictReader(f), start=1)]


def load_snowflake() -> list[Prop]:
    """SNOWFLAKE HOOK: read the props catalog from Snowflake.

    Today this reads our own PROPS table (create it with sql/props.sql). To use a
    Marketplace dataset instead, change the SELECT so it still returns the
    columns name, category, theme, price, e.g. join a price table and map its
    categories onto our theme tags.
    """
    from app.services.snowflake_client import run_query

    table = get_settings().props_table
    if not re.fullmatch(r"[A-Za-z_][\w$]*(\.[A-Za-z_][\w$]*){0,2}", table):
        raise ValueError(f"PROPS_TABLE is not a valid table name: {table!r}")

    rows = run_query(
        f"SELECT name, category, theme, price FROM {table} "
        "WHERE price IS NOT NULL AND price > 0 ORDER BY theme, price DESC"
    )
    # Snowflake upper-cases unquoted column names
    props = [_to_prop(i, {k.lower(): v for k, v in row.as_dict().items()}) for i, row in enumerate(rows, 1)]
    if not props:
        raise RuntimeError(f"Snowflake table {table} has no props")
    return props


def _load() -> tuple[list[Prop], str]:
    s = get_settings()
    mode = s.catalog_source.lower()
    if mode == "snowflake" or (mode == "auto" and s.snowflake_configured):
        try:
            return load_snowflake(), "snowflake"
        except Exception:
            if mode == "snowflake":
                raise
            logger.warning("Snowflake catalog unavailable, using local CSV", exc_info=True)
    return load_local(), "local"


def get_catalog() -> tuple[list[Prop], str]:
    """All props plus where they came from ("snowflake" or "local"), cached briefly."""
    global _cache
    with _lock:
        if _cache is None or time.monotonic() - _cache[2] > CACHE_SECONDS:
            props, source = _load()
            _cache = (props, source, time.monotonic())
        return _cache[0], _cache[1]


def clear_cache() -> None:
    global _cache
    with _lock:
        _cache = None
