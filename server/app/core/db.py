from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterator, Optional
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
    conn.execute("PRAGMA foreign_keys=OFF;")
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS slides (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        text TEXT NOT NULL,
        design TEXT NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        aspect_ratio TEXT NOT NULL DEFAULT '9:16',
        selected_result_id TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
      """
    )
    if (
      _column_exists(conn, "slides", "name")
      or _column_exists(conn, "slides", "position")
      or _column_exists(conn, "slides", "subtitle")
      or not _column_exists(conn, "slides", "aspect_ratio")
    ):
      _migrate_slides_table(conn)
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_results_slide_id ON slide_results(slide_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_embeds_slide_id ON embed_assets(slide_id)")
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS script_knowledge_bases (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        data TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
      """
    )
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS script_workspaces (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        knowledge_base_id TEXT NOT NULL,
        knowledge_base_snapshot TEXT NOT NULL DEFAULT '{}',
        current_step TEXT NOT NULL DEFAULT 'task',
        active_profile_id TEXT NOT NULL DEFAULT '',
        task TEXT NOT NULL DEFAULT '',
        selected_source TEXT NOT NULL DEFAULT '',
        source_options TEXT NOT NULL DEFAULT '[]',
        observations TEXT NOT NULL DEFAULT '{}',
        moments TEXT NOT NULL DEFAULT '[]',
        observation_variant_index INTEGER NOT NULL DEFAULT 0,
        moment_variant_index INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (knowledge_base_id) REFERENCES script_knowledge_bases(id) ON DELETE RESTRICT
      )
      """
    )
    if not _column_exists(conn, "script_workspaces", "knowledge_base_snapshot"):
      conn.execute("ALTER TABLE script_workspaces ADD COLUMN knowledge_base_snapshot TEXT NOT NULL DEFAULT '{}'")
    if not _column_exists(conn, "script_workspaces", "active_profile_id"):
      conn.execute("ALTER TABLE script_workspaces ADD COLUMN active_profile_id TEXT NOT NULL DEFAULT ''")
    if not _column_exists(conn, "script_workspaces", "observation_variant_index"):
      conn.execute("ALTER TABLE script_workspaces ADD COLUMN observation_variant_index INTEGER NOT NULL DEFAULT 0")
    if not _column_exists(conn, "script_workspaces", "moment_variant_index"):
      conn.execute("ALTER TABLE script_workspaces ADD COLUMN moment_variant_index INTEGER NOT NULL DEFAULT 0")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_script_workspace_kb_id ON script_workspaces(knowledge_base_id)")
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        google_sub TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL DEFAULT '',
        email TEXT NOT NULL UNIQUE,
        picture TEXT NOT NULL DEFAULT '',
        auth_provider TEXT NOT NULL DEFAULT 'google',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
      """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_users_google_sub ON users(google_sub)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    conn.commit()
  finally:
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.close()


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
  rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
  return any(row[1] == column for row in rows)


