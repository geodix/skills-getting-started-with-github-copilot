from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)
TEST_EMAIL = "test.student@mergington.edu"

def get_any_activity_name():
    r = client.get("/activities")
    assert r.status_code == 200
    activities = r.json()
    assert isinstance(activities, dict)
    assert activities, "Expected at least one activity"
    return next(iter(activities.keys()))

def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    for name, activity in data.items():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

def test_signup_unregister_lifecycle():
    activity = get_any_activity_name()

    # ensure no preexisting test email
    client.post(f"/activities/{activity}/unregister?email={TEST_EMAIL}")

    r = client.post(f"/activities/{activity}/signup?email={TEST_EMAIL}")
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    r = client.get("/activities")
    participants = r.json()[activity]["participants"]
    assert TEST_EMAIL in participants

    r = client.post(f"/activities/{activity}/unregister?email={TEST_EMAIL}")
    assert r.status_code == 200
    assert "Unregistered" in r.json().get("message", "")

    r = client.get("/activities")
    participants = r.json()[activity]["participants"]
    assert TEST_EMAIL not in participants

def test_repeated_signup_fails():
    activity = get_any_activity_name()
    client.post(f"/activities/{activity}/unregister?email={TEST_EMAIL}")

    # first signup succeeds
    r1 = client.post(f"/activities/{activity}/signup?email={TEST_EMAIL}")
    assert r1.status_code == 200

    # duplicate signup returns 400
    r2 = client.post(f"/activities/{activity}/signup?email={TEST_EMAIL}")
    assert r2.status_code == 400

    client.post(f"/activities/{activity}/unregister?email={TEST_EMAIL}")