from fastapi.testclient import TestClient
from src.app import app

# Create TestClient with follow_redirects=False to test redirects properly
client = TestClient(app, follow_redirects=False)


def test_root_redirect():
    """Test that GET / redirects to the static index page"""
    # Arrange - no setup needed
    
    # Act - make the request
    response = client.get("/")
    
    # Assert - check redirect status and location
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test that GET /activities returns all activities"""
    # Arrange - no setup needed (uses in-memory data)
    
    # Act - make the request
    response = client.get("/activities")
    
    # Assert - check response status and data structure
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0  # Should have activities
    
    # Check structure of first activity
    first_activity = next(iter(data.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)


def test_signup_success():
    """Test successful signup for an activity"""
    # Arrange - use an activity with available spots and a new email
    activity_name = "Basketball Team"  # Has no participants initially
    email = "newstudent@mergington.edu"
    
    # Act - make the signup request
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert - check success response
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert f"Signed up {email} for {activity_name}" == result["message"]
    
    # Verify the participant was added
    response2 = client.get("/activities")
    activities = response2.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate():
    """Test that signing up twice for the same activity fails"""
    # Arrange - use an existing participant
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up
    
    # Act - attempt to sign up again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert - check error response
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    assert "already signed up" in result["detail"]


def test_signup_invalid_activity():
    """Test signup for a non-existent activity"""
    # Arrange - use invalid activity name
    activity_name = "NonExistent Activity"
    email = "test@mergington.edu"
    
    # Act - attempt to sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert - check error response
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Activity not found" == result["detail"]