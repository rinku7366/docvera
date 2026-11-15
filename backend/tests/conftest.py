import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

# Use an in-memory SQLite database for tests.
# Why: isolates tests from the real database so they can run in any order
# without leaving data behind.
SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Create all tables before each test, drop them after."""
    import app.models.user
    import app.models.document
    import app.models.query
    import app.models.verification
    import app.models.translation
    import app.models.audit
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(setup_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """Create a test user and return (client, token, user_data)."""
    resp = client.post("/auth/register", json={"email": "test@docvera.test", "password": "testpass123"})
    assert resp.status_code == 201
    login = client.post("/auth/login", json={"email": "test@docvera.test", "password": "testpass123"})
    token = login.json()["access_token"]
    return client, token, {"email": "test@docvera.test"}


@pytest.fixture
def second_user(client):
    """Create a second user to test cross-user ownership protection."""
    client.post("/auth/register", json={"email": "other@docvera.test", "password": "otherpass123"})
    login = client.post("/auth/login", json={"email": "other@docvera.test", "password": "otherpass123"})
    token = login.json()["access_token"]
    return client, token
