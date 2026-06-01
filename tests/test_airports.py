import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base
from tests.conftest import TestingSessionLocal, test_engine

Base.metadata.create_all(bind=test_engine)

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield

# --- Helpers ---
def create_test_airport(overrides={}):
    """Create airport directly in DB — managed via sqladmin"""
    from models.airport import Airport
    db = TestingSessionLocal()
    payload = {
        "code": "KUL",
        "name": "Kuala Lumpur International Airport",
        "city": "Kuala Lumpur",
        "country": "Malaysia",
        "timezone": "Asia/Kuala_Lumpur",
        **overrides
    }
    airport = Airport(**payload)
    db.add(airport)
    db.commit()
    db.refresh(airport)
    db.close()
    return airport

# --- GET /airports ---
def test_get_airports_empty():
    response = client.get("/airports")
    assert response.status_code == 200
    assert response.json() == []

def test_get_airports_returns_created():
    create_test_airport()
    response = client.get("/airports")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["code"] == "KUL"

# --- GET /airports/{id} ---
def test_get_airport_by_id():
    airport = create_test_airport()
    response = client.get(f"/airports/{airport.id}")
    assert response.status_code == 200
    assert response.json()["id"] == airport.id
    assert response.json()["code"] == "KUL"
    assert response.json()["city"] == "Kuala Lumpur"

def test_get_airport_not_found():
    response = client.get("/airports/999")
    assert response.status_code == 404

# --- GET /airports/search ---
def test_search_airports_by_city():
    create_test_airport()
    response = client.get("/airports/search?city=Kuala Lumpur")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["city"] == "Kuala Lumpur"

def test_search_airports_by_country():
    create_test_airport()
    response = client.get("/airports/search?country=Malaysia")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["country"] == "Malaysia"

def test_search_airports_case_insensitive():
    # ilike search should be case insensitive
    create_test_airport()
    response = client.get("/airports/search?city=kuala lumpur")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_search_airports_partial_match():
    # ilike with % should match partial strings
    create_test_airport()
    response = client.get("/airports/search?city=Kuala")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_search_airports_by_city_and_country():
    create_test_airport()
    create_test_airport({
        "code": "SIN",
        "name": "Singapore Changi Airport",
        "city": "Singapore",
        "country": "Singapore",
        "timezone": "Asia/Singapore"
    })
    # filter by both city and country
    response = client.get("/airports/search?city=Kuala Lumpur&country=Malaysia")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["code"] == "KUL"

def test_search_airports_no_results():
    response = client.get("/airports/search?city=NonExistentCity")
    assert response.status_code == 200
    assert response.json() == []

# --- Pagination ---
def test_pagination_airports():
    # Create 15 airports with unique codes
    for i in range(15):
        create_test_airport({
            "code": f"A{i:02d}",  # A00, A01... A14
            "city": f"City{i}",
            "country": f"Country{i}",
            "timezone": "Asia/Kuala_Lumpur"
        })
    page1 = client.get("/airports?page=1&limit=10").json()
    page2 = client.get("/airports?page=2&limit=10").json()
    assert len(page1) == 10
    assert len(page2) == 5

def test_pagination_invalid_page():
    response = client.get("/airports?page=0")
    assert response.status_code == 400

def test_pagination_invalid_limit():
    response = client.get("/airports?limit=0")
    assert response.status_code == 400