import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base
from tests.conftest import TestingSessionLocal, test_engine
from datetime import datetime, timedelta

Base.metadata.create_all(bind=test_engine)

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield

# --- Helpers ---
def create_test_airports():
    from models.airport import Airport
    db = TestingSessionLocal()
    origin = Airport(
        code="KUL",
        name="Kuala Lumpur International",
        city="Kuala Lumpur",
        country="Malaysia",
        timezone="Asia/Kuala_Lumpur"
    )
    destination = Airport(
        code="NRT",
        name="Narita International",
        city="Tokyo",
        country="Japan",
        timezone="Asia/Tokyo"
    )
    db.add(origin)
    db.add(destination)
    db.commit()
    db.refresh(origin)
    db.refresh(destination)
    db.close()
    return origin.id, destination.id

def create_test_flight(origin_id, destination_id, overrides={}):
    from models.flight import Flight
    db = TestingSessionLocal()
    future = datetime.now() + timedelta(days=30)
    arrival = datetime.now() + timedelta(days=30, hours=7)
    payload = {
        "name": "AirAsia",
        "origin_id": origin_id,
        "destination_id": destination_id,
        "flight_number": "AK101",
        "boarding_time": future,
        "arrival_time": arrival,
        "price": 299.99,
        "seats": 10,
        **overrides
    }
    flight = Flight(**payload)
    db.add(flight)
    db.commit()
    db.refresh(flight)
    db.close()
    return flight

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

# --- GET /flights ---
def test_get_flights_empty():
    response = client.get("/flights")
    assert response.status_code == 200
    assert response.json() == []

def test_get_flights_returns_created():
    origin_id, destination_id = create_test_airports()
    create_test_flight(origin_id, destination_id)
    response = client.get("/flights")
    assert response.status_code == 200
    assert len(response.json()) == 1

# --- GET /flights/{id} ---
def test_get_flight_by_id():
    origin_id, destination_id = create_test_airports()
    flight = create_test_flight(origin_id, destination_id)
    response = client.get(f"/flights/{flight.id}")
    assert response.status_code == 200
    assert response.json()["id"] == flight.id
    assert response.json()["name"] == "AirAsia"

def test_get_flight_not_found():
    response = client.get("/flights/999")
    assert response.status_code == 404

# --- GET /flights/search ---
def test_search_flights_by_destination():
    origin_id, destination_id = create_test_airports()  # ← only once
    create_test_flight(origin_id, destination_id)
    response = client.get("/flights/search?destination=NRT")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_search_flights_no_results():
    create_test_airports()
    # valid airport code but no flights
    response = client.get("/flights/search?destination=NRT")
    assert response.status_code == 404
    assert "No flights found" in response.json()["message"]

def test_search_flights_invalid_airport_code():
    # airport code doesn't exist
    response = client.get("/flights/search?destination=XXX")
    assert response.status_code == 404
    assert "Airport" in response.json()["message"]

def test_search_flights_with_max_price():
    origin_id, destination_id = create_test_airports()
    create_test_flight(origin_id, destination_id, {"price": 299.99})
    create_test_flight(origin_id, destination_id, {
        "flight_number": "AK102",
        "price": 599.99
    })
    response = client.get("/flights/search?destination=NRT&max_price=300")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["price"] == 299.99

def test_search_flights_max_price_zero():
    origin_id, destination_id = create_test_airports()
    create_test_flight(origin_id, destination_id)
    response = client.get("/flights/search?destination=NRT&max_price=0")
    assert response.status_code == 404

# --- Pagination ---
def test_pagination():
    origin_id, destination_id = create_test_airports()
    for i in range(15):
        create_test_flight(origin_id, destination_id, {
            "flight_number": f"AK{i:03d}",
            "boarding_time": datetime.now() + timedelta(days=30+i),
            "arrival_time": datetime.now() + timedelta(days=30+i, hours=7)
        })
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