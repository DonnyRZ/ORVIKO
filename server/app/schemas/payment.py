from typing import Literal

from pydantic import BaseModel, Field


PlanSlug = Literal["starter", "creator", "pro"]


class MidtransCreatePaymentRequest(BaseModel):
  user_id: str = Field(..., min_length=1)
  plan: PlanSlug
  price: int = Field(..., gt=0)
  email: str | None = None


class MidtransCreatePaymentResponse(BaseModel):
  payment_id: str
  order_id: str
  snap_token: str
  redirect_url: str
  status: str


class PaymentStatusResponse(BaseModel):
  payment_id: str
  order_id: str
  plan: PlanSlug
  gross_amount: int
  currency: str
  status: str
  user_id: str
  updated_at: str
