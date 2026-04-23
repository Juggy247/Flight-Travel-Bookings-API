import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base
from tests.conftest import TestingSessionLocal, test_engine

Base.metadata.create_all(bind=test_engine)
client = TestClient(app)

# Helper function
@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield

# Helper function
def get_user_token():
    client.post("/users/register", json={
        "first_name": "Regular",
        "last_name": "User",
        "email": "getme@test.com",   
        "password": "userpass123"
    })
    response = client.post("/users/login",
        data={"username": "getme@test.com", "password": "userpass123"}
    )
    return response.json()["access_token"]
# Tests

def test_register_user():
    response = client.post("/users/register",
                        json={
                            "first_name": "Thiri",
                            "last_name": "Zin",
                            "email": "thirittzin@example.com",
                            "password": "12433dd1",
                            "phone": "690234123"
                        } )
    assert response.status_code == 200
    assert response.json()["email"] == "thirittzin@example.com"

def test_register_missing_required_field():
    response = client.post("/users/register",
        json={
            # first_name missing 
            "last_name": "Doe",
            "email": "john@test.com",
            "password": "password123"
        }
    )
    assert response.status_code == 422

def test_register_duplicate_email():

    client.post("/users/register",
                    json={
                        "first_name": "MAX",
                        "last_name": "V",
                        "email": "thirittzin@example.com",
                        "password": "1dqqw324",
                        "phone": "23814355"
                    } )
    response = client.post("/users/register",
                    json={
                        "first_name": "MAX",
                        "last_name": "V",
                        "email": "thirittzin@example.com",
                        "password": "1dqqw324",
                        "phone": "23814355"
                    } )
    assert response.status_code == 409
    
def test_register_invalid_email():
    response = client.post("/users/register",
                    json={
                        "first_name": "testuser",
                        "last_name": "test",
                        "email": "notanemail",
                        "password": "1dqqw324",
                        "phone": "23814355"
                    } )
    assert response.status_code == 422

def test_register_short_password():
    response = client.post("/users/register",
                    json={
                        "first_name": "testuser",
                        "last_name": "test",
                        "email": "testuser@example.com",  
                        "password": "1dqq",               
                        "phone": "23814355"
                    } )
    assert response.status_code == 422

def test_login_success():
    client.post("/users/register", json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@test.com",
        "password": "password123"
    })
    response = client.post("/users/login",
        data={"username": "john@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password():

    client.post("/users/register", json={
        "first_name": "Test",
        "last_name": "User",
        "email": "thirittzin@example.com", 
        "password": "12433dd1"
    })
    
    response = client.post("/users/login",
        data={"username": "thirittzin@example.com", "password": "wrongpassword"})
    
    assert response.status_code == 401

def test_get_me():
    token = get_user_token()
    response = client.get("/users/me",
                          headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "getme@test.com"

def test_login_nonexistent_email():
    # no user register case
    response = client.post("/users/login",
                           data={"username": "nobody@test.com", "password": "password123"})
    
    assert response.status_code == 401

def test_login_inactive_user():
    # register a user then deactivate them directly in DB
    client.post("/users/register", json={
        "first_name": "Inactive",
        "last_name": "User",
        "email": "inactive@test.com",
        "password": "password123"
    })
    # Deactivate directly in DB 
    db = TestingSessionLocal()
    from models.user import User
    user = db.query(User).filter(User.email == "inactive@test.com").first()
    user.is_active = False
    db.commit()
    db.close()

    
    response = client.post("/users/login",
        data={"username": "inactive@test.com", "password": "password123"}
    )
    
    assert response.status_code == 403

def test_get_me_no_token():
    # no Authorization header 
    response = client.get("/users/me")
 
    assert response.status_code == 401


def test_get_me_invalid_token():
    # send a fake token
    response = client.get("/users/me",
        headers={"Authorization": "Bearer thisIsNotAValidToken"}
    )

    assert response.status_code == 401