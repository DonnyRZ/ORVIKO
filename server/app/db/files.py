from __future__ import annotations

from pathlib import Path
from typing import Optional
from uuid import uuid4

from app.db.connection import DATA_DIR, EMBEDS_DIR, RESULTS_DIR


def save_embed_file(file_bytes: bytes, original_name: str) -> tuple[str, int]:
  ext = Path(original_name).suffix or ".png"
  filename = f"{uuid4().hex}{ext}"
  target_path = EMBEDS_DIR / filename
  target_path.write_bytes(file_bytes)
  return f"embeds/{filename}", len(file_bytes)


def save_result_image(image_bytes: bytes, image_id: Optional[str] = None) -> str:
  image_id = image_id or uuid4().hex
  filename = f"{image_id}.png"
  target_path = RESULTS_DIR / filename
  target_path.write_bytes(image_bytes)
  return f"results/{filename}"


def delete_file(relative_path: Optional[str]) -> None:
  if not relative_path:
    return
  full_path = (DATA_DIR / relative_path).resolve()
  if DATA_DIR in full_path.parents and full_path.exists():
    full_path.unlink()
