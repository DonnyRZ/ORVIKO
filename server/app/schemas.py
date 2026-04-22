from typing import Optional

from pydantic import BaseModel, Field


class SlideCreateRequest(BaseModel):
  title: str = Field("Untitled slide", max_length=120)
  text: str = Field("", max_length=5000)
  design: str = Field("", max_length=2000)
  quantity: int = Field(1, ge=1, le=5)
  aspect_ratio: str = Field("9:16", pattern=r"^(1:1|4:5|9:16|16:9)$")


class SlideUpdateRequest(BaseModel):
  title: Optional[str] = Field(None, max_length=120)
  text: Optional[str] = Field(None, max_length=5000)
  design: Optional[str] = Field(None, max_length=2000)
  quantity: Optional[int] = Field(None, ge=1, le=5)
  aspect_ratio: Optional[str] = Field(None, pattern=r"^(1:1|4:5|9:16|16:9)$")
  selected_result_id: Optional[str] = None


class GenerateRequest(BaseModel):
  quantity: int = Field(1, ge=1, le=5)
  grounding: bool = Field(False)


class EmbedUpdateRequest(BaseModel):
  label: Optional[str] = Field(None, max_length=120)
  context: Optional[str] = Field(None, max_length=500)
