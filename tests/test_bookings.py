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
    """Create airports directly in DB — managed via sqladmin"""
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
    """Create flight directly in DB — managed via sqladmin"""
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

def get_second_user_token():
    client.post("/users/register", json={
        "first_name": "Second",
        "last_name": "User",
        "email": "user2@test.com",
        "password": "userpass123"
    })
    response = client.post("/users/login",
        data={"username": "user2@test.com", "password": "userpass123"}
    )
    return response.json()["access_token"]

# --- POST /bookings ---
def test_create_booking():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id)

    response = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight.id}
    )
    assert response.status_code == 200
    assert response.json()["flight_id"] == flight.id
    assert response.json()["status"] == "confirmed"

def test_create_booking_seat_decreases():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id, {"seats": 10})

    client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight.id}
    )
    # Check seats decreased
    updated_flight = client.get(f"/flights/{flight.id}").json()
    assert updated_flight["seats"] == 9

def test_create_booking_no_seats():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    # Create flight with only 1 seat
    flight = create_test_flight(origin_id, destination_id, {"seats": 1})

    # First user books the last seat
    client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight.id}
    )
    # Second user tries to book — no seats left
    second_token = get_second_user_token()
    response = client.post("/bookings",
        headers={"Authorization": f"Bearer {second_token}"},
        json={"flight_id": flight.id}
    )
    assert response.status_code == 400

def test_create_booking_duplicate():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id)

    # First booking
    client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight.id}
    )
    # Second booking — same user same flight
    response = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight.id}
    )
    assert response.status_code == 400

def test_create_booking_invalid_flight():
    user_token = get_user_token()
    response = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": 999}  # flight doesn't exist
    )
    assert response.status_code == 404

def test_create_booking_requires_auth():
    origin_id, destination_id = create_test_airports()
    flight = create_test_flight(origin_id, destination_id)
    # No token
    response = client.post("/bookings",
        json={"flight_id": flight.id}
    )
    assert response.status_code == 401

# --- GET /bookings ---
def test_get_my_bookings():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id)

    client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight.id}
    )
    # GET /bookings — returns only current user's bookings
    response = client.get("/bookings",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["flight_id"] == flight.id

def test_get_my_bookings_only_mine():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    second_token = get_second_user_token()
    flight = create_test_flight(origin_id, destination_id)

    # Both users book same flight
    client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight.id}
    )
    client.post("/bookings",
        headers={"Authorization": f"Bearer {second_token}"},
        json={"flight_id": flight.id}
    )
    # Each user should only see their own booking
    response = client.get("/bookings",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert len(response.json()) == 1

# --- DELETE /bookings/{id} ---
def test_delete_booking():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id, {"seats": 10})

    booking = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight.id}
    ).json()

    response = client.delete(f"/bookings/{booking['id']}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 204

def test_delete_booking_seat_restored():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id, {"seats": 10})

    booking = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight.id}
    ).json()
    # seats now 9

    client.delete(f"/bookings/{booking['id']}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    # seats should be back to 10
    updated_flight = client.get(f"/flights/{flight.id}").json()
    assert updated_flight["seats"] == 10

def test_delete_booking_not_owned():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    second_token = get_second_user_token()
    flight = create_test_flight(origin_id, destination_id)

    # User 1 books
    booking = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight.id}
    ).json()

    # User 2 tries to cancel User 1's booking
    response = client.delete(f"/bookings/{booking['id']}",
        headers={"Authorization": f"Bearer {second_token}"}
    )
    assert response.status_code == 404

def test_delete_booking_not_found():
    user_token = get_user_token()
    response = client.delete("/bookings/999",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 404

# --- PUT /bookings/{id} ---
def test_update_booking_cancel():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id, {"seats": 10})

    booking = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight.id}
    ).json()

    response = client.put(f"/bookings/{booking['id']}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"status": "cancelled"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

def test_update_booking_cancel_restores_seat():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id, {"seats": 10})

    booking = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight.id}
    ).json()
    # seats now 9

    client.put(f"/bookings/{booking['id']}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"status": "cancelled"}
    )
    # seats should be back to 10
    updated_flight = client.get(f"/flights/{flight.id}").json()
    assert updated_flight["seats"] == 10

def test_update_booking_invalid_status():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id)

    booking = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight.id}
    ).json()

    response = client.put(f"/bookings/{booking['id']}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"status": "flying"}  # invalid status
    )
    assert response.status_code == 422

def test_update_booking_not_owned():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    second_token = get_second_user_token()
    flight = create_test_flight(origin_id, destination_id)

    booking = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight.id}
    ).json()

    # User 2 tries to update User 1's booking
    response = client.put(f"/bookings/{booking['id']}",
        headers={"Authorization": f"Bearer {second_token}"},
        json={"status": "cancelled"}
    )
    assert response.status_code == 404