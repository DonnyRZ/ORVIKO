# Backend setup (FastAPI + SQLite)

This project uses a Python backend (FastAPI) with SQLite, aligned with ORVIKO - Main.

## Create venv

From `ORVIKO - Tiktok Slide`:

```
python -m venv server\.venv
```

## Install dependencies

From `ORVIKO - Tiktok Slide/server`:

```
.\.venv\Scripts\python -m pip install -U pip
.\.venv\Scripts\pip install -e .
```

## Run the server

From `ORVIKO - Tiktok Slide/server`:

```
.\.venv\Scripts\uvicorn uvicorn_app:app --reload
```

Server runs on `http://localhost:8000`.

## Production notes

- Jalankan backend sebagai service seperti `systemd`, bukan terminal manual.
- Untuk deploy ORVIKO saat ini, Nginx perlu mem-proxy route same-origin berikut ke backend:
  - `/auth/`
  - `/payments/`
  - `/api/`
  - `/docs`
  - `/openapi.json`
- Frontend static export diserve dari `web/out`, jadi login Google dan payment flow tidak boleh bergantung pada absolute URL localhost.
- Backend tetap perlu env server-side berikut untuk OAuth redirect:

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=https://orviko.net/auth/google/callback
FRONTEND_BASE_URL=https://orviko.net
```

- Google Cloud Console untuk OAuth production perlu memuat:
  - `https://orviko.net`
  - `https://www.orviko.net`
  - `https://orviko.net/auth/google/callback`
  - `https://www.orviko.net/auth/google/callback`

## API endpoints (REST)

- `GET /health`
- `GET /slides`
- `POST /slides`
- `GET /slides/:id`
- `PATCH /slides/:id`
- `DELETE /slides/:id`
- `POST /slides/:id/embeds` (multipart form, field `file`)
- `POST /slides/:id/generate` (SSE stream)
- `POST /slides/:id/results/:resultId/select`
- `GET /results/:resultId/image`

## Local file storage

Files are stored under:

```
ORVIKO - Tiktok Slide/data
```

- Embeds: `data/embeds`
- Generated images: `data/results`
