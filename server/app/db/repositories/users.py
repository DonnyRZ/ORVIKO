from __future__ import annotations

import sqlite3
from typing import Optional
from uuid import uuid4

from app.db.repositories._utils import utc_now


def get_user_by_google_sub(conn: sqlite3.Connection, google_sub: str) -> Optional[dict]:
  row = conn.execute("SELECT * FROM users WHERE google_sub = ?", (google_sub,)).fetchone()
  return dict(row) if row else None


def get_user_by_id(conn: sqlite3.Connection, user_id: str) -> Optional[dict]:
  row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
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
  timestamp = utc_now()
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
    (name, email, picture, utc_now(), google_sub),
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
