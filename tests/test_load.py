"""Load tests for Daily Cinema - run with: locust -f tests/test_load.py --headless -u 10 -r 2 -t 60s"""
import time
import json

from locust import HttpUser, task, between, events


class DailyCinemaUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:8000"

    def on_start(self):
        self.headers = {"X-API-Key": "dc-prod-api-key-change-me"}

    @task(3)
    def create_and_render_project(self):
        r = self.client.post(
            "/projects",
            json={"name": "Load Test", "shots": [{"prompt": "test scene", "order": 1}]},
            headers=self.headers,
        )
        if r.status_code != 200:
            return

        project_id = r.json()["id"]

        self.client.post(
            f"/projects/{project_id}/render",
            headers=self.headers,
            name="/projects/[id]/render",
        )

        for _ in range(30):
            r = self.client.get(
                f"/projects/{project_id}/status",
                headers=self.headers,
                name="/projects/[id]/status",
            )
            if r.status_code == 200:
                status = r.json().get("project_status", "")
                if status in ("completed", "failed"):
                    break
            time.sleep(2)

    @task(5)
    def check_health(self):
        self.client.get("/health/live")

    @task(2)
    def list_projects(self):
        self.client.get("/projects", headers=self.headers)
