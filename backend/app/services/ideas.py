"""Stage 1: the theme, story and a concept + scare for every room.

An open-weight LLM (Llama via Snowflake Cortex AI_COMPLETE) writes the ideas.
It never sees prices or does math; it only picks a prop tag per room, and
sourcing.py turns that tag into real props from the catalog. If Cortex is
unavailable or returns something unusable, a fixed hand-written house is used.
"""

import json
import logging
import random
import re

from pydantic import BaseModel, Field, ValidationError, field_validator

from app.config import get_settings
from app.services.catalog import ROOM_THEMES, room_theme

logger = logging.getLogger(__name__)

PROP_TAGS = [key for key, _ in ROOM_THEMES]
ATTEMPTS = 2


def _first_sentence(text: str) -> str:
    # Keeps the UI short even when the model ignores "one sentence"
    return re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)[0]


class RoomIdea(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    concept: str = Field(min_length=10)
    scare: str = Field(min_length=5)
    prop_tag: str

    _short = field_validator("concept", "scare")(_first_sentence)

    @field_validator("name")
    @classmethod
    def strip_numbering(cls, name: str) -> str:
        # Models like to write "Room 3: The Crypt"
        return re.sub(r"^\s*room\s*\d+\s*[:.\-–]\s*", "", name, flags=re.IGNORECASE).strip()

    @field_validator("prop_tag")
    @classmethod
    def known_tag(cls, tag: str) -> str:
        tag = tag.strip().lower()
        if tag not in PROP_TAGS:
            raise ValueError(f"unknown prop tag {tag!r}")
        return tag


class HouseIdea(BaseModel):
    theme: str = Field(min_length=2, max_length=80)
    story: str = Field(min_length=10)
    rooms: list[RoomIdea]

    _short = field_validator("story")(_first_sentence)


# ---------- fixed fallback ----------

FIXED_THEME = "Midnight Manor"
FIXED_STORY = "The Blackwood family vanished at midnight a century ago, and they're still waiting in the clocktower."

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
    """Which fixed rooms to use, in walking order: entry, middle rooms, climax, exit."""
    if rooms == 1:
        return [ENTRY]
    if rooms == 2:
        return [ENTRY, EXIT]
    return [ENTRY, *MIDDLE[: rooms - 3], CLIMAX, EXIT]


def fixed_room(slot: int) -> RoomIdea:
    name, concept = ROOM_NAMES[slot], ROOM_CONCEPTS[slot]
    return RoomIdea(name=name, concept=concept, scare=ROOM_SCARES[slot], prop_tag=room_theme(name, concept))


def fixed_house(rooms: int) -> HouseIdea:
    return HouseIdea(theme=FIXED_THEME, story=FIXED_STORY, rooms=[fixed_room(s) for s in room_slots(rooms)])


# ---------- Cortex ----------

# A nudge so the model doesn't write the same house every time.
SETTINGS = [
    "abandoned asylum", "witch's cottage", "haunted carnival", "sunken ship", "Victorian mansion",
    "cursed summer camp", "derelict space station", "plague-era village", "abandoned school",
    "funeral home", "swamp shack", "toy factory", "silent film theater", "frozen research outpost",
]


def _tag_guide() -> str:
    # "brain (asylum, brain, lab, ...)" built from the same keywords the catalog uses
    lines = []
    for key, pattern in ROOM_THEMES:
        words = pattern.strip("^()").split("|")
        lines.append(f"- {key}: {', '.join(words)}")
    return "\n".join(lines)


def _room_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "concept": {"type": "string"},
            "scare": {"type": "string"},
            "prop_tag": {"type": "string", "enum": PROP_TAGS},
        },
        "required": ["name", "concept", "scare", "prop_tag"],
    }


HOUSE_SCHEMA = {
    "type": "json",
    "schema": {
        "type": "object",
        "properties": {
            "theme": {"type": "string"},
            "story": {"type": "string"},
            "rooms": {"type": "array", "items": _room_schema()},
        },
        "required": ["theme", "story", "rooms"],
    },
}
ROOM_SCHEMA = {"type": "json", "schema": _room_schema()}

TONE = """Keep it chill: spooky and fun, never gory or melodramatic. Write short and plain,
like a friend pitching a backyard haunt. No flowery language."""

ROOM_RULES = f"""Each room has:
- name: 2 to 4 words, no numbering
- concept: one short sentence (under 15 words) on the mood, lighting or sound
- scare: one short sentence (under 15 words) on the single scare moment, doable by volunteers with store-bought props
  Scares must be safe: actors never touch guests, and no real weapons, chainsaws, fire or blades.
- prop_tag: the prop category that best fits the room, from this list (tag: what it covers):
{_tag_guide()}"""


