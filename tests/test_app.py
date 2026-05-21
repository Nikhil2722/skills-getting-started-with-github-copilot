import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities_returns_activities():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "Chess Club" in body
    assert isinstance(body["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    email = "newstudent@mergington.edu"
    encoded_activity = quote("Chess Club")

    # Act
    response = client.post(f"/activities/{encoded_activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_signup_duplicate_email_returns_400():
    # Arrange
    email = "duplicate@mergington.edu"
    activities["Chess Club"]["participants"].append(email)
    encoded_activity = quote("Chess Club")

    # Act
    response = client.post(f"/activities/{encoded_activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_delete_participant_removes_participant():
    # Arrange
    email = "removeme@mergington.edu"
    activities["Programming Class"]["participants"].append(email)
    encoded_activity = quote("Programming Class")

    # Act
    response = client.delete(f"/activities/{encoded_activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities["Programming Class"]["participants"]
    assert response.json()["message"] == f"Removed {email} from Programming Class"
