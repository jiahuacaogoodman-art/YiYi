from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers(username: str = "admin", password: str = "admin123456") -> dict[str, str]:
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_admin_login_and_subjects() -> None:
    headers = auth_headers()
    response = client.get("/api/subjects", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 5


def test_practice_answer_flow() -> None:
    headers = auth_headers()
    start = client.post(
        "/api/practice/start",
        headers=headers,
        json={"mode": "sequential", "subject_id": 1, "question_count": 1},
    )
    assert start.status_code == 200, start.text
    question = start.json()["questions"][0]
    answer = client.post(
        "/api/practice/answer",
        headers=headers,
        json={"question_id": question["id"], "answer": question["correct_answer"], "mode": "practice"},
    )
    assert answer.status_code == 200, answer.text
    assert answer.json()["is_correct"] is True


def test_dashboard_requires_admin() -> None:
    headers = auth_headers()
    response = client.get("/api/admin/statistics/dashboard", headers=headers)
    assert response.status_code == 200
    assert "total_questions" in response.json()