def _migrate_slides_table(conn: sqlite3.Connection) -> None:
  has_aspect_ratio = _column_exists(conn, "slides", "aspect_ratio")
  conn.execute(
    """
    CREATE TABLE slides_v2 (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      text TEXT NOT NULL,
      design TEXT NOT NULL,
      quantity INTEGER NOT NULL DEFAULT 1,
      aspect_ratio TEXT NOT NULL DEFAULT '9:16',
      selected_result_id TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
    """
  )
  conn.execute(
    (
      """
      INSERT INTO slides_v2 (id, title, text, design, quantity, aspect_ratio, selected_result_id, created_at, updated_at)
      SELECT id, title, text, design, quantity, COALESCE(aspect_ratio, '9:16'), selected_result_id, created_at, updated_at
      FROM slides
      ORDER BY created_at ASC
      """
      if has_aspect_ratio
      else """
      INSERT INTO slides_v2 (id, title, text, design, quantity, aspect_ratio, selected_result_id, created_at, updated_at)
      SELECT id, title, text, design, quantity, '9:16', selected_result_id, created_at, updated_at
      FROM slides
      ORDER BY created_at ASC
      """
    )
  )
  conn.execute("DROP TABLE slides")
  conn.execute("ALTER TABLE slides_v2 RENAME TO slides")


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
  title: str,
  text: str,
  design: str,
  quantity: int,
  aspect_ratio: str,
) -> dict:
  slide_id = uuid4().hex
  timestamp = _utc_now()
  conn.execute(
    """
    INSERT INTO slides (id, title, text, design, quantity, aspect_ratio, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (slide_id, title, text, design, quantity, aspect_ratio, timestamp, timestamp),
  )
  return get_slide(conn, slide_id)


def list_slides(conn: sqlite3.Connection) -> list[dict]:
  rows = conn.execute("SELECT * FROM slides ORDER BY created_at ASC").fetchall()
  return [dict(row) for row in rows]


def get_slide(conn: sqlite3.Connection, slide_id: str) -> Optional[dict]:
  row = conn.execute("SELECT * FROM slides WHERE id = ?", (slide_id,)).fetchone()
  return dict(row) if row else None


def update_slide(conn: sqlite3.Connection, slide_id: str, data: dict) -> Optional[dict]:
  if not data:
    return get_slide(conn, slide_id)

  allowed = {
    "title",
    "text",
    "design",
    "quantity",
    "aspect_ratio",
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


def _json_dumps(value: Any) -> str:
  return json.dumps(value, ensure_ascii=True)


def _json_loads(value: str, fallback: Any) -> Any:
  if not value:
    return fallback
  try:
    return json.loads(value)
  except json.JSONDecodeError:
    return fallback


def _normalize_script_observations(value: Any) -> dict:
  if not isinstance(value, dict):
    return {"perilaku": [], "emosi": [], "situasi": []}
  return {
    "perilaku": value.get("perilaku") if isinstance(value.get("perilaku"), list) else [],
    "emosi": value.get("emosi") if isinstance(value.get("emosi"), list) else [],
    "situasi": value.get("situasi") if isinstance(value.get("situasi"), list) else [],
  }


def _script_workspace_row_to_dict(row: sqlite3.Row) -> dict:
  if not row:
    return {}
  data = dict(row)
  data["source_options"] = _json_loads(data.get("source_options", "[]"), [])
  data["observations"] = _normalize_script_observations(_json_loads(data.get("observations", "{}"), {}))
  data["moments"] = _json_loads(data.get("moments", "[]"), [])
  data["knowledge_base_snapshot"] = _json_loads(data.get("knowledge_base_snapshot", "{}"), {})
  return data


def _script_knowledge_base_row_to_dict(row: sqlite3.Row) -> dict:
  if not row:
    return {}
  data = dict(row)
  data["summary"] = _json_loads(data.get("summary", "{}"), {})
  data["data"] = _json_loads(data.get("data", "{}"), {})
  return data


def create_script_knowledge_base(
  conn: sqlite3.Connection,
  title: str,
  summary: dict,
  data: dict,
) -> dict:
  knowledge_base_id = uuid4().hex
  timestamp = _utc_now()
  conn.execute(
    """
    INSERT INTO script_knowledge_bases (id, title, summary, data, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (knowledge_base_id, title, _json_dumps(summary), _json_dumps(data), timestamp, timestamp),
  )
  return get_script_knowledge_base(conn, knowledge_base_id)


def list_script_knowledge_bases(conn: sqlite3.Connection) -> list[dict]:
  rows = conn.execute("SELECT * FROM script_knowledge_bases ORDER BY created_at ASC").fetchall()
  return [_script_knowledge_base_row_to_dict(row) for row in rows]


def get_script_knowledge_base(conn: sqlite3.Connection, knowledge_base_id: str) -> Optional[dict]:
  row = conn.execute("SELECT * FROM script_knowledge_bases WHERE id = ?", (knowledge_base_id,)).fetchone()
  return _script_knowledge_base_row_to_dict(row) if row else None


def get_first_script_knowledge_base(conn: sqlite3.Connection) -> Optional[dict]:
  row = conn.execute("SELECT * FROM script_knowledge_bases ORDER BY created_at ASC LIMIT 1").fetchone()
  return _script_knowledge_base_row_to_dict(row) if row else None


def create_script_workspace(
  conn: sqlite3.Connection,
  title: str,
  knowledge_base_id: str,
  knowledge_base_snapshot: dict,
) -> dict:
  workspace_id = uuid4().hex
  timestamp = _utc_now()
  conn.execute(
    """
    INSERT INTO script_workspaces (
      id,
      title,
      knowledge_base_id,
      knowledge_base_snapshot,
      current_step,
      active_profile_id,
      task,
      selected_source,
      source_options,
      observations,
      moments,
      observation_variant_index,
      moment_variant_index,
      created_at,
      updated_at
    )
    VALUES (?, ?, ?, ?, 'task', '', '', '', '[]', '{}', '[]', 0, 0, ?, ?)
    """,
    (
      workspace_id,
      title,
      knowledge_base_id,
      _json_dumps(knowledge_base_snapshot),
      timestamp,
      timestamp,
    ),
  )
  return get_script_workspace(conn, workspace_id)


def list_script_workspaces(conn: sqlite3.Connection) -> list[dict]:
  rows = conn.execute("SELECT * FROM script_workspaces ORDER BY created_at ASC").fetchall()
  return [_script_workspace_row_to_dict(row) for row in rows]


def get_script_workspace(conn: sqlite3.Connection, workspace_id: str) -> Optional[dict]:
  row = conn.execute("SELECT * FROM script_workspaces WHERE id = ?", (workspace_id,)).fetchone()
  return _script_workspace_row_to_dict(row) if row else None


def get_first_script_workspace(conn: sqlite3.Connection) -> Optional[dict]:
  row = conn.execute("SELECT * FROM script_workspaces ORDER BY created_at ASC LIMIT 1").fetchone()
  return _script_workspace_row_to_dict(row) if row else None


def get_latest_script_workspace(conn: sqlite3.Connection) -> Optional[dict]:
  row = conn.execute("SELECT * FROM script_workspaces ORDER BY created_at DESC LIMIT 1").fetchone()
  return _script_workspace_row_to_dict(row) if row else None


def update_script_workspace(conn: sqlite3.Connection, workspace_id: str, data: dict) -> Optional[dict]:
  if not data:
    return get_script_workspace(conn, workspace_id)

  allowed = {
    "title",
    "knowledge_base_id",
    "knowledge_base_snapshot",
    "current_step",
    "active_profile_id",
    "task",
    "selected_source",
    "source_options",
    "observations",
    "moments",
    "observation_variant_index",
    "moment_variant_index",
  }
  json_fields = {"knowledge_base_snapshot", "source_options", "observations", "moments"}
  updates = []
  values: dict[str, Any] = {}
  for key in allowed:
    if key in data:
      updates.append(f"{key} = :{key}")
      values[key] = _json_dumps(data[key]) if key in json_fields else data[key]

  if not updates:
    return get_script_workspace(conn, workspace_id)

  values["updated_at"] = _utc_now()
  values["workspace_id"] = workspace_id
  updates.append("updated_at = :updated_at")

  conn.execute(f"UPDATE script_workspaces SET {', '.join(updates)} WHERE id = :workspace_id", values)
  if conn.total_changes == 0:
    return None
  return get_script_workspace(conn, workspace_id)


def get_user_by_google_sub(conn: sqlite3.Connection, google_sub: str) -> Optional[dict]:
  row = conn.execute("SELECT * FROM users WHERE google_sub = ?", (google_sub,)).fetchone()
  return dict(row) if row else None


def create_user(
  conn: sqlite3.Connection,
  google_sub: str,
  name: str,
  email: str,
  picture: str,
  auth_provider: str = "google",
) -> dict:
  user_id = uuid4().hex
  timestamp = _utc_now()
  conn.execute(
    """
    INSERT INTO users (id, google_sub, name, email, picture, auth_provider, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (user_id, google_sub, name, email, picture, auth_provider, timestamp, timestamp),
  )
  row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
  return dict(row) if row else {}


def update_user_by_google_sub(
  conn: sqlite3.Connection,
  google_sub: str,
  *,
  name: str,
  email: str,
  picture: str,
) -> Optional[dict]:
  conn.execute(
    """
    UPDATE users
    SET name = ?, email = ?, picture = ?, updated_at = ?
    WHERE google_sub = ?
    """,
    (name, email, picture, _utc_now(), google_sub),
  )
  return get_user_by_google_sub(conn, google_sub)


def upsert_google_user(
  conn: sqlite3.Connection,
  *,
  google_sub: str,
  name: str,
  email: str,
  picture: str,
) -> dict:
  existing = get_user_by_google_sub(conn, google_sub)
  if existing:
    return update_user_by_google_sub(
      conn,
      google_sub,
      name=name,
      email=email,
      picture=picture,
    ) or existing
  return create_user(
    conn,
    google_sub=google_sub,
    name=name,
    email=email,
    picture=picture,
  )
