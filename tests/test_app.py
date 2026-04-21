import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities before each test
    for activity in activities.values():
        if isinstance(activity["participants"], list):
            activity["participants"].clear()
    activities["Chess Club"]["participants"].extend(["michael@mergington.edu", "daniel@mergington.edu"])
    activities["Programming Class"]["participants"].extend(["emma@mergington.edu", "sophia@mergington.edu"])
    activities["Gym Class"]["participants"].extend(["john@mergington.edu", "olivia@mergington.edu"])


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_success():
    response = client.post("/activities/Art Workshop/signup?email=test1@example.com")
    assert response.status_code == 200
    assert "Signed up test1@example.com for Art Workshop" in response.json()["message"]
    assert "test1@example.com" in activities["Art Workshop"]["participants"]


def test_signup_duplicate():
    client.post("/activities/Art Workshop/signup?email=test2@example.com")
    response = client.post("/activities/Art Workshop/signup?email=test2@example.com")
    assert response.status_code == 400
    assert "Student already signed up" in response.json()["detail"]


def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=test3@example.com")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_success():
    client.post("/activities/Art Workshop/signup?email=test4@example.com")
    response = client.post("/activities/Art Workshop/unregister?email=test4@example.com")
    assert response.status_code == 200
    assert "Unregistered test4@example.com from Art Workshop" in response.json()["message"]
    assert "test4@example.com" not in activities["Art Workshop"]["participants"]


def test_unregister_not_registered():
    response = client.post("/activities/Art Workshop/unregister?email=notfound@example.com")
    assert response.status_code == 400
    assert "Student not registered" in response.json()["detail"]


def test_unregister_activity_not_found():
    response = client.post("/activities/Nonexistent/unregister?email=test5@example.com")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
