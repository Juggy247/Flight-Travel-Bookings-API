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

# helper functions

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

def create_flight(token, overrides={}):
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

# tests

def test_create_booking():
    
    admin_token = get_admin_token()
    user_token = get_user_token()
    flight = create_flight(admin_token).json()

    response = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight["id"]}
    )

    assert response.status_code == 200
    assert response.json()["flight_id"] == flight["id"]
    assert response.json()["status"] == "confirmed"

def test_create_booking_seat_decreases():
    
    admin_token = get_admin_token()
    user_token = get_user_token()
    flight = create_flight(admin_token, {"seats": 10}).json()

    client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight["id"]}
    )

    # Check seats are decreased
    updated_flight = client.get(f"/flights/{flight['id']}").json()
    assert updated_flight["seats"] == 9  

def test_create_booking_no_seats():
    # Flight with 0 seats should be rejected
    admin_token = get_admin_token()
    user_token = get_user_token()
    flight = create_flight(admin_token, {"seats": 1}).json()

    # first user books the last seat
    client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight["id"]}
    )

    # second user tries to book with no seats left
    second_token = get_second_user_token()
    response = client.post("/bookings",
        headers={"Authorization": f"Bearer {second_token}"},
        json={"flight_id": flight["id"]}
    )
    assert response.status_code == 400

def test_create_booking_duplicate():
    # Same user booking same flight twice should be rejected
    admin_token = get_admin_token()
    user_token = get_user_token()
    flight = create_flight(admin_token).json()

    # First booking
    client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight["id"]}
    )
    # Second booking with same user and flight
    response = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight["id"]}
    )
    assert response.status_code == 400

def test_create_booking_invalid_flight():
    user_token = get_user_token()
    response = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": 999}  # flight 999 doesn't exist
    )
    assert response.status_code == 404

def test_create_booking_requires_auth():
    admin_token = get_admin_token()
    flight = create_flight(admin_token).json()
    # No token 
    response = client.post("/bookings",
        json={"flight_id": flight["id"]}
    )
    assert response.status_code == 401

def test_get_my_bookings():
    admin_token = get_admin_token()
    user_token = get_user_token()
    flight = create_flight(admin_token).json()

    client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight["id"]}
    )

    response = client.get("/bookings/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["flight_id"] == flight["id"]

def test_get_my_bookings_only_mine():
    # User should only see THEIR bookings, not other users' bookings
    admin_token = get_admin_token()
    user_token = get_user_token()
    second_token = get_second_user_token()

    flight = create_flight(admin_token).json()

    # Both users book the same flight
    client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight["id"]}
    )
    client.post("/bookings",
        headers={"Authorization": f"Bearer {second_token}"},
        json={"flight_id": flight["id"]}
    )

    # Each user should only see 1 booking — their own
    response = client.get("/bookings/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert len(response.json()) == 1

def test_delete_booking():
    admin_token = get_admin_token()
    user_token = get_user_token()
    flight = create_flight(admin_token, {"seats": 10}).json()

    booking = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight["id"]}
    ).json()

    response = client.delete(f"/bookings/{booking['id']}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200

def test_delete_booking_seat_restored():
    # Most important side effect test — seat must come back after cancellation
    admin_token = get_admin_token()
    user_token = get_user_token()
    flight = create_flight(admin_token, {"seats": 10}).json()

    booking = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight["id"]}
    ).json()
    # seats are now 9

    client.delete(f"/bookings/{booking['id']}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    # seats should be back to 10

    updated_flight = client.get(f"/flights/{flight['id']}").json()
    assert updated_flight["seats"] == 10  # ✅ seat restored

def test_delete_booking_not_owned():
    # User A cannot cancel User B's booking
    admin_token = get_admin_token()
    user_token = get_user_token()
    second_token = get_second_user_token()
    flight = create_flight(admin_token).json()

    # User 1 books
    booking = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight["id"]}
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

def test_update_booking_cancel():
    admin_token = get_admin_token()
    user_token = get_user_token()
    flight = create_flight(admin_token, {"seats": 10}).json()

    booking = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight["id"]}
    ).json()

    response = client.put(f"/bookings/{booking['id']}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"status": "cancelled"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

def test_update_booking_cancel_restores_seat():
    # Cancelling with PUT method should also restore the seat
    admin_token = get_admin_token()
    user_token = get_user_token()
    flight = create_flight(admin_token, {"seats": 10}).json()

    booking = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight["id"]}
    ).json()
    # seats should be change to 9

    client.put(f"/bookings/{booking['id']}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"status": "cancelled"}
    )
    # seats should be back to 10

    updated_flight = client.get(f"/flights/{flight['id']}").json()
    assert updated_flight["seats"] == 10

def test_update_booking_invalid_status():
    admin_token = get_admin_token()
    user_token = get_user_token()
    flight = create_flight(admin_token).json()

    booking = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight["id"]}
    ).json()

    response = client.put(f"/bookings/{booking['id']}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"status": "flying"}  # not a valid status
    )
    assert response.status_code == 422

def test_update_booking_not_owned():
    admin_token = get_admin_token()
    user_token = get_user_token()
    second_token = get_second_user_token()
    flight = create_flight(admin_token).json()

    booking = client.post("/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"flight_id": flight["id"]}
    ).json()

    # User 2 tries to update User 1's booking
    response = client.put(f"/bookings/{booking['id']}",
        headers={"Authorization": f"Bearer {second_token}"},
        json={"status": "cancelled"}
    )
    assert response.status_code == 404