"""Tests for the FastAPI activity management application"""

import pytest


def test_get_activities(client):
    """Test fetching all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Check that activities are returned
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Basketball" in data
    assert "Tennis Club" in data
    
    # Check activity structure
    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess
    assert isinstance(chess["participants"], list)


def test_signup_for_activity(client):
    """Test signing up for an activity"""
    response = client.post(
        "/activities/Chess Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]


def test_duplicate_signup_prevention(client):
    """Test that duplicate signups are prevented"""
    email = "test@mergington.edu"
    
    # First signup should succeed
    response1 = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response2.status_code == 400
    data = response2.json()
    assert "already signed up" in data.get("detail", "").lower()


def test_signup_nonexistent_activity(client):
    """Test signing up for a non-existent activity"""
    response = client.post(
        "/activities/Non-existent Club/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data.get("detail", "")


def test_remove_participant(client):
    """Test removing a participant from an activity"""
    email = "participant@mergington.edu"
    
    # First sign up
    signup_response = client.post(f"/activities/Art Studio/signup?email={email}")
    assert signup_response.status_code == 200
    
    # Then remove the participant
    delete_response = client.delete(
        f"/activities/Art Studio/signup/{email}"
    )
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert "Removed" in data.get("message", "")
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities["Art Studio"]["participants"]


def test_remove_nonexistent_participant(client):
    """Test removing a non-existent participant"""
    response = client.delete(
        "/activities/Drama Club/signup/nonexistent@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data.get("detail", "").lower()


def test_remove_from_nonexistent_activity(client):
    """Test removing from a non-existent activity"""
    response = client.delete(
        "/activities/Fake Activity/signup/test@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data.get("detail", "")


def test_activities_have_initial_participants(client):
    """Test that activities have initial participants loaded"""
    response = client.get("/activities")
    data = response.json()
    
    # Check a few activities have participants
    assert len(data["Chess Club"]["participants"]) > 0
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]
    
    assert len(data["Basketball"]["participants"]) > 0
    assert "alex@mergington.edu" in data["Basketball"]["participants"]
