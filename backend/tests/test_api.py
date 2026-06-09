from __future__ import annotations

import uuid

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


def test_register_requires_email_and_allows_email_login() -> None:
    missing_email = client.post(
        "/api/auth/register",
        json={"username": f"student_{uuid.uuid4().hex[:8]}", "password": "student123"},
    )
    assert missing_email.status_code == 422

    username = f"student_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    registered = client.post(
        "/api/auth/register",
        json={"username": username, "password": "student123", "email": email, "nickname": "邮箱注册学生"},
    )
    assert registered.status_code == 200, registered.text
    assert registered.json()["email"] == email

    login = client.post("/api/auth/login", json={"username": email, "password": "student123"})
    assert login.status_code == 200, login.text
    assert login.json()["access_token"]


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


def test_learning_interactions_flow() -> None:
    headers = auth_headers()
    start = client.post(
        "/api/practice/start",
        headers=headers,
        json={"mode": "sequential", "subject_id": 1, "question_count": 1},
    )
    assert start.status_code == 200, start.text
    question_id = start.json()["questions"][0]["id"]

    note = client.post(
        f"/api/questions/{question_id}/notes",
        headers=headers,
        json={"content": "这里记录一个复盘点"},
    )
    assert note.status_code == 200, note.text
    note_id = note.json()["id"]
    notes = client.get(f"/api/questions/{question_id}/notes", headers=headers)
    assert notes.status_code == 200
    assert notes.json()["total"] >= 1
    updated_note = client.put(f"/api/notes/{note_id}", headers=headers, json={"content": "更新后的笔记"})
    assert updated_note.status_code == 200
    assert updated_note.json()["content"] == "更新后的笔记"

    comment = client.post(
        f"/api/questions/{question_id}/comments",
        headers=headers,
        json={"content": "这道题可以这样记"},
    )
    assert comment.status_code == 200, comment.text
    comment_id = comment.json()["id"]
    comments = client.get(f"/api/questions/{question_id}/comments", headers=headers)
    assert comments.status_code == 200
    assert comments.json()["total"] >= 1
    updated_comment = client.put(f"/api/comments/{comment_id}", headers=headers, json={"content": "更新后的评论"})
    assert updated_comment.status_code == 200
    assert updated_comment.json()["content"] == "更新后的评论"

    liked = client.post(f"/api/questions/{question_id}/like", headers=headers)
    assert liked.status_code == 200, liked.text
    assert liked.json()["is_liked"] is True
    likes = client.get("/api/me/likes", headers=headers)
    assert likes.status_code == 200
    assert likes.json()["total"] >= 1
    unliked = client.delete(f"/api/questions/{question_id}/like", headers=headers)
    assert unliked.status_code == 200
    assert unliked.json()["is_liked"] is False

    deleted_comment = client.delete(f"/api/comments/{comment_id}", headers=headers)
    assert deleted_comment.status_code == 200
    deleted_note = client.delete(f"/api/notes/{note_id}", headers=headers)
    assert deleted_note.status_code == 200


def test_dashboard_requires_admin() -> None:
    headers = auth_headers()
    response = client.get("/api/admin/statistics/dashboard", headers=headers)
    assert response.status_code == 200
    assert "total_questions" in response.json()


def test_admin_users_are_json_serializable() -> None:
    headers = auth_headers()
    response = client.get("/api/admin/users", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["items"]
    assert isinstance(data["items"][0]["role"], dict)
    assert "name" in data["items"][0]["role"]


def test_admin_logs_are_json_serializable() -> None:
    headers = auth_headers()
    response = client.get("/api/admin/logs", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "items" in data