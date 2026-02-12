# Daily Cinema — Production

Distributed video-generation pipeline with full orchestration, monitoring, autoscaling, and robust ML + Unity pipelines.

```
User → FastAPI → Redis Queue → Orchestrator → ML Module → GCS → Orchestrator → Unity HDRP → GCS → User
```

## Architecture

| Service | Port | Description |
|---------|------|-------------|
| Backend (FastAPI) | 8000 | Main API + orchestrator + Redis queue dispatch |
| ML Module | 8001 | Multi-model frame generation with caching |
| Unity Worker | 8002 | Multi-template video rendering with FFmpeg |
| PostgreSQL | 5432 | Database with connection pooling |
| Redis | 6379 | Job queue, DLQ, idempotency |
| GCS Emulator | 4443 | Google Cloud Storage emulator |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3000 | Dashboards and visualization |
| Loki | 3100 | Log aggregation |

## Quick Start (Local Development)

```bash
docker compose up --build
```

Wait for all services to start, then test:

```bash
# 1. Health checks
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready

# 2. Create a project (requires API key)
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dc-prod-api-key-change-me" \
  -d '{"name": "My Film", "shots": [{"prompt": "sunset over ocean", "order": 1}]}'

# 3. Start rendering (replace PROJECT_ID)
curl -X POST http://localhost:8000/projects/PROJECT_ID/render \
  -H "X-API-Key: dc-prod-api-key-change-me"

# 4. Check status
curl http://localhost:8000/projects/PROJECT_ID/status \
  -H "X-API-Key: dc-prod-api-key-change-me"
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health/live` | No | Liveness probe |
| GET | `/health/ready` | No | Readiness probe (DB + Redis) |
| GET | `/metrics` | No | Prometheus metrics |
| POST | `/projects` | Yes | Create a new project |
| GET | `/projects/{id}` | Yes | Get project details |
| GET | `/projects/{id}/timeline` | Yes | Get project timeline |
| POST | `/projects/{id}/render` | Yes | Start render pipeline |
| GET | `/projects/{id}/status` | Yes | Get full pipeline status |

**Authentication**: Pass `X-API-Key` header. Default key: `dc-prod-api-key-change-me`

**Rate Limiting**: 60 requests/minute per IP

## Production Features

### Backend
- Distributed orchestrator with Redis queue-based job dispatch
- Idempotent job execution with deduplication keys
- Retry with exponential backoff (ML: 3 retries / 2s base, Render: 3 retries / 3s base)
- Dead-letter queue for failed jobs
- API key authentication and rate limiting
- Connection pooling (pool_size=20, max_overflow=10)
- Structured JSON logging
- Prometheus metrics (job duration, error rates, queue size, retries)

### ML Module
- Multiple models: placeholder_v1, placeholder_v2, placeholder_artistic
- GPU warmup and model caching
- Temporal consistency with frame-to-frame color shifting
- Motion interpolation (multi-frame generation)
- Batch generation with configurable workers
- Prometheus metrics and health endpoints

### Unity Worker
- Multiple HDRP templates: default (24fps), cinematic (30fps HQ), fast_preview (15fps)
- Optimized FFmpeg pipeline with configurable preset/CRF/threads
- Material/texture caching
- Parallel render queue support
- Prometheus metrics and health endpoints

### Infrastructure
- Kubernetes manifests with HPA for backend (3-10), ML (2-8), Unity (2-8)
- CI/CD with GitHub Actions (build, test, Docker publish, K8s deploy)
- Monitoring stack: Prometheus + Grafana + Loki + Promtail
- Secret management via Kubernetes Secrets

## Kubernetes Deployment

```bash
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/secrets.yaml
kubectl apply -f k8s/base/configmap.yaml
kubectl apply -f k8s/base/redis.yaml
kubectl apply -f k8s/base/postgres.yaml
kubectl apply -f k8s/base/backend.yaml
kubectl apply -f k8s/base/ml-worker.yaml
kubectl apply -f k8s/base/unity-worker.yaml
kubectl apply -f k8s/base/monitoring.yaml
kubectl apply -f k8s/base/ingress.yaml
```

## Monitoring

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- Pre-configured dashboard: "Daily Cinema Overview"

### Key Metrics
- `dailycinema_ml_job_duration_seconds` — ML job processing time
- `dailycinema_render_duration_seconds` — Render job processing time
- `dailycinema_orchestrator_latency_seconds` — End-to-end pipeline latency
- `dailycinema_errors_total` — Error count by component
- `dailycinema_jobs_in_progress` — Active jobs gauge
- `dailycinema_queue_size` — Redis queue depth
- `dailycinema_retries_total` — Retry attempts

## Testing

```bash
# E2E tests (requires running services)
pip install httpx pytest
pytest tests/test_e2e.py -v

# Integration tests
pytest tests/test_integration.py -v

# Chaos tests
pytest tests/test_chaos.py -v

# Load tests (10+ parallel users)
pip install locust
locust -f tests/test_load.py --headless -u 10 -r 2 -t 60s
```

## Pipeline Flow

1. **Create Project** — stores project + shots in PostgreSQL
2. **Start Render** — enqueues pipeline job to Redis (idempotent)
3. **Orchestrator** dequeues and dispatches ML jobs (parallel, with retry)
4. **ML Module** generates frames using selected model, uploads to GCS
5. **Orchestrator** collects frame URLs, builds scene JSON
6. **Unity Worker** downloads frames, renders video with selected template
7. **Unity Worker** uploads final video to GCS
8. **Orchestrator** updates project status, records metrics
9. Failed jobs go to dead-letter queue for inspection

## Storage Structure

```
gs://dailycinema/
  projects/{project_id}/
    ml/
      shot_{shot_id}/
        frame_001.png
        frame_002.png
    render/
      final.mp4
```

## Database Models

- **Project** — name, description, status, error_message, timestamps
- **Shot** — project reference, order, prompt, status
- **MLJob** — shot reference, status, frame URLs, retry_count, error_message, started_at, completed_at
- **RenderJob** — project reference, status, video URL, retry_count, error_message, started_at, completed_at

## Development

```bash
# Backend
cd backend && poetry install && poetry run uvicorn app.main:app --reload --port 8000

# ML module
cd ml_module && poetry install && poetry run uvicorn app.main:app --reload --port 8001

# Unity worker
cd unity_worker && poetry install && poetry run uvicorn app.main:app --reload --port 8002
```

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy (async), PostgreSQL, Redis, Prometheus
- **ML Module**: FastAPI, Pillow, Prometheus
- **Unity Worker**: FastAPI, FFmpeg, Prometheus
- **Storage**: GCS (fake-gcs-server for local dev)
- **Monitoring**: Prometheus, Grafana, Loki, Promtail
- **Orchestration**: Kubernetes with HPA
- **CI/CD**: GitHub Actions
- **DevOps**: Docker, Docker Compose
