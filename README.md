# Daily Cinema MVP

Distributed video-generation pipeline:

```
User → FastAPI → Orchestrator → ML Module → GCS → Orchestrator → Unity HDRP → GCS → User
```

## Architecture

| Service | Port | Description |
|---------|------|-------------|
| Backend (FastAPI) | 8000 | Main API + orchestrator |
| ML Module | 8001 | Placeholder frame generation |
| Unity Worker | 8002 | Placeholder video rendering |
| PostgreSQL | 5432 | Database |
| GCS Emulator | 4443 | Google Cloud Storage emulator |

## Quick Start

```bash
docker-compose up --build
```

Wait for all services to start, then test the pipeline:

```bash
# 1. Create a project
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "My First Film", "description": "A test project", "shots": [{"prompt": "A beautiful sunset", "order": 0}]}'

# 2. Start rendering (replace PROJECT_ID with the id from step 1)
curl -X POST http://localhost:8000/projects/PROJECT_ID/render

# 3. Check status
curl http://localhost:8000/projects/PROJECT_ID/status

# 4. Get timeline
curl http://localhost:8000/projects/PROJECT_ID/timeline
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/projects` | Create a new project |
| GET | `/projects/{id}` | Get project details |
| GET | `/projects/{id}/timeline` | Get project timeline |
| POST | `/projects/{id}/render` | Start render pipeline |
| GET | `/projects/{id}/status` | Get full pipeline status |
| GET | `/health` | Health check |

## Pipeline Flow

1. **Create Project** — stores project + shots in PostgreSQL
2. **Start Render** — triggers the orchestrator in background
3. **Orchestrator** dispatches ML jobs (one per shot) in parallel
4. **ML Module** generates placeholder frames, uploads to GCS emulator
5. **Orchestrator** collects frame URLs, builds scene JSON
6. **Unity Worker** downloads frames, renders placeholder video with ffmpeg
7. **Unity Worker** uploads final video to GCS emulator
8. **Orchestrator** updates project status to `completed`

## Storage Structure

```
gs://dailycinema/
  projects/{project_id}/
    ml/
      shot_{shot_id}/
        frame_001.png
    render/
      final.mp4
```

## Database Models

- **Project** — name, description, status, timestamps
- **Shot** — project reference, order, prompt, status
- **MLJob** — shot reference, status, frame URLs
- **RenderJob** — project reference, status, video URL, scene JSON

## Development

Each service can be developed independently:

```bash
# Backend only
cd backend && poetry install && poetry run uvicorn app.main:app --reload --port 8000

# ML module only
cd ml_module && poetry install && poetry run uvicorn app.main:app --reload --port 8001

# Unity worker only
cd unity_worker && poetry install && poetry run uvicorn app.main:app --reload --port 8002
```

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy (async), PostgreSQL
- **ML Module**: FastAPI, Pillow
- **Unity Worker**: FastAPI, ffmpeg
- **Storage**: fake-gcs-server (GCS emulator)
- **DevOps**: Docker, docker-compose
