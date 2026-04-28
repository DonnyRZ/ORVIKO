from fastapi import APIRouter, Request

from app.schemas.payment import (
  MidtransCreatePaymentRequest,
  MidtransCreatePaymentResponse,
  PaymentStatusResponse,
)
from app.services.payment_service import (
  create_midtrans_transaction,
  get_payment_status,
  handle_midtrans_notification,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/midtrans/create", response_model=MidtransCreatePaymentResponse, status_code=201)
def create_midtrans_payment(payload: MidtransCreatePaymentRequest) -> dict:
  return create_midtrans_transaction(
    user_id=payload.user_id,
    plan=payload.plan,
    price=payload.price,
    email=payload.email,
  )


@router.post("/midtrans/notification")
async def midtrans_notification(request: Request) -> dict:
  payload = await request.json()
  return handle_midtrans_notification(payload)


@router.get("/{payment_id}", response_model=PaymentStatusResponse)
def get_payment(payment_id: str) -> dict:
  return get_payment_status(payment_id)
