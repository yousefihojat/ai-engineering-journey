"""pytest ~ xUnit. Fixtures ~ constructor setup / IClassFixture. TestClient ~ WebApplicationFactory."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_store
from app.store import InMemoryPromptStore


@pytest.fixture
def client() -> Iterator[TestClient]:
    # Fresh store per test, like overriding a service in WebApplicationFactory
    store = InMemoryPromptStore()
    app.dependency_overrides[get_store] = lambda: store
    yield TestClient(app)
    app.dependency_overrides.clear()


def create(client: TestClient, **overrides: object) -> dict[str, object]:
    body = {"name": "greet", "template": "Hello {name}, welcome to {city}!", "tags": ["demo"]}
    body.update(overrides)
    res = client.post("/prompts", json=body)
    assert res.status_code == 201
    data: dict[str, object] = res.json()
    return data


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_create_extracts_variables(client: TestClient) -> None:
    assert create(client)["variables"] == ["city", "name"]


def test_validation_rejects_empty_name(client: TestClient) -> None:
    assert client.post("/prompts", json={"name": "", "template": "x"}).status_code == 422


def test_get_and_404(client: TestClient) -> None:
    p = create(client)
    assert client.get(f"/prompts/{p['id']}").status_code == 200
    assert client.get("/prompts/00000000-0000-0000-0000-000000000000").status_code == 404


def test_list_filters_by_tag(client: TestClient) -> None:
    create(client, name="a", tags=["x"])
    create(client, name="b", tags=["y"])
    names = [p["name"] for p in client.get("/prompts", params={"tag": "x"}).json()]
    assert names == ["a"]


def test_render(client: TestClient) -> None:
    p = create(client)
    res = client.post(f"/prompts/{p['id']}/render", json={"values": {"name": "Ryan", "city": "Frankfurt"}})
    assert res.json()["text"] == "Hello Ryan, welcome to Frankfurt!"


def test_render_missing_value(client: TestClient) -> None:
    p = create(client)
    res = client.post(f"/prompts/{p['id']}/render", json={"values": {"name": "Ryan"}})
    assert res.status_code == 422
    assert "city" in res.json()["detail"]


def test_delete(client: TestClient) -> None:
    p = create(client)
    assert client.delete(f"/prompts/{p['id']}").status_code == 204
    assert client.delete(f"/prompts/{p['id']}").status_code == 404
