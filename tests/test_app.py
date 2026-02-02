import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Preserve and restore global in-memory activities around each test
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_show_in_list(client):
    email = "test_signup@example.com"
    r = client.post(f"/activities/Chess Club/signup?email={email}")
    assert r.status_code == 200
    assert "Signed up" in r.json()["message"]

    # Now check participant is visible
    r = client.get("/activities")
    assert r.status_code == 200
    assert email in r.json()["Chess Club"]["participants"]


def test_duplicate_signup_returns_400(client):
    email = "dup_test@example.com"
    r = client.post(f"/activities/Chess Club/signup?email={email}")
    assert r.status_code == 200

    r2 = client.post(f"/activities/Chess Club/signup?email={email}")
    assert r2.status_code == 400


def test_unregister_existing_and_not_found(client):
    email = "to_remove@example.com"
    # sign up first
    r = client.post(f"/activities/Chess Club/signup?email={email}")
    assert r.status_code == 200

    # unregister
    r2 = client.post(f"/activities/Chess Club/unregister?email={email}")
    assert r2.status_code == 200
    assert "Unregistered" in r2.json()["message"]

    # unregister again => not found
    r3 = client.post(f"/activities/Chess Club/unregister?email={email}")
    assert r3.status_code == 404
