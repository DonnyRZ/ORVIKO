# ODIN - TikTok Slide

Workspace to generate 9:16 TikTok slide images with a three‑panel UI and a Python backend.

## What this app does
- Create slide drafts (text + optional user notes).
- Upload embed images (logos/icons) per slide.
- Generate image variations per slide.
- Preview and download selected results.
- Manage slides, embeds, and generated results.

## Tech stack
- Frontend: Next.js (App Router), React, TypeScript.
- Backend: FastAPI (Python), SQLite, Google GenAI client.

## Project structure
- `web/` Next.js frontend.
- `server/` FastAPI backend + SQLite + GenAI integration.
- `data/` Generated images, embed images, and local SQLite DB (auto‑created).
- `app-flow.md` Product flow reference.

## Setup

### Prerequisites
- Node.js 18+ (or 20+ recommended)
- Python 3.10+

### 1) Backend
From repo root:

```powershell
cd "ODIN - Tiktok Slide\server"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
.\.venv\Scripts\uvicorn uvicorn_app:app --reload
```

Backend health check:
`http://127.0.0.1:8000/health`

### 2) Frontend
From repo root:

```powershell
cd "ODIN - Tiktok Slide\web"
npm install
npm run dev
```

Frontend:
`http://localhost:3000`

## Environment variables
Backend reads `.env` at repo root.

```env
GENAI_API_KEY=
GENAI_MODEL=gemini-3-flash-preview
IMAGE_AI_KEY=
IMAGE_GEN=gemini-3-pro-image-preview

ALLOW_GOOGLE_SEARCH=false
IMAGE_ASPECT_RATIO=9:16
IMAGE_SIZE=2K
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Frontend can override API base URL via `web/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

## Usage flow (short)
1) Create or open a slide.
2) Add slide text (required).
3) Optional: add user notes (style or context).
4) Upload embed images (logos/icons), then add label + context.
5) Generate images.
6) Choose result → preview → download.

## Notes
- Generated files and SQLite DB live under `data/` (ignored by git).
- If a result is deleted, the image file is removed from disk.
- Use embed label/context to ensure the right logo matches the right brand.
