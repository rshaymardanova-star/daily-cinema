"""Unit tests running with ACU_MODE=light — mocked ML and Unity clients.
These tests validate schema correctness, validation logic, and mock outputs
without running real inference, FFmpeg, or GCS uploads.
"""
import time
import httpx
import pytest

pytestmark = [pytest.mark.fast, pytest.mark.unit]

ML_URL = "http://localhost:8001"
UNITY_URL = "http://localhost:8002"
BASE_URL = "http://localhost:8000"
API_KEY = "dc-prod-api-key-change-me"
HEADERS = {"X-API-Key": API_KEY}

ALL_STYLES = [
    "ethereal_default",
    "cosmic_cinematic",
    "luminous_dreamscape",
    "spectral_mythology",
    "neon_ritual",
]


@pytest.fixture
def client():
    return httpx.Client(timeout=30.0)


class TestACUModeFlag:
    def test_ml_reports_acu_mode(self, client):
        r = client.get(f"{ML_URL}/acu_mode")
        assert r.status_code == 200
        assert r.json()["acu_mode"] in ("light", "full")

    def test_unity_reports_acu_mode(self, client):
        r = client.get(f"{UNITY_URL}/acu_mode")
        assert r.status_code == 200
        assert r.json()["acu_mode"] in ("light", "full")


