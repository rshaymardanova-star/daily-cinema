# Frontend Integration Guide

## Architecture

The Daily Cinema MVP frontend is a Next.js 15 application (App Router) with three screens:

1. **Create** (`/`) — Project creation with shot prompts
2. **Status** (`/status/[id]`) — Real-time pipeline polling
3. **Result** (`/result/[id]`) — Video playback and download

## Backend API Integration

### Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/projects` | POST | Create project with shots |
| `/projects/{id}/render` | POST | Start render pipeline |
| `/projects/{id}/status` | GET | Poll pipeline status |
| `/health` | GET | Health check |

### API Client (`src/lib/api.ts`)

Fetch-based client with automatic JSON parsing and error handling:

```typescript
import { createProject, startRender, getProjectStatus } from "@/lib/api";
```

All functions throw `ApiError` on non-2xx responses with the backend's error detail.

### Polling (`src/lib/polling.ts`)

Exponential backoff polling for pipeline status:

- Initial interval: 1s
- Max interval: 8s
- Backoff factor: 1.5x
- Adaptive: 2s during rendering phase
- Auto-stops on `completed` or `failed`

## Flow

1. User fills project name + shot prompts → `POST /projects`
2. Immediately starts pipeline → `POST /projects/{id}/render`
3. Redirects to `/status/{id}` → polls `GET /projects/{id}/status`
4. On completion → redirects to `/result/{id}`
5. Result page shows video player + download link

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |

## Error Handling

- Network errors display retry message on status page
- API errors show backend error detail
- Failed pipelines show error state with "Create New" link
- Result page handles incomplete projects gracefully
