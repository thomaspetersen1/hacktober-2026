import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import Prop
from app.services import catalog
from app.services.ideas import ROOM_NAMES
from app.services.sourcing import pick_items, spent

client = TestClient(app)


def prop(id, price, theme="ghost", category="Props"):
    return Prop(id=id, name=id, category=category, theme=theme, price=price)


@pytest.mark.parametrize("budget,rooms", [(25, 1), (100, 3), (500, 4), (999.99, 7), (5000, 12)])
def test_plan_never_overspends(budget, rooms):
    body = client.post("/api/plan", json={"budget": budget, "rooms": rooms}).json()
    assert body["catalog_source"] == "local"
    assert body["total_spent"] <= body["budget"]
    for room in body["rooms"]:
        assert room["spent"] <= room["budget"]
        cents = sum(round(item["line_total"] * 100) for item in room["items"])
        assert cents == round(room["spent"] * 100)
        for item in room["items"]:
            assert round(item["unit_price"] * item["quantity"] * 100) == round(item["line_total"] * 100)


def test_plan_paces_entry_climax_exit():
    rooms = client.post("/api/plan", json={"budget": 800, "rooms": 5}).json()["rooms"]
    assert rooms[0]["name"] == "Entry Hall"
    assert rooms[-2]["name"] == "Clocktower Landing"
    assert rooms[-1]["name"] == "Final Exit"
    assert rooms[-2]["budget"] == max(r["budget"] for r in rooms)
    assert len({r["name"] for r in rooms}) == 5
    assert all(r["scare"] for r in rooms)


def test_plan_does_not_repeat_themed_props():
    general = {p.id for p in catalog.load_local() if p.theme == catalog.GENERAL_THEME}
    rooms = client.post("/api/plan", json={"budget": 3000, "rooms": 12}).json()["rooms"]
    ids = [item["id"] for room in rooms for item in room["items"] if item["id"] not in general]
    assert len(ids) == len(set(ids))


def test_climax_gets_the_big_scare():
    rooms = client.post("/api/plan", json={"budget": 2000, "rooms": 5}).json()["rooms"]
    assert "Lunging monster animatronic" in [item["name"] for item in rooms[-2]["items"]]


def test_plan_passes_square_feet_through():
    body = client.post("/api/plan", json={"budget": 400, "rooms": 4, "square_feet": 200}).json()
    assert body["square_feet"] == 200
    assert all(room["square_feet"] == 50 for room in body["rooms"])
    assert any("sq ft" in warning for warning in body["warnings"])


def test_tiny_budget_warns_instead_of_failing():
    body = client.post("/api/plan", json={"budget": 5, "rooms": 6}).json()
    assert body["total_spent"] <= 5
    assert any("isn't enough" in warning for warning in body["warnings"])


def test_reroll_comes_with_props():
    room = client.post(
        "/api/rooms/reroll",
        json={"theme": "Midnight Manor", "order": 1, "budget": 150, "avoid": ROOM_NAMES[1:]},
    ).json()
    assert room["name"] == ROOM_NAMES[0]
    assert room["items"]
    assert room["spent"] <= 150


def test_catalog_endpoint():
    body = client.get("/api/catalog").json()
    assert body["source"] == "local"
    assert body["count"] == len(body["props"]) > 0


def test_pick_items_prefers_theme_and_fits_budget():
    props = [prop("big", 80), prop("small", 15), prop("fog", 40, theme="any"), prop("other", 5, theme="witch")]
    items = pick_items(100, ["ghost"], props)
    assert [i.id for i in items] == ["big", "small"]
    assert spent(items) == 95


def test_pick_items_stacks_only_cheap_decor():
    props = [prop("web", 5, category="Decoration"), prop("spider", 5), prop("clock", 30, category="Decoration")]
    quantities = {i.id: i.quantity for i in pick_items(200, ["ghost"], props)}
    assert quantities == {"web": 3, "spider": 1, "clock": 1}


def test_pick_items_skips_used():
    used = {"big", "fog"}
    props = [prop("big", 80), prop("small", 15), prop("fog", 40, theme="any")]
    items = pick_items(100, ["ghost"], props, used)
    assert [i.id for i in items] == ["small", "fog"]  # general effects can repeat
    assert used == {"big", "fog", "small"}


def test_room_theme_matches_frontend_rules():
    assert catalog.room_theme("Whispering Nursery") == "doll"
    assert catalog.room_theme("Moonlit Cellar") == "bat"
    assert catalog.room_theme("Laundry Room", "plain and quiet") == "ghost"  # no match falls back


def test_catalog_falls_back_when_snowflake_fails(monkeypatch):
    settings = catalog.get_settings()
    monkeypatch.setattr(settings, "catalog_source", "auto")
    monkeypatch.setattr(settings, "snowflake_account", "fake-account")
    monkeypatch.setattr(settings, "snowflake_user", "fake-user")

    def broken():
        raise RuntimeError("no warehouse")

    monkeypatch.setattr(catalog, "load_snowflake", broken)
    catalog.clear_cache()
    try:
        props, source = catalog.get_catalog()
        assert source == "local" and props
    finally:
        catalog.clear_cache()
