from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)
TEST_EMAIL = "test.student@mergington.edu"

def get_any_activity_name():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert activities, "Expected at least one activity"
    return next(iter(activities.keys()))

def test_get_activities():
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    for name, activity in activities.items():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

def test_signup_unregister_lifecycle():
    # Arrange
    activity = get_any_activity_name()
    client.post(f"/activities/{activity}/unregister?email={TEST_EMAIL}")

    # Act
    signup_response = client.post(f"/activities/{activity}/signup?email={TEST_EMAIL}")
    # Assert
    assert signup_response.status_code == 200
    assert "Signed up" in signup_response.json().get("message", "")

    # Act
    before = client.get("/activities").json()[activity]["participants"]
    assert TEST_EMAIL in before

    # Act
    unregister_response = client.post(f"/activities/{activity}/unregister?email={TEST_EMAIL}")
    # Assert
    assert unregister_response.status_code == 200
    assert "Unregistered" in unregister_response.json().get("message", "")

    # Act
    after = client.get("/activities").json()[activity]["participants"]
    assert TEST_EMAIL not in after

def test_repeated_signup_fails():
    # Arrange
    activity = get_any_activity_name()
    client.post(f"/activities/{activity}/unregister?email={TEST_EMAIL}")

    # Act
    first = client.post(f"/activities/{activity}/signup?email={TEST_EMAIL}")
    # Assert
    assert first.status_code == 200

    # Act
    second = client.post(f"/activities/{activity}/signup?email={TEST_EMAIL}")
    # Assert
    assert second.status_code == 400

    # Cleanup
    client.post(f"/activities/{activity}/unregister?email={TEST_EMAIL}")