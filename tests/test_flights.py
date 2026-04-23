import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base
from tests.conftest import TestingSessionLocal, test_engine

Base.metadata.create_all(bind=test_engine)

client = TestClient(app)

# Fixtures 
@pytest.fixture(autouse=True)  
def reset_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield

# Helpers functions
def get_admin_token():
    client.post("/users/register", json={
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@test.com",
        "password": "adminpass123"
    })
    db = TestingSessionLocal()
    from models.user import User
    user = db.query(User).filter(User.email == "admin@test.com").first()
    user.is_admin = True
    db.commit()
    db.close()
    response = client.post("/users/login",
        data={"username": "admin@test.com", "password": "adminpass123"}
    )
    return response.json()["access_token"]

def get_user_token():
    client.post("/users/register", json={
        "first_name": "Regular",
        "last_name": "User",
        "email": "user@test.com",
        "password": "userpass123"
    })
    response = client.post("/users/login",
        data={"username": "user@test.com", "password": "userpass123"}
    )
    return response.json()["access_token"]

def create_flight(token, overrides={}):
    """Helper to create a flight with optional field overrides."""
    payload = {
        "name": "AirAsia",
        "origin": "Kuala Lumpur",
        "destination": "Tokyo",
        "flight_number": "AK101",
        "boarding_time": "2026-06-01T10:00:00",
        "price": 299.99,
        "seats": 10,
        **overrides
    }
    return client.post("/flights",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )

# GET /flights 
def test_get_flights_empty():
    response = client.get("/flights")
    assert response.status_code == 200
    assert response.json() == []

def test_get_flights_returns_created():
    token = get_admin_token()
    create_flight(token)
    response = client.get("/flights")
    assert response.status_code == 200
    assert len(response.json()) == 1

# GET /flights/{id} 
def test_get_flight_by_id():
    token = get_admin_token()
    created = create_flight(token).json()
    response = client.get(f"/flights/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["name"] == "AirAsia"

def test_get_flight_not_found():
    response = client.get("/flights/999")
    assert response.status_code == 404

# POST /flights
def test_create_flight_as_admin():
    token = get_admin_token()
    response = create_flight(token)
    assert response.status_code == 200
    assert response.json()["name"] == "AirAsia"
    assert response.json()["seats"] == 10

def test_create_flight_as_regular_user():
    token = get_user_token()
    response = create_flight(token)
    assert response.status_code == 403

def test_create_flight_no_token():
    response = client.post("/flights", json={
        "name": "AirAsia",
        "origin": "Kuala Lumpur",
        "destination": "Tokyo",
        "flight_number": "AK101",
        "boarding_time": "2026-06-01T10:00:00",
        "price": 299.99,
        "seats": 10
    })
    assert response.status_code == 401

def test_create_duplicate_flight():
    token = get_admin_token()
    create_flight(token)  # first one succeeds
    response = create_flight(token)  # duplicate should fail
    assert response.status_code == 400

def test_create_flight_negative_price():
    token = get_admin_token()
    response = create_flight(token, {"price": -100})
    assert response.status_code == 422

def test_create_flight_zero_seats():
    token = get_admin_token()
    response = create_flight(token, {"seats": 0})
    assert response.status_code == 422

def test_create_flight_numeric_name():
    token = get_admin_token()
    response = create_flight(token, {"name": "12345"})
    assert response.status_code == 422

def test_create_flight_whitespace_name():
    token = get_admin_token()
    response = create_flight(token, {"name": "   "})
    assert response.status_code == 422

# DELETE /flights/{id}
def test_delete_flight_as_admin():
    token = get_admin_token()
    created = create_flight(token).json()
    response = client.delete(f"/flights/{created['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    # Confirm deletion
    assert client.get(f"/flights/{created['id']}").status_code == 404

# try with regular user
def test_delete_flight_as_regular_user():
    admin_token = get_admin_token()
    user_token = get_user_token()
    created = create_flight(admin_token).json()
    response = client.delete(f"/flights/{created['id']}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403

def test_delete_flight_not_found():
    token = get_admin_token()
    response = client.delete("/flights/999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

# PUT /flights/{id} 
def test_update_flight_price():
    token = get_admin_token()
    created = create_flight(token).json()
    response = client.put(f"/flights/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"price": 199.99}
    )
    assert response.status_code == 200
    assert response.json()["price"] == 199.99
    #check other fields
    assert response.json()["name"] == "AirAsia"  

def test_update_flight_seats():
    token = get_admin_token()
    created = create_flight(token).json()
    response = client.put(f"/flights/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"seats": 50}
    )
    assert response.status_code == 200
    assert response.json()["seats"] == 50

def test_update_flight_not_found():
    token = get_admin_token()
    response = client.put("/flights/999",
        headers={"Authorization": f"Bearer {token}"},
        json={"price": 199.99}
    )
    assert response.status_code == 404

def test_update_flight_as_regular_user():
    admin_token = get_admin_token()
    user_token = get_user_token()
    created = create_flight(admin_token).json()
    response = client.put(f"/flights/{created['id']}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"price": 199.99}
    )
    assert response.status_code == 403

def test_update_flight_negative_price():
    token = get_admin_token()
    created = create_flight(token).json()
    response = client.put(f"/flights/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"price": -50}
    )
    assert response.status_code == 422

# GET /flights/search
def test_search_flights_by_destination():
    token = get_admin_token()
    create_flight(token)
    response = client.get("/flights/search?destination=Tokyo")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["destination"] == "Tokyo"

def test_search_flights_no_results():
    response = client.get("/flights/search?destination=Paris")
    assert response.status_code == 200
    assert response.json() == []

def test_search_flights_with_max_price():
    token = get_admin_token()
    create_flight(token, {"price": 299.99})
    create_flight(token, {"flight_number": "AK102", "price": 599.99})
    response = client.get("/flights/search?destination=Tokyo&max_price=300")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["price"] == 299.99

def test_search_flights_max_price_zero():
    token = get_admin_token()
    create_flight(token)
    # max_price=0 should return no flights since price > 0
    response = client.get("/flights/search?destination=Tokyo&max_price=0")
    assert response.status_code == 200
    assert response.json() == []

# Pagination
def test_pagination():
    token = get_admin_token()
    for i in range(15):
        create_flight(token, {
            "flight_number": f"AK{i:03d}",
            "boarding_time": f"2026-06-{i+1:02d}T10:00:00" 
        })
    # offset = (1 - 1) * 10 = 0
    page1 = client.get("/flights?page=1&limit=10").json()
    page2 = client.get("/flights?page=2&limit=10").json()

    assert len(page1) == 10
    assert len(page2) == 5

def test_pagination_invalid_page():
    response = client.get("/flights?page=0")
    assert response.status_code == 400

def test_pagination_invalid_limit():
    response = client.get("/flights?limit=0")
    assert response.status_code == 400