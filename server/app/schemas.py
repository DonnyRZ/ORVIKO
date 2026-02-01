from typing import Optional

from pydantic import BaseModel, Field


class SlideCreateRequest(BaseModel):
  name: str = Field("Slide", max_length=80)
  title: str = Field("New slide", max_length=120)
  subtitle: str = Field("Waiting for content", max_length=160)
  text: str = Field("", max_length=5000)
  design: str = Field("", max_length=2000)
  quantity: int = Field(1, ge=1, le=5)
  position: int = Field(0, ge=0)


class SlideUpdateRequest(BaseModel):
  name: Optional[str] = Field(None, max_length=80)
  title: Optional[str] = Field(None, max_length=120)
  subtitle: Optional[str] = Field(None, max_length=160)
  text: Optional[str] = Field(None, max_length=5000)
  design: Optional[str] = Field(None, max_length=2000)
  quantity: Optional[int] = Field(None, ge=1, le=5)
  position: Optional[int] = Field(None, ge=0)
  selected_result_id: Optional[str] = None


class GenerateRequest(BaseModel):
  quantity: int = Field(1, ge=1, le=5)
  grounding: bool = Field(False)


class EmbedUpdateRequest(BaseModel):
  label: Optional[str] = Field(None, max_length=120)
  context: Optional[str] = Field(None, max_length=500)
