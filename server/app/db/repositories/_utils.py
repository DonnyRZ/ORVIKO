from __future__ import annotations

from datetime import datetime
import json
import sqlite3
from typing import Any


def utc_now() -> str:
  return datetime.utcnow().isoformat() + "Z"


def row_to_dict(row: sqlite3.Row) -> dict:
  return dict(row) if row else {}


def json_dumps(value: Any) -> str:
  return json.dumps(value, ensure_ascii=True)


def json_loads(value: str, fallback: Any) -> Any:
  if not value:
    return fallback
  try:
    return json.loads(value)
  except json.JSONDecodeError:
    return fallback
