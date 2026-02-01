# Backend setup (FastAPI + SQLite)

This project uses a Python backend (FastAPI) with SQLite, aligned with ODIN - Main.

## Create venv

From `ODIN - Tiktok Slide`:

```
python -m venv server\.venv
```

## Install dependencies

From `ODIN - Tiktok Slide/server`:

```
.\.venv\Scripts\python -m pip install -U pip
.\.venv\Scripts\pip install -e .
```

## Run the server

From `ODIN - Tiktok Slide/server`:

```
.\.venv\Scripts\uvicorn uvicorn_app:app --reload
```

Server runs on `http://localhost:8000`.

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
ODIN - Tiktok Slide/data
```

- Embeds: `data/embeds`
- Generated images: `data/results`
