from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Iterator, Optional
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "tiktok_slide.db"
EMBEDS_DIR = DATA_DIR / "embeds"
RESULTS_DIR = DATA_DIR / "results"


def _utc_now() -> str:
  return datetime.utcnow().isoformat() + "Z"


def init_db() -> None:
  DATA_DIR.mkdir(parents=True, exist_ok=True)
  EMBEDS_DIR.mkdir(parents=True, exist_ok=True)
  RESULTS_DIR.mkdir(parents=True, exist_ok=True)
  conn = sqlite3.connect(DB_PATH)
  try:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS slides (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        title TEXT NOT NULL,
        subtitle TEXT NOT NULL,
        text TEXT NOT NULL,
        design TEXT NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        position INTEGER NOT NULL DEFAULT 0,
        selected_result_id TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
      """
    )
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS slide_results (
        id TEXT PRIMARY KEY,
        slide_id TEXT NOT NULL,
        title TEXT NOT NULL,
        note TEXT NOT NULL,
        tone TEXT NOT NULL,
        status TEXT NOT NULL,
        image_path TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (slide_id) REFERENCES slides(id) ON DELETE CASCADE
      )
      """
    )
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS embed_assets (
        id TEXT PRIMARY KEY,
        slide_id TEXT NOT NULL,
        label TEXT NOT NULL,
        name TEXT NOT NULL,
        context TEXT NOT NULL DEFAULT '',
        file_path TEXT NOT NULL,
        mime_type TEXT NOT NULL,
        size INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (slide_id) REFERENCES slides(id) ON DELETE CASCADE
      )
      """
    )
    if not _column_exists(conn, "embed_assets", "context"):
      conn.execute("ALTER TABLE embed_assets ADD COLUMN context TEXT NOT NULL DEFAULT ''")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_slides_position ON slides(position)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_results_slide_id ON slide_results(slide_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_embeds_slide_id ON embed_assets(slide_id)")
    conn.commit()
  finally:
    conn.close()


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
  rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
  return any(row[1] == column for row in rows)


@contextmanager
def db_connection() -> Iterator[sqlite3.Connection]:
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  conn.execute("PRAGMA busy_timeout=5000;")
  conn.execute("PRAGMA foreign_keys=ON;")
  try:
    yield conn
    conn.commit()
  finally:
    conn.close()


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


def _row_to_dict(row: sqlite3.Row) -> dict:
  return dict(row) if row else {}


def create_slide(
  conn: sqlite3.Connection,
  name: str,
  title: str,
  subtitle: str,
  text: str,
  design: str,
  quantity: int,
  position: int,
) -> dict:
  slide_id = uuid4().hex
  timestamp = _utc_now()
  conn.execute(
    """
    INSERT INTO slides (id, name, title, subtitle, text, design, quantity, position, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (slide_id, name, title, subtitle, text, design, quantity, position, timestamp, timestamp),
  )
  return get_slide(conn, slide_id)


def list_slides(conn: sqlite3.Connection) -> list[dict]:
  rows = conn.execute("SELECT * FROM slides ORDER BY position ASC, created_at ASC").fetchall()
  return [dict(row) for row in rows]


def get_slide(conn: sqlite3.Connection, slide_id: str) -> Optional[dict]:
  row = conn.execute("SELECT * FROM slides WHERE id = ?", (slide_id,)).fetchone()
  return dict(row) if row else None


def update_slide(conn: sqlite3.Connection, slide_id: str, data: dict) -> Optional[dict]:
  if not data:
    return get_slide(conn, slide_id)

  allowed = {
    "name",
    "title",
    "subtitle",
    "text",
    "design",
    "quantity",
    "position",
    "selected_result_id",
  }
  updates = []
  values: dict = {}
  for key in allowed:
    if key in data:
      updates.append(f"{key} = :{key}")
      values[key] = data[key]

  if not updates:
    return get_slide(conn, slide_id)

  values["updated_at"] = _utc_now()
  values["slide_id"] = slide_id
  updates.append("updated_at = :updated_at")

  conn.execute(f"UPDATE slides SET {', '.join(updates)} WHERE id = :slide_id", values)
  if conn.total_changes == 0:
    return None
  return get_slide(conn, slide_id)


