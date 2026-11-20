"""Tests run against SQLite in memory by default.

CI sets DATABASE_URL to a real PostgreSQL 17 service, so the same tests also
exercise the production database path.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client: TestClient):
    response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "1.0.0"


def test_seed_data(client: TestClient):
    response = client.get("/api/engines")
    assert response.status_code == 200
    engines = response.json()
    assert len(engines) >= 26
    names = {engine["name"] for engine in engines}
    assert {"Firebird", "Redis", "Neo4j"} <= names
    assert all(engine["runtime"] in {"docker", "cloud"} for engine in engines)


def test_stats(client: TestClient):
    response = client.get("/api/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total"] >= 26
    assert stats["docker"] + stats["cloud"] == stats["total"]
    assert stats["categories"] >= 10


def test_filters(client: TestClient):
    cloud = client.get("/api/engines", params={"runtime": "cloud"}).json()
    assert cloud
    assert all(engine["runtime"] == "cloud" for engine in cloud)

    search = client.get("/api/engines", params={"q": "redis"}).json()
    assert [engine["name"] for engine in search] == ["Redis"]


def test_categories(client: TestClient):
    response = client.get("/api/categories")
    assert response.status_code == 200
    assert "Relational" in response.json()


def test_create_duplicate_and_delete(client: TestClient):
    payload = {
        "name": "Test Engine",
        "category": "Testing",
        "runtime": "docker",
        "repo_url": "https://github.com/devarent/test-engine",
        "notes": "Created by the test suite.",
    }

    created = client.post("/api/engines", json=payload)
    assert created.status_code == 201, created.text
    row = created.json()
    assert row["name"] == "Test Engine"

    duplicate = client.post("/api/engines", json=payload)
    assert duplicate.status_code == 409

    deleted = client.delete(f"/api/engines/{row['id']}")
    assert deleted.status_code == 204

    remaining = client.get("/api/engines", params={"q": "Test Engine"}).json()
    assert remaining == []


def test_validation(client: TestClient):
    bad_url = client.post(
        "/api/engines",
        json={
            "name": "Bad URL",
            "category": "Testing",
            "runtime": "docker",
            "repo_url": "not-a-url",
        },
    )
    assert bad_url.status_code == 422

    short_name = client.post(
        "/api/engines",
        json={
            "name": "x",
            "category": "Testing",
            "runtime": "docker",
            "repo_url": "https://example.com",
        },
    )
    assert short_name.status_code == 422

    bad_runtime = client.post(
        "/api/engines",
        json={
            "name": "Bad Runtime",
            "category": "Testing",
            "runtime": "kubernetes",
            "repo_url": "https://example.com",
        },
    )
    assert bad_runtime.status_code == 422
