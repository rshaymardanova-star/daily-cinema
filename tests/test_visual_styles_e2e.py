"""End-to-end tests for Visual Universe style integration."""
import time
import httpx
import pytest

BASE_URL = "http://localhost:8000"
ML_URL = "http://localhost:8001"
UNITY_URL = "http://localhost:8002"
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
    return httpx.Client(timeout=60.0)


def _create_and_render(client: httpx.Client, name: str, visual_style: str, prompt: str = "luminous temple with spectral energy") -> dict:
    r = client.post(
        f"{BASE_URL}/projects",
        json={
            "name": name,
            "visual_style": visual_style,
            "shots": [{"prompt": prompt, "order": 1}],
        },
        headers=HEADERS,
    )
    assert r.status_code == 200, f"Create failed: {r.status_code} {r.text}"
    project = r.json()
    assert project["visual_style"] == visual_style
    project_id = project["id"]

    r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
    assert r.status_code == 200, f"Render start failed: {r.status_code} {r.text}"

    status = "rendering"
    for _ in range(60):
        r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
        assert r.status_code == 200
        data = r.json()
        status = data["project_status"]
        if status in ("completed", "failed"):
            return data
        time.sleep(2)

    pytest.fail(f"Pipeline timed out for style {visual_style}, last status: {status}")


class TestVisualStyleEndpoints:
    def test_ml_styles_endpoint(self, client):
        r = client.get(f"{ML_URL}/styles")
        assert r.status_code == 200
        data = r.json()
        assert "styles" in data
        assert "default" in data
        for style in ALL_STYLES:
            assert style in data["styles"], f"ML missing style: {style}"
            assert "description" in data["styles"][style]
            assert "keywords" in data["styles"][style]

    def test_unity_styles_endpoint(self, client):
        r = client.get(f"{UNITY_URL}/styles")
        assert r.status_code == 200
        data = r.json()
        assert "styles" in data
        assert "default" in data
        for style in ALL_STYLES:
            assert style in data["styles"], f"Unity missing style: {style}"
            assert "description" in data["styles"][style]
            assert "bloom" in data["styles"][style]
            assert "fog" in data["styles"][style]

    def test_ml_models_include_styles(self, client):
        r = client.get(f"{ML_URL}/models")
        assert r.status_code == 200
        models = r.json()["models"]
        for style in ALL_STYLES:
            assert style in models, f"ML models missing style entry: {style}"

    def test_unity_templates_include_styles(self, client):
        r = client.get(f"{UNITY_URL}/templates")
        assert r.status_code == 200
        templates = r.json()["templates"]
        for style in ALL_STYLES:
            assert style in templates, f"Unity templates missing style entry: {style}"


class TestVisualStyleSuccessPaths:
    @pytest.mark.parametrize("style", ALL_STYLES)
    def test_full_pipeline_with_style(self, client, style):
        result = _create_and_render(client, f"E2E {style}", style, f"guardian in {style} realm")
        assert result["project_status"] == "completed", f"Style {style} failed: {result}"
        assert len(result["ml_jobs"]) >= 1
        assert result["ml_jobs"][0]["status"] == "completed"
        assert len(result["render_jobs"]) >= 1
        assert result["render_jobs"][0]["status"] == "completed"
        assert result["render_jobs"][0]["video_url"] != ""

    def test_ethereal_default_pipeline(self, client):
        result = _create_and_render(client, "Ethereal Test", "ethereal_default", "meditative cosmic scene")
        assert result["project_status"] == "completed"

    def test_cosmic_cinematic_pipeline(self, client):
        result = _create_and_render(client, "Cosmic Test", "cosmic_cinematic", "epic starfield with neon nebula")
        assert result["project_status"] == "completed"

    def test_luminous_dreamscape_pipeline(self, client):
        result = _create_and_render(client, "Dreamscape Test", "luminous_dreamscape", "pastel dreamworld with floating lights")
        assert result["project_status"] == "completed"

    def test_spectral_mythology_pipeline(self, client):
        result = _create_and_render(client, "Mythology Test", "spectral_mythology", "ancient dragon guardian in spectral mist")
        assert result["project_status"] == "completed"

    def test_neon_ritual_pipeline(self, client):
        result = _create_and_render(client, "Ritual Test", "neon_ritual", "energy ceremony with violet light")
        assert result["project_status"] == "completed"


