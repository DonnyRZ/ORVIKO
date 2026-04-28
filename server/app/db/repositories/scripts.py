from __future__ import annotations

import sqlite3
from typing import Any, Optional
from uuid import uuid4

from app.db.repositories._utils import json_dumps, json_loads, utc_now


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
  data["source_options"] = json_loads(data.get("source_options", "[]"), [])
  data["observations"] = _normalize_script_observations(json_loads(data.get("observations", "{}"), {}))
  data["moments"] = json_loads(data.get("moments", "[]"), [])
  data["knowledge_base_snapshot"] = json_loads(data.get("knowledge_base_snapshot", "{}"), {})
  return data


def _script_knowledge_base_row_to_dict(row: sqlite3.Row) -> dict:
  if not row:
    return {}
  data = dict(row)
  data["summary"] = json_loads(data.get("summary", "{}"), {})
  data["data"] = json_loads(data.get("data", "{}"), {})
  return data


def create_script_knowledge_base(
  conn: sqlite3.Connection,
  title: str,
  summary: dict,
  data: dict,
) -> dict:
  knowledge_base_id = uuid4().hex
  timestamp = utc_now()
  conn.execute(
    """
    INSERT INTO script_knowledge_bases (id, title, summary, data, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (knowledge_base_id, title, json_dumps(summary), json_dumps(data), timestamp, timestamp),
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
  timestamp = utc_now()
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
      json_dumps(knowledge_base_snapshot),
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
      values[key] = json_dumps(data[key]) if key in json_fields else data[key]

  if not updates:
    return get_script_workspace(conn, workspace_id)

  values["updated_at"] = utc_now()
  values["workspace_id"] = workspace_id
  updates.append("updated_at = :updated_at")

  conn.execute(f"UPDATE script_workspaces SET {', '.join(updates)} WHERE id = :workspace_id", values)
  if conn.total_changes == 0:
    return None
  return get_script_workspace(conn, workspace_id)
