"""REST schema and clinical endpoint regression checks."""
from fastapi.testclient import TestClient
from agents.api import app

client = TestClient(app)


def test_clinical_api():
    body = {
        "site": "ankle", "age": 42, "pain_present": True,
        "acute_blunt_trauma": True, "reliable_exam": True,
        "posterior_lateral_malleolus_tenderness": False,
        "posterior_medial_malleolus_tenderness": False,
        "unable_four_steps_immediately": False,
        "unable_four_steps_at_assessment": False,
    }
    response = client.post("/api/clinical", json=body)
    assert response.status_code == 200
    assert response.json()["outcome"] == "radiography_not_indicated"
    body["posterior_lateral_malleolus_tenderness"] = True
    assert client.post("/api/clinical", json=body).json()["radiography_indicated"] is True


def test_api_rejects_invalid_types_and_sites():
    payload = {
        "site": "ankle", "age": 29, "pain_present": True,
        "acute_blunt_trauma": True, "reliable_exam": True,
    }
    assert client.post("/api/clinical", json={**payload, "age": True}).status_code == 422
    assert client.post("/api/clinical", json={**payload, "site": "elbow"}).status_code == 422
    assert client.post("/api/clinical", json={**payload, "pain_present": "no"}).status_code == 422
    assert client.post("/api/clinical", json={**payload, "patient_name": "Example"}).status_code == 422


def test_openapi_exposes_clinical_endpoint():
    assert "/api/clinical" in client.get("/openapi.json").json()["paths"]


def test_api_serves_web_interface():
    assert client.get("/").status_code == 200
    assert "Ottawa Ankle" in client.get("/").text
    assert "function evaluate" in client.get("/app.js").text