class TestVisualStyleFallback:
    def test_invalid_style_falls_back_to_default(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Invalid Style Test",
                "visual_style": "nonexistent_style_xyz",
                "shots": [{"prompt": "test scene", "order": 1}],
            },
            headers=HEADERS,
        )
        assert r.status_code == 200
        project = r.json()
        project_id = project["id"]

        r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
        assert r.status_code == 200

        for _ in range(60):
            r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
            status = r.json()["project_status"]
            if status in ("completed", "failed"):
                break
            time.sleep(2)

        assert status == "completed", f"Fallback pipeline failed with status: {status}"

    def test_empty_style_uses_default(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Empty Style Test",
                "visual_style": "",
                "shots": [{"prompt": "test scene", "order": 1}],
            },
            headers=HEADERS,
        )
        assert r.status_code == 200
        project_id = r.json()["id"]

        r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
        assert r.status_code == 200

        for _ in range(60):
            r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
            status = r.json()["project_status"]
            if status in ("completed", "failed"):
                break
            time.sleep(2)

        assert status == "completed", f"Empty style pipeline failed with status: {status}"

    def test_no_style_field_uses_default(self, client):
        r = client.post(
            f"{BASE_URL}/projects",
            json={
                "name": "No Style Field Test",
                "shots": [{"prompt": "test scene", "order": 1}],
            },
            headers=HEADERS,
        )
        assert r.status_code == 200
        project = r.json()
        assert project["visual_style"] == "ethereal_default"
        project_id = project["id"]

        r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
        assert r.status_code == 200

        for _ in range(60):
            r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
            status = r.json()["project_status"]
            if status in ("completed", "failed"):
                break
            time.sleep(2)

        assert status == "completed"

    def test_ml_invalid_style_returns_ok(self, client):
        r = client.post(
            f"{ML_URL}/generate",
            json={
                "job_id": "fallback-ml-test-001",
                "shot_id": "00000000-0000-0000-0000-000000000001",
                "project_id": "00000000-0000-0000-0000-000000000002",
                "prompt": "test fallback",
                "visual_style": "totally_bogus_style",
                "model": "totally_bogus_model",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "processing"

    def test_unity_invalid_style_returns_ok(self, client):
        r = client.post(
            f"{UNITY_URL}/render",
            json={
                "job_id": "fallback-unity-test-001",
                "project_id": "00000000-0000-0000-0000-000000000003",
                "scene": {"project_id": "test", "shots": []},
                "visual_style": "totally_bogus_style",
                "template": "totally_bogus_template",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "processing"


class TestMLUnityConsistency:
    def test_ml_and_unity_share_same_styles(self, client):
        ml_r = client.get(f"{ML_URL}/styles")
        unity_r = client.get(f"{UNITY_URL}/styles")
        assert ml_r.status_code == 200
        assert unity_r.status_code == 200

        ml_styles = set(ml_r.json()["styles"].keys())
        unity_styles = set(unity_r.json()["styles"].keys())
        assert ml_styles == unity_styles, f"Style mismatch: ML={ml_styles}, Unity={unity_styles}"

    def test_ml_and_unity_same_default(self, client):
        ml_r = client.get(f"{ML_URL}/styles")
        unity_r = client.get(f"{UNITY_URL}/styles")
        assert ml_r.json()["default"] == unity_r.json()["default"]

    @pytest.mark.parametrize("style", ALL_STYLES)
    def test_style_available_in_both_services(self, client, style):
        ml_r = client.get(f"{ML_URL}/styles")
        unity_r = client.get(f"{UNITY_URL}/styles")
        assert style in ml_r.json()["styles"]
        assert style in unity_r.json()["styles"]

    @pytest.mark.parametrize("style", ALL_STYLES)
    def test_ml_generation_uses_correct_style(self, client, style):
        job_id = f"consistency-ml-{style}-{int(time.time())}"
        r = client.post(
            f"{ML_URL}/generate",
            json={
                "job_id": job_id,
                "shot_id": "00000000-0000-0000-0000-000000000010",
                "project_id": "00000000-0000-0000-0000-000000000020",
                "prompt": "consistency test",
                "visual_style": style,
                "model": style,
            },
        )
        assert r.status_code == 200
        assert r.json()["status"] == "processing"

        for _ in range(30):
            sr = client.get(f"{ML_URL}/status/{job_id}")
            assert sr.status_code == 200
            data = sr.json()
            if data["status"] == "completed":
                assert len(data["frame_urls"]) >= 1
                assert data["model"] == style
                return
            if data["status"] == "failed":
                pytest.fail(f"ML generation failed for style {style}")
            time.sleep(1)

        pytest.fail(f"ML generation timed out for style {style}")

    @pytest.mark.parametrize("style", ALL_STYLES)
    def test_unity_render_uses_correct_style(self, client, style):
        job_id = f"consistency-unity-{style}-{int(time.time())}"
        r = client.post(
            f"{UNITY_URL}/render",
            json={
                "job_id": job_id,
                "project_id": "00000000-0000-0000-0000-000000000030",
                "scene": {"project_id": "test", "visual_style": style, "shots": []},
                "visual_style": style,
                "template": style,
            },
        )
        assert r.status_code == 200
        assert r.json()["status"] == "processing"

        for _ in range(30):
            sr = client.get(f"{UNITY_URL}/status/{job_id}")
            assert sr.status_code == 200
            data = sr.json()
            if data["status"] == "completed":
                assert data["video_url"] != ""
                return
            if data["status"] == "failed":
                pytest.fail(f"Unity render failed for style {style}")
            time.sleep(1)

        pytest.fail(f"Unity render timed out for style {style}")

    def test_pipeline_style_propagation(self, client):
        style = "neon_ritual"
        r = client.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Propagation Test",
                "visual_style": style,
                "shots": [{"prompt": "ritual ceremony with cosmic energy", "order": 1}],
            },
            headers=HEADERS,
        )
        assert r.status_code == 200
        project = r.json()
        assert project["visual_style"] == style
        project_id = project["id"]

        r = client.get(f"{BASE_URL}/projects/{project_id}", headers=HEADERS)
        assert r.status_code == 200
        assert r.json()["visual_style"] == style

        r = client.post(f"{BASE_URL}/projects/{project_id}/render", headers=HEADERS)
        assert r.status_code == 200

        for _ in range(60):
            r = client.get(f"{BASE_URL}/projects/{project_id}/status", headers=HEADERS)
            data = r.json()
            if data["project_status"] in ("completed", "failed"):
                break
            time.sleep(2)

        assert data["project_status"] == "completed"
        assert len(data["ml_jobs"]) >= 1
        assert data["ml_jobs"][0]["status"] == "completed"
        assert len(data["render_jobs"]) >= 1
        assert data["render_jobs"][0]["status"] == "completed"
        assert data["render_jobs"][0]["video_url"] != ""

    def test_multi_shot_with_style(self, client):
        style = "spectral_mythology"
        r = client.post(
            f"{BASE_URL}/projects",
            json={
                "name": "Multi Shot Style Test",
                "visual_style": style,
                "shots": [
                    {"prompt": "ancient dragon guardian", "order": 1},
                    {"prompt": "luminous underwater temple", "order": 2},
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
            data = r.json()
            if data["project_status"] in ("completed", "failed"):
                break
            time.sleep(2)

        assert data["project_status"] == "completed"
        assert len(data["ml_jobs"]) == 2
        for ml_job in data["ml_jobs"]:
            assert ml_job["status"] == "completed"
