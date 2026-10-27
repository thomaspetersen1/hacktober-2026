from fastapi.testclient import TestClient

from app.main import app
from app.services.budget import allocate

client = TestClient(app)


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_plan_allocates_full_budget():
    res = client.post("/api/plan", json={"budget": 500, "rooms": 4})
    assert res.status_code == 200
    body = res.json()
    assert len(body["rooms"]) == 4
    assert body["total_allocated"] == 500


def test_plan_rejects_bad_input():
    res = client.post("/api/plan", json={"budget": 0, "rooms": 4})
    assert res.status_code == 422


def test_plan_has_expected_shape():
    res = client.post("/api/plan", json={"budget": 250, "rooms": 3})
    assert res.status_code == 200
    body = res.json()
    assert body["budget"] == 250
    assert body["total_allocated"] == 250
    assert len(body["rooms"]) == 3
    assert all(room["budget"] > 0 for room in body["rooms"])


def test_allocate_sums_exactly():
    for budget in (1, 99.99, 333.33, 1000):
        for rooms in range(1, 13):
            assert round(sum(allocate(budget, rooms)), 2) == round(budget, 2)


def test_reroll_returns_a_new_room_with_same_slot():
    avoid = ["Entry Hall", "Mirror Gallery", "Whispering Nursery"]
    res = client.post(
        "/api/rooms/reroll",
        json={"theme": "Midnight Manor", "order": 2, "budget": 120.5, "avoid": avoid},
    )
    assert res.status_code == 200
    room = res.json()
    assert room["order"] == 2
    assert room["budget"] == 120.5
    assert room["name"] not in avoid


def test_reroll_rejects_bad_input():
    res = client.post("/api/rooms/reroll", json={"theme": "x", "order": 0, "budget": 10})
    assert res.status_code == 422
