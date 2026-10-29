"""
Tests for restocking API endpoints.
"""
import pytest
from mock_data import submitted_orders


@pytest.fixture(autouse=True)
def clear_submitted_orders():
    """Reset in-memory submitted orders so tests don't leak state."""
    submitted_orders.clear()
    yield
    submitted_orders.clear()


def make_payload(budget=10000, items=None):
    if items is None:
        items = [
            {"sku": "WDG-001", "name": "Industrial Widget Type A", "category": "Widgets",
             "quantity": 100, "unit_cost": 12.5},
            {"sku": "MTR-304", "name": "Electric Motor 5HP", "category": "Motors",
             "quantity": 5, "unit_cost": 420.0},
        ]
    return {"budget": budget, "items": items}


class TestRestockingEndpoints:
    """Test suite for restocking order endpoints."""

    def test_demand_forecasts_include_cost_fields(self, client):
        """Demand forecasts carry the fields needed for restocking."""
        data = client.get("/api/demand").json()
        for forecast in data:
            assert forecast["unit_cost"] is not None
            assert forecast["stock_on_hand"] is not None
            assert forecast["category"]

    def test_create_restock_order(self, client):
        """A valid order is stored with the longest category lead time."""
        response = client.post("/api/restocking/orders", json=make_payload())
        assert response.status_code == 201
        order = response.json()
        assert order["order_number"].startswith("RST-")
        assert order["total_cost"] == 100 * 12.5 + 5 * 420.0
        assert order["lead_time_days"] == 28  # Motors is the slowest category
        assert order["status"] == "Submitted"
        assert order["expected_delivery_date"] > order["submitted_date"]

    def test_unknown_category_uses_default_lead_time(self, client):
        items = [{"sku": "X-1", "name": "Mystery", "category": None, "quantity": 1, "unit_cost": 1.0}]
        response = client.post("/api/restocking/orders", json=make_payload(items=items))
        assert response.status_code == 201
        assert response.json()["lead_time_days"] == 14

    def test_create_restock_order_empty_items(self, client):
        response = client.post("/api/restocking/orders", json=make_payload(items=[]))
        assert response.status_code == 400

    def test_create_restock_order_over_budget(self, client):
        response = client.post("/api/restocking/orders", json=make_payload(budget=100))
        assert response.status_code == 400
        assert "budget" in response.json()["detail"].lower()

    def test_create_restock_order_invalid_quantity(self, client):
        items = [{"sku": "X-1", "name": "Bad", "category": "Widgets", "quantity": 0, "unit_cost": 1.0}]
        response = client.post("/api/restocking/orders", json=make_payload(items=items))
        assert response.status_code == 400

    def test_list_restock_orders_newest_first(self, client):
        client.post("/api/restocking/orders", json=make_payload())
        client.post("/api/restocking/orders", json=make_payload())
        orders = client.get("/api/restocking/orders").json()
        assert [o["id"] for o in orders] == ["2", "1"]

    def test_list_restock_orders_empty(self, client):
        response = client.get("/api/restocking/orders")
        assert response.status_code == 200
        assert response.json() == []
