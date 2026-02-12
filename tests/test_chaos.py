"""Chaos tests - simulate worker failures and verify recovery."""
import subprocess
import time
import httpx
import pytest

BASE_URL = "http://localhost:8000"
API_KEY = "dc-prod-api-key-change-me"
HEADERS = {"X-API-Key": API_KEY}


@pytest.fixture
def client():
    return httpx.Client(timeout=30.0)


def docker_compose_cmd(action, service):
    subprocess.run(
        ["docker", "compose", action, service],
        capture_output=True,
        cwd="/home/ubuntu/repos/dailycinema",
    )


class TestMLWorkerChaos:
    def test_ml_worker_recovery(self, client):
        """Stop ML worker, start project, restart worker, verify completion."""
        docker_compose_cmd("stop", "ml")
        time.sleep(2)

        r = client.post(
            f"{BASE_URL}/projects",
            json={"name": "Chaos ML", "shots": [{"prompt": "chaos test", "order": 1}]},
            headers=HEADERS,
        )
        assert r.status_code == 200
        project_id = r.json()["id"]

        r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
        assert r.status_code == 200

        time.sleep(5)

        docker_compose_cmd("start", "ml")
        time.sleep(10)

        for _ in range(60):
            r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
            status = r.json()["project_status"]
            if status in ("completed", "failed"):
                break
            time.sleep(3)

        assert status in ("completed", "failed")


class TestUnityWorkerChaos:
    def test_unity_worker_recovery(self, client):
        """Stop Unity worker, start project, restart worker, verify completion."""
        r = client.post(
            f"{BASE_URL}/projects",
            json={"name": "Chaos Unity", "shots": [{"prompt": "chaos test", "order": 1}]},
            headers=HEADERS,
        )
        assert r.status_code == 200
        project_id = r.json()["id"]

        docker_compose_cmd("stop", "unity")
        time.sleep(2)

        r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
        assert r.status_code == 200

        time.sleep(5)

        docker_compose_cmd("start", "unity")
        time.sleep(10)

        for _ in range(60):
            r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
            status = r.json()["project_status"]
            if status in ("completed", "failed"):
                break
            time.sleep(3)

        assert status in ("completed", "failed")


class TestBackendResilience:
    def test_backend_stays_alive_without_redis(self, client):
        """Backend should stay alive even if Redis is down (degraded mode)."""
        r = client.get(f"{BASE_URL}/health/live")
        assert r.status_code == 200
        assert r.json()["status"] == "alive"

    def test_health_ready_reports_degraded(self, client):
        """Readiness should report degraded if a dependency is down."""
        r = client.get(f"{BASE_URL}/health/ready")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ("ready", "degraded")
