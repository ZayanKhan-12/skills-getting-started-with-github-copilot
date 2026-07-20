"""Backend API tests for the Mergington High School activities app.

Tests follow the AAA (Arrange-Act-Assert) pattern.
"""

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange / Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    # Arrange
    expected_count = len(activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert len(body) == expected_count
    assert "Chess Club" in body


def test_signup_adds_participant():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]

    # Cleanup
    activities[activity]["participants"].remove(email)


def test_signup_duplicate_returns_400():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # already a participant

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_nonexistent_activity_returns_404():
    # Arrange
    activity = "Underwater Basket Weaving"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant():
    # Arrange
    activity = "Chess Club"
    email = "temp@mergington.edu"
    activities[activity]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{activity}/unregister", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_not_signed_up_returns_400():
    # Arrange
    activity = "Chess Club"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity}/unregister", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up"


def test_unregister_nonexistent_activity_returns_404():
    # Arrange
    activity = "Underwater Basket Weaving"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity}/unregister", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
