# Client Testing Guide

## Local Testing

### 1. Start Backend

```bash
cd /path/to/dailycinema
docker-compose up -d
```

Verify backend is running:
```bash
curl http://localhost:8000/health
```

### 2. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

### 3. Test Flow

#### Create Project
1. Enter a project name (e.g., "Test Video")
2. Add one or more shot prompts
3. Click "Create & Generate"
4. Verify redirect to status page

#### Monitor Status
1. Watch progress bar fill
2. Verify ML Generation step completes
3. Verify Video Rendering step starts
4. Wait for completion

#### View Result
1. Verify automatic redirect to result page
2. Check video player loads
3. Test video playback controls
4. Test download link
5. Test "Create Another" link

## Test Scenarios

### Happy Path
- Single shot project → completes successfully
- Multi-shot project → all shots process → video renders

### Error Cases
- Empty project name → form validation prevents submit
- Backend down → error message on status page with retry
- Invalid project ID in URL → error displayed on result page

### Edge Cases
- Navigate directly to `/status/nonexistent-id` → error handling
- Navigate to `/result/{id}` before completion → "Not Ready" message
- Refresh status page → polling resumes from current state

## Deployed Testing

1. Open the Vercel preview URL
2. Verify the same flow works against the deployed backend
3. Check browser console for CORS or network errors
4. Test on mobile viewport (responsive design)

## Expected Behavior

| Action | Expected Result |
|--------|----------------|
| Submit form | Redirect to `/status/{id}` |
| Poll status | Progress updates every 1-8s |
| Pipeline completes | Auto-redirect to `/result/{id}` |
| Pipeline fails | Error state with retry option |
| Download video | Browser downloads MP4 file |
