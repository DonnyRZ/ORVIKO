from __future__ import annotations

import sqlite3
from typing import Optional
from uuid import uuid4

from app.db.repositories._utils import row_to_dict, utc_now


def create_slide(
  conn: sqlite3.Connection,
  title: str,
  text: str,
  design: str,
  quantity: int,
  aspect_ratio: str,
) -> dict:
  slide_id = uuid4().hex
  timestamp = utc_now()
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

  values["updated_at"] = utc_now()
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
  timestamp = utc_now()
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
  timestamp = utc_now()
  conn.execute(
    """
    INSERT INTO embed_assets (id, slide_id, label, name, context, file_path, mime_type, size, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (embed_id, slide_id, label, name, context, file_path, mime_type, size, timestamp),
  )
  row = conn.execute("SELECT * FROM embed_assets WHERE id = ?", (embed_id,)).fetchone()
  return row_to_dict(row)


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
