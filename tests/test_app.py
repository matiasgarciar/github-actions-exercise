"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    # Store original state
    original = {
        "Tennis Club": {
            "description": "Learn tennis techniques and participate in friendly matches",
            "schedule": "Wednesdays and Saturdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater productions, acting, and stage performance",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts exploration",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["grace@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking skills",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["aiden@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and STEM exploration",
            "schedule": "Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        },
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
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Tennis Club" in data
        assert "Basketball Team" in data
    
    def test_activity_structure(self, client, reset_activities):
        """Test that activity objects have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Tennis Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_participants_list(self, client, reset_activities):
        """Test that participants list is correct"""
        response = client.get("/activities")
        data = response.json()
        
        assert "alex@mergington.edu" in data["Tennis Club"]["participants"]
        assert "james@mergington.edu" in data["Basketball Team"]["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Tennis%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "newstudent@mergington.edu" in data["message"]
        assert "Tennis Club" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds participant to the list"""
        client.post("/activities/Tennis%20Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        participants = response.json()["Tennis Club"]["participants"]
        assert "newstudent@mergington.edu" in participants
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_duplicate_signup(self, client, reset_activities):
        """Test that duplicate signup is rejected"""
        # alex@mergington.edu is already in Tennis Club
        response = client.post(
            "/activities/Tennis%20Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities"""
        # Sign up for first activity
        response1 = client.post(
            "/activities/Tennis%20Club/signup?email=multisport@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Basketball%20Team/signup?email=multisport@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        assert "multisport@mergington.edu" in response.json()["Tennis Club"]["participants"]
        assert "multisport@mergington.edu" in response.json()["Basketball Team"]["participants"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_successful_unregister(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.post(
            "/activities/Tennis%20Club/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "alex@mergington.edu" in data["message"]
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes participant"""
        client.post("/activities/Tennis%20Club/unregister?email=alex@mergington.edu")
        
        response = client.get("/activities")
        participants = response.json()["Tennis Club"]["participants"]
        assert "alex@mergington.edu" not in participants
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregister of student not in the activity"""
        response = client.post(
            "/activities/Tennis%20Club/unregister?email=notstudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signup followed by unregister"""
        email = "testuser@mergington.edu"
        
        # Sign up
        response1 = client.post(
            "/activities/Tennis%20Club/signup?email=" + email
        )
        assert response1.status_code == 200
        
        # Verify signup
        response2 = client.get("/activities")
        assert email in response2.json()["Tennis Club"]["participants"]
        
        # Unregister
        response3 = client.post(
            "/activities/Tennis%20Club/unregister?email=" + email
        )
        assert response3.status_code == 200
        
        # Verify unregister
        response4 = client.get("/activities")
        assert email not in response4.json()["Tennis Club"]["participants"]


class TestIntegration:
    """Integration tests for complex scenarios"""
    
    def test_full_workflow(self, client, reset_activities):
        """Test complete workflow: get activities, signup, unregister"""
        # Get all activities
        response1 = client.get("/activities")
        assert response1.status_code == 200
        initial_tennis_count = len(response1.json()["Tennis Club"]["participants"])
        
        # Sign up for activity
        response2 = client.post(
            "/activities/Tennis%20Club/signup?email=workflow@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify signup
        response3 = client.get("/activities")
        assert len(response3.json()["Tennis Club"]["participants"]) == initial_tennis_count + 1
        
        # Unregister
        response4 = client.post(
            "/activities/Tennis%20Club/unregister?email=workflow@mergington.edu"
        )
        assert response4.status_code == 200
        
        # Verify unregister
        response5 = client.get("/activities")
        assert len(response5.json()["Tennis Club"]["participants"]) == initial_tennis_count
