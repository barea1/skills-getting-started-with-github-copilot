"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
    })


def test_root_redirect(client):
    """Test that root redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert len(data["Chess Club"]["participants"]) == 2


def test_signup_for_activity_success(client):
    """Test successfully signing up for an activity"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert "newstudent@mergington.edu" in data["message"]
    
    # Verify the student was added
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_nonexistent_activity(client):
    """Test signing up for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_signup_already_registered(client):
    """Test signing up when already registered"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_unregister_from_activity_success(client):
    """Test successfully unregistering from an activity"""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    assert "michael@mergington.edu" in data["message"]
    
    # Verify the student was removed
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_from_nonexistent_activity(client):
    """Test unregistering from an activity that doesn't exist"""
    response = client.delete(
        "/activities/Nonexistent%20Club/unregister?email=student@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_unregister_not_registered(client):
    """Test unregistering when not registered"""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=notstudent@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_signup_and_unregister_flow(client):
    """Test the complete flow of signing up and then unregistering"""
    email = "testflow@mergington.edu"
    activity = "Programming Class"
    
    # Sign up
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    
    # Unregister
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_multiple_signups_different_activities(client):
    """Test signing up for multiple different activities"""
    email = "multi@mergington.edu"
    
    # Sign up for Chess Club
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 200
    
    # Sign up for Programming Class
    response = client.post(f"/activities/Programming%20Class/signup?email={email}")
    assert response.status_code == 200
    
    # Verify both signups
    assert email in activities["Chess Club"]["participants"]
    assert email in activities["Programming Class"]["participants"]