class TestMLMockSchema:
    def test_mock_generate_returns_valid_schema(self, client):
        job_id = f"mock-ml-schema-{int(time.time())}"
        r = client.post(
            f"{ML_URL}/generate",
            json={
                "job_id": job_id,
                "shot_id": "00000000-0000-0000-0000-000000000001",
                "project_id": "00000000-0000-0000-0000-000000000002",
                "prompt": "schema test",
                "visual_style": "ethereal_default",
                "model": "ethereal_default",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "job_id" in data
        assert "status" in data
        assert "frame_urls" in data
        assert "model" in data
        assert "duration_ms" in data
        assert "mock" in data
        assert data["status"] in ("processing", "completed")
        assert data["model"] == "ethereal_default"

    def test_mock_generate_completes_with_mock_flag(self, client):
        job_id = f"mock-ml-flag-{int(time.time())}"
        client.post(
            f"{ML_URL}/generate",
            json={
                "job_id": job_id,
                "shot_id": "00000000-0000-0000-0000-000000000001",
                "project_id": "00000000-0000-0000-0000-000000000002",
                "prompt": "mock flag test",
                "visual_style": "cosmic_cinematic",
                "model": "cosmic_cinematic",
            },
        )
        for _ in range(15):
            sr = client.get(f"{ML_URL}/status/{job_id}")
            data = sr.json()
            if data["status"] == "completed":
                assert isinstance(data["frame_urls"], list)
                assert len(data["frame_urls"]) >= 1
                assert data["model"] == "cosmic_cinematic"
                assert isinstance(data["mock"], bool)
                return
            time.sleep(0.5)
        pytest.fail("ML mock job did not complete")

    @pytest.mark.parametrize("style", ALL_STYLES)
    def test_mock_generate_per_style(self, client, style):
        job_id = f"mock-ml-{style}-{int(time.time())}"
        r = client.post(
            f"{ML_URL}/generate",
            json={
                "job_id": job_id,
                "shot_id": "00000000-0000-0000-0000-000000000001",
                "project_id": "00000000-0000-0000-0000-000000000002",
                "prompt": f"test {style}",
                "visual_style": style,
                "model": style,
            },
        )
        assert r.status_code == 200
        for _ in range(15):
            sr = client.get(f"{ML_URL}/status/{job_id}")
            if sr.json()["status"] == "completed":
                assert sr.json()["model"] == style
                return
            time.sleep(0.5)
        pytest.fail(f"ML mock job for {style} did not complete")

    def test_mock_status_not_found(self, client):
        r = client.get(f"{ML_URL}/status/nonexistent-job-xyz")
        assert r.status_code == 200
        assert r.json()["status"] == "not_found"


class TestUnityMockSchema:
    def test_mock_render_returns_valid_schema(self, client):
        job_id = f"mock-unity-schema-{int(time.time())}"
        r = client.post(
            f"{UNITY_URL}/render",
            json={
                "job_id": job_id,
                "project_id": "00000000-0000-0000-0000-000000000003",
                "scene": {"project_id": "test", "shots": []},
                "visual_style": "ethereal_default",
                "template": "ethereal_default",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "job_id" in data
        assert "status" in data
        assert "video_url" in data
        assert "template" in data
        assert "duration_ms" in data
        assert "mock" in data
        assert data["status"] in ("processing", "completed")
        assert data["template"] == "ethereal_default"

    def test_mock_render_completes_with_mock_flag(self, client):
        job_id = f"mock-unity-flag-{int(time.time())}"
        client.post(
            f"{UNITY_URL}/render",
            json={
                "job_id": job_id,
                "project_id": "00000000-0000-0000-0000-000000000003",
                "scene": {"project_id": "test", "shots": []},
                "visual_style": "neon_ritual",
                "template": "neon_ritual",
            },
        )
        for _ in range(15):
            sr = client.get(f"{UNITY_URL}/status/{job_id}")
            data = sr.json()
            if data["status"] == "completed":
                assert data["video_url"] != ""
                assert data["template"] == "neon_ritual"
                assert isinstance(data["mock"], bool)
                return
            time.sleep(0.5)
        pytest.fail("Unity mock job did not complete")

    @pytest.mark.parametrize("style", ALL_STYLES)
    def test_mock_render_per_style(self, client, style):
        job_id = f"mock-unity-{style}-{int(time.time())}"
        r = client.post(
            f"{UNITY_URL}/render",
            json={
                "job_id": job_id,
                "project_id": "00000000-0000-0000-0000-000000000003",
                "scene": {"project_id": "test", "shots": []},
                "visual_style": style,
                "template": style,
            },
        )
        assert r.status_code == 200
        for _ in range(15):
            sr = client.get(f"{UNITY_URL}/status/{job_id}")
            if sr.json()["status"] == "completed":
                assert sr.json()["video_url"] != ""
                return
            time.sleep(0.5)
        pytest.fail(f"Unity mock job for {style} did not complete")

    def test_mock_status_not_found(self, client):
        r = client.get(f"{UNITY_URL}/status/nonexistent-job-xyz")
        assert r.status_code == 200
        assert r.json()["status"] == "not_found"


class TestValidationInLightMode:
    def test_invalid_style_coerced_at_backend(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Light Mode Validation",
                "visual_style": "INVALID_STYLE",
                "shots": [{"prompt": "test", "order": 1}],
            },
            headers=HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["visual_style"] == "ethereal_default"

    def test_ml_fallback_in_light_mode(self, client):
        job_id = f"light-ml-fallback-{int(time.time())}"
        r = client.post(
            f"{ML_URL}/generate",
            json={
                "job_id": job_id,
                "shot_id": "00000000-0000-0000-0000-000000000001",
                "project_id": "00000000-0000-0000-0000-000000000002",
                "prompt": "fallback test",
                "visual_style": "bogus_style",
                "model": "bogus_model",
            },
        )
        assert r.status_code == 200
        assert r.json()["model"] == "ethereal_default"

    def test_unity_fallback_in_light_mode(self, client):
        job_id = f"light-unity-fallback-{int(time.time())}"
        r = client.post(
            f"{UNITY_URL}/render",
            json={
                "job_id": job_id,
                "project_id": "00000000-0000-0000-0000-000000000003",
                "scene": {"project_id": "test", "shots": []},
                "visual_style": "bogus_style",
                "template": "bogus_template",
            },
        )
        assert r.status_code == 200
        assert r.json()["template"] == "ethereal_default"


class TestLightModePipeline:
    def test_full_pipeline_in_light_mode(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Light Mode Pipeline",
                "visual_style": "ethereal_default",
                "shots": [{"prompt": "light mode test", "order": 1}],
            },
            headers=HEADERS,
        )
        assert r.status_code == 200
        project_id = r.json()["id"]

        r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
        assert r.status_code == 200

        for _ in range(60):
            r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
            data = r.json()
            if data["project_status"] in ("completed", "failed"):
                assert data["project_status"] == "completed"
                assert len(data["ml_jobs"]) >= 1
                assert data["ml_jobs"][0]["status"] == "completed"
                assert len(data["render_jobs"]) >= 1
                assert data["render_jobs"][0]["status"] == "completed"
                return
            time.sleep(1)
        pytest.fail("Light mode pipeline timed out")

    def test_multi_shot_pipeline_in_light_mode(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Light Multi Shot",
                "visual_style": "cosmic_cinematic",
                "shots": [
                    {"prompt": "shot one", "order": 1},
                    {"prompt": "shot two", "order": 2},
                ],
            },
            headers=HEADERS,
        )
        assert r.status_code == 200
        project_id = r.json()["id"]

        r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
        assert r.status_code == 200

        for _ in range(60):
            r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
            data = r.json()
            if data["project_status"] in ("completed", "failed"):
                assert data["project_status"] == "completed"
                assert len(data["ml_jobs"]) == 2
                return
            time.sleep(1)
        pytest.fail("Light mode multi-shot pipeline timed out")
