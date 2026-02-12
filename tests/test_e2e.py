"""End-to-end tests for the Daily Cinema pipeline."""
import time
import httpx
import pytest

pytestmark = [pytest.mark.full, pytest.mark.e2e]

BASE_URL = "http://localhost:8000"
ML_URL = "http://localhost:8001"
UNITY_URL = "http://localhost:8002"
API_KEY = "dc-prod-api-key-change-me"
HEADERS = {"X-API-Key": API_KEY}


@pytest.fixture
def client():
    return httpx.Client(timeout=30.0)


class TestHealthEndpoints:
    def test_backend_liveness(self, client):
        r = client.get(f"{BASE_URL}/health/live")
        assert r.status_code == 200
        assert r.json()["status"] == "alive"

    def test_backend_readiness(self, client):
        r = client.get(f"{BASE_URL}/health/ready")
        assert r.status_code == 200
        assert r.json()["status"] in ("ready", "degraded")

    def test_ml_liveness(self, client):
        r = client.get(f"{ML_URL}/health/live")
        assert r.status_code == 200

    def test_unity_liveness(self, client):
        r = client.get(f"{UNITY_URL}/health/live")
        assert r.status_code == 200


class TestAuthentication:
    def test_reject_no_api_key(self, client):
        r = client.get(f"{BASE_URL}/projects")
        assert r.status_code == 401

    def test_reject_bad_api_key(self, client):
        r = client.get(f"{BASE_URL}/projects", headers={"X-API-Key": "wrong"})
        assert r.status_code == 401

    def test_accept_valid_api_key(self, client):
        r = client.get(f"{BASE_URL}/projects", headers=HEADERS)
        assert r.status_code != 401


class TestMetrics:
    def test_backend_metrics(self, client):
        r = client.get(f"{BASE_URL}/metrics")
        assert r.status_code == 200
        assert "http_requests_total" in r.text or "http_request" in r.text

    def test_ml_metrics(self, client):
        r = client.get(f"{ML_URL}/metrics")
        assert r.status_code == 200

    def test_unity_metrics(self, client):
        r = client.get(f"{UNITY_URL}/metrics")
        assert r.status_code == 200


class TestMLModels:
    def test_list_models(self, client):
        r = client.get(f"{ML_URL}/models")
        assert r.status_code == 200
        data = r.json()
        assert "placeholder_v1" in data["models"]
        assert "placeholder_v2" in data["models"]
        assert "placeholder_artistic" in data["models"]


class TestUnityTemplates:
    def test_list_templates(self, client):
        r = client.get(f"{UNITY_URL}/templates")
        assert r.status_code == 200
        data = r.json()
        assert "default" in data["templates"]
        assert "cinematic" in data["templates"]
        assert "fast_preview" in data["templates"]


class TestFullPipeline:
    def test_create_and_render_project(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={"name": "E2E Test", "shots": [{"prompt": "sunset over ocean", "order": 1}]},
            headers=HEADERS,
        )
        assert r.status_code == 200
        project = r.json()
        project_id = project["id"]

        r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
        assert r.status_code == 200

        for _ in range(90):
            r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
            assert r.status_code == 200
            status = r.json()["project_status"]
            if status in ("completed", "failed"):
                break
            time.sleep(2)

        assert status == "completed", f"Pipeline ended with status: {status}"

    def test_multi_shot_project(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Multi Shot E2E",
                "shots": [
                    {"prompt": "sunrise in mountains", "order": 1},
                    {"prompt": "city at night", "order": 2},
                    {"prompt": "ocean waves", "order": 3},
                ],
            },
            headers=HEADERS,
        )
        assert r.status_code == 200
        project_id = r.json()["id"]

        r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
        assert r.status_code == 200

        for _ in range(120):
            r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
            status = r.json()["project_status"]
            if status in ("completed", "failed"):
                break
            time.sleep(2)

        assert status == "completed"
