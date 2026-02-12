"""Integration tests for Daily Cinema components."""
import time
import httpx
import pytest

BASE_URL = "http://localhost:8000"
ML_URL = "http://localhost:8001"
UNITY_URL = "http://localhost:8002"
API_KEY = "dc-prod-api-key-change-me"
HEADERS = {"X-API-Key": API_KEY}


@pytest.fixture
def client():
    return httpx.Client(timeout=30.0)


class TestMLIntegration:
    def test_direct_ml_generation(self, client):
        r = client.post(
            f"{ML_URL}/generate",
            json={
                "job_id": "test-ml-001",
                "shot_id": "shot-001",
                "project_id": "proj-001",
                "prompt": "test scene",
                "model": "placeholder_v1",
            },
        )
        assert r.status_code == 200
        assert r.json()["status"] == "processing"

        for _ in range(30):
            r = client.get(f"{ML_URL}/status/test-ml-001")
            if r.json()["status"] == "completed":
                break
            time.sleep(1)

        data = r.json()
        assert data["status"] == "completed"
        assert len(data["frame_urls"]) > 0

    def test_ml_multiple_models(self, client):
        for model in ["placeholder_v1", "placeholder_v2", "placeholder_artistic"]:
            r = client.post(
                f"{ML_URL}/generate",
                json={
                    "job_id": f"test-model-{model}",
                    "shot_id": "shot-model",
                    "project_id": "proj-model",
                    "prompt": "model test",
                    "model": model,
                },
            )
            assert r.status_code == 200

        for model in ["placeholder_v1", "placeholder_v2", "placeholder_artistic"]:
            for _ in range(30):
                r = client.get(f"{ML_URL}/status/test-model-{model}")
                if r.json()["status"] == "completed":
                    break
                time.sleep(1)
            assert r.json()["status"] == "completed"


class TestUnityIntegration:
    def test_direct_unity_render(self, client):
        ml_r = client.post(
            f"{ML_URL}/generate",
            json={
                "job_id": "unity-test-ml",
                "shot_id": "shot-unity",
                "project_id": "proj-unity",
                "prompt": "render test",
            },
        )
        assert ml_r.status_code == 200

        for _ in range(30):
            r = client.get(f"{ML_URL}/status/unity-test-ml")
            if r.json()["status"] == "completed":
                break
            time.sleep(1)

        frame_urls = r.json()["frame_urls"]

        r = client.post(
            f"{UNITY_URL}/render",
            json={
                "job_id": "test-render-001",
                "project_id": "proj-unity",
                "scene": {"shots": [{"shot_id": "shot-unity", "frame_urls": frame_urls}]},
                "template": "fast_preview",
            },
        )
        assert r.status_code == 200

        for _ in range(60):
            r = client.get(f"{UNITY_URL}/status/test-render-001")
            if r.json()["status"] == "completed":
                break
            time.sleep(2)

        assert r.json()["status"] == "completed"
        assert r.json()["video_url"] != ""


class TestOrchestratorIntegration:
    def test_multi_shot_orchestration(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Integration Multi-Shot",
                "shots": [
                    {"prompt": "scene one", "order": 1},
                    {"prompt": "scene two", "order": 2},
                ],
            },
            headers=HEADERS,
        )
        assert r.status_code == 200
        project_id = r.json()["id"]

        r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
        assert r.status_code == 200

        for _ in range(90):
            r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
            status = r.json()
            if status["project_status"] in ("completed", "failed"):
                break
            time.sleep(2)

        assert status["project_status"] == "completed"
        assert len(status["ml_jobs"]) == 2
        assert len(status["render_jobs"]) >= 1

    def test_orchestrator_recovery_on_retry(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={"name": "Retry Test", "shots": [{"prompt": "retry test", "order": 1}]},
            headers=HEADERS,
        )
        assert r.status_code == 200
        project_id = r.json()["id"]

        r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
        assert r.status_code == 200

        for _ in range(90):
            r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
            status = r.json()["project_status"]
            if status in ("completed", "failed"):
                break
            time.sleep(2)

        assert status == "completed"