def delete_slide(conn: sqlite3.Connection, slide_id: str) -> bool:
  conn.execute("DELETE FROM slides WHERE id = ?", (slide_id,))
  return conn.total_changes > 0


def create_result(
  conn: sqlite3.Connection,
  slide_id: str,
  title: str,
  note: str,
  tone: str,
  status: str,
  image_path: Optional[str],
) -> dict:
  result_id = uuid4().hex
  timestamp = _utc_now()
  conn.execute(
    """
    INSERT INTO slide_results (id, slide_id, title, note, tone, status, image_path, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (result_id, slide_id, title, note, tone, status, image_path, timestamp, timestamp),
  )
  return get_result(conn, result_id)


def get_result(conn: sqlite3.Connection, result_id: str) -> Optional[dict]:
  row = conn.execute("SELECT * FROM slide_results WHERE id = ?", (result_id,)).fetchone()
  return dict(row) if row else None


def list_results(conn: sqlite3.Connection, slide_id: str) -> list[dict]:
  rows = conn.execute(
    "SELECT * FROM slide_results WHERE slide_id = ? ORDER BY created_at ASC",
    (slide_id,),
  ).fetchall()
  return [dict(row) for row in rows]


def list_result_paths(conn: sqlite3.Connection, slide_id: str) -> list[str]:
  rows = conn.execute(
    "SELECT image_path FROM slide_results WHERE slide_id = ? AND image_path IS NOT NULL",
    (slide_id,),
  ).fetchall()
  return [row["image_path"] for row in rows]


def delete_result(conn: sqlite3.Connection, result_id: str) -> Optional[dict]:
  result = get_result(conn, result_id)
  if not result:
    return None
  conn.execute("DELETE FROM slide_results WHERE id = ?", (result_id,))
  return result if conn.total_changes else None


def select_result(conn: sqlite3.Connection, slide_id: str, result_id: str) -> Optional[dict]:
  return update_slide(conn, slide_id, {"selected_result_id": result_id})


def create_embed(
  conn: sqlite3.Connection,
  slide_id: str,
  label: str,
  name: str,
  context: str,
  file_path: str,
  mime_type: str,
  size: int,
) -> dict:
  embed_id = uuid4().hex
  timestamp = _utc_now()
  conn.execute(
    """
    INSERT INTO embed_assets (id, slide_id, label, name, context, file_path, mime_type, size, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (embed_id, slide_id, label, name, context, file_path, mime_type, size, timestamp),
  )
  row = conn.execute("SELECT * FROM embed_assets WHERE id = ?", (embed_id,)).fetchone()
  return _row_to_dict(row)


def list_embeds(conn: sqlite3.Connection, slide_id: str) -> list[dict]:
  rows = conn.execute(
    "SELECT * FROM embed_assets WHERE slide_id = ? ORDER BY created_at ASC",
    (slide_id,),
  ).fetchall()
  return [dict(row) for row in rows]


def get_embed(conn: sqlite3.Connection, embed_id: str) -> Optional[dict]:
  row = conn.execute("SELECT * FROM embed_assets WHERE id = ?", (embed_id,)).fetchone()
  return dict(row) if row else None


def list_embed_paths(conn: sqlite3.Connection, slide_id: str) -> list[str]:
  rows = conn.execute(
    "SELECT file_path FROM embed_assets WHERE slide_id = ?",
    (slide_id,),
  ).fetchall()
  return [row["file_path"] for row in rows]


def delete_embed(conn: sqlite3.Connection, embed_id: str) -> Optional[dict]:
  embed = get_embed(conn, embed_id)
  if not embed:
    return None
  conn.execute("DELETE FROM embed_assets WHERE id = ?", (embed_id,))
  return embed if conn.total_changes else None


def update_embed(conn: sqlite3.Connection, embed_id: str, data: dict) -> Optional[dict]:
  if not data:
    return get_embed(conn, embed_id)

  allowed = {"label", "context"}
  updates = []
  values: dict = {}
  for key in allowed:
    if key in data:
      updates.append(f"{key} = :{key}")
      values[key] = data[key]

  if not updates:
    return get_embed(conn, embed_id)

  values["embed_id"] = embed_id
  conn.execute(f"UPDATE embed_assets SET {', '.join(updates)} WHERE id = :embed_id", values)
  if conn.total_changes == 0:
    return None
  return get_embed(conn, embed_id)
