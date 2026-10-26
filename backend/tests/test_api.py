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


def test_plan_square_feet_is_optional():
    res = client.post("/api/plan", json={"budget": 500, "rooms": 4, "square_feet": 1200})
    assert res.status_code == 200
    assert res.json()["square_feet"] == 1200
    res = client.post("/api/plan", json={"budget": 500, "rooms": 4, "square_feet": 0})
    assert res.status_code == 422


def test_allocate_sums_exactly():
    for budget in (1, 99.99, 333.33, 1000):
        for rooms in range(1, 13):
            assert round(sum(allocate(budget, rooms)), 2) == round(budget, 2)
