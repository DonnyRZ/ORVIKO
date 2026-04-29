from __future__ import annotations

import sqlite3
from typing import Any, Optional
from uuid import uuid4

from app.db.repositories._utils import json_dumps, utc_now


def create_payment(
  conn: sqlite3.Connection,
  *,
  user_id: str,
  order_id: str,
  plan: str,
  gross_amount: int,
  currency: str = "IDR",
  status: str = "created",
) -> dict:
  payment_id = uuid4().hex
  timestamp = utc_now()
  conn.execute(
    """
    INSERT INTO payments (
      id,
      user_id,
      order_id,
      plan,
      gross_amount,
      currency,
      status,
      created_at,
      updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (payment_id, user_id, order_id, plan, gross_amount, currency, status, timestamp, timestamp),
  )
  row = conn.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)).fetchone()
  return dict(row) if row else {}


def get_payment(conn: sqlite3.Connection, payment_id: str) -> Optional[dict]:
  row = conn.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)).fetchone()
  return dict(row) if row else None


def get_payment_by_order_id(conn: sqlite3.Connection, order_id: str) -> Optional[dict]:
  row = conn.execute("SELECT * FROM payments WHERE order_id = ?", (order_id,)).fetchone()
  return dict(row) if row else None


def update_payment_snap_details(
  conn: sqlite3.Connection,
  payment_id: str,
  *,
  snap_token: str,
  snap_redirect_url: str,
  status: str = "pending",
) -> Optional[dict]:
  conn.execute(
    """
    UPDATE payments
    SET snap_token = ?, snap_redirect_url = ?, status = ?, updated_at = ?
    WHERE id = ?
    """,
    (snap_token, snap_redirect_url, status, utc_now(), payment_id),
  )
  return get_payment(conn, payment_id)


def update_payment_status(
  conn: sqlite3.Connection,
  payment_id: str,
  *,
  status: str,
  midtrans_transaction_id: str = "",
  midtrans_order_id: str = "",
  raw_notification: dict[str, Any] | None = None,
) -> Optional[dict]:
  conn.execute(
    """
    UPDATE payments
    SET status = ?, midtrans_transaction_id = ?, midtrans_order_id = ?, raw_notification = ?, updated_at = ?
    WHERE id = ?
    """,
    (
      status,
      midtrans_transaction_id,
      midtrans_order_id,
      json_dumps(raw_notification or {}),
      utc_now(),
      payment_id,
    ),
  )
  return get_payment(conn, payment_id)
