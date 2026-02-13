# Vercel Deployment Guide

## Prerequisites

- Vercel account connected to GitHub
- Backend deployed and accessible via public URL

## Setup

### 1. Connect Repository

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import `rshaymardanova-star/daily-cinema`
3. Set root directory to `frontend`
4. Framework preset: Next.js

### 2. Environment Variables

Add in Vercel project settings → Environment Variables:

| Variable | Value | Example |
|----------|-------|---------|
| `NEXT_PUBLIC_API_URL` | Your backend URL | `https://api.dailycinema.example.com` |

### 3. Build Settings

- Build command: `npm run build`
- Output directory: `.next`
- Install command: `npm install`

### 4. Deploy

Push to the branch or trigger deploy from Vercel dashboard.

## Backend CORS

Ensure your FastAPI backend allows the Vercel domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Custom Domain (Optional)

1. Go to project settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Update `NEXT_PUBLIC_API_URL` if backend domain changes

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API calls fail | Check `NEXT_PUBLIC_API_URL` is set and backend is accessible |
| CORS errors | Add Vercel domain to backend CORS origins |
| Build fails | Run `npm run build` locally first to check for errors |
