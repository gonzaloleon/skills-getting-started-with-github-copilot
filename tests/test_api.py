from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def reset_activities():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_all_activities(client, reset_activities):
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_for_activity_success(client, reset_activities):
    # Arrange
    activity = "Chess Club"
    email = "new_student@mergington.edu"
    assert email not in activities[activity]["participants"]
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    assert email in activities[activity]["participants"]


def test_signup_for_activity_already_signed(client, reset_activities):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # already in initial data
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 400


def test_signup_capacity(client, reset_activities):
    # Arrange
    activity = "Chess Club"
    max_p = activities[activity]["max_participants"]
    activities[activity]["participants"] = [f"user{i}@example.com" for i in range(max_p)]
    email = "overflow@student.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 400


def test_remove_participant_success(client, reset_activities):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    assert email in activities[activity]["participants"]
    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert f"Removed {email} from {activity}" in body["message"]
    assert email not in activities[activity]["participants"]
