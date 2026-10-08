import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_input_validation_empty_recipients():
    response = client.post(
        "/api/certificates/generate",
        json={"event_name": "DevCon", "issue_date": "2026-10-10", "recipients": []},
    )
    assert response.status_code == 422


def test_input_validation_invalid_email():
    response = client.post(
        "/api/certificates/generate",
        json={
            "event_name": "DevCon",
            "issue_date": "2026-10-10",
            "recipients": [{"name": "Jane", "email": "not-valid"}],
        },
    )
    assert response.status_code == 422


def test_bulk_generation_and_individual_failure():
    payload = {
        "event_name": "Cloud Summit 2026",
        "issue_date": "2026-10-08",
        "recipients": [
            {"name": "Alice Cooper", "email": "alice@example.com"},
            {"name": "trigger-failure Bob", "email": "bob@example.com"},
        ],
    }

    # 1. Submit Generation Job (TestClient automatically finishes background task on return)
    post_res = client.post("/api/certificates/generate", json=payload)
    assert post_res.status_code == 202
    job_id = post_res.json()["job_id"]

    # 2. Check status & error isolation
    status_res = client.get(f"/api/certificates/jobs/{job_id}")
    assert status_res.status_code == 200
    data = status_res.json()

    assert data["status"] == "COMPLETED"
    assert data["total_count"] == 2
    assert data["success_count"] == 1
    assert data["failed_count"] == 1

    alice = next(i for i in data["items"] if i["recipient_name"] == "Alice Cooper")
    bob = next(i for i in data["items"] if "trigger-failure" in i["recipient_name"])

    assert alice["status"] == "SUCCESS"
    assert alice["certificate_url"] is not None

    assert bob["status"] == "FAILED"
    assert "Simulated failure" in bob["error_message"]

    # 3. Check retrieval
    download_res = client.get(alice["certificate_url"])
    assert download_res.status_code == 200
    assert download_res.headers["content-type"] == "image/png"
