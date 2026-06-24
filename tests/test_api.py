from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models import Document, KnowledgeBase, User


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)
    for table in (User.__table__, KnowledgeBase.__table__, Document.__table__):
        table.create(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def register_and_login(client: TestClient, username: str) -> str:
    response = client.post("/auth/register", json={"username": username, "password": "secret123"})
    assert response.status_code == 201

    response = client.post("/auth/login", json={"username": username, "password": "secret123"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_register_duplicate_username_fails(client: TestClient):
    payload = {"username": "alice", "password": "secret123"}

    assert client.post("/auth/register", json=payload).status_code == 201
    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400


def test_protected_endpoint_requires_jwt(client: TestClient):
    response = client.get("/knowledge-bases")

    assert response.status_code == 401


def test_user_cannot_access_another_users_knowledge_base(client: TestClient):
    alice_token = register_and_login(client, "alice")
    bob_token = register_and_login(client, "bob")

    response = client.post(
        "/knowledge-bases",
        json={"name": "Alice KB", "description": "private"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert response.status_code == 201
    kb_id = response.json()["id"]

    response = client.get(
        f"/knowledge-bases/{kb_id}/documents",
        headers={"Authorization": f"Bearer {bob_token}"},
    )

    assert response.status_code == 403


def test_reject_unsupported_upload_file_type(client: TestClient):
    token = register_and_login(client, "alice")
    response = client.post(
        "/knowledge-bases",
        json={"name": "Demo KB"},
        headers={"Authorization": f"Bearer {token}"},
    )
    kb_id = response.json()["id"]

    response = client.post(
        f"/knowledge-bases/{kb_id}/documents",
        files={"file": ("demo.docx", b"not supported", "application/octet-stream")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
