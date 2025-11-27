from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_reservation_endpoint():
    payload = {
        "name": "Test User",
        "date": "2025-12-25",
        "time": "19:00",
        "guests": 2,
        "special_requests": "window seat",
    }
    resp = client.post("/reservation", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["confirmed"] is True
    assert "RSV" in body["reference"]


def test_order_endpoint():
    payload = {
        "table": "12",
        "items": [{"item": "Pasta", "quantity": 2}, {"item": "Salad", "quantity": 1}],
    }
    resp = client.post("/order", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["confirmed"] is True
    assert body["total_items"] == 3
