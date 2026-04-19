import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base,get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_users.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] =override_get_db
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
        "email": "getme@test.com",   # ← different email
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
                        "email": "notanemail",
                        "password": "1dqq",
                        "phone": "23814355"
                    } )
    assert response.status_code == 422

def test_login_success():
    token = get_user_token()
    assert token is not None
    
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