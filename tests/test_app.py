import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app
from database import Base, get_db

# ── Test Database (in-memory SQLite) ────────────────────────────────
SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


client = TestClient(app)


# ── Health ────────────────────────────────────────────────────────────
def test_health_returns_200():
    res = client.get("/health")
    assert res.status_code == 200


def test_health_reports_status():
    res = client.get("/health")
    assert res.json()["status"] == "healthy"


# ── Categories ────────────────────────────────────────────────────────
def test_create_category_returns_201():
    res = client.post("/categories", json={"name": "Docker", "description": "Container tools"})
    assert res.status_code == 201


def test_create_duplicate_category_returns_400():
    client.post("/categories", json={"name": "Docker"})
    res = client.post("/categories", json={"name": "Docker"})
    assert res.status_code == 400


def test_list_categories_returns_200():
    res = client.get("/categories")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


# ── Snippets ──────────────────────────────────────────────────────────
def _create_category():
    res = client.post("/categories", json={"name": "Linux"})
    return res.json()["id"]


def test_create_snippet_returns_201():
    cat_id = _create_category()
    res = client.post("/snippets", json={
        "category_id": cat_id,
        "title": "Check disk usage",
        "command": "df -h",
        "description": "Shows disk space",
        "tags": ["linux", "disk"]
    })
    assert res.status_code == 201


def test_create_snippet_with_invalid_category_returns_404():
    res = client.post("/snippets", json={
        "category_id": 9999,
        "title": "Test",
        "command": "echo test"
    })
    assert res.status_code == 404


def test_list_snippets_returns_200():
    res = client.get("/snippets")
    assert res.status_code == 200


def test_get_snippet_by_id():
    cat_id = _create_category()
    create_res = client.post("/snippets", json={
        "category_id": cat_id, "title": "Find me", "command": "echo hi"
    })
    snippet_id = create_res.json()["id"]
    res = client.get(f"/snippets/{snippet_id}")
    assert res.status_code == 200
    assert res.json()["title"] == "Find me"


def test_get_nonexistent_snippet_returns_404():
    res = client.get("/snippets/99999")
    assert res.status_code == 404


def test_update_snippet():
    cat_id = _create_category()
    create_res = client.post("/snippets", json={
        "category_id": cat_id, "title": "Old title", "command": "echo old"
    })
    snippet_id = create_res.json()["id"]
    res = client.put(f"/snippets/{snippet_id}", json={"title": "New title"})
    assert res.status_code == 200
    assert res.json()["title"] == "New title"


def test_delete_snippet():
    cat_id = _create_category()
    create_res = client.post("/snippets", json={
        "category_id": cat_id, "title": "Delete me", "command": "echo bye"
    })
    snippet_id = create_res.json()["id"]
    res = client.delete(f"/snippets/{snippet_id}")
    assert res.status_code == 200
    get_res = client.get(f"/snippets/{snippet_id}")
    assert get_res.status_code == 404


def test_search_snippets_by_title():
    cat_id = _create_category()
    client.post("/snippets", json={
        "category_id": cat_id, "title": "Unique Search Target", "command": "echo test"
    })
    res = client.get("/snippets/search?q=Unique")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_filter_snippets_by_category():
    cat_id = _create_category()
    client.post("/snippets", json={
        "category_id": cat_id, "title": "Filtered", "command": "echo filtered"
    })
    res = client.get("/snippets?category=Linux")
    assert res.status_code == 200
    assert all(s["category_name"] == "Linux" for s in res.json())
