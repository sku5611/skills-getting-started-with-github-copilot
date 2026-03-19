from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activity state after each test."""
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_get_activities_returns_existing_activity():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert isinstance(data[expected_activity]["participants"], list)


def test_signup_adds_participant_and_returns_success_message():
    # Arrange
    activity = "Chess Club"
    email = "test@example.com"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    assert email in activities[activity]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity = "Chess Club"
    email = "duplicate@example.com"
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400


def test_unregister_removes_participant():
    # Arrange
    activity = "Chess Club"
    email = "remove@example.com"
    client.post(f"/activities/{activity}/signup?email={email}")
    assert email in activities[activity]["participants"]

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_returns_404():
    # Arrange
    activity = "Chess Club"
    email = "nosuch@example.com"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert response.status_code == 404
