import json
from urllib.parse import parse_qs, urlencode

import requests
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.core.config import get_settings
from app.core.db import db_connection, upsert_google_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google/login")
def google_login(
  plan: str = Query("creator"),
  price: str = Query("Rp 199.000"),
) -> RedirectResponse:
  settings = get_settings()

  if not settings.google_client_id or not settings.google_redirect_uri:
    raise HTTPException(status_code=500, detail="Google OAuth belum dikonfigurasi lengkap.")

  state = json.dumps({"plan": plan, "price": price}, ensure_ascii=True)
  params = urlencode(
    {
      "client_id": settings.google_client_id,
      "redirect_uri": settings.google_redirect_uri,
      "response_type": "code",
      "scope": "openid email profile",
      "access_type": "offline",
      "prompt": "consent",
      "state": state,
    }
  )

  auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{params}"
  return RedirectResponse(url=auth_url, status_code=302)


@router.get("/google/callback")
def google_callback(code: str | None = None, state: str | None = None) -> RedirectResponse:
  settings = get_settings()

  if not settings.google_client_id or not settings.google_client_secret or not settings.google_redirect_uri:
    raise HTTPException(status_code=500, detail="Google OAuth belum dikonfigurasi lengkap.")

  if not code:
    raise HTTPException(status_code=400, detail="Code dari Google tidak ditemukan.")

  token_response = requests.post(
    "https://oauth2.googleapis.com/token",
    data={
      "code": code,
      "client_id": settings.google_client_id,
      "client_secret": settings.google_client_secret,
      "redirect_uri": settings.google_redirect_uri,
      "grant_type": "authorization_code",
    },
    timeout=20,
  )

  if not token_response.ok:
    raise HTTPException(status_code=400, detail="Gagal menukar code Google menjadi token.")

  token_data = token_response.json()
  access_token = token_data.get("access_token")
  if not access_token:
    raise HTTPException(status_code=400, detail="Access token Google tidak ditemukan.")

  userinfo_response = requests.get(
    "https://openidconnect.googleapis.com/v1/userinfo",
    headers={"Authorization": f"Bearer {access_token}"},
    timeout=20,
  )

  if not userinfo_response.ok:
    raise HTTPException(status_code=400, detail="Gagal mengambil profil user dari Google.")

  userinfo = userinfo_response.json()
  with db_connection() as conn:
    user = upsert_google_user(
      conn,
      google_sub=userinfo.get("sub", ""),
      name=userinfo.get("name", ""),
      email=userinfo.get("email", ""),
      picture=userinfo.get("picture", ""),
    )

  selected_plan = "creator"
  selected_price = "Rp 199.000"
  if state:
    try:
      state_data = json.loads(state)
      selected_plan = str(state_data.get("plan") or selected_plan)
      selected_price = str(state_data.get("price") or selected_price)
    except json.JSONDecodeError:
      parsed_state = parse_qs(state)
      selected_plan = parsed_state.get("plan", [selected_plan])[0]
      selected_price = parsed_state.get("price", [selected_price])[0]

  redirect_query = urlencode(
    {
      "login": "success",
      "user_id": user["id"],
      "email": userinfo.get("email", ""),
      "plan": selected_plan,
      "price": selected_price,
    }
  )
  redirect_target = f"{settings.frontend_base_url.rstrip('/')}/payment?{redirect_query}"
  return RedirectResponse(url=redirect_target, status_code=302)
