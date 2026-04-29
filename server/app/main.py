from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.migrations import init_db
from app.routes.auth import router as auth_router
from app.routes.payments import router as payments_router
from app.routes.script import router as script_router
from app.routes.slides import router as slides_router
from app.services.script_service import ensure_script_workspace_seeded

app = FastAPI()
settings = get_settings()


@app.on_event("startup")
def _startup() -> None:
  init_db()
  ensure_script_workspace_seeded()


origins = [origin.strip() for origin in settings.cors_allowed_origins.split(",") if origin.strip()]
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
  return {"status": "ok"}


app.include_router(slides_router)
app.include_router(script_router)
app.include_router(auth_router)
app.include_router(payments_router)
