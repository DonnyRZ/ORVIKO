from __future__ import annotations

import base64
import hashlib
from typing import Any
from uuid import uuid4

import requests
from fastapi import HTTPException

from app.core.config import get_settings
from app.core.db import (
  create_payment,
  db_connection,
  get_payment,
  get_payment_by_order_id,
  get_user_by_id,
  update_payment_snap_details,
  update_payment_status,
)

PLAN_CATALOG = {
  "starter": {"name": "Starter", "gross_amount": 79000},
  "creator": {"name": "Creator", "gross_amount": 199000},
  "pro": {"name": "Pro", "gross_amount": 499000},
}


def _build_order_id(plan: str) -> str:
  return f"ORVIKO-{plan.upper()}-{uuid4().hex[:12].upper()}"


def _build_midtrans_auth_header(server_key: str) -> dict[str, str]:
  encoded = base64.b64encode(f"{server_key}:".encode("utf-8")).decode("utf-8")
  return {
    "Authorization": f"Basic {encoded}",
    "Content-Type": "application/json",
    "Accept": "application/json",
  }


def create_midtrans_transaction(*, user_id: str, plan: str, price: int, email: str | None = None) -> dict[str, Any]:
  settings = get_settings()
  if not settings.midtrans_server_key:
    raise HTTPException(status_code=500, detail="Midtrans server key belum dikonfigurasi.")

  if plan not in PLAN_CATALOG:
    raise HTTPException(status_code=400, detail="Paket yang dipilih tidak valid.")

  catalog_item = PLAN_CATALOG[plan]
  expected_amount = int(catalog_item["gross_amount"])
  if int(price) != expected_amount:
    raise HTTPException(status_code=400, detail="Harga paket tidak sesuai.")

  with db_connection() as conn:
    user = get_user_by_id(conn, user_id)
    if not user:
      raise HTTPException(status_code=404, detail="User tidak ditemukan.")

    order_id = _build_order_id(plan)
    payment = create_payment(
      conn,
      user_id=user_id,
      order_id=order_id,
      plan=plan,
      gross_amount=expected_amount,
    )

  payload = {
    "transaction_details": {
      "order_id": payment["order_id"],
      "gross_amount": expected_amount,
    },
    "item_details": [
      {
        "id": plan,
        "price": expected_amount,
        "quantity": 1,
        "name": catalog_item["name"],
      }
    ],
    "customer_details": {
      "first_name": user.get("name") or "User ORVIKO",
      "email": email or user.get("email") or "",
    },
  }

  response = requests.post(
    f"{settings.midtrans_snap_base_url}/snap/v1/transactions",
    json=payload,
    headers=_build_midtrans_auth_header(settings.midtrans_server_key),
    timeout=30,
  )

  if not response.ok:
    raise HTTPException(status_code=400, detail="Gagal membuat transaksi Midtrans.")

  data = response.json()
  snap_token = data.get("token", "")
  redirect_url = data.get("redirect_url", "")
  if not snap_token or not redirect_url:
    raise HTTPException(status_code=400, detail="Respons Midtrans tidak lengkap.")

  with db_connection() as conn:
    updated_payment = update_payment_snap_details(
      conn,
      payment["id"],
      snap_token=snap_token,
      snap_redirect_url=redirect_url,
      status="pending",
    )

  if not updated_payment:
    raise HTTPException(status_code=500, detail="Gagal menyimpan transaksi payment.")

  return {
    "payment_id": updated_payment["id"],
    "order_id": updated_payment["order_id"],
    "snap_token": updated_payment["snap_token"],
    "redirect_url": updated_payment["snap_redirect_url"],
    "status": updated_payment["status"],
  }


def get_payment_status(payment_id: str) -> dict[str, Any]:
  with db_connection() as conn:
    payment = get_payment(conn, payment_id)
  if not payment:
    raise HTTPException(status_code=404, detail="Payment tidak ditemukan.")

  return {
    "payment_id": payment["id"],
    "order_id": payment["order_id"],
    "plan": payment["plan"],
    "gross_amount": payment["gross_amount"],
    "currency": payment["currency"],
    "status": payment["status"],
    "user_id": payment["user_id"],
    "updated_at": payment["updated_at"],
  }


def _expected_signature(order_id: str, status_code: str, gross_amount: str, server_key: str) -> str:
  raw = f"{order_id}{status_code}{gross_amount}{server_key}"
  return hashlib.sha512(raw.encode("utf-8")).hexdigest()


def _map_midtrans_status(payload: dict[str, Any]) -> str:
  transaction_status = str(payload.get("transaction_status") or "").lower()
  fraud_status = str(payload.get("fraud_status") or "").lower()

  if transaction_status == "capture":
    return "capture" if fraud_status == "challenge" else "settlement"
  if transaction_status in {"settlement", "pending", "deny", "cancel", "expire", "failure"}:
    return transaction_status
  return transaction_status or "unknown"


def handle_midtrans_notification(payload: dict[str, Any]) -> dict[str, Any]:
  settings = get_settings()
  if not settings.midtrans_server_key:
    raise HTTPException(status_code=500, detail="Midtrans server key belum dikonfigurasi.")

  order_id = str(payload.get("order_id") or "")
  status_code = str(payload.get("status_code") or "")
  gross_amount = str(payload.get("gross_amount") or "")
  signature_key = str(payload.get("signature_key") or "")

  if not order_id or not status_code or not gross_amount or not signature_key:
    raise HTTPException(status_code=400, detail="Payload Midtrans tidak lengkap.")

  expected = _expected_signature(order_id, status_code, gross_amount, settings.midtrans_server_key)
  if signature_key != expected:
    raise HTTPException(status_code=400, detail="Signature Midtrans tidak valid.")

  with db_connection() as conn:
    payment = get_payment_by_order_id(conn, order_id)
    if not payment:
      raise HTTPException(status_code=404, detail="Order payment tidak ditemukan.")

    updated = update_payment_status(
      conn,
      payment["id"],
      status=_map_midtrans_status(payload),
      midtrans_transaction_id=str(payload.get("transaction_id") or ""),
      midtrans_order_id=order_id,
      raw_notification=payload,
    )

  if not updated:
    raise HTTPException(status_code=500, detail="Gagal memperbarui status payment.")

  return {
    "payment_id": updated["id"],
    "order_id": updated["order_id"],
    "status": updated["status"],
  }
