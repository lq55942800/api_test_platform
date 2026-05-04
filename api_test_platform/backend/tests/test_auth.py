import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.base_models import Team, User, TeamMember
from app.services.auth_service import get_password_hash

TEST_DATABASE_URL = "sqlite:///./test_auth.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    team = Team(id=1, name="Default Team", description="Test team", is_active=True)
    db.add(team)
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)


def test_register_success():
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["username"] == "testuser"


def test_register_duplicate_username():
    client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test1@example.com",
        "password": "TestPass123",
    })
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test2@example.com",
        "password": "TestPass123",
    })
    assert response.status_code == 409


def test_register_weak_password():
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "weak",
    })
    assert response.status_code == 422


def test_login_success():
    db = TestingSessionLocal()
    user = User(
        username="loginuser",
        email="login@example.com",
        password_hash=get_password_hash("TestPass123"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.close()

    response = client.post("/api/v1/auth/login", json={
        "username": "loginuser",
        "password": "TestPass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password():
    db = TestingSessionLocal()
    user = User(
        username="wronguser",
        email="wrong@example.com",
        password_hash=get_password_hash("TestPass123"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.close()

    response = client.post("/api/v1/auth/login", json={
        "username": "wronguser",
        "password": "WrongPass123",
    })
    assert response.status_code == 401


def test_login_locked_account():
    db = TestingSessionLocal()
    from datetime import datetime, timedelta
    user = User(
        username="lockeduser",
        email="locked@example.com",
        password_hash=get_password_hash("TestPass123"),
        is_active=True,
        login_fail_count=5,
        locked_until=datetime.utcnow() + timedelta(minutes=30),
    )
    db.add(user)
    db.commit()
    db.close()

    response = client.post("/api/v1/auth/login", json={
        "username": "lockeduser",
        "password": "TestPass123",
    })
    assert response.status_code == 423


def test_get_me_authenticated():
    reg_response = client.post("/api/v1/auth/register", json={
        "username": "meuser",
        "email": "me@example.com",
        "password": "TestPass123",
    })
    token = reg_response.json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "meuser"


def test_get_me_unauthenticated():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_refresh_token():
    reg_response = client.post("/api/v1/auth/register", json={
        "username": "refreshuser",
        "email": "refresh@example.com",
        "password": "TestPass123",
    })
    refresh_token = reg_response.json()["refresh_token"]

    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_logout():
    reg_response = client.post("/api/v1/auth/register", json={
        "username": "logoutuser",
        "email": "logout@example.com",
        "password": "TestPass123",
    })
    token = reg_response.json()["access_token"]

    response = client.post("/api/v1/auth/logout", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200


def test_change_password():
    db = TestingSessionLocal()
    user = User(
        username="changepw",
        email="changepw@example.com",
        password_hash=get_password_hash("OldPass123"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.close()

    login_response = client.post("/api/v1/auth/login", json={
        "username": "changepw",
        "password": "OldPass123",
    })
    token = login_response.json()["access_token"]

    response = client.put("/api/v1/auth/password", json={
        "old_password": "OldPass123",
        "new_password": "NewPass456",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
