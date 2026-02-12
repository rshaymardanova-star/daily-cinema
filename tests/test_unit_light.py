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


class TestFallbackMissingStyle:
    """Tests for missing visual_style (field omitted — Pydantic defaults apply)."""

    def test_ml_generate_missing_style_uses_default(self, client):
        job_id = f"ml-missing-style-{int(time.time())}"
        r = client.post(
            f"{ML_URL}/generate",
            json={
                "job_id": job_id,
                "shot_id": "00000000-0000-0000-0000-000000000001",
                "project_id": "00000000-0000-0000-0000-000000000002",
                "prompt": "missing style test",
            },
        )
        assert r.status_code == 200
        assert r.json()["model"] == "ethereal_default"

    def test_unity_render_missing_style_uses_default(self, client):
        job_id = f"unity-missing-style-{int(time.time())}"
        r = client.post(
            f"{UNITY_URL}/render",
            json={
                "job_id": job_id,
                "project_id": "00000000-0000-0000-0000-000000000003",
                "scene": {"project_id": "test", "shots": []},
            },
        )
        assert r.status_code == 200
        assert r.json()["template"] == "ethereal_default"

    def test_backend_project_missing_style_defaults(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={"name": "No Style Field", "shots": [{"prompt": "test", "order": 1}]},
            headers=HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["visual_style"] == "ethereal_default"


class TestFallbackEmptyStyle:
    """Tests for empty-string visual_style."""

    def test_ml_generate_empty_style_uses_default(self, client):
        job_id = f"ml-empty-style-{int(time.time())}"
        r = client.post(
            f"{ML_URL}/generate",
            json={
                "job_id": job_id,
                "shot_id": "00000000-0000-0000-0000-000000000001",
                "project_id": "00000000-0000-0000-0000-000000000002",
                "prompt": "empty style test",
                "visual_style": "",
                "model": "",
            },
        )
        assert r.status_code == 200
        assert r.json()["model"] == "ethereal_default"

    def test_unity_render_empty_style_uses_default(self, client):
        job_id = f"unity-empty-style-{int(time.time())}"
        r = client.post(
            f"{UNITY_URL}/render",
            json={
                "job_id": job_id,
                "project_id": "00000000-0000-0000-0000-000000000003",
                "scene": {"project_id": "test", "shots": []},
                "visual_style": "",
                "template": "",
            },
        )
        assert r.status_code == 200
        assert r.json()["template"] == "ethereal_default"

    def test_backend_project_empty_style_coerced(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={"name": "Empty Style", "visual_style": "", "shots": [{"prompt": "test", "order": 1}]},
            headers=HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["visual_style"] == "ethereal_default"


class TestFallbackInvalidStyle:
    """Tests for various invalid visual_style values."""

    @pytest.mark.parametrize("bad_style", ["nonexistent", "UPPERCASE", "123", "null", " ", "ethereal_defaul"])
    def test_ml_invalid_styles_fall_back(self, client, bad_style):
        job_id = f"ml-bad-{bad_style[:8]}-{int(time.time())}"
        r = client.post(
            f"{ML_URL}/generate",
            json={
                "job_id": job_id,
                "shot_id": "00000000-0000-0000-0000-000000000001",
                "project_id": "00000000-0000-0000-0000-000000000002",
                "prompt": "invalid style test",
                "visual_style": bad_style,
                "model": bad_style,
            },
        )
        assert r.status_code == 200
        assert r.json()["model"] == "ethereal_default"

    @pytest.mark.parametrize("bad_style", ["nonexistent", "UPPERCASE", "123", "null", " ", "ethereal_defaul"])
    def test_unity_invalid_styles_fall_back(self, client, bad_style):
        job_id = f"unity-bad-{bad_style[:8]}-{int(time.time())}"
        r = client.post(
            f"{UNITY_URL}/render",
            json={
                "job_id": job_id,
                "project_id": "00000000-0000-0000-0000-000000000003",
                "scene": {"project_id": "test", "shots": []},
                "visual_style": bad_style,
                "template": bad_style,
            },
        )
        assert r.status_code == 200
        assert r.json()["template"] == "ethereal_default"

    @pytest.mark.parametrize("bad_style", ["nonexistent", "UPPERCASE", "123", " "])
    def test_backend_invalid_styles_coerced(self, client, bad_style):
        r = client.post(
            f"{BASE_URL}/projects",
            json={"name": f"Bad {bad_style}", "visual_style": bad_style, "shots": [{"prompt": "test", "order": 1}]},
            headers=HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["visual_style"] == "ethereal_default"


class TestStylesValidateEndpoint:
    """Tests for POST /styles/validate fallback behavior."""

    def test_validate_valid_style(self, client):
        r = client.post(
            f"{BASE_URL}/styles/validate",
            json={"visual_style": "cosmic_cinematic"},
            headers=HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["valid"] is True
        assert data["resolved_style"] == "cosmic_cinematic"
        assert len(data["ml_keywords"]) > 0
        assert "bloom_intensity" in data["hdrp_preset"]
        assert "fps" in data["ffmpeg_preset"]

    def test_validate_invalid_style_returns_fallback(self, client):
        r = client.post(
            f"{BASE_URL}/styles/validate",
            json={"visual_style": "totally_wrong"},
            headers=HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["valid"] is False
        assert data["visual_style"] == "totally_wrong"
        assert data["resolved_style"] == "ethereal_default"
        assert len(data["ml_keywords"]) > 0

    def test_validate_empty_style_returns_fallback(self, client):
        r = client.post(
            f"{BASE_URL}/styles/validate",
            json={"visual_style": ""},
            headers=HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["valid"] is False
        assert data["resolved_style"] == "ethereal_default"


class TestFallbackPipelinePropagation:
    """Tests that invalid/missing styles propagate correctly through the full pipeline."""

    def test_pipeline_with_invalid_style_completes(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Invalid Style Pipeline",
                "visual_style": "INVALID_XYZ",
                "shots": [{"prompt": "fallback pipeline test", "order": 1}],
            },
            headers=HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["visual_style"] == "ethereal_default"
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
        pytest.fail("Pipeline with invalid style timed out")

    def test_pipeline_with_missing_style_completes(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Missing Style Pipeline",
                "shots": [{"prompt": "no style field test", "order": 1}],
            },
            headers=HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["visual_style"] == "ethereal_default"
        project_id = r.json()["id"]

        r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
        assert r.status_code == 200

        for _ in range(60):
            r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
            data = r.json()
            if data["project_status"] in ("completed", "failed"):
                assert data["project_status"] == "completed"
                return
            time.sleep(1)
        pytest.fail("Pipeline with missing style timed out")

    def test_pipeline_with_empty_style_completes(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Empty Style Pipeline",
                "visual_style": "",
                "shots": [{"prompt": "empty style field test", "order": 1}],
            },
            headers=HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["visual_style"] == "ethereal_default"
        project_id = r.json()["id"]

        r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
        assert r.status_code == 200

        for _ in range(60):
            r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
            data = r.json()
            if data["project_status"] in ("completed", "failed"):
                assert data["project_status"] == "completed"
                return
            time.sleep(1)
        pytest.fail("Pipeline with empty style timed out")


class TestFFmpegFilterDeduplication:
    """Tests for FFmpeg filter deduplication in the Unity render pipeline."""

    def test_no_duplicate_filters_in_default_style(self, client):
        job_id = f"dedup-default-{int(time.time())}"
        r = client.post(
            f"{UNITY_URL}/render",
            json={
                "job_id": job_id,
                "project_id": "00000000-0000-0000-0000-000000000010",
                "scene": {"project_id": "test", "shots": []},
                "visual_style": "ethereal_default",
                "template": "ethereal_default",
            },
        )
        assert r.status_code == 200

    @pytest.mark.parametrize("style", ALL_STYLES)
    def test_no_duplicate_filters_per_style(self, client, style):
        job_id = f"dedup-{style}-{int(time.time())}"
        r = client.post(
            f"{UNITY_URL}/render",
            json={
                "job_id": job_id,
                "project_id": "00000000-0000-0000-0000-000000000010",
                "scene": {"project_id": "test", "shots": []},
                "visual_style": style,
                "template": style,
            },
        )
        assert r.status_code == 200
        for _ in range(15):
            sr = client.get(f"{UNITY_URL}/status/{job_id}")
            if sr.json()["status"] == "completed":
                return
            time.sleep(0.5)
        pytest.fail(f"Render for {style} did not complete")

    def test_dedup_endpoint_returns_200_with_invalid_style(self, client):
        job_id = f"dedup-invalid-{int(time.time())}"
        r = client.post(
            f"{UNITY_URL}/render",
            json={
                "job_id": job_id,
                "project_id": "00000000-0000-0000-0000-000000000010",
                "scene": {"project_id": "test", "shots": []},
                "visual_style": "bogus",
                "template": "bogus",
            },
        )
        assert r.status_code == 200
        assert r.json()["template"] == "ethereal_default"

    def test_dedup_endpoint_returns_200_with_empty_style(self, client):
        job_id = f"dedup-empty-{int(time.time())}"
        r = client.post(
            f"{UNITY_URL}/render",
            json={
                "job_id": job_id,
                "project_id": "00000000-0000-0000-0000-000000000010",
                "scene": {"project_id": "test", "shots": []},
                "visual_style": "",
                "template": "",
            },
        )
        assert r.status_code == 200
        assert r.json()["template"] == "ethereal_default"

    def test_pipeline_with_dedup_completes(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Dedup Pipeline Test",
                "visual_style": "cosmic_cinematic",
                "shots": [{"prompt": "dedup test", "order": 1}],
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
                return
            time.sleep(1)
        pytest.fail("Dedup pipeline timed out")


class TestFFmpegDeduplicateFilterUnit:
    """Direct unit tests for _deduplicate_filters logic via the /dedup-check endpoint."""

    def test_duplicate_eq_filters(self, client):
        r = client.post(
            f"{UNITY_URL}/filters/check",
            json={"filters": [
                "eq=saturation=1.2:contrast=1.1",
                "vignette=angle=0.40",
                "eq=saturation=1.0:contrast=1.0",
            ]},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["duplicates_found"] is True
        assert len(data["deduplicated"]) == 2
        assert data["deduplicated"][-1] == "eq=saturation=1.0:contrast=1.0"

    def test_duplicate_noise_filters(self, client):
        r = client.post(
            f"{UNITY_URL}/filters/check",
            json={"filters": [
                "noise=alls=3:allf=t",
                "gblur=sigma=0.5",
                "noise=alls=5:allf=t",
            ]},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["duplicates_found"] is True
        assert len(data["deduplicated"]) == 2
        eq_keys = [f.split("=", 1)[0] for f in data["deduplicated"]]
        assert eq_keys.count("noise") == 1

    def test_no_duplicates(self, client):
        r = client.post(
            f"{UNITY_URL}/filters/check",
            json={"filters": [
                "scale=1920:1080",
                "eq=saturation=1.1:contrast=0.9",
                "vignette=angle=0.43",
            ]},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["duplicates_found"] is False
        assert len(data["deduplicated"]) == 3

    def test_empty_filter_list(self, client):
        r = client.post(
            f"{UNITY_URL}/filters/check",
            json={"filters": []},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["duplicates_found"] is False
        assert data["deduplicated"] == []

    def test_mixed_valid_and_duplicate_filters(self, client):
        r = client.post(
            f"{UNITY_URL}/filters/check",
            json={"filters": [
                "scale=1920:1080",
                "eq=saturation=1.2:contrast=1.1",
                "vignette=angle=0.40",
                "gblur=sigma=0.5",
                "eq=saturation=0.95:contrast=0.85",
                "noise=alls=3:allf=t",
                "vignette=angle=0.44",
            ]},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["duplicates_found"] is True
        assert len(data["deduplicated"]) == 5
        eq_keys = [f.split("=", 1)[0] for f in data["deduplicated"]]
        assert eq_keys.count("eq") == 1
        assert eq_keys.count("vignette") == 1

    def test_single_filter(self, client):
        r = client.post(
            f"{UNITY_URL}/filters/check",
            json={"filters": ["eq=saturation=1.0:contrast=1.0"]},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["duplicates_found"] is False
        assert len(data["deduplicated"]) == 1

    def test_all_duplicates(self, client):
        r = client.post(
            f"{UNITY_URL}/filters/check",
            json={"filters": [
                "eq=saturation=1.0",
                "eq=saturation=1.1",
                "eq=saturation=1.2",
            ]},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["duplicates_found"] is True
        assert len(data["deduplicated"]) == 1
        assert data["deduplicated"][0] == "eq=saturation=1.2"


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
