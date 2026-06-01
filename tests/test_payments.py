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

def create_test_booking(user_token, flight_id):
    """Create a booking via API"""
    return client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight_id}
    ).json()

# --- POST /payments ---
def test_create_payment():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id)
    booking = create_test_booking(user_token, flight.id)

    response = client.post("/payments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "booking_id": booking["id"],
            "amount": 299.99,
            "currency": "USD"
        }
    )
    assert response.status_code == 200
    assert response.json()["booking_id"] == booking["id"]
    assert response.json()["status"] == "pending"
    assert response.json()["amount"] == 299.99

def test_create_payment_invalid_booking():
    user_token = get_user_token()
    response = client.post("/payments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "booking_id": 999,  # doesn't exist
            "amount": 299.99,
            "currency": "USD"
        }
    )
    assert response.status_code == 404

def test_create_payment_duplicate():
    # Can't pay for same booking twice
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id)
    booking = create_test_booking(user_token, flight.id)

    # First payment
    client.post("/payments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"booking_id": booking["id"], "amount": 299.99, "currency": "USD"}
    )
    # Second payment — duplicate
    response = client.post("/payments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"booking_id": booking["id"], "amount": 299.99, "currency": "USD"}
    )
    assert response.status_code == 400

def test_create_payment_not_owned():
    # User 2 cannot pay for User 1's booking
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    second_token = get_second_user_token()
    flight = create_test_flight(origin_id, destination_id)
    booking = create_test_booking(user_token, flight.id)

    response = client.post("/payments",
        headers={"Authorization": f"Bearer {second_token}"},
        json={"booking_id": booking["id"], "amount": 299.99, "currency": "USD"}
    )
    assert response.status_code == 404

def test_create_payment_requires_auth():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id)
    booking = create_test_booking(user_token, flight.id)

    # No token
    response = client.post("/payments",
        json={"booking_id": booking["id"], "amount": 299.99, "currency": "USD"}
    )
    assert response.status_code == 401

def test_create_payment_invalid_currency():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id)
    booking = create_test_booking(user_token, flight.id)

    response = client.post("/payments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"booking_id": booking["id"], "amount": 299.99, "currency": "XYZ"}
    )
    assert response.status_code == 422

def test_create_payment_negative_amount():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id)
    booking = create_test_booking(user_token, flight.id)

    response = client.post("/payments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"booking_id": booking["id"], "amount": -100, "currency": "USD"}
    )
    assert response.status_code == 422

# --- GET /payments ---
def test_get_payments():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id)
    booking = create_test_booking(user_token, flight.id)

    client.post("/payments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"booking_id": booking["id"], "amount": 299.99, "currency": "USD"}
    )

    response = client.get("/payments",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["booking_id"] == booking["id"]

def test_get_payments_only_mine():
    # User should only see their own payments
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    second_token = get_second_user_token()
    flight = create_test_flight(origin_id, destination_id)

    # User 1 books and pays
    booking1 = create_test_booking(user_token, flight.id)
    client.post("/payments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"booking_id": booking1["id"], "amount": 299.99, "currency": "USD"}
    )

    # User 2 books and pays
    booking2 = create_test_booking(second_token, flight.id)
    client.post("/payments",
        headers={"Authorization": f"Bearer {second_token}"},
        json={"booking_id": booking2["id"], "amount": 299.99, "currency": "USD"}
    )

    # Each user should only see their own payment
    response = client.get("/payments",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert len(response.json()) == 1

def test_get_payments_requires_auth():
    response = client.get("/payments")
    assert response.status_code == 401

# --- GET /payments/{id} ---
def test_get_payment_by_id():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id)
    booking = create_test_booking(user_token, flight.id)

    payment = client.post("/payments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"booking_id": booking["id"], "amount": 299.99, "currency": "USD"}
    ).json()

    response = client.get(f"/payments/{payment['id']}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == payment["id"]

def test_get_payment_not_found():
    user_token = get_user_token()
    response = client.get("/payments/999",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 404

def test_get_payment_not_owned():
    # User 2 cannot see User 1's payment
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    second_token = get_second_user_token()
    flight = create_test_flight(origin_id, destination_id)
    booking = create_test_booking(user_token, flight.id)

    payment = client.post("/payments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"booking_id": booking["id"], "amount": 299.99, "currency": "USD"}
    ).json()

    response = client.get(f"/payments/{payment['id']}",
        headers={"Authorization": f"Bearer {second_token}"}
    )
    assert response.status_code == 404

# --- PUT /payments/{id} ---
def test_update_payment_status():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id)
    booking = create_test_booking(user_token, flight.id)

    payment = client.post("/payments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"booking_id": booking["id"], "amount": 299.99, "currency": "USD"}
    ).json()

    response = client.put(f"/payments/{payment['id']}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"status": "completed"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

def test_update_payment_invalid_status():
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    flight = create_test_flight(origin_id, destination_id)
    booking = create_test_booking(user_token, flight.id)

    payment = client.post("/payments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"booking_id": booking["id"], "amount": 299.99, "currency": "USD"}
    ).json()

    response = client.put(f"/payments/{payment['id']}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"status": "invalid_status"}  # not valid
    )
    assert response.status_code == 422

def test_update_payment_not_owned():
    # User 2 cannot update User 1's payment
    origin_id, destination_id = create_test_airports()
    user_token = get_user_token()
    second_token = get_second_user_token()
    flight = create_test_flight(origin_id, destination_id)
    booking = create_test_booking(user_token, flight.id)

    payment = client.post("/payments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"booking_id": booking["id"], "amount": 299.99, "currency": "USD"}
    ).json()

    response = client.put(f"/payments/{payment['id']}",
        headers={"Authorization": f"Bearer {second_token}"},
        json={"status": "completed"}
    )
    assert response.status_code == 404