def _pacing(rooms: int) -> str:
    if rooms == 1:
        return "There is only one room: make it the entrance and the big scare in one."
    if rooms == 2:
        return "Room 1 is the entrance. Room 2 is the big scare and the exit."
    return (
        f"Room 1 is the entrance and starts calm and eerie. Tension builds room by room. "
        f"Room {rooms - 1} is the climax and the biggest scare. Room {rooms} is the exit: a last small scare."
    )


def complete(prompt: str, response_format: dict, max_tokens: int) -> str:
    """One AI_COMPLETE call with an open-weight model; returns the raw JSON text."""
    from app.services.snowflake_client import run_query

    params = {"temperature": 0.9, "max_tokens": max_tokens}
    rows = run_query(
        "SELECT AI_COMPLETE(model => ?, prompt => ?, model_parameters => PARSE_JSON(?), "
        "response_format => PARSE_JSON(?)) AS R",
        [get_settings().cortex_model, prompt, json.dumps(params), json.dumps(response_format)],
    )
    return rows[0]["R"]


def ai_house(rooms: int, budget: float) -> HouseIdea:
    prompt = f"""You design home haunted houses for Halloween. Invent an original haunted house with exactly {rooms} rooms.
Setting to riff on (make it your own): {random.choice(SETTINGS)}.
The total budget is ${budget:,.0f}, so keep ideas achievable at that budget.

Give it:
- theme: a short, catchy name for the house
- story: one short sentence (under 20 words) of backstory
- rooms: exactly {rooms} rooms in the order guests walk through them

{_pacing(rooms)}
Every room name must be different. Avoid repeating the same gimmick in two rooms.

{TONE}

{ROOM_RULES}"""

    last_error = None
    for _ in range(ATTEMPTS):
        try:
            house = HouseIdea.model_validate_json(complete(prompt, HOUSE_SCHEMA, 250 + 100 * rooms))
            names = [room.name.lower() for room in house.rooms]
            if len(house.rooms) != rooms:
                raise ValueError(f"asked for {rooms} rooms, got {len(house.rooms)}")
            if len(set(names)) != len(names):
                raise ValueError("room names repeat")
            return house
        except (ValidationError, ValueError) as err:
            last_error = err
            logger.warning("Cortex house idea rejected, retrying: %s", err)
    raise ValueError(f"Cortex gave no usable house after {ATTEMPTS} tries: {last_error}")


def ai_room(theme: str, order: int, avoid: list[str]) -> RoomIdea:
    taken = ", ".join(avoid) or "none"
    prompt = f"""You design home haunted houses for Halloween. The house is called "{theme}".
Invent one new room to go at position {order} of the walk-through. It must be different from these rooms: {taken}.

{TONE}

{ROOM_RULES}"""

    avoid_lower = {name.lower() for name in avoid}
    last_error = None
    for _ in range(ATTEMPTS):
        try:
            room = RoomIdea.model_validate_json(complete(prompt, ROOM_SCHEMA, 150))
            if room.name.lower() in avoid_lower:
                raise ValueError(f"{room.name} is already in the house")
            return room
        except (ValidationError, ValueError) as err:
            last_error = err
            logger.warning("Cortex room idea rejected, retrying: %s", err)
    raise ValueError(f"Cortex gave no usable room after {ATTEMPTS} tries: {last_error}")


# ---------- entry points ----------


def _use_ai() -> bool:
    s = get_settings()
    mode = s.ideas_source.lower()
    return mode == "ai" or (mode == "auto" and s.snowflake_configured)


def _fallback(err: Exception) -> None:
    if get_settings().ideas_source.lower() == "ai":
        raise err
    logger.warning("Using the fixed house instead of Cortex", exc_info=err)


def generate_house(rooms: int, budget: float) -> tuple[HouseIdea, str]:
    """The house idea plus where it came from: "ai" or "fixed"."""
    if _use_ai():
        try:
            return ai_house(rooms, budget), "ai"
        except Exception as err:  # noqa: BLE001 -- any Cortex failure falls back to the fixed house
            _fallback(err)
    return fixed_house(rooms), "fixed"


def generate_room(theme: str, order: int, avoid: list[str]) -> tuple[RoomIdea, str]:
    if _use_ai():
        try:
            return ai_room(theme, order, avoid), "ai"
        except Exception as err:  # noqa: BLE001 -- any Cortex failure falls back to the fixed house
            _fallback(err)
    avoid_lower = {name.lower() for name in avoid}
    slots = [s for s in range(len(ROOM_NAMES)) if ROOM_NAMES[s].lower() not in avoid_lower]
    return fixed_room(random.choice(slots or range(len(ROOM_NAMES)))), "fixed"
