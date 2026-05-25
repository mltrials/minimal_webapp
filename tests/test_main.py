import os
from app.main import app
import pytest
from fastapi.testclient import TestClient


client = TestClient(app)


# -----------------------------
# 1. Root endpoint test
# -----------------------------
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello FastAPI"}
    

# -----------------------------
# 2. Item creation test (POST)
# -----------------------------
def test_create_item():
    payload = {
        "name": "phone",
        "price": 100.0,
        "tags": ["tech"]
    }

    response = client.post("/items/", json=payload)

    assert response.status_code == 200
    assert response.json()["item"]["name"] == "phone"
    
    
# -----------------------------
# 3. Path parameter test + error case
# -----------------------------
def test_get_item_not_found():
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"
    
    
# -----------------------------
# 4. Query + dependency test
# -----------------------------
def test_list_items():
    response = client.get("/items/?q=abc&limit=5")

    assert response.status_code == 200
    assert response.json()["params"]["q"] == "abc"
    assert response.json()["params"]["limit"] == 5